// [etransport] Notificare e-Transport - formular dedicat (structura imbricata), genereaza XML pt SPV
// [cap.24 batch 3a] randuri dinamice: model pozitional cu valori + re-randare integrala + stergere/rand +
// validarea per-camp o face BACKENDUL (autoritatea); frontendul consuma 422.campuri si plaseaza prin eroareCamp.
import { api, esc, arataMesaj, confirmaCaseta, dataRo, eroareCamp, curataEroriCamp } from "../api.js?v=c20d0584e2";
const JUDETE = ["AB","AR","AG","BC","BH","BN","BT","BV","BR","B","BZ","CS","CL","CJ","CT","CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS","IF","MM","MH","MS","NT","OT","PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN"];

// Garda de timp UIT client-side (oglinda etransport_send.fereastra_uit) — pt avertisment + blocare buton.
// AIC (tip 10) = achizitie intracomunitara -> UIT valabil 15 zile; rest 5 zile. Backend re-verifica (autoritar).
function _fereastraUit(dataTransport, intracom) {
  if (!dataTransport) return { ok: false, mesaj: "Completează data transportului.", semafor: "gri" };
  const azi = new Date(); azi.setHours(0, 0, 0, 0);
  const dt = new Date(dataTransport + "T00:00:00");
  const zi = 86400000;
  const zileVal = intracom ? 15 : 5;
  const valabilPana = new Date(dt.getTime() + zileVal * zi);
  const zilePanaTransport = Math.round((dt - azi) / zi);
  const zileRamase = Math.round((valabilPana - azi) / zi);
  const preaDevreme = zilePanaTransport > 3;
  const expirat = zileRamase < 0;
  const ok = !preaDevreme && !expirat;
  let mesaj, semafor;
  if (preaDevreme) { mesaj = `Prea devreme: declari cu max 3 zile înainte (transport ${dataRo(dataTransport)}).`; semafor = "rosu"; }
  else if (expirat) { mesaj = `Fereastră expirată: UIT ar fi fost valabil până la ${dataRo(valabilPana.toISOString().slice(0,10))}.`; semafor = "rosu"; }
  else { mesaj = `În fereastră. UIT valabil ${zileVal} zile (până la ${dataRo(valabilPana.toISOString().slice(0,10))}).`; semafor = zileRamase <= 1 ? "galben" : "verde"; }
  return { ok, mesaj, semafor, valabilPana: valabilPana.toISOString().slice(0,10), zileVal, zileRamase };
}

export async function ecranEtransport(corp, nav, t) {
  const ziAzi = new Date().toISOString().slice(0, 10);
  const COD_SCOP = [["101","Comercializare"],["201","Productie"],["301","Gratuitati"],["401","Echipament comercial"],["501","Mijloace fixe"],["601","Uz propriu"],["703","Livrare cu instalare"],["704","Transfer intre gestiuni"],["705","Bunuri puse la dispozitie"],["9901","Altele"]];
  const CAMPURI_BUN = ["cod_scop", "cod_tarifar", "denumire", "cantitate", "um", "greutate_neta", "greutate_bruta", "valoare_fara_tva"];

  // MODEL: array de obiecte simple, POZITIONALE, fara identitati persistente (cap.24 / constrangere batch 3a).
  // Valorile stau in model, NU in DOM: re-randarea integrala la add/delete (cap.24 regula 1) distruge inputurile,
  // altfel, cu valorile tinute in DOM, s-ar pierde ce s-a tastat pe randurile ramase. bunuri[i] tine pozitia i.
  const bunNou = () => ({ cod_scop: "101", cod_tarifar: "", denumire: "", cantitate: "", um: "H87", greutate_neta: "", greutate_bruta: "", valoare_fara_tva: "" });
  let bunuri = [bunNou()];

  const _et = (e) => e.endsWith(" *")
    ? `<span class="camp-eticheta">${e.slice(0, -2)}<span class="oblig">*</span></span>`
    : `<span class="camp-eticheta">${e}</span>`;
  const inp = (id, eticheta, tip = "text", val = "", extra = "") =>
    `<label class="camp">${_et(eticheta)}<input type="${tip}" id="${id}" class="camp-input" value="${esc(val)}" ${extra}></label>`;
  const sel = (id, eticheta, optiuni, val = "") =>
    `<label class="camp">${_et(eticheta)}<select id="${id}" class="camp-input">${optiuni.map(([v, l]) => `<option value="${v}"${String(v) === String(val) ? " selected" : ""}>${esc(l)}</option>`).join("")}</select></label>`;

  const blocLoc = (p, titlu) => `
    <div class="pf-frand-nume" style="margin:12px 0 6px">${titlu}</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px">
      ${sel(p + "-judet", "Județ *", JUDETE.map((j) => [j, j]))}
      ${inp(p + "-localitate", "Localitate *")}
      ${inp(p + "-strada", "Strada *")}
      ${inp(p + "-numar", "Numar")}
    </div>`;

  // un rand se randeaza DIN MODEL (bunuri[i]); id-urile = pozitia i (cap.24 regula 2). Fiecare rand are stergere.
  const randBun = (i) => {
    const b = bunuri[i];
    return `
    <div class="grila-campuri grila-campuri-compacta" data-bun="${i}">
      ${sel(`b${i}-cod_scop`, "Scop *", COD_SCOP, b.cod_scop)}
      ${inp(`b${i}-cod_tarifar`, "Cod tarifar (NC) *", "text", b.cod_tarifar)}
      ${inp(`b${i}-denumire`, "Denumire marfă *", "text", b.denumire)}
      ${inp(`b${i}-cantitate`, "Cantitate *", "number", b.cantitate)}
      ${inp(`b${i}-um`, "UM *", "text", b.um, 'placeholder="H87=buc, KGM=kg"')}
      ${inp(`b${i}-greutate_neta`, "Gr. netă (kg) *", "number", b.greutate_neta)}
      ${inp(`b${i}-greutate_bruta`, "Gr. brută (kg) *", "number", b.greutate_bruta)}
      ${inp(`b${i}-valoare_fara_tva`, "Valoare fără TVA *", "number", b.valoare_fara_tva)}
      <p style="margin:4px 0 2px"><button type="button" class="buton-sters b-sterge" data-bun="${i}">× Șterge bunul ${i + 1}</button></p>
    </div>`;
  };

  // re-randare INTEGRALA din model (cap.24 regula 1): NU se muta/insereaza/sterge noduri DOM individual.
  const deseneazaBunuri = () => {
    const cont = corp.querySelector("#et-bunuri");
    if (!cont) return;
    cont.innerHTML = bunuri.map((_, i) => randBun(i)).join("");
    bunuri.forEach((_, i) => legaRand(i));
  };

  // inputurile scriu in MODEL (nu re-randeaza -> fara pierdere de focus la tastare); stergerea splice + re-randare.
  const legaRand = (i) => {
    const cont = corp.querySelector("#et-bunuri");
    CAMPURI_BUN.forEach((camp) => {
      const el = cont.querySelector(`#b${i}-${camp}`);
      if (!el) return;
      const ev = el.tagName === "SELECT" ? "change" : "input";
      el.addEventListener(ev, () => { bunuri[i][camp] = el.value; });
    });
    const del = cont.querySelector(`.b-sterge[data-bun="${i}"]`);
    if (del) del.addEventListener("click", () => { bunuri.splice(i, 1); deseneazaBunuri(); });
  };

  const v = (id) => (corp.querySelector("#" + id) || {}).value || "";

  // corpul trimis la backend. NU se filtreaza niciun rand (cap.24 regula 2): lista trimisa = lista randata.
  // Un rand incomplet pleaca la validare si se raporteaza langa campul lui, nu dispare tacit.
  const construiesteCorp = () => {
    const loc = (p) => ({ cod_judet: v(p + "-judet"), localitate: v(p + "-localitate"),
      strada: v(p + "-strada"), numar: v(p + "-numar") || undefined });
    return {
      ref: v("et-ref") || undefined,
      cod_tip_operatiune: v("et-tip"),
      bunuri: bunuri.map((b) => ({
        cod_scop: b.cod_scop, cod_tarifar: b.cod_tarifar,
        denumire: b.denumire, cantitate: parseFloat(b.cantitate || "0"),
        um: b.um, greutate_neta: parseFloat(b.greutate_neta || "0"),
        greutate_bruta: parseFloat(b.greutate_bruta || "0"),
        valoare_fara_tva: parseFloat(b.valoare_fara_tva || "0"),
      })),
      partener: { cod_tara: v("p-cod_tara"), cod: v("p-cod") || undefined, denumire: v("p-denumire") },
      transport: { nr_vehicul: v("t-nr_vehicul"), nr_remorca1: v("t-nr_remorca1") || undefined,
        cod_tara_org: v("t-cod_tara_org"), cod_org: v("t-cod_org"),
        denumire_org: v("t-denumire_org"), data: v("t-data") },
      start: loc("s"), final: loc("f"),
    };
  };

  // plaseaza erorile field-keyed din raspunsul 422 al backendului (detail.campuri = [{camp, eticheta}], purtate
  // de api.js ca {camp, mesaj}) LANGA campul lor (cap.6 mecanism A). Cele fara #camp in DOM -> B (fallback OBL.).
  const plaseazaErori = (zona, e) => {
    curataEroriCamp(corp);
    const eris = (e && e.erori_campuri) || [];
    const rest = [];
    eris.forEach((x) => { if (!eroareCamp(corp, x.camp, x.mesaj)) rest.push(x.mesaj); });
    if (rest.length) arataMesaj(zona, "Completează câmpurile obligatorii: " + rest.join("; "), "eroare");
    else if (!eris.length) arataMesaj(zona, (e && e.mesaj) || e.message || "eroare", "eroare");
    else arataMesaj(zona, "", "info");
  };

  const deseneaza = () => {
    corp.innerHTML = `
      <h2 class="pf-titlu">e-Transport</h2>
      <p class="pf-intro">Generează XML-ul notificării (v2) pentru încărcare manuală în SPV. UIT-ul vine de la ANAF după upload.</p>
      <div class="pf-frand" style="display:block">
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px">
          ${sel("et-tip", "Tip operațiune *", [["10","AIC - achiziție intracomunitară"],["20","LIC - livrare intracomunitara"],["30","Transport national"],["40","Import"],["50","Export"],["60","Tranzactie intracom. - intrare"],["70","Tranzactie intracom. - iesire"]])}
          ${inp("et-ref", "Referința internă")}
        </div>
        <div class="pf-frand-nume" style="margin:14px 0 6px">Bunuri transportate</div>
        <div id="et-bunuri"></div>
        <p><button type="button" class="buton-secundar" id="et-plus-bun">+ Bun</button></p>
        <div class="pf-frand-nume" style="margin:12px 0 6px">Partener comercial</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px">
          ${inp("p-cod_tara", "Cod țară *", "text", "RO")}
          ${inp("p-cod", "CUI/Cod partener")}
          ${inp("p-denumire", "Denumire *")}
        </div>
        <div class="pf-frand-nume" style="margin:12px 0 6px">Transport</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px">
          ${inp("t-nr_vehicul", "Nr. vehicul *", "text", "", 'placeholder="B123ABC"')}
          ${inp("t-nr_remorca1", "Nr. remorca")}
          ${inp("t-cod_tara_org", "Tara transportator *", "text", "RO")}
          ${inp("t-cod_org", "CUI transportator *")}
          ${inp("t-denumire_org", "Denumire transportator *")}
          ${inp("t-data", "Data transport *", "date", ziAzi)}
        </div>
        ${blocLoc("s", "Loc de pornire")}
        ${blocLoc("f", "Loc de sosire")}
        <div id="et-fereastra" style="margin-top:12px"></div>
        <p style="margin-top:8px">
          <button type="button" class="buton-primar" id="et-trimite">Trimite UIT în SPV</button>
          <button type="button" class="buton-secundar" id="et-genereaza" style="margin-left:8px">Doar generează XML (manual)</button>
        </p>
        <div id="et-mesaj"></div>
        <div class="pf-frand-nume" style="margin:18px 0 6px">UIT-uri trimise</div>
        <div id="et-trimiteri"><p class="ecran-nota">Se încarcă…</p></div>
      </div>`;

    deseneazaBunuri();

    corp.querySelector("#et-plus-bun").addEventListener("click", () => {
      bunuri.push(bunNou());
      deseneazaBunuri();
    });

    // SEMAFOR DE TIMP (fereastra UIT) + blocarea butonului Trimite daca in afara ferestrei
    const updateFereastra = () => {
      const zf = corp.querySelector("#et-fereastra");
      const btn = corp.querySelector("#et-trimite");
      const f = _fereastraUit(v("t-data"), v("et-tip") === "10");
      const cul = { verde: "var(--verde)", galben: "var(--galben)", rosu: "var(--rosu-semafor)", gri: "var(--gri-semafor)" }[f.semafor];
      zf.innerHTML = `<span class="fd-stare" style="color:${cul}">Fereastră UIT: ${esc(f.mesaj)}</span>`;
      btn.disabled = !f.ok;
      btn.title = f.ok ? "" : f.mesaj;
    };
    corp.querySelector("#et-tip").addEventListener("change", updateFereastra);
    corp.querySelector("#t-data").addEventListener("change", updateFereastra);
    updateFereastra();

    corp.querySelector("#et-genereaza").addEventListener("click", async () => {
      const zona = corp.querySelector("#et-mesaj");
      curataEroriCamp(corp);
      arataMesaj(zona, "", "info");
      try {
        const r = await api.post(`/tenants/${t.id}/etransport-xml`, construiesteCorp());
        const blob = new Blob([r.xml], { type: "application/xml" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = `etransport_${ziAzi}.xml`; a.click();
        URL.revokeObjectURL(url);
        zona.innerHTML = `<p class="pf-intro">XML generat și descărcat. ${esc(r.nota || "")}</p>`;
      } catch (e) { plaseazaErori(zona, e); }
    });

    corp.querySelector("#et-trimite").addEventListener("click", () => {
      const zona = corp.querySelector("#et-mesaj");
      const f = _fereastraUit(v("t-data"), v("et-tip") === "10");
      if (!f.ok) { arataMesaj(zona, f.mesaj, "avert"); return; }   // poarta de timp (backend re-verifica)
      confirmaCaseta(zona, `Trimiți notificarea UIT în SPV? Se validează întâi pe TEST. ${f.mesaj}`, async () => {
        curataEroriCamp(corp);
        arataMesaj(zona, "Se validează pe TEST și se trimite…", "info");
        try {
          const r = await api.post(`/tenants/${t.id}/etransport/trimite`, construiesteCorp());
          if (r.stare === "blocat_timp") arataMesaj(zona, "Blocat (fereastră): " + (r.mesaj || ""), "avert");
          else if (r.stare === "nevalidat") arataMesaj(zona, "Structură invalidă — NU s-a trimis:\n" + (r.erori || []).join("\n"), "avert");
          else if (r.stare === "deja_trimisa") arataMesaj(zona, "Deja trimisă (UIT " + (r.uit || "") + ").", "info");
          else if (r.stare === "incarcat") { arataMesaj(zona, "Trimisă. UIT: " + (r.uit || "—") + ".", "ok"); incarcaTrimiteri(); }
          else { arataMesaj(zona, "Răspuns ANAF:\n" + (r.errors || [r.raspuns || "eroare"]).join("\n"), "avert"); incarcaTrimiteri(); }
        } catch (e) { plaseazaErori(zona, e); }
      }, { textOk: "Trimite UIT" });
    });

    incarcaTrimiteri();
  };

  // Lista UIT-uri trimise — semafor de TIMP (valabilitate) SEPARAT de semaforul de trimitere (doua dimensiuni).
  async function incarcaTrimiteri() {
    const zona = corp.querySelector("#et-trimiteri");
    if (!zona) return;
    let lista = [];
    try { const r = await api.get(`/tenants/${t.id}/etransport/trimiteri`); lista = (r && r.trimiteri) || []; } catch { zona.innerHTML = `<p class="ecran-nota">Nu am putut încărca notificările e-Transport.</p>`; return; }
    if (!lista.length) { zona.innerHTML = `<div class="stare-goala stare-goala--inline">Nicio notificare trimisă încă. UIT-ul apare aici după transmitere.</div>`; return; }
    const cul = { verde: "var(--verde)", galben: "var(--galben)", rosu: "var(--rosu-semafor)", gri: "var(--gri-semafor)" };
    const etTimp = { verde: "în valabilitate", galben: "expiră curând", rosu: "EXPIRAT", gri: "—" };
    const etTrim = { verde: "trimisă", rosu: "eroare", gri: "în lucru" };
    zona.innerHTML = `<div class="pf-lista zebra-lista">${lista.map((u) => `
      <div class="pf-frand" style="display:flex;justify-content:space-between;align-items:center">
        <div class="pf-frand-text">
          <div class="pf-frand-nume">${u.uit ? "UIT " + esc(u.uit) : "(fără UIT)"} · transport ${u.data_transport ? dataRo(u.data_transport) : "—"}</div>
          <div class="pf-frand-sub">
            <span style="color:${cul[u.semafor_trimitere]}">trimitere: ${esc(etTrim[u.semafor_trimitere] || u.stare)}</span> ·
            <span style="color:${cul[u.semafor_timp]}">timp: ${esc(etTimp[u.semafor_timp] || "")}${u.zile_ramase != null ? " (" + u.zile_ramase + "z)" : ""}</span>
          </div>
        </div>
      </div>`).join("")}</div>`;
  }
  deseneaza();
}

// etransport_std_v1 · batch 3a: randuri dinamice cap.24 (model pozitional + re-randare + stergere + backend autoritar)
