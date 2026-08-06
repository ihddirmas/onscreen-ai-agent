/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // pdf-parse / mammoth load native-ish resources at runtime; keep them
    // external to the server bundle so they load normally.
    serverComponentsExternalPackages: ["pdf-parse", "mammoth"],
  },
};

module.exports = nextConfig;
