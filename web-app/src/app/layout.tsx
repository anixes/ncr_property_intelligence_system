import type { Metadata, Viewport } from "next";
import { Inter, Manrope } from "next/font/google";
import "./globals.css";
import NavShell from "../components/layout/NavShell";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const manrope = Manrope({ subsets: ["latin"], variable: "--font-manrope" });

export const metadata: Metadata = {
  title: "NCR Property Intelligence | Institutional Grade",
  description: "Curated editorial perspective on National Capital Region real estate.",
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
