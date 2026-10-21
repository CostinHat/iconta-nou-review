// inceput.js — cardurile de început și prima intrare (deficiențele 319 + 320, comanda Costin 17.10.2026 7.2, verbatim în DECIZII).
//
// 320: „Cardul duce în ecranul real și se bifează singur doar când acțiunea a fost făcută acolo, nu la apăsarea cardului. Cardurile nu se
// pot închide cât timp nu sunt făcute, dar nu blochează lucrul; când toate sunt făcute dispar de tot, iar ghidul de început rămâne în
// butonul de ajutor (?).” + „La prima intrare, fiecare utilizator își pune obligatoriu telefonul, canalul (WhatsApp sau email) și bifele
// de notificări înainte să ajungă în aplicație.”
// Textul și starea fiecărui card vin de la server (`GET /eu/inceput`, `core/uc_inceput.py`): „făcut” e citit din bază, nu ținut aici.
import { api, esc, arataMesaj } from "../api.js?v=ff30ebaf3f";

// [320] butoanele cardurilor: fiecare deschide ecranul REAL (aceleași funcții ca meniul aplicației)
async function deschide(cheie, nav, laSchimbare) {
  if (cheie === "migrare") {
    const { randeazaMigrare } = await import("./migrare.js?v=9cc61e19f2");
    nav.deschide("Migrare cabinet", (c) => randeazaMigrare(c, nav), { nivel: "cabinet" });
  } else if (cheie === "suport_import") {
    // banda „Suport” de pe pagina principală, apoi fila „Cerere import din altă aplicație”
    const b = document.querySelector('[data-deschide="raport"]');
    if (b) { b.click(); setTimeout(() => { const t = document.querySelector('.rap-tab[data-tab="import"]'); if (t) t.click(); }, 300); }
  } else if (cheie === "setari_spv") {
    const { panouConectareSPV } = await import("./setari.js?v=6a36388d13");
    nav.deschide("Conectare SPV", (c) => panouConectareSPV(c), { nivel: "cabinet" });
  } else if (cheie === "setari_notificari" || cheie === "notificari_portal") {
    const { panouNotificari } = await import("./setari.js?v=6a36388d13");
    nav.deschide("Notificări", (c) => panouNotificari(c, { dupaSalvare: laSchimbare }));
  } else if (cheie === "asistenti") {
    const { randeazaAsistenti } = await import("./asistenti.js?v=e6e5062e27");
    nav.deschide("Asistenți", (c) => randeazaAsistenti(c, nav), { nivel: "cabinet" });
  } else if (cheie === "firme") {
    const { randeazaListaFirme } = await import("./firme.js?v=6855dfc0c2");
    nav.deschide("Firmele tale alocate", (c) => randeazaListaFirme(c, nav, null), { nivel: "cabinet" });
  }
}

// un card nu e reper de pagină (<section> cu nume = landmark): în „?” cardurile apar și peste cele de pe pagina principală (axe landmark-unique)
export function htmlCard(c, citire = false) {
  return `<article class="inceput-card${c.facut ? " inceput-facut" : ""}" data-card="${esc(c.cheie)}" aria-label="${esc(c.titlu)}">
      <h3 class="inceput-titlu">${c.facut ? '<span class="inceput-bifa" aria-label="făcut">✓</span> ' : ""}${esc(c.titlu)}</h3>
      <p class="inceput-ce">${esc(c.ce_faci)}</p>
      <ol class="inceput-pasi">${c.pasi.map((p) => `<li>${esc(p)}</li>`).join("")}</ol>
      ${c.nota ? `<p class="inceput-nota">${esc(c.nota)}</p>` : ""}
      <p class="inceput-verde">${esc(c.verde)}</p>
      ${citire ? "" : `<div class="inceput-butoane">${c.butoane.map((b, i) => {
        const cls = i === 0 ? "buton-primar" : "buton-secundar";   // primul buton al cardului e acțiunea lui
        // „Lucrez singur” cheamă o rută (nu deschide un ecran): `data-actiune` o numește, ca drepturile s-o poată ascunde
        return `<button type="button" class="${cls}" data-inceput="${esc(b.deschide)}"${b.deschide === "lucrez_singur"
          ? ` data-actiune="POST /eu/inceput/lucrez-singur"` : ""}>${esc(b.eticheta)}</button>`;
      }).join("")}</div>`}
    </article>`;
}

// cele două citiri ale stării, fiecare dintr-un singur loc: cardurile (`GET /eu/inceput`) și dacă prima intrare e completă
const stareaCardurilor = () => api.get("/eu/inceput");
const stareaNotificarilor = () => api.get("/eu/notificari");

// Cardurile pe pagina principală: nimic când toate sunt făcute; altfel toate (și cele făcute, verzi), fără „închide”.
export async function cardurileDeInceput(zona, nav) {
  if (!zona) return;
  let r;
  try { r = await stareaCardurilor(); } catch { zona.innerHTML = ""; return; }
  if (!zona.isConnected) return;
  if (!r || r.toate_facute || !(r.carduri || []).length) { zona.innerHTML = ""; zona.hidden = true; return; }
  zona.hidden = false;
  zona.innerHTML = `<h2 class="inceput-cap">Primii pași</h2>
    <p class="ecran-nota">Fiecare card te duce în ecranul lui și se bifează singur când ai făcut pasul acolo. Când sunt toate făcute, cardurile dispar; le regăsești oricând la „?”, sus.</p>
    <div class="inceput-grila">${r.carduri.map((c) => htmlCard(c)).join("")}</div>
    <div id="inceput-msg"></div>`;
  const reia = () => cardurileDeInceput(zona, nav);
  zona.querySelectorAll("[data-inceput]").forEach((b) => b.addEventListener("click", async () => {
    if (b.dataset.inceput === "lucrez_singur") {
      try { await api.post("/eu/inceput/lucrez-singur", {}); reia(); }
      catch (e) { arataMesaj(zona.querySelector("#inceput-msg"), (e && e.mesaj) || "Alegerea nu s-a putut salva.", "eroare"); }
      return;
    }
    deschide(b.dataset.inceput, nav, reia);
  }));
  // se bifează singure: după orice scriere reușită (ecranul real a făcut pasul) cardurile se recitesc
  if (!zona.__laSchimbare) {
    zona.__laSchimbare = () => { if (!zona.isConnected) { window.removeEventListener("iconta:schimbare", zona.__laSchimbare); return; } reia(); };
    window.addEventListener("iconta:schimbare", zona.__laSchimbare);
  }
}

// Ghidul de început, în „?”: aceleași carduri, doar de citit, cu starea lor.
export async function ghidulDeInceput(zona) {
  if (!zona) return;
  try {
    const r = await stareaCardurilor();
    zona.innerHTML = (r.carduri || []).length ? `<h3 class="pf-subtitlu">Primii pași</h3><div class="inceput-grila">${r.carduri.map((c) => htmlCard(c, true)).join("")}</div>` : "";
  } catch { zona.innerHTML = ""; }
}

// [320] prima intrare: telefonul, canalul și bifele, înainte de aplicație
export async function primaIntrareDeFacut() {
  try { const st = await stareaNotificarilor(); return st && st.complet === false; } catch { return false; }
}

export async function ecranPrimaIntrare(radacina, gata) {
  radacina.innerHTML = `<main class="prima-intrare" id="prima-intrare">
      <h1 class="cab-salut-nume">Înainte de a începe</h1>
      <p class="pf-intro">Pune-ți numărul de telefon, alege pe unde te anunțăm (email sau WhatsApp) și ce vrei să primești. O faci o singură dată; le schimbi oricând din Setări cont → Notificări.</p>
      <div id="pi-notificari"></div>
      <p style="margin-top:14px"><button class="buton-primar" id="pi-continua" disabled>Continuă în aplicație</button></p>
      <div id="pi-motiv" class="ecran-nota">„Continuă” se deblochează după ce salvezi numărul de telefon și alegerile de mai sus.</div>
    </main>`;
  const btn = radacina.querySelector("#pi-continua");
  const verifica = (st) => {
    const ok = !!(st && st.complet);
    btn.disabled = !ok;
    radacina.querySelector("#pi-motiv").textContent = ok ? "" : "„Continuă” se deblochează după ce salvezi numărul de telefon și alegerile de mai sus.";
  };
  // butonul se leagă înaintea cererilor așteptate (panoul Notificări): un clic dat între timp nu se pierde
  btn.addEventListener("click", async () => {
    try { const st = await stareaNotificarilor(); if (st && st.complet) gata(); else verifica(st); } catch { /* butonul rămâne */ }
  });
  const { panouNotificari } = await import("./setari.js?v=6a36388d13");
  await panouNotificari(radacina.querySelector("#pi-notificari"), { dupaSalvare: verifica });
}
