import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  allowedDevOrigins: ['192.168.29.249:3000', '192.168.29.249:3001', '192.168.29.249'],
  experimental: {
    serverActions: {
      allowedOrigins: ['192.168.29.249:3000', '192.168.29.249', 'localhost:3000']
    }
  }
};

export default nextConfig;
