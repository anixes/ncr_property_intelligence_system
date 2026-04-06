import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // @ts-ignore
  allowedDevOrigins: ['192.168.29.249', 'localhost:3000'],
  experimental: {
    serverActions: {
      allowedOrigins: ['192.168.29.249:3000', 'localhost:3000']
    }
  }
};

export default nextConfig;
