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

  // Define public route prefixes (e.g., for marketing pages and CarePrep links)
  const publicRoutePrefixes = ['/community', '/features', '/solutions', '/pricing', '/roadmap', '/demo', '/roi', '/security', '/changelog', '/guides', '/how-it-works', '/integrations', '/partners', '/careprep'];

  // Check if the current pathname is an exact public route or starts with a public prefix
  const isPublicRoute = exactPublicRoutes.includes(pathname) ||
    publicRoutePrefixes.some(prefix => pathname.startsWith(prefix));

  // Allow public routes and API auth/careprep routes
  if (isPublicRoute || pathname.startsWith('/api/auth') || pathname.startsWith('/api/careprep')) {
    return NextResponse.next();
  }

  // Redirect to login if no token
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
    // If token is invalid, redirect to login to clear state
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('auth_token');
    return response;
  }

  if (!userRole) {
    // If no role found, treat as unauthenticated
    const loginUrl = new URL('/login', request.url);
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('auth_token');
    return response;
  }

  const isProvider = ['doctor', 'nurse', 'admin', 'super_admin'].includes(userRole);
  const isPatient = userRole === 'patient';

  // Provider route protection
  if (pathname.startsWith('/provider') && !isProvider) {
    console.log('❌ Unauthorized access to provider route:', pathname, 'Role:', userRole);
    return NextResponse.redirect(new URL('/patient/dashboard', request.url));
  }

  // Patient route protection
  if (pathname.startsWith('/patient') && !isPatient) {
    console.log('❌ Unauthorized access to patient route:', pathname, 'Role:', userRole);
    return NextResponse.redirect(new URL('/provider/dashboard', request.url));
  }

  // Allow admin routes - role checking is done in the admin layout
  if (pathname.startsWith('/admin')) {
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
