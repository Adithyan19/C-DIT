import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models import LeafImage, UnknownDisease
from app.config import settings
from typing import List, Dict, Optional, Tuple
import httpx
import tempfile
import logging

logger = logging.getLogger(__name__)

# ========== CONFIG ==========
MODEL_NAME = "resnet50"
IMG_SIZE = 224
UNKNOWN_THRESHOLD = 0.60
CHECKPOINT_PATH = "resnet_rice_best.pth"

CLASS_NAMES = [
    "Bacterial Leaf Blight",
    "Brown Spot",
    "Healthy Rice Leaf",
    "Leaf Blast",
    "Leaf scald",
    "Sheath Blight"
]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ========== TRANSFORMS ==========
val_tf = transforms.Compose([
    transforms.Resize(int(IMG_SIZE * 1.14)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# ========== MODEL CACHE ==========
_model_cache = {}

def get_resnet_model(name: str = MODEL_NAME, num_classes: int = len(CLASS_NAMES)):
    if name in _model_cache:
        return _model_cache[name]
    
    if name == "resnet50":
        model = models.resnet50(weights=None)
    elif name == "resnet34":
        model = models.resnet34(weights=None)
    elif name == "resnet18":
        model = models.resnet18(weights=None)
    else:
        raise ValueError("Unsupported model: " + name)
        
    in_f = model.fc.in_features
    model.fc = nn.Linear(in_f, num_classes)
    
    if os.path.exists(CHECKPOINT_PATH):
        try:
            checkpoint = torch.load(CHECKPOINT_PATH, map_location=DEVICE)
            if "model_state" in checkpoint:
                model.load_state_dict(checkpoint["model_state"])
            else:
                model.load_state_dict(checkpoint)
            logger.info(f"Loaded ResNet checkpoint from {CHECKPOINT_PATH}")
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            
    model = model.to(DEVICE)
    model.eval()
    _model_cache[name] = model
    return model

async def log_unknown_image(db: AsyncSession, image_path: str, confidence: float):
    """Log an unknown image to the database."""
    # Check if already exists
    stmt = select(LeafImage).where(LeafImage.image_path == image_path)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return

    new_leaf = LeafImage(
        image_path=image_path,
        predicted="unknown",
        confidence=confidence,
        verified=False
    )
    db.add(new_leaf)
    await db.commit()

async def predict_rice_disease(
    db: AsyncSession,
    image_url: str,
    threshold: float = UNKNOWN_THRESHOLD
) -> Dict:
    """
    Predict rice disease from an image URL.
    If confidence < threshold, logs to DB as 'unknown'.
    """
    model = get_resnet_model()
    
    # Handle image loading (from URL or local path)
    temp_file = None
    try:
        if image_url.startswith(("http://", "https://")):
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                if response.status_code != 200:
                    raise Exception(f"Failed to download image: {response.status_code}")
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                temp_file.write(response.content)
                temp_file.close()
                img_path = temp_file.name
        else:
            img_path = image_url
            
        img = Image.open(img_path).convert("RGB")
        tensor = val_tf(img).unsqueeze(0).to(DEVICE)
        
        with torch.no_grad():
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
            
        max_conf = float(probs.max())
        pred_idx = int(probs.argmax())
        predicted_class = CLASS_NAMES[pred_idx]
        
        all_scores = {cls: float(probs[i]) for i, cls in enumerate(CLASS_NAMES)}
        
        is_unknown = max_conf < threshold
        if is_unknown:
            logger.info(f"[UNKNOWN] confidence={max_conf:.3f} < {threshold} → logging to DB: {image_url}")
            await log_unknown_image(db, image_url, max_conf)
            predicted_class = "unknown"
            
        return {
            "image_url": image_url,
            "predicted": predicted_class,
            "confidence": max_conf,
            "all_scores": all_scores,
            "is_unknown": is_unknown
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {
            "error": str(e),
            "predicted": "error",
            "confidence": 0.0
        }
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)

async def fetch_verified_rice_images(db: AsyncSession):
    """Fetch verified images for training from both LeafImage and UnknownDisease tables."""
    # 1. Fetch from LeafImage
    stmt1 = select(LeafImage).where(LeafImage.verified == True, LeafImage.true_label != None)
    result1 = await db.execute(stmt1)
    leaf_images = result1.scalars().all()
    
    # 2. Fetch from UnknownDisease (status = 'classified')
    stmt2 = select(UnknownDisease).where(UnknownDisease.status == "classified")
    result2 = await db.execute(stmt2)
    unknown_diseases = result2.scalars().all()
    
    return {
        "leaf_images": leaf_images,
        "classified_unknowns": unknown_diseases
    }
