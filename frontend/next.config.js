/** @type {import('next').NextConfig} */
const nextConfig = {
  // 'standalone' is for Docker production builds only — remove for local dev
  // output: 'standalone',
  images: {
    remotePatterns: [],
  },
};

module.exports = nextConfig;
