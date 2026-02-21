import sys
import os
import asyncio
from typing import List, Optional

# Mocking the database and request objects for a unit test
# Fix path to backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.disease_engine import diagnostic_engine, analyze_message
from app.models import Message

async def test_structured_diagnosis():
    print("Testing Structured Diagnosis Engine...")
    
    # Test 1: Full information
    test_text = "My tomato has brown spots on lower leaves with concentric rings. The weather is humid."
    features = diagnostic_engine.extract_features(test_text)
    print(f"Extracted Features: {features}")
    
    match = diagnostic_engine.find_match(features)
    if match:
        print(f"✅ Match Found: {match['disease']} in {match['crop']}")
    else:
        print("❌ Match Failed")

    # Test 2: Missing crop
    missing_text = "I have brown spots on lower leaves."
    features_missing = diagnostic_engine.extract_features(missing_text)
    print(f"Extracted Features (Missing Crop): {features_missing}")
    if not features_missing['crop']:
        print("✅ Correct: Detected missing crop name.")

if __name__ == "__main__":
    asyncio.run(test_structured_diagnosis())
