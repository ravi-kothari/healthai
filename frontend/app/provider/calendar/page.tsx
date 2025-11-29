'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Plus } from 'lucide-react';

export default function ProviderCalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: (number | null)[] = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Add all days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i);
    }

    return days;
  };

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const isToday = (day: number | null) => {
    if (!day) return false;
    const today = new Date();
    return (
      day === today.getDate() &&
      currentDate.getMonth() === today.getMonth() &&
      currentDate.getFullYear() === today.getFullYear()
    );
  };

  const days = getDaysInMonth(currentDate);

  // Mock appointments for demo
  const mockAppointments: Record<number, Array<{ time: string; patient: string; type: string }>> = {
    29: [
      { time: '10:00 AM', patient: 'John Smith', type: 'Follow-up' },
      { time: '7:00 PM', patient: 'Jamie D. Appleseed', type: 'Annual Physical' },
    ],
    15: [
      { time: '9:00 AM', patient: 'Sarah Johnson', type: 'Consultation' },
      { time: '2:00 PM', patient: 'Mike Williams', type: 'Check-up' },
    ],
    22: [
      { time: '11:00 AM', patient: 'Emily Davis', type: 'Follow-up' },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calendar</h1>
          <p className="text-gray-600 mt-1">Manage your appointments and schedule</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          New Appointment
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm" onClick={goToPreviousMonth}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="text-2xl font-semibold">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </h2>
              <Button variant="outline" size="sm" onClick={goToNextMonth}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <Button variant="outline" onClick={goToToday}>
              <CalendarIcon className="h-4 w-4 mr-2" />
              Today
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-2">
            {/* Day headers */}
            {daysOfWeek.map((day) => (
              <div
                key={day}
                className="text-center font-semibold text-gray-700 text-sm py-2"
              >
                {day}
              </div>
            ))}

            {/* Calendar days */}
            {days.map((day, index) => {
              const hasAppointments = day && mockAppointments[day];
              const appointments = day ? mockAppointments[day] || [] : [];

              return (
                <div
                  key={index}
                  className={`
                    min-h-[120px] p-2 border rounded-lg
                    ${day ? 'bg-white hover:bg-gray-50 cursor-pointer' : 'bg-gray-50'}
                    ${isToday(day) ? 'ring-2 ring-blue-500 bg-blue-50' : ''}
                    transition-colors
                  `}
                >
                  {day && (
                    <>
                      <div
                        className={`
                          text-sm font-medium mb-2
                          ${isToday(day) ? 'text-blue-600' : 'text-gray-700'}
                        `}
                      >
                        {day}
                      </div>
                      <div className="space-y-1">
                        {appointments.map((apt, idx) => (
                          <div
                            key={idx}
                            className={`
                              text-xs p-1.5 rounded
                              ${idx === 0 ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}
                            `}
                          >
                            <div className="font-medium">{apt.time}</div>
                            <div className="truncate">{apt.patient}</div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Appointments */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Appointments</CardTitle>
          <CardDescription>Your scheduled appointments for this month</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(mockAppointments)
              .flatMap(([day, appointments]) =>
                appointments.map((apt) => ({
                  day: parseInt(day),
                  ...apt,
                }))
              )
              .sort((a, b) => a.day - b.day)
              .map((apt, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-xs text-blue-600 font-medium">
                          {monthNames[currentDate.getMonth()].slice(0, 3)}
                        </div>
                        <div className="text-lg font-bold text-blue-700">{apt.day}</div>
                      </div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{apt.patient}</div>
                      <div className="text-sm text-gray-600">
                        {apt.time} • {apt.type}
                      </div>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
