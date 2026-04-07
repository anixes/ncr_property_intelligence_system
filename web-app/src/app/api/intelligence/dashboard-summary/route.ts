import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const city = searchParams.get('city');

  try {
    const response = await fetch(`${BACKEND_URL}/intelligence/dashboard-summary?city=${encodeURIComponent(city || 'Gurgaon')}`);
    if (!response.ok) return NextResponse.json({ detail: 'Dashboard summary failed' }, { status: response.status });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ detail: 'Internal Server Error' }, { status: 500 });
  }
}
