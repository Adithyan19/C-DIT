"""
Pydantic models matching the frontend API contract.
All types mirror the original TypeScript interfaces.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Confidence Levels ───────────────────────────────────────────────────────

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


# ─── Disease Classification ─────────────────────────────────────────────────

class DiseaseClassification(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    confidenceLevel: ConfidenceLevel
    isKnown: bool


# ─── Retrieved Context ──────────────────────────────────────────────────────

class ContextMetadata(BaseModel):
    diseaseName: str
    category: str
    source: str


class RetrievedContext(BaseModel):
    documentId: str
    content: str
    similarity: float
    metadata: ContextMetadata


# ─── Analysis Result ────────────────────────────────────────────────────────

class AnalysisResult(BaseModel):
    sessionId: str
    disease: DiseaseClassification
    advisory: str
    retrievedContext: list[RetrievedContext]
    followUpSuggestions: list[str]
    timestamp: str
    transcribedText: Optional[str] = None


# ─── Chat ────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # 'farmer' | 'assistant'
    content: str
    timestamp: str


class ChatFollowupRequest(BaseModel):
    sessionId: str
    message: str


class ChatFollowupResponse(BaseModel):
    sessionId: str
    reply: str
    timestamp: str


# ─── Feedback ────────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    sessionId: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    wasHelpful: bool
    correctDisease: Optional[str] = None


# ─── Multimodal Fusion ──────────────────────────────────────────────────────

class FusedInput(BaseModel):
    diseaseLabel: Optional[str]
    diseaseConfidence: float
    textDescription: str
    combinedQuery: str


# ─── Prompt Payload ─────────────────────────────────────────────────────────

class PromptPayload(BaseModel):
    systemPrompt: str
    userQuery: str
    diseaseContext: str
    retrievedKnowledge: str
    conversationHistory: list[ChatMessage] = []


# ─── Text Analysis Request ──────────────────────────────────────────────────

class TextAnalysisRequest(BaseModel):
    description: str
    sessionId: Optional[str] = None


# ─── API Response Wrappers ──────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    message: str


class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[ErrorDetail] = None
    message: Optional[str] = None


# ─── Disease Knowledge Entry ────────────────────────────────────────────────

class DiseaseKnowledgeEntry(BaseModel):
    id: str
    diseaseName: str
    cropAffected: str
    symptoms: str
    causes: str
    treatment: str
    prevention: str
    additionalNotes: Optional[str] = None


# ─── Vector Document ────────────────────────────────────────────────────────

class VectorDocument(BaseModel):
    id: str
    content: str
    embedding: list[float]
    metadata: ContextMetadata
