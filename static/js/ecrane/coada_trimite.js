// coada_trimite.js — trimiterea unei declarații în coada de validare, din ORICE ecran (Declarații, Bilanț).
//
// [comanda Costin 07.10.2026] UN singur drum, ca ecranele să nu poată diverge:
//  - C3: „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului. O eroare DUK oprește.”
//    Serverul răspunde `ATENTIONARI_NECONFIRMATE` -> aici se arată atenționările și se cere confirmarea (retrimisă ca
//    `motiv_trecere`, păstrată cu numele omului); `ERORI_DUK` -> se arată, fără portiță.
//  - C1: refuzul spune motivul REAL venit de la server, nu o presupunere („Poate există deja o declarație…” apărea și la o eroare 500).
//  - C11: bilanțul intră în coadă pe același drum ca orice declarație.
import { api, esc, arataMesaj, aduInVedere, TEXT_NOTA_INTERNA } from "../api.js?v=4364ee71f3";
import { butonSpreEcran } from "./ecran_destinatie.js?v=5152ec2b0a";   // [lotul 11, 445] refuzul care trimite la ecranul unde se repară

// [deficiența 222, comanda Costin 10.10.2026] confirmarea intrării în coadă e ACEEAȘI casetă din orice ecran (Declarații, Bilanț) —
// nu un rând de text: bifa, „Trimisă în coada de validare”, declarația și perioada. `cine` = ce urmează („a fost trimisă seniorului …”).
// [deficiența 287] titlul urmează pasul real: „în coada de validare” numai cu validarea în doi efectivă; altfel „în coadă” (gata de depunere)
export function casetaTrimisa(tip, perioada, cine, titlu = "Trimisă în coada de validare") {
  return `<div class="dec-gata">
      <div class="dec-gata-bif">✓</div>
      <div class="dec-gata-titlu">${esc(titlu)}</div>
      <div class="dec-gata-sub"><b>${esc(tip)}</b> · ${esc(perioada)} ${esc(cine)}</div>
    </div>`;
}

// [deficiența 313, comanda Costin 17.10.2026 7.2] „butonul se numește «Trimite în coadă» și pentru cine depune direct”: numele urmează
// pasul real — aceeași regulă ca `uc_coada.pas_urmator` (validarea în doi efectivă -> la validare; altfel cine are «Poate depune» o depune
// el, din „De depus”; altfel o depune un coleg). Eticheta se ține pe buton (`data-eticheta`), ca ecranul s-o pună la loc după „Se trimite…”.
export const ETICHETE_TRIMITERE = { validare: "Trimite la validare →", depunere: "Pune în „De depus” →", altcineva: "Trimite spre depunere →" };
export async function etichetaTrimitere(btn) {
  if (!btn) return;
  try {
    const [po, perm] = await Promise.all([api.get("/eu/patru-ochi"), api.get("/eu/permisiuni")]);
    const e = (po && po.efectiv) ? ETICHETE_TRIMITERE.validare : (perm && perm.poate_depune) ? ETICHETE_TRIMITERE.depunere
      : ETICHETE_TRIMITERE.altcineva;
    btn.dataset.eticheta = e;
    if (!btn.disabled) btn.textContent = e;
  } catch { /* eticheta veche rămâne: trimiterea funcționează la fel */ }
}

// [lotul 13, plasa 436 / 284 / 299 — clasa 515] Refuzul de lângă „Trimite în coadă” îl spune caseta „NU s-a salvat.” (`api.refuzSalvare`),
// iar zona lui se ascunde cât stă caseta — același text, o dată. Butoanele refuzului (notele de deschis, „Deschide declarația existentă” /
// „Înlocuiește”, ecranul unde se repară) nu pot sta în zona ascunsă: stau imediat după ea, într-un rând al lor, vizibil; trimiterea
// următoare îl scoate.
export function actiuniRefuz(zona) {
  let a = zona.nextElementSibling;
  if (!a || !a.classList.contains("coada-actiuni-refuz")) {
    a = document.createElement("div");
    a.className = "coada-actiuni-refuz";
    zona.insertAdjacentElement("afterend", a);
  }
  return a;
}
export function scoateActiuniRefuz(zona) {
  const a = zona && zona.nextElementSibling;
  if (a && a.classList.contains("coada-actiuni-refuz")) a.remove();
}

export async function trimiteInCoada(zona, body, laSucces, confirmare) {
  scoateActiuniRefuz(zona);
  const corp = Object.assign({}, body);
  if (confirmare) corp.motiv_trecere = confirmare;
  try {
    const r = await api.post("/coada", corp);
    laSucces(r);
    // [08.10.2026, decizia Costin §6 pct.7 — R36] ciornele perioadei nu opresc coada: avertismentul porții se arată după intrare
    // (ecranul care se redesenează la succes îl arată el, din `r`; aici numai dacă zona a rămas pe ecran)
    if (zona.isConnected && r && (r.avertismente_poarta || []).length) {
      // [lotul 11, 436 afișare] lângă butoanele notelor, avertismentul le numără, nu le enumeră (`avertismente_poarta_langa_note`)
      const cuNote = (r.surse_note || []).length > 0;
      arataMesaj(zona, mesajLangaNote(cuNote, r.avertismente_poarta_langa_note, r.avertismente_poarta).join(" "), "avert");
      if (cuNote) legaturiNote(zona, body.tenant_id, r.surse_note);
    }
    return r;
  } catch (e) {
    const det = (e && e.detaliu && typeof e.detaliu === "object") ? e.detaliu : {};
    if (det.cod === "ATENTIONARI_NECONFIRMATE") {
      zona.innerHTML = `<div class="caseta-atentie"><div class="ca-mesaj"><span class="pe-randuri">${esc(det.mesaj || "")}</span>
          <pre class="dec-atentionari">${esc(det.erori || "")}</pre>
          <label class="camp"><span class="camp-eticheta">Confirmarea ta (se păstrează cu numele tău) *</span>
          <textarea id="coada-confirmare" class="camp-input" rows="3" aria-label="Confirmarea atenționărilor"></textarea></label>
          <button class="buton-primar" id="coada-confirma" data-actiune="POST /coada">Confirm și trimit în coadă</button></div></div>`;
      zona.querySelector("#coada-confirma").addEventListener("click", () => {
        const t = (zona.querySelector("#coada-confirmare").value || "").trim();
        if (!t) { arataMesaj(zona.querySelector(".ca-mesaj"), "Scrie confirmarea: de ce declarația e corectă așa.", "eroare"); return; }
        trimiteInCoada(zona, body, laSucces, t);
      });
      aduInVedere(zona);
      return null;
    }
    if (det.cod === "DEJA_IN_COADA") {
      // [deficiența 299, comanda Costin 17.10.2026 7.2] refuzul spune perioada declarată, cine a pregătit-o și dă drumul: deschide
      // declarația existentă sau înlocuiește-o cu cea generată acum; mesajul rămâne pe ecran până la alegere
      arataMesaj(zona, det.mesaj, "eroare");
      if (det.coada_id) {
        const b = document.createElement("div");
        b.className = "coada-deja";
        b.innerHTML = `<button type="button" class="buton-secundar" id="coada-deja-deschide">Deschide declarația existentă</button>
          <button type="button" class="buton-primar" id="coada-deja-inlocuieste" data-actiune="POST /coada">Înlocuiește</button>`;
        actiuniRefuz(zona).appendChild(b);
        b.querySelector("#coada-deja-deschide").addEventListener("click", () => deschideInCoada(det.coada_id, true));
        b.querySelector("#coada-deja-inlocuieste").addEventListener("click", () =>
          trimiteInCoada(zona, Object.assign({}, body, { inlocuieste: det.coada_id }), laSucces, confirmare));
      }
      return null;
    }
    // [lotul 11, 436 afișare — „paragraful repetă notele pe care le arată butoanele”] refuzul cu note numite (porțile TVA / D406, notele
    // nevalidate ale declarației din evidență) se arată cu fraza care le NUMĂRĂ (`mesaj_langa_note`); butoanele „Deschide nota …” le numesc
    const cuNote = (det.note || []).length > 0;
    const text = mesajLangaNote(cuNote, det.mesaj_langa_note, (typeof (e && e.mesaj) === "string" && e.mesaj) || det.mesaj)
      || "Nu s-a putut trimite în coadă.";
    arataMesaj(zona, text + (det.erori ? " — " + det.erori : ""), "eroare");
    if (cuNote) legaturiNote(actiuniRefuz(zona), body.tenant_id, det.note);
    // [lotul 11, 445] refuzul generatorului numește ecranul unde se repară (`RefuzGenerare.detaliu`, ex. Date firmă): butonul spre el, cu
    // întoarcerea la declarație (mecanismul unic `butonSpreEcran` -> `nav.dinRefuz`); ca declaratii.js la generare
    if (det.ecran && window._navGlobal) butonSpreEcran(actiuniRefuz(zona), det.ecran, window._navGlobal, body.tenant_id,
      { clasa: "buton-secundar", camp: det.camp_ecran || null });
    return null;
  }
}

// [deficiența 499, lotul 12: „mesajul de respingere se termină cu punct dublu”] motivul scris de om (respingerea unei note, a unui
// NIR, a statului de plată) pus într-o propoziție care se încheie: punctul se adaugă numai dacă omul nu și-a încheiat el fraza
// („lipsește factura.” rămâne așa, nu „lipsește factura..”; nici „?.”). O singură definiție pentru toate ecranele care arată motivul
// urmat de altă propoziție — garda `core/test_lot12_coada_motiv_fraza.py` refuză un motiv interpolat urmat direct de punct.
export function motivInFraza(motiv, gol = "fără motiv") {
  const t = String(motiv == null ? "" : motiv).trim() || gol;
  return /[.!?…]$/.test(t) ? t : t + ".";
}

// [lotul 11, 436 afișare] textul de lângă butoanele notelor: varianta fără lista lor, când serverul o dă (`mesaj_langa_note`,
// `avertismente_poarta_langa_note`); altfel textul întreg. Fără butoane (`cuNote` fals), textul întreg — el numește notele.
export function mesajLangaNote(cuNote, langa, intreg) {
  const areLanga = Array.isArray(langa) ? langa.length > 0 : !!langa;
  return cuNote && areLanga ? langa : intreg;
}

// [deficiența 284] refuzul porții TVA numește notele nevalidate care explică diferența: fiecare are butonul ei spre Registrul jurnal, în
// luna notei, cu nota evidențiată (același drum ca legătura „jurnal:” din notificări). Ecranul declarației rămâne dedesubt.
export async function deschideInCoada(coadaId, dinRefuz = false) {
  if (!window._navGlobal) return;
  const { randeazaValidat } = await import("./validat.js?v=766c35b7f9");
  // [lotul 11, 445] deschisă dintr-un refuz („Deschide declarația existentă”): declarația de dedesubt se păstrează, X / „← Înapoi” întorc la ea
  if (dinRefuz && window._navGlobal.dinRefuz) window._navGlobal.dinRefuz();
  window._navGlobal.deschide("Coada de validare și depunere", (corp, nn) => randeazaValidat(corp, nn, { evidentiaza: coadaId }), { nivel: "cabinet" });
}

export function legaturiNote(zona, tenantId, note) {
  const lista = document.createElement("div");
  lista.className = "coada-note-refuz";
  // [deficiența 329, 18.10.2026] eticheta notei începe deja cu „nota” („nota din 17.10.2026 — F1A6, …”): „Deschide nota nota …”. Cuvântul
  // „nota” se pune o dată, oricum ar veni eticheta.
  lista.innerHTML = note.map((n, i) => `<button type="button" class="buton-secundar" data-nota="${i}">Deschide nota ${esc(String(n.eticheta || "").replace(/^nota\s+/i, ""))}</button>`).join(" ");
  zona.appendChild(lista);
  // [368, decizia Costin 19.10.2026 „Se validează automat”] la partidă simplă notele sunt interne și se validează singure; cele numite aici
  // sunt cele pe care validarea automată le-a refuzat — se spune ce sunt, înaintea legăturilor
  api.get("/tenants").then((r) => {
    const t = ((r && r.tenants) || []).find((x) => x.id === tenantId);
    if (!t || t.regim_contabil !== "simpla") return;
    const p = document.createElement("p");
    p.className = "ecran-nota";
    p.textContent = `Notele de mai jos sunt interne și nu s-au putut valida automat; motivul fiecăreia e pe nota ei în Registrul jurnal. ${TEXT_NOTA_INTERNA}`;
    lista.insertAdjacentElement("beforebegin", p);
  }).catch(() => {});   // eticheta lipsește, legăturile rămân: lista firmelor e citită și la clic
  lista.querySelectorAll("[data-nota]").forEach((b) => b.addEventListener("click", async () => {
    const n = note[parseInt(b.dataset.nota, 10)];
    const [an, luna] = n.data.split("-").map((x) => parseInt(x, 10));
    const { ecranJurnal } = await import("./firme.js?v=eecc415409");
    const t = ((await api.get("/tenants")).tenants || []).find((x) => x.id === tenantId);
    if (!t || !window._navGlobal) return;
    // [lotul 11, 445] nota se deschide dintr-un refuz: formularul / declarația de dedesubt se păstrează, săgeata și X întorc acolo
    if (window._navGlobal.dinRefuz) window._navGlobal.dinRefuz();
    window._navGlobal.deschide(`Registru jurnal · ${t.nume}`, (corp, nn) => ecranJurnal(corp, nn, t, { evidentiaza: n.nota_id, an, luna }),
      { lat: "tabel" });   // [394] Registrul jurnal se deschide lat de pe orice drum
  }));
}
