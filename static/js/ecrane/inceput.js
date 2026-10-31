// inceput.js — cardurile de început și prima intrare (deficiențele 319 + 320, comanda Costin 17.10.2026 7.2, verbatim în DECIZII).
//
// 320: „Cardul duce în ecranul real și se bifează singur doar când acțiunea a fost făcută acolo, nu la apăsarea cardului. Cardurile nu se
// pot închide cât timp nu sunt făcute, dar nu blochează lucrul; când toate sunt făcute dispar de tot, iar ghidul de început rămâne în
// butonul de ajutor (?).” + „La prima intrare, fiecare utilizator își pune obligatoriu telefonul, canalul (WhatsApp sau email) și bifele
// de notificări înainte să ajungă în aplicație.”
// Textul și starea fiecărui card vin de la server (`GET /eu/inceput`, `core/uc_inceput.py`): „făcut” e citit din bază, nu ținut aici.
import { api, esc, arataMesaj } from "../api.js?v=7036a2d894";

// [320] butoanele cardurilor: fiecare deschide ecranul REAL (aceleași funcții ca meniul aplicației)
async function deschide(cheie, nav, laSchimbare) {
  if (cheie === "migrare") {
    const { randeazaMigrare } = await import("./migrare.js?v=6d8714b398");
    nav.deschide("Migrare cabinet", (c) => randeazaMigrare(c, nav), { nivel: "cabinet" });
  } else if (cheie === "suport_import") {
    // banda „Suport” de pe pagina principală, apoi fila „Cerere import din altă aplicație”
    const b = document.querySelector('[data-deschide="raport"]');
    if (b) { b.click(); setTimeout(() => { const t = document.querySelector('.rap-tab[data-tab="import"]'); if (t) t.click(); }, 300); }
  } else if (cheie === "setari_spv") {
    const { panouConectareSPV } = await import("./setari.js?v=ae0ddd2b13");
    nav.deschide("Conectare SPV", (c) => panouConectareSPV(c), { nivel: "cabinet" });
  } else if (cheie === "setari_notificari" || cheie === "notificari_portal") {
    const { panouNotificari } = await import("./setari.js?v=ae0ddd2b13");
    nav.deschide("Notificări", (c) => panouNotificari(c, { dupaSalvare: laSchimbare }));
  } else if (cheie === "asistenti") {
    const { randeazaAsistenti } = await import("./asistenti.js?v=56bbbb1bbc");
    nav.deschide("Asistenți", (c) => randeazaAsistenti(c, nav), { nivel: "cabinet" });
  } else if (cheie === "firme") {
    const { randeazaListaFirme } = await import("./firme.js?v=eecc415409");
    nav.deschide("Firmele tale alocate", (c) => randeazaListaFirme(c, nav, null), { nivel: "cabinet" });
  }
}

// un card nu e reper de pagină (<section> cu nume = landmark): în „?” cardurile apar și peste cele de pe pagina principală (axe landmark-unique)
// [deficiența 596, comanda Costin 12.1] „cardurile «Primii pași» au prea mult text (cardul 1 e tăiat)”: pașii și nota (textul aprobat la 319,
// întreg) stau pliați în „Cum se face”, închis la randare — DS cap.6 v2.95, „Lista de pași care trebuie să încapă în fereastră”: instrucțiunile
// lungi ale unui ecran de pași stau într-un `details.dec-xml` cu titlul „Cum se face”. La vedere rămân titlul, „Ce faci aici”,
// rândul „Cardul devine verde când …” și butoanele. Gard: `core/test_lot12_start_inceput.py`, e2e `test_def_596_*`.
export function htmlCard(c, citire = false) {
  return `<article class="inceput-card${c.facut ? " inceput-facut" : ""}" data-card="${esc(c.cheie)}" aria-label="${esc(c.titlu)}">
      <h3 class="inceput-titlu">${c.facut ? '<span class="inceput-bifa" aria-label="făcut">✓</span> ' : ""}${esc(c.titlu)}</h3>
      <p class="inceput-ce">${esc(c.ce_faci)}</p>
      <details class="dec-xml"><summary>Cum se face</summary>
        <ol class="inceput-pasi">${c.pasi.map((p) => `<li>${esc(p)}</li>`).join("")}</ol>
        ${c.nota ? `<p class="inceput-nota">${esc(c.nota)}</p>` : ""}
      </details>
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

// [deficiențele 561 + 596, comanda Costin 12.1] „«Salvează numărul» nu salvează niciun număr, deci clientul nu poate intra în portal;
// pagina nu derulează” + „iese din ecran; motivul lui «NU s-a salvat» e scris mărunt, sub ecran”. Cauza: ecranul stătea direct în
// `#app`, sub `html, body { overflow-y: hidden }` (scroll-lock-ul aplicației, DS cap.22 §7), deci ce trecea sub ecran — „Salvează” de
// la capătul listei, confirmarea / refuzul lui, „Continuă” — nu se mai putea ajunge, iar „Continuă” rămânea blocat. Acum ecranul e o
// FEREASTRĂ, ca orice formular al aplicației (Notificări din Setări cont e același panou, tot într-o fereastră): încape pe ecran
// (`.fereastra`, `max-height` = ecranul), corpul derulează el însuși (`.fereastra-corp`), iar „Continuă în aplicație” și rândul care spune
// ce mai lipsește stau în `.bara-fixa`, lipite de marginea de jos (DS cap.6 v2.92, „Acțiunea principală și mesajul ei se văd mereu”).
// Rândul se reface după ORICE salvare reușită din panou (numărul, alegerile): `iconta:schimbare` (api.js, după fiecare scriere reușită)
// + `dupaSalvare`. E deschisă de aplicație, nu de un clic (`data-deschidere="aplicatie"`, garda 325); nu are „închide”: e obligatorie
// (decizia 320). Gard: `core/test_lot12_start_inceput.py`, e2e `frontend_test/e2e/e2e_lot12_start.py::test_def_561_*`, `::test_def_596_*`.
export function ceMaiLipseste(st) {
  if (st && st.complet) return "Alegerile tale sunt salvate. Apasă „Continuă în aplicație”.";
  if (!st || !st.telefon) return "„Continuă” se deblochează după doi pași: scrie numărul de telefon și apasă „Salvează numărul”; apoi alege ce primești și apasă „Salvează”, la capătul listei.";
  return `Numărul ${st.telefon} e salvat. Mai rămâne un pas: alege ce primești și apasă „Salvează”, la capătul listei; apoi „Continuă” se deblochează.`;
}

export async function ecranPrimaIntrare(radacina, gata) {
  radacina.innerHTML = `<div class="fereastra-overlay" data-deschidere="aplicatie">
      <div class="fereastra" id="prima-intrare" role="dialog" aria-modal="true" aria-labelledby="pi-titlu">
        <div class="fereastra-antet"><span class="fereastra-titlu" id="pi-titlu" role="heading" aria-level="1">Înainte de a începe</span></div>
        <div class="fereastra-corp" tabindex="0">
          <p class="pf-intro">Pune-ți numărul de telefon, alege pe unde te anunțăm (email sau WhatsApp) și ce vrei să primești. O faci o singură dată; le schimbi oricând din Setări cont → Notificări.</p>
          <div id="pi-notificari"></div>
          <div class="bara-fixa">
            <p class="ecran-nota" id="pi-motiv" role="status">${esc(ceMaiLipseste(null))}</p>
            <div class="dec-bara"><button class="buton-primar" id="pi-continua" data-fara-actiune="intră în aplicație: nu scrie nimic" disabled>Continuă în aplicație</button></div>
          </div>
        </div>
      </div>
    </div>`;
  const btn = radacina.querySelector("#pi-continua");
  const motiv = radacina.querySelector("#pi-motiv");
  const verifica = (st) => {
    btn.disabled = !(st && st.complet);
    motiv.textContent = ceMaiLipseste(st);
  };
  // butonul se leagă înaintea cererilor așteptate (panoul Notificări): un clic dat între timp nu se pierde
  btn.addEventListener("click", async () => {
    try { const st = await stareaNotificarilor(); if (st && st.complet) gata(); else verifica(st); } catch { /* butonul rămâne */ }
  });
  // orice salvare reușită din panou (numărul, alegerile) reface rândul de jos: ce s-a salvat și ce mai lipsește
  const laSchimbare = async () => {
    if (!btn.isConnected) { window.removeEventListener("iconta:schimbare", laSchimbare); return; }
    try { verifica(await stareaNotificarilor()); } catch { /* rândul rămâne */ }
  };
  window.addEventListener("iconta:schimbare", laSchimbare);
  const { panouNotificari } = await import("./setari.js?v=ae0ddd2b13");
  await panouNotificari(radacina.querySelector("#pi-notificari"), { dupaSalvare: verifica });
  try { verifica(await stareaNotificarilor()); } catch { /* rândul rămâne cel de la început */ }
}
