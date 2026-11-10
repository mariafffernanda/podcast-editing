import { test } from "node:test";
import assert from "node:assert/strict";
process.env.COOKIE_SECRET = "test-secret-only-for-tests";
const { makeMiddleware, sign, norm } = await import("./middleware.js");

const access = { "alex-rivera": await sign(`pw:alex-rivera:${norm("Café Lunes")}`), owner: await sign(`pw:owner:${norm("host pass")}`) };
const mw = makeMiddleware(access);
const post = (page, password) => {
  const f = new FormData(); f.set("page", page); f.set("password", password);
  return new Request("https://x.test/entrar/", { method: "POST", body: f });
};

test("right password, any accents or capitals, opens the page with a cookie", async () => {
  const r = await mw(post("alex-rivera", "cafe LUNES"));
  assert.equal(r.status, 303);
  assert.equal(r.headers.get("location"), "/g/alex-rivera/");
  const c = r.headers.get("set-cookie");
  assert.match(c, /gal_alex_rivera=[a-f0-9]{64}; Path=\/; Max-Age=31536000; HttpOnly; Secure; SameSite=Lax/);
  const page = await mw(new Request("https://x.test/g/alex-rivera/", { headers: { cookie: c.split(";")[0] } }));
  assert.equal(page.headers.get("x-middleware-next"), "1");
});

test("wrong password goes back with an error", async () => {
  const r = await mw(post("alex-rivera", "nope"));
  assert.equal(r.headers.get("location"), "/entrar/?page=alex-rivera&e=1");
  assert.equal(r.headers.get("set-cookie"), null);
});

test("no cookie: the page sends you to the password form", async () => {
  const r = await mw(new Request("https://x.test/g/alex-rivera/"));
  assert.equal(r.headers.get("location"), "/entrar/?page=alex-rivera");
});

test("owner password opens any guest page", async () => {
  const r = await mw(post("alex-rivera", "Host Pass"));
  const c = r.headers.get("set-cookie").split(";")[0];
  assert.match(c, /^gal_owner=/);
  const page = await mw(new Request("https://x.test/g/alex-rivera/", { headers: { cookie: c } }));
  assert.equal(page.headers.get("x-middleware-next"), "1");
});

test("a forged cookie does not open the page", async () => {
  const r = await mw(new Request("https://x.test/g/alex-rivera/", { headers: { cookie: "gal_alex_rivera=" + "a".repeat(64) } }));
  assert.equal(r.status, 303);
});

test("unknown pages and the owner slug go home", async () => {
  assert.equal((await mw(post("nobody", "x"))).headers.get("location"), "/");
  assert.equal((await mw(post("owner", "host pass"))).headers.get("location"), "/");
});
