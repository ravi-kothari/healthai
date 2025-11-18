/**
 * Calendar Page
 * Full calendar view with appointment management
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Appointment } from '@/lib/types/calendar';
import { mockAppointments } from '@/lib/mock/appointments';
import { CalendarView } from '@/components/calendar/CalendarView';

export default function CalendarPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching appointments
    const loadAppointments = async () => {
      setIsLoading(true);
      // In a real app, this would be an API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setAppointments(mockAppointments);
      setIsLoading(false);
    };

    loadAppointments();
  }, []);

  const handleAppointmentClick = (appointment: Appointment) => {
    console.log('Appointment clicked:', appointment);
    // TODO: Open appointment details modal or navigate to appointment page
    alert(`Appointment with ${appointment.patientName} clicked`);
  };

  const handleCreateAppointment = (date?: Date, hour?: number) => {
    console.log('Create appointment:', { date, hour });
    // TODO: Open create appointment modal
    alert(`Create appointment for ${date ? date.toLocaleDateString() : 'today'}${hour ? ` at ${hour}:00` : ''}`);
  };

  const handleDayClick = (date: Date) => {
    console.log('Day clicked:', date);
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
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-gray-900">Calendar</h2>
        <p className="text-gray-600 mt-1">Manage your appointments and schedule</p>
      </div>

      <CalendarView
        appointments={appointments}
        initialView="month"
        onAppointmentClick={handleAppointmentClick}
        onCreateAppointment={handleCreateAppointment}
        onDayClick={handleDayClick}
        startHour={7}
        endHour={20}
        weekStartsOn={1}
        showCreateButton={true}
      />
    </div>
  );
}
