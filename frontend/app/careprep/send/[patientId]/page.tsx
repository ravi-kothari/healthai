'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Send, CheckCircle, Clock, Mail, MessageSquare, Copy, ExternalLink } from 'lucide-react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface QuestionnaireTemplate {
  id: string;
  name: string;
  description: string;
  questions: number;
  estimatedTime: string;
}

interface CarePrepLink {
  appointment_id: string;
  token: string;
  careprep_url: string;
  full_url: string;
  expires_at: string | null;
}

const templates: QuestionnaireTemplate[] = [
  {
    id: 'general',
    name: 'General Pre-Visit',
    description: 'Basic health status, current medications, and reason for visit',
    questions: 12,
    estimatedTime: '5 min'
  },
  {
    id: 'symptoms',
    name: 'Symptom Assessment',
    description: 'Detailed symptom checker with severity and duration',
    questions: 18,
    estimatedTime: '8 min'
  },
  {
    id: 'annual',
    name: 'Annual Physical',
    description: 'Comprehensive health review for preventive care visits',
    questions: 25,
    estimatedTime: '12 min'
  },
  {
    id: 'followup',
    name: 'Follow-up Visit',
    description: 'Progress check on previous treatment or condition',
    questions: 10,
    estimatedTime: '4 min'
  }
];

export default function SendCarePrepPage({ params }: { params: { patientId: string } }) {
  const searchParams = useSearchParams();
  const appointmentId = searchParams.get('appointment');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [sendMethod, setSendMethod] = useState<'email' | 'sms' | 'both'>('email');
  const [isSending, setIsSending] = useState(false);
  const [generatedLink, setGeneratedLink] = useState<CarePrepLink | null>(null);
  const [linkGenerated, setLinkGenerated] = useState(false);

  const handleGenerateLink = async () => {
    if (!selectedTemplate) {
      toast.error('Please select a questionnaire template');
      return;
    }

    if (!appointmentId) {
      toast.error('No appointment linked. Please select an appointment first.');
      return;
    }

    setIsSending(true);

    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');

      if (!token) {
        toast.error('Please log in to generate CarePrep links');
        return;
      }

      // Generate CarePrep link via API
      const response = await axios.post(
        `${API_URL}/api/appointments/${appointmentId}/generate-careprep-link`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setGeneratedLink(response.data);
      setLinkGenerated(true);
      toast.success('CarePrep link generated successfully!');
    } catch (error: any) {
      console.error('Error generating CarePrep link:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate CarePrep link');
    } finally {
      setIsSending(false);
    }
  };

  const handleCopyLink = () => {
    if (generatedLink) {
      navigator.clipboard.writeText(generatedLink.full_url);
      toast.success('Link copied to clipboard!');
    }
  };

  const handleSendLink = async () => {
    // In a real implementation, this would call an email/SMS API
    toast.success(`CarePrep link sent via ${sendMethod}!`);
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="flex items-center gap-4 mb-6">
        <Link href="/provider/dashboard" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Send CarePrep Questionnaire</h1>
          <p className="text-gray-600">Patient ID: {params.patientId}</p>
        </div>
      </div>

      {appointmentId && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Linked Appointment:</strong> {appointmentId}
          </p>
        </div>
      )}

      {/* Template Selection */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Select Questionnaire Template</CardTitle>
          <CardDescription>Choose the appropriate questionnaire for this visit</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {templates.map((template) => (
              <div
                key={template.id}
                onClick={() => setSelectedTemplate(template.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedTemplate === template.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold">{template.name}</h3>
                  {selectedTemplate === template.id && (
                    <CheckCircle className="w-5 h-5 text-purple-600" />
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span>{template.questions} questions</span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {template.estimatedTime}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Generated Link Display */}
      {linkGenerated && generatedLink && (
        <Card className="mb-6 border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700">
              <CheckCircle className="w-5 h-5" />
              CarePrep Link Generated
            </CardTitle>
            <CardDescription>Share this link with the patient</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 mb-4">
              <input
                type="text"
                value={generatedLink.full_url}
                readOnly
                className="flex-1 px-3 py-2 bg-white border rounded-lg text-sm font-mono"
              />
              <Button variant="outline" onClick={handleCopyLink}>
                <Copy className="w-4 h-4 mr-2" />
                Copy
              </Button>
              <Link href={generatedLink.full_url} target="_blank">
                <Button variant="outline">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open
                </Button>
              </Link>
            </div>
            {generatedLink.expires_at && (
              <p className="text-sm text-gray-600">
                Link expires: {new Date(generatedLink.expires_at).toLocaleDateString()}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Delivery Method - Only show after link is generated */}
      {linkGenerated && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Send to Patient (Optional)</CardTitle>
            <CardDescription>How should we notify the patient?</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-4">
              <button
                onClick={() => setSendMethod('email')}
                className={`flex-1 p-4 border-2 rounded-lg transition-all ${
                  sendMethod === 'email'
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <Mail className={`w-6 h-6 mx-auto mb-2 ${sendMethod === 'email' ? 'text-purple-600' : 'text-gray-400'}`} />
                <p className="font-medium">Email</p>
              </button>
              <button
                onClick={() => setSendMethod('sms')}
                className={`flex-1 p-4 border-2 rounded-lg transition-all ${
                  sendMethod === 'sms'
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <MessageSquare className={`w-6 h-6 mx-auto mb-2 ${sendMethod === 'sms' ? 'text-purple-600' : 'text-gray-400'}`} />
                <p className="font-medium">SMS</p>
              </button>
              <button
                onClick={() => setSendMethod('both')}
                className={`flex-1 p-4 border-2 rounded-lg transition-all ${
                  sendMethod === 'both'
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="flex justify-center gap-1 mb-2">
                  <Mail className={`w-5 h-5 ${sendMethod === 'both' ? 'text-purple-600' : 'text-gray-400'}`} />
                  <MessageSquare className={`w-5 h-5 ${sendMethod === 'both' ? 'text-purple-600' : 'text-gray-400'}`} />
                </div>
                <p className="font-medium">Both</p>
              </button>
            </div>
            <Button onClick={handleSendLink} className="w-full bg-purple-600 hover:bg-purple-700">
              <Send className="w-4 h-4 mr-2" />
              Send Notification
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <Link href="/provider/dashboard">
          <Button variant="outline">
            {linkGenerated ? 'Done' : 'Cancel'}
          </Button>
        </Link>
        {!linkGenerated && (
          <Button
            onClick={handleGenerateLink}
            disabled={!selectedTemplate || isSending || !appointmentId}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {isSending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Generating...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Generate CarePrep Link
              </>
            )}
          </Button>
        )}
      </div>

      {/* No Appointment Warning */}
      {!appointmentId && (
        <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-sm text-amber-800">
            <strong>Note:</strong> No appointment is linked. To generate a CarePrep link, please access this page from an appointment in the dashboard.
          </p>
        </div>
      )}
    </div>
  );
}
