const origin = process.env.RENDER_ORIGIN?.trim();

if (!origin || !/^https:\/\/[a-z0-9][a-z0-9-]*\.onrender\.com\/?$/i.test(origin)) {
  throw new Error("Set RENDER_ORIGIN to the HTTPS URL of the Render web service.");
}

export const config = {
  framework: null,
  installCommand: "",
  buildCommand: "",
  outputDirectory: "public",
  rewrites: [{
    source: "/:path*",
    destination: `${new URL(origin).origin}/:path*`,
  }],
  headers: [{
    source: "/:path*",
    headers: [{ key: "x-vercel-enable-rewrite-caching", value: "0" }],
  }],
};
