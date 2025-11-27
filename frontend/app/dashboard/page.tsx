'use client';

import { DollarSign, Users, Calendar, AlertCircle } from 'lucide-react';
import { StatCardData } from '@/lib/types';
import StatCard from '@/components/dashboard/StatCard';
import RevenueChart from '@/components/dashboard/RevenueChart';
import RecentActivity from '@/components/dashboard/RecentActivity';
import UpcomingAppointments from '@/components/dashboard/UpcomingAppointments';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { mockAppointments } from '@/lib/mock/appointments';

const stats: StatCardData[] = [
  {
    title: 'Total Revenue',
    value: '$45,231.89',
    icon: DollarSign,
    change: '+20.1% from last month',
    changeType: 'increase',
  },
  {
    title: 'Active Clients',
    value: '235',
    icon: Users,
    change: '+18.1% from last month',
    changeType: 'increase',
  },
  {
    title: 'Upcoming Appointments',
    value: '12',
    icon: Calendar,
    change: '+19% from last month',
    changeType: 'increase',
  },
  {
    title: 'Overdue Invoices',
    value: '4',
    icon: AlertCircle,
    change: '-2 since yesterday',
    changeType: 'decrease',
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Revenue Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Revenue Overview</CardTitle>
            <CardDescription>Monthly revenue vs expenses for 2023</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <RevenueChart />
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest actions across your practice</CardDescription>
          </CardHeader>
          <CardContent>
            <RecentActivity />
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Appointments */}
      <UpcomingAppointments appointments={mockAppointments} limit={5} showViewAll={true} />
    </div>
  );
}
