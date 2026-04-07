import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* 
   * Next.js 16 Turbopack automatically respects tsconfig.json 'paths'.
   * Overriding with manual aliases can sometimes lead to resolution conflicts 
   * in Windows/Linux mixed environments.
   */
};

export default nextConfig;
