import { SignupForm } from '@/components/auth/SignupForm';
import Link from 'next/link';
import Image from 'next/image';

export default function SignupPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg" />
            <span className="text-xl font-bold text-gray-900">simplepractice</span>
          </Link>
          <Link
            href="/login"
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                clipRule="evenodd"
              />
            </svg>
            Are you a client?
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full">
          <SignupForm />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto text-center text-sm text-gray-500">
          <p>© 2024 SimplePractice · <Link href="/support" className="hover:text-gray-700">Support</Link> · <Link href="/terms" className="hover:text-gray-700">Licensed Content</Link></p>
        </div>
      </footer>
    </div>
  );
}
