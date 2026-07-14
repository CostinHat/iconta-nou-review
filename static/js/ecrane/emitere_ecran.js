// emitere_ecran.js  // [p124_orfani]  // [p123_scot_butoane] — emitere facturi (reutilizabil: portal client, gratuit, cabinet).
// Flux:
//   1. daca numerotarea nu e configurata -> intreaba "ai mai emis facturi?"
//      DA -> serie + ultimul numar (continuitate); NU -> serie optionala, start 1
//   2. formular emitere: beneficiar (CUI verificat ANAF) + linii (cota auto) + total live
// Apelare: randeazaEmitere(corp, nav, tenantId, { inapoi, dupaEmitere })
import { api, dataRo } from "../api.js";

export async function randeazaEmitere(corp, nav, tenantId, opt = {}) {
  const inapoi = opt.inapoi || (() => nav && nav.inapoi && nav.inapoi());
  corp.innerHTML = `<p class="ecran-nota">Se \u00eencarc\u0103\u2026</p>`;

  // citesc numerotarea; daca nu e configurata (serie null si urmator 1 fara facturi) -> config
  let num = { serie: null, urmator_numar: 1, configurata: false };
  try { num = await api.get(`/tenants/${tenantId}/facturi/numerotare`); } catch {}

  const neconfigurat = !num.configurata;  // numerotare_configurata_v1
  if (neconfigurat) {
    configureazaNumerotare(corp, nav, tenantId, opt);
  } else {
    formularEmitere(corp, nav, tenantId, num, opt);
  }
}

// ---------- CONFIGURARE NUMEROTARE (o data) ----------
function configureazaNumerotare(corp, nav, tenantId, opt) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || undefined);  // emitere_inapoi_v1
  const inapoi = opt.inapoi || (() => nav.inapoi());
  corp.innerHTML = `
    
    <h2 class="pf-titlu">Configurare emitere</h2>
    <p class="pf-intro">\u00cenainte de prima factur\u0103: numerotarea (ca s\u0103 fie ne\u00eentrerupt\u0103) \u0219i regimul de TVA.</p>
    <div class="em-config-camp" style="margin-bottom:12px">
      <label>Firma e pl\u0103titoare de TVA?<span class="oblig">*</span></label>
      <div class="em-optiuni">
        <button class="buton-secundar em-buton-sec" id="em-tva-da">Da, pl\u0103titoare</button>
        <button class="buton-secundar em-buton-sec" id="em-tva-nu">Nu</button>
      </div>
    </div>
    <div class="em-config">
      <div class="em-intrebare">Ai mai emis facturi p\u00e2n\u0103 acum (\u00een alt program sau pe h\u00e2rtie)?</div>
      <div class="em-optiuni">
        <button class="buton-primar" id="em-da">Da, am mai emis</button>
        <button class="buton-secundar em-buton-sec" id="em-nu">Nu, \u00eencep acum</button>
      </div>
      <div class="em-config-form" id="em-config-form"></div>
    </div>`;

  const zona = corp.querySelector("#em-config-form");
  let platitorTva = null;  // [tva_config_v1] obligatoriu ales inainte de Continua
  const bTvaDa = corp.querySelector("#em-tva-da"), bTvaNu = corp.querySelector("#em-tva-nu");
  bTvaDa.addEventListener("click", () => { platitorTva = true; bTvaDa.classList.add("buton-activ"); bTvaNu.classList.remove("buton-activ"); });
  bTvaNu.addEventListener("click", () => { platitorTva = false; bTvaNu.classList.add("buton-activ"); bTvaDa.classList.remove("buton-activ"); });

  corp.querySelector("#em-da").addEventListener("click", () => {
    zona.innerHTML = `
      <div class="em-config-camp">
        <label>Seria ultimei facturi (dac\u0103 folose\u0219ti, ex: KAI-)</label>
        <input class="pr-input" id="em-serie" placeholder="ex: KAI-" autocomplete="off">
      </div>
      <div class="em-config-camp">
        <label>Num\u0103rul ultimei facturi emise</label>
        <input class="pr-input" id="em-ultim" type="number" placeholder="ex: 147">
      </div>
      <p class="em-hint">Vom continua de la num\u0103rul urm\u0103tor.</p>
      <button class="buton-primar" id="em-salveaza-config">Continu\u0103</button>`;
    zona.querySelector("#em-salveaza-config").addEventListener("click", async () => {
      const serie = zona.querySelector("#em-serie").value.trim() || null;
      if (serie && /^\d+$/.test(serie)) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-). Numărul ultimei facturi se pune în câmpul următor."; return; }
      const ultim = parseInt(zona.querySelector("#em-ultim").value, 10);
      const start = Number.isFinite(ultim) ? ultim + 1 : 1;
      if (platitorTva === null) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Alege dac\u0103 firma e pl\u0103titoare de TVA."; return; }
      await salveazaConfig(tenantId, serie, start, platitorTva);
      randeazaEmitere(corp, nav, tenantId, opt);
    });
  });

  corp.querySelector("#em-nu").addEventListener("click", () => {
    zona.innerHTML = `
      <div class="em-config-camp">
        <label>Serie (op\u021bional, ex: FCT-)</label>
        <input class="pr-input" id="em-serie2" placeholder="las\u0103 gol dac\u0103 nu folose\u0219ti serie" autocomplete="off">
      </div>
      <p class="em-hint">Prima factur\u0103 va avea num\u0103rul 1.</p>
      <button class="buton-primar" id="em-salveaza-config2">Continu\u0103</button>`;
    zona.querySelector("#em-salveaza-config2").addEventListener("click", async () => {
      const serie = zona.querySelector("#em-serie2").value.trim() || null;
      if (serie && /^\d+$/.test(serie)) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Seria conține doar cifre. Seria e un prefix cu litere (ex: KAI- sau FCT-)."; return; }
      if (platitorTva === null) { let m = zona.querySelector(".msg-eroare"); if (!m) { m = document.createElement("p"); m.className = "msg-eroare"; zona.appendChild(m); } m.textContent = "Alege dac\u0103 firma e pl\u0103titoare de TVA."; return; }
      await salveazaConfig(tenantId, serie, 1, platitorTva);
      randeazaEmitere(corp, nav, tenantId, opt);
    });
  });
}

async function salveazaConfig(tenantId, serie, numar_start, platitor_tva) {
  // [tva_config_v1] fara catch mut: esecul configurarii trebuie vazut (DS cap.6)
  await api.put(`/tenants/${tenantId}/facturi/numerotare`, { serie, numar_start });
  if (platitor_tva !== undefined && platitor_tva !== null)
    await api.post(`/tenants/${tenantId}/firma-profil/regim-tva`, { platitor_tva });
}

// ---------- FORMULAR EMITERE ----------
function formularEmitere(corp, nav, tenantId, num, opt) {
  if (nav && nav.setInapoi) nav.setInapoi(opt.inapoi || undefined);  // emitere_inapoi_v1
  let monedaSel = "RON";
  const inapoi = opt.inapoi || (() => nav.inapoi());
  const numarProxim = num.serie ? `${num.serie}${num.urmator_numar}` : `${num.urmator_numar}`;

  corp.innerHTML = `
    
    <div class="pr-cap">
      <h2 class="pf-titlu">Emite factur\u0103</h2>
      <span class="em-numar">Num\u0103r: <b>${numarProxim}</b></span>
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Beneficiar</div>
      <label class="camp-eticheta" for="em-cui">CUI beneficiar</label>
      <div class="em-benef">
        <input class="pr-input em-cui" id="em-cui" placeholder="ex: RO12345678" autocomplete="off">
        <button class="buton-secundar em-buton-sec" id="em-verifica">Verific\u0103 la ANAF</button>  <!-- [p114_buton_anaf] -->
      </div>
      <label class="camp-eticheta" for="em-nume">Denumire beneficiar<span class="oblig">*</span></label>
      <input class="pr-input em-nume" id="em-nume" autocomplete="off">
      <label class="camp-eticheta" for="em-adresa">Adres\u0103 beneficiar (art. 319)</label>
      <input class="pr-input em-adresa" id="em-adresa" autocomplete="off">
      <div class="em-cui-stare" id="em-cui-stare"></div>
    </div>

    <div class="em-sectiune">
      <div class="em-eticheta">Produse \u0219i servicii</div>
      <div class="camp-eticheta">Linie: denumire \u00b7 cantitate \u00b7 pre\u021b unitar <span class="oblig">*</span> <span class="tip-micut">(cota TVA se stabile\u0219te automat din produs)</span></div>
      <div class="em-linii" id="em-linii"></div>
      <button class="buton-secundar em-buton-sec" id="em-add-linie">+ Adaug\u0103 linie</button>
    </div>

    <div class="em-total" id="em-total"></div>
    <div class="em-moneda-rand">
      <label class="em-moneda-eticheta">Moned\u0103</label>
      <select class="em-moneda-select" id="em-moneda">
        <option value="RON" selected>RON (lei)</option>
        <option value="EUR">EUR</option>
        <option value="USD">USD</option>
        <option value="GBP">GBP</option>
        <option value="CHF">CHF</option>
        <option value="HUF">HUF</option>
        <option value="PLN">PLN</option>
      </select>
      <span class="em-moneda-nota" id="em-moneda-nota"></span>
    </div>
    <div class="em-actiuni">
      <select id="em-tip" class="camp-input" style="max-width:180px;margin-right:8px">
        <option value="factura">Factura</option>
        <option value="proforma">Proforma</option>
        <option value="aviz">Aviz insotire</option>
      </select>
      <button class="buton-primar em-emite" id="em-emite">Emite factur\u0103</button>
    </div>
    <div class="em-rezultat" id="em-rezultat"></div>`;

  const zonaLinii = corp.querySelector("#em-linii");
  const linii = [];

  function adaugaLinie() {
    const idx = linii.length;
    linii.push({ descriere: "", cantitate: 1, pret_unitar: 0, cota_tva: null });
    const rand = document.createElement("div");
    rand.className = "em-linie";
    rand.dataset.idx = idx;
    rand.innerHTML = `
      <input class="pr-input em-l-den" placeholder="Denumire (ex: p\u00e2ine, consultan\u021b\u0103)" aria-label="Denumire articol" autocomplete="off">
      <input class="pr-input em-l-cant" type="number" step="0.001" placeholder="Cant." aria-label="Cantitate" title="Cantitate">
      <input class="pr-input em-l-pret" type="number" step="0.01" placeholder="Pre\u021b" aria-label="Pre\u021b unitar" title="Pre\u021b unitar">
      <span class="em-l-cota" title="Cota TVA">\u2014</span>
      <button class="buton-sters em-l-sterge" title="\u0218terge">\u00d7</button>`;
    zonaLinii.appendChild(rand);

    const den = rand.querySelector(".em-l-den");
    const cant = rand.querySelector(".em-l-cant");
    const pret = rand.querySelector(".em-l-pret");
    const cotaEl = rand.querySelector(".em-l-cota");

    let timer = null;
    den.addEventListener("input", () => {
      linii[idx].descriere = den.value.trim();
      linii[idx].cota_tva = null;  // reset -> se repotriveste
      clearTimeout(timer);
      const d = den.value.trim();
      if (d.length < 3) { cotaEl.textContent = "\u2014"; recalc(); return; }
      cotaEl.textContent = "\u2026";
      timer = setTimeout(async () => {
        try {
          const r = await api.post(`/tenants/${tenantId}/produse/potriveste`, { denumire: d });
          if (r && r.ok) {
            linii[idx].cota_tva = r.cota;
            cotaEl.textContent = r.cota === 0 ? "0%" : `${r.cota}%`;
            cotaEl.className = "em-l-cota " + (r.cota === 11 ? "cota-11" : r.cota === 0 ? "cota-0" : "cota-21");
          }
        } catch {}
        recalc();
      }, 550);
    });
    cant.addEventListener("input", () => { linii[idx].cantitate = parseFloat(cant.value) || 0; recalc(); });
    pret.addEventListener("input", () => { linii[idx].pret_unitar = parseFloat(pret.value) || 0; recalc(); });
    rand.querySelector(".em-l-sterge").addEventListener("click", () => {
      linii[idx] = null;
      rand.remove();
      recalc();
    });
  }

  function recalc() {
    let baza = 0, tva = 0;
    linii.forEach((l) => {
      if (!l) return;
      const val = (l.cantitate || 0) * (l.pret_unitar || 0);
      baza += val;
      tva += val * ((l.cota_tva || 0) / 100);
    });
    const total = baza + tva;
    corp.querySelector("#em-total").innerHTML = `
      <div class="em-total-rand"><span>Baz\u0103</span><b>${baza.toLocaleString("ro-RO", {minimumFractionDigits:2, maximumFractionDigits:2})} ${monedaSel}</b></div>
      <div class="em-total-rand"><span>TVA</span><b>${tva.toLocaleString("ro-RO", {minimumFractionDigits:2, maximumFractionDigits:2})} ${monedaSel}</b></div>
      <div class="em-total-rand em-total-mare"><span>Total</span><b>${total.toLocaleString("ro-RO", {minimumFractionDigits:2, maximumFractionDigits:2})} ${monedaSel}</b></div>`;
  }

  corp.querySelector("#em-add-linie").addEventListener("click", adaugaLinie);
  adaugaLinie();  // prima linie
  recalc();

  // verificare CUI
  corp.querySelector("#em-verifica").addEventListener("click", async () => {
    const cui = corp.querySelector("#em-cui").value.trim();
    const stare = corp.querySelector("#em-cui-stare");
    if (!cui) return;
    stare.textContent = "se verific\u0103 la ANAF\u2026";
    stare.className = "em-cui-stare";
    try {
      const r = await api.get(`/tenants/${tenantId}/verifica-cui/${encodeURIComponent(cui)}`);
      if (r && r.gasit) {
        corp.querySelector("#em-nume").value = r.denumire || "";
        if (r.adresa) corp.querySelector("#em-adresa").value = r.adresa;
        // [p113_doar_gri] doar info TVA cu gri, fara verde/bifa/"gasita"
        stare.innerHTML = `<span class="em-cui-info">${r.platitor_tva ? "pl\u0103titor TVA" : "nepl\u0103titor TVA"}</span>`;
        stare.className = "em-cui-stare";
        // [p109_avert_inactiv] avertisment mare pentru firma INACTIVA
        const av = corp.querySelector("#em-avert-inactiv");
        if (av) av.remove();
        if (r.inactiv) {
          const box = document.createElement("div");
          box.id = "em-avert-inactiv";
          box.className = "em-avert-inactiv";
          box.innerHTML = `
            <div class="em-avert-titlu">\u26a0 ATEN\u021aIE: firm\u0103 INACTIV\u0103 fiscal la ANAF</div>
            <div class="em-avert-text">
              Dac\u0103 emi\u021bi factura c\u0103tre aceast\u0103 firm\u0103:<br>
              \u2022 beneficiarul <b>NU \u00ee\u0219i poate deduce cheltuiala \u0219i nici TVA-ul</b> de pe factura ta (art. 11 Cod fiscal);<br>
              \u2022 o firm\u0103 inactiv\u0103 poate fi \u00een curs de dizolvare \u2014 exist\u0103 risc real de <b>neplat\u0103</b>;<br>
              \u2022 tranzac\u021bia poate atrage <b>controale ANAF</b>.<br>
              Verific\u0103 situa\u021bia \u00eenainte de a continua. Po\u021bi emite, dar pe r\u0103spunderea ta.
            </div>`;
          stare.parentNode.insertBefore(box, stare.nextSibling);
        }
      } else {
        stare.textContent = "CUI neg\u0103sit la ANAF";
        stare.className = "em-cui-stare em-cui-rau";
      }
    } catch {
      stare.textContent = "verificarea a e\u0219uat";
      stare.className = "em-cui-stare em-cui-rau";
    }
  });

  // emitere
  // selector moneda -> actualizeaza starea + totalurile + nota
  const selMon = corp.querySelector("#em-moneda");
  const notaMon = corp.querySelector("#em-moneda-nota");
  if (selMon) {
    selMon.addEventListener("change", () => {
      monedaSel = selMon.value || "RON";
      if (notaMon) notaMon.textContent = monedaSel === "RON"
        ? "" : "TVA se converte\u0219te \u00een lei la cursul BNR (art. 319).";
      recalc();
    });
  }

  async function trimiteEmitere(cursManual) {
    const rez = corp.querySelector("#em-rezultat");
    const liniiVal = linii.filter((l) => l && l.descriere && (l.cantitate || 0) > 0);
    if (!liniiVal.length) { rez.textContent = "Adaug\u0103 cel pu\u021bin o linie."; rez.className = "em-rezultat em-rau"; return; }
    const payload = {
      linii: liniiVal.map((l) => ({
        descriere: l.descriere, cantitate: l.cantitate,
        pret_unitar: l.pret_unitar, cota_tva: l.cota_tva,
      })),
      tert_nume: corp.querySelector("#em-nume").value.trim() || null,
      tert_cui: corp.querySelector("#em-cui").value.trim() || null,
      tert_adresa: corp.querySelector("#em-adresa").value.trim() || null,
      moneda: monedaSel,
    };
    if (cursManual != null) payload.curs_manual = cursManual;

    const btn = corp.querySelector("#em-emite");
    if (btn) { btn.disabled = true; btn.textContent = "Se emite\u2026"; }
    const rez2 = corp.querySelector("#em-rezultat");
    try {
      const selTip = corp.querySelector("#em-tip");
      if (selTip) payload.tip = selTip.value;
      const r = await api.post(`/tenants/${tenantId}/facturi/emite`, payload);
      rez2.innerHTML = `\u2713 Factura <b>${r.numar}</b> emis\u0103 \u00b7 total ${Number(r.total).toLocaleString("ro-RO", {minimumFractionDigits:2})} ${monedaSel}. A fost trimis\u0103 c\u0103tre contabil.`;
      rez2.className = "em-rezultat em-bun";
      setTimeout(() => { if (opt.dupaEmitere) opt.dupaEmitere(); }, 1200);
    } catch (e) {
      const det = e && e.mesaj;
      const cursIndisp = e && e.cod === 409 && det && typeof det === "object" && det.cod === "CURS_INDISPONIBIL";
      if (cursIndisp) {
        arataCursIndisponibil(det);
      } else {
        rez2.textContent = "Emiterea a e\u0219uat. \u00cencearc\u0103 din nou.";
        rez2.className = "em-rezultat em-rau";
      }
      if (btn) { btn.disabled = false; btn.textContent = "Emite factur\u0103"; }
    }
  }

  function arataCursIndisponibil(det) {
    const rez = corp.querySelector("#em-rezultat");
    rez.className = "em-rezultat";
    rez.innerHTML = `
      <div class="em-curs-box">
        <div class="em-curs-titlu">\u26a0 Cursul BNR nu e disponibil momentan (${det.moneda}, ${dataRo(det.data)}).</div>
        <div class="em-curs-actiuni">
          <button class="buton-primar em-curs-retry" id="em-curs-retry">Re\u00eencearc\u0103</button>
          <button class="buton-secundar em-buton-sec" id="em-curs-manual">Introdu manual</button>
        </div>
        <div id="em-curs-manual-zona"></div>
      </div>`;
    rez.querySelector("#em-curs-retry").addEventListener("click", () => trimiteEmitere(null));
    rez.querySelector("#em-curs-manual").addEventListener("click", () => {
      const zona = rez.querySelector("#em-curs-manual-zona");
      zona.innerHTML = `
        <div class="em-curs-manual">
          <label>Curs ${det.moneda} \u2192 RON pentru ${dataRo(det.data)}</label>
          <input type="number" step="0.0001" id="em-curs-val" placeholder="ex. 5.2438" class="em-curs-input">
          <button class="buton-primar" id="em-curs-ok">Emite cu acest curs</button>
          <div class="em-curs-avertisment">Introdu cursul BNR valabil pentru data facturii. R\u0103spunderea corectitudinii \u00ee\u021bi revine.</div>
        </div>`;
      zona.querySelector("#em-curs-ok").addEventListener("click", () => {
        const v = parseFloat(zona.querySelector("#em-curs-val").value);
        if (!v || v <= 0) { zona.querySelector("#em-curs-val").focus(); return; }
        trimiteEmitere(v);
      });
    });
  }

  corp.querySelector("#em-emite").addEventListener("click", () => trimiteEmitere(null));
}

// audit_cab_lot1_v1

// emitere_inapoi_v1

// numerotare_configurata_v1

// fara_precompletari_v1
