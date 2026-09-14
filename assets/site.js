/* Shared by every page: the quote form and the contact events.
   A lead is only reported as sent when /api/lead answers { ok: true }. Anything else --
   a 503, a 502, a network error, a non-JSON body -- shows the failure and the phone number. */
(function () {
  var FAIL = "We couldn't send that. Please call (956) 393-7828.";

  function track(name, params) {
    params = params || {};
    params.page = location.pathname;
    window.dataLayer = window.dataLayer || [];
    var ev = { event: name };
    for (var k in params) ev[k] = params[k];
    window.dataLayer.push(ev);
    if (typeof window.gtag === "function") window.gtag("event", name, params);
  }

  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (!a) return;
    var h = a.getAttribute("href") || "";
    if (h.indexOf("tel:") === 0) track("contact_phone");
    else if (h.indexOf("mailto:") === 0) track("contact_email");
  }, true);

  var forms = document.querySelectorAll("form[data-lead]");
  Array.prototype.forEach.call(forms, function (f) {
    var t = f.querySelector('input[name="t"]');
    var status = f.querySelector(".qf-status");
    var btn = f.querySelector('button[type="submit"]');
    function stamp() { if (t) t.value = String(Date.now()); }
    function say(msg, kind) { status.textContent = msg; status.className = "qf-status" + (kind ? " " + kind : ""); }
    stamp();

    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = {};
      Array.prototype.forEach.call(f.elements, function (el) {
        if (el.name) data[el.name] = String(el.value);
      });
      if (!data.phone && !data.email) { say("Add a phone number or an email so we can reach you.", "err"); return; }
      btn.disabled = true;
      say("Sending...", "");
      fetch(f.getAttribute("action"), {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
        .then(function (j) {
          if (j && j.ok === true) {
            say(j.message || "Thanks. Your message reached us.", "ok");
            f.reset();
            stamp();
            track("generate_lead", { service: data.service });
          } else {
            say((j && j.message) || FAIL, "err");
          }
          btn.disabled = false;
        })
        .catch(function () { say(FAIL, "err"); btn.disabled = false; });
    });
  });
})();
