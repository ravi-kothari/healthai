'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/stores/authStore';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';
import { branding } from '@/lib/config/branding';

export default function ProviderLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [isReady, setIsReady] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  useEffect(() => {
    // Wait for hydration to complete
    if (!isAuthenticated) {
      router.replace('/login');
    } else if (user?.role !== 'provider' && user?.role !== 'admin' && user?.role !== 'doctor') {
      router.replace('/login');
    } else {
      setIsReady(true);
    }
  }, [isAuthenticated, user, router]);

  // Show nothing until we've confirmed auth status to prevent flicker
  if (!isReady) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/provider/dashboard" className="font-bold text-xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {branding.name}
              </Link>
              <nav className="hidden md:flex gap-4">
                <Link href="/provider/dashboard" className="text-gray-600 hover:text-blue-600">
                  Dashboard
                </Link>
                <Link href="/provider/calendar" className="text-gray-600 hover:text-blue-600">
                  Calendar
                </Link>
                <Link href="/provider/visits" className="text-gray-600 hover:text-blue-600">
                  Patients
                </Link>
                <Link href="/provider/templates" className="text-gray-600 hover:text-blue-600">
                  Templates
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-600">
                {user?.full_name || user?.email} ({user?.role})
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="text-red-600 border-red-200 hover:bg-red-50"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>
      <main className="container mx-auto p-4">
        {children}
      </main>
    </div>
  );
}
