/** @type {import('next').NextConfig} */
const nextConfig = {
  // Strict mode for highlighting potential problems
  reactStrictMode: true,

  // Performance optimizations
  poweredByHeader: false,
  compress: true,

  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
  },

  // Experimental features for better performance
  experimental: {
    optimizePackageImports: ['@/components/ui'],
  },
};

export default nextConfig;
