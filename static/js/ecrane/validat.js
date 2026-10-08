// validat.js — coada de validare/depunere a declarațiilor (perspectiva seniorului / admin_firma).
// [R41 partea II] „De depus" arată DOAR ce e gata de depus. Ce s-a generat și n-a trecut prin
// validator stă într-o listă separată, care spune CE lipsește și PE UNDE se iese (DS cap.6).
// Populația celor două liste vine din `gata_de_depus`, calculat de SERVER (coada_api.gata_de_depus),
// nu din vreo regulă scrisă aici: două definiții ale aceleiași propoziții ar fi lăsat ecranul să
// numească „de depus" exact ce serverul refuză.
// Cu patru-ochi ACTIV: "De validat" (la_senior -> Aprobă/Respinge) + "Aprobate, de depus" (aprobata -> Depune).
// Cu patru-ochi DEZACTIVAT (mono-utilizator): nu există validare în doi — tot ce e în coadă e "De depus";
//   pentru un item la_senior, „Confirmă depunerea" înlănțuie aproba+depune (backendul permite auto-aprobarea
//   când patru-ochi e oprit). Vezi cardul „De depus" din cabinet.js.
// Butoanele se rescriu după permisiunile actorului curent (poate_valida / poate_depune),
// proaspete de la GET /eu/permisiuni. Control „patru ochi": cine a pregătit nu poate aproba
// (ascuns vizual + blocat în backend) — DOAR când patru-ochi e activ.
// Perioada afișată = perioada DECLARATĂ (an/lună/trim din payload); scadența = termen, etichetată separat.
// Dialogurile (motiv respingere / index SPV) folosesc ferestre modale proprii (nav.deschide).
//
// [R126, 02.09.2026 — DECIZIA lui Costin, varianta (a)] CONFIRMAREA CONSTATARILOR CERTE STA AICI,
// pe drumul depunerii, nu pe ecranul Supervizorului. Motivul, verbatim: *„confirmarea stă unde se
// ia decizia, cu depunerea oprită și constatarea în față. De pe ecranul Supervizorului s-ar putea
// confirma cu ore înainte, rupt de actul căruia îi dă drumul, iar sub termen unul din două ecrane
// se sare."*
//
// CUM: `POST /coada/{id}/depune` raspunde **409** cu `detail.cod = CONSTATARI_NECONFIRMATE` si cu
// constatarile intregi. Raspunsul ala NU e o eroare de aratat — e **pasul urmator al aceluiasi
// act**, deci se randeaza ca pas pe traseu (`nav.mergi`), in aceeasi fereastra, cu drum inapoi.
// Omul scrie un motiv per constatare, iar cererea se retrimite cu `confirmari: [{amprenta, motiv}]`.
//
// AMPRENTA se trimite inapoi asa cum a venit, niciodata recompusa aici: ea leaga confirmarea de
// CIFRELE vazute atunci (`supervizor.amprenta`). O confirmare recompusa pe client ar putea acoperi
// alta constatare decat cea citita — chiar clasa pe care amprenta o apara.
import { api, dataRo, esc, eroareCamp, arataMesaj, bani, confirmaCaseta } from "../api.js?v=4242dc4353";
import { randA as randConstatare } from "./control_verdict.js?v=90aae1066a";
import { sesiune } from "../sesiune.js?v=416ae1edca";

function numeFirma(firme, tid) {
  const f = firme.find((x) => x.tenant_id === tid || x.id === tid);
  return f ? f.nume : `firma #${tid}`;
}

// [R41 partea II] Eticheta verdictului — DERIVATĂ din starea întoarsă de server (interdicția 31:
// eticheta nu se alege de cine randează). Până azi cardul purta `c.coerenta`, care e NULL pe TOATE
// elementele, deci scria „neverificat" despre orice — inclusiv despre o declarație pe care
// validatorul o dăduse validă cu o clipă înainte.
function verdictInfo(c) {
  const v = (c && c.verdict_stare) || { stare: "lipsa" };
  const gata = !!(c && c.gata_de_depus);
  if (gata) {
    return { gata: true, clasa: "val-coer-ok", text: "validat cu DUKIntegrator",
             lipsa: "", iesire: "" };
  }
  if (v.stare === "proaspat" && v.verdict === "erori" && v.severitate === "atentionare") {
    // [C3, 07.10.2026] atenționările DUK nu opresc: se confirmă în scris (pe ACEST conținut), apoi se depune
    return { gata: false, atentionari: true, clasa: "val-coer-atentie", text: "atenționări DUK neconfirmate",
             lipsa: "DUKIntegrator a semnalat atenționări (nu erori) pe conținutul curent.",
             iesire: "Citește-le și confirmă-le în scris; confirmarea se păstrează cu numele tău." };
  }
  if (v.stare === "proaspat") {
    // verdict proaspăt, dar nefavorabil: validatorul a rulat pe conținutul ăsta și a respins.
    // [C3, 07.10.2026] „O eroare DUK oprește.” — fără „Depune totuși”.
    return { gata: false, faraTrecere: v.verdict === "erori", clasa: "val-coer-rau",
             text: v.verdict === "erori" ? "validatorul a găsit erori" : `validator: ${v.verdict || "necunoscut"}`,
             lipsa: "DUKIntegrator a rulat pe conținutul curent și nu l-a acceptat.",
             iesire: "Deschide declarația ca să vezi ce a raportat, apoi regenerează." };
  }
  if (v.stare === "statut") {
    return { gata: false, clasa: "val-coer-atentie", text: "verdict stătut",
             lipsa: v.motiv || "verdictul e pe alt conținut decât cel din coadă.",
             iesire: v.actiune || "Redeschide elementul ca să fie validat conținutul curent." };
  }
  return { gata: false, clasa: "val-coer-gri", text: "nevalidat",
           lipsa: v.motiv || "nu s-a păstrat niciun verdict pentru elementul ăsta.",
           iesire: v.actiune || "Deschide elementul — validatorul rulează și verdictul se păstrează." };
}

// uid-ul actorului curent, ca string (creat_de/aprobat_de sunt UID-uri text în coadă)
function uidCurent() {
  const u = sesiune.user();
  return u && u.id != null ? String(u.id) : null;
}

// [perioada_declarata_v1] perioada DECLARATĂ (nu scadența): "august 2026" lunar, "trim. III 2026" trimestrial,
// "anul 2026" anual. Fallback pe c.perioada (scadența) doar dacă payload-ul nu are an (intrări vechi).
const _ROM = ["", "I", "II", "III", "IV"];
function fmtPerioadaDecl(c) {
  const an = c.p_an, luna = c.p_luna, trim = c.p_trim;
  if (an && luna) return dataRo(`${an}-${String(luna).padStart(2, "0")}`, "luna_an"); // "august 2026"
  if (an && trim) return `trim. ${_ROM[trim] || trim} ${an}`;                          // "trim. III 2026"
  if (an) return `anul ${an}`;
  return c.perioada || "—";
}

// [lotul 07.10 B, C12d] ultima acțiune a validatorului (respinge / validează), cu elementele ei: ecranul o CONFIRMĂ la redesenare.
// Din notificare, redesenarea venea cu `evidentiaza` = elementul tocmai respins, care nu mai e de validat — și ecranul spunea
// „nu mai așteaptă validarea: a fost deja validat sau respins”, ca despre altcineva. Acum spune ce ai făcut tu.
let _ultimaActiune = null;
function _confirma(ids, text) { _ultimaActiune = { ids: ids.map(Number), text, la: Date.now() }; }

// [08.10.2026, U4] Titlul cozii = ce conține: „Note de validat”, „Declarații de validat”, „Declarații de depus” — părțile nevide,
// unite cu „ · ”; coada goală -> „Coada de validare și depunere”.
export function titluCoada({ note = 0, deValidat = 0, deDepus = 0 }) {
  const parti = [note ? "Note de validat" : "", deValidat ? "Declarații de validat" : "", deDepus ? "Declarații de depus" : ""].filter(Boolean);
  return parti.length ? parti.join(" · ") : "Coada de validare și depunere";
}

export async function randeazaValidat(corp, nav, opt = {}) {   // [lotul 07.10 pct.8] opt.evidentiaza = id-ul din notificare
  corp.innerHTML = `<p class="ecran-nota">Se încarcă coada…</p>`;
  let coada = [];
  let firme = [];
  let perm = { poate_valida: false, poate_depune: false, rol: null };
  let patruOchi = false;          // efectiv = politica AND aplicabilitate
  let patruOchiPolitica = false;  // politica bruta a patronului (pentru a distinge „oprit" de „suspendat")
  try {
    const [rc, rf, rp, rpo] = await Promise.all([
      api.get("/coada"),
      api.get("/tenants"),
      api.get("/eu/permisiuni"),
      api.get("/eu/patru-ochi"),
    ]);
    coada = (rc && rc.coada) || [];
    firme = (rf && rf.tenants) || [];
    if (rp) perm = rp;
    // [po_efectiv_v1] `efectiv` (politica AND aplicabilitate), nu flagul brut: pe un cabinet cu un
    // singur validator ecranul arata "o valideaza altcineva" cu un "altcineva" inexistent, iar
    // butoanele de aprobare lipseau desi backendul permitea aprobarea.
    patruOchi = !!(rpo && rpo.efectiv);
    patruOchiPolitica = !!(rpo && rpo.activ);
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca coada.</p>`;
    return;
  }
  // [validare_note 06.10.2026, comanda Costin pct.1] coada poartă și NOTELE pregătite de asistenți (`fel: "nota"`). Ele se
  // validează (nota devine validată în jurnal) sau se resping cu motiv — nu se depun; au secțiunea lor, oricare ar fi
  // regimul patru-ochi, fiindcă le-a pregătit altcineva decât cel care le validează.
  const noteDeValidat = coada.filter((c) => c.fel === "nota" && c.stare === "la_senior");
  const declaratii = coada.filter((c) => c.fel !== "nota");
  const laSenior = declaratii.filter((c) => c.stare === "la_senior");
  const aprobate = declaratii.filter((c) => c.stare === "aprobata");

  // [po_efectiv_v1] TREI texte, nu doua: „oprit" si „suspendat" nu sunt acelasi lucru. Pe un cabinet
  // solo cu politica PORNITA, „Patru-ochi e dezactivat" contrazicea indicatorul din subbara
  // („suspendata") si il lasa pe patron sa creada ca i s-a stins setarea. Politica persista; ce
  // lipseste e al doilea validator - si se spune, cu iesirea (DS cap.6, stare goala: gol + cauza + iesire).
  // [lotul 07.10 pct.11, comanda Costin 06.10.2026] „Contabilul vede o etichetă pentru ce are de validat și un text fără termeni
  // interni.” Notele au eticheta lor și propoziția lor (le-a pregătit un asistent; le validezi sau le respingi); textul despre
  // declarații vorbește despre declarații, fără „patru-ochi” — „validarea în doi” e numele pe care îl vede omul în Asistenți.
  const intro = patruOchi
    ? "Declarațiile pregătite de asistenți așteaptă validarea ta înainte de depunere. Nimic nu se depune nevalidat."
    : (patruOchiPolitica
      ? "Validarea în doi e pornită, dar suspendată: ești singurul validator din cabinet, așa că pregătești și depui singur. Reintră în vigoare de îndată ce un coleg primește dreptul de validare (cardul Asistenți)."
      : "Declarațiile le pregătești și le depui tu (validarea în doi nu e pornită). Cele din listă așteaptă depunerea.");
  // [08.10.2026, decizia Costin U4] „Fereastra cu note de validat se numește «De depus». Titlul trebuie să spună ce conține.” Titlul
  // venea din cardul de pe desktop (calculat o dată, fără note), iar navigatorul îl punea ca <h2>. Acum ecranul își scrie titlul din
  // ce are în el: părțile nevide, în ordinea în care apar (`titluCoada`).
  const titlu = titluCoada({ note: noteDeValidat.length, deValidat: patruOchi ? laSenior.length : 0,
                             deDepus: patruOchi ? aprobate.length : declaratii.filter((c) => c.stare === "la_senior" || c.stare === "aprobata").length });
  corp.innerHTML = `
    <h2 class="pf-titlu" id="val-titlu">${esc(titlu)}</h2>
    <div id="val-note"></div>
    <p class="mig-intro">${intro}</p>
    <div id="val-deValidat"></div>
    <div id="val-deDepus"></div>
    <div id="val-nevalidate"></div>
    <div class="mig-eroare" id="val-eroare"></div>
  `;
  const z1 = corp.querySelector("#val-deValidat");
  const z2 = corp.querySelector("#val-deDepus");
  const z3 = corp.querySelector("#val-nevalidate");

  const zN = corp.querySelector("#val-note");
  if (noteDeValidat.length) {
    zN.innerHTML = `<div class="cf-grup-titlu cf-galben">Note de validat (${noteDeValidat.length})</div>
      <p class="mig-intro">Notele pregătite de asistenți: le validezi (intră în evidență) sau le respingi cu motivul, pe care asistentul îl vede lângă notă. Notele aceleiași facturi (contarea și ieșirea din stoc) se validează împreună.</p>`;
    noteDeValidat.forEach((c) => zN.appendChild(randNota(c, firme, corp, nav, perm)));
  }
  // [lotul 07.10 pct.8] din notificare: elementul ei, adus în vedere și marcat (și când e un membru al unui document)
  const evid = Number(opt.evidentiaza);
  // valabilă câteva secunde, nu „consumată”: întoarcerea din dialog poate redesena ecranul de două ori (o dată din navigator, cu
  // opțiunile notificării, o dată explicit) — ambele desene arată confirmarea, niciunul nu spune „deja validat sau respins”
  const actiune = _ultimaActiune && Date.now() - _ultimaActiune.la < 10000 ? _ultimaActiune : null;
  if (actiune) {
    const p = document.createElement("div");
    p.className = "caseta-info";
    p.innerHTML = `<span class="ci-mesaj">${esc(actiune.text)}</span>`;
    corp.prepend(p);
  }
  const _arataEvidentiat = () => {
    if (!Number.isFinite(evid)) return;
    if (actiune && actiune.ids.includes(evid)) return;          // acțiunea pe elementul din notificare e confirmată mai sus
    const el = [...corp.querySelectorAll("[data-coada-ids]")].find((x) => x.dataset.coadaIds.split(",").map(Number).includes(evid));
    if (el) { el.classList.add("val-evidentiat"); el.scrollIntoView({ block: "center" }); }
    else {
      const p = document.createElement("p");
      p.className = "ecran-nota";
      p.textContent = "Elementul din notificare nu mai așteaptă validarea: a fost deja validat sau respins.";
      corp.prepend(p);
    }
  };
  setTimeout(_arataEvidentiat, 0);
  if (laSenior.length === 0 && aprobate.length === 0) {
    if (!noteDeValidat.length) {
      z1.innerHTML = `<div class="stare-goala">${patruOchi ? "Nimic de validat. Coada e goală." : "Nimic de depus. Coada e goală."}</div>`;
    }
    return;
  }

  // [R41 partea II] «gata de depus» vine de la server, per element. Nu se recalculează aici.
  const gata = (c) => !!c.gata_de_depus;

  if (patruOchi) {
    // ── patru-ochi ACTIV: validare în doi ──
    if (laSenior.length) {
      z1.innerHTML = `<div class="cf-grup-titlu cf-galben">De validat (${laSenior.length})</div>`;
      laSenior.forEach((c) => z1.appendChild(randDeclaratie(c, firme, corp, nav, "valida", perm, patruOchi)));
    }
    const apGata = aprobate.filter(gata);
    const apNu = aprobate.filter((c) => !gata(c));
    if (apGata.length) {
      z2.innerHTML = `<div class="cf-grup-titlu" style="color:var(--verde)">Aprobate, de depus (${apGata.length})</div>`;
      apGata.forEach((c) => z2.appendChild(randDeclaratie(c, firme, corp, nav, "depune", perm, patruOchi)));
    }
    if (apNu.length) z3.appendChild(zonaNevalidate(apNu, firme, corp, nav, perm, patruOchi, "Aprobate, dar nevalidate"));
  } else {
    // ── patru-ochi DEZACTIVAT: mono-utilizator, pregătește și depune singur ──
    const deDepus = [...laSenior, ...aprobate];
    const dGata = deDepus.filter(gata);
    const dNu = deDepus.filter((c) => !gata(c));
    if (dGata.length) {
      z1.innerHTML = `<div class="cf-grup-titlu" style="color:var(--verde)">De depus (${dGata.length})</div>`;
      dGata.forEach((c) => z1.appendChild(randDeclaratie(c, firme, corp, nav, "depune", perm, patruOchi)));
    } else {
      // DS cap.6: gol + cauză + ieșire. Fundătura („Nimic de depus.") e interzisă, iar aici
      // golul are o cauză precisă — există lucrări, dar niciuna validată.
      z1.innerHTML = `<div class="cf-grup-titlu" style="color:var(--verde)">De depus (0)</div>
        <div class="stare-goala">Nimic gata de depus. ${dNu.length} ${dNu.length === 1 ? "declarație e generată" : "declarații sunt generate"}, dar ${dNu.length === 1 ? "n-a trecut" : "n-au trecut"} prin validatorul oficial.<br>Deschide-le mai jos — validatorul rulează și verdictul se păstrează.</div>`;
    }
    if (dNu.length) z2.appendChild(zonaNevalidate(dNu, firme, corp, nav, perm, patruOchi, "Generate, nevalidate"));
  }
}

// UN singur apel de aprobare, pentru declarații și note: pentru notă, serverul o validează în jurnal (aceeași tranzacție)
function aprobaElement(c) {
  return api.post(`/coada/${c.id}/aproba`, {});
}

// [validare_note] Rândul unei note din coadă: ce e, cine a pregătit-o, documentul și totalul; „Vezi nota” arată liniile.
function randNota(c, firme, corp, nav, perm) {
  const n = c.nota || {};
  const div = document.createElement("div");
  div.className = "val-card";
  div.dataset.coadaIds = (c.membri_ids || [c.id]).join(",");   // [lotul 07.10 pct.8-9] documentul, cu toate notele lui
  const uid = uidCurent();
  const euAmPregatit = uid != null && c.creat_de != null && String(c.creat_de) === uid;
  let actiuni = "";
  if (!perm.poate_valida) {
    actiuni = `<span class="val-nota-perm">nu ai dreptul de validare</span>`;
  } else if (euAmPregatit) {
    actiuni = `<span class="val-nota-perm">ai pregătit-o tu — o validează altcineva</span>`;
  } else {
    actiuni = `<button class="buton-primar val-btn val-aproba" data-act="valideaza-nota" data-actiune="POST /coada/{coada_id}/aproba">Validează</button>
      <button class="buton-sters val-btn val-respinge" data-act="respinge-nota" data-actiune="POST /coada/{coada_id}/respinge">Respinge</button>`;
  }
  div.innerHTML = `
    <div class="val-info">
      <div class="val-titlu"><b>${esc(c.eticheta || "Notă")}</b></div>
      <div class="val-sub">${esc(numeFirma(firme, c.tenant_id))} · pregătită de ${esc(c.creat_de_nume || c.creat_de || "—")}</div>
      ${c.retrimisa ? `<div class="val-sub">Retrimisă după respingere · motivul anterior: „${esc(c.retrimisa.motiv_respingere || "fără motiv")}” · ${c.retrimisa.schimbata === true ? "nota s-a schimbat față de cea respinsă" : c.retrimisa.schimbata === false ? "nota NU s-a schimbat față de cea respinsă" : "schimbarea nu se poate compara (nota respinsă e dinaintea amprentei)"}</div>` : ""}
      <div class="val-termen">${n.data ? esc(dataRo(n.data)) : ""} · total ${bani(n.total || 0)} lei${n.document_ref ? "" : " · fără document justificativ"}${n.stinge ? " · stinge " + esc(n.stinge) : ""}</div>
      <button type="button" class="btn-link val-vezi-nota">${(c.membri_ids || []).length > 1 ? "Vezi notele →" : "Vezi nota →"}</button>
    </div>
    <div class="val-actiuni">${actiuni}</div>`;
  div.querySelector(".val-vezi-nota").addEventListener("click", () => deschideNota(c, nav, { actiuni, corpLista: corp }));
  legaActiuniNota(div, c, corp, nav, corp.querySelector("#val-eroare"), false);
  return div;
}

// [08.10.2026, decizia Costin U5] Validează / Respinge ale unei note — o singură definiție, pentru cardul din coadă și pentru detaliul
// notei („Detaliul notei are direct Validează și Respinge”). `dinDetaliu`: după act se închide detaliul și se reîncarcă lista.
function legaActiuniNota(zona, c, corpLista, nav, eroare, dinDetaliu) {
  const n = c.nota || {};
  const bResp = zona.querySelector(".val-respinge");
  if (bResp) bResp.addEventListener("click", () => {
    dialogInput(nav, {
      titlu: "Respinge nota",
      eticheta: `Motiv respingere pentru ${esc(c.eticheta || "notă")}:`,
      placeholder: "ex: lipsește factura; contul de cheltuială e greșit",
      // [lotul 07.10 B, C12e] butonul de confirmare arată ca butonul care l-a deschis (roșu plin), nu roz-pal „dezactivat”
      obligatoriu: true, buton: "Respinge", butonClasa: "buton-sters val-respinge",
      onConfirm: async (motiv) => {
        await api.post(`/coada/${c.id}/respinge`, { motiv });
        _confirma(c.membri_ids || [c.id], `Ai respins ${c.eticheta || "nota"}. Motivul („${motiv}”) apare lângă notă la cel care a pregătit-o.`);
        nav.inapoi(); if (dinDetaliu) nav.inapoi();
        randeazaValidat(corpLista, nav);
      },
    });
  });
  const bVal = zona.querySelector(".val-aproba");
  if (bVal) bVal.addEventListener("click", () => {
    const btn = bVal;
    const valideaza = async () => {
      try {
        await aprobaElement(c);
        _confirma(c.membri_ids || [c.id], `Ai validat ${c.eticheta || "nota"}: a intrat în evidență.`);
        if (dinDetaliu) nav.inapoi();
        randeazaValidat(corpLista, nav);
      }
      catch (e) { if (eroare) arataMesaj(eroare, (e && e.mesaj) || "Eroare la validare.", "eroare"); }
    };
    // aceeași confirmare ca în Registrul-jurnal: nota fără document justificativ se validează numai explicit
    if (!n.document_ref) {
      confirmaCaseta(btn.parentElement || btn, "Nota nu are document justificativ. Validezi totuși?", valideaza,
        { textOk: "Validează fără document" });
      return;
    }
    valideaza();
  });
}

async function deschideNota(c, nav, ctx = {}) {
  nav.deschide(c.eticheta || "Notă", async (corp) => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă nota…</p>`;
    let d;
    try { d = await api.get(`/coada/${c.id}/continut`); }
    catch (e) { corp.innerHTML = `<div class="dec-eroare">${esc((e && e.mesaj) || "Nu am putut încărca nota.")}</div>`; return; }
    // [lotul 07.10 pct.9] un document cu mai multe note (contarea + ieșirea din stoc a aceleiași facturi): toate, una sub alta
    const note = d.note || [{ nota: d.nota || {}, linii: d.linii || [] }];
    corp.innerHTML = note.map(({ nota: n, linii }) => `
      <p class="mig-intro">Nota #${esc(String(n.id || ""))} · ${esc(dataRo(n.data))} · ${esc(n.descriere || "")} · ${n.document_ref ? "document: " + esc(n.document_ref) : "fără document justificativ"}${n.stinge ? " · stinge " + esc(n.stinge) : ""}</p>
      <table class="fd-tabel"><thead><tr><th>Debit</th><th>Credit</th><th>Sumă</th></tr></thead>
        <tbody>${(linii || []).map((l) => `<tr><td>${esc(l.debit)}</td><td>${esc(l.credit)}</td><td>${bani(l.suma)}</td></tr>`).join("")}</tbody>
      </table>`).join("") + (ctx.actiuni ? `<div class="val-actiuni" id="val-nota-actiuni" style="margin-top:12px">${ctx.actiuni}</div><div id="val-nota-eroare"></div>` : "");
    if (ctx.actiuni && ctx.corpLista) legaActiuniNota(corp, c, ctx.corpLista, nav, corp.querySelector("#val-nota-eroare"), true);
  }, { nivel: "cabinet" });
}

// [R41 partea II] Lista separată. Titlul nu spune „de depus" — fiindcă nu sunt.
function zonaNevalidate(lista, firme, corp, nav, perm, patruOchi, titlu) {
  const frag = document.createDocumentFragment();
  const cap = document.createElement("div");
  cap.className = "cf-grup-titlu cf-galben";
  cap.textContent = `${titlu} (${lista.length})`;
  frag.appendChild(cap);
  const nota = document.createElement("p");
  nota.className = "ecran-nota";
  nota.textContent = "Serverul refuză depunerea lor. Se poate trece peste refuz, dar numai explicit, cu un motiv scris — iar motivul se consemnează cu cine și când.";
  frag.appendChild(nota);
  lista.forEach((c) => frag.appendChild(randDeclaratie(c, firme, corp, nav, "depune", perm, patruOchi)));
  return frag;
}

// [patru-ochi-vizibil] deschide continutul unui element din coada pentru validare: declaratie
// (avertismente/note) + XML + verdictul DUK. Read-only. Fara asta, cine aproba nu vede ce aproba.
async function deschideContinut(c, nav, corpLista) {
  // [R41 partea II] Ruta asta RULEAZĂ validatorul și PĂSTREAZĂ verdictul. Deci după închiderea
  // ferestrei, lista de dedesubt e stătută — se reîncarcă. Fără asta, omul validează, se întoarce,
  // și vede aceeași etichetă „nevalidat" pe care tocmai a schimbat-o.
  const titlu = `${(c.tip || "").toUpperCase()} \u00b7 ${fmtPerioadaDecl(c)}`;
  nav.deschide(titlu, async (corp) => {
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103 declara\u021bia\u2026</p>`;
    let d;
    try { d = await api.get(`/coada/${c.id}/continut`); }
    catch (e) {
      corp.innerHTML = `<div class="dec-eroare">Nu am putut \u00eencarca con\u021binutul: ${esc((e && e.mesaj) || "eroare")}</div>`;
      return;
    }
    const xml = d.xml_b64 ? (function(){ try { return decodeURIComponent(escape(atob(d.xml_b64))); } catch(e){ return ""; } })() : "";
    const stare = d.stare || "gri";
    const duk = stare === "valid"
      ? `<div class="dec-ok">Validat cu DUKIntegrator (validatorul oficial ANAF, rulat local), f\u0103r\u0103 erori.</div>`
      : (stare === "erori"
          ? `<div class="dec-eroare"><div class="dec-avert-cap">DUKIntegrator (validatorul ANAF, local) a g\u0103sit ${d.severitate === "atentionare" ? "aten\u021bion\u0103ri" : "erori"}</div><pre class="dec-xml-pre">${esc(d.erori || "")}</pre></div>`
          : `<div class="dec-avert"><div class="dec-avert-cap">Nu am putut valida cu DUKIntegrator</div><ul><li>${esc(d.temei || "")}</li><li>${esc(d.limita || "")}</li></ul></div>`);
    const av = d.avertismente || [];
    const avert = av.length
      ? `<div class="caseta-atentie"><b>Avertismente (${av.length})</b><ul>${av.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></div>`
      : "";
    corp.innerHTML = `
      <p class="mig-intro">Con\u021binutul declara\u021biei \u2014 vizualizare pentru validare (patru ochi). Read-only.</p>
      ${duk}
      ${avert}
      <details open><summary>XML generat</summary><pre class="dec-xml-pre">${esc(xml)}</pre></details>
    `;
    if (corpLista) randeazaValidat(corpLista, nav);
  }, { nivel: "cabinet" });
}


function randDeclaratie(c, firme, corp, nav, mod, perm, patruOchi) {
  const div = document.createElement("div");
  div.className = "val-card";
  div.dataset.coadaIds = String(c.id);   // [lotul 07.10 pct.8] ținta notificării
  const vi = verdictInfo(c);
  const coer = `<span class="val-coer ${vi.clasa}">${vi.gata ? "✓ " : ""}${esc(vi.text)}</span>`;

  const uid = uidCurent();
  const euAmPregatit = uid != null && c.creat_de != null && String(c.creat_de) === uid;

  let actiuni = "";
  if (mod === "valida") {
    // Aprobă — doar dacă pot valida ȘI (patru-ochi activ) nu eu am pregătit-o
    if (!perm.poate_valida) {
      actiuni += `<span class="val-nota-perm">nu ai dreptul de validare</span>`;
    } else if (euAmPregatit) {
      actiuni += `<span class="val-nota-perm">ai pregătit-o tu — o validează altcineva</span>`;
    } else {
      actiuni += `<button class="buton-primar val-btn val-aproba" data-act="aproba" data-actiune="POST /coada/{coada_id}/aproba">Aprobă</button>`;
    }
    // Respinge — oricine cu drept de validare (și care n-a pregătit-o, când patru-ochi e activ)
    if (perm.poate_valida && !euAmPregatit) {
      actiuni += `<button class="buton-sters val-btn val-respinge" data-act="respinge" data-actiune="POST /coada/{coada_id}/respinge">Respinge</button>`;
    }
  } else {
    // depune -> "Confirmă depunerea". Cu patru-ochi OFF, un item la_senior se aprobă automat înainte de depunere.
    const needsAproba = c.stare === "la_senior";
    const potDepune = perm.poate_depune && (!needsAproba || perm.poate_valida);
    if (!potDepune) {
      actiuni += `<span class="val-nota-perm">nu ai dreptul de depunere</span>`;
    } else if (vi.gata) {
      actiuni += `<button class="buton-primar val-btn val-depune" data-act="depune" data-actiune="POST /coada/{coada_id}/depune">Confirmă depunerea</button>`;
    } else {
      // [R41 partea II] Nu e gata: acțiunea principală devine cea care REPARĂ (deschide, ca
      // validatorul să ruleze și verdictul să se păstreze). Depunerea rămâne posibilă, dar
      // explicită și consemnată — nu ascunsă, fiindcă un blocaj fără cale de trecere pentru om
      // e interdicția 47.
      actiuni += `<button class="val-btn val-valideaza" data-act="vezi">Deschide ca să fie validat</button>`;
      if (vi.atentionari) {
        actiuni += `<button class="val-btn val-trece" data-act="trece" data-actiune="POST /coada/{coada_id}/depune">Confirmă atenționările și depune…</button>`;
      } else if (!vi.faraTrecere) {
        actiuni += `<button class="val-btn val-trece" data-act="trece" data-actiune="POST /coada/{coada_id}/depune">Depune totuși…</button>`;
      }
    }
    // Cu patru-ochi OFF, mono-utilizatorul poate renunța la un item încă neaprobat (respinge din la_senior)
    if (!patruOchi && needsAproba && perm.poate_valida) {
      actiuni += `<button class="buton-sters val-btn val-respinge" data-act="respinge" data-actiune="POST /coada/{coada_id}/respinge">Renunță</button>`;
    }
  }

  const perDecl = fmtPerioadaDecl(c);
  div.innerHTML = `
    <div class="val-info">
      <div class="val-titlu"><b>${(c.tip||"").toUpperCase()}</b> · ${perDecl}</div>
      <div class="val-sub">${numeFirma(firme, c.tenant_id)} · pregătit de ${c.creat_de_nume || c.creat_de || "—"}</div>
      <div class="val-termen">termen (scadență): ${c.perioada || "—"}</div>
      ${vi.gata ? "" : `<div class="val-lipsa">${esc(vi.lipsa)} <span class="val-lipsa-iesire">${esc(vi.iesire)}</span></div>`}
      ${c.trecere_motiv ? `<div class="val-lipsa">trecut peste refuz, motiv: ${esc(c.trecere_motiv)}</div>` : ""}
      <button type="button" class="btn-link val-vezi" data-act="vezi">Vezi declarația, XML și verdictul DUK →</button>
    </div>
    <div class="val-mij">${coer}</div>
    <div class="val-actiuni">${actiuni}</div>
  `;
  div.querySelectorAll(".val-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.dataset.act === "vezi") { deschideContinut(c, nav, corp); return; }
      actioneaza(c, btn.dataset.act, firme, corp, nav);
    });
  });
  const _vezi = div.querySelector(".val-vezi");
  if (_vezi) _vezi.addEventListener("click", () => deschideContinut(c, nav, corp));
  return div;
}

async function actioneaza(c, act, firme, corp, nav) {
  const eroare = corp.querySelector("#val-eroare");
  if (eroare) eroare.textContent = "";
  const perDecl = fmtPerioadaDecl(c);
  if (act === "respinge") {
    dialogInput(nav, {
      titlu: "Respinge declarația",
      eticheta: `Motiv respingere pentru ${(c.tip||"").toUpperCase()} (${perDecl}):`,
      placeholder: "ex: TVA necorelată cu jurnalul de vânzări",
      obligatoriu: true,
      buton: "Respinge",
      butonClasa: "buton-sters val-respinge",   // [lotul 07.10 B, C12e]
      onConfirm: async (motiv) => {
        await api.post(`/coada/${c.id}/respinge`, { motiv });
        _confirma([c.id], `Ai respins ${(c.tip || "").toUpperCase()} (${perDecl}). Motivul („${motiv}”) apare la cel care a pregătit-o.`);
        nav.inapoi();
        randeazaValidat(corp, nav);
      },
    });
    return;
  }
  if (act === "trece") {
    // [R41 partea II] Trecerea peste refuz: motiv OBLIGATORIU, consemnat cu cine și când.
    const atent = verdictInfo(c).atentionari;   // [C3] atenționări: confirmarea lor, nu o trecere peste verdict
    dialogInput(nav, {
      titlu: atent ? "Confirmă atenționările DUK" : "Depune fără verdict de validare",
      eticheta: atent
        ? `${(c.tip||"").toUpperCase()} (${perDecl}): DUKIntegrator a semnalat atenționări (nu erori). De ce e corectă declarația așa?`
        : `${(c.tip||"").toUpperCase()} (${perDecl}) nu are verdict valid de la DUKIntegrator. De ce o depui totuși?`,
      placeholder: "ex: validatorul nu pornește, iar termenul e azi",
      obligatoriu: true,
      buton: "Depune, cu motivul de mai sus",
      butonClasa: "val-trece",
      onConfirm: async (motiv, corpDialog) => {
        // [02.09] NU se mai înlănțuie `aproba` aici: aprobarea e a serverului și vine DUPĂ poartă.
        await depuneCuPoarta(nav, c, corpDialog, corp, firme, perDecl, { motiv_trecere: motiv });
      },
    });
    return;
  }
  if (act === "depune") {
    dialogInput(nav, {
      titlu: "Confirmă depunerea",
      eticheta: `Index SPV pentru ${(c.tip||"").toUpperCase()} (${perDecl}) — opțional:`,
      placeholder: "lasă gol dacă nu ai indexul încă",
      obligatoriu: false,
      buton: "Confirmă depunerea",
      butonClasa: "val-depune",
      onConfirm: async (spv, corpDialog) => {
        // [02.09.2026, defect găsit apăsând] ÎNLĂNȚUIREA A IEȘIT DIN CLIENT.
        // Ecranul chema `aproba` apoi `depune`; poarta confirmării trăiește în `depune`, deci
        // aprobarea trecea și poarta cădea DUPĂ ea. Elementul rămânea `aprobata` — stare din care
        // nu se mai poate respinge —, iar o listă care încă îl credea `la_senior` re-chema `aproba`
        // și murea pe „nu pot aproba din starea «aprobata»", fără să ajungă la depunere.
        // Măsurat în `uvicorn.log`, pe elementul 8052. Acum se trimite UN act, iar serverul aprobă
        // după ce poarta a trecut (`coada_api.auto_aproba_daca_e_cazul`).
        await depuneCuPoarta(nav, c, corpDialog, corp, firme, perDecl,
                             spv ? { spv_index: spv } : {});
      },
    });
    return;
  }
  // aproba — fara dialog, direct
  try {
    await aprobaElement(c);
    randeazaValidat(corp, nav);
  } catch (e) {
    if (eroare) arataMesaj(eroare, (e && e.mesaj) || "Eroare la aprobare.", "eroare");
  }
}

// [R82/instanță, 02.09.2026 — DECIZIA lui Costin, varianta (a)] CONFIRMAREA UNUI ACT DE DEPUNERE.
//
// Verbatim: *„același buton nu poate să se încheie vizibil pe un drum și tăcut pe celălalt, iar
// drumul tăcut e cel obișnuit. Tăcerea ajunge să însemne «s-a făcut», și atunci ziua în care nu s-a
// făcut arată la fel."*
//
// UNA SINGURĂ, deliberat: o a doua casetă pentru drumul „simplu" ar fi divergit de prima la prima
// schimbare, iar ce s-ar fi pierdut e chiar partea care contează — ENTITATEA și CONSECINȚA (DS
// cap.27 / E2). Aici se numesc amândouă, plus ce s-a confirmat, când e cazul.
//
// `n` = câte constatări certe s-au confirmat odată cu depunerea; `0` = drumul obișnuit.
function casetaDepusa(fc, nav, corpLista, c, firme, perDecl, n) {
  const desprConf = n
    ? ` ${n === 1 ? "O constatare certă a fost confirmată" : n + " constatări certe au fost confirmate"}`
      + " în scris, cu numele tău și cu motivul. Confirmarea acoperă cifrele de acum: dacă se schimbă,"
      + " se cere din nou."
    : "";
  fc.innerHTML = `
    <div class="caseta-info">
      <div class="ci-mesaj">
        <b>${esc((c.tip || "").toUpperCase())} · ${esc(perDecl)} · ${esc(numeFirma(firme, c.tenant_id))}</b>
        — depusă.${desprConf}
      </div>
    </div>
    <div class="dlg-actiuni">
      <button type="button" class="val-btn val-depune" id="val-conf-gata">Înapoi la coadă</button>
    </div>`;
  fc.querySelector("#val-conf-gata").addEventListener("click", () => {
    nav.inapoi();
    randeazaValidat(corpLista, nav);
  });
}

// [R126] DEPUNEREA, cu poarta confirmării pe drum. Un singur loc pentru amândouă butoanele care
// depun („Confirmă depunerea" și „Depune, cu motivul de mai sus"): altfel unul dintre ele ar fi
// rămas fără tratarea lui 409, iar contabilul ar fi primit un mesaj brut în loc de pasul următor.
async function depuneCuPoarta(nav, c, corpDialog, corpLista, firme, perDecl, corpCerere) {
  try {
    await api.post(`/coada/${c.id}/depune`, corpCerere);
  } catch (e) {
    const d = e && e.detaliu;
    // NU e o eroare de arătat: e pasul următor al aceluiași act, iar serverul a trimis tot ce
    // trebuie ca să-l putem oferi. Orice ALT refuz merge mai departe la dialog.
    if (e && e.cod === 409 && d && d.cod === "CONSTATARI_NECONFIRMATE" && (d.constatari || []).length) {
      pasConfirmariConstatari(nav, c, corpCerere, d, firme, corpLista, perDecl);
      return;
    }
    throw e;
  }
  casetaDepusa(corpDialog, nav, corpLista, c, firme, perDecl, 0);
}

// [R126] PASUL DE CONFIRMARE — constatările CERTE, în față, cu un motiv per constatare.
//
// De ce `nav.mergi` și nu o fereastră nouă: confirmarea e **un pas al depunerii**, nu un act
// separat. Pasul păstrează drumul înapoi (la indexul SPV) și firul de pesmet, deci omul poate
// renunța fără să piardă ce scrisese la pasul dinainte.
//
// CE NU FACE, declarat: nu decide nimic despre constatări și nu le filtrează. Le arată pe toate
// cele întoarse de server, cu **randarea unică** (`control_verdict.randA`) — aceeași anatomie
// (semn + mesaj + TEMEI + remediu) ca pe ecranul Supervizorului și pe cel de control fiscal. O a
// doua randare ar diverge, iar temeiul e primul care s-ar pierde.
function pasConfirmariConstatari(nav, c, corpBaza, detaliu, firme, corpLista, perDecl) {
  const cs = detaliu.constatari || [];
  nav.mergi("Constatări de confirmat", (fc) => {
    fc.innerHTML = `
      <div class="caseta-atentie">
        <div class="ca-mesaj">${esc(detaliu.mesaj || "")}</div>
      </div>
      <p class="mig-intro">${esc((c.tip || "").toUpperCase())} · ${esc(perDecl)} · ${esc(numeFirma(firme, c.tenant_id))}</p>
      ${cs.map((x, i) => `
        <div class="val-conf-item">
          ${randConstatare(x)}
          <label class="dlg-eticheta" for="val-conf-${i}">De ce depui peste constatarea asta? Motivul rămâne scris, cu numele tău.</label>
          <input class="camp-input dlg-input val-conf-motiv" id="val-conf-${i}" type="text"
                 placeholder="ex: se corectează prin rectificativă; termenul de depunere e azi"
                 autocomplete="off">
        </div>`).join("")}
      <div class="dlg-eroare" id="val-conf-eroare"></div>
      <div class="dlg-actiuni">
        <button type="button" class="buton-secundar val-btn" id="val-conf-renunt">Renunță</button>
        <button type="button" class="val-btn val-depune" id="val-conf-ok" data-actiune="POST /coada/{coada_id}/depune">Confirmă și depune</button>
      </div>`;
    const er = fc.querySelector("#val-conf-eroare");
    const btn = fc.querySelector("#val-conf-ok");
    fc.querySelector("#val-conf-renunt").addEventListener("click", () => nav.inapoiPas());
    btn.addEventListener("click", async () => {
      const campuri = Array.from(fc.querySelectorAll(".val-conf-motiv"));
      er.textContent = "";
      campuri.forEach((inp) => { inp.classList.remove("camp-invalid"); inp.removeAttribute("aria-invalid"); });
      // Motivul e OBLIGATORIU pe FIECARE: o confirmare fără motiv e o bifă, iar o bifă nu se poate
      // citi peste șase luni (`supervizor.scrie_confirmare` o refuză oricum — dar refuzul de acolo
      // ar veni după ce omul a apăsat, fără să spună care câmp).
      const goale = campuri.filter((inp) => !inp.value.trim());
      if (goale.length) {
        goale.forEach((inp) => eroareCamp(fc, inp.id, "Scrie motivul."));
        er.textContent = goale.length === 1
          ? "O constatare n-are motiv scris."
          : `${goale.length} constatări n-au motiv scris.`;
        goale[0].focus();
        return;
      }
      btn.disabled = true;
      try {
        // Amprenta se trimite ÎNAPOI cum a venit — nu se recompune aici. Vezi antetul modulului.
        const confirmari = cs.map((x, i) => ({ amprenta: x.amprenta, motiv: campuri[i].value.trim() }));
        // Corpul cererii dintâi se DUCE MAI DEPARTE (index SPV, sau motivul trecerii peste verdict):
        // a doua cerere e aceeași depunere, nu una nouă. Fără asta, indexul SPV tastat la primul pas
        // s-ar fi pierdut tăcut la confirmare.
        await api.post(`/coada/${c.id}/depune`, Object.assign({}, corpBaza, { confirmari }));
      } catch (e) {
        btn.disabled = false;
        arataMesaj(er, (e && e.mesaj) || "Nu am putut depune. Încearcă din nou.", "eroare");
        return;
      }
      // [DS cap.27 / E2] Aceeasi caseta ca pe drumul fara constatari — v. `casetaDepusa`.
      // DE CE AICI si nu in lista: prima forma scria mesajul in zona de mesaje a listei, dupa
      // `nav.inapoi()`. Proba pe ecran l-a gasit GOL — inchiderea ferestrei re-randeaza ecranul de
      // dedesubt, iar re-randarea suprascrie mesajul. *Un mesaj care pierde o cursa cu re-randarea
      // e mai rau decat niciunul: codul spune ca arata ceva, si nu arata.*
      casetaDepusa(fc, nav, corpLista, c, firme, perDecl, cs.length);
    });
  });
}

// dialog modal cu un input (foloseste fereastra standard nav.deschide)
function dialogInput(nav, opt) {
  nav.deschide(opt.titlu, (corp) => {
    corp.innerHTML = `
      <label for="dlg-input" class="dlg-eticheta">${opt.eticheta}</label>
      <input class="camp-input dlg-input" id="dlg-input" type="text" placeholder="${opt.placeholder || ""}" autocomplete="off">
      <div class="dlg-eroare" id="dlg-eroare"></div>
      <div class="dlg-actiuni">
        <button class="buton-secundar val-btn dlg-anuleaza" id="dlg-anuleaza">Anulează</button>
        <button class="val-btn ${opt.butonClasa}" id="dlg-ok">${opt.buton}</button>
      </div>
    `;
    const input = corp.querySelector("#dlg-input");
    const er = corp.querySelector("#dlg-eroare");
    input.focus();
    const confirma = async () => {
      const val = input.value.trim();
      if (opt.obligatoriu && !val) {
        er.textContent = "Câmpul e obligatoriu.";
        input.focus();
        return;
      }
      const btn = corp.querySelector("#dlg-ok");
      btn.disabled = true;
      try {
        // Al doilea argument e CORPUL dialogului: actul care reuseste isi scrie confirmarea CHIAR
        // AICI, in pasul in care s-a petrecut. Fara el, singura incheiere posibila era demontarea
        // ferestrei — iar „a disparut" arata identic cu „a reusit" si cu „s-a rupt ceva".
        await opt.onConfirm(val, corp);
      } catch (e) {
        btn.disabled = false;
        arataMesaj(er, (e && e.mesaj) || "Eroare. Încearcă din nou.", "eroare");
      }
    };
    corp.querySelector("#dlg-ok").addEventListener("click", confirma);
    corp.querySelector("#dlg-anuleaza").addEventListener("click", () => nav.inapoi());
    input.addEventListener("keydown", (ev) => { if (ev.key === "Enter") confirma(); });
  });
}
