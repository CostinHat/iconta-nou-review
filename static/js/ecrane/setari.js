// setari.js — Ecran Setari cont: meniu cu sectiuni; fiecare se deschide doar la selectie.
import { api, confirmaCaseta } from "../api.js";
import { sesiune } from "../sesiune.js";

function esc(s) { return (s || "").replace(/"/g, "&quot;"); }

export async function randeazaSetari(corp, nav) {
  const u = sesiune.user() || {};
  const eAdmin = u.rol === "admin_firma" || u.rol === "superadmin";

  function randeazaMeniu() {
    nav.setInapoi(undefined);
    const itemi = [];
    if (eAdmin) itemi.push({ cheie: "cabinet", titlu: "Date cabinet" });
    if (eAdmin) itemi.push({ cheie: "competente", titlu: "Ce pot face" });
    if (eAdmin) itemi.push({ cheie: "chei", titlu: "Chei API" });
    itemi.push({ cheie: "profil", titlu: "Date profil" });
    itemi.push({ cheie: "parola", titlu: "Schimba parola" });
    corp.innerHTML = `
      <p class="mig-intro">Datele contului tau si setarile cabinetului.</p>
      <div class="set-meniu"></div>
    `;
    const meniu = corp.querySelector(".set-meniu");
    itemi.forEach((it) => {
      const b = document.createElement("button");
      b.className = "acces-card meniu-card";
      b.textContent = it.titlu;
      b.addEventListener("click", () => nav.mergi(it.titlu, (c) => { corp = c; deschide(it.cheie); }));  // faza_b2_traseu_v1
      meniu.appendChild(b);
    });
  }

  function deschide(cheie) {
    if (cheie === "cabinet") randeazaCabinet();
    else if (cheie === "competente") randeazaCompetente();
    else if (cheie === "chei") randeazaChei();
    else if (cheie === "profil") randeazaProfil();
    else if (cheie === "parola") randeazaParola();
  }

  function butonInapoi() { return ""; }
  function legaInapoi() {}

  async function randeazaCabinet() {
    corp.innerHTML = butonInapoi() + '<p class="ecran-nota">Se incarca...</p>';
    legaInapoi();
    let cab = null;
    try { const r = await api.get("/eu/cabinet"); if (r && r.ok) cab = r.cabinet; } catch {}
    corp.innerHTML = butonInapoi() + `
      <div class="set-sectiune">
        <div class="set-titlu">Date cabinet</div>
        <label class="set-camp">
          <span class="set-eticheta">Nume cabinet</span>
          <input id="set-cab-nume" class="set-input" type="text" value="${esc(cab && cab.nume)}">
        </label>
        <label class="set-camp">
          <span class="set-eticheta">CUI</span>
          <input id="set-cab-cui" class="set-input" type="text" value="${esc(cab && cab.cui)}">
        </label>
        <button class="buton-primar" id="set-salveaza-cabinet">Salveaza datele cabinetului</button>
        <div class="set-mesaj" id="set-msg-cabinet"></div>
      </div>`;
    legaInapoi();
    corp.querySelector("#set-salveaza-cabinet").addEventListener("click", async () => {
      const msg = corp.querySelector("#set-msg-cabinet");
      const nume = corp.querySelector("#set-cab-nume").value.trim();
      const cui = corp.querySelector("#set-cab-cui").value.trim();
      msg.textContent = "Se salveaza..."; msg.className = "set-mesaj";
      try {
        const r = await api.post("/eu/cabinet", { nume, cui });
        if (r && r.ok && r.cabinet) {
          const us = sesiune.user() || {};
          us.nume_firma = r.cabinet.nume;
          sesiune.intra(sesiune.token(), us);
          msg.textContent = "Date cabinet salvate."; msg.className = "set-mesaj set-ok";
        } else { msg.textContent = "Nu am putut salva."; msg.className = "set-mesaj set-err"; }
      } catch (e) { msg.textContent = "Eroare la salvare."; msg.className = "set-mesaj set-err"; }
    });
  }

  async function randeazaCompetente() {
    corp.innerHTML = butonInapoi() + '<p class="ecran-nota">Se incarca...</p>';
    legaInapoi();
    let comp = null;
    try { const rc = await api.get("/eu/competente"); if (rc && rc.ok) comp = rc; } catch {}
    const c = comp || {};
    const b = (k) => c[k] ? "checked" : "";
    corp.innerHTML = butonInapoi() + `
      <div class="set-sectiune">
        <div class="set-titlu">Ce pot face</div>
        <p class="set-nota">Alege ce poti face in fluxul de declaratii. Le poti lasa nebifate daca procesarea o fac asistentii.</p>
        <label class="set-bifa"><input type="checkbox" id="cmp-preg" ${b("poate_pregati")}> <span>Pot pregati declaratii</span></label>
        <label class="set-bifa"><input type="checkbox" id="cmp-val" ${b("poate_valida")}> <span>Pot valida declaratii</span></label>
        <label class="set-bifa"><input type="checkbox" id="cmp-dep" ${b("poate_depune")}> <span>Pot depune declaratii</span></label>
        <button class="buton-primar" id="set-salveaza-compet">Salveaza competentele</button>
        <div class="set-mesaj" id="set-msg-compet"></div>
      </div>`;
    legaInapoi();
    const btnCmp = corp.querySelector("#set-salveaza-compet");
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

  function randeazaChei() {
    corp.innerHTML = butonInapoi() + `
      <div class="set-sectiune">
        <div class="set-titlu">Chei API</div>
        <p class="mig-intro">Pentru conectarea altor aplicatii la datele cabinetului. Cheia se afiseaza o singura data.</p>
        <div id="set-chei-lista"><p class="ecran-nota">Se incarca...</p></div>
        <input id="set-cheie-nume" class="set-input" type="text" placeholder="Nume cheie (ex: integrare CRM)">
        <button class="buton-primar" id="set-cheie-noua">Genereaza cheie noua</button>
        <div class="set-mesaj" id="set-msg-chei"></div>
      </div>`;
    legaInapoi();
    _initChei(corp);
  }

  function randeazaProfil() {
    corp.innerHTML = butonInapoi() + `
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
        <button class="buton-primar" id="set-salveaza-profil">Salveaza profilul</button>
        <div class="set-mesaj" id="set-msg-profil"></div>
      </div>`;
    legaInapoi();
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
  }

  function randeazaParola() {
    corp.innerHTML = butonInapoi() + `
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
        <button class="buton-primar" id="set-schimba-parola">Schimba parola</button>
        <div class="set-mesaj" id="set-msg-parola"></div>
      </div>`;
    legaInapoi();
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

  randeazaMeniu();
}


// ---------- CHEI API ----------
async function _incarcaChei(corp) {
  const zona = corp.querySelector("#set-chei-lista");
  if (!zona) return;
  let chei = [];
  try { const r = await api.get("/cabinet/api-chei"); chei = (r && r.chei) || []; } catch {}
  if (!chei.length) { zona.innerHTML = `<div class="mig-gol">Nicio cheie generata.</div>`; return; }
  zona.innerHTML = chei.map((c) => `
    <div class="pf-frand">
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(c.nume) || "—"} · <code>${c.prefix}…</code></div>
        <div class="pf-frand-sub">${c.activ ? "activa" : "revocata"}${c.ultima_folosire ? " · folosita: " + c.ultima_folosire.slice(0, 16) : ""}</div>
      </div>
      ${c.activ ? `<span class="btn-link set-cheie-revoca" data-id="${c.id}" style="color:#c0392b">Revoca</span>` : ""}
    </div>`).join("");
  zona.querySelectorAll(".set-cheie-revoca").forEach((b) => b.addEventListener("click", () => {
    confirmaCaseta(b.closest(".pf-frand") || b, "Revoci cheia? Aplicatiile care o folosesc nu vor mai avea acces.", async () => {
      try { await api.del(`/cabinet/api-chei/${b.dataset.id}`); _incarcaChei(corp); }
      catch (e) {
        b.parentElement.querySelectorAll(".msg-eroare").forEach((x) => x.remove());
        b.insertAdjacentHTML("afterend", '<span class="msg-eroare" style="margin-left:8px">' + (e.mesaj || "Nu am putut revoca cheia.") + '</span>');
      }
    }, { textOk: "Revoca" });
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
      msg.innerHTML = `Cheia ta (copiaz-o ACUM, nu se mai afiseaza):<br><code style="user-select:all;word-break:break-all">${r.cheie}</code>`;
      corp.querySelector("#set-cheie-nume").value = "";
      _incarcaChei(corp);
    } catch (e) {
      msg.textContent = e.mesaj || e.message || "eroare";
    }
  });
}

// audit_cab_lot1_v1

// faza_b2_traseu_v1
