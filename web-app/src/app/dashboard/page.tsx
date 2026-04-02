import AnalyticalDashboard from "@/components/dashboard/AnalyticalDashboard";
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Intelligence Dashboard | NCR Property Intelligence',
  description: 'High-resolution spatial intelligence and market alpha discovery for NCR Real Estate.',
};

export default function DashboardPage() {
  return <AnalyticalDashboard />;
}
