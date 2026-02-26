"""
ResNet transfer-learning pipeline for rice leaf disease detection
with PostgreSQL integration for 'unknown' image logging and
verified-image ingestion into the training set.

PostgreSQL table schema expected:
─────────────────────────────────────────────────────────────────
CREATE TABLE leaf_images (
    id            SERIAL PRIMARY KEY,
    image_path    TEXT        NOT NULL,          -- absolute path on disk
    predicted     TEXT,                          -- predicted class name or 'unknown'
    confidence    FLOAT,                         -- max softmax score (0-1)
    verified      BOOLEAN     DEFAULT FALSE,     -- set TRUE after human review
    true_label    TEXT,                          -- filled in after human review
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
─────────────────────────────────────────────────────────────────

Workflow:
  1. Before training: pull rows WHERE verified = TRUE and true_label IS NOT NULL
     from the DB and merge them into the training set.
  2. Train as normal (two-phase: frozen → fine-tune).
  3. During inference: any image whose max softmax confidence < UNKNOWN_THRESHOLD
     is logged to the DB as 'unknown' (if not already present).

Expected folder structure (single-folder dataset):
rice_disease/
  Rice_Leaf_AUG/
    Bacterial Leaf Blight/
    Brown Spot/
    Healthy Rice Leaf/
    Leaf Blast/
    Leaf scald/
    Sheath Blight/
"""

import io
import os
import copy
import shutil
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg2
import psycopg2.extras
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import (
    DataLoader, WeightedRandomSampler, Subset, Dataset, ConcatDataset
)
from torchvision import datasets, transforms, models
from tqdm import tqdm


# ========== USER CONFIG ==========
ROOT_DATA_DIR   = os.environ.get("DATA_DIR", "/kaggle/input/rice-disease-dataset")

MODEL_NAME          = "resnet50"    # "resnet18" or "resnet34" are faster
BATCH_SIZE          = 32
NUM_EPOCHS_FROZEN   = 6
NUM_EPOCHS_FINETUNE = 12
INIT_LR             = 1e-4
FT_LR               = 1e-5
NUM_WORKERS         = 4
IMG_SIZE            = 224
VAL_SPLIT           = 0.20
CHECKPOINT          = "resnet_rice_best.pth"
SEED                = 42

# Confidence below this → image is stored in DB as 'unknown'
UNKNOWN_THRESHOLD = 0.60

# ── PostgreSQL connection ──────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("PG_HOST",     "localhost"),
    "port":     int(os.environ.get("PG_PORT", "5432")),
    "dbname":   os.environ.get("PG_DB",       "rice_disease"),
    "user":     os.environ.get("PG_USER",     "postgres"),
    "password": os.environ.get("PG_PASSWORD", ""),
}
# ================================

torch.manual_seed(SEED)
np.random.seed(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)
print("Dataset root:", ROOT_DATA_DIR)


# ─────────────────────────────────────────────────────────────
#  DATABASE HELPERS
# ─────────────────────────────────────────────────────────────

def get_db_connection():
    """Return a new psycopg2 connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


def ensure_table_exists():
    """Create the leaf_images table if it doesn't already exist."""
    ddl = """
    CREATE TABLE IF NOT EXISTS leaf_images (
        id          SERIAL PRIMARY KEY,
        image_path  TEXT        NOT NULL UNIQUE,
        predicted   TEXT,
        confidence  FLOAT,
        verified    BOOLEAN     DEFAULT FALSE,
        true_label  TEXT,
        created_at  TIMESTAMPTZ DEFAULT NOW()
    );
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
    print("DB table 'leaf_images' ready.")


def log_unknown_image(image_path: str, confidence: float):
    """
    Insert a record for an image the model couldn't confidently classify.
    Uses INSERT ... ON CONFLICT DO NOTHING so re-running never creates duplicates.
    """
    sql = """
    INSERT INTO leaf_images (image_path, predicted, confidence, verified, true_label)
    VALUES (%s, 'unknown', %s, FALSE, NULL)
    ON CONFLICT (image_path) DO NOTHING;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (str(image_path), float(confidence)))
        conn.commit()


def fetch_verified_images() -> list[dict]:
    """
    Return all rows where verified = TRUE and true_label is set.
    These will be folded into the training set.
    """
    sql = """
    SELECT id, image_path, true_label
    FROM   leaf_images
    WHERE  verified = TRUE
      AND  true_label IS NOT NULL;
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
#  DATASET FOR DB-SOURCED (VERIFIED) IMAGES
# ─────────────────────────────────────────────────────────────

class VerifiedDBDataset(Dataset):
    """
    Loads images whose paths are stored in PostgreSQL (verified=True).
    Maps true_label strings → integer indices using the same class_to_idx
    dict built by ImageFolder so the label space is consistent.
    Rows whose image_path no longer exists on disk are skipped with a warning.
    """

    def __init__(self, db_rows: list[dict], class_to_idx: dict, transform=None):
        self.transform    = transform
        self.class_to_idx = class_to_idx
        self.samples: list[tuple[str, int]] = []

        skipped = 0
        for row in db_rows:
            path  = row["image_path"]
            label = row["true_label"]

            if not os.path.isfile(path):
                print(f"  [WARN] Verified image not found on disk, skipping: {path}")
                skipped += 1
                continue

            if label not in class_to_idx:
                print(f"  [WARN] true_label '{label}' not in known classes, skipping: {path}")
                skipped += 1
                continue

            self.samples.append((path, class_to_idx[label]))

        print(f"VerifiedDBDataset: {len(self.samples)} usable rows "
              f"({skipped} skipped).")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


# ─────────────────────────────────────────────────────────────
#  TRANSFORMS
# ─────────────────────────────────────────────────────────────

train_tf = transforms.Compose([
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.7, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2,
                           saturation=0.15, hue=0.02),
    transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=0.15),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

val_tf = transforms.Compose([
    transforms.Resize(int(IMG_SIZE * 1.14)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


# ─────────────────────────────────────────────────────────────
#  MAIN DATA-LOADING (with DB-verified merge)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.isdir(ROOT_DATA_DIR):
        raise FileNotFoundError(f"Root data dir not found: {ROOT_DATA_DIR}")

    # Ensure DB table exists before anything else
    ensure_table_exists()

    # Base filesystem dataset
    full_ds_train_tf = datasets.ImageFolder(ROOT_DATA_DIR, transform=train_tf)
    full_ds_val_tf   = datasets.ImageFolder(ROOT_DATA_DIR, transform=val_tf)

    class_names   = full_ds_train_tf.classes
    class_to_idx  = full_ds_train_tf.class_to_idx
    num_classes   = len(class_names)
    print("Classes (detected):", class_names)
    print("Total filesystem images:", len(full_ds_train_tf))

    all_indices = list(range(len(full_ds_train_tf)))
    all_labels  = [y for _, y in full_ds_train_tf.imgs]

    train_idx, val_idx = train_test_split(
        all_indices, test_size=VAL_SPLIT,
        stratify=all_labels, random_state=SEED,
    )

    train_ds = Subset(full_ds_train_tf, train_idx)
    val_ds   = Subset(full_ds_val_tf,   val_idx)
    train_labels = [all_labels[i] for i in train_idx]

    # ── Pull verified images from DB and merge into training set ──
    print("\nFetching verified images from PostgreSQL …")
    verified_rows = fetch_verified_images()
    print(f"Found {len(verified_rows)} verified DB rows.")

    if verified_rows:
        db_train_ds = VerifiedDBDataset(verified_rows, class_to_idx, transform=train_tf)
        if len(db_train_ds) > 0:
            train_ds     = ConcatDataset([train_ds, db_train_ds])
            # Extend label list for sampler construction
            train_labels = train_labels + [lbl for _, lbl in db_train_ds.samples]
            print(f"Training set after DB merge: {len(train_ds)} images.")

    # ── Weighted sampler (handles class imbalance) ────────────────
    train_class_counts = Counter(train_labels)
    class_weights_for_sampler = {
        cls: 1.0 / cnt for cls, cnt in train_class_counts.items()
    }
    sample_weights = [class_weights_for_sampler[lbl] for lbl in train_labels]
    sampler = WeightedRandomSampler(
        sample_weights, num_samples=len(sample_weights), replacement=True
    )

    train_loader = DataLoader(train_ds,  batch_size=BATCH_SIZE,
                              sampler=sampler, num_workers=NUM_WORKERS)
    val_loader   = DataLoader(val_ds,    batch_size=BATCH_SIZE,
                              shuffle=False,  num_workers=NUM_WORKERS)

    print(f"Train samples: {len(train_ds)}, Val samples: {len(val_idx)}")
    print("Per-class counts (train):",
          {class_names[k]: v for k, v in train_class_counts.items()})


    # ─────────────────────────────────────────────────────────────
    #  MODEL
    # ─────────────────────────────────────────────────────────────

    def build_resnet(name="resnet50", num_classes=6, pretrained=True):
        if name == "resnet50":
            model = models.resnet50(pretrained=pretrained)
        elif name == "resnet34":
            model = models.resnet34(pretrained=pretrained)
        elif name == "resnet18":
            model = models.resnet18(pretrained=pretrained)
        else:
            raise ValueError("Unsupported model: " + name)
        in_f = model.fc.in_features
        model.fc = nn.Linear(in_f, num_classes)
        return model


    model = build_resnet(MODEL_NAME, num_classes=num_classes,
                         pretrained=True).to(DEVICE)

    weights_for_loss = torch.tensor(
        [1.0 / train_class_counts[i] if train_class_counts[i] > 0 else 1.0
         for i in range(num_classes)],
        dtype=torch.float,
    ).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=weights_for_loss)

    scaler = torch.cuda.amp.GradScaler() if DEVICE.type == "cuda" else None


    # ─────────────────────────────────────────────────────────────
    #  TRAIN LOOP
    # ─────────────────────────────────────────────────────────────

    def run_epoch(loader, model, criterion, optimizer=None, train=True):
        model.train() if train else model.eval()
        running_loss = running_corrects = n_samples = 0
        loop = tqdm(loader, leave=False)
        for inputs, labels in loop:
            inputs = inputs.to(DEVICE, non_blocking=True)
            labels = labels.to(DEVICE, non_blocking=True)
            if train:
                optimizer.zero_grad()
            with torch.set_grad_enabled(train):
                if scaler is not None and train:
                    with torch.cuda.amp.autocast():
                        outputs = model(inputs)
                        loss    = criterion(outputs, labels)
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                elif scaler is not None:
                    with torch.cuda.amp.autocast():
                        outputs = model(inputs)
                        loss    = criterion(outputs, labels)
                else:
                    outputs = model(inputs)
                    loss    = criterion(outputs, labels)
                    if train:
                        loss.backward()
                        optimizer.step()
                preds = torch.argmax(outputs, dim=1)
            running_loss     += loss.item() * inputs.size(0)
            running_corrects += (preds == labels).sum().item()
            n_samples        += inputs.size(0)
            loop.set_description(
                f"{'train' if train else 'val'} loss: {loss.item():.4f}"
            )
        return running_loss / n_samples, running_corrects / n_samples


    # ── Phase 1: frozen backbone, train head only ─────────────────
    for p in model.parameters():
        p.requires_grad = False
    for p in model.fc.parameters():
        p.requires_grad = True

    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()),
                     lr=INIT_LR)
    scheduler = CosineAnnealingLR(
        optimizer, T_max=NUM_EPOCHS_FROZEN + NUM_EPOCHS_FINETUNE
    )

    best_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    print("\nPhase 1: training classifier head only")
    for epoch in range(NUM_EPOCHS_FROZEN):
        tl, ta = run_epoch(train_loader, model, criterion,
                           optimizer=optimizer, train=True)
        vl, va = run_epoch(val_loader,   model, criterion, train=False)
        print(f"[Phase1] Epoch {epoch+1}/{NUM_EPOCHS_FROZEN} "
              f"train_acc={ta:.4f} val_acc={va:.4f} "
              f"train_loss={tl:.4f} val_loss={vl:.4f}")
        if va > best_acc:
            best_acc = va
            best_wts = copy.deepcopy(model.state_dict())
            torch.save({"model_state": best_wts, "classes": class_names},
                       CHECKPOINT)
            print("  ✓ Saved checkpoint:", CHECKPOINT)
        scheduler.step()

    # ── Phase 2: unfreeze layer4 + fc ────────────────────────────
    print("\nPhase 2: fine-tuning layer4 and fc")
    for name, p in model.named_parameters():
        p.requires_grad = name.startswith("layer4") or name.startswith("fc")

    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()),
                     lr=FT_LR)
    scheduler = CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS_FINETUNE)

    for epoch in range(NUM_EPOCHS_FINETUNE):
        tl, ta = run_epoch(train_loader, model, criterion,
                           optimizer=optimizer, train=True)
        vl, va = run_epoch(val_loader,   model, criterion, train=False)
        print(f"[FT] Epoch {epoch+1}/{NUM_EPOCHS_FINETUNE} "
              f"train_acc={ta:.4f} val_acc={va:.4f} "
              f"train_loss={tl:.4f} val_loss={vl:.4f}")
        if va > best_acc:
            best_acc = va
            best_wts = copy.deepcopy(model.state_dict())
            torch.save({"model_state": best_wts, "classes": class_names},
                       CHECKPOINT)
            print("  ✓ Saved checkpoint:", CHECKPOINT)
        scheduler.step()

    print(f"\nTraining complete. Best val acc: {best_acc:.4f}")
    model.load_state_dict(best_wts)
    torch.save({"model_state": model.state_dict(), "classes": class_names},
               CHECKPOINT)
    print("Saved final model to", CHECKPOINT)


    # ─────────────────────────────────────────────────────────────
    #  FINAL EVALUATION
    # ─────────────────────────────────────────────────────────────

    model.eval()
    all_preds_eval, all_labels_eval = [], []
    with torch.no_grad():
        for inputs, labels in tqdm(val_loader, desc="Final eval"):
            inputs  = inputs.to(DEVICE)
            outputs = model(inputs)
            preds   = torch.argmax(outputs, dim=1)
            all_preds_eval.extend(preds.cpu().numpy())
            all_labels_eval.extend(labels.numpy())

    print("\nClassification report:")
    print(classification_report(all_labels_eval, all_preds_eval,
                                 target_names=class_names, digits=4))
    print("Confusion matrix (rows=true, cols=pred):")
    print(confusion_matrix(all_labels_eval, all_preds_eval))

    with open("class_map.txt", "w") as f:
        for idx, cls in enumerate(class_names):
            f.write(f"{idx}\t{cls}\n")
    print("Saved class_map.txt")

    print("\nScript finished.")
