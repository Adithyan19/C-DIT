from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# --- Auth ---
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class CreateMitlRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# --- User ---
class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    location: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    location: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# --- Conversation ---
class ConversationResponse(BaseModel):
    id: UUID
    title: str
    started_at: datetime
    last_location_lat: Optional[float] = None
    last_location_lng: Optional[float] = None

    model_config = {"from_attributes": True}


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"


# --- Message ---
class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender: str
    content_type: str
    text_content: Optional[str] = None
    image_url: Optional[str] = None
    voice_url: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Unknown Disease ---
class UnknownDiseaseResponse(BaseModel):
    id: UUID
    message_id: UUID
    image_url: Optional[str] = None
    text_symptoms: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    status: str
    disease_name: Optional[str] = None
    solution: Optional[str] = None
    classified_by: Optional[UUID] = None
    created_at: datetime
    classified_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ClassifyDiseaseRequest(BaseModel):
    disease_name: str
    solution: str
    region: Optional[str] = None


# --- Disease Knowledge ---
class DiseaseKnowledgeResponse(BaseModel):
    id: UUID
    crop: str
    disease_name: str
    symptom: Optional[str] = None
    position: Optional[str] = None
    pattern: Optional[str] = None
    weather: Optional[str] = None
    treatment_summary: str
    image_urls: List[str] = []
    region: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Dashboard Stats ---
class DashboardStatsResponse(BaseModel):
    pending_count: int
    classified_count: int
    total_farmers: int
    total_conversations: int
