'use client';

import React, { useState, useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { practiceSettingsSchema, PracticeSettingsFormValues } from '@/lib/validators/auth';
import { timezones, cancellationPolicies } from '@/lib/mock/documents';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Upload, X } from 'lucide-react';

export default function PracticeSettingsPage() {
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<PracticeSettingsFormValues>({
    resolver: zodResolver(practiceSettingsSchema),
    defaultValues: {
      practiceName: 'Rakesh Mondal',
      practiceEmail: 'saasui@rakeshmondal.in',
      timezone: timezones[0],
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setValue('logo', file);
      setLogoPreview(URL.createObjectURL(file));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setValue('logo', file);
      setLogoPreview(URL.createObjectURL(file));
    }
  };

  const removeLogo = () => {
    setValue('logo', null);
    if (logoPreview) {
      URL.revokeObjectURL(logoPreview);
      setLogoPreview(null);
    }
  };

  const onSubmit = async (data: PracticeSettingsFormValues) => {
    console.log('Practice settings submitted:', data);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    alert('Settings saved successfully!');
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-gray-900">My Practice</h2>
        <p className="text-gray-600 mt-1">Manage your practice details and settings</p>
      </div>

      <div className="bg-white border-t border-gray-200">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            <button className="border-b-2 border-blue-600 py-4 px-1 text-sm font-medium text-blue-600">
              Details
            </button>
            <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 py-4 px-1 text-sm font-medium">
              Locations
            </button>
          </nav>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Practice Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Practice Information</h3>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="practiceName">
                  <span className="text-red-600">* </span>Practice Name
                </Label>
                <Input
                  id="practiceName"
                  {...register('practiceName')}
                  className={errors.practiceName ? 'border-red-500' : ''}
                />
                {errors.practiceName && (
                  <p className="text-sm text-red-600">{errors.practiceName.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="practiceEmail">
                  Practice Email
                  <span className="ml-1 text-gray-400 cursor-help" title="Info">
                    ⓘ
                  </span>
                </Label>
                <Input
                  id="practiceEmail"
                  type="email"
                  {...register('practiceEmail')}
                  className={errors.practiceEmail ? 'border-red-500' : ''}
                />
                {errors.practiceEmail && (
                  <p className="text-sm text-red-600">{errors.practiceEmail.message}</p>
                )}
              </div>
            </div>

            <div className="mt-6 space-y-2">
              <Label htmlFor="timezone">Time Zone</Label>
              <Select
                id="timezone"
                {...register('timezone')}
                className={errors.timezone ? 'border-red-500' : ''}
              >
                {timezones.map((tz) => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </Select>
              {errors.timezone && (
                <p className="text-sm text-red-600">{errors.timezone.message}</p>
              )}
            </div>
          </div>

          {/* Practice Logo */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Practice Logo</h3>
            <p className="text-sm text-gray-600 mb-4">
              Add your practice's logo for use on your SimplePractice documents. You can manage which
              documents include the logo{' '}
              <a href="#" className="text-blue-600 hover:underline">
                here
              </a>
              .
            </p>

            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isDragging
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-300 hover:border-blue-500'
              }`}
            >
              {logoPreview ? (
                <div className="relative inline-block">
                  <img
                    src={logoPreview}
                    alt="Logo preview"
                    className="h-24 w-auto mx-auto rounded-md"
                  />
                  <button
                    type="button"
                    onClick={removeLogo}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-gray-500">
                  <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mb-3">
                    <Upload className="h-6 w-6 text-gray-400" />
                  </div>
                  <label
                    htmlFor="logoUpload"
                    className="text-blue-600 hover:text-blue-700 font-medium cursor-pointer"
                  >
                    Choose image
                  </label>
                  <span className="mx-2">or drag and drop image</span>
                  <p className="text-sm mt-2">
                    Upload a .jpg or .png image under 10 MB, with a minimum of 200px height and
                    300px width.
                  </p>
                  <input
                    id="logoUpload"
                    type="file"
                    accept="image/jpeg,image/png"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Practice Phone */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Practice Phone</h3>
            <Button type="button" variant="outline">
              Add Phone Number
            </Button>
          </div>

          {/* Cancellation Policy */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Cancellation policy</h3>
            <p className="text-sm text-gray-600 mb-4">
              How many hours before their appointment must a client cancel via text, voice
              reminders, or the Client Portal to avoid penalty?
            </p>

            <Select id="cancellationPolicy" {...register('cancellationPolicy')} className="max-w-md">
              {cancellationPolicies.map((policy) => (
                <option key={policy} value={policy}>
                  {policy}
                </option>
              ))}
            </Select>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 border-t pt-6">
            <Button type="button" variant="outline">
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
