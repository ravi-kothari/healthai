import { ComingSoon } from '@/components/layout/ComingSoon';

export default function PatientContextPage() {
  return (
    <ComingSoon
      title="MediGenie Context"
      description="Get comprehensive patient information at your fingertips. See the full picture before every appointment with AI-powered context building and risk stratification."
      estimatedLaunch="Available Now in Beta"
      features={[
        "Complete patient history timeline",
        "Active medications and allergies",
        "Recent lab results and vitals",
        "Care gap identification",
        "Risk stratification scores",
        "Smart appointment preparation",
      ]}
    />
  );
}
