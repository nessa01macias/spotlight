/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow Mapbox GL images
  images: {
    domains: ['api.mapbox.com'],
  },
};

export default nextConfig;
