import type { Metadata, Viewport } from "next";
import { Inter, Manrope } from "next/font/google";
import "./globals.css";
import NavShell from "@/components/layout/NavShell";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const manrope = Manrope({ subsets: ["latin"], variable: "--font-manrope" });

export const metadata: Metadata = {
  title: "NCR Property Intelligence | Geospatial ROI Engine",
  description: "Institutional-grade real estate analytics for the National Capital Region. Advanced valuation models, geospatial ROI heatmaps, and predictive risk assessment.",
  openGraph: {
    title: "NCR Property Intelligence | Institutional Grade",
    description: "Geospatial ROI Intelligence & ML-Powered Valuation for NCR Real Estate. Advanced predictive analytics for data-driven asset discovery.",
    type: "website",
    url: "https://ncr-intelligence.vercel.app",
    siteName: "NCR Property Intelligence",
  },
  twitter: {
    card: "summary_large_image",
    title: "NCR Property Intelligence | ROI Engine",
    description: "Advanced valuation models and geospatial ROI tracking for NCR high-growth corridors.",
    creator: "@anixes",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${manrope.variable} dark`} suppressHydrationWarning>
      <body className="bg-background text-on-background font-body min-h-screen antialiased flex flex-col overflow-x-hidden" suppressHydrationWarning>
        <NavShell />
        <main className="flex-grow relative">
          {children}
        </main>
      </body>
    </html>
  );
}
