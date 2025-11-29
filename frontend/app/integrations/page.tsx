import { ComingSoon } from '@/components/layout/ComingSoon';

export default function IntegrationsPage() {
  return (
    <ComingSoon
      title="EHR & System Integrations"
      description="Seamlessly connect MediGenie with your existing healthcare systems. FHIR R4 compatible with bi-directional sync for major EHRs and practice management platforms."
      estimatedLaunch="Expanding - New Integrations Monthly"
      features={[
        "Epic, Cerner, Athenahealth integrations",
        "FHIR R4 API compatibility",
        "Bi-directional data sync",
        "Practice management systems (Kareo, DrChrono, AdvancedMD)",
        "Lab integrations (Quest, LabCorp)",
        "Secure webhook notifications",
      ]}
    />
  );
}
