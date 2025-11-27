'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { MyNotesAndForms } from '@/components/documents/MyNotesAndForms';
import { TemplateLibrary } from '@/components/documents/TemplateLibrary';
import { Video } from 'lucide-react';
import Link from 'next/link';

export default function DocumentsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">Notes and Forms</h2>
          <p className="text-gray-600 mt-1">Manage your clinical documentation templates</p>
        </div>
        <Link
          href="#"
          className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          <Video className="w-4 h-4" />
          Watch a quick video about creating templates
        </Link>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="my-notes" className="w-full">
        <TabsList className="border-b border-gray-200 bg-transparent h-auto p-0 w-full justify-start">
          <TabsTrigger
            value="my-notes"
            className="border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 data-[state=active]:bg-transparent rounded-none px-4 py-3"
          >
            My Notes & Forms
          </TabsTrigger>
          <TabsTrigger
            value="template-library"
            className="border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 data-[state=active]:bg-transparent rounded-none px-4 py-3"
          >
            Template Library
          </TabsTrigger>
        </TabsList>

        <TabsContent value="my-notes" className="mt-6">
          <MyNotesAndForms />
        </TabsContent>

        <TabsContent value="template-library" className="mt-6">
          <TemplateLibrary />
        </TabsContent>
      </Tabs>
    </div>
  );
}
