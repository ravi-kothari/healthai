'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  Building2,
  Search,
  Plus,
  MoreVertical,
  Users,
  Calendar,
  Mail,
  Phone,
  MapPin,
  ExternalLink,
  Edit,
  Trash2,
  Eye,
  Filter,
  Download,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

// Mock organization data
const organizations = [
  {
    id: '1',
    name: 'Metro Health System',
    email: 'admin@metrohealth.com',
    phone: '+1 (555) 123-4567',
    address: 'New York, NY',
    plan: 'Enterprise',
    status: 'active',
    users: 156,
    mrr: 2499,
    createdAt: '2024-01-15',
    lastActive: '2 hours ago',
  },
  {
    id: '2',
    name: 'Sunrise Medical Group',
    email: 'contact@sunrisemedical.com',
    phone: '+1 (555) 234-5678',
    address: 'Los Angeles, CA',
    plan: 'Professional',
    status: 'active',
    users: 42,
    mrr: 599,
    createdAt: '2024-02-20',
    lastActive: '5 hours ago',
  },
  {
    id: '3',
    name: 'Valley Care Clinic',
    email: 'info@valleycare.com',
    phone: '+1 (555) 345-6789',
    address: 'Phoenix, AZ',
    plan: 'Starter',
    status: 'trial',
    users: 8,
    mrr: 0,
    createdAt: '2024-11-10',
    lastActive: '1 day ago',
  },
  {
    id: '4',
    name: 'Northside Physicians',
    email: 'admin@northsidephysicians.com',
    phone: '+1 (555) 456-7890',
    address: 'Chicago, IL',
    plan: 'Professional',
    status: 'active',
    users: 28,
    mrr: 599,
    createdAt: '2024-03-05',
    lastActive: '3 hours ago',
  },
  {
    id: '5',
    name: 'Community Health Partners',
    email: 'support@communityhealth.org',
    phone: '+1 (555) 567-8901',
    address: 'Houston, TX',
    plan: 'Enterprise',
    status: 'active',
    users: 89,
    mrr: 2499,
    createdAt: '2024-01-28',
    lastActive: '30 min ago',
  },
  {
    id: '6',
    name: 'Pacific Coast Medical',
    email: 'hello@pacificcoastmed.com',
    phone: '+1 (555) 678-9012',
    address: 'San Francisco, CA',
    plan: 'Professional',
    status: 'past_due',
    users: 35,
    mrr: 599,
    createdAt: '2024-04-12',
    lastActive: '1 week ago',
  },
  {
    id: '7',
    name: 'Mountain View Clinic',
    email: 'office@mountainviewclinic.com',
    phone: '+1 (555) 789-0123',
    address: 'Denver, CO',
    plan: 'Starter',
    status: 'active',
    users: 12,
    mrr: 299,
    createdAt: '2024-06-18',
    lastActive: '2 days ago',
  },
  {
    id: '8',
    name: 'Atlantic Health Network',
    email: 'info@atlantichealth.net',
    phone: '+1 (555) 890-1234',
    address: 'Miami, FL',
    plan: 'Enterprise',
    status: 'active',
    users: 210,
    mrr: 2499,
    createdAt: '2023-11-22',
    lastActive: '1 hour ago',
  },
];

export default function OrganizationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);

  const filteredOrgs = organizations.filter((org) => {
    const matchesSearch = org.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      org.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPlan = selectedPlan === 'all' || org.plan.toLowerCase() === selectedPlan;
    const matchesStatus = selectedStatus === 'all' || org.status === selectedStatus;
    return matchesSearch && matchesPlan && matchesStatus;
  });

  const totalMRR = filteredOrgs.reduce((sum, org) => sum + org.mrr, 0);
  const totalUsers = filteredOrgs.reduce((sum, org) => sum + org.users, 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Organizations</h2>
          <p className="text-slate-600 mt-1">Manage all organizations on the platform</p>
        </div>
        <Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
          Add Organization
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Organizations</p>
                <p className="text-2xl font-bold text-slate-900">{filteredOrgs.length}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-xl">
                <Building2 className="w-5 h-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Users</p>
                <p className="text-2xl font-bold text-slate-900">{totalUsers.toLocaleString()}</p>
              </div>
              <div className="p-3 bg-emerald-100 rounded-xl">
                <Users className="w-5 h-5 text-emerald-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Monthly Revenue</p>
                <p className="text-2xl font-bold text-slate-900">${totalMRR.toLocaleString()}</p>
              </div>
              <div className="p-3 bg-violet-100 rounded-xl">
                <Building2 className="w-5 h-5 text-violet-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Active Trials</p>
                <p className="text-2xl font-bold text-slate-900">
                  {organizations.filter(o => o.status === 'trial').length}
                </p>
              </div>
              <div className="p-3 bg-amber-100 rounded-xl">
                <Calendar className="w-5 h-5 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search organizations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>

            {/* Plan Filter */}
            <select
              value={selectedPlan}
              onChange={(e) => setSelectedPlan(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="all">All Plans</option>
              <option value="starter">Starter</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>

            {/* Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="trial">Trial</option>
              <option value="past_due">Past Due</option>
            </select>

            {/* Export Button */}
            <Button variant="outline" size="sm" leftIcon={<Download className="w-4 h-4" />}>
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Organizations Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Plan
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Users
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    MRR
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Last Active
                  </th>
                  <th className="text-right px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredOrgs.map((org) => (
                  <tr key={org.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold">
                          {org.name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-medium text-slate-900">{org.name}</p>
                          <p className="text-sm text-slate-500">{org.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge
                        variant={
                          org.plan === 'Enterprise' ? 'primary' :
                          org.plan === 'Professional' ? 'info' : 'outline'
                        }
                        size="sm"
                      >
                        {org.plan}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <Badge
                        variant={
                          org.status === 'active' ? 'success' :
                          org.status === 'trial' ? 'warning' : 'destructive'
                        }
                        size="sm"
                      >
                        {org.status === 'past_due' ? 'Past Due' : org.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-slate-900 font-medium">{org.users}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-slate-900 font-medium">
                        ${org.mrr.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-slate-500 text-sm">{org.lastActive}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200">
            <p className="text-sm text-slate-600">
              Showing <span className="font-medium">1-{filteredOrgs.length}</span> of{' '}
              <span className="font-medium">{organizations.length}</span> organizations
            </p>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm" className="bg-emerald-50 border-emerald-200 text-emerald-700">
                1
              </Button>
              <Button variant="outline" size="sm">
                2
              </Button>
              <Button variant="outline" size="sm">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
