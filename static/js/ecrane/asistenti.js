// asistenti.js — managementul actorilor de cabinet (cardul Asistenți).
// Trei niveluri: listă actori -> editare actor (permisiuni + firme atribuite) -> Vizualizează.
// Doar admin_firma. Stil aliniat la validat.js / control.js (api.js + nav.deschide).
import { api, arataMesaj, confirmaCaseta, esc, eroareCamp, curataEroriCamp, dataIso } from "../api.js?v=4242dc4353";  /* audit_cab_lot2_v1 */
/* [patch11_semafor_explicit] */
function _semaforEticheta(culoare) {
  // [eticheta_din_fapt 20.08.2026] `gri` lipsea din harta -> M[culoare] || "" randa o bulina
  // colorata CU ETICHETA GOALA. Griul a devenit accesibil in practica pe 20.08 (pastila_firma
  // nu-l mai falsifica in verde), deci golul ar fi ajuns pe ecran.
  const M = { rosu: "probleme", galben: "de urm\u0103rit", verde: "f\u0103r\u0103 probleme",
              gri: "nu se poate verifica" };
  const t = M[culoare] || "";
  return `<span class="asi-sem asi-sem-${culoare}"></span><span class="asi-sem-txt">${t}</span>`;
}

const PERM = [
  ["poate_pregati", "Poate pregăti"],
  ["poate_valida", "Poate valida"],
  ["poate_depune", "Poate depune"],
];

// ── NIVEL 2: listă actori ──────────────────────────────────
export async function randeazaAsistenti(corp, nav) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă asistenții…</p>`;
  let date;
  try {
    date = await api.get("/asistenti");
  } catch {
    corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca asistenții.</p>`;
    return;
  }
  const actori = (date && date.actori) || [];
  const sumar = (date && date.sumar) || { administratori: 0, asistenti: 0, asistenti_activi: 0 };
  // [comanda Costin 04.10.2026 pct.6] administratorul cabinetului NU e numărat printre asistenți
  const _n = (k, unu, multi) => `${k} ${k === 1 ? unu : multi}`;
  const textSumar = `${_n(sumar.administratori, "administrator", "administratori")} · ` +
    `${_n(sumar.asistenti, "asistent", "asistenți")}` +
    (sumar.asistenti ? ` (${_n(sumar.asistenti_activi, "activ", "activi")})` : "");

  corp.innerHTML = `
    <p class="mig-intro">Asistenții cabinetului: roluri, permisiuni și firmele pe care le lucrează.
      Tu decizi cine poate pregăti, valida și depune declarații.</p>
    <div class="asi-sumar">${textSumar}</div>
    <div id="asi-banner"></div>
    <button class="buton-primar" id="asi-adauga" data-actiune="POST /asistenti" style="margin:6px 0 14px">Adaug\u0103 asistent</button>
    <div id="asi-adauga-form" hidden style="margin-bottom:14px">
      <div class="camp" style="margin-bottom:10px"><label for="asi-email" class="camp-eticheta">Email asistent<span class="oblig">*</span></label>
        <input class="camp-input" id="asi-email" type="email" placeholder="asistent@cabinet.ro" autocomplete="off"></div>
      <div class="camp" style="margin-bottom:10px"><label for="asi-nume" class="camp-eticheta">Nume (op\u021bional)</label>
        <input class="camp-input" id="asi-nume" autocomplete="off"></div>
      <label class="set-bifa" style="margin-bottom:6px"><input type="checkbox" id="asi-pregati" checked> <span>Poate pregăti (munca curentă pe firmele alocate)</span></label>
      <label class="set-bifa" style="margin-bottom:10px"><input type="checkbox" id="asi-valida"> <span>Poate valida (Nivel 2)</span></label>
      <button class="buton-primar" id="asi-trimite" data-actiune="POST /asistenti">Trimite invita\u021bia</button>
      <p id="asi-adauga-msg" style="margin:8px 0 0"></p>
    </div>
    <div id="asi-lista"></div>
    <div class="mig-eroare" id="asi-eroare"></div>
  `;
  _asiBannerEchipa(corp, nav);
  corp.querySelector("#asi-adauga").addEventListener("click", () => {  /* asistent_nou_fe_v1 + investigatie_identitate_toggle */
    const f = corp.querySelector("#asi-adauga-form");
    const b = corp.querySelector("#asi-adauga");
    f.hidden = !f.hidden;
    b.classList.toggle("buton-activ", !f.hidden);
  });
  corp.querySelector("#asi-trimite").addEventListener("click", async () => {
    const msg = corp.querySelector("#asi-adauga-msg");
    const email = corp.querySelector("#asi-email").value.trim();
    curataEroriCamp(corp);
    if (!email.includes("@")) { eroareCamp(corp, "asi-email", "Completeaz\u0103 un email valid."); return; }
    try {
      // [drepturi_rol 04.10.2026] „Poate pregăti” e trimis explicit: până azi invitația nu-l dădea niciodată, iar
      // asistentul nou ieșea fără niciun drept (ecranul îi spunea totuși „Nivel 1”)
      await api.post("/asistenti", { email, nume: corp.querySelector("#asi-nume").value.trim(),
        poate_pregati: corp.querySelector("#asi-pregati").checked,
        poate_valida: corp.querySelector("#asi-valida").checked });
      arataMesaj(msg, "Invita\u021bie trimis\u0103 pe " + email + ".", "info");
      setTimeout(() => randeazaAsistenti(corp, nav), 900);
    } catch (e) {
      // [comanda Costin 04.10.2026 pct.3] adresa cu alt rol: refuzul numit stă pe câmpul de email
      let peCamp = false;
      (e.erori_campuri || []).forEach((c) => { if (c.camp === "email" && eroareCamp(corp, "asi-email", c.mesaj)) peCamp = true; });
      // motivul o singură dată: pe câmp; aici doar ce s-a întâmplat
      arataMesaj(msg, peCamp ? "Invitația nu s-a trimis. Corectează adresa marcată." : (e.mesaj || e.message), "eroare");
    }
  });
  const lista = corp.querySelector("#asi-lista");
  /* [patch8_lista_dez] */
  if (!actori.length) {
    lista.innerHTML = `<div class="stare-goala">Niciun asistent în cabinet.</div>`;
    return;
  }
  const activi = actori.filter((a) => a.activ);
  const inactivi = actori.filter((a) => !a.activ);

  if (!activi.length) {
    lista.innerHTML = `<div class="stare-goala">Niciun asistent activ.</div>`;
  } else {
    activi.forEach((a) => lista.appendChild(randActor(a, corp, nav)));
  }

  if (inactivi.length) {
    const wrap = document.createElement("div");
    wrap.innerHTML = `
      <button class="buton-secundar" id="asi-toggle-dez" style="margin-top:10px">Arată dezactivați (${inactivi.length})</button>
      <div id="asi-lista-dez" style="display:none;"></div>`;
    lista.appendChild(wrap);
    const cont = wrap.querySelector("#asi-lista-dez");
    inactivi.forEach((a) => cont.appendChild(randActor(a, corp, nav)));
    const btn = wrap.querySelector("#asi-toggle-dez");
    btn.onclick = () => {
      const deschis = cont.style.display !== "none";
      cont.style.display = deschis ? "none" : "";
      btn.textContent = (deschis ? "Arată" : "Ascunde") + ` dezactivați (${inactivi.length})`;
    };
  }
}

function pastilaPerm(activ, text) {
  const cls = activ ? "asi-perm-on" : "asi-perm-off";
  return `<span class="asi-perm ${cls}">${activ ? "✓" : "·"} ${text}</span>`;
}

function randActor(a, corp, nav) {
  const div = document.createElement("div");
  div.className = "val-card" + (a.activ ? "" : " asi-inactiv");
  const nume = [a.prenume, a.nume].filter(Boolean).join(" ") || a.email;
  const rolText = a.rol === "admin_firma" ? "administrator" : (a.functie || "asistent");
  // [comanda Costin 05.10.2026 pct.4] administratorul are toate drepturile (B3): cele trei apar active, indiferent de bife
  const perms = PERM.map(([k, t]) => pastilaPerm(a.rol === "admin_firma" || a[k], t)).join(" ");
  const inactivBadge = a.activ ? "" : `<span class="asi-badge-inactiv">dezactivat</span>`;
  div.innerHTML = `
    <div class="asi-rand-sus">
      <div>
        <div class="asi-nume">${esc(nume)} ${inactivBadge}</div>
        <div class="asi-rol">${rolText} · ${a.nr_firme} firme</div>
      </div>
      <div class="asi-actiuni-rand">
        <button class="buton-mic mig-buton-mic" data-act="edit">Editează</button>
        <button class="buton-mic mig-buton-mic" data-act="vezi">Vizualizează</button>
      </div>
    </div>
    <div class="asi-perms">${perms}</div>
  `;
  div.querySelector('[data-act="edit"]').onclick = () =>
    deschideEditare(a.id, corp, nav);
  div.querySelector('[data-act="vezi"]').onclick = () =>
    deschideVizualizare(a.id, nav);
  return div;
}

// ── NIVEL 3a: editare actor (permisiuni + firme) ───────────
// [patch6_editare_completa]
async function deschideEditare(uid, corp, nav) {
  let d;
  try { d = await api.get(`/asistenti/${uid}`); }
  catch { nav.deschide("Asistent", (c2) => { c2.innerHTML = '<p class="msg-eroare">Nu am putut încărca asistentul.</p>'; }); return; }
  if (!d.ok) return;
  const a = d.actor;
  const firme = d.firme || [];
  const nume = [a.prenume, a.nume].filter(Boolean).join(" ") || a.email;
  // [drepturi_rol 04.10.2026] fără nicio competență NU e „Nivel 1”: asistentul nu poate face nimic pe firme
  const nivelText = (preg, val, dep) => dep ? "Nivel 3" : (val ? "Nivel 2" : (preg ? "Nivel 1" : "fără competențe"));
  const esteAdmin = a.rol === "admin_firma";
  const calcNivel = () => esteAdmin ? "toate drepturile" : nivelText(a.poate_pregati, a.poate_valida, a.poate_depune);

  nav.deschide(`Editeaza \u2014 ${nume}`, (box) => {
    const sectiuneFirme = a.atribuire_relevanta
      ? `
        <div class="asi-sectiune-titlu">Selectează firme</div>
        <p class="asi-mic">Asistentul vede doar firmele bifate. Bifarea = stare finala.</p>
        <label class="camp-eticheta" for="asi-cauta-firme">Caut\u0103 firma</label>
        <input id="asi-cauta-firme" class="camp-input" placeholder="Caută firma (nume sau CUI)..." style="width:100%;margin-bottom:8px;">
        <div id="asi-firme">${firme.map((f) => `
          <label class="asi-firma-rand">
            <input type="checkbox" data-tid="${f.id}" ${f.atribuit ? "checked" : ""}>
            <span>${esc(f.nume)}${f.cui ? ` \u00b7 ${esc(f.cui)}` : ""}</span>
          </label>`).join("")}</div>`
      : `<p class="asi-mic">Administratorul vede automat tot portofoliul (nu se atribuie firme individual).</p>`;

    box.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
        <span class="asi-nivel-badge" id="asi-nivel-badge">${calcNivel()}</span>
        <span class="tip-desc">${a.rol === "admin_firma" ? "administrator" : (a.functie || "asistent")}</span>
      </div>
      <div class="asi-sectiune-titlu">${esteAdmin ? "Competențe" : "Alege competente"}</div>
      <div id="asi-perm-edit">
        ${esteAdmin
          ? `<p class="asi-mic">Administratorul cabinetului are toate drepturile: ${PERM.map(([, t]) => t).join(", ")}. Nu se bifează.</p>
             <div class="asi-perms">${PERM.map(([, t]) => pastilaPerm(true, t)).join(" ")}</div>`
          : PERM.map(([k, t]) => `
          <label class="asi-firma-rand">
            <input type="checkbox" data-perm="${k}" ${a[k] ? "checked" : ""}>
            <span>${t}</span>
          </label>`).join("")}
      </div>
      <div class="asi-info-patru">\u2139 \u201ePoate valida\u201d permite aprobarea, dar niciodată a ceea ce a pregătit el însuși (patru ochi).</div>
      ${sectiuneFirme}
      <div class="asi-editbtns">
        <button class="buton-primar" id="asi-salveaza" data-actiune="POST /asistenti/{uid}/permisiuni|POST /asistenti/{uid}/firme/{tid}|DELETE /asistenti/{uid}/firme/{tid}|POST /asistenti/{uid}/finalizeaza-firme">Salveaz\u0103</button>
        ${a.rol !== "admin_firma" && a.activ
          ? `<button class="buton-secundar mig-buton-sec" id="asi-dezactiveaza" data-actiune="POST /asistenti/{uid}/dezactiveaza">Dezactiveaza asistentul</button>` : ""}
        ${!a.activ
          ? `<button class="buton-secundar mig-buton-sec" id="asi-reactiveaza" data-actiune="POST /asistenti/{uid}/reactiveaza">Reactiveaza</button>` : ""}
      </div>
      <div class="mig-eroare" id="asi-edit-eroare"></div>
    `;

    const err = box.querySelector("#asi-edit-eroare");

    box.querySelectorAll("[data-perm]").forEach((cb) => {
      cb.addEventListener("change", () => {
        const preg = box.querySelector('[data-perm="poate_pregati"]')?.checked;
        const val = box.querySelector('[data-perm="poate_valida"]')?.checked;
        const dep = box.querySelector('[data-perm="poate_depune"]')?.checked;
        const bd = box.querySelector("#asi-nivel-badge");
        if (bd) bd.textContent = nivelText(preg, val, dep);
      });
    });

    const cauta = box.querySelector("#asi-cauta-firme");
    if (cauta)
      cauta.oninput = () => {
        const q = cauta.value.toLowerCase();
        box.querySelectorAll("#asi-firme .asi-firma-rand").forEach((r) => {
          r.style.display = r.textContent.toLowerCase().includes(q) ? "" : "none";
        });
      };

    const _salveazaEfectiv = async () => {  // audit_cab_lot2_v1
      try {
        const permVals = {};
        box.querySelectorAll("[data-perm]").forEach((cb) => { permVals[cb.dataset.perm] = cb.checked; });
        // administratorul n-are bife de trimis (serverul le refuză: ADMIN_TOATE_DREPTURILE)
        const _rp = esteAdmin ? null : await api.post(`/asistenti/${uid}/permisiuni`, permVals);
        if (a.atribuire_relevanta) {
          const initiale = {};
          firme.forEach((f) => (initiale[f.id] = f.atribuit));
          const tasks = [];
          box.querySelectorAll("[data-tid]").forEach((cb) => {
            const tid = Number(cb.dataset.tid);
            if (cb.checked && !initiale[tid]) tasks.push(api.post(`/asistenti/${uid}/firme/${tid}`));
            if (!cb.checked && initiale[tid]) tasks.push(api.del(`/asistenti/${uid}/firme/${tid}`));
          });
          await Promise.all(tasks);
          await api.post(`/asistenti/${uid}/finalizeaza-firme`);
        }
        nav.inapoi();
        await randeazaAsistenti(corp, nav);
        // [po_efectiv_v1] PUNCT DE ACTIUNE: acordarea dreptului de validare e chiar momentul in care
        // patru-ochi poate reintra in vigoare. Indicatorul din subbara (crom persistent) arata STAREA
        // la fiecare deschidere; aici se marcheaza MOMENTUL, ca patronul care reangajeaza sa nu afle
        // dintr-un buton disparut. Trecerea granitei nu e tacuta - DECIZII 20.08.2026.
        if (_rp && _rp.patru_ochi_intra_in_vigoare)
          arataMesaj(corp, "Validarea \u00een doi intr\u0103 acum \u00een vigoare: de aici \u00eenainte, cine preg\u0103te\u0219te o declara\u021bie nu o mai poate aproba singur. Declara\u021biile deja \u00een coad\u0103 trec la al doilea validator.", "ok");
      } catch { err.textContent = "Nu am putut salva. Încearcă din nou."; }
    };
    box.querySelector("#asi-salveaza").onclick = () => {
      err.textContent = "";
      const btnS = box.querySelector("#asi-salveaza");
      const valNou = box.querySelector('[data-perm="poate_valida"]')?.checked && !a.poate_valida;
      let intrebari = [];
      if (valNou) intrebari.push(`Acorzi dreptul de validare lui ${esc(nume)} (Nivel 2)? Asigură-te că acoperă tipurile pe care le va valida.`);
      if (a.atribuire_relevanta) {
        const bifate = [...box.querySelectorAll("[data-tid]")].filter((cb) => cb.checked).length;
        if (bifate === 0) {
          intrebari.push(a.rol === "angajat"
            ? `${esc(nume)} rămâne fără nicio firmă. Competențele se șterg și contul se DEZACTIVEAZĂ (rămâne în istoric).`
            : `${esc(nume)} rămâne fără nicio firmă. Competențele se șterg și iese din lista de procesatori (contul de administrator rămâne).`);
        }
      }
      if (!intrebari.length) { _salveazaEfectiv(); return; }
      confirmaCaseta(btnS.parentElement || btnS, intrebari.join(" ") + " Continui?", _salveazaEfectiv, { textOk: "Da, salvează" });
    };

    const bDez = box.querySelector("#asi-dezactiveaza");
    if (bDez) bDez.onclick = () => {
      confirmaCaseta(bDez.parentElement || bDez, `Dezactivezi ${esc(nume)}? Rămâne în istoric, dar nu mai are acces.`, async () => {
        try { await api.post(`/asistenti/${uid}/dezactiveaza`); nav.inapoi(); randeazaAsistenti(corp, nav); }
        catch { err.textContent = "Nu am putut dezactiva."; }
      }, { textOk: "Dezactivează" });
    };
    const bReact = box.querySelector("#asi-reactiveaza");
    if (bReact) bReact.onclick = async () => {
      try { await api.post(`/asistenti/${uid}/reactiveaza`); nav.inapoi(); randeazaAsistenti(corp, nav); }
      catch { err.textContent = "Nu am putut reactiva."; }
    };
  });
}

// ── NIVEL 3b: Vizualizează (read-only, activitate + patru ochi) ──
// [patch5_fereastra_completa]
async function deschideVizualizare(uid, nav) {
  const qp = (de, pana) => {
    const p = [];
    if (de) p.push("de=" + de);
    if (pana) p.push("pana=" + pana);
    return p.length ? "?" + p.join("&") : "";
  };
  const iso = (x) => dataIso(x);

  let d0;
  try { d0 = await api.get(`/asistenti/${uid}/activitate`); }
  catch { nav.deschide("Fișa asistentului", (c2) => { c2.innerHTML = '<p class="msg-eroare">Nu am putut încărca fișa.</p>'; }); return; }
  if (!d0.ok) return;
  const nume = [d0.actor.prenume, d0.actor.nume].filter(Boolean).join(" ") || `#${d0.actor.id}`;

  nav.deschide(`Asistent \u2014 ${nume}`, (box) => {
    async function reincarca(de, pana) {
      let c;
      try { c = await api.get(`/asistenti/${uid}/calitate` + qp(de, pana)); }
      catch { c = null; }
      box.innerHTML = _asiRandeazaFereastra(d0, c);
    }
    box.addEventListener("change", (e) => {
      const t = e.target;
      if (!(t && t.classList && (t.matches && t.matches("select[data-per]")))) return;
      const azi = new Date();
      let de = null, pana = null;
      if (t.value === "azi") { de = iso(azi); pana = iso(azi); }
      else if (t.value === "luna") { de = iso(new Date(azi.getFullYear(), azi.getMonth(), 1)); pana = iso(azi); }
      else if (t.value === "an") { de = iso(new Date(azi.getFullYear(), 0, 1)); pana = iso(azi); }
      reincarca(de, pana);
    });
    reincarca(null, null);
  });
}

function _asiRandeazaFereastra(d, c) {
  const cal = c && c.ok ? c : null;
  const nivel = cal ? cal.nivel : 1;
  let sem = "verde";
  if (cal && (cal.tipare || []).some((t) => t.tip === "sistematic")) sem = "rosu";
  else if (cal && (cal.tipare || []).some((t) => t.nou)) sem = "galben";

  const header = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
      <span class="asi-nivel-badge">Nivel ${nivel}</span>
      ${_semaforEticheta(sem)}
      <span class="tip-desc">${d.actor.rol}</span>
    </div>`;

  const perioada = `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
      <span class="tip-desc">Perioada:</span>
      <select class="camp-input" data-per aria-label="Perioada" style="width:auto;">
        <option value="tot">Tot</option>
        <option value="azi">Azi</option>
        <option value="luna">Luna curentă</option>
        <option value="an">Anul curent</option>
      </select>
    </div>`;

  const calitate = cal ? `
    <div class="asi-sectiune-titlu">Calitate</div>
    <div style="display:flex;gap:10px;margin:8px 0 12px;">
      <div class="asi-cal-card" style="flex:1;"><div class="asi-cal-eticheta">Pregătite</div><div class="asi-cal-cifra">${cal.pregatite}</div></div>
      <div class="asi-cal-card" style="flex:1;"><div class="asi-cal-eticheta">Aprobate</div><div class="asi-cal-cifra asi-cal-verde">${cal.aprobate}</div></div>
      <div class="asi-cal-card" style="flex:1;"><div class="asi-cal-eticheta">Respinse</div><div class="asi-cal-cifra asi-cal-rosu">${cal.respinse} \u00b7 ${cal.rata_respins}%</div></div>
    </div>
    <div class="asi-cal-rand2">
      <span>Timp mediu pregătit\u2192aprobat: <b>${cal.zile_mediu != null ? cal.zile_mediu + " zile" : "\u2014"}</b></span>
      <span>Acoperire: <b>${(cal.tipuri || []).join(", ") || "\u2014"}</b></span>
    </div>` : `<p class="ecran-nota">Calitatea nu a putut fi incarcata.</p>`;

  let tipare = "";
  if (cal) {
    const lst = cal.tipare || [];
    const rows = lst.length ? lst.map((t) => {
      const bt = t.tip === "sistematic"
        ? `<span class="asi-badge asi-badge-rosu">sistematic</span>`
        : `<span class="asi-badge asi-badge-gri">accident</span>`;
      const bn = t.nou ? `<span class="asi-badge asi-badge-galben">nou</span>` : "";
      return `<div class="asi-cal-motiv"><span>${t.motiv}</span><span>${bt} ${bn} <b>${t.nr}\u00d7</b></span></div>`;
    }).join("") : `<div class="stare-goala">Nicio respingere înregistrată.</div>`;
    tipare = `<div class="asi-sectiune-titlu">Tipare sistematice și greșeli noi</div>${rows}`;
  }

  const acte = d.activitate || [];
  const alerta = d.nr_self_approval > 0
    ? `<div class="asi-alerta-rosu">\u26a0 ${d.nr_self_approval} declara\u021bii aprobate de propriul preg\u0103titor (patru ochi).</div>`
    : `<div class="asi-alerta-verde">\u2713 Nicio declara\u021bie aprobat\u0103 de propriul preg\u0103titor.</div>`;
  const randuri = acte.length ? acte.map((c2) => {
    const roluri = [];
    if (c2.a_pregatit) roluri.push("pregatit");
    if (c2.a_aprobat) roluri.push("aprobat");
    if (c2.a_respins) roluri.push("respins");
    const flag = c2.self_approval ? `<span class="asi-flag-rosu">și-a aprobat singur</span>` : "";
    return `<div class="asi-act-rand ${c2.self_approval ? "asi-act-rosu" : ""}"><div class="asi-act-tip">${c2.tip} \u00b7 ${c2.perioada}</div><div class="asi-act-meta">firma #${c2.tenant_id} \u00b7 ${roluri.join(", ")} \u00b7 stare: ${c2.stare} ${flag}</div></div>`;
  }).join("") : `<div class="stare-goala">Nicio activitate \u00eenregistrat\u0103.</div>`;

  return `${header}${perioada}${calitate}${tipare}${alerta}<div class="asi-sectiune-titlu">Declarații lucrate (max. 200)</div><div id="asi-activitate">${randuri}</div>`;
}

/* [patch10_banner_erori] */
async function _asiBannerEchipa(corp, nav) {
  let s;
  try { s = await api.get("/asistenti/echipa/semafor"); } catch { return; }
  if (!s || !s.ok) return;
  const host = corp.querySelector("#asi-banner");
  if (!host) return;
  const cnt = s.counts || {};
  const detalii = [];
  // [pct.6, generalizat] semaforul numără TOȚI cei care lucrează declarații, inclusiv administratorul — deci
  // „persoane din echipă”, nu „asistenți” (aceeași clasă cu contorul de sus)
  if (cnt.rosu) detalii.push(`${cnt.rosu} ${cnt.rosu === 1 ? "persoană" : "persoane"} din echipă cu gre\u0219eli repetate`);
  if (cnt.galben) detalii.push(`${cnt.galben} de urm\u0103rit`);
  if (cnt.verde) detalii.push(`${cnt.verde} f\u0103r\u0103 probleme`);
  const text = detalii.length ? detalii.join(" \u00b7 ") : "nicio declara\u021bie lucrat\u0103 \u00een aceast\u0103 perioad\u0103"; /* semafor_text_explicit_v1 */
  const areErori = (cnt.rosu || 0) + (cnt.galben || 0) > 0;
  host.innerHTML = `
    <div class="asi-echipa-banner">
      <span class="asi-sem asi-sem-${s.culoare}"></span>
      <span class="asi-echipa-text">Calitatea echipei (${s.zile} zile): ${text}</span>
      ${areErori ? `<button class="buton-secundar buton-mic" id="asi-vezi-erori">Vezi erorile</button>` : ""}
    </div>`;
  const b = host.querySelector("#asi-vezi-erori");
  if (b) b.onclick = () => deschideEchipaErori(nav);
}

async function deschideEchipaErori(nav) {
  let d;
  try { d = await api.get("/asistenti/echipa/erori"); }
  catch { nav.deschide("Erori echipă", (c2) => { c2.innerHTML = '<p class="msg-eroare">Nu am putut încărca erorile.</p>'; }); return; }
  if (!d.ok) return;
  nav.deschide("Erori — echipa", (box) => {
    const lst = d.asistenti || [];
    if (!lst.length) {
      box.innerHTML = `<div class="asi-alerta-verde">✓ Nicio respingere \u00een ultimele ${d.zile} zile.</div>`;
      return;
    }
    const carduri = lst.map((a) => {
      const tipare = (a.tipare || []).map((t) => {
        const bt = t.tip === "sistematic"
          ? `<span class="asi-badge asi-badge-rosu">sistematic</span>`
          : `<span class="asi-badge asi-badge-gri">accident</span>`;
        const bn = t.nou ? `<span class="asi-badge asi-badge-galben">nou</span>` : "";
        return `<div class="asi-cal-motiv"><span>${t.motiv}</span><span>${bt} ${bn} <b>${t.nr}×</b></span></div>`;
      }).join("");
      return `
        <div class="val-card" style="display:block;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            ${_semaforEticheta(a.culoare)}
            <b>${esc(a.nume)}</b>
            <span class="tip-desc">${a.respinse} respinse · ${a.rata}%</span>
          </div>
          ${tipare}
        </div>`;
    }).join("");
    box.innerHTML = `<p class="mig-intro">Cine a produs respingeri în ultimele ${d.zile} zile, sortat după volum.</p>${carduri}`;
  });
}

// audit_cab_lot1_v1

// audit_cab_lot2_v1
