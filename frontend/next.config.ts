import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:9001",
    API_BASE_URL: process.env.API_BASE_URL || "http://127.0.0.1:9001",
  },
  async rewrites() {
    return [];
  },
};

export default nextConfig;
