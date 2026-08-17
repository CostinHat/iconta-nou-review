// setari.js — Ecran Setari cont: meniu cu sectiuni; fiecare se deschide doar la selectie.
import { api, esc, confirmaCaseta, arataMesaj, dataRo, semnAjutor } from "../api.js?v=427bd69bf5";
import { sesiune } from "../sesiune.js?v=5d142951c9";

export async function randeazaSetari(corp, nav) {
  const u = sesiune.user() || {};
  const eAdmin = u.rol === "admin_firma" || u.rol === "superadmin";

  function randeazaMeniu() {
    nav.setInapoi(undefined);
    const itemi = [];
    if (eAdmin) itemi.push({ cheie: "cabinet", titlu: "Date cabinet" });
    if (eAdmin) itemi.push({ cheie: "competente", titlu: "Ce pot face" });
    if (eAdmin) itemi.push({ cheie: "chei", titlu: "Chei API" });
    if (eAdmin) itemi.push({ cheie: "spv", titlu: "Conectare SPV" });
    if (eAdmin) itemi.push({ cheie: "gdpr", titlu: "Datele cabinetului (GDPR)" });
    itemi.push({ cheie: "profil", titlu: "Date profil" });
    itemi.push({ cheie: "parola", titlu: "Schimbă parola" });
    corp.innerHTML = `
      <p class="mig-intro">Datele contului tău și setările cabinetului.</p>
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
    else if (cheie === "spv") randeazaSPV();
    else if (cheie === "gdpr") randeazaGDPR();
    else if (cheie === "profil") randeazaProfil();
    else if (cheie === "parola") randeazaParola();
  }

  function butonInapoi() { return ""; }
  function legaInapoi() {}

  async function randeazaCabinet() {
    corp.innerHTML = butonInapoi() + '<p class="ecran-nota">Se încarcă...</p>';
    legaInapoi();
    let cab = null;
    try { const r = await api.get("/eu/cabinet"); if (r && r.ok) cab = r.cabinet; } catch {}
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <div class="cap-titlu">Date cabinet</div>
        <label class="camp">
          <span class="camp-eticheta">Nume cabinet</span>
          <input id="set-cab-nume" class="camp-input" type="text" value="${esc(cab && cab.nume)}">
        </label>
        <label class="camp">
          <span class="camp-eticheta">CUI</span>
          <input id="set-cab-cui" class="camp-input" type="text" value="${esc(cab && cab.cui)}">
        </label>
        <button class="buton-primar" id="set-salveaza-cabinet">Salveaz\u0103 datele cabinetului</button>
        <div class="" id="set-msg-cabinet"></div>
      </div>`;
    legaInapoi();
    corp.querySelector("#set-salveaza-cabinet").addEventListener("click", async () => {
      const msg = corp.querySelector("#set-msg-cabinet");
      const nume = corp.querySelector("#set-cab-nume").value.trim();
      const cui = corp.querySelector("#set-cab-cui").value.trim();
      arataMesaj(msg, "Se salvează...", "info");
      try {
        const r = await api.post("/eu/cabinet", { nume, cui });
        if (r && r.ok && r.cabinet) {
          const us = sesiune.user() || {};
          us.nume_firma = r.cabinet.nume;
          sesiune.intra(sesiune.token(), us);
          arataMesaj(msg, "Date cabinet salvate.", "ok");
        } else { arataMesaj(msg, "Nu am putut salva.", "eroare"); }
      } catch (e) { arataMesaj(msg, "Eroare la salvare.", "eroare"); }
    });
  }

  async function randeazaCompetente() {
    corp.innerHTML = butonInapoi() + '<p class="ecran-nota">Se încarcă...</p>';
    legaInapoi();
    let comp = null;
    try { const rc = await api.get("/eu/competente"); if (rc && rc.ok) comp = rc; } catch {}
    const c = comp || {};
    const b = (k) => c[k] ? "checked" : "";
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <div class="cap-titlu">Ce pot face</div>
        <p class="ecran-nota">Alege ce poți face în fluxul de declarații. Le poți lăsa nebifate dacă procesarea o fac asistenții.</p>
        <label class="set-bifa"><input type="checkbox" id="cmp-preg" ${b("poate_pregati")}> <span>Pot pregăti declarații</span></label>
        <label class="set-bifa"><input type="checkbox" id="cmp-val" ${b("poate_valida")}> <span>Pot valida declarații</span></label>
        <label class="set-bifa"><input type="checkbox" id="cmp-dep" ${b("poate_depune")}> <span>Pot depune declarații</span></label>
        <button class="buton-primar" id="set-salveaza-compet">Salveaz\u0103 competen\u021bele</button>
        <div class="" id="set-msg-compet"></div>
      </div>`;
    legaInapoi();
    const btnCmp = corp.querySelector("#set-salveaza-compet");
    btnCmp.addEventListener("click", async () => {
      const msg = corp.querySelector("#set-msg-compet");
      const preg = corp.querySelector("#cmp-preg").checked;
      const val = corp.querySelector("#cmp-val").checked;
      const dep = corp.querySelector("#cmp-dep").checked;
      arataMesaj(msg, "Se salvează...", "info");
      btnCmp.disabled = true;
      try {
        const r = await api.post("/eu/competente", { poate_pregati: preg, poate_valida: val, poate_depune: dep });
        if (r && r.ok) {
          sesiune.actualizeazaUser({ poate_pregati: r.poate_pregati, poate_valida: r.poate_valida, poate_depune: r.poate_depune });
          arataMesaj(msg, "Competențe salvate.", "ok");
        } else { arataMesaj(msg, "Nu am putut salva.", "eroare"); }
      } catch (e) { arataMesaj(msg, "Eroare la salvare.", "eroare"); }
      btnCmp.disabled = false;
    });
  }

  function randeazaChei() {
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <div class="cap-titlu">Chei API ${semnAjutor("F005")}</div>
        <p class="mig-intro">Pentru conectarea altor aplicatii la datele cabinetului. Cheia se afiseaza o singura data.</p>
        <div id="set-chei-lista"><p class="ecran-nota">Se încarcă...</p></div>
        <label class="camp-eticheta" for="set-cheie-nume">Nume cheie</label>
        <input id="set-cheie-nume" class="camp-input" type="text" placeholder="ex: integrare CRM">
        <button class="buton-primar" id="set-cheie-noua">Generează cheie nouă</button>
        <div class="" id="set-msg-chei"></div>
      </div>`;
    legaInapoi();
    _initChei(corp);
  }

  async function randeazaSPV() {
    corp.innerHTML = butonInapoi() + '<p class="ecran-nota">Se încarcă...</p>';
    legaInapoi();
    let st = { conectat: false };
    try { const r = await api.get("/spv/stare"); if (r) st = r; } catch {}
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <div class="cap-titlu">Conectare SPV</div>
        <p class="ecran-nota">Autorizezi iConta.eu să lucreze cu SPV/ANAF (e-Factura, e-Transport) folosind certificatul tău. Autorizarea se face o singură dată pentru tot cabinetul.</p>
        <div class="caseta-info"><span class="ci-mesaj">După înrolarea certificatului în SPV, așteaptă 24 de ore înainte de prima conectare. Altfel ANAF răspunde cu eroare, deși totul e configurat corect.</span></div>
        <div id="spv-stare" style="margin:10px 0"></div>
        <button class="buton-primar" id="spv-conecteaza">Conectează SPV</button>
        <span class="camp-ajutor">Certificatul cloud (vToken instalat local) e acceptat, la fel ca cel pe token USB.</span>
      </div>`;
    legaInapoi();
    const msg = corp.querySelector("#spv-stare");
    const btn = corp.querySelector("#spv-conecteaza");
    if (st.conectat) {
      const pana = st.access_expira ? dataRo(st.access_expira, "lung") : "—";
      if (st.expira_curand) {
        arataMesaj(msg, `Conectat, dar accesul expiră curând (${pana}). Reconectează pentru siguranță.`, "avert");
      } else {
        arataMesaj(msg, `Conectat. Certificat ${st.serial_certificat || "—"}. Acces valabil până la ${pana}.`, "ok");
      }
      btn.textContent = "Reconectează SPV";
      btn.className = "buton-secundar";
    } else {
      arataMesaj(msg, "Neconectat.", "info");
    }
    btn.addEventListener("click", async () => {
      const text = btn.textContent;
      btn.disabled = true; btn.textContent = "Se conectează…";
      try {
        const r = await api.get("/spv/autorizare");
        if (r && r.url) {
          window.open(r.url, "_blank");
          arataMesaj(msg, "S-a deschis autorizarea ANAF în altă filă. După ce alegi certificatul și confirmi, revino aici și redeschide ecranul.", "info");
        } else { arataMesaj(msg, "Nu am putut porni autorizarea.", "eroare"); }
      } catch (e) { arataMesaj(msg, "Eroare la pornirea autorizării.", "eroare"); }
      btn.disabled = false; btn.textContent = text;
    });
  }

  async function randeazaGDPR() {
    corp.innerHTML = butonInapoi() + '<p class="ecran-nota">Se încarcă...</p>';
    legaInapoi();
    let cab = null;
    try { const r = await api.get("/eu/cabinet"); if (r && r.ok) cab = r.cabinet; } catch {}
    const numeCab = ((cab && cab.nume) || "").trim();
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <div class="cap-titlu">Export date cabinet ${semnAjutor("F199")}</div>
        <p class="ecran-nota">Descarci o arhivă ZIP cu toate datele cabinetului: firmele, utilizatorii, facturile, documentele contabile, jurnalul de audit și fișierele atașate (poze bonuri, e-Factură). Format: fișiere JSON per tabelă + fișierele originale. Îți exerciți dreptul la portabilitate (GDPR art. 20), oricând, fără intervenția noastră.</p>
        <div class="caseta-atentie"><div class="ca-mesaj">Arhiva conține date personale (ale clienților, salariaților și partenerilor). Păstreaz-o în siguranță și nu o distribui.</div></div>
        <button class="buton-primar" id="gdpr-export">Descarcă arhiva cabinetului</button>
        <div class="" id="gdpr-export-msg"></div>
      </div>

      <div class="panou" style="margin-top:16px">
        <div class="cap-titlu">Cerere de ștergere cont ${semnAjutor("F205")}</div>
        <div class="caseta-atentie"><div class="ca-mesaj">
          <b>Ștergerea este ireversibilă.</b> Se șterg definitiv toate firmele cabinetului, utilizatorii, facturile, declarațiile, documentele și fișierele — prin distrugerea completă a bazei de date a cabinetului.<br><br>
          <b>Ce NU se poate șterge imediat:</b> copiile de siguranță (backup) rămân până la 30 de zile, apoi se suprascriu automat. Ștergerea selectivă dintr-un backup nu e posibilă tehnic.<br><br>
          Nu se șterge nimic acum. Depui o cerere; o executăm noi manual, după verificare.
        </div></div>
        <div class="caseta-info"><span class="ci-mesaj">Îți răspundem în cel mult 5 zile lucrătoare de la depunere. Termenul legal maxim de răspuns este de 30 de zile (GDPR art. 12).</span></div>
        <label class="camp">
          <span class="camp-eticheta">Motivul cererii (opțional)</span>
          <textarea id="gdpr-motiv" class="camp-input" rows="3" placeholder="ex: încetăm activitatea"></textarea>
        </label>
        <label class="camp">
          <span class="camp-eticheta">Pentru confirmare, retastează denumirea exactă a cabinetului: <b>${esc(numeCab)}</b></span>
          <input id="gdpr-confirm" class="camp-input" type="text" autocomplete="off" placeholder="Denumirea cabinetului">
        </label>
        <button class="buton-sters" id="gdpr-cere" disabled>Trimite cererea de ștergere</button>
        <div class="" id="gdpr-cere-msg"></div>
      </div>`;
    legaInapoi();

    const btnEx = corp.querySelector("#gdpr-export");
    btnEx.addEventListener("click", async () => {
      const msg = corp.querySelector("#gdpr-export-msg");
      const txt = btnEx.textContent;
      btnEx.disabled = true; btnEx.textContent = "Se pregătește arhiva…";
      arataMesaj(msg, "Se generează arhiva. Poate dura până la un minut pentru cabinete mari.", "info");
      try {
        const resp = await fetch("/gdpr/export-cabinet", { headers: { Authorization: "Bearer " + sesiune.token() } });
        if (!resp.ok) throw new Error("eroare " + resp.status);
        const url = URL.createObjectURL(await resp.blob());
        const a = document.createElement("a");
        a.href = url; a.download = "export-cabinet.zip"; a.click();
        URL.revokeObjectURL(url);
        arataMesaj(msg, "Arhivă descărcată. Verifică folderul de descărcări.", "ok");
      } catch (e) { arataMesaj(msg, "Nu am putut genera arhiva. Încearcă din nou.", "eroare"); }
      btnEx.disabled = false; btnEx.textContent = txt;
    });

    const inp = corp.querySelector("#gdpr-confirm");
    const btnCe = corp.querySelector("#gdpr-cere");
    inp.addEventListener("input", () => { btnCe.disabled = inp.value.trim() !== numeCab || !numeCab; });
    btnCe.addEventListener("click", () => {
      const msg = corp.querySelector("#gdpr-cere-msg");
      confirmaCaseta(btnCe, "Trimiți cererea de ștergere a cabinetului? Datele vor fi șterse definitiv de echipa iConta.eu după verificare.", async () => {
        btnCe.disabled = true;
        arataMesaj(msg, "Se trimite cererea…", "info");
        try {
          const r = await api.post("/gdpr/cerere-stergere", { confirmare_nume: inp.value.trim(), motiv: corp.querySelector("#gdpr-motiv").value.trim() || null });
          if (r && r.ok) {
            arataMesaj(msg, "Cerere înregistrată (#" + r.cerere_id + "). Îți răspundem în cel mult 5 zile lucrătoare.", "ok");
          } else { arataMesaj(msg, "Nu am putut înregistra cererea.", "eroare"); btnCe.disabled = false; }
        } catch (e) { arataMesaj(msg, e.mesaj || "Eroare la trimiterea cererii.", "eroare"); btnCe.disabled = false; }
      }, { textOk: "Trimite cererea" });
    });
  }

  function randeazaProfil() {
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <div class="cap-titlu">Date profil</div>
        <label class="camp">
          <span class="camp-eticheta">Nume</span>
          <input id="set-nume" class="camp-input" type="text" value="${esc(u.nume)}">
        </label>
        <label class="camp">
          <span class="camp-eticheta">Prenume</span>
          <input id="set-prenume" class="camp-input" type="text" value="${esc(u.prenume)}">
        </label>
        <button class="buton-primar" id="set-salveaza-profil">Salveaz\u0103 profilul</button>
        <div class="" id="set-msg-profil"></div>
      </div>`;
    legaInapoi();
    corp.querySelector("#set-salveaza-profil").addEventListener("click", async () => {
      const msg = corp.querySelector("#set-msg-profil");
      const nume = corp.querySelector("#set-nume").value.trim();
      const prenume = corp.querySelector("#set-prenume").value.trim();
      arataMesaj(msg, "Se salvează...", "info");
      try {
        const r = await api.post("/eu/profil", { nume, prenume });
        if (r && r.ok && r.user) {
          sesiune.intra(sesiune.token(), r.user);
          arataMesaj(msg, "Profil salvat.", "ok");
        } else { arataMesaj(msg, "Nu am putut salva.", "eroare"); }
      } catch (e) { arataMesaj(msg, "Eroare la salvare.", "eroare"); }
    });
  }

  function randeazaParola() {
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <div class="cap-titlu">Schimbă parola</div>
        <label class="camp">
          <span class="camp-eticheta">Parola actuala</span>
          <input id="set-pv" class="camp-input" type="password" autocomplete="current-password">
        </label>
        <label class="camp">
          <span class="camp-eticheta">Parola nouă (min 8 caractere)</span>
          <input id="set-pn" class="camp-input" type="password" autocomplete="new-password">
        </label>
        <label class="camp">
          <span class="camp-eticheta">Confirmă parola nouă</span>
          <input id="set-pc" class="camp-input" type="password" autocomplete="new-password">
        </label>
        <button class="buton-primar" id="set-schimba-parola">Schimbă parola</button>
        <div class="" id="set-msg-parola"></div>
      </div>`;
    legaInapoi();
    corp.querySelector("#set-schimba-parola").addEventListener("click", async () => {
      const msg = corp.querySelector("#set-msg-parola");
      const pv = corp.querySelector("#set-pv").value;
      const pn = corp.querySelector("#set-pn").value;
      const pc = corp.querySelector("#set-pc").value;
      if (pn.length < 8) { arataMesaj(msg, "Parola nouă trebuie să aibă minim 8 caractere.", "eroare"); return; }
      if (pn !== pc) { arataMesaj(msg, "Parolele nu coincid.", "eroare"); return; }
      msg.textContent = "Se schimba...";
      try {
        await api.post("/eu/schimba-parola", { parola_veche: pv, parola_noua: pn });
        arataMesaj(msg, "Parolă schimbată cu succes.", "ok");
        corp.querySelector("#set-pv").value = "";
        corp.querySelector("#set-pn").value = "";
        corp.querySelector("#set-pc").value = "";
      } catch (e) { arataMesaj(msg, "Parola actuală greșită sau eroare.", "eroare"); }
    });
  }

  randeazaMeniu();
}


// ---------- CHEI API ----------
async function _incarcaChei(corp) {
  const zona = corp.querySelector("#set-chei-lista");
  if (!zona) return;
  let chei = [];
  try { const r = await api.get("/cabinet/api-chei"); chei = (r && r.chei) || []; } catch { zona.innerHTML = `<p class="ecran-nota">Nu am putut încărca cheile API.</p>`; return; }
  if (!chei.length) { zona.innerHTML = `<div class="stare-goala">Nicio cheie generată încă.</div>`; return; }
  zona.innerHTML = chei.map((c) => `
    <div class="pf-frand">
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(c.nume) || "—"} · <code>${c.prefix}…</code></div>
        <div class="pf-frand-sub">${c.activ ? "activa" : "revocata"}${c.ultima_folosire ? " · folosita: " + c.ultima_folosire.slice(0, 16) : ""}</div>
      </div>
      ${c.activ ? `<span class="btn-link set-cheie-revoca" data-id="${c.id}" style="color:var(--rosu)">Revoca</span>` : ""}
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
