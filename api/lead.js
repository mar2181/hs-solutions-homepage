// POST /api/lead -- the quote form on every page of hs-solutions.dev.
//
// It emails the lead to LEAD_INBOX through Resend and never pretends:
//   - no RESEND_API_KEY or LEAD_INBOX  -> 503, and the page tells the visitor to call
//   - Resend refuses or times out      -> 502, same
//   - only a Resend response carrying an email id counts as sent
// A filled honeypot or a form submitted faster than a person can type is answered as if it
// worked (so a bot learns nothing) and sends nothing.
//
// Without JavaScript the browser posts form-encoded and follows a 303 back to the page it came
// from, landing on #quote-sent or #quote-failed. The page name is checked against a fixed list,
// so this can never redirect anywhere else.
"use strict";

const PHONE_DISPLAY = "(956) 393-7828";
const PAGES = new Set([
  "index.html", "websites-landing-pages.html", "local-seo.html", "online-marketing.html",
  "content-creative.html", "ai-agents.html", "ai-webmaster.html", "automation.html",
  "webapps-apps.html", "pos-inventory.html", "real-estate.html",
]);
const SERVICES = [
  "Not sure yet", "Website or landing page", "Local SEO and Google Business Profile",
  "Online marketing and ads", "Content and creative", "AI agent", "AI Webmaster",
  "Automation", "Web or mobile app", "POS and inventory", "Real estate marketing",
];
const MIN_FILL_MS = 3000;

const MSG = {
  sent: "Thanks. Your message reached us, and we'll reply by phone or email.",
  needName: "Please tell us your name.",
  needContact: "Add a phone number or an email so we can reach you.",
  badEmail: "That email doesn't look right.",
  badPhone: "Please include a full 10-digit phone number.",
  cannotSend: `Our form isn't sending right now. Please call ${PHONE_DISPLAY} and we'll take it from there.`,
  failed: `We couldn't send that. Please call ${PHONE_DISPLAY} and we'll take your details directly.`,
};

function str(v, max) {
  if (Array.isArray(v)) v = v[0];
  if (v === undefined || v === null) return "";
  return String(v).replace(/\r\n?/g, "\n").trim().slice(0, max);
}
function oneLine(s) {
  return s.replace(/[\r\n\t]+/g, " ").replace(/\s{2,}/g, " ").trim();
}

function readBody(req) {
  const b = req.body;
  if (!b) return {};
  if (typeof b === "object" && !Buffer.isBuffer(b)) return b;
  const text = Buffer.isBuffer(b) ? b.toString("utf8") : String(b);
  try { return JSON.parse(text); } catch (_) { /* not JSON */ }
  return Object.fromEntries(new URLSearchParams(text));
}

// Pure: what the visitor sent, cleaned, plus field errors. Exported for the guard.
function validate(raw) {
  const f = {
    name: oneLine(str(raw.name, 80)),
    business: oneLine(str(raw.business, 120)),
    phone: oneLine(str(raw.phone, 30)),
    email: oneLine(str(raw.email, 120)),
    service: oneLine(str(raw.service, 80)),
    message: str(raw.message, 2000),
    page: str(raw.page, 60),
  };
  if (!SERVICES.includes(f.service)) f.service = "Not sure yet";
  if (!PAGES.has(f.page)) f.page = "index.html";
  const errors = {};
  if (!f.name) errors.name = MSG.needName;
  const digits = f.phone.replace(/\D/g, "");
  if (!f.phone && !f.email) errors.contact = MSG.needContact;
  if (f.email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(f.email)) errors.email = MSG.badEmail;
  if (f.phone && digits.length < 10) errors.phone = MSG.badPhone;
  return { fields: f, errors };
}

function looksLikeBot(raw) {
  if (str(raw.website, 200)) return true; // honeypot: hidden from people, filled by scripts
  const t = Number(str(raw.t, 20));
  return Number.isFinite(t) && t > 0 && Date.now() - t < MIN_FILL_MS;
}

function emailText(f) {
  return [
    `New lead from hs-solutions.dev (${f.page})`,
    "",
    `Name:     ${f.name}`,
    `Business: ${f.business || "-"}`,
    `Phone:    ${f.phone || "-"}`,
    `Email:    ${f.email || "-"}`,
    `Needs:    ${f.service}`,
    "",
    f.message || "(no message)",
  ].join("\n");
}

async function sendLead(f, env, fetchImpl) {
  const key = env.RESEND_API_KEY;
  const inbox = (env.LEAD_INBOX || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (!key || !inbox.length) return { ok: false, status: 503, message: MSG.cannotSend, reason: "not configured" };
  const payload = {
    from: env.LEAD_FROM || "HS Solutions <noreply@petbuddyconcierge.com>",
    to: inbox,
    subject: oneLine(`New lead: ${f.service} - ${f.name}`).slice(0, 150),
    text: emailText(f),
  };
  if (f.email) payload.reply_to = f.email;
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 10000);
  try {
    const r = await fetchImpl("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: ctl.signal,
    });
    const j = await r.json().catch(() => ({}));
    if (r.ok && j && j.id) return { ok: true, status: 200, message: MSG.sent, id: j.id };
    return { ok: false, status: 502, message: MSG.failed, reason: `resend ${r.status}` };
  } catch (e) {
    return { ok: false, status: 502, message: MSG.failed, reason: e && e.name === "AbortError" ? "timeout" : "network" };
  } finally {
    clearTimeout(timer);
  }
}

function wantsHtml(req) {
  const ct = String(req.headers["content-type"] || "");
  const accept = String(req.headers.accept || "");
  return ct.includes("application/x-www-form-urlencoded") && accept.includes("text/html");
}

function reply(req, res, status, body, page) {
  if (wantsHtml(req)) {
    const where = page === "index.html" ? "/" : `/${page}`;
    res.statusCode = 303;
    res.setHeader("Location", `${where}#${body.ok ? "quote-sent" : "quote-failed"}`);
    res.end();
    return;
  }
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(body));
}

async function handler(req, res, deps) {
  const env = (deps && deps.env) || process.env;
  const fetchImpl = (deps && deps.fetch) || fetch;
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "POST");
    res.end();
    return;
  }
  const raw = readBody(req);
  const { fields, errors } = validate(raw);
  if (looksLikeBot(raw)) return reply(req, res, 200, { ok: true, message: MSG.sent }, fields.page);
  if (Object.keys(errors).length) {
    const first = errors.name || errors.contact || errors.email || errors.phone;
    return reply(req, res, 400, { ok: false, message: first, errors }, fields.page);
  }
  const out = await sendLead(fields, env, fetchImpl);
  if (!out.ok) console.error(`[lead] not sent: ${out.reason}`);
  return reply(req, res, out.status, { ok: out.ok, message: out.message }, fields.page);
}

module.exports = handler;
module.exports.validate = validate;
module.exports.SERVICES = SERVICES;
module.exports.PAGES = PAGES;
module.exports.MSG = MSG;
