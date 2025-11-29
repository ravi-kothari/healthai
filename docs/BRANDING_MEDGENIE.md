# MediGenie Branding Implementation

## 🎯 Brand Identity

**Name**: MediGenie
**Domain**: medgenie.co
**Tagline**: "Your AI healthcare companion"

## 📝 Brand Story

MediGenie combines "Medical" + "Genie" to represent an AI assistant that grants healthcare wishes:
- **Wish 1**: Save time with automated PreVisit questionnaires
- **Wish 2**: Enhance care quality with ambient AI support
- **Wish 3**: Improve patient experience with seamless workflows

## 🎨 Brand Voice & Tone

- **Friendly** yet **professional**
- **Innovative** but **trustworthy**
- **Magical** (genie metaphor) balanced with **clinical precision**
- Focus on **results**: time saved, care improved, patients happier

## 🏗️ Centralized Branding System

All branding is controlled through a single configuration file:

**File**: `frontend/lib/config/branding.ts`

This file contains:
- Brand name and tagline
- Product names
- Contact information
- Meta tags for SEO
- Call-to-action text
- Feature taglines

### Quick Rebrand Guide

To change branding across the entire application:

1. Open `frontend/lib/config/branding.ts`
2. Update the values:
   ```typescript
   export const branding = {
     name: "MediGenie",
     tagline: "Your AI healthcare companion",
     domain: "medgenie.co",
     // ... etc
   }
   ```
3. Rebuild frontend:
   ```bash
   cd backend/docker
   docker-compose build frontend
   docker-compose up -d frontend
   ```
4. All pages automatically update!

## 📦 Product Suite

### MediGenie PreVisit
**Purpose**: Patient questionnaires and triage before appointments
**Tagline**: "Know before you go"
**Key Benefits**:
- Automated symptom checking
- Insurance verification
- Medical history collection
- Pre-appointment prep

### MediGenie Ambient
**Purpose**: Real-time AI support during clinical visits
**Tagline**: "AI support in every visit"
**Key Benefits**:
- Live transcription
- Clinical note generation
- Context-aware suggestions
- Hands-free documentation

### CarePrep
**Purpose**: Subset of PreVisit focused on appointment preparation
**Use**: Patient-facing questionnaire workflows

### MediGenie Context
**Purpose**: Provider-facing patient context building (formerly Appoint-Ready)
**Key Benefits**:
- Patient history at a glance
- Risk stratification
- Care gap detection
- Appointment readiness score

## 🌐 Web Presence

### Primary Domain
- **Production**: https://medgenie.co
- **Development**: http://localhost:3000

### Email
- **Support**: support@medgenie.co
- **General**: hello@medgenie.co
- **Sales**: sales@medgenie.co

### Social Media
- Twitter: @medgenie (when active)
- LinkedIn: /company/medgenie (when active)
- Facebook: /medgenie (when active)

## 📄 Files Updated

### Core Branding
- ✅ `frontend/lib/config/branding.ts` - **Centralized configuration**

### Layout & Metadata
- ✅ `frontend/app/layout.tsx` - Meta tags and SEO

### Authentication Pages
- ✅ `frontend/components/auth/SignupForm.tsx` - Signup form header
- ✅ `frontend/app/signup/page.tsx` - Signup page header/footer
- ✅ `frontend/app/login/page.tsx` - Login page header
- ✅ `frontend/app/register/page.tsx` - Register page header

### Other Pages
- ✅ `frontend/app/demo/page.tsx` - Demo environment

### Landing Page
- ⏸️ `frontend/app/page.tsx` - (Deferred - uses generic copy)

## 🎨 Visual Identity (Future)

### Logo Concepts
1. **Genie Lamp + Medical Cross**
   - Stylized lamp integrated with healthcare symbol
   - Modern, minimal design

2. **Abstract "M" with Sparkle**
   - Letter M for MediGenie
   - Star/sparkle elements representing AI "magic"
   - Clean, tech-forward

3. **Chat Bubble + Stethoscope**
   - Represents conversation (AI) + care (medical)
   - Friendly, approachable

### Color Palette
**Primary**: Deep Teal (#0D9488)
- Trust, healthcare, professional

**Accent**: Gold (#F59E0B)
- Premium, magic, genie lamp
- Use sparingly for CTAs

**Secondary**: Purple (#8B5CF6)
- Innovation, AI, intelligence
- Gradient backgrounds

**Neutral**: White + Slate Gray (#64748B)
- Clean, modern, readable

### Typography
**Headers**: Inter (Bold 700)
**Body**: Inter (Regular 400, Medium 500)
**Code/Technical**: Roboto Mono

## 📊 SEO & Meta Tags

### Primary Meta Tags
```html
<title>MediGenie - AI-Powered PreVisit & Ambient Clinical Support</title>
<meta name="description" content="Transform your practice with MediGenie's AI-driven patient questionnaires and real-time ambient support. Save time, improve care quality, enhance patient experience." />
<meta name="keywords" content="medgenie, healthcare AI, previsit questionnaire, ambient AI, clinical documentation, medical AI, patient intake, ai scribe" />
```

### Open Graph (Social Sharing)
```html
<meta property="og:title" content="MediGenie - Your AI Healthcare Companion" />
<meta property="og:description" content="AI-powered PreVisit questionnaires and ambient clinical support" />
<meta property="og:url" content="https://medgenie.co" />
<meta property="og:type" content="website" />
```

## 🎯 Key Messaging

### Elevator Pitch (30 seconds)
"MediGenie is your AI healthcare companion that saves hours for doctors and patients. We automate PreVisit questionnaires so providers know before patients arrive, then provide real-time ambient AI support during visits for hands-free documentation. It's like having a genie in your practice—granting the wish of more time for actual care."

### Value Propositions

**For Providers**:
- ⏱️ Save 2-3 hours per day on documentation
- 📋 Complete patient context before the visit
- 🎯 Better prepared appointments
- 💡 AI-powered clinical insights

**For Patients**:
- ⚡ Faster check-in and visits
- 📱 Complete forms from home
- 🤝 More face-time with providers
- ✨ Better care experience

**For Practices**:
- 📈 Increased patient throughput
- 💰 Improved billing accuracy
- 😊 Higher patient satisfaction
- 🔒 HIPAA-compliant automation

## 🚀 Launch Checklist

### Before Going Live
- [ ] Finalize logo design
- [ ] Set up medgenie.co domain and DNS
- [ ] Configure SSL certificates
- [ ] Set up professional email (support@medgenie.co)
- [ ] Create social media accounts
- [ ] Design favicon and app icons
- [ ] Update all marketing materials
- [ ] Test all branding across devices

### Content Updates Needed
- [ ] Landing page hero section
- [ ] About page with brand story
- [ ] Features pages (PreVisit, Ambient)
- [ ] Pricing page
- [ ] Blog/resources section
- [ ] Legal pages (Terms, Privacy, BAA)

## 📝 Brand Guidelines

### Do's
✅ Use "MediGenie" (capital M, capital G)
✅ Emphasize time savings and care quality
✅ Use friendly, professional tone
✅ Highlight AI benefits without being technical
✅ Focus on user outcomes

### Don'ts
❌ Don't use "Medigenie", "mediGenie", or "MEDIGENIE"
❌ Don't overpromise AI capabilities
❌ Don't use medical jargon in marketing
❌ Don't compare directly to competitors
❌ Don't forget HIPAA compliance mentions

## 🔄 Changelog

### 2024-11-28 - Initial MediGenie Branding
- Created centralized branding configuration
- Updated all authentication pages
- Implemented meta tags and SEO
- Domain: medgenie.co
- Tagline: "Your AI healthcare companion"

---

**Brand Owner**: MediGenie Team
**Last Updated**: 2024-11-28
**Next Review**: Q1 2025
