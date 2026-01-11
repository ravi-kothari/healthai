import { getRequestConfig } from 'next-intl/server';

// Supported locales for MedGenie
export const locales = ['en', 'hi', 'fr'] as const;
export type Locale = (typeof locales)[number];

// Default locale
export const defaultLocale: Locale = 'en';

// Locale metadata for UI
export const localeNames: Record<Locale, string> = {
    en: 'English',
    hi: 'हिन्दी',
    fr: 'Français',
};

// Locale to region mapping
export const localeRegions: Record<Locale, string[]> = {
    en: ['us', 'in', 'ca', 'uk', 'ae'],
    hi: ['in'],
    fr: ['ca'],
};

export default getRequestConfig(async ({ locale }) => {
    // Validate that the incoming locale is valid
    if (!locales.includes(locale as Locale)) {
        // Return default locale messages if invalid
        return {
            messages: (await import(`../messages/en.json`)).default
        };
    }

    return {
        messages: (await import(`../messages/${locale}.json`)).default
    };
});
