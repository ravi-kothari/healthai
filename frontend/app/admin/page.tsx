'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Building2,
  Users,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Zap,
  Server,
  Database,
  Cpu,
  HardDrive,
  Globe,
  Calendar,
} from 'lucide-react';

// Mock data for the admin dashboard
const platformStats = [
  {
    title: 'Total Organizations',
    value: '127',
    change: '+12',
    changeLabel: 'this month',
    changeType: 'increase' as const,
    icon: Building2,
    color: 'blue',
  },
  {
    title: 'Active Users',
    value: '2,847',
    change: '+234',
    changeLabel: 'this month',
    changeType: 'increase' as const,
    icon: Users,
    color: 'emerald',
  },
  {
    title: 'Monthly Revenue',
    value: '$89,420',
    change: '+18.2%',
    changeLabel: 'vs last month',
    changeType: 'increase' as const,
    icon: DollarSign,
    color: 'violet',
  },
  {
    title: 'API Requests',
    value: '1.2M',
    change: '+45%',
    changeLabel: 'this week',
    changeType: 'increase' as const,
    icon: Activity,
    color: 'amber',
  },
];

const recentOrganizations = [
  { id: 1, name: 'Metro Health System', plan: 'Enterprise', users: 156, status: 'active', createdAt: '2 hours ago' },
  { id: 2, name: 'Sunrise Medical Group', plan: 'Professional', users: 42, status: 'active', createdAt: '5 hours ago' },
  { id: 3, name: 'Valley Care Clinic', plan: 'Starter', users: 8, status: 'trial', createdAt: '1 day ago' },
  { id: 4, name: 'Northside Physicians', plan: 'Professional', users: 28, status: 'active', createdAt: '2 days ago' },
  { id: 5, name: 'Community Health Partners', plan: 'Enterprise', users: 89, status: 'active', createdAt: '3 days ago' },
];

const systemAlerts = [
  { id: 1, type: 'warning', message: 'High API latency detected in US-East region', time: '5 min ago' },
  { id: 2, type: 'info', message: 'Scheduled maintenance window: Dec 15, 2AM-4AM UTC', time: '1 hour ago' },
  { id: 3, type: 'success', message: 'Database backup completed successfully', time: '3 hours ago' },
];

const systemHealth = [
  { name: 'API Server', status: 'operational', uptime: '99.99%', icon: Server },
  { name: 'Database', status: 'operational', uptime: '99.98%', icon: Database },
  { name: 'AI Services', status: 'operational', uptime: '99.95%', icon: Cpu },
  { name: 'Storage', status: 'operational', uptime: '100%', icon: HardDrive },
];

const revenueByPlan = [
  { plan: 'Enterprise', revenue: 52450, percentage: 58.7 },
  { plan: 'Professional', revenue: 28920, percentage: 32.3 },
  { plan: 'Starter', revenue: 8050, percentage: 9.0 },
];

export default function AdminOverviewPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Platform Overview</h2>
          <p className="text-slate-600 mt-1">Monitor your SaaS platform performance and health</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" leftIcon={<Calendar className="w-4 h-4" />}>
            Last 30 Days
          </Button>
          <Button variant="primary" size="sm" leftIcon={<Globe className="w-4 h-4" />}>
            View Public Status
          </Button>
        </div>
      </div>

      {/* Platform Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {platformStats.map((stat) => (
          <Card key={stat.title} className="relative overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-slate-900 mt-2">{stat.value}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {stat.changeType === 'increase' ? (
                      <TrendingUp className="w-4 h-4 text-emerald-500" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${
                      stat.changeType === 'increase' ? 'text-emerald-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </span>
                    <span className="text-sm text-slate-500">{stat.changeLabel}</span>
                  </div>
                </div>
                <div className={`p-3 rounded-xl bg-${stat.color}-100`}>
                  <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Organizations */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Organizations</CardTitle>
              <CardDescription>Latest organizations that joined the platform</CardDescription>
            </div>
            <Link href="/admin/organizations">
              <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-4 h-4" />}>
                View All
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentOrganizations.map((org) => (
                <div
                  key={org.id}
                  className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold">
                      {org.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">{org.name}</p>
                      <p className="text-sm text-slate-500">{org.users} users</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge
                      variant={
                        org.plan === 'Enterprise' ? 'primary' :
                        org.plan === 'Professional' ? 'info' : 'outline'
                      }
                      size="sm"
                    >
                      {org.plan}
                    </Badge>
                    <Badge
                      variant={org.status === 'active' ? 'success' : 'warning'}
                      size="sm"
                    >
                      {org.status}
                    </Badge>
                    <span className="text-xs text-slate-500">{org.createdAt}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-500" />
              System Health
            </CardTitle>
            <CardDescription>All systems operational</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {systemHealth.map((system) => (
                <div key={system.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-100 rounded-lg">
                      <system.icon className="w-4 h-4 text-slate-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{system.name}</p>
                      <p className="text-xs text-slate-500">Uptime: {system.uptime}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs text-emerald-600 font-medium">Operational</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200">
              <Link href="/admin/settings">
                <Button variant="outline" size="sm" className="w-full">
                  View System Logs
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue by Plan */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue by Plan</CardTitle>
            <CardDescription>Monthly recurring revenue breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {revenueByPlan.map((item) => (
                <div key={item.plan} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-slate-700">{item.plan}</span>
                    <span className="text-slate-900 font-semibold">
                      ${item.revenue.toLocaleString()}
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        item.plan === 'Enterprise' ? 'bg-violet-500' :
                        item.plan === 'Professional' ? 'bg-blue-500' : 'bg-slate-400'
                      }`}
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500">{item.percentage}% of total</p>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-700">Total MRR</span>
                <span className="text-lg font-bold text-slate-900">$89,420</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Alerts */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>System Alerts</CardTitle>
              <CardDescription>Recent platform notifications and alerts</CardDescription>
            </div>
            <Badge variant="outline" size="sm">
              {systemAlerts.length} alerts
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {systemAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`flex items-start gap-3 p-4 rounded-lg ${
                    alert.type === 'warning' ? 'bg-amber-50 border border-amber-200' :
                    alert.type === 'success' ? 'bg-emerald-50 border border-emerald-200' :
                    'bg-blue-50 border border-blue-200'
                  }`}
                >
                  {alert.type === 'warning' ? (
                    <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                  ) : alert.type === 'success' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                  ) : (
                    <Activity className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${
                      alert.type === 'warning' ? 'text-amber-800' :
                      alert.type === 'success' ? 'text-emerald-800' :
                      'text-blue-800'
                    }`}>
                      {alert.message}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">{alert.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common administrative tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link href="/admin/organizations">
              <Button variant="outline" className="w-full h-auto py-4 flex-col gap-2">
                <Building2 className="w-6 h-6 text-blue-600" />
                <span>Add Organization</span>
              </Button>
            </Link>
            <Link href="/admin/users">
              <Button variant="outline" className="w-full h-auto py-4 flex-col gap-2">
                <Users className="w-6 h-6 text-emerald-600" />
                <span>Manage Users</span>
              </Button>
            </Link>
            <Link href="/admin/billing">
              <Button variant="outline" className="w-full h-auto py-4 flex-col gap-2">
                <DollarSign className="w-6 h-6 text-violet-600" />
                <span>View Billing</span>
              </Button>
            </Link>
            <Link href="/admin/settings">
              <Button variant="outline" className="w-full h-auto py-4 flex-col gap-2">
                <Activity className="w-6 h-6 text-amber-600" />
                <span>System Logs</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
