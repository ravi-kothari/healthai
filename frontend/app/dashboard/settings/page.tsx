import { SettingsCategory } from '@/lib/types';
import { Card } from '@/components/ui/card';
import Link from 'next/link';
import {
  Building2,
  User,
  Users,
  FileText,
  File,
  Folder,
  DollarSign,
  Shield,
  Calendar,
  MessageSquare,
  Bell,
  Send,
  Megaphone,
  Globe,
  CreditCard,
  Database,
  Download
} from 'lucide-react';

const getIcon = (title: string) => {
  const iconMap: Record<string, any> = {
    'My Profile': User,
    'My Practice': Building2,
    'Team Members': Users,
    'Documents': FileText,
    'Notes & Forms': File,
    'Business Files': Folder,
    'Billing & Services': DollarSign,
    'Insurance': Shield,
    'Calendar': Calendar,
    'Widget': Calendar,
    'Client Portal': MessageSquare,
    'Client Reminders': Bell,
    'Secure Messaging': Send,
    'Client Referrals': Megaphone,
    'Professional Website': Globe,
    'Domains': Globe,
    'Subscription Information': CreditCard,
    'Notifications': Bell,
    'Demo Data': Database,
    'Data Export': Download,
  };
  return iconMap[title] || File;
};

const settingsData: SettingsCategory[] = [
  {
    title: 'Practice Management',
    items: [
      { title: 'My Profile', description: 'Update your personal information and credentials.', href: '/dashboard/settings/profile' },
      { title: 'My Practice', description: 'Manage practice details, branding, and location.', href: '/dashboard/settings/practice' },
      { title: 'Team Members', description: 'Invite and manage your team members.', href: '/dashboard/settings/team' },
    ],
  },
  {
    title: 'Documents & Files',
    items: [
      { title: 'Documents', description: 'Manage client documents and templates.', href: '/dashboard/settings/documents' },
      { title: 'Notes & Forms', description: 'Create and manage clinical note templates.', href: '/dashboard/settings/forms' },
      { title: 'Business Files', description: 'Store your business-related documents.', href: '/dashboard/settings/files' },
    ],
  },
  {
    title: 'Billing',
    items: [
      { title: 'Billing & Services', description: 'Set up services, rates, and payment methods.', href: '/dashboard/settings/billing' },
      { title: 'Insurance', description: 'Manage insurance providers and billing settings.', href: '/dashboard/settings/insurance' },
    ],
  },
  {
    title: 'Scheduling',
    items: [
      { title: 'Calendar', description: 'Configure your calendar and availability.', href: '/dashboard/settings/calendar' },
      { title: 'Widget', description: 'Customize your online booking widget.', href: '/dashboard/settings/widget' },
    ],
  },
  {
    title: 'Client Communication',
    items: [
      { title: 'Client Portal', description: 'Customize the client portal experience.', href: '/dashboard/settings/portal' },
      { title: 'Client Reminders', description: 'Set up automated appointment reminders.', href: '/dashboard/settings/reminders' },
      { title: 'Secure Messaging', description: 'Enable HIPAA-compliant client messaging.', href: '/dashboard/settings/messaging' },
    ],
  },
  {
    title: 'Marketing',
    items: [
      { title: 'Client Referrals', description: 'Track and manage client referrals.', href: '/dashboard/settings/referrals' },
      { title: 'Professional Website', description: 'Build your professional website.', href: '/dashboard/settings/website' },
      { title: 'Domains', description: 'Manage your custom domains.', href: '/dashboard/settings/domains' },
    ],
  },
  {
    title: 'Account',
    items: [
      { title: 'Subscription Information', description: 'Manage your plan and billing details.', href: '/dashboard/subscription' },
      { title: 'Notifications', description: 'Configure your notification preferences.', href: '/dashboard/settings/notifications' },
      { title: 'Data Export', description: 'Export your practice data and records.', href: '/dashboard/settings/export' },
    ],
  },
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-gray-900">Settings</h2>
        <p className="text-gray-600 mt-1">Manage your practice settings and preferences</p>
      </div>

      <div className="space-y-8">
        {settingsData.map((category) => (
          <div key={category.title}>
            <h3 className="mb-4 text-xl font-semibold text-gray-900">{category.title}</h3>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {category.items.map((item) => {
                const Icon = getIcon(item.title);
                return (
                  <Link href={item.href} key={item.title} className="block group">
                    <Card className="p-5 h-full hover:shadow-md transition-shadow hover:border-blue-200">
                      <div className="flex items-start gap-3">
                        <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
                          <Icon className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <h4 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">{item.title}</h4>
                          <p className="text-sm text-gray-500 mt-1">{item.description}</p>
                        </div>
                      </div>
                    </Card>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
