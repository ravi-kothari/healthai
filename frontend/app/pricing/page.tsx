import Link from 'next/link';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function PricingPage() {
    const plans = [
        {
            name: 'Starter',
            price: '$29',
            description: 'Perfect for solo practitioners starting out.',
            features: [
                'Up to 100 Patients',
                'Basic Charting',
                'Appointment Scheduling',
                'Secure Messaging',
                'Email Support'
            ],
            cta: 'Start Free Trial',
            href: '/signup?plan=starter',
            popular: false
        },
        {
            name: 'Professional',
            price: '$79',
            description: 'Everything you need to grow your practice.',
            features: [
                'Unlimited Patients',
                'Advanced Charting & Templates',
                'Telehealth Integration',
                'Patient Portal',
                'e-Prescribing',
                'Priority Support'
            ],
            cta: 'Start Free Trial',
            href: '/signup?plan=professional',
            popular: true
        },
        {
            name: 'Enterprise',
            price: 'Custom',
            description: 'For large clinics and hospitals.',
            features: [
                'Everything in Professional',
                'Multi-location Support',
                'API Access',
                'SSO & Advanced Security',
                'Dedicated Account Manager',
                'Custom Training'
            ],
            cta: 'Contact Sales',
            href: '/contact',
            popular: false
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">M</div>
                        <span className="text-xl font-bold text-gray-900">MedGeni</span>
                    </Link>
                    <div className="flex items-center gap-4">
                        <Link href="/login" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                            Log in
                        </Link>
                        <Link href="/signup">
                            <Button>Get Started</Button>
                        </Link>
                    </div>
                </div>
            </header>

            <main className="py-20 px-4 sm:px-6 lg:px-8">
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                        Simple, transparent pricing
                    </h1>
                    <p className="mt-4 text-xl text-gray-600">
                        Choose the plan that's right for your practice. All plans include a 30-day free trial.
                    </p>
                </div>

                <div className="max-w-7xl mx-auto grid grid-cols-1 gap-8 md:grid-cols-3">
                    {plans.map((plan) => (
                        <Card key={plan.name} className={`flex flex-col ${plan.popular ? 'border-blue-600 shadow-lg scale-105 relative' : ''}`}>
                            {plan.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                                    Most Popular
                                </div>
                            )}
                            <CardHeader>
                                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                                <CardDescription>{plan.description}</CardDescription>
                                <div className="mt-4">
                                    <span className="text-4xl font-bold">{plan.price}</span>
                                    {plan.price !== 'Custom' && <span className="text-gray-500">/month</span>}
                                </div>
                            </CardHeader>
                            <CardContent className="flex-1">
                                <ul className="space-y-3">
                                    {plan.features.map((feature) => (
                                        <li key={feature} className="flex items-start gap-2">
                                            <Check className="h-5 w-5 text-green-500 shrink-0" />
                                            <span className="text-sm text-gray-600">{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                            <CardFooter>
                                <Link href={plan.href} className="w-full">
                                    <Button className="w-full" variant={plan.popular ? 'primary' : 'outline'}>
                                        {plan.cta}
                                    </Button>
                                </Link>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 px-6 py-12 mt-20">
                <div className="max-w-7xl mx-auto text-center text-sm text-gray-500">
                    <p>© 2025 MedGeni. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
}
