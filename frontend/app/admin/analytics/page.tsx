'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Building2,
  Activity,
  Calendar,
  DollarSign,
  Clock,
  FileText,
  Zap,
  Globe,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';

// Mock analytics data
const platformMetrics = {
  totalOrganizations: 127,
  activeUsers: 2847,
  monthlyRevenue: 89420,
  apiRequests: 1.2,
  avgSessionDuration: 24,
  patientEncounters: 15420,
};

const growthMetrics = [
  { label: 'Organizations', value: 127, change: 12, changePercent: 10.4, period: 'this month' },
  { label: 'Active Users', value: 2847, change: 234, changePercent: 8.9, period: 'this month' },
  { label: 'Revenue', value: '$89,420', change: 15200, changePercent: 20.5, period: 'vs last month' },
  { label: 'API Calls', value: '1.2M', change: 450000, changePercent: 60.0, period: 'this week' },
];

const topOrganizations = [
  { name: 'Metro Health System', users: 156, revenue: 2499, visits: 3420, growth: 15 },
  { name: 'Atlantic Health Network', users: 210, revenue: 2499, visits: 2890, growth: 12 },
  { name: 'Community Health Partners', users: 89, revenue: 2499, visits: 2150, growth: 8 },
  { name: 'Sunrise Medical Group', users: 42, revenue: 599, visits: 1840, growth: 22 },
  { name: 'Northside Physicians', users: 28, revenue: 599, visits: 980, growth: -3 },
];

const featureUsage = [
  { feature: 'AI Assistant', usage: 78, trend: 'up' },
  { feature: 'Transcription', usage: 92, trend: 'up' },
  { feature: 'CarePrep', usage: 65, trend: 'up' },
  { feature: 'SOAP Templates', usage: 88, trend: 'stable' },
  { feature: 'FHIR Integration', usage: 34, trend: 'up' },
  { feature: 'Quick Notes', usage: 71, trend: 'up' },
];

const revenueByPlan = [
  { plan: 'Enterprise', revenue: 52450, orgs: 21, percentage: 58.7 },
  { plan: 'Professional', revenue: 28920, orgs: 48, percentage: 32.3 },
  { plan: 'Starter', revenue: 8050, orgs: 27, percentage: 9.0 },
  { plan: 'Trial', revenue: 0, orgs: 31, percentage: 0 },
];

const monthlyData = [
  { month: 'Jun', revenue: 62000, users: 1850 },
  { month: 'Jul', revenue: 68000, users: 2100 },
  { month: 'Aug', revenue: 72000, users: 2350 },
  { month: 'Sep', revenue: 78000, users: 2520 },
  { month: 'Oct', revenue: 84000, users: 2680 },
  { month: 'Nov', revenue: 89420, users: 2847 },
];

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d');

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Platform Analytics</h2>
          <p className="text-slate-600 mt-1">Monitor platform performance and usage metrics</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button variant="outline" size="sm" leftIcon={<Calendar className="w-4 h-4" />}>
            Custom Range
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {growthMetrics.map((metric) => (
          <Card key={metric.label}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">{metric.label}</p>
                  <p className="text-3xl font-bold text-slate-900 mt-2">{metric.value}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {metric.changePercent > 0 ? (
                      <>
                        <ArrowUpRight className="w-4 h-4 text-emerald-500" />
                        <span className="text-sm font-medium text-emerald-600">
                          +{metric.changePercent}%
                        </span>
                      </>
                    ) : (
                      <>
                        <ArrowDownRight className="w-4 h-4 text-red-500" />
                        <span className="text-sm font-medium text-red-600">
                          {metric.changePercent}%
                        </span>
                      </>
                    )}
                    <span className="text-sm text-slate-500">{metric.period}</span>
                  </div>
                </div>
                <div className="p-3 bg-emerald-100 rounded-xl">
                  {metric.label === 'Organizations' && <Building2 className="w-6 h-6 text-emerald-600" />}
                  {metric.label === 'Active Users' && <Users className="w-6 h-6 text-emerald-600" />}
                  {metric.label === 'Revenue' && <DollarSign className="w-6 h-6 text-emerald-600" />}
                  {metric.label === 'API Calls' && <Activity className="w-6 h-6 text-emerald-600" />}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trend</CardTitle>
            <CardDescription>Monthly recurring revenue over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between gap-2">
              {monthlyData.map((data, index) => (
                <div key={data.month} className="flex flex-col items-center flex-1">
                  <div
                    className="w-full bg-emerald-500 rounded-t-lg transition-all hover:bg-emerald-600"
                    style={{ height: `${(data.revenue / 100000) * 200}px` }}
                  />
                  <span className="text-xs text-slate-500 mt-2">{data.month}</span>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-200">
              <div>
                <p className="text-sm text-slate-600">Total MRR</p>
                <p className="text-2xl font-bold text-slate-900">$89,420</p>
              </div>
              <Badge variant="success" size="sm">
                <TrendingUp className="w-3 h-3 mr-1" />
                +20.5% growth
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* User Growth Chart */}
        <Card>
          <CardHeader>
            <CardTitle>User Growth</CardTitle>
            <CardDescription>Active users over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between gap-2">
              {monthlyData.map((data, index) => (
                <div key={data.month} className="flex flex-col items-center flex-1">
                  <div
                    className="w-full bg-blue-500 rounded-t-lg transition-all hover:bg-blue-600"
                    style={{ height: `${(data.users / 3000) * 200}px` }}
                  />
                  <span className="text-xs text-slate-500 mt-2">{data.month}</span>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-200">
              <div>
                <p className="text-sm text-slate-600">Total Users</p>
                <p className="text-2xl font-bold text-slate-900">2,847</p>
              </div>
              <Badge variant="info" size="sm">
                <TrendingUp className="w-3 h-3 mr-1" />
                +8.9% growth
              </Badge>
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
            <CardDescription>MRR breakdown by subscription tier</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {revenueByPlan.map((item) => (
                <div key={item.plan} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-700">{item.plan}</span>
                      <Badge variant="outline" size="sm">{item.orgs} orgs</Badge>
                    </div>
                    <span className="text-slate-900 font-semibold">
                      ${item.revenue.toLocaleString()}
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        item.plan === 'Enterprise' ? 'bg-violet-500' :
                        item.plan === 'Professional' ? 'bg-blue-500' :
                        item.plan === 'Starter' ? 'bg-emerald-500' : 'bg-slate-400'
                      }`}
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Feature Usage */}
        <Card>
          <CardHeader>
            <CardTitle>Feature Usage</CardTitle>
            <CardDescription>Adoption rate by feature</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {featureUsage.map((item) => (
                <div key={item.feature} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Zap className="w-4 h-4 text-amber-500" />
                    <span className="text-sm text-slate-700">{item.feature}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-amber-500"
                        style={{ width: `${item.usage}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-700 w-10">{item.usage}%</span>
                    {item.trend === 'up' && <TrendingUp className="w-3 h-3 text-emerald-500" />}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Organizations */}
        <Card>
          <CardHeader>
            <CardTitle>Top Organizations</CardTitle>
            <CardDescription>By patient encounters</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topOrganizations.map((org, index) => (
                <div key={org.name} className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-xs font-medium text-slate-600">
                      {index + 1}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{org.name}</p>
                      <p className="text-xs text-slate-500">{org.users} users</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-slate-900">{org.visits.toLocaleString()}</p>
                    <p className={`text-xs ${org.growth >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {org.growth >= 0 ? '+' : ''}{org.growth}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Platform Health */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Health Metrics</CardTitle>
          <CardDescription>System performance and reliability</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-slate-50 rounded-lg">
              <Globe className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-900">99.98%</p>
              <p className="text-sm text-slate-600">Uptime</p>
            </div>
            <div className="text-center p-4 bg-slate-50 rounded-lg">
              <Clock className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-900">142ms</p>
              <p className="text-sm text-slate-600">Avg Response Time</p>
            </div>
            <div className="text-center p-4 bg-slate-50 rounded-lg">
              <Activity className="w-8 h-8 text-violet-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-900">1.2M</p>
              <p className="text-sm text-slate-600">API Requests/Week</p>
            </div>
            <div className="text-center p-4 bg-slate-50 rounded-lg">
              <FileText className="w-8 h-8 text-amber-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-slate-900">0.02%</p>
              <p className="text-sm text-slate-600">Error Rate</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
