from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from app.database import get_db
from app.models import User, Conversation, Message, MessageSender, ContentType
from app.deps import get_current_user
from app.schemas import ConversationResponse, MessageResponse, CreateConversationRequest
from app.storage import upload_image, upload_voice
from app.disease_engine import analyze_message
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    req: CreateConversationRequest = CreateConversationRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = Conversation(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=req.title or "New Conversation",
        started_at=datetime.utcnow(),
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.started_at))
    )
    return [ConversationResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify conversation belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return [MessageResponse.model_validate(m) for m in result.scalars().all()]


@router.post("/messages", response_model=List[MessageResponse])
async def send_message(
    conversation_id: str = Form(...),
    text: Optional[str] = Form(None),
    location_lat: Optional[float] = Form(None),
    location_lng: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    voice: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify conversation belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Update conversation location
    if location_lat is not None:
        conv.last_location_lat = location_lat
        conv.last_location_lng = location_lng

    # Determine content type
    has_text = bool(text and text.strip())
    has_image = image is not None
    has_voice = voice is not None

    if not has_text and not has_image and not has_voice:
        raise HTTPException(status_code=400, detail="Message must contain text, image, or voice")

    content_type = ContentType.text
    if has_image and has_text:
        content_type = ContentType.mixed
    elif has_image:
        content_type = ContentType.image
    elif has_voice:
        content_type = ContentType.voice

    # Upload files
    image_url = None
    voice_url = None
    if has_image:
        image_bytes = await image.read()
        image_url = await upload_image(image_bytes, image.filename or "image.jpg")
    if has_voice:
        voice_bytes = await voice.read()
        voice_url = await upload_voice(voice_bytes, voice.filename or "voice.webm")

    # If voice, simulate transcription
    voice_text = None
    if has_voice and not has_text:
        voice_text = "[Voice message received - transcription pending]"

    # Create user message
    user_msg = Message(
        id=uuid.uuid4(),
        conversation_id=conv.id,
        sender=MessageSender.user,
        content_type=content_type,
        text_content=text if has_text else voice_text,
        image_url=image_url,
        voice_url=voice_url,
        location_lat=location_lat,
        location_lng=location_lng,
        created_at=datetime.utcnow(),
    )
    db.add(user_msg)
    await db.flush()

    # Get conversation history for context
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    history = result.scalars().all()

    # Auto-title conversation from first message
    if len(history) <= 1 and has_text:
        conv.title = (text[:50] + "...") if len(text) > 50 else text

    # Get bot response
    analysis = await analyze_message(
        db=db,
        text=text if has_text else voice_text,
        image_url=image_url,
        conversation_messages=list(history),
        location_lat=location_lat,
        location_lng=location_lng,
        message=user_msg,
    )

    # Create bot message
    bot_msg = Message(
        id=uuid.uuid4(),
        conversation_id=conv.id,
        sender=MessageSender.bot,
        content_type=ContentType.text,
        text_content=analysis["response_text"],
        created_at=datetime.utcnow(),
    )
    db.add(bot_msg)
    await db.commit()

    await db.refresh(user_msg)
    await db.refresh(bot_msg)

    return [
        MessageResponse.model_validate(user_msg),
        MessageResponse.model_validate(bot_msg),
    ]
