// The lock on every guest page. POST /entrar checks a password against data/access.js (keyed hashes, never the
// passwords), then sets a signed cookie. /g/<guest>/ opens with that guest's cookie or the owner's.
// COOKIE_SECRET lives in Vercel's environment variables, never in this repo.
import ACCESS from "./data/access.js";

export const config = { matcher: ["/g/:path*", "/entrar", "/entrar/"] };

const enc = new TextEncoder();
// Same as tools/set_password.py: lower case, no accents, no spaces.
export const norm = (p) => String(p || "").trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/\s+/g, "");

export async function sign(msg, secret = process.env.COOKIE_SECRET) {
  if (!secret) throw new Error("COOKIE_SECRET is not set");
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(msg));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function same(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
const cookieName = (who) => `gal_${who.replace(/[^a-z0-9]/g, "_")}`;
function cookie(req, name) {
  const m = (req.headers.get("cookie") || "").match(new RegExp(`(?:^|;\\s*)${name}=([a-f0-9]{64})`));
  return m ? m[1] : null;
}
const go = (url) => new Response(null, { status: 303, headers: { Location: url, "Cache-Control": "no-store" } });
const pass = () => new Response(null, { headers: { "x-middleware-next": "1", "Cache-Control": "private, no-store" } });

export function makeMiddleware(access) {
  const has = async (req, who) => same(cookie(req, cookieName(who)), await sign(`ok:${who}`));
  return async function middleware(req) {
    const url = new URL(req.url);
    const path = url.pathname;
    if (path.startsWith("/entrar")) {
      if (req.method !== "POST") return new Response(null, { headers: { "x-middleware-next": "1" } });
      const form = await req.formData();
      const page = String(form.get("page") || "");
      const pw = norm(form.get("password"));
      if (!(page in access) || page === "owner") return go("/");
      let who = null;
      if (same(await sign(`pw:${page}:${pw}`), access[page])) who = page;
      else if (access.owner && same(await sign(`pw:owner:${pw}`), access.owner)) who = "owner";
      if (!who) return go(`/entrar/?page=${encodeURIComponent(page)}&e=1`);
      const res = go(`/g/${page}/`);
      res.headers.append("Set-Cookie", `${cookieName(who)}=${await sign(`ok:${who}`)}; Path=/; Max-Age=31536000; HttpOnly; Secure; SameSite=Lax`);
      return res;
    }
    const guest = path.split("/")[2] || "";
    if (guest && guest in access && guest !== "owner" && ((await has(req, guest)) || (await has(req, "owner")))) return pass();
    return go(guest && guest in access ? `/entrar/?page=${encodeURIComponent(guest)}` : "/");
  };
}

export default makeMiddleware(ACCESS);
