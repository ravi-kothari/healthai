"""
Azure Speech Service for audio transcription.
Supports both mock mode (local development) and real Azure Speech-to-Text.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import io

from src.api.config import settings

logger = logging.getLogger(__name__)


class MockSpeechService:
    """Mock Speech Service for local development."""

    def __init__(self):
        logger.info("Using mock Speech service for local development")

    async def transcribe_audio_file(
        self,
        audio_data: bytes,
        language: str = "en-US",
        audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Mock transcription of an audio file.

        Args:
            audio_data: Audio file bytes
            language: Language code (e.g., 'en-US')
            audio_format: Audio format (e.g., 'wav', 'mp3')

        Returns:
            Dict with transcription results
        """
        # Simulate processing
        audio_size_mb = len(audio_data) / (1024 * 1024)
        duration_seconds = int(audio_size_mb * 60)  # Rough estimate

        # Mock transcription text
        mock_text = """
        Patient presents with chief complaint of headache for 3 days.
        Patient reports the headache is localized to the frontal region,
        described as a dull, constant pain, rated 6 out of 10 in severity.
        Associated symptoms include photophobia and mild nausea.
        No vomiting, no fever, no neck stiffness.
        Patient has tried over-the-counter ibuprofen with minimal relief.
        Past medical history is significant for migraines.
        Current medications include oral contraceptives.
        No known drug allergies.
        Physical examination reveals blood pressure 120/80,
        heart rate 72, temperature 98.6 Fahrenheit.
        Neurological examination is within normal limits.
        No focal deficits noted.
        Assessment: Migraine headache.
        Plan: Prescribe sumatriptan 50 mg as needed for headache.
        Recommend follow-up in 2 weeks if symptoms persist.
        Advised patient to keep a headache diary.
        """

        return {
            "transcription": mock_text.strip(),
            "confidence": 95,
            "language": language,
            "duration_seconds": duration_seconds,
            "audio_format": audio_format,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def transcribe_audio_stream(
        self,
        audio_stream: io.BytesIO,
        language: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Mock real-time transcription from audio stream.

        Args:
            audio_stream: Audio stream
            language: Language code

        Returns:
            Dict with transcription results
        """
        # Read stream data
        audio_data = audio_stream.read()

        return await self.transcribe_audio_file(
            audio_data=audio_data,
            language=language,
            audio_format="stream"
        )


class AzureSpeechService:
    """Real Azure Speech-to-Text Service."""

    def __init__(self):
        """Initialize Azure Speech Service."""
        try:
            import azure.cognitiveservices.speech as speechsdk

            self.speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION
            )
            logger.info(f"Azure Speech Service initialized for region: {settings.AZURE_SPEECH_REGION}")

        except ImportError:
            logger.error("azure-cognitiveservices-speech package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech Service: {e}")
            raise

    async def transcribe_audio_file(
        self,
        audio_data: bytes,
        language: str = "en-US",
        audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Azure Speech-to-Text.

        Args:
            audio_data: Audio file bytes
            language: Language code (e.g., 'en-US')
            audio_format: Audio format (e.g., 'wav', 'mp3')

        Returns:
            Dict with transcription results
        """
        import azure.cognitiveservices.speech as speechsdk

        try:
            # Set recognition language
            self.speech_config.speech_recognition_language = language

            # Create audio stream from bytes
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_stream.write(audio_data)
            audio_stream.close()

            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

            # Create speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            # Perform recognition
            result = speech_recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "transcription": result.text,
                    "confidence": int(result.properties.get(
                        speechsdk.PropertyId.SpeechServiceResponse_JsonResult, {}).get("NBest", [{}])[0].get("Confidence", 0) * 100),
                    "language": language,
                    "audio_format": audio_format,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized")
                return {
                    "transcription": "",
                    "confidence": 0,
                    "language": language,
                    "audio_format": audio_format,
                    "error": "No speech recognized",
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                logger.error(f"Speech recognition canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {cancellation.error_details}")

                return {
                    "transcription": "",
                    "confidence": 0,
                    "language": language,
                    "audio_format": audio_format,
                    "error": f"Recognition canceled: {cancellation.error_details}",
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "transcription": "",
                "confidence": 0,
                "language": language,
                "audio_format": audio_format,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def transcribe_audio_stream(
        self,
        audio_stream: io.BytesIO,
        language: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Real-time transcription from audio stream.

        Args:
            audio_stream: Audio stream
            language: Language code

        Returns:
            Dict with transcription results
        """
        # For streaming, read the entire stream and process as file
        # In production, you'd use continuous recognition
        audio_data = audio_stream.read()

        return await self.transcribe_audio_file(
            audio_data=audio_data,
            language=language,
            audio_format="stream"
        )


# Initialize the appropriate service based on configuration
if settings.USE_MOCK_SPEECH:
    speech_service = MockSpeechService()
else:
    speech_service = AzureSpeechService()
