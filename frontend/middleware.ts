/**
 * Next.js Middleware for Route Protection
 * Enforces role-based access control
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('auth_token')?.value;

  // Define exact public routes
  const exactPublicRoutes = ['/login', '/signup', '/'];

  // Define public route prefixes (e.g., for marketing pages)
  const publicRoutePrefixes = ['/community', '/features', '/solutions', '/pricing', '/roadmap', '/demo', '/roi', '/security', '/changelog', '/guides', '/how-it-works', '/integrations', '/partners'];

  // Check if the current pathname is an exact public route or starts with a public prefix
  const isPublicRoute = exactPublicRoutes.includes(pathname) ||
                        publicRoutePrefixes.some(prefix => pathname.startsWith(prefix));

  // Allow public routes and API auth routes
  if (isPublicRoute || pathname.startsWith('/api/auth')) {
    return NextResponse.next();
  }

  // Redirect to login if no token
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Simple role detection from token (in production, decode JWT)
  const isProvider = token.includes('provider');
  const isPatient = token.includes('patient');

  // Provider route protection
  if (pathname.startsWith('/provider') && !isProvider) {
    console.log('❌ Patient trying to access provider route:', pathname);
    return NextResponse.redirect(new URL('/patient/dashboard', request.url));
  }

  // Patient route protection
  if (pathname.startsWith('/patient') && !isPatient) {
    console.log('❌ Provider trying to access patient route:', pathname);
    return NextResponse.redirect(new URL('/provider/dashboard', request.url));
  }

  // Allow SaaS dashboard routes (/dashboard/*) for all authenticated users
  // The SaaS dashboard is the main admin/analytics dashboard
  if (pathname.startsWith('/dashboard')) {
    return NextResponse.next();
  }

  return NextResponse.next();
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
