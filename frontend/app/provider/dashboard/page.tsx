'use client';

import { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, Users, ListTodo, Plus, TrendingUp, Clock, FileText, Stethoscope, Edit3, Sparkles, ClipboardList, Send, Eye, AlertTriangle, Target, Activity } from "lucide-react";
import Link from "next/link";
import { useAuthStore } from '@/lib/stores/authStore';
import PreVisitPrepModal from '@/components/provider/PreVisitPrepModal';

type CareprepStatus = 'not_sent' | 'pending' | 'completed';
type AppointReadyStatus = 'Ready' | 'Pending' | 'Incomplete';
type RiskLevel = 'high' | 'medium' | 'low';

interface ScheduledAppointment {
  id: string;
  patient: { id: string; name: string };
  time: string;
  reason: string;
  isNewPatient: boolean;
  careprepStatus: CareprepStatus;
  riskLevel: RiskLevel;
  careGapsCount: number;
}

interface PatientListItem {
  id: string;
  name: string;
  lastSeen: string;
  appointReadyStatus: AppointReadyStatus;
}

interface ProviderTask {
  id: string;
  description: string;
  patientName: string;
  dueDate: string;
  priority: 'High' | 'Medium' | 'Low';
}

interface RecentVisit {
  id: string;
  patientName: string;
  visitDate: string;
  chiefComplaint: string;
  soapStatus: 'completed' | 'in_progress' | 'pending';
  visitId: string;
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

const riskColorMap: Record<RiskLevel, string> = {
  high: "bg-red-100 text-red-700 border-red-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  low: "bg-green-100 text-green-700 border-green-200",
};

// Mock data with context badges
const todaysSchedule: ScheduledAppointment[] = [
  { id: "appt-p1", patient: { id: "p1", name: "Jane Cooper" }, time: "09:00 AM", reason: "Follow-up", isNewPatient: false, careprepStatus: "completed", riskLevel: "medium", careGapsCount: 2 },
  { id: "appt-p2", patient: { id: "p2", name: "Robert Fox" }, time: "09:30 AM", reason: "Annual Physical", isNewPatient: true, careprepStatus: "pending", riskLevel: "low", careGapsCount: 0 },
  { id: "appt-p3", patient: { id: "p3", name: "Cody Fisher" }, time: "10:00 AM", reason: "Medication Check", isNewPatient: false, careprepStatus: "not_sent", riskLevel: "high", careGapsCount: 4 },
  { id: "appt-p4", patient: { id: "p4", name: "Esther Howard" }, time: "10:15 AM", reason: "New Complaint", isNewPatient: false, careprepStatus: "not_sent", riskLevel: "medium", careGapsCount: 1 },
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

const recentVisits: RecentVisit[] = [
  { id: "visit-1", patientName: "Jane Cooper", visitDate: "Today, 9:00 AM", chiefComplaint: "Follow-up", soapStatus: "completed", visitId: "appt-p1" },
  { id: "visit-2", patientName: "Robert Fox", visitDate: "Today, 9:30 AM", chiefComplaint: "Annual Physical", soapStatus: "pending", visitId: "appt-p2" },
  { id: "visit-3", patientName: "Cody Fisher", visitDate: "Yesterday, 2:00 PM", chiefComplaint: "Medication Check", soapStatus: "in_progress", visitId: "appt-p3" },
];

export default function ProviderDashboardPage() {
  // Auth is handled by the layout - no need to check here
  const { user } = useAuthStore();
  const [selectedAppointment, setSelectedAppointment] = useState<ScheduledAppointment | null>(null);

  const pendingSOAPNotes = recentVisits.filter(v => v.soapStatus !== 'completed').length;
  const highRiskPatients = todaysSchedule.filter(a => a.riskLevel === 'high').length;

  return (
    <div className="space-y-6">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white py-8 px-6 rounded-2xl shadow-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white">Provider Dashboard</h1>
            <p className="text-slate-300 mt-2">Welcome back, {user?.full_name || user?.email || 'Provider'}</p>
          </div>
          <div className="flex gap-2 shrink-0 flex-wrap">
            <Link href="/provider/templates">
              <Button variant="ghost" size="sm" className="bg-white/10 text-white hover:bg-white/20 border border-white/20">
                <FileText className="w-4 h-4 mr-2" /> Templates
              </Button>
            </Link>
            <Link href="/careprep">
              <Button variant="ghost" size="sm" className="bg-white/10 text-white hover:bg-white/20 border border-white/20">
                <Stethoscope className="w-4 h-4 mr-2" /> CarePrep
              </Button>
            </Link>
            <Link href="/provider/visits/new">
              <Button variant="primary" size="sm" className="bg-purple-600 hover:bg-purple-700">
                <Plus className="w-4 h-4 mr-2" /> New Visit
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Cards - Now Clickable */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Today's Appointments */}
        <Link href="/provider/calendar">
          <Card className="hover:scale-105 transition-transform duration-200 cursor-pointer hover:shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-slate-600 mb-1.5">Today's Appointments</p>
                  <h3 className="text-3xl font-bold text-slate-900">{todaysSchedule.length}</h3>
                  <p className="text-xs text-blue-600 flex items-center gap-1 mt-2 font-medium">
                    <Calendar className="w-3.5 h-3.5" />
                    View calendar
                  </p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>

        {/* High Risk Patients */}
        <Card className="hover:scale-105 transition-transform duration-200 cursor-pointer hover:shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-1.5">High Risk Patients</p>
                <h3 className="text-3xl font-bold text-red-600">{highRiskPatients}</h3>
                <p className="text-xs text-red-600 flex items-center gap-1 mt-2 font-medium">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Need attention today
                </p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Incomplete Documentation */}
        <Card className="hover:scale-105 transition-transform duration-200 cursor-pointer hover:shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-1.5">Incomplete Notes</p>
                <h3 className="text-3xl font-bold text-slate-900">{pendingSOAPNotes}</h3>
                <p className="text-xs text-orange-600 flex items-center gap-1 mt-2 font-medium">
                  <FileText className="w-3.5 h-3.5" />
                  {pendingSOAPNotes > 0 ? 'Complete documentation' : 'All caught up! ✓'}
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                <FileText className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Care Gaps Identified */}
        <Card className="hover:scale-105 transition-transform duration-200 cursor-pointer hover:shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-slate-600 mb-1.5">Care Gaps Today</p>
                <h3 className="text-3xl font-bold text-slate-900">
                  {todaysSchedule.reduce((acc, a) => acc + a.careGapsCount, 0)}
                </h3>
                <p className="text-xs text-purple-600 flex items-center gap-1 mt-2 font-medium">
                  <Target className="w-3.5 h-3.5" />
                  {todaysSchedule.filter(a => a.careGapsCount > 0).length} patients affected
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Schedule with Context Badges */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-blue-600" />
                    Today's Schedule
                  </CardTitle>
                  <CardDescription>{todaysSchedule.length} appointments • Click patient name for pre-visit prep</CardDescription>
                </div>
                <Badge className="bg-blue-100 text-blue-700">
                  <Activity className="w-3 h-3 mr-1" />
                  ContextAI Enabled
                </Badge>
              </div>
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
                        <div className="flex items-center gap-2 flex-wrap">
                          {/* Clickable patient name opens Pre-Visit Prep */}
                          <button
                            onClick={() => setSelectedAppointment(appt)}
                            className="font-semibold text-gray-900 hover:text-blue-600 hover:underline transition-colors"
                          >
                            {appt.patient.name}
                          </button>
                          {appt.isNewPatient && (
                            <Badge className="bg-cyan-100 text-cyan-700 text-xs">New</Badge>
                          )}
                          {/* Risk Badge */}
                          <Badge className={`text-xs ${riskColorMap[appt.riskLevel]}`}>
                            {appt.riskLevel === 'high' && <AlertTriangle className="w-3 h-3 mr-1" />}
                            {appt.riskLevel.charAt(0).toUpperCase() + appt.riskLevel.slice(1)} Risk
                          </Badge>
                          {/* Care Gaps Badge */}
                          {appt.careGapsCount > 0 && (
                            <Badge className="bg-purple-100 text-purple-700 text-xs">
                              <Target className="w-3 h-3 mr-1" />
                              {appt.careGapsCount} Gaps
                            </Badge>
                          )}
                          {/* CarePrep Status */}
                          {appt.careprepStatus === "completed" && (
                            <Badge className="bg-green-100 text-green-700 text-xs">CarePrep ✓</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{appt.reason}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {appt.careprepStatus === "completed" ? (
                        <Link href={`/careprep/responses/${appt.patient.id}`}>
                          <Button variant="outline" size="sm" className="text-green-600 border-green-200 hover:bg-green-50">
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                        </Link>
                      ) : appt.careprepStatus === "pending" ? (
                        <Button variant="outline" size="sm" className="text-yellow-600 border-yellow-200 hover:bg-yellow-50">
                          <Clock className="w-4 h-4 mr-1" />
                          Awaiting
                        </Button>
                      ) : (
                        <Link href={`/careprep/send/${appt.patient.id}?appointment=${appt.id}`}>
                          <Button variant="outline" size="sm" className="text-purple-600 border-purple-200 hover:bg-purple-50">
                            <Send className="w-4 h-4 mr-1" />
                            CarePrep
                          </Button>
                        </Link>
                      )}
                      <Link href={`/provider/visits/${appt.id}`}>
                        <Button variant="outline" size="sm">Document</Button>
                      </Link>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Recent Visits & SOAP Notes */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Stethoscope className="w-5 h-5 text-purple-600" />
                    Recent Visits & SOAP Notes
                  </CardTitle>
                  <CardDescription>Documentation status for recent encounters</CardDescription>
                </div>
                <Link href="/provider/visits/new">
                  <Button variant="primary" size="sm" className="bg-purple-600 hover:bg-purple-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Start New Visit
                  </Button>
                </Link>
              </div>
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
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          {/* Patient Watchlist */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-gray-600" />
                Patient Watchlist
              </CardTitle>
              <CardDescription>CarePrep status for upcoming visits</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {patientList.map(p => (
                  <li key={p.id} className="flex justify-between items-center p-2 rounded hover:bg-gray-50">
                    <div>
                      <p className="font-medium text-gray-900">{p.name}</p>
                      <p className="text-xs text-gray-500">Last seen: {p.lastSeen}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link href={`/careprep/send/${p.id}`}>
                        <Button variant="ghost" size="sm" className="text-purple-600 hover:bg-purple-50 h-7 px-2">
                          <ClipboardList className="w-3.5 h-3.5" />
                        </Button>
                      </Link>
                      <Badge className={statusColorMap[p.appointReadyStatus]}>
                        {p.appointReadyStatus}
                      </Badge>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Pending Tasks */}
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
                      For: <span className="font-medium">{task.patientName}</span> • Due: {task.dueDate}
                    </p>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Quick Templates */}
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
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="p-3 bg-white rounded-lg border border-amber-200 hover:border-amber-300 cursor-pointer">
                  <p className="font-semibold text-sm text-slate-900">General Visit</p>
                  <p className="text-xs text-slate-600">Standard SOAP template</p>
                </div>
                <div className="p-3 bg-white rounded-lg border border-amber-200 hover:border-amber-300 cursor-pointer">
                  <p className="font-semibold text-sm text-slate-900">Annual Physical</p>
                  <p className="text-xs text-slate-600">Comprehensive exam template</p>
                </div>
              </div>
              <Link href="/provider/templates">
                <Button variant="primary" size="sm" className="w-full mt-4 bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Template
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Pre-Visit Prep Modal */}
      {selectedAppointment && (
        <PreVisitPrepModal
          isOpen={!!selectedAppointment}
          onClose={() => setSelectedAppointment(null)}
          appointment={selectedAppointment}
        />
      )}
    </div>
  );
}
