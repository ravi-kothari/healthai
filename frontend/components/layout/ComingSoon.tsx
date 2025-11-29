import Link from 'next/link';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { branding } from '@/lib/config/branding';

interface ComingSoonProps {
  title: string;
  description: string;
  estimatedLaunch?: string;
  features?: string[];
}

export const ComingSoon = ({
  title,
  description,
  estimatedLaunch = "Coming Soon",
  features = []
}: ComingSoonProps) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">{branding.shortName}</span>
            </Link>
            <Link href="/">
              <Button variant="outline" size="sm" className="flex items-center gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-8 animate-pulse">
            <Sparkles className="w-10 h-10 text-white" />
          </div>

          {/* Badge */}
          <div className="inline-block mb-6">
            <span className="px-4 py-2 rounded-full bg-blue-100 text-blue-700 text-sm font-semibold">
              {estimatedLaunch}
            </span>
          </div>

          {/* Title */}
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            {title}
          </h1>

          {/* Description */}
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            {description}
          </p>

          {/* Features Preview */}
          {features.length > 0 && (
            <div className="mb-12">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                What to Expect
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                {features.map((feature, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-white rounded-lg border border-gray-200 shadow-sm"
                  >
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center mt-0.5">
                      <svg
                        className="w-4 h-4 text-blue-600"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <p className="text-left text-gray-700">{feature}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/">
              <Button size="lg" variant="primary" className="w-full sm:w-auto">
                Explore Other Features
              </Button>
            </Link>
            <Link href="/signup">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                Join the Waitlist
              </Button>
            </Link>
          </div>

          {/* Notification Signup */}
          <div className="mt-16 p-8 bg-white rounded-2xl shadow-lg border border-gray-200 max-w-xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Get Notified When We Launch
            </h3>
            <p className="text-gray-600 mb-6">
              Be the first to know when {title} becomes available.
            </p>
            <form className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <Button type="submit" size="lg">
                Notify Me
              </Button>
            </form>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white/80 backdrop-blur-sm mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-sm text-gray-600">
            © {branding.copyrightYear} {branding.copyrightText}. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};
