import PlaceholderPage from '@/components/PlaceholderPage';
import { Lock } from 'lucide-react';

export default function SecurityPage() {
  return (
    <PlaceholderPage
      title="Security & Compliance"
      description="Bank-grade security, HIPAA compliance, and SOC 2 certification. Your patient data is always protected."
      icon={Lock}
    />
  );
}
