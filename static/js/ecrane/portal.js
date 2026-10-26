// portal.js  // [p93_facturi] — desktopul clientului (rol 'client'), READ-ONLY.
// Landing: panou status ANAF (semafor + scadente) sus + carduri de navigatie.
import { api, dataRo, arataMesaj, confirmaCaseta, deschideLupa, esc, bani, baniRotund, CULORI_CARD, semnAjutor, descarca, cate, refuzPeRand } from "../api.js?v=e38843b1ec";  /* generalizare_zi_v1 */
import { sesiune } from "../sesiune.js?v=898215e0ee";
import { randeazaFacturi, monedaScrisa } from "./facturi_ecran.js?v=c5b207b0d7";  // [p116_facturi_modul]; [lotul 13, 559] moneda scrisă ca în Scadențar

const SVG = (d, c) => `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;

const ICON = {
  facturi: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>',
  declaratii: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  povestea: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
  solicitari: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  recomanda: '<path d="M20 12v10H4V12"/><path d="M2 7h20v5H2z"/><path d="M12 22V7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/>',
  documente: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
};

export function desktopPortal(continut, nav) {
  const u = sesiune.user() || {};
  const firma = u.nume_tenant || u.nume_firma || "firma ta";

  const CARDURI = [
    { cheie: "facturi", titlu: "Facturi", icon: "facturi", ...CULORI_CARD.albastru,
      sinteza: "Vizualizează facturile emise și primite." },
    { cheie: "cifre", titlu: "Cifrele firmei", icon: "declaratii", ...CULORI_CARD.verde,
      sinteza: "Rezultat, bani disponibili, de încasat și de plătit" },
    { cheie: "solicitari", titlu: "Solicitări", icon: "solicitari", ...CULORI_CARD.piersica,
      sinteza: "Trimite o solicitare contabilului." },
    { cheie: "declaratii", titlu: "Declarații depuse", icon: "declaratii", ...CULORI_CARD.teal,
      sinteza: "Ce s-a depus la ANAF, cu data și recipisa" },
    /* [lotul 13, 555] cardul promitea „Recipise, balanțe, bilanț”, dar avea numai balanțele și, a doua oară, declarațiile */
    { cheie: "documente", titlu: "Documente", icon: "documente", ...CULORI_CARD.ardezie,
      sinteza: "Balanțele lunare, în PDF" },
    { cheie: "povestea", titlu: "Povestea lunii", icon: "povestea", ...CULORI_CARD.violet,
      sinteza: "Raportul lunar de la contabil" },
    { cheie: "acces-cont", titlu: "Acces cont", icon: "solicitari", ...CULORI_CARD.ardezie,
      sinteza: "Email și acces suplimentar la portal" },
  ];
  const CARD_BON = { cheie: "bon", titlu: "Pozează bon sau chitanță", icon: "facturi", ...CULORI_CARD.piersica,
      sinteza: "Fotografiază documentul, iConta.eu îl citește" };  /* portal_layout_v2 */
  const carduriVizibile = CARDURI;

  continut.innerHTML = `
    ${sesiune.estePreview() ? '<div class="caseta-atentie" style="margin-bottom:12px"><span class="ca-mesaj"><b>Previzualizare — doar vizualizare.</b> Vezi portalul exact ca acest client. Acțiunile (trimitere solicitări, pozare bon, orice input) sunt dezactivate în acest mod.</span></div>' : ""}
    <div class="cab-salut portal-sus" style="display:flex;justify-content:space-between;align-items:flex-end;gap:12px">
      <div>
        <div class="cab-salut-nume">${esc(firma)}</div>
        <div class="cab-salut-sub">Portal Client</div>
      </div>
      <button class="cab-card cab-card-mic accent-recomanda" id="portal-recomanda-mic">
        <div class="cab-card-cap">${SVG(ICON["recomanda"], CULORI_CARD.chihlimbar.fg)}<span class="cab-card-titlu">Recomand\u0103</span></div>
      </button>
    </div>
    <div class="inceput" id="inceput-carduri" hidden></div>
    <div class="cab-grila">
      <div class="pa-status" id="pa-status" style="grid-column: span 2; margin:0"><p class="ecran-nota">Se verifică situația la ANAF...</p></div>
      <div id="pa-bon-slot" style="display:flex"></div>
    </div>
  `;

  const grila = continut.querySelector(".cab-grila");
  // [deficiența 320] clientul din portal: cardul lui de început (telefonul, canalul, ce primește); nu în previzualizare
  if (!sesiune.estePreview()) import("./inceput.js?v=9a8b26bf4b").then((m) => m.cardurileDeInceput(continut.querySelector("#inceput-carduri"), nav)).catch(() => {});
  {
    const c = CARD_BON;
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.cssText = "background:" + c.bg + ";color:" + c.fg + ";flex:1";
    card.innerHTML = '<div class="cab-card-cap">' + SVG(ICON[c.icon], c.fg) + '<span class="cab-card-titlu">' + c.titlu + '</span></div><div class="cab-card-sinteza">' + c.sinteza + '</div>';
    card.addEventListener("click", () => deschideCard(c.cheie, nav));
    continut.querySelector("#pa-bon-slot").appendChild(card);
  }
  continut.querySelector("#portal-recomanda-mic").addEventListener("click", () => nav.deschide("Recomandă", (corp) => ecranRecomanda(corp, nav)));  /* recomanda_mic_portal_v1 */
  carduriVizibile.forEach((c) => {
    const card = document.createElement("button");
    card.className = "cab-card";
    card.style.background = c.bg;
    card.style.color = c.fg;
    card.innerHTML = `
      <div class="cab-card-cap">${SVG(ICON[c.icon], c.fg)}<span class="cab-card-titlu">${c.titlu}</span></div>
      <div class="cab-card-sinteza">${c.sinteza}</div>
    `;
    card.addEventListener("click", () => deschideCard(c.cheie, nav));
    grila.appendChild(card);
  });

  actualizeazaStatusAcasa(continut);
}

function deschideCard(cheie, nav) {
  if (cheie === "facturi") nav.deschide("Facturi", (corp) => deschideFacturi(corp, nav)); /* portal: latime normala 680px, lista nu are nevoie de larg */  // [p116_facturi_modul]
  else if (cheie === "declaratii") nav.deschide("Declarații depuse", (corp) => ecranDeclaratii(corp, nav));
  else if (cheie === "povestea") nav.deschide("Povestea lunii", (corp) => ecranPovestea(corp, nav));
  else if (cheie === "solicitari") nav.deschide("Solicitări", (corp) => ecranSolicitari(corp, nav));  // ICRD_SOLICITARI_FRONT_V1
  else if (cheie === "recomanda") nav.deschide("Recomandă", (corp) => ecranRecomanda(corp, nav));
  else if (cheie === "bon") nav.deschide("Pozează bon sau chitanță", (corp) => ecranBon(corp, nav));
  else if (cheie === "documente") nav.deschide("Documente", (corp) => ecranDocumente(corp, nav));
  else if (cheie === "cifre") nav.deschide("Cifrele firmei", (corp) => ecranCifre(corp, nav));  // portal_kpi_fe_v1
  else if (cheie === "acces-cont") nav.deschide("Acces cont", (corp) => ecranAccesCont(corp, nav));
}
async function ecranAccesCont(corp, nav) {
  corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
  let d;
  try { d = await api.get("/portal/acces-cont"); }
  catch (e) { corp.innerHTML = "<p></p>"; arataMesaj(corp.firstElementChild, e.mesaj || "Eroare la încărcare.", "eroare"); return; }

  let mesajSucces = "";
  function randeazaEcran() {
    nav.setInapoi(undefined);
    const p = d.principal || {};
    corp.innerHTML = `
      ${mesajSucces ? '<p style="color:var(--verde);font-weight:600;margin:0 0 14px">' + mesajSucces + '</p>' : ""}
      <div style="margin-bottom:6px"><b>Adresa de autentificare:</b> ${esc(p.email || "-")}</div>
      <div style="margin-bottom:6px"><b>Adresa la care primești pachetul lunar:</b> ${esc(d.email_pachet || "-")}</div>
      ${d.aceeasi_adresa ? '<p class="ecran-nota" style="margin:0 0 10px">Sunt aceeași adresă acum, dar rămân două câmpuri diferite: schimbând-o pe prima nu se schimbă și a doua. Pentru a doua, spune-i contabilului.</p>' : ""}
      ${d.eu_principal ? '<button class="buton-secundar" id="ac-btn-schimba-email" style="margin-bottom:24px">Schimbă adresa de email</button>' : '<p class="ecran-nota" style="margin:0 0 24px">Doar titularul contului poate schimba acest email.</p>'}
      <h3 style="margin:0 0 8px">Alte persoane cu acces</h3>
      <div id="ac-lista-suplimentar" style="margin-bottom:16px"></div>
      ${d.eu_principal ? '<button class="buton-secundar" id="ac-btn-adauga-acces" data-fara-actiune="portalul clientului: nu e acțiune de cabinet">Adaugă acces altor persoane</button>' : ""}
    `;
    const lista = corp.querySelector("#ac-lista-suplimentar");
    lista.innerHTML = (d.suplimentare || []).map((c) => `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--linie)">
        <span>${esc(c.email)}${c.nume ? " · " + esc(c.nume) : ""}</span>
        ${d.eu_principal ? '<button class="btn-link" data-uid="' + c.id + '">Revocă</button>' : ""}
      </div>`).join("") || '<p class="ecran-nota">Niciun acces suplimentar.</p>';
    if (d.eu_principal) {
      lista.querySelectorAll("[data-uid]").forEach((b) => b.addEventListener("click", () => {
        confirmaCaseta(b.parentElement, "Revoci accesul pentru " + esc(b.previousElementSibling?.textContent || "") + "?", async () => {
          try {
            await api.del("/portal/acces-cont/acces/" + b.dataset.uid);
            d.suplimentare = d.suplimentare.filter((c) => String(c.id) !== b.dataset.uid);
            randeazaEcran();
          } catch (e) { b.parentElement.insertAdjacentHTML("afterend", '<p class="msg-eroare">' + esc(e.mesaj || "Eroare la revocare.") + '</p>'); }
        }, { textOk: "Revocă" });
      }));
      corp.querySelector("#ac-btn-schimba-email").addEventListener("click", randeazaFormEmail);
      corp.querySelector("#ac-btn-adauga-acces").addEventListener("click", randeazaFormAdauga);
    }
  }

  function randeazaFormEmail() {
    nav.setInapoi(randeazaEcran);
    const p = d.principal || {};
    corp.innerHTML = `
      <div class="camp" style="margin-bottom:10px">
        <label for="ac-email-nou-val" class="camp-eticheta">Adresa nouă de email<span class="oblig">*</span></label>
        <input class="camp-input" id="ac-email-nou-val" value="${esc(p.email || "")}" autofocus>
      </div>
      <p class="ecran-nota" style="margin:0 0 14px">Data viitoare când te loghezi, vei primi linkul la această adresă. <b>Pachetul lunar nu urmează schimbarea</b> — el pleacă la adresa firmei, pe care o schimbă contabilul.</p>
      <button class="buton-primar" id="ac-salveaza-email">Salvează</button>
      <button class="btn-link" id="ac-anuleaza-email" style="margin-left:10px">Renunță</button>
      <p class="ecran-nota" id="ac-email-msg" style="margin:10px 0 0"></p>
    `;
    corp.querySelector("#ac-anuleaza-email").addEventListener("click", randeazaEcran);
    corp.querySelector("#ac-salveaza-email").addEventListener("click", async (ev) => {
      const b = ev.currentTarget;
      const msg = corp.querySelector("#ac-email-msg");
      const val = corp.querySelector("#ac-email-nou-val").value.trim();
      b.disabled = true; b.textContent = "Se salvează...";
      try {
        // [R62] Adresa NU se schimba aici: pleaca un link de confirmare pe adresa noua.
        const rasp = await api.put("/portal/acces-cont/email", { email: val });
        d = await api.get("/portal/acces-cont");
        mesajSucces = esc(rasp.mesaj || "Un link de confirmare a fost trimis pe adresa nouă.");
        randeazaEcran();
      } catch (e) { b.disabled = false; b.textContent = "Salvează"; arataMesaj(msg, e.mesaj || "Eroare.", "eroare"); }
    });
  }

  function randeazaFormAdauga() {
    nav.setInapoi(randeazaEcran);
    corp.innerHTML = `
      <div class="camp" style="margin-bottom:10px">
        <label for="ac-email-nou" class="camp-eticheta">Email de invitat</label>
        <input class="camp-input" id="ac-email-nou" placeholder="persoana@exemplu.ro" autofocus>
      </div>
      <p class="ecran-nota" style="margin:0 0 14px">Persoana primește un link de logare, fără parolă.</p>
      <button class="buton-primar" id="ac-adauga">Trimite acces</button>
      <button class="btn-link" id="ac-anuleaza-adauga" style="margin-left:10px">Renunță</button>
      <p class="ecran-nota" id="ac-adauga-msg" style="margin:10px 0 0"></p>
    `;
    corp.querySelector("#ac-anuleaza-adauga").addEventListener("click", randeazaEcran);
    corp.querySelector("#ac-adauga").addEventListener("click", async (ev) => {
      const b = ev.currentTarget;
      const msg = corp.querySelector("#ac-adauga-msg");
      const email = corp.querySelector("#ac-email-nou").value.trim();
      if (!email.includes("@")) { arataMesaj(msg, "Email invalid.", "eroare"); return; }
      b.disabled = true; b.textContent = "Se trimite...";
      try {
        await api.post("/portal/acces-cont/acces", { email });
        d = await api.get("/portal/acces-cont");
        mesajSucces = "Invitație trimisă către " + esc(email) + ".";
        randeazaEcran();
      } catch (e) { b.disabled = false; b.textContent = "Trimite acces"; arataMesaj(msg, e.mesaj || "Eroare.", "eroare"); }
    });
  }

  randeazaEcran();
}

// ---------- PANOU DE PLĂTIT (Acasa) ----------
/* [lotul 13, deficiența 554, comanda Costin 13.1] „Clientul vede codurile și termenele de depunere ale cabinetului («d300», «d394», literă
   mică); decizia din 05.10: restanțele declarațiilor rămân alertă la cabinet. Clientul vede ce are de plătit și până când (TVA, impozit,
   contribuții), cu sume, în cuvintele lui.” Serverul dă rândurile gata (`uc_portal.de_platit`): ce, perioada, termenul, suma din balanța
   notelor validate (sau „o calculează contabilul”). Lista e informația panoului: se vede direct (DS cap.2: „informația de stare esențială”). */
async function actualizeazaStatusAcasa(continut) {
  const zona = continut.querySelector("#pa-status");
  if (!zona) return;
  let d = {};
  try {
    d = await api.get("/portal/acasa");
  } catch {
    zona.innerHTML = "";
    return;
  }
  if (d.mesaj === "vector fiscal necompletat" || d.stare === "gri") {
    zona.innerHTML = `<div class="pa-card pa-neutru">
      <div class="pa-titlu">Situația fiscală se configurează</div>
      <div class="pa-sub">Contabilul tău finalizează încă setarea firmei.</div>
    </div>`;
    return;
  }
  const plati = d.de_platit || [];
  const rand = (x) => `
      <div class="pa-rand">
        <span class="pa-tip">${esc(x.ce)}</span>
        <span class="pa-perioada">${esc(x.perioada || "")}</span>
        <span class="pa-termen">${x.suma != null ? bani(x.suma) + " lei" : "suma o calculează contabilul"} · până pe ${dataRo(x.termen, "zi_luna_text")}</span>
      </div>`;
  zona.innerHTML = `<div class="pa-card pa-neutru" id="pa-card">
    <div class="pa-titlu">${plati.length ? "De plătit la stat" : "Nimic de plătit la stat în perioada următoare"}</div>
    <div class="pa-sub">${plati.length ? "Sumele vin din contabilitatea înregistrată de contabilul tău." : "Când apare o plată, o vezi aici, cu suma și termenul."}</div>
    ${plati.length ? `<div class="pa-lista" id="pa-lista">${plati.map(rand).join("")}</div>` : ""}
  </div>`;
}

// [p107_facturi_meniu] MENIU FACTURI: doua optiuni (Istoric / Emite)
// [p116_facturi_modul] Facturi -> modul reutilizabil facturi_ecran.js
async function deschideFacturi(corp, nav) {
  let tenantId = null;
  try {
    const f = await api.get("/portal/firma");
    tenantId = (f && (f.tenant_id || f.id)) || null;
  } catch {}
  if (!tenantId) {
    const u = sesiune.user() || {};
    tenantId = u.tenant_id || u.tenant || null;
  }
  if (!tenantId) {
    corp.innerHTML = `<p class="msg-eroare">Nu s-a putut identifica firma.</p>`;
    return;
  }
  randeazaFacturi(corp, nav, tenantId, { client: true });  // [p125_portal_curat] portal client
}

// ---------- DECLARATII DEPUSE ----------
/* [lotul 13, deficiența 555] „Rândul arată doar «d406 · depusă» (fără perioadă, dată, recipisă; gol după «·»)”: rândul citea câmpuri pe care
   serverul nu le trimitea. Acum: codul și denumirea formularului, perioada, ziua depunerii și recipisa (`portal_api.declaratii_depuse`). */
function randDeclaratie(d) {
  return `
      <div class="pf-frand">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${esc(d.cod || "")} \u00b7 ${esc(d.perioada || "")}</div>
          <div class="pf-frand-sub">${d.denumire ? esc(d.denumire) + " \u00b7 " : ""}depusă pe ${d.data ? dataRo(d.data) : "o dată necunoscută"}${d.recipisa ? " \u00b7 recipisa " + esc(d.recipisa) : ""}</div>
        </div>
        <span class="pf-frand-ok">\u2713 depusă</span>
      </div>`;
}
async function ecranDeclaratii(corp, nav) {
  nav.setInapoi(undefined);  // portal_ds_audit_a_v1
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  let lista = [], err = null;
  try {
    const r = await api.get("/portal/declaratii");
    lista = (r && r.declaratii) || [];
  } catch (e) { err = e; }
  let corpuri = err
    ? `<p class="msg-eroare">${esc(err.mesaj || "Nu s-au putut încărca declarațiile.")}</p>`
    : !lista.length
    ? `<div class="stare-goala">Nicio declarație depusă încă.</div>`
    : lista.map(randDeclaratie).join("");
  corp.innerHTML = `
    <h2 class="pf-titlu">Declarații depuse</h2>
    <p class="pf-intro">Ce a fost depus la ANAF pentru firma ta.</p>
    <div class="pf-lista zebra-lista">${corpuri}</div>`;
}

// ---------- SOLICITARI (chat cu contabilul) ----------  // ICRD_SOLICITARI_FRONT_V1

async function ecranSolicitari(corp, nav) {
  nav.setInapoi(undefined);  // portal_ds_audit_a_v1
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  await randeazaSolicitari(corp, nav);
}

async function randeazaSolicitari(corp, nav) {
  let lista = [], err = null;
  try {
    const r = await api.get("/portal/solicitari");
    lista = (r && r.solicitari) || [];
  } catch (e) { err = e; }
  let firHtml = err
    ? '<p class="msg-eroare">' + esc(err.mesaj || "Nu s-au putut încărca mesajele.") + '</p>'
    : '<div class="stare-goala">Niciun mesaj încă.</div>';
  if (lista.length) {
    firHtml = lista.map((s) => {
      const cine = s.autor_rol === "cabinet" ? "Contabil" : "Tu";
      return `<div class="sol-rand sol-${s.autor_rol}">
        <div class="sol-mesaj">${esc(s.mesaj)}</div>
        <div class="sol-meta">${cine} · ${dataRo(s.creat_la)}</div>
      </div>`;
    }).join("");
  }
  corp.innerHTML = `
    <h2 class="pf-titlu">Solicitări</h2>
    <p class="pf-intro">Cere ceva contabilului tău.</p>
    <div class="sol-fir" id="sol-fir">${firHtml}</div>
    <div class="sol-trimite">
      <textarea aria-label="Mesajul tău" id="sol-input" placeholder="Scrie un mesaj..." rows="3"></textarea>
      <button class="buton-primar" id="sol-trimite-btn">Trimite</button>
      <div class="msg-eroare" id="sol-msg"></div>
    </div>
  `;
  const fir = corp.querySelector("#sol-fir");
  if (fir) fir.scrollTop = fir.scrollHeight;
  const btn = corp.querySelector("#sol-trimite-btn");
  if (btn) btn.addEventListener("click", async () => {
    const inp = corp.querySelector("#sol-input");
    const txt = ((inp && inp.value) || "").trim();
    if (!txt) { arataMesaj(corp.querySelector("#sol-msg"), "Scrie solicitarea înainte de a o trimite.", "eroare"); return; }
    btn.disabled = true; btn.textContent = "Se trimite...";
    try {
      await api.post("/portal/solicitari", { mesaj: txt });
      await randeazaSolicitari(corp, nav);
    } catch (e) {
      btn.disabled = false; btn.textContent = "Trimite";
      refuzPeRand(btn, e.mesaj || "Nu s-a putut trimite mesajul.");
    }
  });
}

// ---------- POVESTEA LUNII ----------
async function ecranPovestea(corp, nav) {
  nav.setInapoi(undefined);  // portal_ds_audit_a_v1
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  let lista = [], err = null;
  try {
    const r = await api.get("/portal/povesti");
    lista = (r && r.povesti) || [];
  } catch (e) { err = e; }
  if (err) { corp.innerHTML = `<h2 class="pf-titlu">Povestea lunii</h2><p class="msg-eroare">${esc(err.mesaj || "Nu s-au putut încărca rapoartele.")}</p>`; return; }
  if (!lista.length) {
    corp.innerHTML = `
      <h2 class="pf-titlu">Povestea lunii</h2>
      <p class="pf-intro">Raportul lunar de la contabil.</p>
      <div class="stare-goala">Încă nu ai primit niciun raport lunar.</div>`;
    return;
  }
  /* [lotul 13, deficiența 558] „la prima lună nu se face comparație”: `diferenta` lipsește (null) când luna trecută e dinaintea evidenței în
     iConta.eu; povestea scrisă cu alți termeni decât cifrele (ex. „încasări” în loc de „venituri”) sau aprobată pe alte cifre e „retrasă”:
     rândul arată cifrele lunii și spune că textul se reface, nu textul greșit. */
  const textRand = (p) => p.retrasa
    ? `Textul acestei luni a fost retras: folosea alți termeni decât cifrele lunii. Contabilul îl reface. Cifrele lunii: venituri ${bani(p.venituri)} lei, cheltuieli ${bani(p.cheltuieli)} lei, ${p.tip === "pierdere" ? "pierdere" : (p.tip === "profit" ? "profit" : "rezultat")} înainte de impozit ${bani(Math.abs(p.rezultat || 0))} lei.`
    : (p.text || "");
  const fmtDif = (p) => {
    if (typeof p.diferenta !== "number") return "";
    const semn = p.diferenta > 0 ? "+" : "";
    const culoare = p.diferenta > 0 ? "var(--verde)" : (p.diferenta < 0 ? "var(--rosu)" : "var(--gri)");
    return `<span style="color:${culoare};font-weight:600">${semn}${bani(p.diferenta)} lei la rezultatul înainte de impozit, față de luna anterioară</span>`;
  };
  const corpuri = lista.map((p) => `
    <div class="pf-frand">
      <div class="pf-frand-text">
        <div class="pf-frand-nume">${dataRo(`${p.an}-${String(p.luna).padStart(2,"0")}`, "luna_an")}</div>
        <div class="pf-frand-sub">${p.retrasa ? esc(textRand(p)) : esc(p.text || "").slice(0, 80) + "..."}</div>
        <div class="pf-frand-sub">${fmtDif(p)}</div>
      </div>
    </div>`).join("");
  corp.innerHTML = `
    <h2 class="pf-titlu">Povestea lunii</h2>
    <p class="pf-intro">Raportul lunar de la contabil.</p>
    <div class="pf-lista zebra-lista" id="pov-lista">${corpuri}</div>
    <div id="pov-detaliu"></div>`;
  corp.querySelectorAll(".pf-frand").forEach((el, i) => {
    el.style.cursor = "pointer";
    el.addEventListener("click", () => {
      const p = lista[i];
      corp.querySelector("#pov-detaliu").innerHTML = `
        <div class="pov-card">
          <h3>${dataRo(`${p.an}-${String(p.luna).padStart(2,"0")}`, "luna_an")}</h3>
          <div class="pov-text">${esc(textRand(p)).replace(/\n/g, "<br>")}</div>
          ${typeof p.diferenta === "number" ? `<div class="pov-dif">${fmtDif(p)}</div>` : ""}
        </div>`;
    });
  });
}

// ---------- RECOMANDA ----------
async function ecranRecomanda(corp, nav) {
  nav.setInapoi(undefined);  // portal_ds_audit_a_v1
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  let previewHtml = "";
  try {
    const p = await api.get("/portal/recomanda/preview");
    previewHtml = (p && p.html) || "";
  } catch {}
  corp.innerHTML = `
    <h2 class="pf-titlu">Recomandă</h2>
    <p class="pf-intro">Invită un antreprenor prieten să afle despre iConta.eu.</p>
    <div class="pov-card" style="margin-bottom:16px">
      <button type="button" id="rec-vezi-mesaj" class="buton-secundar">Vezi mesajul</button>
      <div id="rec-preview" style="display:none;margin-top:10px;border:1px solid var(--linie);border-radius:var(--raza);padding:16px;background:var(--fundal)">${previewHtml}</div>
    </div>
    <textarea aria-label="Adresele de email ale destinatarilor, separate prin virgulă" id="rec-emails" placeholder="email1@exemplu.ro, email2@exemplu.ro" rows="4"
      style="width:100%;padding:10px;border-radius:var(--raza);border:1px solid var(--linie);font-family:inherit"></textarea>
    <p class="ecran-nota">Separă mai multe adrese prin virgulă. Maxim 10.</p>
    <button class="buton-primar" id="rec-trimite-btn" style="margin-top:14px">Trimite recomandarea</button>
    <div id="rec-rezultat" style="margin-top:16px"></div>
  `;
  const bVezi = corp.querySelector("#rec-vezi-mesaj");
  if (bVezi) bVezi.addEventListener("click", () => {
    const zona = corp.querySelector("#rec-preview");
    zona.style.display = zona.style.display === "none" ? "block" : "none";
  });
  corp.querySelector("#rec-trimite-btn").addEventListener("click", async () => {
    const raw = corp.querySelector("#rec-emails").value || "";
    const emails = raw.split(",").map((e) => e.trim()).filter(Boolean);
    const zona = corp.querySelector("#rec-rezultat");
    if (!emails.length) {
      zona.innerHTML = `<p class="msg-eroare">Scrie cel puțin un email.</p>`;
      return;
    }
    const bTr = corp.querySelector("#rec-trimite-btn");
    bTr.disabled = true; bTr.textContent = "Se trimite...";
    zona.innerHTML = "";
    try {
      const r = await api.post("/portal/recomanda", { emails });
      const rez = (r && r.rezultate) || [];
      bTr.disabled = false; bTr.textContent = "Trimite recomandarea";
      zona.innerHTML = rez.map((x) =>
        `<div class="pf-frand"><div class="pf-frand-text ${x.stare === "trimis" ? "msg-ok" : "msg-eroare"}">${esc(x.email)} — ${x.stare === "trimis" ? "trimis" : x.stare === "dezabonat" ? "nu s-a trimis: adresa s-a dezabonat de la recomandări" : "eșuat"}</div></div>`
      ).join("");
    } catch {
      bTr.disabled = false; bTr.textContent = "Trimite recomandarea";
      zona.innerHTML = `<p class="msg-eroare">A apărut o eroare. Încearcă din nou.</p>`;
    }
  });
}

// ---------- DOCUMENTE: balanțele lunare ----------
/* [lotul 13, deficiențele 555 + 556] Cardul are un singur conținut — balanțele (declarațiile au cardul lor) —, deci se deschide direct pe
   listă, fără meniul cu două opțiuni. Fiecare lună își spune starea: „definitivă” (luna închisă de contabil) sau „provizorie” (încă se
   lucrează la ea, cu câte înregistrări neverificate are): pe 22.10 clientul vedea octombrie, cu 42 de ciorne, ca definitivă. */
async function ecranDocumente(corp, nav) {
  nav.setInapoi(undefined);
  corp.innerHTML = `<p class="ecran-nota">Se încarcă...</p>`;
  let luni = [], err = null;
  try { const r = await api.get("/portal/documente/luni"); luni = (r && r.luni) || []; } catch (e) { err = e; }
  if (err) { corp.innerHTML = `<h2 class="pf-titlu">Balanțe lunare</h2><p class="msg-eroare">${esc(err.mesaj || "Nu s-a putut încărca lista.")}</p>`; return; }
  const stare = (l) => l.definitiva ? "definitivă — luna e închisă de contabil"
    : "provizorie — contabilul încă lucrează la ea" + (l.neverificate ? ` (${cate(l.neverificate, "înregistrare neverificată", "înregistrări neverificate")})` : "");
  const corpuri = !luni.length
    ? `<div class="stare-goala">Nicio lună cu date contabile încă.</div>`
    : luni.map((l) => {
      const [an, ll] = l.luna.split("-");   // pastrat pentru data-bal; eticheta trece prin dataRo (P1b)
      return `
        <div class="pf-frand" data-luna="${an}-${ll}" data-definitiva="${l.definitiva ? "da" : "nu"}">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">Balanța de verificare · ${dataRo(l.luna, "luna_an")}</div>
            <div class="pf-frand-sub">${stare(l)}</div>
          </div>
          <button class="buton-primar" data-bal="${an}-${ll}">Descarcă PDF</button>
        </div>`;
    }).join("");
  corp.innerHTML = `
    <h2 class="pf-titlu">Balanțe lunare</h2>
    <p class="pf-intro">Generate din contabilitate. O lună provizorie se poate schimba până o închide contabilul.</p>
    <div class="pf-lista zebra-lista">${corpuri}</div>`;
  corp.querySelectorAll("[data-bal]").forEach((b) => {
    b.addEventListener("click", async () => {
      const [an, ll] = b.dataset.bal.split("-");
      try {
        await descarca(`/portal/documente/balanta?an=${an}&luna=${parseInt(ll)}`, `balanta_${an}_${ll}.pdf`);
      } catch (e) {
        refuzPeRand(b, (e && (e.mesaj || e.message)) || "eroare");   // [R131]
      }
    });
  });
}
// [bon] Pozeaza bon - OCR cu AI + confirmare client  // bon_flux_e2_v1
let _pozareMesaj = "";  // faza_b_traseu_v1
async function ecranBon(corp, nav) {
  let mesajSucces = "";
  let draft = null;  // { bon_id, bon, avertismente, urls: [obiect URL-uri poze] }

  function curataUrls() {
    if (draft && draft.urls) draft.urls.forEach((u) => URL.revokeObjectURL(u));
  }

  function randeazaPozare() {
    nav.setInapoi(undefined);
    curataUrls(); draft = null;
    corp.innerHTML = `
      <h2 class="pf-titlu">Pozează bon sau chitanță</h2>
      <p class="pf-intro">Fotografiază sau încarcă bonul fiscal ori chitanța. iConta.eu citește documentul automat, apoi tu îl trimiți contabilului.</p>
      ${(mesajSucces || _pozareMesaj) ? '<p style="color:var(--verde);font-weight:600;margin:0 0 14px">' + (mesajSucces || _pozareMesaj) + '</p>' : ""}
      <input type="file" id="bon-fisier" accept="image/*" capture="environment" multiple hidden>
      <input type="file" id="bon-fisier-galerie" accept="image/*" multiple hidden>
      <div id="bon-butoane" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px">
        <button class="buton-primar" id="bon-fotografiaza">Fotografiază documentul</button>
        <button class="buton-secundar" id="bon-incarca">Încarcă din galerie</button>
      </div>
      <div id="bon-rezultat"></div>`;
    mesajSucces = ""; _pozareMesaj = "";
    corp.querySelector("#bon-fotografiaza").addEventListener("click", () => corp.querySelector("#bon-fisier").click());  // ux_login_camera_v1
    corp.querySelector("#bon-incarca").addEventListener("click", () => corp.querySelector("#bon-fisier-galerie").click());
    const laSelectie = async (ev) => {
      const fs = Array.from(ev.target.files);
      if (!fs.length) return;
      corp.querySelectorAll("#bon-butoane button").forEach((b) => { b.disabled = true; });
      const zona = corp.querySelector("#bon-rezultat");
      zona.innerHTML = `<p class="ecran-nota">Se citește documentul…</p>`;
      const fd = new FormData();
      fs.forEach((f) => fd.append("fisiere", f));
      try {
        const r = await api.postForm("/portal/bon", fd);
        // CSP nginx: img-src 'self' data: (fara blob:) -> folosim data:URL prin FileReader, nu createObjectURL.
        const citesteDataUrl = (f) => new Promise((rez, resp) => {
          const fr = new FileReader();
          fr.onload = () => rez(fr.result);
          fr.onerror = () => resp(fr.error || new Error("Nu s-a putut citi fișierul."));
          fr.readAsDataURL(f);
        });
        const urls = await Promise.all(fs.map(citesteDataUrl));
        draft = { bon_id: r.bon_id, bon: r.bon || {}, avertismente: r.avertismente || [], urls };
        nav.mergi("Verific\u0103 documentul", (c) => { corp = c; randeazaConfirmare(); });  // faza_b_traseu_v1
      } catch (e) {
        corp.querySelectorAll("#bon-butoane button").forEach((b) => { b.disabled = false; });
        ev.target.value = "";
        zona.innerHTML = `<p class="msg-eroare">${esc(e.mesaj || "Nu s-a putut citi documentul. Încearcă o poză mai clară.")}</p>`;
      }
    };
    corp.querySelector("#bon-fisier").addEventListener("change", laSelectie);
    corp.querySelector("#bon-fisier-galerie").addEventListener("change", laSelectie);
  }

  function randeazaConfirmare() {
    nav.setInapoi(refaPoza);
    const b = draft.bon;
    const tvaTxt = (b.tva || []).filter((x) => x && x.valoare)
      .map((x) => "TVA " + x.cota + "%: " + bani(x.valoare) + " lei").join(" \u00b7 ");
    const avert = (draft.avertismente || []).map((a) =>
      `<div class="caseta-atentie" style="margin:0 0 12px"><div class="ca-mesaj">${a}</div></div>`).join("");
    corp.innerHTML = `
      <h2 class="pf-titlu">Verifică documentul</h2>
      <p class="pf-intro">Compară cu documentul din mână: poza e întreagă și datele se potrivesc?</p>
      ${avert}
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">
        ${draft.urls.map((u) => `<img src="${u}" alt="document" class="lupa-mini" data-lupa="${u}">`).join("")}
      </div>
      <div class="pf-lista">
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${b.tip === "chitanta" ? "Chitanță" : "Bon fiscal"} \u00b7 ${b.comerciant || "Comerciant necitit"}</div>
            <div class="pf-frand-sub">${b.numar_document ? "nr. " + b.numar_document + " \u00b7 " : ""}${b.data ? dataRo(b.data) : "dată necitită"}${b.cui ? " \u00b7 CUI " + b.cui : ""}${tvaTxt ? " \u00b7 " + tvaTxt : ""}${b.mentiuni ? " \u00b7 " + b.mentiuni : ""}</div>
          </div>
          <span class="pf-frand-suma">${b.total != null ? bani(b.total) + " lei" : "total necitit"}</span>
        </div>
      </div>
      <div style="margin-top:16px">
        <button class="buton-verde" id="bon-trimite">Trimite la contabil</button>
        <button class="buton-secundar" id="bon-refa" style="margin-left:10px">Refă poza</button>
      </div>
      <p class="ecran-nota" id="bon-msg" style="margin:10px 0 0"></p>`;
    corp.querySelector("#bon-trimite").addEventListener("click", async (ev) => {
      const bt = ev.currentTarget, br = corp.querySelector("#bon-refa");
      bt.disabled = true; br.disabled = true; bt.textContent = "Se trimite...";
      try {
        await api.post("/portal/bon/" + draft.bon_id + "/confirma", {});
        _pozareMesaj = "Documentul a plecat la contabil pentru verificare. După ce îl înregistrează, efectul lui se va vedea în «Cifrele firmei».";
        nav.inapoiPas();  // faza_b_traseu_v1
      } catch (e) {
        bt.disabled = false; br.disabled = false; bt.textContent = "Trimite la contabil";
        arataMesaj(corp.querySelector("#bon-msg"), e.mesaj || "Nu s-a putut trimite. Încearcă din nou.", "eroare");
      }
    });
    corp.querySelector("#bon-refa").addEventListener("click", refaPoza);
    corp.querySelectorAll("[data-lupa]").forEach((img) =>
      img.addEventListener("click", () => deschideLupa(img.dataset.lupa)));
  }

  async function refaPoza() {
    if (draft && draft.bon_id) {
      try { await api.del("/portal/bon/" + draft.bon_id); } catch {}
    }
    nav.inapoiPas();  // faza_b_traseu_v1
  }

  randeazaPozare();
}


// ---------- CIFRELE FIRMEI (KPI) ----------  // portal_kpi_fe_v1
/* [lotul 13, deficiențele 553 + 559, comanda Costin 13.1]
   553: „«Profit −6.075 lei» — la rezultat negativ clientul citește «Pierdere» (și e înainte de impozit)”: rândul spune felul rezultatului
   (`kpi.tip`) și suma fără minus; cheltuielile nu cuprind impozitul pe profit / venit (grupa 69), ca rezultatul să fie înainte de impozit.
   559: „De încasat” / „De plătit” = facturile deschise cu nota validată, aceleași rânduri ca Scadențarul portalului: lei separat de euro,
   cu totalul în lei; ce arată balanța peste ele (sold preluat nedefalcat, avans) se spune pe rând, nu se adună tăcut. */
function sumePeMoneda(f) {
  const parti = (f.pe_moneda || []).filter((x) => Number(x.suma) > 0).map((x) => bani(x.suma) + " " + monedaScrisa(x.moneda));
  return parti.length ? parti.join(" + ") : "0 lei";
}
function subFacturi(f) {
  const strain = (f.pe_moneda || []).some((x) => x.moneda !== "RON" && Number(x.suma) > 0);
  const dif = Number(f.fara_factura || 0);
  return `${cate(f.nr || 0, "factură deschisă", "facturi deschise")}, aceleași ca în Scadențar${strain ? " · în total, în lei: " + bani(f.total_lei) + " lei" : ""}` +
    (Math.abs(dif) >= 0.01 ? ` · balanța contabilă arată ${bani(f.balanta)} lei: ${bani(Math.abs(dif))} lei ${dif > 0 ? "nu sunt legați de o factură (sold preluat nedefalcat sau avans)" : "mai puțin decât facturile (încasări sau plăți neîmpărțite pe facturi)"}` : "");
}
async function ecranCifre(corp, nav) {
  nav.setInapoi(undefined);  // portal_ds_audit_a_v1
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;
  let d = null;
  try {
    d = await api.get("/portal/kpi");
  } catch (e) {
    corp.innerHTML = `<p class="msg-eroare">${esc(e.mesaj || e.message || "Nu s-au putut \u00eenc\u0103rca cifrele.")}</p>`;
    return;
  }
  const k = d.kpi || {};
  const lei = (v) => baniRotund(v) + " lei";
  const rand = (eticheta, valoare, culoare, sub, id) => `
    <div class="pf-frand"${id ? ` id="${id}"` : ""}>
      <div class="pf-frand-text"><div class="pf-frand-nume">${eticheta}</div>${sub ? `<div class="pf-frand-sub">${sub}</div>` : ""}</div>
      <span class="pf-frand-suma" style="${culoare ? "color:" + culoare : ""}">${valoare}</span>
    </div>`;
  const felRez = k.tip === "pierdere" ? "Pierdere" : (k.tip === "profit" ? "Profit" : "Rezultat");
  const provizorie = d.luna_definitiva === false
    ? ` Luna ${dataRo(`${d.an}-${String(d.luna).padStart(2, "0")}`, "luna_an")} e încă deschisă: cifrele sunt provizorii${d.neverificate ? ` (${cate(d.neverificate, "înregistrare neverificată", "înregistrări neverificate")} de contabil nu sunt cuprinse)` : ""}.`
    : "";
  corp.innerHTML = `
    <h2 class="pf-titlu">Cifrele firmei</h2>
    <p class="pf-intro" id="cf-perioada">Cumulat de la \u00eenceputul anului, p\u00e2n\u0103 la ${dataRo(`${d.an}-${String(d.luna).padStart(2,"0")}`, "luna_an")}, din înregistrările verificate de contabil.${provizorie}</p>
    <div class="pf-lista">
      ${rand("Venituri", lei(k.venituri))}
      ${rand("Cheltuieli (fără impozitul pe profit sau pe venit)", lei(k.cheltuieli))}
      ${rand(felRez + " înainte de impozit", lei(Math.abs(k.profit || 0)), k.tip === "pierdere" ? "var(--rosu)" : (k.tip === "profit" ? "var(--verde)" : null), "", "cf-rezultat")}
      ${rand("Bani disponibili (cas\u0103 + banc\u0103)", lei(k.cash))}
      ${rand("De \u00eencasat de la clien\u021bi", sumePeMoneda(k.facturi_de_incasat || {}), null, subFacturi(k.facturi_de_incasat || {}), "cf-de-incasat")}
      ${rand("De pl\u0103tit c\u0103tre furnizori", sumePeMoneda(k.facturi_de_platit || {}), null, subFacturi(k.facturi_de_platit || {}), "cf-de-platit")}
    </div>
    <h2 class="pf-titlu" style="margin-top:20px">Previziune bani (8 s\u0103pt\u0103m\u00e2ni) ${semnAjutor("F016")}</h2>
    <p class="pf-intro" id="cf-intro">Estimare pe scaden\u021bele facturilor \u2014 orientativ.</p>
    <div class="pf-lista" id="cf-zona"><p class="ecran-nota">Se \u00eencarc\u0103\u2026</p></div>`;
  incarcaForecast(corp, rand, lei);  // portal_cashflow_fe_v1
}

/* [lotul 13, 553] „În prima săptămână ies 15.423 lei fără explicație (furnizorii sunt 3.000) — fiecare rând spune din ce e format; media
   cheltuielilor lunare «~117 lei» nu se potrivește cu cheltuielile anului”: rândul săptămânii își numește componentele (`componente` de la
   server), iar media spune lunile din care e făcută. Componentele nu poartă „+… lei” (forma încasării pe rând). */
async function incarcaForecast(corp, rand, lei) {  // portal_cashflow_fe_v1
  const zona = corp.querySelector("#cf-zona");
  if (!zona) return;
  let d = null;
  try { d = await api.get("/portal/cashflow"); }
  catch (e) { zona.innerHTML = `<p class="msg-eroare">${esc(e.mesaj || "Previziunea este indisponibilă momentan.")}</p>`; return; }
  const intro = corp.querySelector("#cf-intro");  // portal_cashflow_fe_v2
  if (intro && d.medie_cheltuieli > 0) {
    const ml = d.medie_luni || {};
    const luni = ml.de_la && ml.pana_la && ml.de_la !== ml.pana_la
      ? `lunile ${dataRo(ml.de_la + "-01", "luna_an_numeric")}–${dataRo(ml.pana_la + "-01", "luna_an_numeric")}`
      : `luna ${dataRo((ml.pana_la || ml.de_la) + "-01", "luna_an_numeric")}`;
    intro.textContent = "Estimare pe scaden\u021bele facturilor \u0219i obliga\u021biilor \u2014 presupun\u00e2nd c\u0103 cheltuielile lunare (inclusiv salariile) r\u0103m\u00e2n la ~" +
      lei(d.medie_cheltuieli) + ", media pe " + luni + ".";
  }
  zona.innerHTML = (d.saptamani || []).map((w) => {
    const detaliu = (w.incasari ? "+" + lei(w.incasari) : "") +
      (w.incasari && w.plati ? " / " : "") + (w.plati ? "\u2212" + lei(w.plati) : "");
    const parte = (sens, titlu) => {
      const c = (w.componente || []).filter((x) => x.sens === sens);
      return c.length ? titlu + ": " + c.map((x) => `${esc(x.ce)} ${baniRotund(x.suma)}`).join(", ") : "";
    };
    const din = [parte("+", "Încasări"), parte("-", "Plăți")].filter(Boolean).join(" · ");
    return rand("din " + dataRo(w.de_la, "zi_luna") + (detaliu ? " \u00b7 " + detaliu : ""),
      lei(w.sold), w.sold < 0 ? "var(--rosu)" : null, din);
  }).join("");
}

// portal_culori_v2

// portal_status_in_grila_v1

// portal_ds_audit_b_v1

// bon_flux_e2b_v1

// ux_login_camera_v1

// faza_b_traseu_v1
