"""
Sample / Placeholder Model Service

All AI model calls are simulated here. Each function has a clearly marked
INTEGRATION POINT comment showing exactly where to plug in a real model.

Replace each function's placeholder logic with your actual model inference.
"""
import asyncio
import logging

from app.models import (
    DiseaseClassification,
    ConfidenceLevel,
    PromptPayload,
)
from app.data.disease_knowledge import DISEASE_KNOWLEDGE

logger = logging.getLogger("c-dit")

# Labels derived from the knowledge base
_SIMULATED_LABELS = [d["diseaseName"] for d in DISEASE_KNOWLEDGE]

# Simulated STT descriptions
_SIMULATED_DESCRIPTIONS = [
    "My rice crop leaves have developed diamond-shaped spots with gray centers. The spots are spreading quickly across the field.",
    "The tomato plants in my farm are showing dark circular spots with ring patterns on the lower leaves. Some leaves have started to yellow and fall off.",
    "I am seeing white powdery coating on my grape vine leaves. The leaves are starting to curl and the fruits have blemishes on them.",
    "The potato plants have water-soaked dark patches on the leaf tips. In the morning I can see white fuzzy growth underneath the leaves.",
    "My banana plants are wilting even though I water them regularly. When I cut the stem I can see brown discoloration inside.",
    "The corn leaves have long gray-green spots that are getting bigger each day. It started after the recent rains.",
    "My mango fruits have dark sunken spots and some have pink colored growth on them during humid weather.",
    "The wheat crop has reddish-brown spots on the stems and leaf sheaths. Some stalks are becoming weak and bending.",
]


async def classify_image(image_data: bytes) -> DiseaseClassification:
    """
    Classify a crop disease from image data.

    # INTEGRATION POINT ─────────────────────────────────────────────────
    # Replace with your real model call:
    #
    #   import httpx
    #   async with httpx.AsyncClient() as client:
    #       resp = await client.post(
    #           settings.image_classifier_endpoint,
    #           content=image_data,
    #           headers={"Content-Type": "application/octet-stream"},
    #       )
    #       result = resp.json()
    #       return DiseaseClassification(
    #           label=result["label"],
    #           confidence=result["confidence"],
    #           confidenceLevel=_get_confidence_level(result["confidence"]),
    #           isKnown=result["confidence"] >= 0.2,
    #       )
    # ───────────────────────────────────────────────────────────────────
    """
    logger.info(f"Image classification started (size={len(image_data)})")

    # Simulated: deterministic result based on image size
    seed = len(image_data) % len(_SIMULATED_LABELS)
    label = _SIMULATED_LABELS[seed]
    confidence = 0.65 + (len(image_data) % 35) / 100
    confidence = min(confidence, 0.99)
    confidence_level = _get_confidence_level(confidence)

    # Simulate processing time
    await asyncio.sleep(0.3)

    result = DiseaseClassification(
        label=label,
        confidence=round(confidence, 2),
        confidenceLevel=confidence_level,
        isKnown=confidence_level != ConfidenceLevel.UNKNOWN,
    )

    logger.info(f"Image classification complete: {result.label} ({result.confidence})")
    return result


async def speech_to_text(audio_data: bytes) -> str:
    """
    Convert audio to text via speech-to-text.

    # INTEGRATION POINT ─────────────────────────────────────────────────
    # Replace with your real STT model:
    #
    #   import httpx
    #   async with httpx.AsyncClient() as client:
    #       files = {"file": ("recording.wav", audio_data)}
    #       resp = await client.post(settings.stt_endpoint, files=files)
    #       return resp.json()["text"]
    # ───────────────────────────────────────────────────────────────────
    """
    logger.info(f"Speech-to-text started (size={len(audio_data)})")

    # Simulated: deterministic result based on audio size
    index = len(audio_data) % len(_SIMULATED_DESCRIPTIONS)
    transcribed = _SIMULATED_DESCRIPTIONS[index]

    await asyncio.sleep(0.3)

    logger.info(f"Speech-to-text complete: {transcribed[:60]}...")
    return transcribed


async def generate_advisory(prompt: PromptPayload) -> str:
    """
    Generate an advisory response from the LLM.

    # INTEGRATION POINT ─────────────────────────────────────────────────
    # Replace with your real LLM call:
    #
    #   import httpx
    #   async with httpx.AsyncClient() as client:
    #       resp = await client.post(
    #           settings.llm_endpoint,
    #           json={
    #               "model": "tinyllama",
    #               "prompt": _format_prompt(prompt),
    #               "stream": False,
    #           },
    #       )
    #       return resp.json()["response"]
    # ───────────────────────────────────────────────────────────────────
    """
    logger.info("Generating LLM advisory response")

    advisory = _generate_simulated_response(prompt)
    await asyncio.sleep(0.5)

    logger.info(f"Advisory generated (length={len(advisory)})")
    return advisory


async def generate_followup_response(prompt: PromptPayload) -> str:
    """
    Generate a follow-up response for an ongoing conversation.

    # INTEGRATION POINT — same as generate_advisory above.
    """
    logger.info("Generating follow-up response")

    response = _generate_simulated_followup(prompt)
    await asyncio.sleep(0.3)

    return response


# ─── Simulated Response Generation ──────────────────────────────────────────

def _generate_simulated_response(prompt: PromptPayload) -> str:
    knowledge = prompt.retrievedKnowledge

    if not knowledge or len(knowledge.strip()) == 0:
        return (
            "Thank you for describing your crop issue. Based on your description, "
            "I was unable to find a specific matching disease in our knowledge base.\n\n"
            "**Recommendations:**\n"
            "1. Take clear photos of the affected parts (leaves, stems, fruits) and consult your nearest agricultural extension office.\n"
            "2. Isolate affected plants if possible to prevent further spread.\n"
            "3. Avoid over-watering and ensure good air circulation around plants.\n"
            "4. Apply a broad-spectrum fungicide as a precautionary measure.\n\n"
            "Please provide more details about the affected crop, the specific symptoms, "
            "and how long you've observed the problem, so I can give more targeted advice."
        )

    lines = knowledge.split("\n")
    disease_match = next((l for l in lines if l.startswith("Disease:")), None)
    symptoms_match = next((l for l in lines if l.startswith("Symptoms:")), None)
    treatment_match = next((l for l in lines if l.startswith("Treatment:")), None)
    prevention_match = next((l for l in lines if l.startswith("Prevention:")), None)
    crop_match = next((l for l in lines if l.startswith("Crop:")), None)

    disease_name = disease_match.replace("Disease:", "").strip() if disease_match else "the identified disease"
    symptoms = symptoms_match.replace("Symptoms:", "").strip() if symptoms_match else ""
    treatment = treatment_match.replace("Treatment:", "").strip() if treatment_match else ""
    prevention = prevention_match.replace("Prevention:", "").strip() if prevention_match else ""
    crop = crop_match.replace("Crop:", "").strip() if crop_match else "your crop"

    return (
        f"## Disease Diagnosis: {disease_name}\n\n"
        f"Based on the analysis of your {crop} and your description, "
        f"the symptoms are consistent with **{disease_name}**.\n\n"
        f"### Symptoms to Confirm\n{symptoms}\n\n"
        f"### Recommended Treatment\n{treatment}\n\n"
        f"### Prevention for Future Seasons\n{prevention}\n\n"
        "### Immediate Actions\n"
        "1. **Isolate affected plants** — remove heavily infected plants to prevent spread to healthy ones.\n"
        "2. **Start treatment immediately** — early intervention significantly improves outcomes.\n"
        "3. **Document the situation** — take photos for your records and for consultation with local experts.\n"
        "4. **Monitor regularly** — check neighboring plants daily for early signs of spread.\n\n"
        "> If the disease persists after treatment, please consult your nearest Krishi Vigyan Kendra (KVK) "
        "or agricultural extension officer for a detailed laboratory analysis.\n\n"
        "Feel free to ask any follow-up questions about the treatment or prevention measures."
    )


def _generate_simulated_followup(prompt: PromptPayload) -> str:
    question = prompt.userQuery.lower()

    if any(kw in question for kw in ("dosage", "how much", "quantity")):
        return (
            "**Dosage Guidelines:**\n\n"
            "The exact dosage depends on the specific product you are using, but here are general guidelines:\n\n"
            "1. **Mancozeb** — 2.5 g per liter of water (spray both sides of leaves)\n"
            "2. **Copper oxychloride** — 3 g per liter of water\n"
            "3. **Carbendazim** — 1 g per liter of water\n\n"
            "**Application Tips:**\n"
            "- Spray early morning or late evening for best absorption\n"
            "- Ensure complete coverage of all plant parts\n"
            "- Repeat application after 7–10 days\n"
            "- Do not spray during windy or rainy conditions\n\n"
            "Always read the product label carefully for specific dosage instructions and safety precautions."
        )

    if any(kw in question for kw in ("organic", "natural", "chemical free")):
        return (
            "**Organic/Natural Treatment Options:**\n\n"
            "1. **Neem oil spray** — Mix 5 ml neem oil with 1 liter of water and add 1 ml liquid soap as emulsifier. Spray every 5–7 days.\n"
            "2. **Trichoderma** — Apply Trichoderma viride (5 g per liter) as soil drench and foliar spray.\n"
            "3. **Pseudomonas** — Use Pseudomonas fluorescens (10 g per liter) as preventive spray.\n"
            "4. **Cow urine spray** — Dilute cow urine (1:10 with water) and spray on leaves.\n"
            "5. **Bordeaux mixture** — Mix copper sulfate and lime (1:1 ratio, 1% each).\n\n"
            "These methods are best for prevention and early-stage infections."
        )

    if any(kw in question for kw in ("spread", "other plant", "contagious")):
        return (
            "**Disease Spread Prevention:**\n\n"
            "Yes, most crop diseases can spread to neighboring plants. Here's how to contain it:\n\n"
            "1. **Physical removal** — Remove and destroy severely infected plant parts immediately\n"
            "2. **Spacing** — Maintain recommended plant spacing for adequate air circulation\n"
            "3. **Sanitation** — Disinfect pruning tools with rubbing alcohol between cuts\n"
            "4. **Drainage** — Ensure fields are well-drained\n"
            "5. **Barrier spraying** — Apply preventive fungicide sprays on healthy plants\n"
            "6. **Crop isolation** — Create a buffer zone of 2–3 meters around infected areas\n\n"
            "Regular monitoring is crucial — check all plants at least twice a week."
        )

    return (
        "Thank you for your question. Based on the current context of your crop situation:\n\n"
        "1. Continue the recommended treatment regimen consistently\n"
        "2. Monitor the affected plants daily for improvement or worsening\n"
        "3. Ensure proper nutrients and water management alongside disease treatment\n"
        "4. If you notice any new symptoms, please share updated photos or descriptions\n\n"
        "Would you like more specific information about any particular aspect of the treatment, "
        "prevention, or crop management?"
    )


def _get_confidence_level(confidence: float) -> ConfidenceLevel:
    if confidence >= 0.8:
        return ConfidenceLevel.HIGH
    if confidence >= 0.5:
        return ConfidenceLevel.MEDIUM
    if confidence >= 0.2:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNKNOWN
