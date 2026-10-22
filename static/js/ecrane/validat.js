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
import { api, cate, dataRo, esc, eroareCamp, arataMesaj, bani, confirmaCaseta, focusFaraSalt, refuzPeRand } from "../api.js?v=58f26a3fc4";
import { randA as randConstatare } from "./control_verdict.js?v=2daa29640d";
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { deschideFirma, ecranJurnal } from "./firme.js?v=020b99dd0c";
import { permis } from "../drepturi.js?v=34d0fb0afd";

// [Retest 2, pct.7] „«total 0,00 lei» la notele de stornare + reînregistrare. Se afișează rulajul notei.” Partea în roșu și partea
// înregistrată, fiecare cu suma ei; o notă fără stornare are un singur rulaj. (Payload-urile vechi, fără `rulaj`, arată totalul.)
function rulajNota(n) {
  const st = Number(n.rulaj_storno || 0);
  const rj = n.rulaj != null ? n.rulaj : n.total;
  return st ? `stornare −${bani(st)} lei · înregistrare ${bani(rj || 0)} lei` : `rulaj ${bani(rj || 0)} lei`;
}

function numeFirma(firme, tid) {
  const f = firme.find((x) => x.tenant_id === tid || x.id === tid);
  return f ? f.nume : "o firmă care nu mai e în lista ta";   // [258] niciodată id-ul intern
}

// [R41 partea II] Eticheta verdictului — DERIVATĂ din starea întoarsă de server (interdicția 31:
// eticheta nu se alege de cine randează). Până azi cardul purta `c.coerenta`, care e NULL pe TOATE
// elementele, deci scria „neverificat" despre orice — inclusiv despre o declarație pe care
// validatorul o dăduse validă cu o clipă înainte.
function verdictInfo(c) {
  const v = (c && c.verdict_stare) || { stare: "lipsa" };
  const gata = !!(c && c.gata_de_depus);
  // [deficiența 323, 18.10.2026] declarația DEPĂȘITĂ nu e „respinsă de validator”: verdictul DUK poate fi „valid” pe XML-ul vechi, dar
  // cifrele lui nu mai sunt cele din evidență. Eticheta spune asta, nu „n-a trecut prin validator” / „validator: valid” ca refuz.
  if (c && c.depasita) {
    return { gata: false, depasita: true, clasa: "val-coer-atentie", text: "depășită — de generat din nou", lipsa: "", iesire: "" };
  }
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

// [perioada_declarata_v1] perioada DECLARATĂ (nu scadența), în cele trei forme din DS v2.85 cap.4: „08/2026” lunar, „T3/2026”
// trimestrial, „2026” anual (până la retestul 09.10 cardul cozii scria „trim. IV 2026” și „august 2026”). Fallback pe c.perioada
// (scadența) doar dacă payload-ul nu are an (intrări vechi).
function fmtPerioadaDecl(c) {
  const an = c.p_an, luna = c.p_luna, trim = c.p_trim;
  if (an && luna) return dataRo(`${an}-${String(luna).padStart(2, "0")}`, "luna_an_numeric"); // „08/2026”
  if (an && trim) return `T${trim}/${an}`;                                                        // „T3/2026”
  if (an) return String(an);
  return c.perioada || "—";
}

// [lotul 07.10 B, C12d] ultima acțiune a validatorului (respinge / validează), cu elementele ei: ecranul o CONFIRMĂ la redesenare.
// Din notificare, redesenarea venea cu `evidentiaza` = elementul tocmai respins, care nu mai e de validat — și ecranul spunea
// „nu mai așteaptă validarea: a fost deja validat sau respins”, ca despre altcineva. Acum spune ce ai făcut tu.
let _ultimaActiune = null;
// [Retest 2 pct.14] „Confirmarea respingerii repetă tot titlul notei.” Confirmarea numește nota SCURT: documentul (sau data), nu
// titlul întreg cu descrierea — titlul e deja pe card, deasupra.
function numeScurt(c) {
  const n = c.nota || {}, p = c.payload || {};
  const doc = (n.document_ref || p.document_ref || "").trim();
  const nr = (c.membri_ids || []).length;
  if (nr > 1) return `cele ${cate(nr, "notă", "note")} ale documentului${doc ? " " + doc : ""}`;
  const data = n.data || p.data;
  return doc ? `nota (${doc})` : (data ? `nota din ${dataRo(data)}` : "nota");
}
function _confirma(ids, text) { _ultimaActiune = { ids: ids.map(Number), text, la: Date.now() }; }

// [08.10.2026, U4] Titlul cozii = ce conține: „Note de validat”, „Declarații de validat”, „Declarații de depus” — părțile nevide,
// unite cu „ · ”; coada goală -> „Coada de validare și depunere” (fără dreptul «Poate depune»: „Coada de validare” — deficiența 266).
// [deficiența 313, comanda Costin 17.10.2026 7.2] titlul CARDULUI cozii — o singură regulă, pentru card (cabinet.js) și pentru fereastra
// deschisă din el: cardul trecea pe „De depus”, iar fereastra rămânea pe titlul de la deschidere („De validat”)
export function titluCardCoada({ patruOchi = false, note = 0 }) {
  return (patruOchi || note) ? "De validat" : "De depus";
}

export function titluCoada({ note = 0, deValidat = 0, deDepus = 0, poateDepune = true }) {
  const parti = [note ? "Note de validat" : "", deValidat ? "Declarații de validat" : "", deDepus ? "Declarații de depus" : ""].filter(Boolean);
  return parti.length ? parti.join(" · ") : (poateDepune ? "Coada de validare și depunere" : "Coada de validare");
}

// [deficiența 266, comanda Costin 15.10.2026] „coada de validare îi spune asistentului fără «Poate depune» că «Declarațiile le pregătești
// și le depui tu»; cardul promite «Declarații și note de validat», iar ecranul vorbește doar de declarații.” Textul de sub titlu urmează
// dreptul real — `poate_valida` / `poate_depune` din `/eu/permisiuni`, aceleași din care se aleg butoanele cardurilor — și vorbește întâi
// de note, apoi de declarații. Unde dreptul lipsește, spune cine face pasul, nu „tu”.
const CINE_VALIDEAZA = "un coleg care are dreptul «Poate valida»";
const CINE_DEPUNE = "un coleg care are dreptul «Poate depune»";
export function introCoada({ poateValida = false, poateDepune = false, admin = false, patruOchi = false, politica = false, note = 0 }) {
  // [deficiența 323, retestul 19.10.2026: „In De depus, textul de sus vorbește tot de «notele pe care asistenții le trimit la validare»”]
  // fără note de validat, textul nu vorbește deloc de note: spune numai ce e pe ecran — declarațiile
  const fraze = note
    ? [poateValida ? "Notele de mai sus le-au pregătit asistenții: le validezi sau le respingi."
      : `Notele de mai sus le-au pregătit asistenții: le validează sau le respinge ${CINE_VALIDEAZA}.`]
    : [];
  if (patruOchi) {
    fraze.push(poateValida
      ? (poateDepune ? "Declarațiile pregătite de asistenți așteaptă validarea ta înainte de depunere."
        : `Declarațiile pregătite de asistenți așteaptă validarea ta; după validare, le depune ${CINE_DEPUNE}.`)
      : (poateDepune ? `Declarațiile pregătite de asistenți le validează ${CINE_VALIDEAZA}; după validare, le depui tu.`
        : `Declarațiile pregătite de asistenți le validează ${CINE_VALIDEAZA} și le depune ${CINE_DEPUNE}.`));
    fraze.push("Nimic nu se depune nevalidat.");
  } else if (politica) {
    fraze.push((poateValida ? "Validarea în doi a declarațiilor e pornită, dar suspendată: ești singurul validator din cabinet."
      : "Validarea în doi a declarațiilor e pornită, dar suspendată: cabinetul are un singur validator.")
      + " Reintră în vigoare de îndată ce un coleg primește dreptul de validare" + (admin ? " (cardul Asistenți)." : "."));
    fraze.push(poateDepune ? "Până atunci, declarațiile le depui tu." : `Până atunci, declarațiile le depune ${CINE_DEPUNE}.`);
  } else {
    fraze.push(poateDepune ? "Declarațiile le depui tu — validarea în doi a declarațiilor nu e pornită."
      : `Declarațiile le depune ${CINE_DEPUNE} — validarea în doi a declarațiilor nu e pornită.`);
  }
  return fraze.join(" ");
}

export async function randeazaValidat(corp, nav, opt = {}) {   // [lotul 07.10 pct.8] opt.evidentiaza = id-ul din notificare
  // [265] drepturile schimbate în sesiunea deschisă: coada își alege butoanele și textele la desenare, deci se redesenează la semnalul
  // din drepturi.js; un singur ascultător pe fereastră, scos când fereastra s-a închis
  if (!corp.__laDrepturi) {
    corp.__laDrepturi = () => {
      if (!corp.isConnected) { window.removeEventListener("iconta:drepturi", corp.__laDrepturi); return; }
      randeazaValidat(corp, nav, { peLoc: true });
    };
    window.addEventListener("iconta:drepturi", corp.__laDrepturi);
  }
  // [292] titlul cardului se ține pe fereastră: redesenările de după o aprobare / respingere / drepturi nu-l mai primesc ca argument
  if (opt.titlu) corp.dataset.titluCard = opt.titlu;
  // `peLoc` (redesenarea la drepturi): coada rămâne pe ecran cât se citește, fără „Se încarcă” intermediar
  if (!opt.peLoc) corp.innerHTML = `<p class="ecran-nota">Se încarcă coada…</p>`;
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
    corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca coada.</p>`;
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
  // [deficiența 217, retestul Costin 09.10: „textul «validarea în doi nu e pornită» contrazice notele de validat de pe același ecran”]
  // validarea în doi privește DECLARAȚIILE; notele pregătite de asistenți se validează întotdeauna — textul o spune. [266] `introCoada`.
  const intro = introCoada({ poateValida: !!perm.poate_valida, poateDepune: !!perm.poate_depune,
                             admin: perm.rol === "admin_firma" || perm.rol === "superadmin",
                             patruOchi, politica: patruOchiPolitica, note: noteDeValidat.length });
  // [08.10.2026, decizia Costin U4] „Fereastra cu note de validat se numește «De depus». Titlul trebuie să spună ce conține.” Titlul
  // venea din cardul de pe desktop (calculat o dată, fără note), iar navigatorul îl punea ca <h2>. Acum ecranul își scrie titlul din
  // ce are în el: părțile nevide, în ordinea în care apar (`titluCoada`).
  // [deficiența 292, comanda Costin 16.10.2026, verbatim în DECIZII] „Titlul ferestrei urmează cardul din care a fost deschisă (rest din
  // 266; aceeași clasă cu 127).” Cardul își dă titlul (`opt.titlu`); fără card (din notificare) titlul spune ce conține (127, U4).
  if (corp.dataset.titluCard) corp.dataset.titluCard = titluCardCoada({ patruOchi, note: noteDeValidat.length });   // [313] urmează cardul
  const titlu = corp.dataset.titluCard || titluCoada({ note: noteDeValidat.length, deValidat: patruOchi ? laSenior.length : 0,
                             deDepus: patruOchi ? aprobate.length : declaratii.filter((c) => c.stare === "la_senior" || c.stare === "aprobata").length,
                             poateDepune: !!perm.poate_depune });
  corp.innerHTML = `
    <h2 class="pf-titlu" id="val-titlu">${esc(titlu)}</h2>
    <div id="val-note"></div>
    <p class="mig-intro">${intro}</p>
    <div id="val-deValidat"></div>
    <div id="val-deDepus"></div>
    <div id="val-nevalidate"></div>
    <div id="val-depasite"></div>
    <div class="mig-eroare" id="val-eroare"></div>
    <div id="val-ciorne"></div>
  `;
  ciorneleMele(corp.querySelector("#val-ciorne"), firme, nav, corp);
  const z1 = corp.querySelector("#val-deValidat");
  const z2 = corp.querySelector("#val-deDepus");
  const z3 = corp.querySelector("#val-nevalidate");

  const zN = corp.querySelector("#val-note");
  if (noteDeValidat.length) {
    zN.innerHTML = `<div class="cf-grup-titlu cf-galben">Note de validat (${noteDeValidat.length})</div>
      <p class="mig-intro">${perm.poate_valida
        ? "Notele pregătite de asistenți: le validezi (intră în evidență) sau le respingi cu motivul, pe care asistentul îl vede lângă notă."
        : `Notele pregătite de asistenți: le validează (intră în evidență) sau le respinge cu motivul ${CINE_VALIDEAZA}; asistentul vede motivul lângă notă.`} Notele aceleiași facturi (contarea și ieșirea din stoc) se validează împreună.</p>`;
    noteDeValidat.forEach((c) => zN.appendChild(randNota(c, firme, corp, nav, perm)));
    barMaiMulte(zN, corp, nav);
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
      // [266] coada goală spune ce n-a venit — note și declarații —, nu „nimic de depus” celui care nu depune
      z1.innerHTML = `<div class="stare-goala">Coada e goală: nicio notă contabilă și nicio declarație nu așteaptă acum.</div>`;
    }
    return;
  }

  // [R41 partea II] «gata de depus» vine de la server, per element. Nu se recalculează aici.
  const gata = (c) => !!c.gata_de_depus;
  // [deficiența 323, 18.10.2026] declarațiile DEPĂȘITE au grupul lor: nu sunt „nevalidate” (validatorul le poate da valide), ci
  // generate din documente care între timp s-au schimbat
  const depasite = [...laSenior, ...aprobate].filter((c) => !!c.depasita);
  const nedepasita = (c) => !c.depasita;
  const zD = corp.querySelector("#val-depasite");
  if (depasite.length) zD.appendChild(zonaDepasite(depasite, firme, corp, nav, perm, patruOchi));

  if (patruOchi) {
    // ── patru-ochi ACTIV: validare în doi ──
    const deValidat = laSenior.filter(nedepasita);
    if (deValidat.length) {
      z1.innerHTML = `<div class="cf-grup-titlu cf-galben">De validat (${deValidat.length})</div>`;
      deValidat.forEach((c) => z1.appendChild(randDeclaratie(c, firme, corp, nav, "valida", perm, patruOchi)));
    }
    const apGata = aprobate.filter(gata);
    const apNu = aprobate.filter((c) => !gata(c) && nedepasita(c));
    if (apGata.length) {
      z2.innerHTML = `<div class="cf-grup-titlu" style="color:var(--verde)">Aprobate, de depus (${apGata.length})</div>`;
      apGata.forEach((c) => z2.appendChild(randDeclaratie(c, firme, corp, nav, "depune", perm, patruOchi)));
    }
    if (apNu.length) z3.appendChild(zonaNevalidate(apNu, firme, corp, nav, perm, patruOchi, "Aprobate, dar nevalidate"));
  } else {
    // ── patru-ochi DEZACTIVAT: mono-utilizator, pregătește și depune singur ──
    const deDepus = [...laSenior, ...aprobate];
    const dGata = deDepus.filter(gata);
    const dNu = deDepus.filter((c) => !gata(c) && nedepasita(c));
    if (dGata.length) {
      z1.innerHTML = `<div class="cf-grup-titlu" style="color:var(--verde)">De depus (${dGata.length})</div>`;
      dGata.forEach((c) => z1.appendChild(randDeclaratie(c, firme, corp, nav, "depune", perm, patruOchi)));
    } else {
      // DS cap.6: gol + cauză + ieșire. Fundătura („Nimic de depus.") e interzisă, iar aici
      // golul are o cauză precisă — există lucrări, dar niciuna validată.
      // [323] cauza golului se spune după ce e de fapt mai jos: nevalidate (validatorul) și / sau depășite (de generat din nou)
      const cauze = [];
      if (dNu.length) cauze.push(`${cate(dNu.length, "declarație", "declarații")} ${dNu.length === 1 ? "e generată, dar n-a trecut" : "sunt generate, dar n-au trecut"} prin validatorul oficial — deschide-le mai jos: validatorul rulează și verdictul se păstrează`);
      if (depasite.length) cauze.push(`${cate(depasite.length, "declarație e depășită", "declarații sunt depășite")} — documentele perioadei s-au schimbat după generare; se generează din nou`);
      z1.innerHTML = `<div class="cf-grup-titlu" style="color:var(--verde)">De depus (0)</div>
        <div class="stare-goala">Nimic gata de depus.${cauze.length ? "<br>" + cauze.map((t) => esc(t) + ".").join("<br>") : ""}</div>`;
    }
    if (dNu.length) z2.appendChild(zonaNevalidate(dNu, firme, corp, nav, perm, patruOchi, "Generate, nevalidate"));
  }
}

// [08.10.2026, decizia Costin pct.3 la §6 S6] „Coada de validare permite validarea mai multor note deodată (Z-urile vin zilnic).”
// Bara apare numai când există note pe care le poți valida; serverul trece fiecare notă prin aceeași aprobare și spune ce a refuzat.
// [Retest 2 pct.12, comanda Costin 09.10.2026] „Ciornele proprii ale contabilului trebuie să fie vizibile undeva fără căutare.”
// La capătul ferestrei: notele tale încă în ciornă, pe firme, cu starea lor (trimisă la validare / respinsă cu motivul / netrimisă).
// [lotul 11, deficiența 457] „ciornele făcute de contabil nu ajung în nicio coadă (182 nerezolvată)”: lista era numai de citit, deci ciorna
// netrimisă (a celui care validează: n-o trimite nimeni în coadă) nu aștepta nicăieri unde să se lucreze. Acum lista e coada ta: pe rând,
// „Validează” (cine are dreptul; serverul aplică aceleași reguli ca în Registrul jurnal, iar refuzul stă sub rând), „Trimite la validare”
// (cine nu validează, pentru ciorna încă netrimisă) și „Deschide nota” (Registrul jurnal, pe luna notei, cu nota evidențiată).
async function ciorneleMele(zona, firme, nav, corp) {
  if (!zona) return;
  let r;
  try { r = await api.get("/eu/ciorne"); } catch (e) { arataMesaj(zona, "Nu s-au putut încărca notele tale în ciornă" + (e && e.mesaj ? " (" + e.mesaj + ")" : "") + ".", "eroare"); return; }
  if (!r || !r.total) return;
  const stare = (n) => n.in_coada === "la_senior" ? "trimisă la validare"
    : (n.in_coada === "respinsa" ? `respinsă${n.motiv_respingere ? ": " + n.motiv_respingere : ""}` : "nevalidată, netrimisă");
  const valideaza = permis("POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza");
  const actiuni = (f, n) => {
    const b = [];
    if (n.in_coada !== "la_senior" && valideaza)
      b.push(`<button class="buton-primar val-ciorna-valideaza" data-val-ciorna="${n.id}" data-tenant="${f.tenant_id}" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza">Validează</button>`);
    else if (!n.in_coada && !valideaza)
      b.push(`<button class="buton-secundar val-ciorna-trimite" data-trimite-ciorna="${n.id}" data-tenant="${f.tenant_id}" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/retrimite">Trimite la validare</button>`);
    b.push(`<button class="btn-link val-ciorna-deschide" data-deschide-ciorna="${n.id}" data-tenant="${f.tenant_id}">Deschide nota</button>`);
    return b.join(" ");
  };
  zona.innerHTML = `<div class="cf-grup-titlu">Notele tale în ciornă (${r.total})</div>
    <p class="mig-intro">Notele scrise de tine care nu sunt încă în evidență. ${valideaza ? "Le validezi de aici" : "Le trimiți la validare de aici"} sau din Registrul jurnal al firmei; acolo se și șterg.</p>
    ${r.firme.map((f) => `<div class="val-ciorne-firma">
      <div class="pf-frand-nume">${esc(f.firma)} <button class="btn-link" data-firma="${f.tenant_id}">Deschide firma</button></div>
      <ul class="sa-jurnal">${f.note.map((n) => `<li data-ciorna="${n.id}">${esc(dataRo(n.data))} · ${esc(n.descriere || "")} · ${rulajNota(n)} · ${esc(stare(n))} ${actiuni(f, n)}</li>`).join("")}</ul>
    </div>`).join("")}`;
  const nota = (b) => (r.firme.find((f) => String(f.tenant_id) === b.dataset.tenant) || { note: [] }).note
    .find((n) => String(n.id) === (b.dataset.valCiorna || b.dataset.trimiteCiorna || b.dataset.deschideCiorna)) || {};
  const numeNota = (n) => `nota din ${dataRo(n.data)}${n.descriere ? " („" + n.descriere + "”)" : ""}`;
  zona.querySelectorAll("[data-firma]").forEach((b) => b.addEventListener("click", () => {
    const t = firme.find((x) => String(x.id) === b.dataset.firma);
    if (t) deschideFirma(t, nav);
  }));
  const dupaAct = (text) => { _confirma([], text); if (corp) randeazaValidat(corp, nav); else ciorneleMele(zona, firme, nav, corp); };
  zona.querySelectorAll("[data-val-ciorna]").forEach((b) => b.addEventListener("click", async () => {
    const n = nota(b);
    b.disabled = true;
    try {
      await api.post(`/tenants/${b.dataset.tenant}/jurnal/${b.dataset.valCiorna}/valideaza`, {});
      dupaAct(`Ai validat ${numeNota(n)}: a intrat în evidență.`);
    } catch (e) { b.disabled = false; refuzPeRand(b, (e && e.mesaj) || "Nota nu s-a putut valida."); }
  }));
  zona.querySelectorAll("[data-trimite-ciorna]").forEach((b) => b.addEventListener("click", async () => {
    const n = nota(b);
    b.disabled = true;
    try {
      await api.post(`/tenants/${b.dataset.tenant}/jurnal/${b.dataset.trimiteCiorna}/retrimite`, {});
      dupaAct(`Ai trimis la validare ${numeNota(n)}.`);
    } catch (e) { b.disabled = false; refuzPeRand(b, (e && e.mesaj) || "Nota nu s-a putut trimite la validare."); }
  }));
  zona.querySelectorAll("[data-deschide-ciorna]").forEach((b) => b.addEventListener("click", () => {
    const n = nota(b);
    const t = firme.find((x) => String(x.id) === b.dataset.tenant);
    if (!n.data || !t) return;
    const [an, luna] = n.data.split("-").map((x) => parseInt(x, 10));
    nav.deschide(`Registru jurnal · ${t.nume}`, (c, nn) => ecranJurnal(c, nn, t, { evidentiaza: n.id, an, luna }), { lat: "tabel" });
  }));
}

function barMaiMulte(zN, corp, nav) {
  const bife = [...zN.querySelectorAll(".val-sel")];
  if (bife.length < 2) return;
  const bara = document.createElement("div");
  bara.className = "dec-bara";
  bara.innerHTML = `<label class="set-bifa"><input type="checkbox" id="val-sel-toate"> <span>Selectează toate (${bife.length})</span></label>
    <button class="buton-primar" id="val-aproba-selectate" data-actiune="POST /coada/aproba-mai-multe" disabled>Validează selectate</button>
    <div id="val-mai-multe-msg"></div>`;
  zN.insertBefore(bara, zN.querySelector(".val-card"));
  const btn = bara.querySelector("#val-aproba-selectate"), toate = bara.querySelector("#val-sel-toate");
  const alese = () => bife.filter((b) => b.checked).map((b) => Number(b.dataset.nota));
  const actualizeaza = () => { const n = alese().length; btn.disabled = !n; btn.textContent = n ? `Validează selectate (${n})` : "Validează selectate"; };
  bife.forEach((b) => b.addEventListener("change", actualizeaza));
  toate.addEventListener("change", () => { bife.forEach((b) => { b.checked = toate.checked; }); actualizeaza(); });
  btn.addEventListener("click", async () => {
    const ids = alese();
    btn.disabled = true;
    try {
      const r = await api.post("/coada/aproba-mai-multe", { ids });
      const refuz = r.refuzate || [];
      _confirma(r.validate || [], `Ai validat ${cate((r.validate || []).length, "notă", "note")}.`
        + (refuz.length ? ` Nu s-au validat ${refuz.length}: ${refuz.map((x) => x.mesaj).join(" · ")}` : ""));
      randeazaValidat(corp, nav);
    } catch (e) {
      arataMesaj(bara.querySelector("#val-mai-multe-msg"), (e && e.mesaj) || "Nu s-au putut valida notele selectate.", "eroare");
      actualizeaza();
    }
  });
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
  let actiuni = "", selectabila = false;
  if (!perm.poate_valida) {
    actiuni = `<span class="val-nota-perm">nu ai dreptul de validare</span>`;
  } else if (euAmPregatit) {
    actiuni = `<span class="val-nota-perm">ai pregătit-o tu — o validează altcineva</span>`;
  } else {
    actiuni = `<button class="buton-primar val-btn val-aproba" data-act="valideaza-nota" data-actiune="POST /coada/{coada_id}/aproba">Validează</button>
      <button class="buton-sters val-btn val-respinge" data-act="respinge-nota" data-actiune="POST /coada/{coada_id}/respinge">Respinge</button>`;
    selectabila = true;
  }
  div.innerHTML = `
    <div class="val-info">
      <div class="val-titlu">${selectabila ? `<input type="checkbox" class="val-sel" data-nota="${c.id}" aria-label="Selectează ${esc(c.eticheta || "nota")}" data-actiune="POST /coada/aproba-mai-multe"> ` : ""}<b>${esc(c.eticheta || "Notă")}</b></div>
      <div class="val-sub">${esc(numeFirma(firme, c.tenant_id))} · pregătită de ${esc(c.creat_de_nume || c.creat_de || "—")}</div>
      ${c.retrimisa ? `<div class="val-sub">Retrimisă după respingere · motivul anterior: „${esc(c.retrimisa.motiv_respingere || "fără motiv")}” · ${c.retrimisa.schimbata === true ? "nota s-a schimbat față de cea respinsă" : c.retrimisa.schimbata === false ? "nota nu s-a schimbat față de cea respinsă" : "nu se poate spune dacă nota s-a schimbat: cea respinsă e mai veche decât compararea notelor"}</div>` : ""}
      <div class="val-termen">${n.data ? esc(dataRo(n.data)) : ""} · ${rulajNota(n)}${n.document_ref ? "" : " · fără document justificativ"}${n.stinge ? " · stinge " + esc(n.stinge) : ""}</div>
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
      eticheta: `Motivul respingerii pentru ${esc(numeScurt(c))}:`,   // [Retest 2 pct.14] nota numită scurt, titlul e deja pe card
      placeholder: "ex: lipsește factura; contul de cheltuială e greșit",
      // [lotul 07.10 B, C12e] butonul de confirmare arată ca butonul care l-a deschis (roșu plin), nu roz-pal „dezactivat”
      obligatoriu: true, buton: "Respinge", butonClasa: "buton-sters val-respinge",
      onConfirm: async (motiv) => {
        await api.post(`/coada/${c.id}/respinge`, { motiv });
        _confirma(c.membri_ids || [c.id], `Ai respins ${numeScurt(c)}. Motivul („${motiv}”) apare lângă notă la cel care a pregătit-o.`);
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
        _confirma(c.membri_ids || [c.id], `Ai validat ${numeScurt(c)}: a intrat în evidență.`);
        if (dinDetaliu) nav.inapoi();
        randeazaValidat(corpLista, nav);
      }
      catch (e) {
        if (eroare) { arataMesaj(eroare, (e && e.mesaj) || "Eroare la validare.", "eroare"); ofertaRefacere(eroare, c, corpLista, nav); }
      }
    };
    // [386, lotul 9] ca în Registrul-jurnal: regula de fond R3 din bază refuză validarea fără document justificativ — caseta spune de ce
    // și duce la pasul posibil (respingerea cu motivul, ca cel care a pregătit nota să scrie referința)
    if (!n.document_ref) {
      confirmaCaseta(btn.parentElement || btn, "Nota nu are document justificativ, iar o notă nu se validează fără documentul din care provine (Registrul-jurnal, col.3: felul, numărul și data). Respinge-o cu motivul, ca cel care a pregătit-o să scrie referința.",
        () => { const r = zona.querySelector(".val-respinge"); if (r) r.click(); }, { textOk: "Respinge nota" });
      return;
    }
    valideaza();
  });
}

// [lotul 11, deficiența 451] „ciornele generate înainte de o reparație rămân validabile cu regula veche” — serverul refuză validarea
// ciornei DEPĂȘITE (regenerată pe uscat din sursa ei, dă altă notă). Sub refuz, refacerea din sursă, ca în Registrul jurnal: aceeași
// verificare (`GET …/jurnal/{nota_id}/depasita`), aceeași refacere (`POST …/reface`). Butonul stă SUB mesaj (DS cap.5, `.caseta-atentie`).
async function ofertaRefacere(zona, c, corpLista, nav) {
  const p0 = c.nota || {};
  const ids = (p0.note || [p0]).map((p) => p && p.inregistrare_id).filter(Boolean);
  for (const nid of ids) {
    let d = null;
    try { d = await api.get(`/tenants/${c.tenant_id}/jurnal/${nid}/depasita`); } catch { d = null; }
    if (!d || !d.depasita || !d.refacere) continue;
    const p = document.createElement("p");
    p.style.marginTop = "6px";
    p.innerHTML = `<button class="buton-secundar val-reface" data-actiune="POST /tenants/{tenant_id}/jurnal/{nota_id}/reface">${esc(d.refacere.eticheta)}</button>`;
    zona.appendChild(p);
    p.querySelector(".val-reface").addEventListener("click", async (ev) => {
      const b = ev.currentTarget;
      b.disabled = true;
      try {
        const r = await api.post(`/tenants/${c.tenant_id}/jurnal/${nid}/reface`, {});
        _confirma([], `${r.mesaj} O găsești în Registrul jurnal al firmei.`);
        randeazaValidat(corpLista, nav);
      } catch (e) { b.disabled = false; arataMesaj(zona, (e && e.mesaj) || "Nota nu s-a putut reface din sursă.", "eroare"); }
    });
  }
}

async function deschideNota(c, nav, ctx = {}) {
  nav.deschide(c.eticheta || "Notă", async (corp) => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă nota…</p>`;
    let d;
    try { d = await api.get(`/coada/${c.id}/continut`); }
    catch (e) { corp.innerHTML = `<div class="dec-eroare">${esc((e && e.mesaj) || "Nu s-a putut încărca nota.")}</div>`; return; }
    // [lotul 07.10 pct.9] un document cu mai multe note (contarea + ieșirea din stoc a aceleiași facturi): toate, una sub alta
    const note = d.note || [{ nota: d.nota || {}, linii: d.linii || [] }];
    corp.innerHTML = note.map(({ nota: n, linii }) => `
      <div class="rezumat-fix"><p class="mig-intro">Nota ${esc(n.eticheta || "")} · ${esc(dataRo(n.data))} · ${esc(n.descriere || "")} · ${n.document_ref ? "document: " + esc(n.document_ref) : "fără document justificativ"}${n.stinge ? " · stinge " + esc(n.stinge) : ""}</p></div>   <!-- [lotul 10, 421 / 424, DS cap.9 v2.97 pct.5] antetul notei rămâne sus -->
      <table class="fd-tabel"><thead><tr><th>Debit</th><th>Credit</th><th>Sumă</th></tr></thead>
        <tbody>${(linii || []).map((l) => `<tr><td>${esc(l.debit)}</td><td>${esc(l.credit)}</td><td>${bani(l.suma)}</td></tr>`).join("")}</tbody>
      </table>`).join("") + (ctx.actiuni   // [lotul 10, 421 / 424, DS cap.9 v2.96] „acțiunea principală fix jos”: validarea și refuzul ei, lipite jos
      ? `<div class="bara-fixa"><div class="val-actiuni" id="val-nota-actiuni" style="margin-top:12px">${ctx.actiuni}</div><div id="val-nota-eroare"></div></div>`
      : "");
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

// [deficiența 323, 18.10.2026] grupul declarațiilor depășite: nici aprobare, nici depunere — se generează din nou (serverul refuză la fel,
// `coada_api.refuz_depasita`). Nota grupului nu e cea a celor nevalidate („se poate trece peste refuz” nu e adevărat aici).
function zonaDepasite(lista, firme, corp, nav, perm, patruOchi) {
  const frag = document.createDocumentFragment();
  const cap = document.createElement("div");
  cap.className = "cf-grup-titlu cf-galben";
  cap.textContent = `Depășite — de generat din nou (${lista.length})`;
  frag.appendChild(cap);
  const nota = document.createElement("p");
  nota.className = "ecran-nota";
  nota.textContent = "Documentele perioadei s-au schimbat după generare, deci cifrele lor nu mai sunt cele din evidență. Nu se aprobă și nu se depun; se generează din nou.";
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
      corp.innerHTML = `<div class="dec-eroare">Nu s-a putut \u00eencarca con\u021binutul: ${esc((e && e.mesaj) || "eroare")}</div>`;
      return;
    }
    const xml = d.xml_b64 ? (function(){ try { return decodeURIComponent(escape(atob(d.xml_b64))); } catch(e){ return ""; } })() : "";
    const stare = d.stare || "gri";
    const duk = stare === "valid"
      ? `<div class="dec-ok">Validat cu DUKIntegrator (validatorul oficial ANAF, rulat local), f\u0103r\u0103 erori.</div>`
      : (stare === "erori"
          ? `<div class="dec-eroare"><div class="dec-avert-cap">DUKIntegrator (validatorul ANAF, local) a g\u0103sit ${d.severitate === "atentionare" ? "aten\u021bion\u0103ri" : "erori"}</div><pre class="dec-xml-pre">${esc(d.erori || "")}</pre></div>`
          : `<div class="dec-avert"><div class="dec-avert-cap">Nu s-a putut valida cu DUKIntegrator</div><ul><li>${esc(d.temei || "")}</li><li>${esc(d.limita || "")}</li></ul></div>`);
    const av = d.avertismente || [];
    const avert = av.length
      ? `<div class="caseta-atentie"><b>Avertismente (${av.length})</b><ul>${av.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></div>`
      : "";
    // [deficiența 323, 18.10.2026] fereastra spune „depășită”, cu motivul, înaintea verdictului (verdictul e al XML-ului vechi)
    const depasita = d.depasita ? `<div class="caseta-atentie val-depasita"><b>Depășită</b> — ${esc(d.depasita.mesaj)}</div>` : "";
    corp.innerHTML = `
      <p class="mig-intro">Con\u021binutul declara\u021biei \u2014 vizualizare pentru validare; numai pentru citire.</p>
      ${depasita}
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

  // [383, lotul 9] perioada neîncheiată se spune pe rând, în orice stare (la validare și la depunere); butonul de depunere nu se oferă
  // [lotul 10, 436] la fel declarația care știe că cifra ei nu cuprinde note nevalidate (`blocaj_depunere` = perioada sau notele, serverul)
  let actiuni = c.blocaj_depunere
    ? `<span class="val-nota-perm ${c.perioada_neincheiata ? "val-neincheiata" : "val-blocaj-note"}">${esc(c.blocaj_depunere)}</span>` : "";
  // [deficiența 297] declarația DEPĂȘITĂ (documentele perioadei s-au schimbat după generare): nici aprobare, nici depunere — se generează
  // din nou; serverul refuză la fel (`coada_api.refuz_depasita`)
  const dep = c.depasita;
  if (dep) {
    // [deficiența 324, 18.10.2026] „Generează din nou” numai unde serverul îl poate face (cererea păstrată, `se_poate_regenera`); o
    // declarație intrată în coadă înainte de 17.10.2026 se generează din Declarații — butonul duce acolo, cu firma, tipul și perioada
    actiuni += perm.poate_pregati === false
      ? `<span class="val-nota-perm">o generează din nou cine are dreptul «Poate pregăti»</span>`
      : c.se_poate_regenera
        ? `<button class="buton-primar val-btn val-regenereaza" data-act="regenereaza" data-actiune="POST /coada/{coada_id}/regenereaza">Generează din nou</button>`
        : `<button class="buton-primar val-btn val-din-declaratii" data-act="din_declaratii" data-fara-actiune="navigare la Declarații; generarea de acolo poartă acțiunea">Generează din Declarații</button>`;
  } else if (mod === "valida") {
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
    if (c.blocaj_depunere) {
      // [383, lotul 9] „O declarație nu se oferă spre depunere înainte de încheierea perioadei.” (serverul refuză și el; motivul e pe rând)
      // [lotul 10, 436] „depunerea se blochează până la validare, cu motivul lângă buton” — notele nevalidate, la fel
    } else if (!potDepune) {
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
    // Cu patru-ochi OFF, mono-utilizatorul poate renunța la un item încă neaprobat (respinge din la_senior).
    // [deficiența 293, comanda Costin 16.10.2026] „Pe o declarație a altcuiva, fără dreptul de depunere, nu se oferă nicio acțiune în afară
    // de vizualizare; serverul refuză la fel.” Renunțarea e a celui care a pregătit-o sau a celui care o depune (`uc_coada.coada_respinge`).
  }
  // [deficiența 313] fără validarea în doi, „Renunță” pe PROPRIA declarație e retragerea ei — fără „Respinge declarația” cu motiv obligatoriu
  if (!patruOchi && c.stare === "la_senior" && perm.poate_valida && (euAmPregatit || perm.poate_depune)) {
    const actRetragere = euAmPregatit ? "renunta" : "respinge";   // cheia acțiunii, nu text pe ecran
    actiuni += `<button class="buton-sters val-btn val-respinge" data-act="${actRetragere}" data-actiune="POST /coada/{coada_id}/respinge">Renunță</button>`;
  }

  const perDecl = fmtPerioadaDecl(c);
  div.innerHTML = `
    <div class="val-info">
      <div class="val-titlu"><b>${(c.tip||"").toUpperCase()}</b> · ${perDecl}</div>
      <div class="val-sub">${esc(numeFirma(firme, c.tenant_id))} · pregătit de ${esc(c.creat_de_nume || c.creat_de || "—")}</div>
      <div class="val-termen">termen (scadență): ${c.perioada || "—"}</div>
      ${dep ? `<div class="val-lipsa val-depasita">${esc(dep.mesaj)}</div>`
        : vi.gata ? "" : `<div class="val-lipsa">${esc(vi.lipsa)} <span class="val-lipsa-iesire">${esc(vi.iesire)}</span></div>`}
      ${c.surse_nevalidate ? `<div class="val-lipsa val-surse">${esc((c.surse_note || []).length && c.surse_nevalidate_langa_note ? c.surse_nevalidate_langa_note : c.surse_nevalidate)}</div><div class="val-surse-note"></div>` : ""}  <!-- [lotul 11, 436] lângă butoanele notelor, fraza fără lista lor -->
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
  // [298 + 313] notele nevalidate pe care se sprijină declarația, fiecare cu butonul ei spre Registrul jurnal
  const zSurse = div.querySelector(".val-surse-note");
  if (zSurse && (c.surse_note || []).length) import("./coada_trimite.js?v=c05f894cb8").then((m) => m.legaturiNote(zSurse, c.tenant_id, c.surse_note));
  return div;
}

async function actioneaza(c, act, firme, corp, nav) {
  const eroare = corp.querySelector("#val-eroare");
  if (eroare) eroare.textContent = "";
  const perDecl = fmtPerioadaDecl(c);
  if (act === "din_declaratii") {
    // [324] declarația veche n-are cererea păstrată: Declarații, cu firma, tipul și perioada ei; „Înlocuiește” scoate elementul vechi
    const { randeazaDeclaratii } = await import("./declaratii.js?v=f65bf1fdb3");
    nav.deschide("Declarații", (c2) => randeazaDeclaratii(c2, nav, null, { tenant_id: c.tenant_id, tip: c.tip, an: c.p_an, luna: c.p_luna, trim: c.p_trim }),
                 { lat: "tabel" });
    return;
  }
  if (act === "regenereaza") {
    try {
      const r = await api.post(`/coada/${c.id}/regenereaza`, {});
      _confirma([r.coada_id], `${(c.tip || "").toUpperCase()} (${perDecl}) s-a generat din nou din documentele de acum; cea veche a ieșit din coadă.`);
      randeazaValidat(corp, nav);
    } catch (e) {
      if (eroare) arataMesaj(eroare, (e && e.mesaj) || "Declarația nu s-a putut genera din nou.", "eroare");
    }
    return;
  }
  if (act === "renunta") {
    dialogInput(nav, {
      titlu: "Renunți la declarație",
      eticheta: `Retragi din coadă ${(c.tip||"").toUpperCase()} (${perDecl}), pregătită de tine. Motivul — opțional:`,
      placeholder: "ex: o generez din nou după ce validez nota",
      obligatoriu: false,
      buton: "Renunță la declarație",
      butonClasa: "buton-sters val-respinge",
      onConfirm: async (motiv) => {
        await api.post(`/coada/${c.id}/respinge`, { motiv: motiv || "" });
        _confirma([c.id], `Ai retras din coadă ${(c.tip || "").toUpperCase()} (${perDecl}).`);
        nav.inapoi();
        randeazaValidat(corp, nav);
      },
    });
    return;
  }
  if (act === "respinge") {
    dialogInput(nav, {
      titlu: "Respinge declarația",
      eticheta: `Motivul respingerii pentru ${(c.tip||"").toUpperCase()} (${perDecl}):`,
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
    ? ` ${n === 1 ? "O constatare certă a fost confirmată" : cate(n, "constatare certă", "constatări certe") + " au fost confirmate"}`
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
        <div class="ca-mesaj pe-randuri">${esc(detaliu.mesaj || "")}</div>
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
          : `${cate(goale.length, "constatare", "constatări")} n-au motiv scris.`;
        focusFaraSalt(goale[0]);
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
        arataMesaj(er, (e && e.mesaj) || "Nu s-a putut depune. Încearcă din nou.", "eroare");
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
    focusFaraSalt(input);
    const confirma = async () => {
      const val = input.value.trim();
      if (opt.obligatoriu && !val) {
        er.textContent = "Câmpul e obligatoriu.";
        focusFaraSalt(input);
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
