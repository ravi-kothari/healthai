import { ComingSoon } from '@/components/layout/ComingSoon';

export default function GuidesPage() {
  return (
    <ComingSoon
      title="Guides & Resources"
      description="Comprehensive documentation, video tutorials, and best practices to help you master MediGenie. From quick setup to advanced workflows."
      estimatedLaunch="Growing Library - New Guides Weekly"
      features={[
        "Getting started in 5 minutes",
        "Video tutorials for every feature",
        "Specialty-specific best practices",
        "Workflow optimization guides",
        "Troubleshooting and FAQs",
        "Integration setup walkthroughs",
      ]}
    />
  );
}
