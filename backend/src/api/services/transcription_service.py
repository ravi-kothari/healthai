"""
Transcription Service for managing audio transcriptions.
Handles audio upload, transcription, and storage.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import UUID
import io

from src.api.models.visit import Transcript, TranscriptionStatus
from src.api.services.ai.speech_service import speech_service

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for managing audio transcriptions."""

    def __init__(self):
        """Initialize transcription service."""
        self.speech_service = speech_service

    async def create_transcription(
        self,
        db: Session,
        visit_id: str,
        audio_data: bytes,
        audio_format: str = "wav",
        language: str = "en-US"
    ) -> Transcript:
        """
        Create a new transcription from audio data.

        Args:
            db: Database session
            visit_id: Visit ID
            audio_data: Audio file bytes
            audio_format: Audio format (wav, mp3, etc.)
            language: Language code (e.g., 'en-US')

        Returns:
            Transcript model instance
        """
        try:
            # Create transcript record
            transcript = Transcript(
                visit_id=visit_id,
                audio_format=audio_format,
                language=language,
                status=TranscriptionStatus.PROCESSING,
                started_at=datetime.utcnow()
            )

            db.add(transcript)
            db.commit()
            db.refresh(transcript)

            logger.info(f"Created transcript {transcript.id} for visit {visit_id}")

            # Perform transcription
            result = await self.speech_service.transcribe_audio_file(
                audio_data=audio_data,
                language=language,
                audio_format=audio_format
            )

            # Update transcript with results
            if "error" in result:
                transcript.status = TranscriptionStatus.FAILED
                transcript.error_message = result["error"]
            else:
                transcript.status = TranscriptionStatus.COMPLETED
                transcript.transcription_text = result["transcription"]
                transcript.confidence_score = result.get("confidence", 0)
                transcript.audio_duration_seconds = result.get("duration_seconds")

            transcript.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(transcript)

            logger.info(f"Completed transcription {transcript.id}, status: {transcript.status}")

            return transcript

        except Exception as e:
            logger.error(f"Transcription error: {e}")

            # Update transcript status to failed
            if 'transcript' in locals():
                transcript.status = TranscriptionStatus.FAILED
                transcript.error_message = str(e)
                transcript.completed_at = datetime.utcnow()
                db.commit()

            raise

    async def get_transcription(
        self,
        db: Session,
        transcript_id: str
    ) -> Optional[Transcript]:
        """
        Get transcription by ID.

        Args:
            db: Database session
            transcript_id: Transcript ID

        Returns:
            Transcript model instance or None
        """
        return db.query(Transcript).filter(Transcript.id == transcript_id).first()

    async def get_visit_transcriptions(
        self,
        db: Session,
        visit_id: str
    ) -> list[Transcript]:
        """
        Get all transcriptions for a visit.

        Args:
            db: Database session
            visit_id: Visit ID

        Returns:
            List of Transcript instances
        """
        return db.query(Transcript).filter(Transcript.visit_id == visit_id).all()

    async def retry_transcription(
        self,
        db: Session,
        transcript_id: str,
        audio_data: bytes
    ) -> Transcript:
        """
        Retry a failed transcription.

        Args:
            db: Database session
            transcript_id: Transcript ID
            audio_data: Audio file bytes

        Returns:
            Updated Transcript instance
        """
        transcript = await self.get_transcription(db, transcript_id)

        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")

        if transcript.status != TranscriptionStatus.FAILED:
            raise ValueError(f"Can only retry failed transcriptions")

        # Reset status
        transcript.status = TranscriptionStatus.PROCESSING
        transcript.error_message = None
        transcript.started_at = datetime.utcnow()
        db.commit()

        # Perform transcription
        result = await self.speech_service.transcribe_audio_file(
            audio_data=audio_data,
            language=transcript.language,
            audio_format=transcript.audio_format
        )

        # Update transcript
        if "error" in result:
            transcript.status = TranscriptionStatus.FAILED
            transcript.error_message = result["error"]
        else:
            transcript.status = TranscriptionStatus.COMPLETED
            transcript.transcription_text = result["transcription"]
            transcript.confidence_score = result.get("confidence", 0)
            transcript.audio_duration_seconds = result.get("duration_seconds")

        transcript.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(transcript)

        return transcript


# Create service instance
transcription_service = TranscriptionService()
