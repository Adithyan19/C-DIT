"""
Prompt Construction Module
Builds structured prompts for the LLM, incorporating disease data,
farmer descriptions, retrieved expert knowledge, and conversation history.
"""
import logging
from typing import Optional

from app.models import ChatMessage, RetrievedContext, PromptPayload

logger = logging.getLogger("c-dit")

SYSTEM_PROMPT = """You are KrishiRakshak, an expert agricultural advisor AI. You help farmers identify crop diseases and provide actionable guidance.

Instructions:
- Communicate clearly and simply, appropriate for farmers of varying education levels.
- Provide specific, actionable treatment recommendations.
- Include preventive measures for the future.
- If uncertain about the diagnosis, clearly state the uncertainty and recommend consulting a local agricultural extension officer.
- Be empathetic and encouraging.
- Keep responses concise but comprehensive.
- When multiple diseases are possible, list them with distinguishing features."""


def build_analysis_prompt(
    disease_label: Optional[str],
    farmer_description: str,
    retrieved_knowledge: list[RetrievedContext],
) -> PromptPayload:
    """Build an analysis prompt for initial disease diagnosis."""
    logger.info("Building analysis prompt")

    knowledge_context = "\n\n---\n\n".join(ctx.content for ctx in retrieved_knowledge)

    if disease_label:
        user_query = (
            f'A crop image has been analyzed and the suspected disease is "{disease_label}".\n'
            f'The farmer describes the situation as follows: "{farmer_description}"\n\n'
            "Based on the disease identification and expert knowledge provided below, give the farmer:\n"
            "1. Confirmation or correction of the disease diagnosis\n"
            "2. Detailed treatment recommendations\n"
            "3. Preventive measures for the future\n"
            "4. Any immediate actions the farmer should take"
        )
    else:
        user_query = (
            f'A farmer describes their crop problem as follows: "{farmer_description}"\n\n'
            "Based on the description and expert knowledge provided below, help the farmer by:\n"
            "1. Identifying the most likely disease(s)\n"
            "2. Detailed treatment recommendations\n"
            "3. Preventive measures for the future\n"
            "4. Any immediate actions the farmer should take"
        )

    return PromptPayload(
        systemPrompt=SYSTEM_PROMPT,
        userQuery=user_query,
        diseaseContext=(
            f"Suspected Disease: {disease_label}" if disease_label
            else "No disease identified from image analysis."
        ),
        retrievedKnowledge=knowledge_context,
        conversationHistory=[],
    )


def build_followup_prompt(
    user_message: str,
    conversation_history: list[ChatMessage],
    retrieved_knowledge: list[RetrievedContext],
) -> PromptPayload:
    """Build a follow-up prompt for continuing the conversation."""
    logger.info("Building follow-up prompt")

    knowledge_context = "\n\n---\n\n".join(ctx.content for ctx in retrieved_knowledge)

    return PromptPayload(
        systemPrompt=SYSTEM_PROMPT,
        userQuery=user_message,
        diseaseContext="",
        retrievedKnowledge=knowledge_context,
        conversationHistory=conversation_history,
    )
