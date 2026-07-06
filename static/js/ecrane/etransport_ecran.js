// [etransport] Notificare e-Transport - formular dedicat (structura imbricata), genereaza XML pt SPV
import { api } from "../api.js";

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const JUDETE = ["AB","AR","AG","BC","BH","BN","BT","BV","BR","B","BZ","CS","CL","CJ","CT","CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS","IF","MM","MH","MS","NT","OT","PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN"];

export async function ecranEtransport(corp, nav, t) {
  let bunuri = [{}];
  const ziAzi = new Date().toISOString().slice(0, 10);

  const inp = (id, eticheta, tip = "text", val = "", extra = "") =>
    `<label class="camp">${"<span class=\"camp-eticheta\">" + eticheta + "</span>"}<input type="${tip}" id="${id}" class="camp-input" value="${esc(val)}" ${extra}></label>`;
  const sel = (id, eticheta, optiuni) =>
    `<label class="camp">${"<span class=\"camp-eticheta\">" + eticheta + "</span>"}<select id="${id}" class="camp-input">${optiuni.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("")}</select></label>`;

  const blocLoc = (p, titlu) => `
    <div class="pf-frand-nume" style="margin:12px 0 6px">${titlu}</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px">
      ${sel(p + "-judet", "Judet *", JUDETE.map((j) => [j, j]))}
      ${inp(p + "-localitate", "Localitate *")}
      ${inp(p + "-strada", "Strada *")}
      ${inp(p + "-numar", "Numar")}
    </div>`;

  const randBun = (i) => `
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:8px;padding:8px;border:1px solid var(--linie);border-radius:8px">
      ${sel(`b${i}-cod_scop`, "Scop *", [["101","Comercializare"],["201","Productie"],["301","Gratuitati"],["401","Echipament comercial"],["501","Mijloace fixe"],["601","Uz propriu"],["703","Livrare cu instalare"],["704","Transfer intre gestiuni"],["705","Bunuri puse la dispozitie"],["9901","Altele"]])}
      ${inp(`b${i}-cod_tarifar`, "Cod tarifar (NC) *")}
      ${inp(`b${i}-denumire`, "Denumire marfa *")}
      ${inp(`b${i}-cantitate`, "Cantitate *", "number")}
      ${inp(`b${i}-um`, "UM *", "text", "H87", 'placeholder="H87=buc, KGM=kg"')}
      ${inp(`b${i}-greutate_neta`, "Greutate neta (kg) *", "number")}
      ${inp(`b${i}-greutate_bruta`, "Greutate bruta (kg) *", "number")}
      ${inp(`b${i}-valoare_fara_tva`, "Valoare fara TVA *", "number")}
    </div>`;

  const deseneaza = () => {
    corp.innerHTML = `
      <h2 class="pf-titlu">e-Transport \u00b7 ${esc(t.nume || "")}</h2>
      <p class="pf-intro">Genereaz\u0103 XML-ul notific\u0103rii (v2) pentru \u00eenc\u0103rcare manual\u0103 \u00een SPV. UIT-ul vine de la ANAF dup\u0103 upload.</p>
      <div class="pf-frand" style="display:block">
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px">
          ${sel("et-tip", "Tip operatiune *", [["10","AIC - achizitie intracomunitara"],["20","LIC - livrare intracomunitara"],["30","Transport national"],["40","Import"],["50","Export"],["60","Tranzactie intracom. - intrare"],["70","Tranzactie intracom. - iesire"]])}
          ${inp("et-ref", "Referinta interna")}
        </div>
        <div class="pf-frand-nume" style="margin:14px 0 6px">Bunuri transportate</div>
        <div id="et-bunuri">${bunuri.map((_, i) => randBun(i)).join("")}</div>
        <p><button class="btn btn-secundar" id="et-plus-bun">+ Bun</button></p>
        <div class="pf-frand-nume" style="margin:12px 0 6px">Partener comercial</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px">
          ${inp("p-cod_tara", "Cod tara *", "text", "RO")}
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
        <p style="margin-top:14px"><button class="btn" id="et-genereaza">Genereaz\u0103 XML</button></p>
        <div id="et-mesaj"></div>
      </div>`;

    corp.querySelector("#et-plus-bun").addEventListener("click", () => {
      bunuri.push({});
      const div = document.createElement("div");
      div.innerHTML = randBun(bunuri.length - 1);
      corp.querySelector("#et-bunuri").appendChild(div.firstElementChild);
    });

    corp.querySelector("#et-genereaza").addEventListener("click", async () => {
      const zona = corp.querySelector("#et-mesaj");
      const v = (id) => (corp.querySelector("#" + id) || {}).value || "";
      const loc = (p) => ({ cod_judet: v(p + "-judet"), localitate: v(p + "-localitate"),
        strada: v(p + "-strada"), numar: v(p + "-numar") || undefined });
      const corpReq = {
        ref: v("et-ref") || undefined,
        cod_tip_operatiune: v("et-tip"),
        bunuri: bunuri.map((_, i) => ({
          cod_scop: v(`b${i}-cod_scop`), cod_tarifar: v(`b${i}-cod_tarifar`),
          denumire: v(`b${i}-denumire`), cantitate: parseFloat(v(`b${i}-cantitate`) || "0"),
          um: v(`b${i}-um`), greutate_neta: parseFloat(v(`b${i}-greutate_neta`) || "0"),
          greutate_bruta: parseFloat(v(`b${i}-greutate_bruta`) || "0"),
          valoare_fara_tva: parseFloat(v(`b${i}-valoare_fara_tva`) || "0"),
        })).filter((b) => b.denumire),
        partener: { cod_tara: v("p-cod_tara"), cod: v("p-cod") || undefined, denumire: v("p-denumire") },
        transport: { nr_vehicul: v("t-nr_vehicul"), nr_remorca1: v("t-nr_remorca1") || undefined,
          cod_tara_org: v("t-cod_tara_org"), cod_org: v("t-cod_org"),
          denumire_org: v("t-denumire_org"), data: v("t-data") },
        start: loc("s"), final: loc("f"),
      };
      try {
        const r = await api.post(`/tenants/${t.id}/etransport-xml`, corpReq);
        const blob = new Blob([r.xml], { type: "application/xml" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = `etransport_${ziAzi}.xml`; a.click();
        URL.revokeObjectURL(url);
        zona.innerHTML = `<p class="pf-intro">XML generat si descarcat. ${esc(r.nota || "")}</p>`;
      } catch (e) { zona.innerHTML = `<div class="mig-gol">${esc(e.mesaj || e.message || "eroare")}</div>`; }
    });
  };
  deseneaza();
}

// etransport_std_v1
