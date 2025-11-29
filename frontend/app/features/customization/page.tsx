import { ComingSoon } from '@/components/layout/ComingSoon';

export default function CustomizationPage() {
  return (
    <ComingSoon
      title="Custom Workflows"
      description="Tailor MediGenie to match your unique practice. Create custom templates, shortcuts, and workflows that adapt to how you work, not the other way around."
      estimatedLaunch="Coming Q2 2025"
      features={[
        "Custom note templates",
        "Personalized keyboard shortcuts",
        "Workflow automation rules",
        "Practice-specific forms",
        "Custom data fields",
        "White-label branding options",
      ]}
    />
  );
}
