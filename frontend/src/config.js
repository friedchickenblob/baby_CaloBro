// Backend base URL. Override with VITE_API_URL (e.g. in frontend/.env.local or Vercel env vars).
export const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "");
