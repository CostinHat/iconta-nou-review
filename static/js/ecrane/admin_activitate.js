// admin_activitate.js — Admin iConta: activitate + business cabinete (doar superadmin).
// Sumar + lista cu firme/utilizatori/recomandari/actiuni, suspenda/reactiveaza, „Fișa” -> fereastra cabinetului.
import { api, dataRo, confirmaCaseta, esc, cate, arataMesaj, arataRefuzul } from "../api.js?v=c6c45aefe4";  /* audit_cab_lot2_v1 + esc_nc27 */

// [lotul 13, deficiența 645 — anexa comenzii 13.1, decizia Costin + arhitect 24.10.2026, verbatim: „motiv obligatoriu din listă fixă —
// neplată, la cererea cabinetului, încălcarea termenilor, acces suspect / securitate, la cererea unei autorități — plus notă internă
// opțională. […] nota internă nu se arată. […] Email către administratorul cabinetului la suspendare, cu același motiv. Cine, când, motivul
// și reactivarea rămân în jurnal.”] Cheile sunt ale serverului (`core/uc_admin.MOTIVE_SUSPENDARE`, CHECK-ul din bază); serverul refuză
// orice altă valoare. Cinci opțiuni -> butoane alăturate, nimic ales din oficiu (clasa 676: lista scurtă nu e listă derulantă).
export const MOTIVE_SUSPENDARE = [
  ["neplata", "Neplată"],
  ["cerere_cabinet", "La cererea cabinetului"],
  ["incalcare_termeni", "Încălcarea termenilor"],
  ["securitate", "Acces suspect / securitate"],
  ["autoritate", "La cererea unei autorități"],
];

// confirmarea suspendării, arătată de lista redesenată după închiderea ferestrei de suspendare (`nav.inapoi` o redesenează)
let _mesajUrmator = null;

export async function randeazaAdminActivitate(corp, nav) {
  const f = corp.closest(".fereastra");
  if (f) f.classList.add("fer-larg-simplu");
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  const m = _mesajUrmator;
  _mesajUrmator = null;
  await randeaza(corp, nav, m);
}

// [lotul 13, 644 b] „«Angajați» în bară și pe cabinet înseamnă conturile de utilizator, nu salariați: eticheta devine «utilizatori».”
function cifreCabinet(c) {
  return `${cate(c.nr_firme ?? 0, "firmă", "firme")} · ${cate(c.nr_utilizatori ?? 0, "utilizator", "utilizatori")} · ${cate(c.nr_facturi ?? 0, "factură emisă", "facturi emise")} · ${cate(c.nr_declaratii ?? 0, "declarație depusă", "declarații depuse")} · ${cate(c.nr_recomandari ?? 0, "recomandare", "recomandări")}`;
}

function stareSuspendare(c) {
  if (c.activ) return "";
  const motiv = c.motiv_suspendare ? `· motivul: ${esc(c.motiv_suspendare)}` : "· motivul nu s-a înregistrat";
  const din = c.suspendat_la ? ` · din ${dataRo(c.suspendat_la, "cu_ora")}` : "";
  return `<div class="pf-frand-sub ac-suspendat">Suspendat ${motiv}${din}</div>`;
}

async function randeaza(corp, nav, mesajOk) {
  if (nav && nav.setInapoi) nav.setInapoi(undefined);
  let cabinete = [];
  try {
    const r = await api.get("/admin/activitate/cabinete");
    cabinete = (r && r.cabinete) || [];
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu s-a putut încărca activitatea.</p>`;
    return;
  }
  if (!cabinete.length) {
    corp.innerHTML = `
      <h2 class="pf-titlu">Cabinete</h2>
      <div class="stare-goala">Niciun cabinet încă. Apar automat aici când se înregistrează primul (self-service).</div>`;
    return;
  }

  // [lotul 13, 674 / 675] fiecare rând are aceleași două butoane, în aceeași ordine: „Fișa” (fereastră nouă — 673) și „Suspendă” /
  // „Reactivează”; textul rândului nu mai e o acțiune pe care se dă clic
  const randuri = cabinete.map((c, i) => {
    const stare = (c.activ ? "" : `<span class="mig-stare mig-rosu">suspendat</span>`)
      + (c.de_test ? `<span class="mig-stare mig-gri" title="Cabinet de test: alerta de acces anormal nu-l semnalează">de test</span>` : "");   // [715.1, 14.3]
    const cls = c.activ ? "buton-sters" : "buton-secundar";   // Suspendă (ștergere de acces) / Reactivează
    return `
      <div class="pf-frand" data-zebra="${i % 2}" data-cabinet="${c.id}">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(c.nume || "—")}</div>
          <div class="pf-frand-sub">${cifreCabinet(c)} · ultima activitate: ${dataRo(c.ultima_activitate, "cu_ora")}${c.creat_la ? ` · creat: ${dataRo(c.creat_la, "cu_ora")}${c.cale ? ` (${esc(c.cale)})` : ""}` : ""}</div>
          ${stareSuspendare(c)}
        </div>
        ${stare}
        <button class="buton-secundar" data-fisa="${i}" style="margin-left:10px" data-fara-actiune="deschide fișa cabinetului (citire)">Fișa</button>
        <button class="buton-secundar" data-de-test="${i}" style="margin-left:8px" data-actiune="POST /admin/cabinete/{firm_id}/de-test">${c.de_test ? "Scoate marcajul de test" : "Marchează ca test"}</button>
        <button class="${cls}" data-toggle="${i}" style="margin-left:8px"
          data-actiune="${c.activ ? "POST /admin/cabinete/{firm_id}/suspenda" : "POST /admin/cabinete/{firm_id}/reactiveaza"}">${c.activ ? "Suspendă" : "Reactivează"}</button>
      </div>`;
  }).join("");

  corp.innerHTML = `
    <h2 class="pf-titlu">Cabinete</h2>
    <div class="rezumat-fix">
      <label class="camp" style="max-width:340px;margin-bottom:10px"><span class="camp-eticheta">Caută cabinet</span><input type="text" id="ac-cauta" class="camp-input" placeholder="nume cabinet"></label>
      <div id="ac-mesaj"></div>
    </div>
    <div class="pf-lista zebra-lista" id="ac-lista" data-zona-derulare>${randuri}</div>
  `;
  if (mesajOk) arataMesaj(corp.querySelector("#ac-mesaj"), mesajOk, "ok");

  corp.querySelector("#ac-cauta").addEventListener("input", (e) => {  // [ac_cauta] filtrare live
    const q = e.target.value.trim().toLowerCase();
    corp.querySelectorAll("#ac-lista .pf-frand").forEach((rand, i) => {
      rand.style.display = !q || (cabinete[i].nume || "").toLowerCase().includes(q) ? "" : "none";
    });
  });
  // [lotul 13, 673] fișa cabinetului e o acțiune din fereastră: fereastră nouă, nu un bloc desfăcut sub listă
  corp.querySelectorAll("#ac-lista [data-fisa]").forEach((b) => b.addEventListener("click", () => {
    const c = cabinete[Number(b.dataset.fisa)];
    nav.deschide(`Fișa cabinetului ${c.nume || ""}`, (corpF) => deschideFisa(corpF, c), { lat: "larg" });
  }));

  // [715.1, comanda 14.3] marcajul „cabinet de test”: excepția alertei de acces urmează marcajul, nu numele cabinetului
  corp.querySelectorAll("#ac-lista [data-de-test]").forEach((btn) => btn.addEventListener("click", (ev) => {
    ev.stopPropagation();
    const c = cabinete[Number(btn.dataset.deTest)];
    const nou = !c.de_test;
    confirmaCaseta(btn.parentElement || btn, nou
      ? `Marchezi „${esc(c.nume)}” ca cabinet de test? Alerta de acces anormal nu-l va mai semnala.`
      : `Scoți marcajul de test de la „${esc(c.nume)}”? Alerta de acces anormal îl va semnala din nou.`, async () => {
      try {
        await api.post(`/admin/cabinete/${c.id}/de-test`, { de_test: nou });
        corp.innerHTML = `<p class="ecran-nota">Se actualizează...</p>`;
        await randeaza(corp, nav, nou ? `Cabinetul „${c.nume}” e marcat ca test.` : `Marcajul de test a fost scos de la „${c.nume}”.`);
      } catch (e) {
        arataMesaj(corp.querySelector("#ac-mesaj"), (e && e.mesaj) || "Marcajul nu s-a putut schimba.", "eroare");
      }
    }, { textOk: nou ? "Marchează" : "Scoate marcajul" });
  }));
  corp.querySelectorAll("#ac-lista [data-toggle]").forEach((btn) => {
    btn.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const c = cabinete[Number(btn.dataset.toggle)];
      if (c.activ) {
        // [645] suspendarea cere motivul: fereastră nouă, centrată (673), nu o întrebare pe rând
        nav.deschide(`Suspendă cabinetul ${c.nume || ""}`, (corpS) => formularSuspendare(corpS, c, (m) => {
          _mesajUrmator = m;
          nav.inapoi();
        }));
        return;
      }
      confirmaCaseta(btn.parentElement || btn, `Reactivezi accesul cabinetului „${esc(c.nume)}”? Logarea cu parola și cu linkul de logare merg din nou.`, async () => {  // audit_cab_lot2_v1
        try {
          await api.post(`/admin/cabinete/${c.id}/reactiveaza`, {});
          corp.innerHTML = `<p class="ecran-nota">Se actualizează...</p>`;
          await randeaza(corp, nav, `Cabinetul „${c.nume}” e activ din nou; reactivarea e în jurnalul lui.`);
        } catch (e) {
          arataMesaj(corp.querySelector("#ac-mesaj"), (e && e.mesaj) || "Cabinetul nu s-a putut reactiva.", "eroare");
        }
      }, { textOk: "Reactivează" });
    });
  });
}

// [645] fereastra suspendării: motivul (obligatoriu, butoane alăturate), nota internă (opțională), acțiunea jos
function formularSuspendare(corp, c, dupa) {
  let motiv = null;
  corp.innerHTML = `
    <h2 class="pf-titlu">Suspendă cabinetul</h2>
    <p class="pf-intro"><b>${esc(c.nume || "")}</b> — cabinetul vede motivul la logare; administratorii lui primesc un email cu același motiv.</p>
    <fieldset class="camp" id="sus-motiv" style="border:0;padding:0;margin:0 0 12px">
      <legend class="camp-eticheta">Motivul suspendării<span class="oblig">*</span></legend>
      <div role="group" aria-label="Motivul suspendării" style="display:flex;flex-wrap:wrap;gap:8px">
        ${MOTIVE_SUSPENDARE.map(([k, t]) => `<button type="button" class="buton-secundar" data-motiv="${k}" aria-pressed="false" data-fara-actiune="alegerea motivului, în formular">${t}</button>`).join("")}
      </div>
    </fieldset>
    <div class="camp" style="margin-bottom:10px"><label for="sus-nota" class="camp-eticheta">Notă internă (opțional — n-o vede cabinetul)</label>
      <textarea class="camp-input" id="sus-nota" rows="3" maxlength="1000" style="resize:vertical;min-height:70px"></textarea></div>
    <div class="bara-fixa">
      <button class="buton-sters" id="sus-trimite" data-actiune="POST /admin/cabinete/{firm_id}/suspenda">Suspendă accesul</button>
      <div id="sus-msg"></div>
    </div>`;
  corp.querySelectorAll("[data-motiv]").forEach((b) => b.addEventListener("click", () => {
    motiv = b.dataset.motiv;
    corp.querySelectorAll("[data-motiv]").forEach((x) => {
      const ales = x === b;
      x.classList.toggle("buton-activ", ales);
      x.setAttribute("aria-pressed", String(ales));
    });
    corp.querySelector("#sus-msg").innerHTML = "";
  }));
  const b = corp.querySelector("#sus-trimite");
  b.addEventListener("click", () => {
    const msg = corp.querySelector("#sus-msg");
    if (!motiv) { arataMesaj(msg, "Alege motivul suspendării.", "eroare"); return; }
    const eticheta = (MOTIVE_SUSPENDARE.find((m) => m[0] === motiv) || [])[1] || "";
    confirmaCaseta(b, `Suspenzi accesul cabinetului „${esc(c.nume)}” (motivul: ${esc(eticheta.toLowerCase())})? Logarea se taie imediat, datele rămân.`, async () => {
      try {
        const r = await api.post(`/admin/cabinete/${c.id}/suspenda`, { motiv, nota_interna: corp.querySelector("#sus-nota").value.trim() || null });
        const em = r.destinatari ? ` Emailul cu motivul a plecat la ${cate(r.emailuri_trimise, "administrator", "administratori")} din ${r.destinatari}.`
          : " Cabinetul nu are niciun administrator activ cu email: emailul nu a plecat.";
        await dupa(`Cabinetul „${c.nume}” e suspendat (motivul: ${r.motiv}).${em}`);
      } catch (e) { arataRefuzul(corp, e, msg, { campuri: { motiv: "sus-motiv", nota_interna: "sus-nota" } }); }
    }, { textOk: "Suspendă" });
  });
}

function actiuneRo(a) {  // [aa_ro] jurnalul pe romaneste; necunoscutele raman brute
  a = a || "";
  if (a === "login") return "Autentificare";
  const REGULI = [
    ["control-fiscal", "A deschis Control fiscal"], ["eu/competente", "A deschis competențele"],
    ["eu/cabinet", "A deschis cabinetul"], ["recomanda", "A deschis Recomandă"],
    ["asistenti/echipa", "A deschis echipa"], ["facturi", "A lucrat în Facturi"],
    ["declaratii", "A lucrat în Declarații"], ["salariati", "A lucrat în Salariați"],
    ["migrare", "A lucrat în Migrare"], ["stocuri", "A lucrat în Stocuri"],
    ["banca", "A lucrat în Bancă"], ["portal", "A folosit portalul"],
    ["raportari", "A folosit Suport"], ["termene", "A deschis Termene"],
    ["anunturi", "A citit anunțurile"], ["notificari", "A citit notificările"],
    ["educatie", "A deschis Educație pe tipare"], ["patru-ochi", "A deschis patru-ochi"],
    ["asistenti", "A deschis echipa"], ["coada", "A lucrat în coada de validare"],
    ["plan-conturi", "A deschis planul de conturi"], ["firma-profil", "A deschis profilul firmei"],
    ["capacitate", "A deschis Capacitate"], ["permisiuni", "A deschis permisiunile"],
    ["consolidare", "A deschis Consolidare"],
    ["tenants", "A deschis o firmă"], ["recomanda", "A deschis Recomandă"],
  ];
  for (const [k, t] of REGULI) if (a.includes(k)) return t;
  return a;
}

// [645] jurnalul suspendărilor: cine, când, motivul, nota internă (o vede numai Admin iConta), reactivarea
function htmlSuspendari(lst) {
  if (!lst.length) return "";
  const rand = (s) => `<tr><td>${s.suspendat_la ? dataRo(s.suspendat_la, "cu_ora") : "dată neînregistrată"}</td><td>${esc(s.suspendat_de || "—")}</td>
    <td>${esc(s.motiv_suspendare || "neînregistrat (suspendare de dinainte de jurnal)")}</td><td>${esc(s.nota_interna || "—")}</td>
    <td>${s.reactivat_la ? `${dataRo(s.reactivat_la, "cu_ora")}${s.reactivat_de ? " · " + esc(s.reactivat_de) : ""}` : "încă suspendat"}</td></tr>`;
  return `<h3 class="pf-subtitlu" style="margin-top:14px">Suspendări</h3>
    <table class="fd-tabel" id="ac-suspendari"><thead><tr><th>Suspendat la</th><th>De</th><th>Motivul</th><th>Notă internă</th><th>Reactivat</th></tr></thead>
    <tbody>${lst.map(rand).join("")}</tbody></table>`;
}

async function deschideFisa(corp, cabinet) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă istoricul...</p>`;
  let activitate = [], suspendari = [];
  try {
    const r = await api.get(`/admin/activitate/cabinet/${cabinet.id}`);
    activitate = (r && r.activitate) || [];
    suspendari = (r && r.suspendari) || [];
  } catch (e) {
    corp.innerHTML = `<div class="ecran-nota">Nu s-a putut încărca istoricul cabinetului. Reîncearcă.</div>`;
    return;
  }
  // [aa_grupe] DS cap.2: nimic vizibil decat la selectie - jurnal grupat pe categorii, butoane toggle
  const grupe = {};
  activitate.forEach((a) => {
    const t = actiuneRo(a.actiune);
    (grupe[t] = grupe[t] || []).push(a);
  });
  const butoane = Object.keys(grupe).map((t, i) =>
    `<button class="buton-secundar buton-mic" data-grup="${i}">${esc(t)} (${grupe[t].length})</button>`).join(" ");
  const c = cabinet;  // [aa_rezumat] cifrele cabinetului, vizibile in capul detaliului
  corp.innerHTML = `
    <div class="rezumat-fix" id="ac-detaliu">
      <div class="pf-frand-nume" style="margin-bottom:4px">${esc(c.nume || "")}</div>
      <div class="pf-frand-sub" style="margin-bottom:10px">${cifreCabinet(c)}</div>
    </div>
    ${htmlSuspendari(suspendari)}
    ${activitate.length ? `<h3 class="pf-subtitlu" style="margin-top:14px">Activitate</h3><div style="display:flex;flex-wrap:wrap;gap:6px">${butoane}</div><div id="aa-evenimente"></div>`
      : `<div class="stare-goala">Niciun eveniment înregistrat încă. Apar aici pe măsură ce cabinetul lucrează.</div>`}`;
  const chei = Object.keys(grupe);
  let deschis = null;
  corp.querySelectorAll("[data-grup]").forEach((b) => b.addEventListener("click", () => {
    const i = Number(b.dataset.grup);
    const ev = corp.querySelector("#aa-evenimente");
    corp.querySelectorAll("[data-grup]").forEach((x) => x.classList.remove("buton-activ"));  // DS cap.1: fratii se inchid
    if (deschis === i) { deschis = null; ev.innerHTML = ""; return; }
    deschis = i; b.classList.add("buton-activ");
    ev.innerHTML = `<div class="sol-fir" style="margin-top:10px">${grupe[chei[i]].map((a) => `
      <div class="sol-rand sol-cabinet">
        <div class="sol-meta">${esc(a.nume || "")} ${esc(a.prenume || "")} · ${dataRo(a.created_at, "cu_ora")}</div>
      </div>`).join("")}</div>`;
  }));
}

// audit_cab_lot1_v1

// audit_cab_lot2_v1
