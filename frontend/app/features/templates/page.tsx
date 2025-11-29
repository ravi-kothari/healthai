import { ComingSoon } from '@/components/layout/ComingSoon';

export default function ClinicalTemplatesPage() {
  return (
    <ComingSoon
      title="Smart Clinical Templates"
      description="Specialty-specific SOAP note templates that learn from your documentation patterns. Get AI-powered suggestions that adapt to your practice style."
      estimatedLaunch="Available Now in Beta"
      features={[
        "Specialty-specific templates (Family Med, Cardiology, Pediatrics, etc.)",
        "AI-powered auto-completion",
        "Custom template builder",
        "ICD-10 and CPT code suggestions",
        "Billing-optimized documentation",
        "Quality measure tracking",
      ]}
    />
  );
}
