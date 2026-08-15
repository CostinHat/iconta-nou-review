// asistenti.js — managementul actorilor de cabinet (cardul Asistenți).
// Trei niveluri: listă actori -> editare actor (permisiuni + firme atribuite) -> Vizualizează.
// Doar admin_firma. Stil aliniat la validat.js / control.js (api.js + nav.deschide).
import { api, arataMesaj, confirmaCaseta, esc } from "../api.js?v=a0acf0511a";  /* audit_cab_lot2_v1 */
/* [patch11_semafor_explicit] */
function _semaforEticheta(culoare) {
  const M = { rosu: "probleme", galben: "de urm\u0103rit", verde: "f\u0103r\u0103 probleme" };
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
  const sumar = (date && date.sumar) || { total: 0, activi: 0 };

  corp.innerHTML = `
    <p class="mig-intro">Asistenții cabinetului: roluri, permisiuni și firmele pe care le lucrează.
      Tu decizi cine poate pregăti, valida și depune declarații.</p>
    <div class="asi-sumar">${sumar.total} asistenț${sumar.total === 1 ? "ă" : "i"} · ${sumar.activi} activ${sumar.activi === 1 ? "" : "i"}</div>
    <div id="asi-banner"></div>
    <button class="buton-primar" id="asi-adauga" style="margin:6px 0 14px">Adaug\u0103 asistent</button>
    <div id="asi-adauga-form" hidden style="margin-bottom:14px">
      <div class="camp" style="margin-bottom:10px"><label class="camp-eticheta">Email asistent<span class="oblig">*</span></label>
        <input class="camp-input" id="asi-email" type="email" placeholder="asistent@cabinet.ro" autocomplete="off"></div>
      <div class="camp" style="margin-bottom:10px"><label class="camp-eticheta">Nume (op\u021bional)</label>
        <input class="camp-input" id="asi-nume" autocomplete="off"></div>
      <label class="set-bifa" style="margin-bottom:10px"><input type="checkbox" id="asi-valida"> <span>Poate valida (Nivel 2)</span></label>
      <button class="buton-primar" id="asi-trimite">Trimite invita\u021bia</button>
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
    if (!email.includes("@")) { arataMesaj(msg, "Completeaz\u0103 un email valid.", "eroare"); return; }
    try {
      await api.post("/asistenti", { email, nume: corp.querySelector("#asi-nume").value.trim(),
        poate_valida: corp.querySelector("#asi-valida").checked });
      arataMesaj(msg, "Invita\u021bie trimis\u0103 pe " + email + ".", "info");
      setTimeout(() => randeazaAsistenti(corp, nav), 900);
    } catch (e) { arataMesaj(msg, e.mesaj || e.message, "eroare"); }
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
  const perms = PERM.map(([k, t]) => pastilaPerm(a[k], t)).join(" ");
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
  const calcNivel = () => a.poate_depune ? 3 : (a.poate_valida ? 2 : 1);

  nav.deschide(`Editeaza \u2014 ${nume}`, (box) => {
    const sectiuneFirme = a.atribuire_relevanta
      ? `
        <div class="asi-sectiune-titlu">Selecteaza firme</div>
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
        <span class="asi-nivel-badge" id="asi-nivel-badge">Nivel ${calcNivel()}</span>
        <span class="tip-desc">${a.rol === "admin_firma" ? "administrator" : (a.functie || "asistent")}</span>
      </div>
      <div class="asi-sectiune-titlu">Alege competente</div>
      <div id="asi-perm-edit">
        ${PERM.map(([k, t]) => `
          <label class="asi-firma-rand">
            <input type="checkbox" data-perm="${k}" ${a[k] ? "checked" : ""}>
            <span>${t}</span>
          </label>`).join("")}
      </div>
      <div class="asi-info-patru">\u2139 \u201ePoate valida\u201d permite aprobarea, dar niciodată a ceea ce a pregătit el însuși (patru ochi).</div>
      ${sectiuneFirme}
      <div class="asi-editbtns">
        <button class="buton-primar" id="asi-salveaza">Salveaz\u0103</button>
        ${a.rol !== "admin_firma" && a.activ
          ? `<button class="buton-secundar mig-buton-sec" id="asi-dezactiveaza">Dezactiveaza asistentul</button>` : ""}
        ${!a.activ
          ? `<button class="buton-secundar mig-buton-sec" id="asi-reactiveaza">Reactiveaza</button>` : ""}
      </div>
      <div class="mig-eroare" id="asi-edit-eroare"></div>
    `;

    const err = box.querySelector("#asi-edit-eroare");

    box.querySelectorAll("[data-perm]").forEach((cb) => {
      cb.addEventListener("change", () => {
        const val = box.querySelector('[data-perm="poate_valida"]')?.checked;
        const dep = box.querySelector('[data-perm="poate_depune"]')?.checked;
        const nv = dep ? 3 : (val ? 2 : 1);
        const bd = box.querySelector("#asi-nivel-badge");
        if (bd) bd.textContent = "Nivel " + nv;
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
        await api.post(`/asistenti/${uid}/permisiuni`, permVals);
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
        randeazaAsistenti(corp, nav);
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
  const iso = (x) => x.toISOString().slice(0, 10);

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
      <select class="camp-input" data-per style="width:auto;">
        <option value="tot">Tot</option>
        <option value="azi">Azi</option>
        <option value="luna">Luna curenta</option>
        <option value="an">Anul curent</option>
      </select>
    </div>`;

  const calitate = cal ? `
    <div class="asi-sectiune-titlu">Calitate</div>
    <div style="display:flex;gap:10px;margin:8px 0 12px;">
      <div class="asi-cal-card" style="flex:1;"><div class="asi-cal-eticheta">Pregatite</div><div class="asi-cal-cifra">${cal.pregatite}</div></div>
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
  if (cnt.rosu) detalii.push(`${cnt.rosu} asisten\u021b${cnt.rosu === 1 ? "" : "i"} cu gre\u0219eli repetate`);
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
