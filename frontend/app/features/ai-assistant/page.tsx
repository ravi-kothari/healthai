import { ComingSoon } from '@/components/layout/ComingSoon';

export default function AIAssistantPage() {
  return (
    <ComingSoon
      title="AI Clinical Assistant"
      description="Your intelligent companion for smarter clinical decisions. Get AI-powered recommendations, drug interaction alerts, and evidence-based insights right when you need them."
      estimatedLaunch="Coming Q1 2025"
      features={[
        "Real-time clinical decision support",
        "Drug interaction checking",
        "Differential diagnosis suggestions",
        "Evidence-based treatment recommendations",
        "Lab result interpretation",
        "Clinical guideline integration",
      ]}
    />
  );
}
