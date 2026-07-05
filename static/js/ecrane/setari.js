// setari.js — Ecran Setari cont: date cabinet (doar admin) + profil + parola.
// uid/rol din token (sursa unica). Refolosit oriunde apare cardul.

import { api } from "../api.js";
import { sesiune } from "../sesiune.js";

function esc(s) { return (s || "").replace(/"/g, "&quot;"); }

// [p48_compet] sectiunea de competente (pentru admin patron)
function _sectiuneCompetente(comp) {
  const c = comp || {};
  const b = (k) => c[k] ? "checked" : "";
  return `
    <div class="set-sectiune">
      <div class="set-titlu">Ce pot face</div>
      <p class="set-nota">Alege ce poți face în fluxul de declarații. Le poți lăsa nebifate dacă procesarea o fac asistenții.</p>
      <label class="set-bifa"><input type="checkbox" id="cmp-preg" ${b("poate_pregati")}> <span>Pot pregăti declarații</span></label>
      <label class="set-bifa"><input type="checkbox" id="cmp-val" ${b("poate_valida")}> <span>Pot valida declarații</span></label>
      <label class="set-bifa"><input type="checkbox" id="cmp-dep" ${b("poate_depune")}> <span>Pot depune declarații</span></label>
      <button class="set-buton" id="set-salveaza-compet">Salvează competențele</button>
      <div class="set-mesaj" id="set-msg-compet"></div>
    </div>`;
}

export async function randeazaSetari(corp, nav) {
  const u = sesiune.user() || {};
  const eAdmin = u.rol === "admin_firma" || u.rol === "superadmin";

  // datele cabinetului (doar admin)
  let cab = null;
  let _comp = null;  // [p48_compet]
  if (eAdmin) {
    try { const r = await api.get("/eu/cabinet"); if (r && r.ok) cab = r.cabinet; } catch {}
    try { const rc = await api.get("/eu/competente"); if (rc && rc.ok) _comp = rc; } catch {}
  }
  const sectiuneCabinet = (eAdmin && cab) ? `
    <div class="set-sectiune">
      <div class="set-titlu">Date cabinet</div>
      <label class="set-camp">
        <span class="set-eticheta">Nume cabinet</span>
        <input id="set-cab-nume" class="set-input" type="text" value="${esc(cab.nume)}">
      </label>
      <label class="set-camp">
        <span class="set-eticheta">CUI</span>
        <input id="set-cab-cui" class="set-input" type="text" value="${esc(cab.cui)}">
      </label>
      <button class="set-buton" id="set-salveaza-cabinet">Salveaza datele cabinetului</button>
      <div class="set-mesaj" id="set-msg-cabinet"></div>
    </div>` : "";

  corp.innerHTML = `
    <p class="mig-intro">Datele contului tau si schimbarea parolei.</p>

    ${sectiuneCabinet}

    ${eAdmin ? _sectiuneCompetente(_comp) : ""}
    ${eAdmin ? `<div class="set-sectiune">
      <div class="set-titlu">Chei API</div>
      <p class="mig-intro">Pentru conectarea altor aplica\u021bii la datele cabinetului. Cheia se afi\u0219eaz\u0103 o singur\u0103 dat\u0103.</p>
      <div id="set-chei-lista"><p class="ecran-nota">Se \u00eencarc\u0103...</p></div>
      <input id="set-cheie-nume" class="set-input" type="text" placeholder="Nume cheie (ex: integrare CRM)">
      <button class="set-buton" id="set-cheie-noua">Genereaz\u0103 cheie nou\u0103</button>
      <div class="set-mesaj" id="set-msg-chei"></div>
    </div>` : ""}

    <div class="set-sectiune">
      <div class="set-titlu">Date profil</div>
      <label class="set-camp">
        <span class="set-eticheta">Prenume</span>
        <input id="set-nume" class="set-input" type="text" value="${esc(u.nume)}">
      </label>
      <label class="set-camp">
        <span class="set-eticheta">Nume</span>
        <input id="set-prenume" class="set-input" type="text" value="${esc(u.prenume)}">
      </label>
      <button class="set-buton" id="set-salveaza-profil">Salveaza profilul</button>
      <div class="set-mesaj" id="set-msg-profil"></div>
    </div>

    <div class="set-sectiune">
      <div class="set-titlu">Schimba parola</div>
      <label class="set-camp">
        <span class="set-eticheta">Parola actuala</span>
        <input id="set-pv" class="set-input" type="password" autocomplete="current-password">
      </label>
      <label class="set-camp">
        <span class="set-eticheta">Parola noua (min 8 caractere)</span>
        <input id="set-pn" class="set-input" type="password" autocomplete="new-password">
      </label>
      <label class="set-camp">
        <span class="set-eticheta">Confirma parola noua</span>
        <input id="set-pc" class="set-input" type="password" autocomplete="new-password">
      </label>
      <button class="set-buton" id="set-schimba-parola">Schimba parola</button>
      <div class="set-mesaj" id="set-msg-parola"></div>
    </div>
  `;

  // --- salvare cabinet (doar admin) ---
  const btnCab = corp.querySelector("#set-salveaza-cabinet");
  if (btnCab) {
    btnCab.addEventListener("click", async () => {
      const msg = corp.querySelector("#set-msg-cabinet");
      const nume = corp.querySelector("#set-cab-nume").value.trim();
      const cui = corp.querySelector("#set-cab-cui").value.trim();
      msg.textContent = "Se salveaza..."; msg.className = "set-mesaj";
      try {
        const r = await api.post("/eu/cabinet", { nume, cui });
        if (r && r.ok && r.cabinet) {
          // sursa unica: numele cabinetului din bara 1 vine din sesiune.user().nume_firma
          const us = sesiune.user() || {};
          us.nume_firma = r.cabinet.nume;
          sesiune.intra(sesiune.token(), us);
          msg.textContent = "Date cabinet salvate."; msg.className = "set-mesaj set-ok";
        } else { msg.textContent = "Nu am putut salva."; msg.className = "set-mesaj set-err"; }
      } catch (e) { msg.textContent = "Eroare la salvare."; msg.className = "set-mesaj set-err"; }
    });
  }

  // [p48_compet] salvare competente proprii
  const btnCmp = corp.querySelector("#set-salveaza-compet");
  if (btnCmp) {
    btnCmp.addEventListener("click", async () => {
      const msg = corp.querySelector("#set-msg-compet");
      const preg = corp.querySelector("#cmp-preg").checked;
      const val = corp.querySelector("#cmp-val").checked;
      const dep = corp.querySelector("#cmp-dep").checked;
      msg.textContent = "Se salveaza..."; msg.className = "set-mesaj";
      btnCmp.disabled = true;
      try {
        const r = await api.post("/eu/competente", { poate_pregati: preg, poate_valida: val, poate_depune: dep });
        if (r && r.ok) {
          sesiune.actualizeazaUser({ poate_pregati: r.poate_pregati, poate_valida: r.poate_valida, poate_depune: r.poate_depune });
          msg.textContent = "Competente salvate."; msg.className = "set-mesaj set-ok";
        } else { msg.textContent = "Nu am putut salva."; msg.className = "set-mesaj set-err"; }
      } catch (e) { msg.textContent = "Eroare la salvare."; msg.className = "set-mesaj set-err"; }
      btnCmp.disabled = false;
    });
  }

  // --- salvare profil ---
  _initChei(corp);  // setari_api_chei_v2
  corp.querySelector("#set-salveaza-profil").addEventListener("click", async () => {
    const msg = corp.querySelector("#set-msg-profil");
    const nume = corp.querySelector("#set-nume").value.trim();
    const prenume = corp.querySelector("#set-prenume").value.trim();
    msg.textContent = "Se salveaza..."; msg.className = "set-mesaj";
    try {
      const r = await api.post("/eu/profil", { nume, prenume });
      if (r && r.ok && r.user) {
        sesiune.intra(sesiune.token(), r.user);
        msg.textContent = "Profil salvat."; msg.className = "set-mesaj set-ok";
      } else { msg.textContent = "Nu am putut salva."; msg.className = "set-mesaj set-err"; }
    } catch (e) { msg.textContent = "Eroare la salvare."; msg.className = "set-mesaj set-err"; }
  });

  // --- schimbare parola ---
  corp.querySelector("#set-schimba-parola").addEventListener("click", async () => {
    const msg = corp.querySelector("#set-msg-parola");
    const pv = corp.querySelector("#set-pv").value;
    const pn = corp.querySelector("#set-pn").value;
    const pc = corp.querySelector("#set-pc").value;
    msg.className = "set-mesaj";
    if (pn.length < 8) { msg.textContent = "Parola noua trebuie sa aiba minim 8 caractere."; msg.className = "set-mesaj set-err"; return; }
    if (pn !== pc) { msg.textContent = "Parolele nu coincid."; msg.className = "set-mesaj set-err"; return; }
    msg.textContent = "Se schimba...";
    try {
      await api.post("/eu/schimba-parola", { parola_veche: pv, parola_noua: pn });
      msg.textContent = "Parola schimbata cu succes."; msg.className = "set-mesaj set-ok";
      corp.querySelector("#set-pv").value = "";
      corp.querySelector("#set-pn").value = "";
      corp.querySelector("#set-pc").value = "";
    } catch (e) { msg.textContent = "Parola actuala gresita sau eroare."; msg.className = "set-mesaj set-err"; }
  });
}


// ---------- CHEI API ----------  // setari_api_chei_v1
async function _incarcaChei(corp) {
  const zona = corp.querySelector("#set-chei-lista");
  if (!zona) return;
  let chei = [];
  try { const r = await api.get("/cabinet/api-chei"); chei = (r && r.chei) || []; } catch {}
  if (!chei.length) { zona.innerHTML = `<div class="mig-gol">Nicio cheie generat\u0103.</div>`; return; }
  zona.innerHTML = chei.map((c) => `
    <div class="pf-frand">
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(c.nume) || "\u2014"} \u00b7 <code>${c.prefix}\u2026</code></div>
        <div class="pf-frand-sub">${c.activ ? "activ\u0103" : "revocat\u0103"}${c.ultima_folosire ? " \u00b7 folosit\u0103: " + c.ultima_folosire.slice(0, 16) : ""}</div>
      </div>
      ${c.activ ? `<span class="btn-link set-cheie-revoca" data-id="${c.id}" style="color:#c0392b">Revoc\u0103</span>` : ""}
    </div>`).join("");
  zona.querySelectorAll(".set-cheie-revoca").forEach((b) => b.addEventListener("click", async () => {
    if (!confirm("Revoci cheia? Aplica\u021biile care o folosesc nu vor mai avea acces.")) return;
    try { await api.del(`/cabinet/api-chei/${b.dataset.id}`); _incarcaChei(corp); }
    catch (e) { alert(e.mesaj || "eroare"); }
  }));
}

function _initChei(corp) {
  const btn = corp.querySelector("#set-cheie-noua");
  if (!btn) return;
  _incarcaChei(corp);
  btn.addEventListener("click", async () => {
    const msg = corp.querySelector("#set-msg-chei");
    const nume = corp.querySelector("#set-cheie-nume").value.trim() || null;
    try {
      const r = await api.post("/cabinet/api-chei", { nume });
      msg.innerHTML = `Cheia ta (copiaz-o ACUM, nu se mai afi\u0219eaz\u0103):<br><code style="user-select:all;word-break:break-all">${r.cheie}</code>`;
      corp.querySelector("#set-cheie-nume").value = "";
      _incarcaChei(corp);
    } catch (e) {
      msg.textContent = e.mesaj || e.message || "eroare";
    }
  });
}
