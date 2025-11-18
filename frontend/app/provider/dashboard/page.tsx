import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { getCurrentUser } from "@/lib/auth/middleware";
import type { ScheduledAppointment, PatientListItem, ProviderTask, AppointReadyStatus } from "@/lib/types/dashboard";
import { Calendar, Users, ListTodo, Plus, BriefcaseMedical, TrendingUp, Clock, FileText, Stethoscope, Edit3, Activity, AlertCircle, Sparkles, Star } from "lucide-react";
import Link from "next/link";
import PatientContextCard from "@/components/appoint-ready/PatientContextCard";
import RiskStratification from "@/components/appoint-ready/RiskStratification";
import CareGaps from "@/components/appoint-ready/CareGaps";
import { cookies } from "next/headers";
import { mockTemplates } from "@/lib/data/mockTemplates";

// Mock Data Fetching
async function getProviderDashboardData(providerId: string) {
  const todaysSchedule: ScheduledAppointment[] = [
    { id: "appt-p1", patient: { id: "p1", name: "Jane Cooper" }, time: "09:00 AM", reason: "Follow-up", isNewPatient: false },
    { id: "appt-p2", patient: { id: "p2", name: "Robert Fox" }, time: "09:30 AM", reason: "Annual Physical", isNewPatient: true },
    { id: "appt-p3", patient: { id: "p3", name: "Cody Fisher" }, time: "10:00 AM", reason: "Medication Check", isNewPatient: false },
    { id: "appt-p4", patient: { id: "p4", name: "Esther Howard" }, time: "10:15 AM", reason: "New Complaint", isNewPatient: false },
  ];

  const patientList: PatientListItem[] = [
    { id: "p1", name: "Jane Cooper", lastSeen: "2 weeks ago", appointReadyStatus: "Ready" },
    { id: "p4", name: "Esther Howard", lastSeen: "1 month ago", appointReadyStatus: "Pending" },
    { id: "p2", name: "Robert Fox", lastSeen: "N/A", appointReadyStatus: "Incomplete" },
  ];

  const pendingTasks: ProviderTask[] = [
    { id: "task-p1", description: "Review lab results", patientName: "Jane Cooper", dueDate: "Today", priority: "High" },
    { id: "task-p2", description: "Sign prescription renewal", patientName: "Cody Fisher", dueDate: "Tomorrow", priority: "Medium" },
    { id: "task-p3", description: "Complete chart notes", patientName: "Robert Fox", dueDate: "Today", priority: "High" },
  ];

  const recentVisits = [
    {
      id: "visit-1",
      patientName: "Jane Cooper",
      visitDate: "Today, 9:00 AM",
      chiefComplaint: "Follow-up",
      soapStatus: "completed" as const,
      visitId: "appt-p1"
    },
    {
      id: "visit-2",
      patientName: "Robert Fox",
      visitDate: "Today, 9:30 AM",
      chiefComplaint: "Annual Physical",
      soapStatus: "pending" as const,
      visitId: "appt-p2"
    },
    {
      id: "visit-3",
      patientName: "Cody Fisher",
      visitDate: "Yesterday, 2:00 PM",
      chiefComplaint: "Medication Check",
      soapStatus: "in_progress" as const,
      visitId: "appt-p3"
    },
  ];

  const pendingSOAPNotes = recentVisits.filter(v => v.soapStatus !== 'completed').length;

  return { todaysSchedule, patientList, pendingTasks, recentVisits, pendingSOAPNotes };
}

// Fetch next scheduled appointment from API
async function getNextAppointment() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('token')?.value;

    if (!token) {
      return null;
    }

    const response = await fetch('http://localhost:8000/api/appointments/next', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      cache: 'no-store', // Always fetch fresh data
    });

    if (!response.ok) {
      if (response.status === 404) {
        // No upcoming appointments
        return null;
      }
      throw new Error('Failed to fetch next appointment');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching next appointment:', error);
    return null;
  }
}

const statusColorMap: Record<AppointReadyStatus, string> = {
  Ready: "bg-green-100 text-green-700",
  Pending: "bg-yellow-100 text-yellow-700",
  Incomplete: "bg-red-100 text-red-700",
};

const soapStatusColorMap = {
  completed: "bg-green-100 text-green-700",
  in_progress: "bg-blue-100 text-blue-700",
  pending: "bg-orange-100 text-orange-700",
};

const soapStatusLabelMap = {
  completed: "Complete",
  in_progress: "In Progress",
  pending: "Not Started",
};

export default async function ProviderDashboardPage() {
  const user = await getCurrentUser();
  if (!user) return null;

  const { todaysSchedule, patientList, pendingTasks, recentVisits, pendingSOAPNotes } = await getProviderDashboardData(user.id);

  // Fetch next appointment for ContextAI
  const nextAppointment = await getNextAppointment();

  // Get user's templates
  const userTemplates = mockTemplates.filter(t => t.type === 'personal' && t.metadata.isFavorite);
  const recentTemplates = mockTemplates.filter(t => t.type === 'personal').slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Hero Header with Gradient Background */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white py-8 px-6 rounded-2xl shadow-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white">Provider Dashboard</h1>
            <p className="text-slate-300 mt-2 flex items-center gap-2">
              Welcome back, {user.name}
            </p>
          </div>
          <div className="flex gap-2 shrink-0 flex-wrap">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="bg-white/10 text-white hover:bg-white/20 border border-white/20">
                📊 SaaS
              </Button>
            </Link>
            <Link href="/dashboard/calendar">
              <Button variant="ghost" size="sm" className="bg-white/10 text-white hover:bg-white/20 border border-white/20">
                <BriefcaseMedical className="w-4 h-4 mr-2" /> Schedule
              </Button>
            </Link>
            <Link href="/provider/templates">
              <Button variant="ghost" size="sm" className="bg-white/10 text-white hover:bg-white/20 border border-white/20">
                <FileText className="w-4 h-4 mr-2" /> Templates
              </Button>
            </Link>
            <Button variant="primary" size="sm" className="bg-forest-600 hover:bg-forest-700">
              <Plus className="w-4 h-4 mr-2" /> New Patient
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Cards - Modernized with colored icon backgrounds */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card variant="elevated" className="hover:scale-105 transition-transform duration-200">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-1.5">Patients Today</p>
                <h3 className="text-3xl font-bold text-slate-900">{todaysSchedule.length}</h3>
                <p className="text-xs text-forest-600 flex items-center gap-1 mt-2 font-medium">
                  <TrendingUp className="w-3.5 h-3.5" />
                  +3 from yesterday
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="hover:scale-105 transition-transform duration-200">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-1.5">Pending Tasks</p>
                <h3 className="text-3xl font-bold text-slate-900">{pendingTasks.length}</h3>
                <p className="text-xs text-slate-600 mt-2">
                  {pendingTasks.filter(t => t.priority === 'High').length} high priority
                </p>
              </div>
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <ListTodo className="h-6 w-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="hover:scale-105 transition-transform duration-200">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-1.5">ContextAI</p>
                <h3 className="text-3xl font-bold text-slate-900">
                  {patientList.filter(p => p.appointReadyStatus === 'Ready').length}
                </h3>
                <p className="text-xs text-slate-600 mt-2">Ready for visit</p>
              </div>
              <div className="w-12 h-12 bg-forest-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Clock className="h-6 w-6 text-forest-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated" className="hover:scale-105 transition-transform duration-200">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-1.5">SOAP Notes</p>
                <h3 className="text-3xl font-bold text-slate-900">{pendingSOAPNotes}</h3>
                <p className="text-xs text-slate-600 mt-2">
                  {pendingSOAPNotes > 0 ? 'Pending documentation' : 'All complete ✓'}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <FileText className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Link href="/provider/templates">
          <Card variant="elevated" className="hover:scale-105 transition-transform duration-200 cursor-pointer">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-slate-600 mb-1.5">My Templates</p>
                  <h3 className="text-3xl font-bold text-slate-900">{mockTemplates.filter(t => t.type === 'personal').length}</h3>
                  <p className="text-xs text-forest-600 flex items-center gap-1 mt-2 font-medium">
                    <Sparkles className="w-3.5 h-3.5" />
                    {userTemplates.length} favorited
                  </p>
                </div>
                <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Sparkles className="h-6 w-6 text-amber-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                Today's Schedule
              </CardTitle>
              <CardDescription>{todaysSchedule.length} appointments scheduled for today</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {todaysSchedule.map(appt => (
                  <li key={appt.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="font-mono text-sm bg-blue-50 text-blue-700 px-3 py-2 rounded font-semibold">
                        {appt.time}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">{appt.patient.name}</span>
                          {appt.isNewPatient && (
                            <Badge className="bg-cyan-100 text-cyan-700 text-xs">New Patient</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{appt.reason}</p>
                      </div>
                    </div>
                    <Link href={`/provider/visits/${appt.id}`}>
                      <Button variant="outline" size="sm">Document Visit</Button>
                    </Link>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* SOAP Notes Status Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Stethoscope className="w-5 h-5 text-purple-600" />
                Recent Visits & SOAP Notes
              </CardTitle>
              <CardDescription>Documentation status for recent patient encounters</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {recentVisits.map(visit => (
                  <li key={visit.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-gray-900">{visit.patientName}</span>
                        <Badge className={soapStatusColorMap[visit.soapStatus]}>
                          {soapStatusLabelMap[visit.soapStatus]}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{visit.chiefComplaint}</p>
                      <p className="text-xs text-gray-500 mt-1">{visit.visitDate}</p>
                    </div>
                    <Link href={`/provider/visits/${visit.visitId}`}>
                      <Button variant="outline" size="sm">
                        {visit.soapStatus === 'completed' ? (
                          <>
                            <FileText className="w-4 h-4 mr-2" />
                            View
                          </>
                        ) : (
                          <>
                            <Edit3 className="w-4 h-4 mr-2" />
                            Document
                          </>
                        )}
                      </Button>
                    </Link>
                  </li>
                ))}
              </ul>
              {pendingSOAPNotes > 0 && (
                <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <p className="text-sm text-orange-800 font-medium">
                    ⚠️ {pendingSOAPNotes} visit{pendingSOAPNotes > 1 ? 's' : ''} need documentation
                  </p>
                  <p className="text-xs text-orange-700 mt-1">
                    Complete SOAP notes to ensure accurate patient records
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-gray-600" />
                Patient Watchlist
              </CardTitle>
              <CardDescription>ContextAI status for upcoming visits</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {patientList.map(p => (
                  <li key={p.id} className="flex justify-between items-center p-2 rounded hover:bg-gray-50">
                    <div>
                      <p className="font-medium text-gray-900">{p.name}</p>
                      <p className="text-xs text-gray-500">Last seen: {p.lastSeen}</p>
                    </div>
                    <Badge className={statusColorMap[p.appointReadyStatus]}>
                      {p.appointReadyStatus}
                    </Badge>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ListTodo className="w-5 h-5 text-gray-600" />
                Pending Tasks
              </CardTitle>
              <CardDescription>Items requiring your attention</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {pendingTasks.map(task => (
                  <li key={task.id} className="border-b pb-3 last:border-b-0">
                    <div className="flex justify-between items-start mb-1">
                      <p className="font-semibold text-sm text-gray-900">{task.description}</p>
                      <Badge className={task.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}>
                        {task.priority}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500">
                      For: <span className="font-medium">{task.patientName}</span> &bull; Due: {task.dueDate}
                    </p>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Quick Access Templates Card */}
          <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-600" />
                  Quick Templates
                </CardTitle>
                <Link href="/provider/templates">
                  <Button variant="ghost" size="sm" className="text-amber-700 hover:text-amber-900">
                    View All
                  </Button>
                </Link>
              </div>
              <CardDescription>Recently used templates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentTemplates.map((template) => (
                  <div
                    key={template.id}
                    className="p-3 bg-white rounded-lg border border-amber-200 hover:border-amber-300 hover:shadow-sm transition-all cursor-pointer group"
                  >
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-semibold text-sm text-slate-900 truncate group-hover:text-forest-600">
                            {template.name}
                          </p>
                          {template.metadata.isFavorite && (
                            <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500 flex-shrink-0" />
                          )}
                        </div>
                        <p className="text-xs text-slate-600 line-clamp-1">
                          {template.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" size="sm">
                        {template.metadata.category}
                      </Badge>
                      <span className="text-xs text-slate-500">
                        {template.metadata.usageCount} uses
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <Link href="/provider/templates">
                <Button variant="primary" size="sm" className="w-full mt-4 bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Create New Template
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* ContextAI Section */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-600" />
              ContextAI: Next Patient
            </h2>
            <p className="text-gray-600 mt-1">
              {nextAppointment
                ? `Appointment at ${new Date(nextAppointment.scheduled_start).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`
                : 'No upcoming appointments scheduled'}
            </p>
          </div>
          {nextAppointment && (
            <Badge className={nextAppointment.is_today ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}>
              {nextAppointment.is_today ? 'Today' : 'Upcoming'}
            </Badge>
          )}
        </div>

        {nextAppointment ? (
          <>
            {/* Appointment Info Card */}
            <Card className="mb-6 border-blue-200 bg-blue-50">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Patient</p>
                    <p className="font-semibold text-gray-900">{nextAppointment.patient?.name}</p>
                    <p className="text-xs text-gray-500">MRN: {nextAppointment.patient?.mrn}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Chief Complaint</p>
                    <p className="font-medium text-gray-900">{nextAppointment.chief_complaint}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">CarePrep Status</p>
                    <Badge className={nextAppointment.previsit_completed ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}>
                      {nextAppointment.previsit_completed ? 'Completed' : 'Pending'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 gap-6">
              {/* Patient Context */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Patient Context</h3>
                <PatientContextCard patientId={nextAppointment.patient_id} />
              </div>

              {/* Risk Stratification */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Risk Stratification</h3>
                <RiskStratification patientId={nextAppointment.patient_id} />
              </div>

              {/* Care Gaps */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Care Gaps</h3>
                <CareGaps patientId={nextAppointment.patient_id} />
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>📋 ContextAI:</strong> This information is automatically generated from the patient's CarePrep responses, medical history, and FHIR data to help you prepare for the appointment.
              </p>
            </div>
          </>
        ) : (
          <Card className="border-gray-200">
            <CardContent className="py-12 text-center">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Upcoming Appointments</h3>
              <p className="text-gray-600 mb-6">
                You don't have any scheduled appointments at the moment.
              </p>
              <Button>
                <Calendar className="w-4 h-4 mr-2" />
                View All Appointments
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
