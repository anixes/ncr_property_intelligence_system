import type { Metadata } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";
import "leaflet/dist/leaflet.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    template: "%s | NCR Property Intelligence",
    default: "NCR Property Intelligence | Institutional Real Estate Data",
  },
  description: "Advanced AI-driven property valuation and discovery for the NCR region. Analyze 43,000+ verified listings with professional accuracy.",
  metadataBase: new URL("http://localhost:3000"),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_IE",
    url: "http://localhost:3000",
    siteName: "NCR Property Intelligence",
    images: [{
      url: "/og-main.png",
      width: 1200,
      height: 630,
      alt: "NCR Property Intelligence System",
    }],
  },
  twitter: {
    card: "summary_large_image",
    title: "NCR Property Intelligence",
    description: "Institutional Real Estate Data for NCR.",
    images: ["/og-main.png"],
  },
  icons: {
    icon: "/favicon.ico",
  },
};

import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col bg-background text-foreground`}>
        {/* We keep Navbar and Footer for other pages, but the background is now forced to dark void */}
        <Navbar />
        <main className="flex-grow flex flex-col">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}

