import { SubscriptionPlan } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/Card';
import { Check, Sparkles } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

const plans: SubscriptionPlan[] = [
  {
    name: 'Starter',
    price: '$49/mo',
    features: [
      'Up to 50 clients',
      'Basic Scheduling',
      'Standard Invoicing',
      'Email Support',
      '5GB Storage'
    ],
    isCurrent: false,
  },
  {
    name: 'Professional',
    price: '$99/mo',
    features: [
      'Unlimited clients',
      'Advanced Scheduling',
      'Insurance Billing',
      'Client Portal',
      'Priority Support',
      '50GB Storage',
      'Custom Branding'
    ],
    isCurrent: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    features: [
      'All Professional features',
      'Team Management (Unlimited)',
      'API Access',
      'Dedicated Support',
      'Unlimited Storage',
      'Advanced Analytics',
      'Custom Integrations',
      'SLA Guarantee'
    ],
    isCurrent: false,
  },
];

export default function SubscriptionPage() {
  const currentPlan = plans.find(p => p.isCurrent);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-gray-900">Subscription</h2>
        <p className="text-gray-600 mt-1">Manage your subscription and billing details</p>
      </div>

      {/* Current Plan Card */}
      <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-white">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Your Current Plan</CardTitle>
              {currentPlan && (
                <CardDescription className="mt-1">
                  You are currently on the <span className="font-semibold text-blue-600">{currentPlan.name}</span> plan.
                </CardDescription>
              )}
            </div>
            <Badge variant="default" className="bg-blue-600">
              Active
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {currentPlan && (
            <div className="space-y-4">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                  <p className="text-4xl font-bold text-gray-900">{currentPlan.price}</p>
                  <p className="text-sm text-gray-600 mt-1">Billed monthly. Next payment on August 1, 2025.</p>
                </div>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Button variant="outline" className="border-red-200 text-red-600 hover:bg-red-50">
                    Cancel Subscription
                  </Button>
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    Update Payment Method
                  </Button>
                </div>
              </div>
              <div className="pt-4 border-t">
                <h4 className="font-medium text-gray-900 mb-2">Included Features:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {currentPlan.features.map((feature) => (
                    <div key={feature} className="flex items-center text-sm text-gray-700">
                      <Check className="mr-2 h-4 w-4 text-green-600" />
                      {feature}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Available Plans */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">Available Plans</h3>
          <Badge variant="secondary" className="bg-purple-100 text-purple-700">
            <Sparkles className="h-3 w-3 mr-1" />
            Annual billing saves 20%
          </Badge>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`flex flex-col ${plan.isCurrent ? 'border-2 border-blue-500 shadow-lg' : 'border hover:shadow-md transition-shadow'}`}
            >
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <CardTitle>{plan.name}</CardTitle>
                  {plan.isCurrent && (
                    <Badge variant="default" className="bg-blue-600">
                      Current
                    </Badge>
                  )}
                </div>
                <CardDescription className="text-3xl font-bold text-gray-900 mt-2">
                  {plan.price}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-grow">
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start text-sm">
                      <Check className="mr-2 h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  disabled={plan.isCurrent}
                  variant={plan.isCurrent ? 'secondary' : 'default'}
                >
                  {plan.isCurrent ? 'Current Plan' : plan.name === 'Enterprise' ? 'Contact Sales' : 'Upgrade'}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>

      {/* Billing History */}
      <Card>
        <CardHeader>
          <CardTitle>Billing History</CardTitle>
          <CardDescription>View your past invoices and payments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { date: 'July 1, 2025', amount: '$99.00', status: 'Paid', invoice: 'INV-2025-07' },
              { date: 'June 1, 2025', amount: '$99.00', status: 'Paid', invoice: 'INV-2025-06' },
              { date: 'May 1, 2025', amount: '$99.00', status: 'Paid', invoice: 'INV-2025-05' },
            ].map((payment) => (
              <div
                key={payment.invoice}
                className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{payment.invoice}</p>
                  <p className="text-sm text-gray-600">{payment.date}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{payment.amount}</p>
                    <Badge variant="success" className="text-xs">
                      {payment.status}
                    </Badge>
                  </div>
                  <Button variant="ghost" size="sm">
                    Download
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
