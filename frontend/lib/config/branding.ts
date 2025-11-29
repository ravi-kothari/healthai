/**
 * Centralized Branding Configuration
 *
 * Update this file to change branding across the entire application.
 * All brand names, taglines, and metadata are controlled here.
 */

export const branding = {
  // Primary Brand Name
  name: "MediGenie",

  // Short name (for mobile, small spaces)
  shortName: "MediGenie",

  // Tagline / Description
  tagline: "Your AI healthcare companion",

  // Full description (for meta tags, about sections)
  description: "AI-powered PreVisit questionnaires and ambient clinical support - Save time for doctors and patients with intelligent automation",

  // Domain
  domain: "medgenie.co",
  url: "https://medgenie.co",

  // Product Names
  products: {
    previsit: "MediGenie PreVisit",
    ambient: "MediGenie Ambient",
    careprep: "CarePrep",
    context: "MediGenie Context",
  },

  // Company/Legal Name
  companyName: "MediGenie",

  // Copyright
  copyrightYear: 2024,
  copyrightText: "MediGenie",

  // Contact & Support
  support: {
    email: "support@medgenie.co",
    phone: "(555) 123-4567",
  },

  // Social Media (add when available)
  social: {
    twitter: "",
    linkedin: "",
    facebook: "",
  },

  // Meta Tags
  meta: {
    title: "MediGenie - AI-Powered PreVisit & Ambient Clinical Support",
    description: "Transform your practice with MediGenie's AI-driven patient questionnaires and real-time ambient support. Save time, improve care quality, enhance patient experience.",
    keywords: "medgenie, healthcare AI, previsit questionnaire, ambient AI, clinical documentation, medical AI, patient intake, ai scribe",
    author: "MediGenie Team",
  },

  // Feature Taglines
  features: {
    previsit: "Know before you go",
    ambient: "AI support in every visit",
    timeSavings: "Hours saved, care improved",
    intelligence: "Smarter visits, better outcomes",
  },

  // Call to Action Text
  cta: {
    primary: "Start Free Trial",
    secondary: "Schedule Demo",
    signup: "Get Started with MediGenie",
    login: "Sign in to MediGenie",
  },
} as const;

// Helper function to get full page title
export const getPageTitle = (pageTitle?: string): string => {
  if (!pageTitle) return branding.meta.title;
  return `${pageTitle} | ${branding.name}`;
};

// Helper function to format copyright
export const getCopyright = (): string => {
  return `© ${branding.copyrightYear} ${branding.copyrightText}`;
};

/**
 * QUICK REBRAND GUIDE:
 *
 * To change the brand name across the entire app:
 * 1. Update `branding.name` above
 * 2. Update `branding.shortName` if different
 * 3. Update `branding.tagline`
 * 4. Update `branding.meta.title` and `branding.meta.description`
 * 5. Rebuild frontend: `docker-compose build frontend`
 * 6. Restart: `docker-compose up -d frontend`
 *
 * Example for "MediGenie":
 * - name: "MediGenie"
 * - tagline: "Your AI healthcare companion"
 * - meta.title: "MediGenie - PreVisit Intelligence & Ambient AI Support"
 *
 * Example for "CareGenie":
 * - name: "CareGenie"
 * - tagline: "Smart care, zero wait"
 * - meta.title: "CareGenie - PreVisit Intelligence & Ambient AI Support"
 */
