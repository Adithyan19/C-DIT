import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import AsyncSessionLocal
from app.rice_engine import predict_rice_disease
from app.models import LeafImage
from sqlalchemy import select

async def verify_rice_inference():
    print("--- Verifying Rice Inference ---")
    
    async with AsyncSessionLocal() as db:
        # 1. Test image URL (using a placeholder or a real URL if possible)
        # Note: In a real test, you'd use a valid rice leaf image URL.
        test_url = "https://example.com/rice_leaf_test.jpg"
        print(f"Testing with URL: {test_url} (Expected to fail/be unknown if model not loaded)")
        
        # We'll mock the prediction if it fails due to network/model absence for this verification script
        try:
            result = await predict_rice_disease(db, test_url, threshold=0.9)
            print("Prediction Result:", result)
            
            # 2. Check if logged to DB if unknown
            if result.get("is_unknown") or result.get("predicted") == "unknown":
                stmt = select(LeafImage).where(LeafImage.image_path == test_url)
                db_result = await db.execute(stmt)
                leaf = db_result.scalar_one_or_none()
                if leaf:
                    print(f"✓ Successfully logged unknown image to DB: {leaf.image_path}")
                else:
                    print("✗ Failed to log unknown image to DB.")
            else:
                print("Prediction was confident, no DB logging expected (unless tested otherwise).")
                
        except Exception as e:
            print(f"✗ Inference failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_rice_inference())
