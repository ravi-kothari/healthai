'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/stores/authStore';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  Heart,
  Brain,
  Shield,
  Zap,
  CheckCircle2,
  ArrowRight,
  Activity,
  Users,
  Clock,
  TrendingUp,
  Clipboard,
  FileText,
  Star,
  ChevronRight,
  ChevronDown,
  Rocket,
  DollarSign,
  Building,
  Stethoscope,
  Calendar,
  BarChart,
  Sparkles,
  Lock,
  Smartphone,
  Globe
} from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'patient') {
        router.push('/patient/dashboard');
      } else if (['doctor', 'nurse', 'admin', 'staff'].includes(user.role)) {
        router.push('/provider/dashboard');
      }
    }
  }, [isAuthenticated, user, router]);

  const toggleDropdown = (menu: string) => {
    setOpenDropdown(openDropdown === menu ? null : menu);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Header - Mega Menu with Dropdowns */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-forest rounded-lg flex items-center justify-center">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900">HealthAI</span>
            </Link>

            {/* Navigation Links with Dropdowns - Hidden on mobile */}
            <nav className="hidden lg:flex items-center space-x-1">
              {/* Product Dropdown - Comprehensive 3-column mega menu */}
              <div className="relative group">
                <button
                  onMouseEnter={() => setOpenDropdown('product')}
                  className="flex items-center gap-1 px-4 py-2 text-slate-600 hover:text-forest-600 transition-colors font-medium rounded-lg hover:bg-forest-50"
                >
                  Product
                  <ChevronDown className="w-4 h-4" />
                </button>
                {openDropdown === 'product' && (
                  <div
                    onMouseLeave={() => setOpenDropdown(null)}
                    className="absolute top-full left-0 mt-2 w-[800px] bg-white rounded-xl shadow-2xl border border-slate-200 p-8 animate-fade-in"
                  >
                    <div className="grid grid-cols-3 gap-8">
                      {/* Column 1: Features */}
                      <div>
                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wide">Features</h4>
                        <div className="space-y-1">
                          <a href="/features/transcribe" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <FileText className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600 font-medium">Transcribe & Dictate</span>
                          </a>
                          <a href="/features/ai-assistant" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Sparkles className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600 font-medium">AI Assistant</span>
                          </a>
                          <a href="/features/context" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Activity className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600 font-medium">Patient Context</span>
                          </a>
                          <a href="/features/tasks" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Clipboard className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600 font-medium">Smart Tasks</span>
                          </a>
                          <Link href="/provider/templates" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <FileText className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600 font-medium">Clinical Templates</span>
                          </Link>
                          <Link href="/community" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Users className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600 font-medium">Community Templates</span>
                          </Link>
                          <a href="/features/customization" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Zap className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600 font-medium">Customization</span>
                          </a>
                        </div>
                      </div>

                      {/* Column 2: For Different Users */}
                      <div>
                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wide">For Clinicians</h4>
                        <a href="#careprep" className="flex items-start gap-3 p-3 rounded-lg hover:bg-cream-50 transition-colors group/item mb-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <Brain className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-semibold text-slate-900 group-hover/item:text-forest-600 text-sm">CarePrep</p>
                            <p className="text-xs text-slate-600">Patient preparation & symptom analysis</p>
                          </div>
                        </a>
                        <a href="#contextai" className="flex items-start gap-3 p-3 rounded-lg hover:bg-cream-50 transition-colors group/item mb-4">
                          <div className="w-10 h-10 bg-forest-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <Stethoscope className="w-5 h-5 text-forest-600" />
                          </div>
                          <div>
                            <p className="font-semibold text-slate-900 group-hover/item:text-forest-600 text-sm">ContextAI</p>
                            <p className="text-xs text-slate-600">Real-time patient context & insights</p>
                          </div>
                        </a>

                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-3 mt-4 tracking-wide">For Organizations</h4>
                        <div className="space-y-1">
                          <a href="/solutions/practices" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors text-xs text-slate-700 hover:text-forest-600">
                            Standardize quality
                          </a>
                          <a href="/solutions/hospitals" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors text-xs text-slate-700 hover:text-forest-600">
                            Scale efficiently
                          </a>
                          <a href="/solutions/loyalty" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors text-xs text-slate-700 hover:text-forest-600">
                            Patient loyalty
                          </a>
                        </div>
                      </div>

                      {/* Column 3: Resources & Platform */}
                      <div>
                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wide">Get Started</h4>
                        <div className="space-y-1">
                          <a href="/how-it-works" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Rocket className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600">How it works</span>
                          </a>
                          <a href="/changelog" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Activity className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600">Changelog</span>
                          </a>
                          <a href="/guides" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <FileText className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600">Guides</span>
                          </a>
                          <a href="/roi" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <DollarSign className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600">ROI Calculator</span>
                          </a>
                        </div>

                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-3 mt-6 tracking-wide">Platform</h4>
                        <div className="space-y-1">
                          <a href="/integrations" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Globe className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600">Integrations</span>
                          </a>
                          <a href="/security" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Lock className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600">Security & Compliance</span>
                          </a>
                          <a href="/partners" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-cream-50 transition-colors group/item text-sm">
                            <Users className="w-4 h-4 text-slate-400 group-hover/item:text-forest-600" />
                            <span className="text-slate-700 group-hover/item:text-forest-600">Partners</span>
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Solutions Dropdown */}
              <div className="relative group">
                <button
                  onMouseEnter={() => setOpenDropdown('solutions')}
                  className="flex items-center gap-1 px-4 py-2 text-slate-600 hover:text-forest-600 transition-colors font-medium rounded-lg hover:bg-forest-50"
                >
                  Solutions
                  <ChevronDown className="w-4 h-4" />
                </button>
                {openDropdown === 'solutions' && (
                  <div
                    onMouseLeave={() => setOpenDropdown(null)}
                    className="absolute top-full left-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 p-6 animate-fade-in"
                  >
                    <div className="space-y-3">
                      <a href="#" className="flex items-start gap-3 p-3 rounded-lg hover:bg-cream-50 transition-colors">
                        <Building className="w-5 h-5 text-forest-600 mt-0.5" />
                        <div>
                          <p className="font-semibold text-slate-900">Healthcare Systems</p>
                          <p className="text-sm text-slate-600">Enterprise solutions</p>
                        </div>
                      </a>
                      <a href="#" className="flex items-start gap-3 p-3 rounded-lg hover:bg-cream-50 transition-colors">
                        <Users className="w-5 h-5 text-forest-600 mt-0.5" />
                        <div>
                          <p className="font-semibold text-slate-900">Private Practices</p>
                          <p className="text-sm text-slate-600">Small to medium clinics</p>
                        </div>
                      </a>
                      <a href="#" className="flex items-start gap-3 p-3 rounded-lg hover:bg-cream-50 transition-colors">
                        <Globe className="w-5 h-5 text-forest-600 mt-0.5" />
                        <div>
                          <p className="font-semibold text-slate-900">Telehealth</p>
                          <p className="text-sm text-slate-600">Virtual care platforms</p>
                        </div>
                      </a>
                    </div>
                  </div>
                )}
              </div>

              <a href="#pricing" className="px-4 py-2 text-slate-600 hover:text-forest-600 transition-colors font-medium rounded-lg hover:bg-forest-50">
                Pricing
              </a>
              <a href="#roadmap" className="px-4 py-2 text-slate-600 hover:text-forest-600 transition-colors font-medium rounded-lg hover:bg-forest-50">
                Roadmap
              </a>

              {/* Resources Dropdown */}
              <div className="relative group">
                <button
                  onMouseEnter={() => setOpenDropdown('resources')}
                  className="flex items-center gap-1 px-4 py-2 text-slate-600 hover:text-forest-600 transition-colors font-medium rounded-lg hover:bg-forest-50"
                >
                  Resources
                  <ChevronDown className="w-4 h-4" />
                </button>
                {openDropdown === 'resources' && (
                  <div
                    onMouseLeave={() => setOpenDropdown(null)}
                    className="absolute top-full right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-slate-200 p-4 animate-fade-in"
                  >
                    <div className="space-y-2">
                      <a href="#" className="block px-3 py-2 text-slate-700 hover:text-forest-600 hover:bg-cream-50 rounded-lg transition-colors">
                        Documentation
                      </a>
                      <a href="#" className="block px-3 py-2 text-slate-700 hover:text-forest-600 hover:bg-cream-50 rounded-lg transition-colors">
                        Help Center
                      </a>
                      <a href="#" className="block px-3 py-2 text-slate-700 hover:text-forest-600 hover:bg-cream-50 rounded-lg transition-colors">
                        Blog
                      </a>
                      <a href="#" className="block px-3 py-2 text-slate-700 hover:text-forest-600 hover:bg-cream-50 rounded-lg transition-colors">
                        Case Studies
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </nav>

            {/* CTA Buttons */}
            <div className="flex items-center space-x-3">
              <Link href="/auth/login">
                <Button variant="ghost" size="base">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/register">
                <Button variant="primary" size="base" rightIcon={<ArrowRight className="w-4 h-4" />}>
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-cream-50 via-white to-sand-50">
        {/* Decorative blobs */}
        <div className="absolute top-20 right-0 w-96 h-96 bg-forest-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="text-center lg:text-left">
              <Badge variant="primary" size="lg" className="mb-6">
                AI-Powered Healthcare Platform
              </Badge>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 mb-6 leading-tight">
                Transform Patient Care with{' '}
                <span className="text-forest-600">Intelligent Preparation</span>
              </h1>

              <p className="text-lg sm:text-xl text-slate-600 mb-8 max-w-2xl">
                Empower patients with AI-driven symptom analysis and equip providers with comprehensive
                appointment context—all before the visit begins.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link href="/auth/register">
                  <Button variant="primary" size="lg" rightIcon={<ChevronRight className="w-5 h-5" />}>
                    Start Free Trial
                  </Button>
                </Link>
                <Button variant="outline" size="lg" leftIcon={<Activity className="w-5 h-5" />}>
                  Watch Demo
                </Button>
              </div>

              {/* Social Proof */}
              <div className="mt-12 flex items-center gap-8 justify-center lg:justify-start text-sm text-slate-600">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-forest-600" />
                  <span>HIPAA Compliant</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-forest-600" />
                  <span>FHIR Compatible</span>
                </div>
              </div>
            </div>

            {/* Right Visual */}
            <div className="relative">
              <div className="relative z-10 bg-white rounded-2xl shadow-2xl p-8 transform hover:scale-105 transition-transform duration-300">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="font-semibold text-slate-900">Next Appointment</h3>
                    <p className="text-sm text-slate-600">John Doe - 2:30 PM Today</p>
                  </div>
                  <Badge variant="success">CarePrep Complete</Badge>
                </div>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Brain className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">AI Analysis Complete</p>
                      <p className="text-sm text-slate-600">Moderate urgency, follow-up needed</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                      <Activity className="w-5 h-5 text-amber-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">3 Care Gaps Detected</p>
                      <p className="text-sm text-slate-600">Preventive screenings overdue</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                      <Heart className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">Risk Score: Moderate</p>
                      <p className="text-sm text-slate-600">Cardiovascular & diabetes factors</p>
                    </div>
                  </div>
                </div>
              </div>
              {/* Decorative element */}
              <div className="absolute -bottom-6 -right-6 w-full h-full bg-gradient-forest rounded-2xl -z-10"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-gradient-slate py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { number: '85%', label: 'Reduction in Pre-Visit Admin Time' },
              { number: '4.2min', label: 'Average Time Saved Per Appointment' },
              { number: '92%', label: 'Patient Satisfaction Score' },
              { number: '50k+', label: 'Successful Patient Encounters' },
            ].map((stat, idx) => (
              <div key={idx} className="text-center">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold text-forest-500 mb-2">
                  {stat.number}
                </div>
                <div className="text-sm sm:text-base text-white/90">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PreVisit.ai Feature Section */}
      <section id="features" className="py-20 sm:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Content */}
            <div>
              <Badge variant="info" className="mb-4">For Patients</Badge>
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
                CarePrep: Your Smart Health Companion
              </h2>
              <p className="text-lg text-slate-600 mb-8">
                AI-powered symptom analysis that helps patients understand their health concerns
                before visiting a provider, ensuring efficient and informed care.
              </p>

              <div className="space-y-4 mb-8">
                {[
                  { icon: Brain, text: 'AI-powered symptom analysis' },
                  { icon: Clipboard, text: 'Personalized medical questionnaires' },
                  { icon: Zap, text: 'Smart appointment preparation' },
                  { icon: Shield, text: 'Secure health data handling' },
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-forest-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle2 className="w-4 h-4 text-forest-600" />
                    </div>
                    <div className="flex items-center gap-2">
                      <feature.icon className="w-5 h-5 text-forest-600" />
                      <span className="text-slate-700 font-medium">{feature.text}</span>
                    </div>
                  </div>
                ))}
              </div>

              <Button variant="primary" size="lg" rightIcon={<ArrowRight className="w-5 h-5" />}>
                Try Symptom Checker
              </Button>
            </div>

            {/* Right Visual - Phone Mockup */}
            <div className="relative">
              <Card variant="elevated" className="transform hover:scale-105 transition-transform duration-300">
                <CardContent className="p-8">
                  <div className="mb-6">
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">Symptom Analysis</h3>
                    <Badge variant="warning">In Progress</Badge>
                  </div>
                  <div className="space-y-4">
                    <div className="p-4 bg-cream-50 rounded-lg">
                      <p className="text-sm font-medium text-slate-900 mb-1">Primary Symptom</p>
                      <p className="text-slate-600">Persistent headache - 3 days</p>
                    </div>
                    <div className="p-4 bg-cream-50 rounded-lg">
                      <p className="text-sm font-medium text-slate-900 mb-1">Severity</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-slate-200 rounded-full h-2">
                          <div className="bg-amber-500 h-2 rounded-full" style={{width: '60%'}}></div>
                        </div>
                        <span className="text-sm text-slate-600">Moderate</span>
                      </div>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm font-medium text-blue-900 mb-1">AI Recommendation</p>
                      <p className="text-sm text-blue-700">Schedule appointment with primary care within 3-5 days</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Appoint-Ready Feature Section */}
      <section className="py-20 sm:py-32 bg-cream-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Visual - Desktop Mockup */}
            <div className="order-2 lg:order-1 relative">
              <Card variant="elevated" className="transform hover:scale-105 transition-transform duration-300">
                <CardContent className="p-8">
                  <div className="mb-6">
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">Patient Context Dashboard</h3>
                    <p className="text-sm text-slate-600">John Doe - MRN: 123456</p>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg">
                      <span className="text-sm font-medium text-emerald-900">CarePrep Complete</span>
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                      <span className="text-sm font-medium text-amber-900">3 Care Gaps</span>
                      <Badge variant="warning" size="sm">Action Needed</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <span className="text-sm font-medium text-red-900">Diabetes Risk: Moderate</span>
                      <Badge variant="danger" size="sm">15.0</Badge>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-lg">
                      <p className="text-xs font-medium text-slate-500 uppercase mb-2">Recent Activity</p>
                      <div className="space-y-2 text-sm text-slate-700">
                        <p>• Last visit: 2 weeks ago</p>
                        <p>• Lab results: Within normal range</p>
                        <p>• Medications: 2 active prescriptions</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Content */}
            <div className="order-1 lg:order-2">
              <Badge variant="primary" className="mb-4">For Providers</Badge>
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
                ContextAI: Walk In Fully Prepared
              </h2>
              <p className="text-lg text-slate-600 mb-8">
                Comprehensive appointment preparation that aggregates patient data from multiple sources,
                giving you everything you need for informed care delivery.
              </p>

              <div className="space-y-4 mb-8">
                {[
                  { icon: FileText, text: 'Comprehensive patient context in seconds' },
                  { icon: TrendingUp, text: 'AI-powered risk stratification' },
                  { icon: Activity, text: 'Automated care gap detection' },
                  { icon: Users, text: 'Real-time FHIR integration' },
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-forest-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle2 className="w-4 h-4 text-forest-600" />
                    </div>
                    <div className="flex items-center gap-2">
                      <feature.icon className="w-5 h-5 text-forest-600" />
                      <span className="text-slate-700 font-medium">{feature.text}</span>
                    </div>
                  </div>
                ))}
              </div>

              <Button variant="primary" size="lg" rightIcon={<ArrowRight className="w-5 h-5" />}>
                See Provider Dashboard
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 sm:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-slate-600 max-w-3xl mx-auto">
              Three simple steps to transform your healthcare delivery with AI-powered preparation
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Patient Completes CarePrep',
                description: 'Patients answer AI-guided questions about their symptoms and health concerns before their appointment',
                icon: Clipboard,
                color: 'blue',
              },
              {
                step: '02',
                title: 'AI Analyzes & Prepares Context',
                description: 'Our system builds comprehensive appointment context, detecting care gaps and calculating risk scores',
                icon: Brain,
                color: 'forest',
              },
              {
                step: '03',
                title: 'Provider Reviews & Delivers Care',
                description: 'Doctors walk in fully prepared with actionable insights and comprehensive patient context',
                icon: Heart,
                color: 'emerald',
              },
            ].map((step, idx) => (
              <div key={idx} className="relative">
                {/* Connector Line */}
                {idx < 2 && (
                  <div className="hidden md:block absolute top-20 left-1/2 w-full h-0.5 bg-gradient-to-r from-forest-200 to-forest-300 z-0"></div>
                )}

                <Card variant="elevated" className="relative z-10 h-full hover:scale-105 transition-transform duration-300">
                  <CardContent className="p-8 text-center">
                    <div className={`w-16 h-16 bg-${step.color}-100 rounded-full flex items-center justify-center mx-auto mb-4`}>
                      <step.icon className={`w-8 h-8 text-${step.color}-600`} />
                    </div>
                    <div className="text-4xl font-bold text-forest-600 mb-4">{step.step}</div>
                    <h3 className="text-xl font-semibold text-slate-900 mb-3">{step.title}</h3>
                    <p className="text-slate-600">{step.description}</p>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Grid */}
      <section id="benefits" className="py-20 sm:py-32 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
              Why Healthcare Teams Choose Us
            </h2>
            <p className="text-lg text-slate-600">
              Powerful features designed for modern healthcare delivery
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Clock,
                title: 'Save Time',
                description: 'Reduce pre-visit admin by 85% and focus on what matters most—patient care',
                color: 'blue',
              },
              {
                icon: Heart,
                title: 'Improve Care',
                description: 'Better patient outcomes with comprehensive context and AI-powered insights',
                color: 'red',
              },
              {
                icon: Star,
                title: 'Enhance Experience',
                description: '92% patient satisfaction improvement with streamlined preparation',
                color: 'amber',
              },
              {
                icon: Shield,
                title: 'HIPAA Compliant',
                description: 'Bank-grade security and compliance built into every feature',
                color: 'green',
              },
              {
                icon: Zap,
                title: 'Easy Integration',
                description: 'Seamless FHIR integration with existing EHRs and healthcare systems',
                color: 'purple',
              },
              {
                icon: Brain,
                title: 'AI-Powered',
                description: 'Cutting-edge Azure OpenAI technology for intelligent analysis',
                color: 'forest',
              },
            ].map((benefit, idx) => (
              <Card key={idx} variant="interactive" className="group">
                <CardContent className="p-8">
                  <div className={`w-12 h-12 bg-${benefit.color}-100 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <benefit.icon className={`w-6 h-6 text-${benefit.color}-600`} />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-3">{benefit.title}</h3>
                  <p className="text-slate-600">{benefit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section - SaaS Plans */}
      <section id="pricing" className="py-20 sm:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge variant="primary" size="lg" className="mb-4">
              Flexible Pricing
            </Badge>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
              Choose the Plan That Fits Your Practice
            </h2>
            <p className="text-lg text-slate-600 max-w-3xl mx-auto">
              Start with our 14-day free trial. No credit card required. Scale as you grow.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Starter Plan */}
            <Card variant="outlined" className="relative">
              <CardContent className="p-8">
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">Starter</h3>
                  <p className="text-slate-600">Perfect for small practices</p>
                </div>
                <div className="mb-6">
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-slate-900">$299</span>
                    <span className="text-slate-600">/month</span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">Up to 100 patients/month</p>
                </div>
                <ul className="space-y-3 mb-8">
                  {[
                    'CarePrep symptom checker',
                    'Basic appointment preparation',
                    'FHIR integration',
                    'Email support',
                    '1 provider account',
                  ].map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="w-5 h-5 text-forest-600 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button variant="outline" size="lg" className="w-full">
                  Start Free Trial
                </Button>
              </CardContent>
            </Card>

            {/* Professional Plan - Featured */}
            <Card variant="elevated" className="relative border-2 border-forest-600 shadow-xl scale-105">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                <Badge variant="primary" size="lg">
                  Most Popular
                </Badge>
              </div>
              <CardContent className="p-8">
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">Professional</h3>
                  <p className="text-slate-600">For growing practices</p>
                </div>
                <div className="mb-6">
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-forest-600">$599</span>
                    <span className="text-slate-600">/month</span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">Up to 500 patients/month</p>
                </div>
                <ul className="space-y-3 mb-8">
                  {[
                    'Everything in Starter',
                    'ContextAI dashboard',
                    'Care gap detection',
                    'Risk stratification',
                    'Priority support',
                    'Up to 5 provider accounts',
                    'Custom integrations',
                  ].map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="w-5 h-5 text-forest-600 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button variant="primary" size="lg" className="w-full">
                  Start Free Trial
                </Button>
              </CardContent>
            </Card>

            {/* Enterprise Plan */}
            <Card variant="outlined" className="relative">
              <CardContent className="p-8">
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">Enterprise</h3>
                  <p className="text-slate-600">For healthcare systems</p>
                </div>
                <div className="mb-6">
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-slate-900">Custom</span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">Unlimited patients</p>
                </div>
                <ul className="space-y-3 mb-8">
                  {[
                    'Everything in Professional',
                    'Dedicated account manager',
                    'Custom AI model training',
                    'Advanced analytics',
                    '24/7 phone support',
                    'Unlimited provider accounts',
                    'SSO & advanced security',
                    'SLA guarantee',
                  ].map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="w-5 h-5 text-forest-600 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button variant="outline" size="lg" className="w-full">
                  Contact Sales
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Pricing Footer */}
          <div className="mt-12 text-center">
            <p className="text-slate-600 mb-4">
              All plans include HIPAA compliance, data encryption, and FHIR R4 support
            </p>
            <div className="flex items-center justify-center gap-8 text-sm text-slate-500">
              <span className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                HIPAA Compliant
              </span>
              <span className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                256-bit Encryption
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                99.9% Uptime SLA
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Roadmap - Future Features */}
      <section id="roadmap" className="py-20 sm:py-32 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge variant="primary" size="lg" className="mb-4">
              Coming Soon
            </Badge>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
              The Future of Healthcare AI
            </h2>
            <p className="text-lg text-slate-300 max-w-3xl mx-auto">
              We're constantly innovating to bring you cutting-edge features that transform healthcare delivery
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Smartphone,
                title: 'Mobile Apps',
                description: 'Native iOS and Android apps for patients and providers with offline support',
                timeline: 'Q2 2025',
                status: 'In Development',
              },
              {
                icon: Brain,
                title: 'Advanced AI Diagnostics',
                description: 'Multi-modal AI analysis including imaging, labs, and clinical notes',
                timeline: 'Q3 2025',
                status: 'Planning',
              },
              {
                icon: Activity,
                title: 'Real-time Vitals Integration',
                description: 'Connect wearables and IoT devices for continuous patient monitoring',
                timeline: 'Q3 2025',
                status: 'Planning',
              },
              {
                icon: Users,
                title: 'Team Collaboration',
                description: 'Multi-provider workflows with real-time collaboration and handoffs',
                timeline: 'Q4 2025',
                status: 'Research',
              },
              {
                icon: BarChart,
                title: 'Advanced Analytics',
                description: 'Population health insights, outcome tracking, and performance dashboards',
                timeline: 'Q4 2025',
                status: 'Research',
              },
              {
                icon: Globe,
                title: 'Multi-language Support',
                description: 'AI-powered translation supporting 50+ languages for global healthcare',
                timeline: 'Q1 2026',
                status: 'Research',
              },
            ].map((feature, idx) => (
              <Card key={idx} variant="elevated" className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all">
                <CardContent className="p-6">
                  <div className="w-12 h-12 bg-forest-500/20 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-forest-400" />
                  </div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
                    <Badge variant="outline" size="sm" className="border-forest-400/50 text-forest-400">
                      {feature.status}
                    </Badge>
                  </div>
                  <p className="text-slate-300 mb-4">{feature.description}</p>
                  <div className="flex items-center gap-2 text-sm text-forest-400">
                    <Calendar className="w-4 h-4" />
                    <span>{feature.timeline}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-16 text-center">
            <p className="text-slate-300 mb-6">
              Have a feature request? We'd love to hear from you!
            </p>
            <Button
              variant="outline"
              size="lg"
              className="border-2 border-white text-white hover:bg-white/10"
              rightIcon={<ArrowRight className="w-5 h-5" />}
            >
              Submit Feature Request
            </Button>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 sm:py-32 bg-gradient-forest relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Healthcare Practice?
          </h2>
          <p className="text-xl text-white/90 mb-10">
            Join thousands of providers delivering better care with AI-powered preparation
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/register">
              <Button
                variant="outline"
                size="xl"
                className="bg-white text-forest-600 hover:bg-white/90 border-0"
                rightIcon={<ChevronRight className="w-5 h-5" />}
              >
                Start Free Trial
              </Button>
            </Link>
            <Button
              variant="outline"
              size="xl"
              className="border-2 border-white text-white hover:bg-white/10"
            >
              Schedule Demo
            </Button>
          </div>

          <p className="mt-6 text-white/80 text-sm">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
            {/* Column 1 - Brand */}
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-forest rounded-lg flex items-center justify-center">
                  <Heart className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold">HealthAI</span>
              </div>
              <p className="text-slate-400 text-sm">
                AI-powered healthcare platform for intelligent patient preparation and provider efficiency.
              </p>
            </div>

            {/* Column 2 - Product */}
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#careprep" className="hover:text-white transition-colors">CarePrep</a></li>
                <li><a href="#contextai" className="hover:text-white transition-colors">ContextAI</a></li>
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
              </ul>
            </div>

            {/* Column 3 - Company */}
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              </ul>
            </div>

            {/* Column 4 - Resources */}
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-slate-400 text-sm">
              © 2025 HealthAI. All rights reserved.
            </p>
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-forest-500" />
                HIPAA Compliant
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-forest-500" />
                FHIR R4
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
