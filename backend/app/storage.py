import httpx
import uuid
from app.config import settings


async def upload_file_to_supabase(
    file_bytes: bytes, filename: str, bucket: str, content_type: str = "image/jpeg"
) -> str:
    """Upload a file to Supabase Storage and return the public URL."""
    # Generate a unique filename
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_url = f"{settings.SUPABASE_STORAGE_URL}/object/{bucket}/{unique_name}"

    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": content_type,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(upload_url, content=file_bytes, headers=headers)
        if response.status_code not in (200, 201):
            # Try to create bucket first if it doesn't exist
            create_url = f"{settings.SUPABASE_STORAGE_URL}/bucket"
            await client.post(
                create_url,
                json={"id": bucket, "name": bucket, "public": True},
                headers={"Authorization": f"Bearer {settings.SUPABASE_KEY}",
                         "Content-Type": "application/json"},
            )
            # Retry upload
            response = await client.post(
                upload_url, content=file_bytes, headers=headers
            )

    # Public URL
    public_url = f"{settings.SUPABASE_STORAGE_URL}/object/public/{bucket}/{unique_name}"
    return public_url


async def upload_image(file_bytes: bytes, filename: str) -> str:
    return await upload_file_to_supabase(
        file_bytes, filename, settings.SUPABASE_IMAGE_BUCKET, "image/jpeg"
    )


async def upload_voice(file_bytes: bytes, filename: str) -> str:
    return await upload_file_to_supabase(
        file_bytes, filename, settings.SUPABASE_VOICE_BUCKET, "audio/webm"
    )
