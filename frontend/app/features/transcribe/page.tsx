import { ComingSoon } from '@/components/layout/ComingSoon';

export default function TranscribePage() {
  return (
    <ComingSoon
      title="MediGenie Ambient Scribe"
      description="Real-time medical transcription powered by AI. Dictate naturally during patient visits and watch your conversation transform into structured SOAP notes automatically."
      estimatedLaunch="Available Now in Beta"
      features={[
        "Hands-free voice documentation",
        "Real-time transcription with medical terminology",
        "Auto-generation of SOAP notes",
        "Speaker identification (doctor vs patient)",
        "Multilingual support",
        "HIPAA-compliant cloud processing",
      ]}
    />
  );
}
