import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { getCurrentUser } from "@/lib/auth/middleware";
import type { Appointment, PreVisitTask, SecureMessage } from "@/lib/types/dashboard";
import { Calendar, CheckSquare, Mail, Plus, FileText, ArrowRight, ClipboardCheck, Sparkles } from "lucide-react";
import Link from "next/link";

// Mock Data Fetching
async function getPatientDashboardData(patientId: string) {
  // In a real app, this would fetch data from your API
  const upcomingAppointment: Appointment = {
    id: "appt-123",
    providerName: "Dr. Smith",
    specialty: "Cardiology",
    date: new Date(new Date().setDate(new Date().getDate() + 3)),
    type: "Virtual",
  };

  const preVisitTasks: PreVisitTask[] = [
    { id: "task-1", text: "Update medical history", completed: true, link: "/patient/previsit/history", order: 1 },
    { id: "task-2", text: "Complete symptom checker", completed: false, link: "/patient/previsit/symptoms", order: 2 },
    { id: "task-3", text: "Verify insurance information", completed: false, link: "/patient/previsit/insurance", order: 3 },
  ];

  const recentMessages: SecureMessage[] = [
    { id: "msg-1", from: "Dr. Smith's Office", subject: "Your recent lab results", snippet: "Your results for the lipid panel are now available...", timestamp: "2 days ago", read: false },
    { id: "msg-2", from: "Billing Department", subject: "Your recent statement", snippet: "A new statement is available for your review...", timestamp: "5 days ago", read: true },
  ];

  return { upcomingAppointment, preVisitTasks, recentMessages };
}

export default async function PatientDashboardPage() {
  const user = await getCurrentUser();
  if (!user) return null;

  const { upcomingAppointment, preVisitTasks, recentMessages } = await getPatientDashboardData(user.id);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user.name.split(' ')[0]}!</h1>
          <p className="text-gray-600 mt-1">Here's a summary of your health portal.</p>
        </div>
        <div className="flex gap-2 shrink-0">
          <Link href="/dashboard">
            <Button variant="outline" className="text-xs">📊 SaaS Dashboard</Button>
          </Link>
          <Button variant="outline"><FileText className="w-4 h-4 mr-2" /> View Records</Button>
          <Button><Plus className="w-4 h-4 mr-2" /> Schedule</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600" />
                Upcoming Appointment
              </CardTitle>
              <CardDescription>Your next scheduled visit.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center p-4 border rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50">
                <div>
                  <p className="font-bold text-lg text-gray-900">{upcomingAppointment.providerName}</p>
                  <p className="text-sm text-gray-600">{upcomingAppointment.specialty}</p>
                  <p className="text-sm text-gray-600 mt-2">
                    {upcomingAppointment.date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                    {' at '}
                    {upcomingAppointment.date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                <Badge className={upcomingAppointment.type === 'Virtual' ? 'bg-cyan-100 text-cyan-700' : 'bg-green-100 text-green-700'}>
                  {upcomingAppointment.type}
                </Badge>
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">View Appointment Details</Button>
            </CardFooter>
          </Card>

          {/* Appointment Prep Summary - New Unified Experience */}
          <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ClipboardCheck className="w-5 h-5 text-blue-600" />
                Appointment Preparation
                <Sparkles className="w-4 h-4 text-blue-500 ml-1" />
              </CardTitle>
              <CardDescription>
                Get ready for your visit with personalized preparation guidance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-sm text-gray-700">
                  Your AI-powered appointment prep summary includes:
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2">
                    <CheckSquare className="w-4 h-4 text-green-600" />
                    <span>Personalized discussion topics based on your health</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckSquare className="w-4 h-4 text-green-600" />
                    <span>Medication and allergy review</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckSquare className="w-4 h-4 text-green-600" />
                    <span>Interactive appointment checklist</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckSquare className="w-4 h-4 text-green-600" />
                    <span>Recent symptom analysis summary</span>
                  </li>
                </ul>
                <div className="mt-4 p-3 bg-white rounded-lg border border-blue-200">
                  <p className="text-xs text-gray-600 mb-2">
                    <strong className="text-blue-700">New:</strong> We've combined your symptom analysis and appointment preparation into one easy-to-use summary!
                  </p>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Link href="/patient/appointment-prep" className="w-full">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  <ClipboardCheck className="w-4 h-4 mr-2" />
                  View Appointment Prep Summary
                </Button>
              </Link>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckSquare className="w-5 h-5 text-green-600" />
                Pre-Visit Checklist
              </CardTitle>
              <CardDescription>Tasks to complete before your visit with {upcomingAppointment.providerName}.</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {preVisitTasks.map((task, index) => {
                  // Check if previous task is completed (for sequential workflow)
                  const previousTask = index > 0 ? preVisitTasks[index - 1] : null;
                  const isLocked = previousTask && !previousTask.completed;
                  const canInteract = task.completed || !isLocked;

                  return (
                    <li key={task.id} className={`flex items-center justify-between p-3 border rounded-lg transition-colors ${canInteract ? 'hover:bg-gray-50' : 'bg-gray-50'}`}>
                      <div className="flex items-center flex-1">
                        <span className="text-gray-400 font-semibold text-sm mr-3 w-5">{task.order}.</span>
                        <input
                          type="checkbox"
                          checked={task.completed}
                          readOnly
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className={`ml-3 ${task.completed ? 'text-gray-700' : 'text-gray-900 font-medium'}`}>
                          {task.text}
                        </span>
                      </div>
                      <div className="relative group">
                        {task.completed ? (
                          <Link href={task.link}>
                            <Button variant="outline" size="sm">
                              View / Edit
                            </Button>
                          </Link>
                        ) : isLocked ? (
                          <>
                            <Button variant="secondary" size="sm" disabled className="cursor-not-allowed opacity-50">
                              Start <ArrowRight className="w-4 h-4 ml-1" />
                            </Button>
                            <div className="absolute right-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
                              Please complete "{previousTask.text}" to unlock this step.
                              <div className="absolute top-full right-4 -mt-1 border-4 border-transparent border-t-gray-900"></div>
                            </div>
                          </>
                        ) : (
                          <Link href={task.link}>
                            <Button variant="secondary" size="sm">
                              Start <ArrowRight className="w-4 h-4 ml-1" />
                            </Button>
                          </Link>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="w-5 h-5 text-gray-600" />
                Recent Messages
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-4">
                {recentMessages.map(msg => (
                  <li key={msg.id} className="border-b pb-3 last:border-b-0">
                    <div className="flex justify-between items-start mb-1">
                      <p className="font-semibold text-sm text-gray-900">{msg.from}</p>
                      {!msg.read && <Badge className="bg-red-100 text-red-700">New</Badge>}
                    </div>
                    <p className="text-sm text-gray-800 font-medium">{msg.subject}</p>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{msg.snippet}</p>
                    <p className="text-xs text-gray-400 mt-1">{msg.timestamp}</p>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">View All Messages</Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
}
