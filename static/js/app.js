// app.js — punctul de pornire. Login -> navigator cu desktopul rolului.

import { sesiune } from "./sesiune.js";
import { ecranLogin } from "./ecrane/login.js?v=2";
import { creeazaNavigator } from "./navigator.js";
import { desktopCabinet } from "./ecrane/cabinet.js?v=11";
import { desktopAsistent } from "./ecrane/asistent.js";
import { desktopPortal } from "./ecrane/portal.js?v=12";
import { desktopAdmin } from "./ecrane/admin.js"; // [p37_admin_desktop]

const radacina = document.getElementById("app");

function ecranActivare(tok) {  /* activare_fe_v1 */
  radacina.innerHTML = `
    <div class="pagina-login" style="display:flex;align-items:center;justify-content:center;min-height:100dvh">
      <div style="background:#fff;border-radius:12px;box-shadow:0 3px 12px rgba(20,30,45,0.14);padding:28px;width:min(420px,92vw)">
        <h2 style="margin:0 0 6px">Activare cont</h2>
        <p class="ecran-nota" style="margin:0 0 16px">Seteaz\u0103-\u021bi parola pentru portalul iConta.</p>
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
      try { sesiune.iesi(); } catch (_e) { localStorage.clear(); location.reload(); }
    } catch (e) { msg.textContent = e.message; }
  });
}
function randeaza() {
  const _act = (location.hash.match(/#activare=([\w-]+)/) || [])[1];  /* activare_fe_v1 */
  if (_act) { ecranActivare(_act); return; }
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
