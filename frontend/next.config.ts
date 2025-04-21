import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  env: {
    CHAT: process.env.CHAT,
    CLEAR: process.env.CLEAR,
  },
};

export default nextConfig;
