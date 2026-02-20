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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import DiseaseKnowledge, UnknownDisease, Message
import uuid
from datetime import datetime


# Kerala districts for reference
KERALA_DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
    "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
    "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod",
]

# Common Kerala crop diseases for quick matching
STUB_DISEASES = {
    "yellow leaves": {
        "disease": "Nitrogen Deficiency",
        "solution": "Apply nitrogen-rich fertilizer such as urea (46-0-0) at 50 kg/ha. "
                    "Ensure proper irrigation after application. Symptoms should improve within 7-10 days. "
                    "For paddy in Kuttanad/Palakkad, follow KAU recommendations for N application timing.",
    },
    "brown spots": {
        "disease": "Leaf Blight",
        "solution": "Apply copper-based fungicide (Bordeaux mixture) at 0.5% concentration. "
                    "Remove and destroy infected leaves. Ensure good air circulation between plants. "
                    "Common during Kerala monsoon season - apply preventive spraying before June.",
    },
    "wilting": {
        "disease": "Phytophthora Wilt",
        "solution": "Drench the base with Potassium Phosphonate (3ml/L) or Metalaxyl-Mancozeb (2g/L). "
                    "Improve drainage - critical during Kerala's heavy monsoon rainfall. "
                    "Apply Trichoderma-enriched neem cake as bio-control. "
                    "Contact your nearest Krishi Bhavan for assistance.",
    },
    "white powder": {
        "disease": "Powdery Mildew",
        "solution": "Spray sulfur-based fungicide at 2g/L. Improve air circulation by pruning. "
                    "Avoid overhead irrigation. Apply neem oil as preventive measure. "
                    "Common on vegetables and rubber nurseries during dry spells.",
    },
    "curling leaves": {
        "disease": "Leaf Curl Virus",
        "solution": "Control whitefly vectors using yellow sticky traps and neem-based insecticide. "
                    "Remove severely infected plants. Use virus-resistant varieties for next planting. "
                    "Common in chilli and tomato crops in Kerala.",
    },
    "black rot": {
        "disease": "Black Rot",
        "solution": "Apply copper hydroxide fungicide. Remove all infected plant debris. "
                    "Use certified disease-free seeds. Maintain proper field drainage. "
                    "Especially important during monsoon in lowland areas of Kerala.",
    },
    "coconut": {
        "disease": "Bud Rot / Root Wilt of Coconut",
        "solution": "For Bud Rot: Remove affected portion and apply 10% Bordeaux paste. "
                    "Pour Metalaxyl-Mancozeb (2g/L) into crown. "
                    "For Root Wilt: Apply recommended fertilizer dose with micronutrients. "
                    "Irrigate during summer. Report to the Coconut Development Board.",
    },
    "pepper": {
        "disease": "Quick Wilt of Pepper (Phytophthora)",
        "solution": "Drench base with Potassium Phosphonate (3ml/L). "
                    "Apply Trichoderma-enriched neem cake. Improve drainage around vines. "
                    "Mulch with dried leaves. Avoid waterlogging during monsoon.",
    },
    "rubber": {
        "disease": "Abnormal Leaf Fall of Rubber",
        "solution": "Spray Mancozeb (2g/L) during re-foliation in January-February. "
                    "Maintain optimum plant density. Apply balanced NPK fertilizers. "
                    "Contact the Rubber Board regional office for spraying schedule.",
    },
    "arecanut": {
        "disease": "Kole Rot (Mahali Disease) of Arecanut",
        "solution": "Spray 1% Bordeaux mixture before monsoon onset (May-June). "
                    "Remove and destroy infected bunches. Ensure proper drainage. "
                    "Apply Metalaxyl-Mancozeb (2g/L) during June-September.",
    },
    "banana": {
        "disease": "Sigatoka Leaf Spot of Banana",
        "solution": "Remove severely affected leaves. Spray Propiconazole (1ml/L) at 15-day intervals. "
                    "Ensure proper spacing for air circulation. Apply adequate potash fertilizer.",
    },
    "ginger": {
        "disease": "Rhizome Rot of Ginger",
        "solution": "Treat seed rhizomes with Mancozeb (3g/L) for 30 minutes before planting. "
                    "Drench beds with Copper Oxychloride (3g/L). Ensure raised beds with drainage. "
                    "Practice crop rotation - do not repeat ginger in same bed for 3 years.",
    },
    "cardamom": {
        "disease": "Katte Disease (Cardamom Mosaic)",
        "solution": "Remove and destroy infected plants immediately. "
                    "Control aphid vectors with Dimethoate (2ml/L). "
                    "Use virus-free planting material from certified nurseries.",
    },
    "tapioca": {
        "disease": "Tuber Rot of Tapioca",
        "solution": "Use disease-free stem cuttings for planting. "
                    "Ensure proper drainage in the field. Avoid waterlogging. "
                    "Treat planting material with Copper Oxychloride (3g/L).",
    },
}

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
    """Search the disease knowledge base for matching symptoms."""
    if not text:
        return None

    text_lower = text.lower()

    # Search in database first
    result = await db.execute(select(DiseaseKnowledge))
    diseases = result.scalars().all()

    for disease in diseases:
        if disease.symptoms and any(
            keyword.strip() in text_lower
            for keyword in disease.symptoms.lower().split(",")
        ):
            return disease

    return None


async def analyze_message(
    db: AsyncSession,
    text: Optional[str],
    image_url: Optional[str],
    conversation_messages: List[Message],
    location_lat: Optional[float] = None,
    location_lng: Optional[float] = None,
    message: Optional[Message] = None,
) -> Dict:
    """
    Analyze a farmer's message and return a diagnosis or follow-up.
    Focused on Kerala agricultural context.

    Returns dict with:
        - response_text: Bot's text response
        - is_diagnosis: Whether a diagnosis was made
        - is_unknown: Whether disease is unknown and flagged for MITL
        - follow_up: Whether this is a follow-up question
    """
    response = {
        "response_text": "",
        "is_diagnosis": False,
        "is_unknown": False,
        "follow_up": False,
    }

    # Gather all text from conversation for context
    all_text = ""
    for msg in conversation_messages:
        if msg.sender.value == "user" and msg.text_content:
            all_text += " " + msg.text_content
    if text:
        all_text += " " + text

    all_text_lower = all_text.lower().strip()

    # If very little information, ask follow-up
    if len(all_text_lower) < 10 and not image_url:
        question_idx = min(len(conversation_messages) // 2, len(FOLLOW_UP_QUESTIONS) - 1)
        response["response_text"] = (
            "I'd like to help you diagnose the issue with your crop. "
            + FOLLOW_UP_QUESTIONS[question_idx]
        )
        response["follow_up"] = True
        return response

    # 1. Check knowledge base (RAG simulation)
    kb_match = await search_knowledge_base(db, all_text_lower, location_lat, location_lng)
    if kb_match:
        location_note = ""
        if kb_match.region:
            location_note = f"\nThis disease is commonly reported in: {kb_match.region}."
        response["response_text"] = (
            f"**Diagnosis: {kb_match.disease_name}**\n\n"
            f"**Recommended Solution:**\n{kb_match.solution}"
            f"{location_note}"
        )
        response["is_diagnosis"] = True
        return response

    # 2. Check stub diseases
    for keyword, info in STUB_DISEASES.items():
        if keyword in all_text_lower:
            response["response_text"] = (
                f"**Diagnosis: {info['disease']}**\n\n"
                f"**Recommended Solution:**\n{info['solution']}"
            )
            response["is_diagnosis"] = True
            return response

    # 3. If image provided but no text match — simulate image classification
    if image_url:
        # After a few messages, if still no match, flag as unknown
        user_msgs = [m for m in conversation_messages if m.sender.value == "user"]
        if len(user_msgs) >= 2:
            # Flag as unknown disease for MITL
            unknown = UnknownDisease(
                id=uuid.uuid4(),
                message_id=message.id if message else uuid.uuid4(),
                image_url=image_url,
                text_symptoms=all_text_lower if all_text_lower else "Image-only submission",
                location_lat=location_lat,
                location_lng=location_lng,
                status="pending",
                created_at=datetime.utcnow(),
            )
            db.add(unknown)
            await db.commit()

            response["response_text"] = (
                "I was unable to identify this disease from our current database. "
                "I've flagged this case for our agricultural experts to review.\n\n"
                "An expert will analyze your images and symptoms, and the solution will "
                "be added to our knowledge base to help farmers across Kerala.\n\n"
                "In the meantime, please monitor the affected plants and avoid spreading "
                "material from infected plants to healthy ones. "
                "You may also contact your nearest Krishi Bhavan for immediate assistance."
            )
            response["is_unknown"] = True
            return response
        else:
            # Ask for more info
            response["response_text"] = (
                "I've received your image. To help me better diagnose the issue, "
                "could you please tell me:\n\n"
                + FOLLOW_UP_QUESTIONS[0]
                + "\n"
                + FOLLOW_UP_QUESTIONS[1]
            )
            response["follow_up"] = True
            return response

    # 4. After enough messages with no match — flag as unknown
    user_msgs = [m for m in conversation_messages if m.sender.value == "user"]
    if len(user_msgs) >= 3:
        unknown = UnknownDisease(
            id=uuid.uuid4(),
            message_id=message.id if message else uuid.uuid4(),
            image_url=None,
            text_symptoms=all_text_lower,
            location_lat=location_lat,
            location_lng=location_lng,
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(unknown)
        await db.commit()

        response["response_text"] = (
            "Based on the symptoms you've described, this appears to be an uncommon condition "
            "that I haven't encountered before. I've flagged this for our agricultural experts.\n\n"
            "They will review your case and provide a solution. This will also help us "
            "assist other farmers in Kerala facing similar issues.\n\n"
            "Please send a photo of the affected plant if you haven't already - "
            "it will help the experts significantly. You can also visit your nearest "
            "Krishi Bhavan for immediate assistance."
        )
        response["is_unknown"] = True
        return response

    # 5. Ask more follow-up questions
    question_idx = min(len(user_msgs), len(FOLLOW_UP_QUESTIONS) - 1)
    response["response_text"] = (
        "Thank you for the information. To narrow down the diagnosis:\n\n"
        + FOLLOW_UP_QUESTIONS[question_idx]
    )
    response["follow_up"] = True
    return response
