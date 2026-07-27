import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Pin the workspace root so parent lockfiles cannot make Turbopack scan
  // unrelated projects and exhaust system memory.
  turbopack: {
    root: __dirname,
  },
  experimental: {
    proxyClientMaxBodySize: "64mb",
  },
  async rewrites() {
    const apiUrl = process.env.API_URL ?? "http://127.0.0.1:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
