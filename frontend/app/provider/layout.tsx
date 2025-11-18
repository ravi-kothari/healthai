import { requireRole } from "@/lib/auth/middleware";
import { ProviderHeader } from "@/components/layout/ProviderHeader";

export default async function ProviderLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Enforce provider role requirement
  await requireRole("provider");

  return (
    <div className="min-h-screen bg-gray-50">
      <ProviderHeader />
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        {children}
      </main>
    </div>
  );
}
