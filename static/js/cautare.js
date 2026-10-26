// cautare.js — CĂUTAREA GLOBALĂ din antet (lotul 13, deficiența 681; decizia Costin 25.10.2026, comanda 13.1, verbatim: „Căsuță de căutare
// în antet, mereu vizibilă; scrii o funcție, o declarație sau un nume («diurnă», «tichet», «D112», un salariat) și te duce în fereastra
// potrivită, pentru firma în lucru. Proba: «Decont deplasare / diurnă» nu se găsește azi fără să știi că e în Operațiuni → Personal și
// deconturi.”). DS cap.9 „Căutarea globală”.
//
// Rezultatele vin de la server (`GET /eu/cautare`, `core/cautare.py`): cardurile ferestrei firmei, operațiunile speciale (cu etichetele
// câmpurilor lor), declarațiile și salariații firmei în lucru. Lista apare sub căsuță numai cât omul scrie (nimic nu se deschide singur);
// fiecare rezultat e un buton (DS cap.2a, 674); alegerea (clic / Enter) deschide fereastra potrivită PESTE ce e deschis — ce s-a tastat
// într-o fereastră de dedesubt se păstrează (DS cap.3, `nav` păstrează corpul ferestrei). Operațiunile refuzate rolului nu apar (`permis`).
// Gard: `core/test_lot13_ds_cautare.py` (server) + e2e `frontend_test/e2e/e2e_lot13_ds.py::test_def_681_*`.
import { api, esc, ultimaCerere } from "./api.js?v=e38843b1ec";
import { permis } from "./drepturi.js?v=34d0fb0afd";

const ASTEPTARE_MS = 200;
const TEXT_FARA_FIRMA = "Alege întâi firma în lucru (Firme › Firme existente), apoi caută din nou.";

function _fereastraSus() {
  const f = [...document.querySelectorAll(".fereastra")];
  return f.length ? f[f.length - 1] : null;
}

// elementul `sel` în fereastra de sus, cât apare (ecranele se încarcă după o cerere)
function _asteapta(sel, ms = 20000) {
  return new Promise((rez, resp) => {
    const t0 = Date.now();
    const caut = () => {
      const f = _fereastraSus();
      const el = f && f.querySelector(sel);
      if (el) { rez(el); return; }
      if (Date.now() - t0 > ms) { resp(new Error("nu a apărut " + sel)); return; }
      setTimeout(caut, 80);
    };
    caut();
  });
}

async function _firmaInLucru(nav) {
  const tid = nav.firmaInLucruId && nav.firmaInLucruId();
  if (!tid) return null;
  const r = await api.get("/tenants");
  return ((r && r.tenants) || []).find((t) => Number(t.id) === Number(tid)) || null;
}

// fereastra firmei în lucru: cea de sus, dacă e deja ea (are cardurile firmei), altfel se deschide peste ce e deschis
async function _fereastraFirmei(nav, t) {
  const sus = _fereastraSus();
  if (sus && sus.querySelector('[id^="fa-"]') && String(sus.getAttribute("aria-label") || "").startsWith(String(t.nume || ""))) return;
  const { deschideFirma } = await import("./ecrane/firme.js?v=2b27eebcaf");
  deschideFirma(t, nav);
  await _asteapta('[id^="fa-"]');
}

async function _cardul(nav, t, cheie) {
  await _fereastraFirmei(nav, t);
  const b = await _asteapta("#fa-" + cheie);
  if (b.disabled || b.offsetParent === null) throw new Error("Fereastra „" + (b.textContent || cheie).trim().split("\n")[0]
    + "” nu se poate deschide pentru firma aceasta sau pentru rolul tău.");
  b.click();
}

// alegerea unui rezultat: fereastra potrivită, pe firma în lucru
export async function deschideRezultatul(x, nav) {
  const t = await _firmaInLucru(nav);
  if (!t) throw new Error(TEXT_FARA_FIRMA);
  if (x.fel === "card") { await _cardul(nav, t, x.cheie); return; }
  if (x.fel === "operatiune") {
    await _cardul(nav, t, "operatiuni");
    (await _asteapta('[data-op="' + CSS.escape(x.cheie) + '"]')).click();
    return;
  }
  if (x.fel === "declaratie") {
    await _fereastraFirmei(nav, t);
    const { randeazaDeclaratii } = await import("./ecrane/declaratii.js?v=cb3b13150a");
    nav.deschide("Declarații", (c2) => randeazaDeclaratii(c2, nav, { tenant_id: t.id, nume: t.nume }, { tenant_id: t.id, tip: x.tip }),
      { lat: "tabel" });
    return;
  }
  if (x.fel === "salariat") {
    await _cardul(nav, t, "salariati");
    const nume = String(x.titlu || "");
    const f = await _asteapta("table, .pf-frand, .stat-rand");
    const rand = [...f.closest(".fereastra").querySelectorAll("tr, .pf-frand")].find((r) => (r.innerText || "").includes(nume));
    if (rand) { rand.classList.add("val-evidentiat"); rand.scrollIntoView({ block: "center" }); }
  }
}

// căsuța de căutare, pusă de navigator în bara de sus (înaintea spațiului care împinge butoanele la dreapta)
export function puneCautarea(bara, nav) {
  const loc = document.createElement("div");
  loc.className = "cautare-globala";
  loc.innerHTML = `<input type="search" id="cautare-globala" class="cautare-camp" autocomplete="off" spellcheck="false"
      placeholder="Caută: diurnă, D112, un salariat…" aria-label="Caută o funcție, o declarație sau un salariat"
      role="combobox" aria-expanded="false" aria-controls="cautare-rez" aria-autocomplete="list">
    <div class="cautare-rez" id="cautare-rez" role="listbox" aria-label="Rezultatele căutării" hidden></div>`;
  bara.insertBefore(loc, bara.querySelector(".bara-spatiu"));
  const inp = loc.querySelector("#cautare-globala");
  const lista = loc.querySelector("#cautare-rez");
  let ceas = null, rezultate = [], activ = -1;
  const cerereNoua = ultimaCerere();   // [C103] numai răspunsul ultimei căutări ajunge în listă

  const inchide = () => { lista.hidden = true; inp.setAttribute("aria-expanded", "false"); activ = -1; };
  const marcheaza = () => lista.querySelectorAll("button.cautare-item").forEach((b, i) => {
    b.classList.toggle("buton-activ", i === activ);
    b.setAttribute("aria-selected", i === activ ? "true" : "false");
  });
  const deseneaza = (mesaj) => {
    lista.innerHTML = (mesaj ? `<p class="cautare-mesaj" role="status">${esc(mesaj)}</p>` : "")
      + rezultate.map((x, i) => `<button type="button" class="btn-link cautare-item" role="option" data-i="${i}"
          data-fara-actiune="deschide fereastra găsită; acțiunea o face fereastra"><span class="cautare-titlu">${esc(x.titlu)}</span>
          <span class="cautare-unde">${esc(x.unde || "")}</span></button>`).join("");
    lista.hidden = false;
    inp.setAttribute("aria-expanded", "true");
    activ = -1;
    lista.querySelectorAll("button.cautare-item").forEach((b) => b.addEventListener("click", () => alege(Number(b.dataset.i))));
  };
  const alege = async (i) => {
    const x = rezultate[i];
    if (!x) return;
    try {
      inchide();
      inp.value = "";
      await deschideRezultatul(x, nav);
    } catch (e) {
      rezultate = [];
      deseneaza((e && (e.mesaj || e.message)) || "Fereastra nu s-a putut deschide.");
    }
  };
  const cauta = async (q) => {
    const actuala = cerereNoua();
    const tid = nav.firmaInLucruId && nav.firmaInLucruId();
    let r;
    try {
      r = await api.get("/eu/cautare?q=" + encodeURIComponent(q) + (tid ? "&tenant_id=" + encodeURIComponent(tid) : ""));
    } catch (e) {
      if (!actuala()) return;
      rezultate = [];
      deseneaza((e && e.mesaj) || "Căutarea nu s-a putut face — reîncearcă.");
      return;
    }
    if (!actuala()) return;   // a sosit răspunsul unei căutări mai vechi
    rezultate = ((r && r.rezultate) || []).filter((x) => !x.actiune || permis(x.actiune));
    const deFirma = rezultate.some((x) => x.fel !== "card" && x.fel !== "operatiune") || tid;
    deseneaza(rezultate.length ? (deFirma ? "" : TEXT_FARA_FIRMA) : `Nimic găsit pentru „${q}”.`);
  };
  inp.addEventListener("input", () => {
    clearTimeout(ceas);
    const q = inp.value.trim();
    if (q.length < 2) { cerereNoua(); inchide(); return; }
    ceas = setTimeout(() => cauta(q), ASTEPTARE_MS);
  });
  inp.addEventListener("keydown", (e) => {
    const n = rezultate.length;
    if (e.key === "Escape") { inchide(); inp.blur(); return; }
    if (lista.hidden || !n) return;
    if (e.key === "ArrowDown") { e.preventDefault(); activ = (activ + 1) % n; marcheaza(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); activ = (activ - 1 + n) % n; marcheaza(); }
    else if (e.key === "Enter") { e.preventDefault(); alege(activ < 0 ? 0 : activ); }
  });
  document.addEventListener("pointerdown", (e) => { if (!loc.contains(e.target)) inchide(); }, true);
  return inp;
}
