/**
 * Next.js Middleware for Internationalization and Route Protection
 * Combines locale detection with role-based access control
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import createIntlMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n/config';

// Create the intl middleware
const intlMiddleware = createIntlMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'as-needed' // Only add locale prefix for non-default locales
});

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip locale handling for API routes and static files
  if (
    pathname.startsWith('/api/') ||
    pathname.startsWith('/_next/') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // Handle internationalization
  const intlResponse = intlMiddleware(request);

  // Get pathname without locale prefix for route checks
  const pathnameWithoutLocale = pathname.replace(/^\/(en|hi|fr)/, '') || '/';

  const token = request.cookies.get('auth_token')?.value;

  // Define exact public routes
  const exactPublicRoutes = ['/login', '/signup', '/', '/register'];

  // Define public route prefixes (e.g., for marketing pages and CarePrep links)
  const publicRoutePrefixes = [
    '/community', '/features', '/solutions', '/pricing', '/roadmap',
    '/demo', '/roi', '/security', '/changelog', '/guides', '/how-it-works',
    '/integrations', '/partners', '/careprep'
  ];

  // Check if the current pathname is an exact public route or starts with a public prefix
  const isPublicRoute = exactPublicRoutes.includes(pathnameWithoutLocale) ||
    publicRoutePrefixes.some(prefix => pathnameWithoutLocale.startsWith(prefix));

  // Allow public routes
  if (isPublicRoute) {
    return intlResponse;
  }

  // Redirect to login if no token for protected routes
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Decode token to check role
  let userRole = '';
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) throw new Error('Invalid token structure');
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = atob(base64);
    const payload = JSON.parse(jsonPayload);
    userRole = payload.role || '';
  } catch (e) {
    console.error('Error decoding token in middleware:', e);
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('auth_token');
    return response;
  }

  if (!userRole) {
    const loginUrl = new URL('/login', request.url);
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('auth_token');
    return response;
  }

  const isProvider = ['doctor', 'nurse', 'admin', 'super_admin'].includes(userRole);
  const isPatient = userRole === 'patient';

  // Provider route protection
  if (pathnameWithoutLocale.startsWith('/provider') && !isProvider) {
    console.log('❌ Unauthorized access to provider route:', pathname, 'Role:', userRole);
    return NextResponse.redirect(new URL('/patient/dashboard', request.url));
  }

  // Patient route protection
  if (pathnameWithoutLocale.startsWith('/patient') && !isPatient) {
    console.log('❌ Unauthorized access to patient route:', pathname, 'Role:', userRole);
    return NextResponse.redirect(new URL('/provider/dashboard', request.url));
  }

  // Allow admin routes - role checking is done in the admin layout
  if (pathnameWithoutLocale.startsWith('/admin')) {
    return intlResponse;
  }

  return intlResponse;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
