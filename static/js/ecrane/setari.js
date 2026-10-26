// setari.js — Ecran Setari cont: meniu cu sectiuni; fiecare se deschide doar la selectie.
import { api, esc, confirmaCaseta, arataMesaj, arataRefuzul, dataRo, semnAjutor, descarca, refuzPeRand, cate, eroareCamp, aduInVedere, atributeInactiv } from "../api.js?v=c6c45aefe4";
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { panouIntocmitor } from "./intocmitor_bilant.js?v=5d705395fe";   // [lotul 11, decizia 10.3] întocmitorul bilanțului, sub Date cabinet

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
    itemi.push({ cheie: "notificari", titlu: "Notificări" });   // [17.10.2026, lotul 7 pct.2.2]
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
    else if (cheie === "notificari") panouNotificari(corp);
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
        <h2 class="pf-titlu">Date cabinet</h2>
        <label class="camp">
          <span class="camp-eticheta">Nume cabinet</span>
          <input id="set-cab-nume" class="camp-input" type="text" value="${esc(cab && cab.nume)}">
        </label>
        <label class="camp">
          <span class="camp-eticheta">CUI</span>
          <input id="set-cab-cui" class="camp-input" type="text" value="${esc(cab && cab.cui)}">
        </label>
        <button class="buton-primar" id="set-salveaza-cabinet" data-actiune="POST /eu/cabinet">Salveaz\u0103 datele cabinetului</button>
        <div class="" id="set-msg-cabinet"></div>
      </div>
      <div class="panou" id="set-intocmitor"></div>`;
    legaInapoi();
    panouIntocmitor(corp.querySelector("#set-intocmitor"));
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
        } else { arataMesaj(msg, "Nu s-a putut salva.", "eroare"); }
      } catch (e) {
        // [lotul 10, C73 / U3] refuzul numit al serverului (CUI-ul altui cabinet, 422 cu erori_campuri), lângă câmp și sub buton
        const peCui = ((e && e.erori_campuri) || []).find((x) => x.camp === "cui");
        if (peCui) eroareCamp(corp, "set-cab-cui", peCui.mesaj);
        arataMesaj(msg, (e && e.mesaj) || "Eroare la salvare.", "eroare");
      }
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
        <h2 class="pf-titlu">Ce pot face</h2>
        <p class="ecran-nota">Alege ce poți face în fluxul de declarații. Le poți lăsa nebifate dacă procesarea o fac asistenții.</p>
        <label class="set-bifa"><input type="checkbox" id="cmp-preg" ${b("poate_pregati")}> <span>Pot pregăti declarații</span></label>
        <label class="set-bifa"><input type="checkbox" id="cmp-val" ${b("poate_valida")}> <span>Pot valida declarații</span></label>
        <label class="set-bifa"><input type="checkbox" id="cmp-dep" ${b("poate_depune")}> <span>Pot depune declarații</span></label>
        <button class="buton-primar" id="set-salveaza-compet" data-actiune="POST /eu/competente">Salveaz\u0103 competen\u021bele</button>
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
        } else { arataMesaj(msg, "Nu s-a putut salva.", "eroare"); }
      } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
      btnCmp.disabled = false;
    });
  }

  function randeazaChei() {
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <h2 class="pf-titlu">Chei API ${semnAjutor("F005")}</h2>
        <p class="mig-intro">Pentru conectarea altor aplicații la datele cabinetului. Cheia se afișează o singură dată.</p>
        <div id="set-chei-lista" data-actiune="GET /cabinet/api-chei"><p class="ecran-nota">Se încarcă...</p></div>
        <label class="camp-eticheta" for="set-cheie-nume">Nume cheie</label>
        <input id="set-cheie-nume" class="camp-input" type="text" placeholder="ex: integrare CRM">
        <button class="buton-primar" id="set-cheie-noua" data-actiune="POST /cabinet/api-chei">Generează cheie nouă</button>
        <div class="" id="set-msg-chei"></div>
      </div>`;
    legaInapoi();
    _initChei(corp);
  }

  async function randeazaSPV() {
    corp.innerHTML = butonInapoi() + '<div id="spv-panou"></div>';
    legaInapoi();
    await panouConectareSPV(corp.querySelector("#spv-panou"));
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
        <button class="buton-primar" id="gdpr-export" data-actiune="GET /gdpr/export-cabinet">Descarcă arhiva cabinetului</button>
        <div class="" id="gdpr-export-msg"></div>
      </div>

      <div class="panou" style="margin-top:16px">
        <div class="cap-titlu">Cerere de ștergere cont ${semnAjutor("F205")}</div>
        <div class="caseta-atentie"><div class="ca-mesaj">
          <b>Ștergerea este ireversibilă.</b> Se șterg definitiv toate firmele cabinetului, utilizatorii, facturile, declarațiile, documentele și fișierele — prin distrugerea completă a bazei de date a cabinetului.<br><br>
          <b>Ce nu se poate șterge imediat:</b> copiile de siguranță (backup) rămân până la 30 de zile, apoi se suprascriu automat. Ștergerea selectivă dintr-un backup nu e posibilă tehnic.<br><br>
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
        <button class="buton-sters" id="gdpr-cere" data-actiune="POST /gdpr/cerere-stergere" disabled>Trimite cererea de ștergere</button>
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
        await descarca("/gdpr/export-cabinet", "export-cabinet.zip");
        arataMesaj(msg, "Arhivă descărcată. Verifică folderul de descărcări.", "ok");
      } catch (e) { arataMesaj(msg, (e && (e.mesaj || e.message)) || "eroare", "eroare"); }   // [R131]
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
            arataMesaj(msg, "Cerere înregistrată. Îți răspundem în cel mult 5 zile lucrătoare.", "ok");   // [258] fără id-ul intern
          } else { arataMesaj(msg, "Nu s-a putut înregistra cererea.", "eroare"); btnCe.disabled = false; }
        } catch (e) { arataMesaj(msg, e.mesaj || "Eroare la trimiterea cererii.", "eroare"); btnCe.disabled = false; }
      }, { textOk: "Trimite cererea" });
    });
  }

  function randeazaProfil() {
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <h2 class="pf-titlu">Date profil</h2>
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
        } else { arataMesaj(msg, "Nu s-a putut salva.", "eroare"); }
      } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la salvare.", "eroare"); }
    });
  }

  function randeazaParola() {
    corp.innerHTML = butonInapoi() + `
      <div class="panou">
        <h2 class="pf-titlu">Schimbă parola</h2>
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
      arataMesaj(msg, "Se schimbă parola…", "info");
      try {
        await api.post("/eu/schimba-parola", { parola_veche: pv, parola_noua: pn });
        arataMesaj(msg, "Parolă schimbată cu succes.", "ok");
        corp.querySelector("#set-pv").value = "";
        corp.querySelector("#set-pn").value = "";
        corp.querySelector("#set-pc").value = "";
      } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Parola actuală greșită sau eroare.", "eroare"); }
    });
  }

  randeazaMeniu();
}


// ---------- CHEI API ----------
async function _incarcaChei(corp) {
  const zona = corp.querySelector("#set-chei-lista");
  if (!zona) return;
  let chei = [];
  try { const r = await api.get("/cabinet/api-chei"); chei = (r && r.chei) || []; } catch { zona.innerHTML = `<p class="ecran-nota">Nu s-au putut încărca cheile API.</p>`; return; }
  if (!chei.length) { zona.innerHTML = `<div class="stare-goala">Nicio cheie generată încă.</div>`; return; }
  // [lotul 13, deficiența 564: „lista nu arată ultima folosire (promisă în descriere)”] fiecare rând spune când a fost creată cheia și
  // când a deschis ultima dată datele (sau că n-a fost folosită încă), cu data în forma aplicației (DS cap.4, `dataRo`), nu ISO.
  // [674, clasă DS: „Orice acțiune e un buton, nu text pe care se dă click”] „Revocă” e buton (`.buton-sters buton-mic`, DS cap.1:
  // „Ștergere/revocare/distructiv”); cheia revocată rămâne în listă, cu starea ei, fără acțiune.
  zona.innerHTML = chei.map((c) => `
    <div class="pf-frand" data-cheie-id="${c.id}">
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${esc(c.nume) || "—"} · <code>${esc(c.prefix)}…</code></div>
        <div class="pf-frand-sub">${c.activ ? "activă" : "revocată"}${c.creat_la ? " · creată " + dataRo(c.creat_la, "cu_ora") : ""} · ${c.ultima_folosire ? "folosită ultima dată " + dataRo(c.ultima_folosire, "cu_ora") : "nefolosită încă"}</div>
      </div>
      <button type="button" class="buton-sters buton-mic set-cheie-revoca" data-actiune="DELETE /cabinet/api-chei/{kid}" data-id="${c.id}"${c.activ ? "" : atributeInactiv("Cheia e deja revocată.")}>Revocă</button>
    </div>`).join("");
  zona.querySelectorAll(".set-cheie-revoca").forEach((b) => b.addEventListener("click", () => {
    confirmaCaseta(b.closest(".pf-frand") || b, "Revoci cheia? Aplicațiile care o folosesc nu vor mai avea acces.", async () => {
      try {
        await api.del(`/cabinet/api-chei/${b.dataset.id}`);
        // [564: „cheia completă rămâne afișată și după revocare”] cheia arătată la creare dispare odată cu revocarea ei
        const msg = corp.querySelector("#set-msg-chei");
        if (msg && msg.dataset.cheieId === String(b.dataset.id)) { msg.innerHTML = ""; msg.className = ""; delete msg.dataset.cheieId; }
        _incarcaChei(corp);
      }
      catch (e) {
        refuzPeRand(b, e.mesaj || "Nu s-a putut revoca cheia.");
      }
    }, { textOk: "Revocă" });
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
      // [lotul 12, 45] mesajul cu cheia (HTML: cheia se copiază din <code>) e un mesaj de după buton: zonă de mesaj + adus în vedere,
      // ca orice mesaj din `arataMesaj` (o zonă fără clasă, scrisă direct, rămânea sub marginea ecranului)
      msg.className = "msg-ok";
      // [564: „lipsește butonul Copiază”] cheia se copiază cu un buton (clipboard, ca „Copiază tot” din Suport), nu numai prin selecție
      msg.innerHTML = `Cheia ta (copiaz-o acum: nu se mai afișează):<br><code id="set-cheie-text" style="user-select:all;word-break:break-all">${esc(r.cheie)}</code>
        <div><button type="button" class="buton-secundar buton-mic" id="set-cheie-copiaza" data-fara-actiune>Copiază</button></div>`;
      msg.dataset.cheieId = String(r.id);
      const bc = msg.querySelector("#set-cheie-copiaza");
      bc.addEventListener("click", () => {
        navigator.clipboard.writeText(r.cheie).then(() => { bc.textContent = "Copiată"; setTimeout(() => { bc.textContent = "Copiază"; }, 1400); })
          .catch(() => { bc.textContent = "Selectează cheia și copiaz-o"; });
      });
      corp.querySelector("#set-cheie-nume").value = "";
      // [lotul 12, 45] lista cheilor (deasupra mesajului) se reîncarcă ÎNTÂI: altfel rândul cheii noi împingea mesajul sub margine după ce
      // fusese adus în vedere (cu multe chei, cu zeci de pixeli)
      await _incarcaChei(corp);
      aduInVedere(msg);
    } catch (e) {
      arataMesaj(msg, e.mesaj || e.message || "eroare", "eroare");
    }
  });
}

// audit_cab_lot1_v1

// faza_b2_traseu_v1

// [deficiența 289a/b] Panoul „Conectare SPV” — din Setări cont și din orice refuz / stare care trimite aici (`ecran_destinatie.ECRANE`).
// Certificatul se arată prin emitentul lui (claim-ul `issuer` din tokenul ANAF), nu prin seria hexazecimală; titularul nu e în token
// (ANAF nu-l trimite) — se spune. Conectarea o face administratorul cabinetului; ceilalți văd starea și cui să-i ceară.
// [17.10.2026, lotul 7 pct.2.2, comanda Costin verbatim în DECIZII] „în Setări cont, fiecare utilizator își pune numărul și alege
// WhatsApp sau email (implicit email). WhatsApp se activează numai după confirmarea numărului printr-un cod trimis pe WhatsApp și bifa
// de acord pentru mesaje.” Ordinea pe ecran = ordinea serverului (`core/uc_cont_notificari.py`): numărul, acordul + codul, confirmarea,
// canalul. Opțiunea WhatsApp e inactivă până la confirmare și acord, cu motivul lângă ea. Superadminul îl deschide din cardul lui.
// [comanda Costin 17.10.2026 7.2 pct.2] „titlul din Notificări rămâne o singură dată, în corpul ferestrei, ca la celelalte ecrane”: fiecare
// ecran din Setări cont își scrie titlul ca <h2 class="pf-titlu"> în corp (navigatorul nu-l mai adaugă a doua oară); era și titlul pus
// de navigator, și „cap-titlu” în panou. Aceeași clasă pe toate cele șapte ecrane ale meniului.
export async function panouNotificari(zona, opt = {}) {
  zona.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
  let st = null;
  try { st = await api.get("/eu/notificari"); } catch (e) { zona.innerHTML = ""; arataMesaj(zona, e.mesaj || "Setările notificărilor nu s-au putut citi.", "eroare"); return; }
  const deschis = (st) => st.whatsapp_disponibil && st.telefon && st.confirmat && st.acord;
  // [deficiențele 335 + 336, 18.10.2026] de ce WhatsApp nu e ales: întâi pentru că nu trimite încă (atunci nici codul nu se oferă), apoi
  // numărul / confirmarea / acordul. Același motiv sub listă și în mesajul de după salvare.
  const motivWa = (s) => (deschis(s) ? "" : !s.whatsapp_disponibil ? (s.whatsapp_motiv || "")
    : !s.telefon ? "WhatsApp: salvează întâi numărul, apoi confirmă-l cu codul."
    : !s.confirmat ? "WhatsApp: numărul nu e confirmat încă — confirmă-l cu codul primit pe WhatsApp."
    : "WhatsApp: bifează acordul pentru mesaje.");
  zona.innerHTML = `
    <div class="panou">
      <h2 class="pf-titlu">Notificări</h2>
      <p class="ecran-nota">Notificările din clopoțel îți vin și pe canalul ales aici. Pe WhatsApp primești un mesaj scurt, fără date fiscale, cu linkul spre aplicație. Confirmarea contului, resetarea parolei și linkul de logare vin mereu pe email.</p>
      <label class="camp">
        <span class="camp-eticheta">Telefon</span>
        <span class="camp-ajutor">Cu prefixul țării (+40 7xx xxx xxx) sau ca număr românesc (07xx xxx xxx).</span>
        <input id="not-telefon" class="camp-input" type="tel" autocomplete="tel" value="${esc(st.telefon || "")}">
      </label>
      <div><button class="buton-secundar" id="not-salveaza-telefon">Salvează numărul</button></div>
      <div id="not-msg-telefon"></div>
      <div id="not-stare-telefon" class="ecran-nota"></div>
      <div id="not-avert-telefon" class="caseta-atentie" hidden><div class="ca-mesaj"></div></div>
      <div id="not-confirmare">
        <label class="set-bifa"><input type="checkbox" id="not-acord"${st.acord ? " checked" : ""}> <span>Sunt de acord să primesc mesaje de la iConta.eu pe WhatsApp (${esc(st.numar_iconta)}), la numărul de mai sus.</span></label>
        <button class="buton-secundar" id="not-cere-cod">Trimite codul pe WhatsApp</button>
        <label class="camp">
          <span class="camp-eticheta">Codul primit pe WhatsApp</span>
          <input id="not-cod" class="camp-input" inputmode="numeric" autocomplete="one-time-code" maxlength="6">
        </label>
        <button class="buton-secundar" id="not-confirma">Confirmă numărul</button>
      </div>
      <label class="camp">
        <span class="camp-eticheta">Primește notificările pe</span>
        <select id="not-canal" class="camp-input" data-butoane="">
          <option value="email">Email</option>
          <option value="whatsapp">WhatsApp</option>
        </select>
      </label>
      <div id="not-motiv-canal" class="ecran-nota"></div>
      <div id="not-tipuri"></div>
      <button class="buton-primar" id="not-salveaza-canal">Salvează</button>
      <div id="not-msg"></div>
    </div>`;
  // [deficiența 320, comanda Costin 17.10.2026 7.2] toate tipurile care te privesc, grupate, cu un rând despre ce face aplicația la
  // fiecare; termenele și validările vin bifate din oficiu; emailurile contului nu sunt în listă și pleacă mereu (nota de sub listă)
  const zTip = zona.querySelector("#not-tipuri");
  zTip.innerHTML = (st.grupuri || []).length ? `<fieldset class="camp not-tipuri" style="border:0;padding:0;margin:12px 0 8px">
      <legend class="camp-eticheta">Ce primești pe canalul ales</legend>
      ${st.grupuri.map((g) => `<div class="not-grup"><div class="cf-grup-titlu">${esc(g.grup)}</div>
        ${g.tipuri.map((t) => `<label class="set-bifa not-tip"><input type="checkbox" data-tip="${esc(t.cheie)}"${t.bifat ? " checked" : ""}>
          <span><b>${esc(t.eticheta.charAt(0).toUpperCase() + t.eticheta.slice(1))}</b><br><span class="ecran-nota">${esc(t.rand)}</span></span></label>`).join("")}</div>`).join("")}
      <p class="ecran-nota">${esc(st.nota_emailuri_cont || "")}</p>
      ${st.nota_sinteza ? `<p class="ecran-nota" id="not-nota-sinteza">${esc(st.nota_sinteza)}</p>` : ""}</fieldset>` : "";
  const $ = (s) => zona.querySelector(s);
  const msg = $("#not-msg");
  function arata(s) {
    st = s;
    $("#not-stare-telefon").textContent = !s.telefon ? "Niciun număr salvat."
      : s.confirmat ? `Numărul ${s.telefon} e confirmat.` : `Numărul ${s.telefon} nu e confirmat încă.`;
    $("#not-confirmare").hidden = !s.whatsapp_disponibil || !s.telefon || s.confirmat;   // [335] fără WhatsApp activ, nici cod
    const av = $("#not-avert-telefon");   // [338] același număr la alt cont
    av.hidden = !s.avertisment_telefon;
    av.querySelector(".ca-mesaj").textContent = s.avertisment_telefon || "";
    $("#not-acord").checked = !!s.acord;
    $("#not-canal").value = s.canal;
    const wa = $("#not-canal").querySelector('option[value="whatsapp"]');
    wa.disabled = !deschis(s);
    $("#not-motiv-canal").textContent = motivWa(s);
  }
  arata(st);
  $("#not-salveaza-telefon").addEventListener("click", async () => {
    // [596, lotul 12] mesajul salvării numărului stă lângă butonul lui (înainte cădea sub tot panoul); refuzul, lângă câmp
    const zm = $("#not-msg-telefon");
    try { arata(await api.put("/eu/telefon", { telefon: $("#not-telefon").value.trim() })); arataMesaj(zm, st.telefon ? `Numărul ${st.telefon} a fost salvat.` : "Numărul a fost șters.", "ok"); }
    catch (e) { arataRefuzul(zona, e, zm); }
  });
  $("#not-cere-cod").addEventListener("click", async () => {
    try { const r = await api.post("/eu/telefon/cod", { acord: $("#not-acord").checked }); arataMesaj(msg, `Codul a plecat pe WhatsApp. E valabil ${cate(r.minute, "minut", "minute")}.`, "ok"); }
    // [lotul 13, deficiența 647: „Afișare: «NU s-a salvat» deși numărul e salvat”] WhatsApp indisponibil nu e un refuz al unei salvări:
    // numărul și acordul sunt salvate, doar codul n-a plecat — avertisment, fără caseta „NU s-a salvat” (care se leagă numai de „eroare”)
    catch (e) {
      if ((e.detaliu || {}).cod === "WHATSAPP_INDISPONIBIL") arataMesaj(msg, e.mesaj || "WhatsApp nu e disponibil acum; notificările vin pe email.", "avert");
      else arataRefuzul(zona, e, msg);
    }
    try { arata(await api.get("/eu/notificari")); } catch { /* starea rămâne cea afișată */ }
  });
  $("#not-confirma").addEventListener("click", async () => {
    try { arata(await api.post("/eu/telefon/confirma", { cod: $("#not-cod").value.trim() })); arataMesaj(msg, "Numărul e confirmat. Poți alege WhatsApp.", "ok"); }
    catch (e) { arataMesaj(msg, e.mesaj || "Codul nu s-a putut verifica.", "eroare"); }
  });
  $("#not-salveaza-canal").addEventListener("click", async () => {
    try {
      const tipuri = {};
      zona.querySelectorAll("#not-tipuri [data-tip]").forEach((c) => { tipuri[c.dataset.tip] = c.checked; });
      arata(await api.put("/eu/notificari", { canal: $("#not-canal").value, acord: $("#not-acord").checked, tipuri }));
      // [336] pe email fiindcă WhatsApp nu se poate încă: motivul, nu doar „vin pe email”
      const motiv = st.canal !== "whatsapp" && (st.acord || !st.whatsapp_disponibil) ? motivWa(st) : "";
      arataMesaj(msg, (st.canal === "whatsapp" ? "Notificările vin pe WhatsApp." : "Notificările vin pe email." + (motiv ? " " + motiv : ""))
        + " Alegerile tale sunt salvate.", "ok");
      if (opt.dupaSalvare) opt.dupaSalvare(st);   // [320] prima intrare: „Continuă” se deblochează
    } catch (e) {
      (e.erori_campuri || []).forEach((c) => eroareCamp(zona, c.camp, c.mesaj));
      arataMesaj(msg, e.mesaj || "Canalul nu s-a putut salva.", "eroare");
    }
  });
}

export async function panouConectareSPV(zona) {
  const u = sesiune.user() || {};
  const eAdmin = u.rol === "admin_firma" || u.rol === "superadmin";
  zona.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
  let st = { conectat: false };
  try { const r = await api.get("/spv/stare"); if (r) st = r; } catch {}
  zona.innerHTML = `
    <div class="panou">
      <h2 class="pf-titlu">Conectare SPV</h2>
      <p class="ecran-nota">Autorizezi iConta.eu să lucreze cu SPV/ANAF (e-Factura, e-Transport) folosind certificatul tău. Autorizarea se face o singură dată pentru tot cabinetul și acoperă firmele pentru care certificatul are împuternicire la ANAF.</p>
      <div class="caseta-info"><span class="ci-mesaj">După înrolarea certificatului în SPV, așteaptă 24 de ore înainte de prima conectare. Altfel ANAF răspunde cu eroare, deși totul e configurat corect.</span></div>
      <div id="spv-stare" style="margin:10px 0"></div>
      ${eAdmin ? `<button class="buton-primar" id="spv-conecteaza">Conectează SPV</button>
      <span class="camp-ajutor">Certificatul cloud (vToken instalat local) e acceptat, la fel ca cel pe token USB.</span>`
        : `<p class="ecran-nota">Conectarea o face administratorul cabinetului, din Setări cont → Conectare SPV.</p>`}
    </div>`;
  const msg = zona.querySelector("#spv-stare");
  const btn = zona.querySelector("#spv-conecteaza");
  if (st.conectat) {
    const pana = st.access_expira ? dataRo(st.access_expira, "lung") : "—";
    const cert = `Certificat ${st.emitent_certificat ? "emis de " + st.emitent_certificat : "(emitent necunoscut)"}; titularul nu e transmis de ANAF.`;
    if (st.expira_curand) arataMesaj(msg, `Conectat, dar accesul expiră curând (${pana}). Reconectează pentru siguranță. ${cert}`, "avert");
    else arataMesaj(msg, `Conectat. ${cert} Acces valabil până la ${pana}.`, "ok");
    // [289 + 17.10.2026, decizia Costin pct.2] CUI-urile verificate de citirea automată: cu drept / fără drept (cu ce faci)
    const cuiuri = st.cuiuri || [];
    if (cuiuri.length) {
      const z = document.createElement("div");
      z.id = "spv-cuiuri";
      // [deficiența 315, comanda Costin 17.10.2026 7.2] explicația (OMFP 660/2017) o dată, deasupra; pe fiecare firmă un rând:
      // „<firmă> · fără drept în SPV · verificat <data, ora>”
      z.innerHTML = `<div class="cap-titlu" style="margin-top:12px">Firme verificate în SPV cu acest certificat</div>`
        + (st.explicatie_fara_drept ? `<div class="caseta-atentie" id="spv-explicatie"><span class="ca-mesaj">${esc(st.explicatie_fara_drept)}</span></div>` : "")
        + `<ul class="spv-cuiuri-lista">` + cuiuri.map((c) =>
        `<li class="spv-cui${c.are_drept === false ? " spv-cui-fara" : ""}" data-cui="${esc(c.cui)}">`
        + `<b>${esc(c.nume || "CUI " + c.cui)}</b> · ${c.are_drept === false ? "fără drept în SPV" : (c.are_drept ? "cu drept în SPV" : "nedeterminat: " + esc(c.eroare || ""))}`
        + `${c.verificat_la ? " · verificat " + esc(dataRo(c.verificat_la, "cu_ora")) : ""}</li>`).join("") + `</ul>`;
      msg.after(z);
    }
    if (btn) { btn.textContent = "Reconectează SPV"; btn.className = "buton-secundar"; }
  } else {
    arataMesaj(msg, "Neconectat: facturile nu pleacă în SPV, iar cele de la furnizori nu vin automat.", "info");
  }
  if (btn) btn.addEventListener("click", async () => {
    const text = btn.textContent;
    btn.disabled = true; btn.textContent = "Se conectează…";
    try {
      const r = await api.get("/spv/autorizare");
      if (r && r.url) {
        window.open(r.url, "_blank");
        arataMesaj(msg, "S-a deschis autorizarea ANAF în altă filă. După ce alegi certificatul și confirmi, revino în această filă: dacă ai venit dintr-un formular, „← Înapoi” te duce la el.", "info");
        asteaptaIntoarcerea(zona, st);
      } else { arataMesaj(msg, "Nu s-a putut porni autorizarea.", "eroare"); }
    } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Eroare la pornirea autorizării.", "eroare"); }
    btn.disabled = false; btn.textContent = text;
  });
}

// [deficiența 600, lotul 12] „la orice eșec contabilul se întoarce în iConta cu un mesaj clar”: când ANAF nu-l trimite înapoi (fila ANAF
// rămâne pe „sesiune invalidă” sau pe pagina de ieșire, iar pagina de retur a aplicației nu se deschide deloc), fila iConta.eu află singură,
// la întoarcerea în ea, că nu s-a conectat nimic și spune ce face. Conexiunea nouă = alt acces decât cel de la apăsarea butonului.
export const MESAJ_SPV_NEINCHEIAT = "Conectarea la SPV nu s-a încheiat: ANAF nu a trimis încă înapoi autorizarea. Dacă pagina deschisă de ANAF a rămas pe o eroare (de exemplu „sesiune invalidă”) sau pe pagina de ieșire ANAF, închide-o și apasă din nou „Conectează SPV”. Dacă se repetă, închide toate ferestrele browserului (browserul ține minte certificatul ales) și încearcă din nou.";
export const MESAJ_SPV_INCHEIAT = "Gata: iConta.eu e conectat la SPV pentru cabinetul tău.";

function asteaptaIntoarcerea(zona, inainte) {
  let verific = false;
  const opreste = () => { document.removeEventListener("visibilitychange", laIntoarcere); window.removeEventListener("focus", laIntoarcere); };
  async function laIntoarcere() {
    if (!zona.isConnected) { opreste(); return; }
    if (document.visibilityState === "hidden" || verific) return;
    verific = true;
    try {
      const s = await api.get("/spv/stare");
      if (!zona.isConnected) { opreste(); return; }
      const nou = s && s.conectat && (!inainte.conectat || s.access_expira !== inainte.access_expira);
      if (nou) {
        opreste();
        await panouConectareSPV(zona);
        const m = zona.querySelector("#spv-stare");
        if (m) { const z = document.createElement("div"); z.id = "spv-intors"; m.before(z); arataMesaj(z, MESAJ_SPV_INCHEIAT, "ok"); }
      } else {
        arataMesaj(zona.querySelector("#spv-stare"), MESAJ_SPV_NEINCHEIAT, "info");
      }
    } catch { /* starea nu s-a putut citi: rămâne mesajul de dinainte, următoarea întoarcere o citește din nou */ }
    verific = false;
  }
  document.addEventListener("visibilitychange", laIntoarcere);
  window.addEventListener("focus", laIntoarcere);
}
