'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/stores/authStore';
import { Activity, Calendar, LogOut } from 'lucide-react';

export default function ProviderLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [isReady, setIsReady] = useState(false);

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

  const handleLogout = () => {
    // Clear Zustand state
    useAuthStore.getState().logout();

    // Remove the auth_token cookie
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';

    // Redirect to login
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/provider/dashboard" className="flex items-center gap-2 font-bold text-xl text-blue-600">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                  <Activity className="h-5 w-5 text-white" />
                </div>
                MediGenie
              </Link>
              <nav className="hidden md:flex gap-4">
                <Link href="/provider/dashboard" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Dashboard
                </Link>
                <Link
                  href="/provider/calendar"
                  className="flex items-center gap-1 text-gray-600 hover:text-blue-600 transition-colors"
                >
                  <Calendar className="h-4 w-4" />
                  Calendar
                </Link>
                <Link href="/provider/visits" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Visits
                </Link>
                <Link href="/provider/templates" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Templates
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-700">
                <span className="font-medium">{user?.full_name || user?.email}</span>
                <span className="text-gray-500 ml-2">({user?.role})</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
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
