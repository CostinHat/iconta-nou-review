// app.js — punctul de pornire. Login -> navigator cu desktopul rolului.

// [handler_global_erori_v1] Design System: nicio tacere la eroare, nici la nivel de aplicatie.
function _bannerEroareGlobala(detaliu) {
  if (document.getElementById("eroare-globala")) return;  // un singur banner o data
  const b = document.createElement("div");
  b.id = "eroare-globala";
  b.style.cssText = "position:fixed;left:0;right:0;bottom:0;z-index:99999;background:#fdf3f3;border-top:2px solid #d98c8c;color:#7a2020;padding:12px 20px;font-size:14px;font-family:'Segoe UI',system-ui,sans-serif;text-align:center;";
  b.textContent = "A ap\u0103rut o eroare nea\u0219teptat\u0103. Reinc\u0103rca\u021bi pagina (Ctrl+F5). Dac\u0103 problema persist\u0103, anun\u021ba\u021bi.";
  document.body.appendChild(b);
  console.error("[eroare_globala]", detaliu);
}
window.addEventListener("error", (e) => _bannerEroareGlobala(e.error || e.message));
window.addEventListener("unhandledrejection", (e) => _bannerEroareGlobala(e.reason));

import { sesiune } from "./sesiune.js";
import { ecranLogin } from "./ecrane/login.js?v=6";
import { creeazaNavigator } from "./navigator.js?v=2";
import { desktopCabinet } from "./ecrane/cabinet.js?v=2";
import { desktopAsistent } from "./ecrane/asistent.js";
import { desktopPortal } from "./ecrane/portal.js?v=11";
import { desktopAdmin } from "./ecrane/admin.js?v=12"; // [p37_admin_desktop]

const radacina = document.getElementById("app");

function ecranActivare(tok) {  /* activare_fe_v1 */
  radacina.innerHTML = `
    <div class="pagina-login" style="display:flex;align-items:center;justify-content:center;min-height:100dvh">
      <div style="background:#fff;border-radius:12px;box-shadow:0 3px 12px rgba(20,30,45,0.14);padding:28px;width:min(420px,92vw)">
        <h2 style="margin:0 0 6px">Activare cont</h2>
        <p class="ecran-nota" style="margin:0 0 16px">Seteaz\u0103-\u021bi parola pentru portalul iConta.eu.</p>
        <div class="camp" style="margin-bottom:12px">
          <label class="camp-eticheta">Parol\u0103 nou\u0103 (minim 8 caractere)</label>
          <input class="camp-input" type="password" id="act-p1">
        </div>
        <div class="camp" style="margin-bottom:16px">
          <label class="camp-eticheta">Repet\u0103 parola</label>
          <input class="camp-input" type="password" id="act-p2">
        </div>
        <p class="ecran-nota" id="act-msg" style="margin:0 0 10px"></p>
        <button class="buton-primar" id="act-btn" style="width:100%">Activeaz\u0103 contul</button>
      </div>
    </div>`;
  const msg = radacina.querySelector("#act-msg");
  radacina.querySelector("#act-btn").addEventListener("click", async () => {
    const p1 = radacina.querySelector("#act-p1").value, p2 = radacina.querySelector("#act-p2").value;
    if (p1.length < 8) { msg.textContent = "Parola trebuie s\u0103 aib\u0103 minim 8 caractere."; return; }
    if (p1 !== p2) { msg.textContent = "Parolele nu coincid."; return; }
    try {
      const r = await fetch("/public/activare", { method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: tok, parola: p1 }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "Eroare");
      location.hash = "";  /* activare_logout_v1: sesiunea veche nu ramane activa */
      try { sesiune.iesi(); } catch (_e) { sessionStorage.clear(); location.reload(); }
    } catch (e) { msg.textContent = e.message; }
  });
}
function ecranResetParola(tok) {  /* [reset_parola_v1] setare parola noua din linkul de resetare (oglinda ecranActivare) */
  radacina.innerHTML = `
    <div class="pagina-login" style="display:flex;align-items:center;justify-content:center;min-height:100dvh">
      <div style="background:#fff;border-radius:12px;box-shadow:0 3px 12px rgba(20,30,45,0.14);padding:28px;width:min(420px,92vw)">
        <h2 style="margin:0 0 6px">Parolă nouă</h2>
        <p class="ecran-nota" style="margin:0 0 16px">Setează o parolă nouă pentru contul tău iConta.eu.</p>
        <div class="camp" style="margin-bottom:12px">
          <label class="camp-eticheta">Parolă nouă (minim 8 caractere)</label>
          <input class="camp-input" type="password" id="rst-p1">
        </div>
        <div class="camp" style="margin-bottom:16px">
          <label class="camp-eticheta">Repetă parola</label>
          <input class="camp-input" type="password" id="rst-p2">
        </div>
        <p class="ecran-nota" id="rst-msg" style="margin:0 0 10px"></p>
        <button class="buton-primar" id="rst-btn" style="width:100%">Setează parola</button>
      </div>
    </div>`;
  const msg = radacina.querySelector("#rst-msg");
  radacina.querySelector("#rst-btn").addEventListener("click", async () => {
    const p1 = radacina.querySelector("#rst-p1").value, p2 = radacina.querySelector("#rst-p2").value;
    if (p1.length < 8) { msg.textContent = "Parola trebuie să aibă minim 8 caractere."; return; }
    if (p1 !== p2) { msg.textContent = "Parolele nu coincid."; return; }
    try {
      const r = await fetch("/public/reset-parola/seteaza", { method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: tok, parola: p1 }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "Eroare");
      location.hash = "";  /* parola schimbata -> login normal cu parola noua */
      try { sesiune.iesi(); } catch (_e) { sessionStorage.clear(); location.reload(); }
    } catch (e) { msg.textContent = e.message; }
  });
}

function randeaza() {
  const _act = (location.hash.match(/#activare=([\w-]+)/) || [])[1];  /* activare_fe_v1 */
  if (_act) { ecranActivare(_act); return; }
  const _rst = (location.hash.match(/#reset=([\w-]+)/) || [])[1];  /* [reset_parola_v1] */
  if (_rst) { ecranResetParola(_rst); return; }
  const _mag = (location.hash.match(/#magic=([\w-]+)/) || [])[1];  /* magic_login_fe_v1 */
  if (_mag) {
    location.hash = "";
    fetch("/public/magic-login", { method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: _mag }) })
      .then((r) => r.json().then((d) => ({ ok: r.ok, d })))
      .then(({ ok, d }) => {
        if (!ok) { alert(d.detail || "Link expirat sau folosit."); randeaza(); return; }
        sesiune.intra(d.token, d.user);
        location.reload();
      })
      .catch(() => { alert("Eroare la logare."); randeaza(); });
    return;
  }
  const _hp = new URLSearchParams(location.hash.slice(1));  /* [F-preview] #acces=<token>&u=<json user> */
  const _acc = _hp.get("acces");
  if (_acc) {
    location.hash = "";
    let _u = { rol: "client" };  /* fallback: fara user -> portal client (nu gratuit) */
    try { const _raw = _hp.get("u"); if (_raw) _u = JSON.parse(_raw); } catch { /* URL trunchiat -> fallback */ }
    sesiune.intraPreview(_acc, _u);  /* user cu nume_tenant/tenant_are_cabinet -> portal client corect, nu gratuit */
  }
  if (!sesiune.esteLogat()) {
    radacina.innerHTML = "";
    ecranLogin(radacina);
    return;
  }

  switch (sesiune.rol()) {
    case "client":
      creeazaNavigator(radacina, desktopPortal);
      break;
    case "angajat":
      creeazaNavigator(radacina, desktopAsistent);
      break;
    case "superadmin": // [p37_admin_desktop]
      creeazaNavigator(radacina, desktopAdmin);
      break;
    default: // admin_firma
      creeazaNavigator(radacina, desktopCabinet);
  }
}

sesiune.laSchimbare(randeaza);
randeaza();
