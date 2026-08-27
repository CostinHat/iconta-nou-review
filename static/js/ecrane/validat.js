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
import { api, dataRo, esc } from "../api.js?v=c20d0584e2";
import { sesiune } from "../sesiune.js?v=5d142951c9";

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
  if (v.stare === "proaspat") {
    // verdict proaspăt, dar nefavorabil: validatorul a rulat pe conținutul ăsta și a respins
    return { gata: false, clasa: "val-coer-rau",
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

export async function randeazaValidat(corp, nav) {
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
  const laSenior = coada.filter((c) => c.stare === "la_senior");
  const aprobate = coada.filter((c) => c.stare === "aprobata");

  // [po_efectiv_v1] TREI texte, nu doua: „oprit" si „suspendat" nu sunt acelasi lucru. Pe un cabinet
  // solo cu politica PORNITA, „Patru-ochi e dezactivat" contrazicea indicatorul din subbara
  // („suspendata") si il lasa pe patron sa creada ca i s-a stins setarea. Politica persista; ce
  // lipseste e al doilea validator - si se spune, cu iesirea (DS cap.6, stare goala: gol + cauza + iesire).
  const intro = patruOchi
    ? "Declarațiile pregătite de asistenți așteaptă validarea ta înainte de depunere. Nimic nu se depune nevalidat."
    : (patruOchiPolitica
      ? "Validarea în doi e pornită, dar suspendată: ești singurul validator din cabinet, așa că pregătești și depui singur. Reintră în vigoare de îndată ce un coleg primește dreptul de validare (cardul Asistenți)."
      : "Patru-ochi e dezactivat: pregătești și depui singur. Declarațiile din coadă așteaptă depunerea.");
  corp.innerHTML = `
    <p class="mig-intro">${intro}</p>
    <div id="val-deValidat"></div>
    <div id="val-deDepus"></div>
    <div id="val-nevalidate"></div>
    <div class="mig-eroare" id="val-eroare"></div>
  `;
  const z1 = corp.querySelector("#val-deValidat");
  const z2 = corp.querySelector("#val-deDepus");
  const z3 = corp.querySelector("#val-nevalidate");

  if (laSenior.length === 0 && aprobate.length === 0) {
    z1.innerHTML = `<div class="stare-goala">${patruOchi ? "Nimic de validat. Coada e goală." : "Nimic de depus. Coada e goală."}</div>`;
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
      actiuni += `<button class="buton-primar val-btn val-aproba" data-act="aproba">Aprobă</button>`;
    }
    // Respinge — oricine cu drept de validare (și care n-a pregătit-o, când patru-ochi e activ)
    if (perm.poate_valida && !euAmPregatit) {
      actiuni += `<button class="buton-sters val-btn val-respinge" data-act="respinge">Respinge</button>`;
    }
  } else {
    // depune -> "Confirmă depunerea". Cu patru-ochi OFF, un item la_senior se aprobă automat înainte de depunere.
    const needsAproba = c.stare === "la_senior";
    const potDepune = perm.poate_depune && (!needsAproba || perm.poate_valida);
    if (!potDepune) {
      actiuni += `<span class="val-nota-perm">nu ai dreptul de depunere</span>`;
    } else if (vi.gata) {
      actiuni += `<button class="buton-primar val-btn val-depune" data-act="depune">Confirmă depunerea</button>`;
    } else {
      // [R41 partea II] Nu e gata: acțiunea principală devine cea care REPARĂ (deschide, ca
      // validatorul să ruleze și verdictul să se păstreze). Depunerea rămâne posibilă, dar
      // explicită și consemnată — nu ascunsă, fiindcă un blocaj fără cale de trecere pentru om
      // e interdicția 47.
      actiuni += `<button class="val-btn val-valideaza" data-act="vezi">Deschide ca să fie validat</button>`;
      actiuni += `<button class="val-btn val-trece" data-act="trece">Depune totuși…</button>`;
    }
    // Cu patru-ochi OFF, mono-utilizatorul poate renunța la un item încă neaprobat (respinge din la_senior)
    if (!patruOchi && needsAproba && perm.poate_valida) {
      actiuni += `<button class="buton-sters val-btn val-respinge" data-act="respinge">Renunță</button>`;
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
      butonClasa: "val-respinge",
      onConfirm: async (motiv) => {
        await api.post(`/coada/${c.id}/respinge`, { motiv });
        nav.inapoi();
        randeazaValidat(corp, nav);
      },
    });
    return;
  }
  if (act === "trece") {
    // [R41 partea II] Trecerea peste refuz: motiv OBLIGATORIU, consemnat cu cine și când.
    dialogInput(nav, {
      titlu: "Depune fără verdict de validare",
      eticheta: `${(c.tip||"").toUpperCase()} (${perDecl}) nu are verdict valid de la DUKIntegrator. De ce o depui totuși?`,
      placeholder: "ex: validatorul nu pornește, iar termenul e azi",
      obligatoriu: true,
      buton: "Depune, cu motivul de mai sus",
      butonClasa: "val-trece",
      onConfirm: async (motiv) => {
        if (c.stare === "la_senior") {
          await api.post(`/coada/${c.id}/aproba`, { motiv_trecere: motiv });
        }
        await api.post(`/coada/${c.id}/depune`, { motiv_trecere: motiv });
        nav.inapoi();
        randeazaValidat(corp, nav);
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
      onConfirm: async (spv) => {
        // Cu patru-ochi OFF, un item încă „la_senior" se aprobă automat înainte de depunere
        // (aceeași auto-aprobare pe care backendul o permite când patru-ochi e oprit).
        if (c.stare === "la_senior") {
          await api.post(`/coada/${c.id}/aproba`, {});
        }
        await api.post(`/coada/${c.id}/depune`, spv ? { spv_index: spv } : {});
        nav.inapoi();
        randeazaValidat(corp, nav);
      },
    });
    return;
  }
  // aproba — fara dialog, direct
  try {
    await api.post(`/coada/${c.id}/aproba`, {});
    randeazaValidat(corp, nav);
  } catch (e) {
    if (eroare) eroare.textContent = (e && e.mesaj) || "Eroare la aprobare.";
  }
}

// dialog modal cu un input (foloseste fereastra standard nav.deschide)
function dialogInput(nav, opt) {
  nav.deschide(opt.titlu, (corp) => {
    corp.innerHTML = `
      <label class="dlg-eticheta">${opt.eticheta}</label>
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
        await opt.onConfirm(val);
      } catch (e) {
        btn.disabled = false;
        er.textContent = (e && e.mesaj) || "Eroare. Încearcă din nou.";
      }
    };
    corp.querySelector("#dlg-ok").addEventListener("click", confirma);
    corp.querySelector("#dlg-anuleaza").addEventListener("click", () => nav.inapoi());
    input.addEventListener("keydown", (ev) => { if (ev.key === "Enter") confirma(); });
  });
}
