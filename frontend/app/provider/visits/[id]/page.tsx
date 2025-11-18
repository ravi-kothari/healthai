import { getCurrentUser } from "@/lib/auth/middleware";
import VisitWorkflow from "@/components/visit/VisitWorkflow";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ArrowLeft, User, Calendar, FileText } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/Badge";

// Mock function to get visit details
async function getVisit(visitId: string) {
  return {
    id: visitId,
    patient_id: "patient-123",
    patient_name: "Jane Cooper",
    provider_id: "provider-456",
    visit_type: "Follow-up",
    status: "in_progress" as const,
    chief_complaint: "Persistent headache",
    reason_for_visit: "Follow-up on medication changes",
    scheduled_start: new Date().toISOString(),
    actual_start: new Date().toISOString(),
  };
}

export default async function VisitPage({ params }: { params: { id: string } }) {
  const user = await getCurrentUser();
  if (!user) return null;

  const visit = await getVisit(params.id);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/provider/dashboard" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Visit Documentation</h1>
          <p className="text-gray-600">Complete clinical documentation</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Visit Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-gray-500">Patient</p>
              <p className="font-semibold text-gray-900">{visit.patient_name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Visit Type</p>
              <p className="font-semibold text-gray-900">{visit.visit_type}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Chief Complaint</p>
              <p className="font-semibold text-gray-900">{visit.chief_complaint}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <VisitWorkflow visitId={params.id} />
    </div>
  );
}
