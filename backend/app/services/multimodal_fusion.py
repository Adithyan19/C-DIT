"""
Multimodal Fusion Layer
Combines disease classification results with text descriptions
into a unified query for the RAG pipeline.
"""
import logging
from typing import Optional

from app.models import DiseaseClassification, FusedInput

logger = logging.getLogger("c-dit")


def fuse_inputs(
    classification: Optional[DiseaseClassification],
    text_description: str,
) -> FusedInput:
    """Fuse multimodal inputs into a single structured query."""
    logger.info(
        f"Fusing multimodal inputs (has_classification={classification is not None}, "
        f"text_length={len(text_description)})"
    )

    disease_label = classification.label if (classification and classification.isKnown) else None
    disease_confidence = classification.confidence if classification else 0.0

    # Build combined query that weights known disease labels higher
    if disease_label and disease_confidence >= 0.5:
        combined_query = f"Disease: {disease_label}. {text_description}"
    elif disease_label:
        combined_query = f"Possible disease: {disease_label}. {text_description}"
    else:
        combined_query = text_description

    fused = FusedInput(
        diseaseLabel=disease_label,
        diseaseConfidence=disease_confidence,
        textDescription=text_description,
        combinedQuery=combined_query.strip(),
    )

    logger.info(f"Fusion complete (combined_query_length={len(fused.combinedQuery)})")
    return fused
