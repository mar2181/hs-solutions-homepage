// Guard for the quote form and api/lead.js. Exit 0 = clean.
//
//   node tools/check_lead.mjs
//
// It EXECUTES the real handler with a fake Resend, because a source scan cannot tell a function
// that reports a failure from one that swallows it. The worst outcome here is a visitor told
// "sent" while nobody got the email, so most checks are about that.
import { createRequire } from "node:module";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const handler = require(join(ROOT, "api", "lead.js"));

let passes = 0;
const fails = [];
const check = (ok, msg) => (ok ? passes++ : fails.push(msg));

function fakeRes() {
  return {
    statusCode: 200, headers: {}, body: "",
    setHeader(k, v) { this.headers[k.toLowerCase()] = v; },
    end(b) { this.body = b || ""; this.done = true; },
    json() { try { return JSON.parse(this.body); } catch { return null; } },
  };
}
function fakeResend(status, body) {
  const calls = [];
  const fn = async (url, init) => {
    calls.push({ url, init, payload: JSON.parse(init.body) });
    if (status === "throw") throw new Error("network down");
    return { ok: status >= 200 && status < 300, status, json: async () => body };
  };
  fn.calls = calls;
  return fn;
}
const ENV = { RESEND_API_KEY: "re_test", LEAD_INBOX: "a@example.com, b@example.com" };
const GOOD = { name: "Ana Lopez", phone: "(956) 555-0101", email: "ana@example.com", service: "Local SEO and Google Business Profile", message: "Need help", page: "local-seo.html", t: String(Date.now() - 60000) };

async function run(body, { env = ENV, resend = fakeResend(200, { id: "em_1" }), method = "POST", headers = {} } = {}) {
  const res = fakeRes();
  await handler({ method, body, headers }, res, { env, fetch: resend });
  return { res, resend, j: res.json() };
}

// 1. the happy path
{
  const { res, resend, j } = await run(GOOD);
  check(res.statusCode === 200 && j?.ok === true, "a valid lead with a Resend id is reported sent");
  check(resend.calls.length === 1, `exactly one email sent (got ${resend.calls.length})`);
  const p = resend.calls[0]?.payload || {};
  check(JSON.stringify(p.to) === JSON.stringify(["a@example.com", "b@example.com"]), `sent to every LEAD_INBOX address (got ${JSON.stringify(p.to)})`);
  check(p.reply_to === "ana@example.com", "reply_to is the visitor's email, so replying reaches them");
  check(/Ana Lopez/.test(p.text) && /\(956\) 555-0101/.test(p.text) && /Need help/.test(p.text), "the email carries name, phone and message");
  check(resend.calls[0]?.init.headers.Authorization === "Bearer re_test", "authenticates with RESEND_API_KEY");
}
// 2. never "sent" without a real send
{
  const noKey = await run(GOOD, { env: { LEAD_INBOX: "a@example.com" } });
  check(noKey.res.statusCode === 503 && noKey.j?.ok === false && noKey.resend.calls.length === 0, "no RESEND_API_KEY -> 503, not ok, nothing sent");
  check(/956\) 393-7828/.test(noKey.j?.message || ""), "the not-configured message gives the phone number");
  const noInbox = await run(GOOD, { env: { RESEND_API_KEY: "re_test" } });
  check(noInbox.res.statusCode === 503 && noInbox.j?.ok === false, "no LEAD_INBOX -> 503, not ok");
  const refused = await run(GOOD, { resend: fakeResend(422, { message: "bad" }) });
  check(refused.res.statusCode === 502 && refused.j?.ok === false, "Resend refusal -> 502, not ok");
  const noId = await run(GOOD, { resend: fakeResend(200, {}) });
  check(noId.j?.ok === false, "a 200 from Resend WITHOUT an email id is not reported sent");
  const down = await run(GOOD, { resend: fakeResend("throw") });
  check(down.res.statusCode === 502 && down.j?.ok === false, "a network error -> 502, not ok");
}
// 3. validation
{
  const cases = [
    [{ ...GOOD, name: "" }, "name"], [{ ...GOOD, phone: "", email: "" }, "contact"],
    [{ ...GOOD, email: "not-an-email" }, "email"], [{ ...GOOD, phone: "12345" }, "phone"],
  ];
  for (const [body, field] of cases) {
    const { res, resend, j } = await run(body);
    check(res.statusCode === 400 && j?.ok === false && j?.errors?.[field] && resend.calls.length === 0, `missing/bad ${field} -> 400 and nothing sent`);
  }
  const phoneOnly = await run({ ...GOOD, email: "" });
  check(phoneOnly.j?.ok === true && !("reply_to" in phoneOnly.resend.calls[0].payload), "phone only is enough, and no reply_to is invented");
  const junk = handler.validate({ ...GOOD, service: "<script>", page: "../../etc" });
  check(junk.fields.service === "Not sure yet" && junk.fields.page === "index.html", "unknown service and page fall back to known values");
  const crlf = await run({ ...GOOD, name: "Ana\r\nBcc: x@evil.com" });
  check(!/[\r\n]/.test(crlf.resend.calls[0]?.payload.subject || "x\n"), "no line break reaches the subject");
}
// 4. bots are answered ok and cost nothing
{
  const hp = await run({ ...GOOD, website: "http://spam" });
  check(hp.j?.ok === true && hp.resend.calls.length === 0, "filled honeypot -> ok, nothing sent");
  const fast = await run({ ...GOOD, t: String(Date.now() - 500) });
  check(fast.j?.ok === true && fast.resend.calls.length === 0, "submitted in under 3s -> ok, nothing sent");
  const noT = await run({ ...GOOD, t: "" });
  check(noT.resend.calls.length === 1, "no timestamp (JavaScript off) is still a real lead");
}
// 5. transport details
{
  const get = await run(GOOD, { method: "GET" });
  check(get.res.statusCode === 405 && get.resend.calls.length === 0, "GET -> 405");
  const form = new URLSearchParams(GOOD).toString();
  const html = await run(form, { headers: { "content-type": "application/x-www-form-urlencoded", accept: "text/html" } });
  check(html.res.statusCode === 303 && html.res.headers.location === "/local-seo.html#quote-sent", `no-JS post -> 303 to the page's #quote-sent (got ${html.res.headers.location})`);
  const htmlFail = await run(form, { env: {}, headers: { "content-type": "application/x-www-form-urlencoded", accept: "text/html" } });
  check(htmlFail.res.headers.location === "/local-seo.html#quote-failed", "no-JS failure lands on #quote-failed");
  const evil = await run(new URLSearchParams({ ...GOOD, page: "//evil.com" }).toString(), { headers: { "content-type": "application/x-www-form-urlencoded", accept: "text/html" } });
  check(evil.res.headers.location === "/#quote-sent", `a forged page cannot redirect off the site (got ${evil.res.headers.location})`);
}
// 6. every page is wired to it, the same way
{
  const pages = readdirSync(ROOT).filter((f) => f.endsWith(".html"));
  check(pages.length === 11, `11 pages on disk (got ${pages.length})`);
  for (const f of pages) {
    const t = readFileSync(join(ROOT, f), "utf8");
    const forms = t.match(/<form\b[^>]*data-lead[^>]*>/g) || [];
    check(forms.length === 1, `${f}: exactly one lead form (got ${forms.length})`);
    check(/action="\/api\/lead"/.test(forms[0] || ""), `${f}: the form posts to /api/lead`);
    check(t.includes(`name="page" value="${f}"`), `${f}: the form names its own page`);
    const sel = (t.match(/<option selected>([^<]*)<\/option>/) || [])[1];
    check(handler.SERVICES.includes((sel || "").replace(/&amp;/g, "&")), `${f}: preselected service "${sel}" is one the API accepts`);
    for (const opt of [...t.matchAll(/<option(?: selected)?>([^<]*)<\/option>/g)]) {
      check(handler.SERVICES.includes(opt[1].replace(/&amp;/g, "&")), `${f}: option "${opt[1]}" is one the API accepts`);
    }
    check(handler.PAGES.has(f), `${f}: the API accepts this page name`);
    check(t.includes('id="quote-sent"') && t.includes('id="quote-failed"'), `${f}: no-JS landing messages exist`);
    check((t.match(/<script src="assets\/site\.js" defer><\/script>/g) || []).length === 1, `${f}: loads assets/site.js once`);
    check(t.includes('name="website"') && /class="hp"/.test(t), `${f}: honeypot present and hidden`);
  }
  const js = readFileSync(join(ROOT, "assets", "site.js"), "utf8");
  check(/j\.ok === true/.test(js), "site.js only reports success on ok === true");
  check(!/\.then\(function \(r\) \{ return r\.ok/.test(js), "site.js does not treat an HTTP status as success");
  check(/catch\(function \(\) \{ say\(FAIL/.test(js), "site.js shows the failure on a network error");
}

for (const m of fails) console.log("FAIL", m);
console.log(`${passes} checks passed, ${fails.length} failed`);
process.exit(fails.length ? 1 : 0);
