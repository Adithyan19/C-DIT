import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Float,
    Integer,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    farmer = "farmer"
    mitl = "mitl"
    superadmin = "superadmin"


class MessageSender(str, enum.Enum):
    user = "user"
    bot = "bot"


class ContentType(str, enum.Enum):
    text = "text"
    image = "image"
    voice = "voice"
    mixed = "mixed"


class DiseaseStatus(str, enum.Enum):
    pending = "pending"
    classified = "classified"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.farmer.value, nullable=False)
    location = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), default="New Conversation")
    started_at = Column(DateTime, default=datetime.utcnow)
    last_location_lat = Column(Float, nullable=True)
    last_location_lng = Column(Float, nullable=True)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True
    )
    sender = Column(SAEnum(MessageSender), nullable=False)
    content_type = Column(SAEnum(ContentType), default=ContentType.text)
    text_content = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
    voice_url = Column(String(1000), nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    unknown_disease = relationship("UnknownDisease", back_populates="message", uselist=False)


class UnknownDisease(Base):
    __tablename__ = "unknown_diseases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(
        UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False, unique=True, index=True
    )
    image_url = Column(String(1000), nullable=True)
    text_symptoms = Column(Text, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    status = Column(SAEnum(DiseaseStatus), default=DiseaseStatus.pending)
    disease_name = Column(String(255), nullable=True)
    solution = Column(Text, nullable=True)
    classified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    classified_at = Column(DateTime, nullable=True)

    message = relationship("Message", back_populates="unknown_disease")
    classifier = relationship("User", foreign_keys=[classified_by])


class DiseaseKnowledge(Base):
    __tablename__ = "disease_knowledge"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop = Column(String(255), nullable=False, index=True)
    disease_name = Column(String(255), nullable=False, index=True)
    symptom = Column(Text, nullable=True)
    position = Column(String(255), nullable=True)
    pattern = Column(String(255), nullable=True)
    weather = Column(String(255), nullable=True)
    treatment_summary = Column(Text, nullable=False)
    image_urls = Column(JSON, default=list)
    region = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LeafImage(Base):
    __tablename__ = "leaf_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_path = Column(Text, nullable=False, unique=True)
    predicted = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    verified = Column(Boolean, default=False)
    true_label = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
