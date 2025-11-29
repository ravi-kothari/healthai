/**
 * Provider Calendar Page
 * Enhanced calendar with appointment management and CarePrep integration
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Appointment } from '@/lib/types/calendar';
import { mockAppointments } from '@/lib/mock/appointments';
import { CalendarView } from '@/components/calendar/CalendarView';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Plus, Upload, Download, RefreshCw, Send } from 'lucide-react';
import Link from 'next/link';

export default function ProviderCalendarPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showImportModal, setShowImportModal] = useState(false);

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    setIsLoading(true);
    // In a real app, this would fetch from backend API
    await new Promise(resolve => setTimeout(resolve, 500));
    setAppointments(mockAppointments);
    setIsLoading(false);
  };

  const handleAppointmentClick = (appointment: Appointment) => {
    console.log('Appointment clicked:', appointment);
    // TODO: Open appointment details modal with CarePrep options
  };

  const handleCreateAppointment = (date?: Date, hour?: number) => {
    console.log('Create appointment:', { date, hour });
    setShowImportModal(false);
    // TODO: Open create appointment modal
  };

  const handleImportFromCSV = () => {
    setShowImportModal(true);
    // TODO: Implement CSV import functionality
  };

  const handleSyncCalendar = () => {
    // TODO: Implement Google Calendar / Outlook sync
    alert('Calendar sync coming soon! For now, you can:\n1. Manually add appointments\n2. Import from CSV\n3. Import from your EHR export');
  };

  const getUpcomingAppointments = () => {
    const now = new Date();
    return appointments
      .filter(apt => apt.start > now)
      .sort((a, b) => a.start.getTime() - b.start.getTime())
      .slice(0, 5);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading calendar...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">Calendar</h2>
          <p className="text-gray-600 mt-1">Manage appointments and send CarePrep questionnaires</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSyncCalendar}
            className="text-blue-600 border-blue-200 hover:bg-blue-50"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync Calendar
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleImportFromCSV}
            className="text-green-600 border-green-200 hover:bg-green-50"
          >
            <Upload className="w-4 h-4 mr-2" />
            Import CSV
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleCreateAppointment()}
            className="bg-purple-600 hover:bg-purple-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Appointment
          </Button>
        </div>
      </div>

      {/* Info Banner - No EHR Integration Yet */}
      <Card className="bg-blue-50 border-blue-200 p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-blue-900 mb-1">Appointment Management Options</h3>
            <p className="text-sm text-blue-700">
              While we're building EHR integration, you can manage appointments by:
            </p>
            <ul className="mt-2 space-y-1 text-sm text-blue-700">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                <strong>Manual Entry:</strong> Click "+ New Appointment" to add patients
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                <strong>CSV Import:</strong> Upload appointment list from your practice management system
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                <strong>Calendar Sync:</strong> Connect Google Calendar or Outlook (coming soon)
              </li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Quick Actions for Upcoming Appointments */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900">Upcoming Appointments</h3>
          <Link href="/careprep">
            <Button variant="outline" size="sm" className="text-purple-600 border-purple-200 hover:bg-purple-50">
              Manage CarePrep
            </Button>
          </Link>
        </div>
        <div className="space-y-2">
          {getUpcomingAppointments().map((apt) => (
            <div key={apt.id} className="flex items-center justify-between p-2 border rounded hover:bg-gray-50">
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-900">{apt.patientName}</p>
                <p className="text-xs text-gray-500">
                  {apt.start.toLocaleDateString()} at {apt.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
              <Link href={`/careprep/send/${apt.patientId}?appointment=${apt.id}`}>
                <Button variant="outline" size="sm" className="text-purple-600 border-purple-200 hover:bg-purple-50">
                  <Send className="w-3 h-3 mr-1" />
                  Send CarePrep
                </Button>
              </Link>
            </div>
          ))}
          {getUpcomingAppointments().length === 0 && (
            <p className="text-sm text-gray-500 text-center py-4">No upcoming appointments</p>
          )}
        </div>
      </Card>

      {/* Calendar Component */}
      <CalendarView
        appointments={appointments}
        initialView="month"
        onAppointmentClick={handleAppointmentClick}
        onCreateAppointment={handleCreateAppointment}
        startHour={7}
        endHour={20}
        weekStartsOn={1}
        showCreateButton={true}
      />

      {/* CSV Import Modal Placeholder */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="max-w-lg w-full p-6">
            <h3 className="text-xl font-bold mb-4">Import Appointments from CSV</h3>
            <p className="text-sm text-gray-600 mb-4">
              Upload a CSV file with columns: Patient Name, Date, Time, Duration, Type, Notes
            </p>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-4">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Drag and drop CSV file here, or click to browse</p>
              <input type="file" accept=".csv" className="hidden" />
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowImportModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" className="bg-green-600 hover:bg-green-700">
                Upload & Import
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
