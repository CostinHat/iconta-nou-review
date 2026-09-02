// [cm_flux_v1] Concediu medical — introducere certificat + calcul + lista.
// Design System: cap.2 (form la buton), cap.4 (casete date), cap.1 (butoane), cap.5 (confirmaCaseta), cap.6 (mesaj succes).
// Modul ES de sine statator. nav/t/sal vin ca parametri.
import { api, esc, confirmaCaseta, dataRo, bani, pct, eroareCamp, curataEroriCamp } from "../api.js?v=5b2978a5b9";

// [cm_coduri_v1 22.08.2026] Lista de coduri NU mai traieste aici. Denumirea vine din
// nomenclator (`core/nomenclator_cm.py`), procentul din registru (`salarizare.procent_cm`,
// doua variante datate ale OUG 158/2005 art.17(1)), iar eticheta se compune LA RANDARE, pe
// data certificatului. Scrisa de mana, lista omitea 11/91/92 - coduri legale pe care
// aplicatia le accepta - deci bloca introducerea lor. Vezi DECIZII.md D3.
let CM_CODURI_CACHE = null;

async function coduriCM(tenantId, laData) {
  const cheie = laData || "";
  if (CM_CODURI_CACHE && CM_CODURI_CACHE.cheie === cheie) return CM_CODURI_CACHE.lista;
  const q = laData ? `?la_data=${encodeURIComponent(laData)}` : "";
  const r = await api.get(`/tenants/${tenantId}/concedii/coduri${q}`);
  CM_CODURI_CACHE = { cheie, lista: r.coduri || [] };
  return CM_CODURI_CACHE.lista;
}

function optiuniCM(lista) {
  // eticheta se COMPUNE aici: cod + denumire + procent. Niciuna nu e scrisa in fisierul asta.
  return lista.map((c) => {
    const p = c.procent_text ? ` (${esc(c.procent_text)})` : "";
    return `<option value="${esc(c.cod)}">${esc(c.cod)} \u2014 ${esc(c.denumire)}${p}</option>`;
  }).join("");
}

export async function fluxConcediu(nav, t, sal, dupaSalvare) {
  // sal = { id, nume } (salariatul selectat)
  const numeSal = [sal.prenume, sal.nume].filter(Boolean).join(" ") || ("Salariat #" + sal.id);
  nav.mergi("Concediu medical \u2014 " + numeSal, (corp) => randeaza(corp));

  async function randeaza(corp) {
    corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103...</p>`;
    let lista = [];
    try {
      const r = await api.get(`/tenants/${t.id}/salariati/${sal.id}/concedii`);
      lista = (r && r.concedii) || [];
    } catch { corp.innerHTML = `<p class="ecran-nota">Nu am putut încărca concediile medicale.</p>`; return; }

    const randuriLista = !lista.length
      ? `<div class="stare-goala">Niciun concediu medical \u00eenregistrat.</div>`
      : lista.map((c) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(c.serie || "")}${esc(c.numar || "")} \u00b7 cod ${esc(c.cod || "")} \u00b7 ${c.zile || 0} zile</div>
            <div class="pf-frand-sub">${dataRo(c.data_inceput)} \u2192 ${dataRo(c.data_sfarsit)} \u00b7 indemniza\u021bie brut\u0103 ${bani(c.indemnizatie || 0)} lei \u00b7 net ${bani(c.net || 0)} lei</div>
          </div>
          <button class="buton-sters buton-mic" data-sterge="${c.id}">\u0218terge</button>
        </div>`).join("");

    corp.innerHTML = `
      <h2 class="pf-titlu">Concedii medicale</h2>
      <p class="pf-sub">Salariat: <strong>${esc(numeSal)}</strong></p>
      <p class="pf-intro">Certificatele de concediu medical ale salariatului. Prima zi din fiecare certificat nu se pl\u0103te\u0219te (OUG 91/2025, p\u00e2n\u0103 la 31.12.2027).
        <button class="buton-primar" id="cm-nou" style="margin-left:12px">+ Certificat nou</button></p>
      <div id="cm-form-zona"></div>
      <div class="pf-lista">${randuriLista}</div>`;

    corp.querySelector("#cm-nou").addEventListener("click", async () => { await deschideFormular(corp); });

    corp.querySelectorAll("[data-sterge]").forEach((b) => b.addEventListener("click", () => {
      confirmaCaseta(b, "\u0218tergi acest concediu medical? Ac\u021biunea nu poate fi anulat\u0103.", async () => {
        try {
          await api.del(`/tenants/${t.id}/salariati/${sal.id}/concedii/${b.dataset.sterge}`);
          randeaza(corp);
          if (dupaSalvare) dupaSalvare();
        } catch (e) {
          b.insertAdjacentHTML("afterend", `<span class="msg-eroare" style="margin-left:8px">${esc(e.mesaj || "eroare")}</span>`);
        }
      }, { textOk: "\u0218terge" });
    }));
  }

  async function deschideFormular(corp) {
    const zona = corp.querySelector("#cm-form-zona");
    const azi = new Date();
    const optCod = optiuniCM(await coduriCM(t.id, null));
    zona.innerHTML = `
      <div class="cm-form" style="display:block;margin:12px 0;max-width:720px">
        <div class="pf-frand-nume" style="margin-bottom:10px">Certificat nou</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px">
          <label class="camp"><span class="camp-eticheta">Serie</span><input type="text" id="cm-serie" class="camp-input" placeholder="ex. AB"></label>
          <label class="camp"><span class="camp-eticheta">Num\u0103r</span><input type="text" id="cm-numar" class="camp-input" placeholder="ex. 1234567"></label>
          <label class="camp" style="grid-column:span 2"><span class="camp-eticheta">Cod indemniza\u021bie</span><select id="cm-cod" class="camp-input">${optCod}</select></label>
          <label class="camp" id="cm-venit-zona" style="grid-column:span 2;display:none"><span class="camp-eticheta">Venit brut realizat \u00een perioada CM, dup\u0103 reducerea timpului (lei)<span class="oblig">*</span></span><input type="number" id="cm-venit" class="camp-input" min="0" step="0.01"></label>
          <label class="camp" id="cm-urgenta-zona" style="grid-column:span 2;display:none"><span class="camp-eticheta">Cod urgen\u021b\u0103 medico-chirurgical\u0103<span class="oblig">*</span></span><input type="number" id="cm-urgenta" class="camp-input" min="1" max="177" placeholder="1\u2013177"><span class="camp-ajutor">Cod din nomenclatorul urgen\u021belor medico-chirurgicale (HG 423/2020). D112 \u00eel cere obligatoriu la codul 06.</span></label>
          <label class="camp" id="cm-cnp-zona" style="grid-column:span 2;display:none"><span class="camp-eticheta">CNP-ul persoanei \u00eengrijite<span class="oblig">*</span></span><input type="text" id="cm-cnp-ingrijit" class="camp-input" maxlength="13" inputmode="numeric" placeholder="13 cifre"><span class="camp-ajutor">CNP-ul copilului (cod 09/91/92) sau al pacientului cu afec\u021biuni oncologice (cod 17) pentru care s-a eliberat certificatul. D112 \u00eel cere obligatoriu (regula DUK S97).</span></label>
          <label class="camp"><span class="camp-eticheta">Data acord\u0103rii</span><input type="date" id="cm-acord" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Data \u00eenceput<span class="oblig">*</span></span><input type="date" id="cm-inceput" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Data sf\u00e2r\u0219it <span class="oblig">*</span></span><input type="date" id="cm-sfarsit" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Zile lucr\u0103toare CM<span class="oblig">*</span></span><input type="number" id="cm-zile" class="camp-input" min="0" placeholder="ex. 8"></label>
        </div>
        <div class="pf-frand-nume" style="margin:14px 0 6px">Episod de boală</div>
        <label class="set-bifa"><input type="checkbox" id="cm-continuare"> <span>Certificat de continuare (același episod de boală)</span></label>
        <div id="cm-episod-zona" style="display:none;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:8px">
          <label class="camp"><span class="camp-eticheta">Seria certificatului inițial<span class="oblig">*</span></span><input type="text" id="cm-serie-ini" class="camp-input" placeholder="ex. AB"><span class="camp-ajutor">Seria și numărul certificatului INIȚIAL al episodului (tipărite pe certificatul de continuare). Indemnizația se calculează pe durata întregului episod (OUG 158/2005 art.17(1)): adăugarea continuării poate ridica procentul certificatelor anterioare (procentul valabil se vede în dreptul codului).</span></label>
          <label class="camp"><span class="camp-eticheta">Numărul certificatului inițial<span class="oblig">*</span></span><input type="text" id="cm-numar-ini" class="camp-input" placeholder="ex. 1234567"></label>
        </div>
        <div class="pf-frand-nume" style="margin:14px 0 6px">Baza de calcul (ultimele 6 luni)</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px">
          <label class="camp"><span class="camp-eticheta">Venituri brute 6 luni<span class="oblig">*</span></span><input type="number" id="cm-ven6" class="camp-input" step="0.01" placeholder="suma total\u0103"><span class="camp-ajutor">Suma veniturilor brute din ultimele 6 luni lucrate (din statele de plat\u0103). Baza = aceast\u0103 sum\u0103 \u00eemp\u0103r\u021bit\u0103 la zilele lucr\u0103toare.</span></label>
          <label class="camp"><span class="camp-eticheta">Zile lucr\u0103toare 6 luni<span class="oblig">*</span></span><input type="number" id="cm-zile6" class="camp-input" min="1" placeholder="ex. 126"><span class="camp-ajutor">Total zile lucr\u0103toare din acelea\u0219i 6 luni (ex. ~126 pentru 6 luni pline).</span></label>
          <label class="camp"><span class="camp-eticheta">Diagnostic (op\u021bional)</span><input type="text" id="cm-diag" class="camp-input"></label>
          <label class="set-bifa" style="margin-top:18px"><input type="checkbox" id="cm-spital"> <span>Spitalizare (prima zi se plătește)</span></label>
          <label class="set-bifa" style="margin-top:18px"><input type="checkbox" id="cm-program-national"> <span>Pacient inclus în program național de sănătate (D112 D_9a)</span></label>
        </div>
        <p style="margin-top:14px">
          <button class="buton-primar" id="cm-calc">Calculeaz\u0103 \u0219i salveaz\u0103</button>
          <button class="btn-link" id="cm-renunta" style="margin-left:10px">Renun\u021b\u0103</button>
        </p>
        <div id="cm-rezultat"></div>
      </div>`;
    const selCod = zona.querySelector("#cm-cod");
    const venitZona = zona.querySelector("#cm-venit-zona");
    selCod.addEventListener("change", () => { venitZona.style.display = selCod.value === "10" ? "" : "none"; });  // [cod10] camp conditionat
    const urgentaZona = zona.querySelector("#cm-urgenta-zona");
    selCod.addEventListener("change", () => { urgentaZona.style.display = selCod.value === "06" ? "" : "none"; });  // [cod06] D_11 camp conditionat
    const cnpZona = zona.querySelector("#cm-cnp-zona");
    selCod.addEventListener("change", () => { cnpZona.style.display = ["09","91","92","17"].includes(selCod.value) ? "" : "none"; });  // [D_8/D_8a] CNP persoana ingrijita, camp conditionat
    const chkCont = zona.querySelector("#cm-continuare");
    const episodZona = zona.querySelector("#cm-episod-zona");
    chkCont.addEventListener("change", () => { episodZona.style.display = chkCont.checked ? "grid" : "none"; });  // [CM-episod] campuri certificat initial, conditionat


    zona.querySelector("#cm-renunta").addEventListener("click", () => { zona.innerHTML = ""; });

    // Auto-calcul zile lucratoare (FARA sarbatori legale, OUG 158/2005 art.10) intre inceput
    // si sfarsit; contabilul poate suprascrie. Calendarul e pe backend (sursa unica), NU
    // reimplementat in JS cu getDay() - vechiul cod ignora sarbatorile -> zile CM gresite in D112.
    let zileEditateManual = false;
    const inpZile = zona.querySelector("#cm-zile");
    inpZile.addEventListener("input", () => { zileEditateManual = true; });
    const recalcZile = async () => {
      if (zileEditateManual) return;
      const di = zona.querySelector("#cm-inceput").value;
      const ds = zona.querySelector("#cm-sfarsit").value;
      if (!di || !ds || ds < di) return;
      try {
        const r = await api.get(`/util/zile-lucratoare?start=${di}&end=${ds}`);
        if (r && typeof r.zile === "number") inpZile.value = r.zile;
      } catch { /* auto-calcul best-effort; contabilul poate completa manual */ }
    };
    zona.querySelector("#cm-inceput").addEventListener("change", recalcZile);
    zona.querySelector("#cm-sfarsit").addEventListener("change", recalcZile);

    zona.querySelector("#cm-calc").addEventListener("click", async () => {
      const rez = zona.querySelector("#cm-rezultat");
      rez.innerHTML = "";
      curataEroriCamp(zona);
      const inceput = zona.querySelector("#cm-inceput").value;
      const sfarsit = zona.querySelector("#cm-sfarsit").value;
      const zile = parseInt(zona.querySelector("#cm-zile").value, 10);
      const ven6 = parseFloat(zona.querySelector("#cm-ven6").value);
      const zile6 = parseInt(zona.querySelector("#cm-zile6").value, 10);
      const codSel = zona.querySelector("#cm-cod").value;
      const urg = parseInt(zona.querySelector("#cm-urgenta").value, 10);
      const cnpI = (zona.querySelector("#cm-cnp-ingrijit").value || "").trim();
      // [G10 Faza 1] validari preventive COLECTATE (tiparul erori_generare), plasate langa fiecare camp - fara fail-fast
      const eC = [];
      if (!inceput) eC.push(["cm-inceput", "Completează data de început a concediului."]);
      if (!sfarsit) eC.push(["cm-sfarsit", "Completează data de sfârșit a concediului."]);
      else if (inceput && sfarsit < inceput) eC.push(["cm-sfarsit", "Data de sfârșit nu poate fi înaintea datei de început."]);
      if (!zile || zile < 1) eC.push(["cm-zile", "Zilele lucrătoare CM trebuie să fie cel puțin 1."]);
      if (!ven6 || ven6 <= 0) eC.push(["cm-ven6", "Completează veniturile brute pe 6 luni (baza de calcul)."]);
      if (!zile6 || zile6 < 1) eC.push(["cm-zile6", "Completează zilele lucrătoare din cele 6 luni."]);
      if (codSel === "06" && (!urg || urg < 1 || urg > 177)) eC.push(["cm-urgenta", "La codul 06 completează codul de urgență (1–177, HG 423/2020)."]);
      if (["09","91","92","17"].includes(codSel) && !/^\d{13}$/.test(cnpI)) eC.push(["cm-cnp-ingrijit", "La codurile de îngrijire copil (09/91/92) sau pacient oncologic (17) completează CNP-ul persoanei îngrijite (13 cifre) — D112 îl cere obligatoriu."]);
      if (codSel === "10" && !((zona.querySelector("#cm-venit").value || "").trim())) eC.push(["cm-venit", "La codul 10 completează venitul brut realizat în perioada CM."]);
      // [CM-episod] la continuare, seria+numarul certificatului INITIAL sunt obligatorii (episodul se leaga pe ele)
      if (zona.querySelector("#cm-continuare").checked) {
        if (!(zona.querySelector("#cm-serie-ini").value || "").trim()) eC.push(["cm-serie-ini", "Completează seria certificatului inițial al episodului (de pe certificatul de continuare)."]);
        if (!(zona.querySelector("#cm-numar-ini").value || "").trim()) eC.push(["cm-numar-ini", "Completează numărul certificatului inițial al episodului."]);
      }
      if (eC.length) { eC.forEach(([c, t]) => eroareCamp(zona, c, t)); return; }

      const inc = new Date(inceput);
      const payload = {
        serie: zona.querySelector("#cm-serie").value,
        numar: zona.querySelector("#cm-numar").value,
        cod: zona.querySelector("#cm-cod").value,
        cod_urgenta: zona.querySelector("#cm-urgenta").value || null,
        cnp_ingrijit: (zona.querySelector("#cm-cnp-ingrijit").value || "").trim() || null,
        venit_realizat: zona.querySelector("#cm-venit").value || null,
        data_acordare: zona.querySelector("#cm-acord").value || null,
        data_inceput: inceput,
        data_sfarsit: zona.querySelector("#cm-sfarsit").value || null,
        diagnostic: zona.querySelector("#cm-diag").value,
        spitalizare: zona.querySelector("#cm-spital").checked,
        program_national: zona.querySelector("#cm-program-national").checked,  // [D_9a] marcaj program national de sanatate
        zile_cm: zile,
        venituri_6_luni: ven6,
        zile_6_luni: zile6,
        este_continuare: zona.querySelector("#cm-continuare").checked,
        serie_initiala: (zona.querySelector("#cm-serie-ini").value || "").trim() || null,
        numar_initial: (zona.querySelector("#cm-numar-ini").value || "").trim() || null,
        an: inc.getFullYear(),
        luna: inc.getMonth() + 1,
      };
      const btn = zona.querySelector("#cm-calc");
      btn.disabled = true; btn.textContent = "Se salveaz\u0103\u2026";
      try {
        const r = await api.post(`/tenants/${t.id}/salariati/${sal.id}/concedii`, payload);
        const c = r.calcul || {};
        rez.innerHTML = `
          <div class="panou" style="margin-top:12px;max-width:520px">
            <div class="pf-frand-nume" style="color:var(--verde);margin-bottom:8px">\u2713 Concediu salvat</div>
            <div class="pac-rez-rand"><span>Media zilnic\u0103</span><b>${bani(c.media_zilnica || 0)} lei</b></div>
            <div class="pac-rez-rand"><span>Procent</span><b>${pct(c.procent || 0)}</b></div>
            <div class="pac-rez-rand"><span>Zile pl\u0103tite (dup\u0103 diminuare ${c.diminuare ? "1 zi" : "0"})</span><b>${c.zile_platite || 0}</b></div>
            <div class="pac-rez-rand"><span>Suportat angajator (zile 2\u20136)</span><b>${bani(c.brut_ang || 0)} lei</b></div>
            <div class="pac-rez-rand"><span>Suportat FNUASS (din ziua 7)</span><b>${bani(c.brut_fnuass || 0)} lei</b></div>
            <div class="pac-rez-rand" style="border-top:1px solid var(--linie);margin-top:6px;padding-top:6px"><span>Indemniza\u021bie brut\u0103</span><b>${bani(c.brut || 0)} lei</b></div>
            <div class="pac-rez-rand"><span>CASS</span><b>${bani(c.cass || 0)} lei</b></div>
            <div class="pac-rez-rand"><span>Impozit</span><b>${bani(c.impozit || 0)} lei</b></div>
            <div class="pac-rez-rand"><span><b>Net</b></span><b>${bani(c.net || 0)} lei</b></div>
          </div>`;
        // reincarca lista dupa un moment ca sa apara noul concediu
        setTimeout(() => randeaza(corp), 1400);
        if (dupaSalvare) dupaSalvare();
      } catch (e) {
        btn.disabled = false; btn.textContent = "Calculeaz\u0103 \u0219i salveaz\u0103";
        rez.innerHTML = `<span class="msg-eroare">${esc(e.mesaj || "Nu am putut salva concediul.")}</span>`;
      }
    });
  }
}
