"""
Disease detection engine for Kerala crops — stub implementation.

This module simulates:
1. Image classification (plant disease from photo)
2. Text symptom analysis
3. Fusion of image + text for diagnosis
4. RAG-based solution retrieval from disease_knowledge table
5. Interactive follow-up questions when info is insufficient
6. Flagging unknown diseases for man-in-the-loop review

Focused on crops commonly grown in Kerala:
coconut, rubber, pepper, arecanut, banana, rice, ginger,
cardamom, tapioca, nutmeg, tea, coffee, cashew, etc.
"""

from typing import Optional, List, Dict
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import DiseaseKnowledge, UnknownDisease, Message
import uuid
from datetime import datetime
FOLLOW_UP_QUESTIONS = [
    "Can you describe the color and pattern of the affected areas on the plant?",
    "Which crop is affected? (e.g., coconut, rubber, pepper, banana, rice, arecanut, ginger, tapioca)",
    "How long have you noticed these symptoms?",
    "Are nearby plants also showing similar symptoms?",
    "What is the current season/weather in your area? (monsoon/summer/post-monsoon)",
    "Which district in Kerala are you from?",
    "Have you applied any pesticides or fertilizers recently?",
]


async def search_knowledge_base(
    db: AsyncSession, text: Optional[str], location_lat: Optional[float] = None,
    location_lng: Optional[float] = None
) -> Optional[DiseaseKnowledge]:
    """Search the disease knowledge base for matching symptoms using SQL filtering."""
    if not text:
        return None

    # Use a more efficient search using ILIKE
    # We split keywords and check if any match the query text
    # For better performance, we'll search the symptoms column
    # Note: A real implementation might use pg_trgm for full-text search
    
    result = await db.execute(
        select(DiseaseKnowledge)
        .where(DiseaseKnowledge.symptoms.ilike(f"%{text}%"))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def analyze_message_rag(
    text: Optional[str],
    image_url: Optional[str],
    conversation_messages: List[Message],
    location_lat: Optional[float] = None,
    location_lng: Optional[float] = None,
    request: Optional[Request] = None,
) -> Optional[str]:
    """
    Core AI analysis logic - NO DB connection here.
    Returns the response text from RAG or None if RAG isn't used/available.
    """
    # Gather all text from conversation for context
    query_text: str = ""
    for msg in conversation_messages:
        if msg.sender.value == "user" and msg.text_content:
            query_text += f" {msg.text_content}"
    if text:
        query_text += f" {text}"

    query_text = query_text.strip()

    # Use RAG Service if available
    if request and hasattr(request.app.state, "rag_service"):
        rag_service = request.app.state.rag_service
        if rag_service.is_initialized:
            return await rag_service.generate_answer(query_text)
    
    return None

class StructuredDiagnosticEngine:
    def __init__(self):
        # No longer using CSV as source
        pass
        
    def extract_features(self, text: str) -> Dict[str, str]:
        text = text.lower()
        features = {
            "crop": "",
            "position": "",
            "pattern": "",
            "weather": ""
        }
        
        # Synonym mappings for Extraction
        crop_synonyms = {
            "tomato": ["tomato", "tomatoes"],
            "coconut": ["coconut", "coconuts", "palm", "palms"],
            "pepper": ["pepper", "peppers", "black pepper"],
            "banana": ["banana", "bananas", "plantain"],
            "rice": ["rice", "paddy"],
            "arecanut": ["arecanut", "areca", "betel nut"],
            "ginger": ["ginger"],
            "tapioca": ["tapioca", "cassava"],
            "rubber": ["rubber"],
            "cardamom": ["cardamom"]
        }
        
        position_synonyms = {
            "lower leaves": ["lower leaves", "older leaves", "bottom leaves", "base leaves"],
            "upper leaves": ["upper leaves", "newer leaves", "top leaves", "young leaves"],
            "mid leaves": ["mid leaves", "middle leaves"],
            "rhizome": ["rhizome", "root stock", "bulb"],
            "stem": ["stem", "trunk", "stalk"],
            "roots": ["root", "roots"],
            "leaves": ["leaf", "leaves", "foliage", "frond", "fronds", "leaflet", "leaflets"]
        }
        
        pattern_synonyms = {
            "concentric rings": ["concentric rings", "bullseye", "rings"],
            "lesions": ["lesion", "lesions"],
            "yellowing": ["yellowing", "yellow", "yellow patches", "pale", "chlorosis"],
            "wilting": ["wilting", "wilt", "drooping", "droop", "flaccid", "tired"],
            "dark spots": ["dark spots", "black spots", "brown spots", "sunken spots"],
            "rapid wilt": ["rapid wilt", "sudden wilt", "quick wilt"],
            "streaks": ["streaks", "stripe", "stripes"],
            "mottling": ["mottling", "mottled"],
            "mosaic": ["mosaic"],
            "burnt tips": ["burnt tips", "burnt edges", "scorched"],
            "rot": ["rot", "rotting", "decay"],
            "soft rot": ["soft rot", "mushy"]
        }
        
        weather_synonyms = {
            "humid": ["humid", "humidity", "muggy", "sticky"],
            "rainy": ["rainy", "rain", "rains", "raining", "wet"],
            "monsoon": ["monsoon", "heavy rain"],
            "dry": ["dry", "drought", "no rain"],
            "summer": ["summer", "hot", "heat", "warm"]
        }
        
        # Helper to find first matching key based on synonyms
        def find_match(synonym_dict):
            for key, synonyms in synonym_dict.items():
                if any(syn in text for syn in synonyms):
                    return key
            return ""

        features["crop"] = find_match(crop_synonyms)
        features["position"] = find_match(position_synonyms)
        features["pattern"] = find_match(pattern_synonyms)
        features["weather"] = find_match(weather_synonyms)
        
        return features

    async def find_match(self, db: AsyncSession, features: Dict[str, str]) -> Optional[DiseaseKnowledge]:
        from sqlalchemy import select
        from app.models import DiseaseKnowledge
        
        if not features["crop"]:
            return None
            
        # 1. Fetch all diseases for the identified crop
        result = await db.execute(
            select(DiseaseKnowledge).where(DiseaseKnowledge.crop.ilike(f"%{features['crop']}%"))
        )
        candidates = result.scalars().all()
        
        if not candidates:
            return None
            
        # 2. Score candidates based on matching features
        best_match = None
        highest_score = 0
        
        for candidate in candidates:
            score = 0
            
            # Position match (worth 2 points)
            if features["position"] and candidate.position:
                if features["position"].lower() in candidate.position.lower():
                    score += 2
                
            # Pattern match (worth 2 points)
            if features["pattern"] and candidate.pattern:
                if features["pattern"].lower() in candidate.pattern.lower():
                    score += 2
                    
            # Weather match (worth 1 point)
            if features["weather"] and candidate.weather:
                if features["weather"].lower() in candidate.weather.lower():
                    score += 1
            
            # Additional fallback: if all provided features match
            if score > highest_score:
                highest_score = score
                best_match = candidate
                
        # Return match only if we have at least one strong indicator (position or pattern)
        if highest_score >= 2:
            return best_match
            
        return None

# Global instance
diagnostic_engine = StructuredDiagnosticEngine()

async def analyze_message(
    db: AsyncSession,
    text: Optional[str],
    image_url: Optional[str],
    conversation_messages: List[Message],
    location_lat: Optional[float] = None,
    location_lng: Optional[float] = None,
    message: Optional[Message] = None,
    request: Optional[Request] = None,
) -> Dict:
    """
    Analyze a farmer's message and return a diagnosis or follow-up.
    Uses Structured Feature Extraction and Treatment-Only RAG.
    """
    response = {
        "response_text": "",
        "is_diagnosis": False,
        "is_unknown": False,
        "follow_up": False,
        "disease_name": None,
        "crop_name": None
    }

    # Gather context
    query_text: str = ""
    for msg in conversation_messages:
        if msg.sender.value == "user" and msg.text_content:
            query_text += f" {msg.text_content}"
    if text:
        query_text += f" {text}"
    query_text = query_text.strip().lower()

    if len(query_text) < 10 and not image_url:
        question_idx = min(len(conversation_messages) // 2, len(FOLLOW_UP_QUESTIONS) - 1)
        response["response_text"] = "I need a bit more detail to help. " + FOLLOW_UP_QUESTIONS[question_idx]
        response["follow_up"] = True
        return response

    # 1. Feature Extraction
    features = diagnostic_engine.extract_features(query_text)
    
    # 2. Check if enough features for diagnosis (Query SQL DB)
    found_match = await diagnostic_engine.find_match(db, features)

    if found_match:
        response["disease_name"] = found_match.disease_name
        response["crop_name"] = found_match.crop
        response["response_text"] = (
            f"**IDENTIFIED: {found_match.disease_name.upper()} in {found_match.crop.upper()}**\n\n"
            f"**Symptoms Matched:** {found_match.symptom} ({found_match.position}, {found_match.pattern})\n"
            f"**Weather Context:** {found_match.weather}\n\n"
            f"**Immediate Action:** {found_match.treatment_summary}\n\n"
            "Searching for detailed scientific treatment explanation..."
        )
        response["is_diagnosis"] = True
        return response

    # 3. If no match, check for ambiguity or missing info
    if not features["crop"]:
        response["response_text"] = "To help accurately, I need to know which crop you are asking about (e.g., Tomato, Coconut, Pepper)."
        response["follow_up"] = True
        return response
    
    if not features["position"] or not features["pattern"]:
        response["response_text"] = "I've noted the crop, but could you describe the *position* (e.g., lower leaves) and *pattern* (e.g., spots or rings) of the symptoms?"
        response["follow_up"] = True
        return response

    # 4. Fallback to Unknown if still nothing
    response["response_text"] = "I can't find a direct match in my structured records, but I am consulting my expert database for a broader search..."
    response["is_unknown"] = True 
    return response
