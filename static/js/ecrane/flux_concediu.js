// [cm_flux_v1] Concediu medical — introducere certificat + calcul + lista.
// Design System: cap.2 (form la buton), cap.4 (casete date), cap.1 (butoane), cap.5 (confirmaCaseta), cap.6 (mesaj succes).
// Modul ES de sine statator. nav/t/sal vin ca parametri.
import { api, esc, confirmaCaseta } from "../api.js";

const CM_CODURI = [
  ["01", "01 — Boală obișnuită (55/65/75%)"],
  ["02", "02 — Accident de muncă (80/100%)"],
  ["03", "03 — Accident în afara muncii (80/100%)"],
  ["04", "04 — Boală profesională (80/100%)"],
  ["05", "05 — Boală infectocontagioasă grupa A (100%)"],
  ["06", "06 — Urgență medico-chirurgicală (100%)"],
  ["07", "07 — Carantină (75%)"],
  ["08", "08 — Maternitate (85%)"],
  ["09", "09 — Îngrijire copil bolnav (85%)"],
  ["12", "12 — Tuberculoză (100%)"],
  ["13", "13 — Boli cardiovasculare (75%)"],
  ["14", "14 — Neoplazii / SIDA (100%)"],
  ["15", "15 — Risc maternal (75%)"],
  ["16", "16 — Boală infectocontagioasă (75%)"],
  ["17", "17 — Reducere cu 1/4 (oncologic) (75%)"],
  ["51", "51 — Izolare (100%)"],
];

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
    } catch {}

    const randuriLista = !lista.length
      ? `<div class="mig-gol">Niciun concediu medical \u00eenregistrat.</div>`
      : lista.map((c) => `
        <div class="pf-frand">
          <div class="pf-frand-text">
            <div class="pf-frand-nume">${esc(c.serie || "")}${esc(c.numar || "")} \u00b7 cod ${esc(c.cod || "")} \u00b7 ${c.zile || 0} zile</div>
            <div class="pf-frand-sub">${esc(String(c.data_inceput || ""))} \u2192 ${esc(String(c.data_sfarsit || ""))} \u00b7 indemniza\u021bie brut\u0103 ${Number(c.indemnizatie || 0).toFixed(2)} lei \u00b7 net ${Number(c.net || 0).toFixed(2)} lei</div>
          </div>
          <button class="buton-sters buton-mic" data-sterge="${c.id}">\u0218terge</button>
        </div>`).join("");

    corp.innerHTML = `
      <h2 class="pf-titlu">Concedii medicale \u2014 ${esc(numeSal)}</h2>
      <p class="pf-intro">Certificatele de concediu medical ale salariatului. Prima zi din fiecare certificat nu se pl\u0103te\u0219te (OUG 91/2025, p\u00e2n\u0103 la 31.12.2027).
        <button class="buton-primar" id="cm-nou" style="margin-left:12px">+ Certificat nou</button></p>
      <div id="cm-form-zona"></div>
      <div class="pf-lista">${randuriLista}</div>`;

    corp.querySelector("#cm-nou").addEventListener("click", () => deschideFormular(corp));

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

  function deschideFormular(corp) {
    const zona = corp.querySelector("#cm-form-zona");
    const azi = new Date();
    const optCod = CM_CODURI.map(([v, txt]) => `<option value="${v}">${txt}</option>`).join("");
    zona.innerHTML = `
      <div class="cm-form" style="display:block;background:#fff;border:1px solid var(--linie);border-radius:var(--raza);padding:16px;margin:12px 0;max-width:720px">
        <div class="pf-frand-nume" style="margin-bottom:10px">Certificat nou</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px">
          <label class="camp"><span class="camp-eticheta">Serie</span><input type="text" id="cm-serie" class="camp-input" placeholder="ex. AB"></label>
          <label class="camp"><span class="camp-eticheta">Num\u0103r</span><input type="text" id="cm-numar" class="camp-input" placeholder="ex. 1234567"></label>
          <label class="camp" style="grid-column:span 2"><span class="camp-eticheta">Cod indemniza\u021bie</span><select id="cm-cod" class="camp-input">${optCod}</select></label>
          <label class="camp"><span class="camp-eticheta">Data acord\u0103rii</span><input type="date" id="cm-acord" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Data \u00eenceput</span><input type="date" id="cm-inceput" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Data sf\u00e2r\u0219it</span><input type="date" id="cm-sfarsit" class="camp-input"></label>
          <label class="camp"><span class="camp-eticheta">Zile lucr\u0103toare CM</span><input type="number" id="cm-zile" class="camp-input" min="0" placeholder="ex. 8"></label>
        </div>
        <div class="pf-frand-nume" style="margin:14px 0 6px">Baza de calcul (ultimele 6 luni)</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px">
          <label class="camp"><span class="camp-eticheta">Venituri brute 6 luni</span><input type="number" id="cm-ven6" class="camp-input" step="0.01" placeholder="suma total\u0103"></label>
          <label class="camp"><span class="camp-eticheta">Zile lucr\u0103toare 6 luni</span><input type="number" id="cm-zile6" class="camp-input" min="1" placeholder="ex. 126"></label>
          <label class="camp"><span class="camp-eticheta">Diagnostic (op\u021bional)</span><input type="text" id="cm-diag" class="camp-input"></label>
          <label class="camp cm-check" style="display:flex;align-items:center;gap:6px;margin-top:18px"><input type="checkbox" id="cm-spital"> <span>Spitalizare (prima zi se pl\u0103te\u0219te)</span></label>
        </div>
        <p style="margin-top:14px">
          <button class="buton-primar" id="cm-calc">Calculeaz\u0103 \u0219i salveaz\u0103</button>
          <button class="btn-link" id="cm-renunta" style="margin-left:10px">Renun\u021b\u0103</button>
        </p>
        <div id="cm-rezultat"></div>
      </div>`;

    zona.querySelector("#cm-renunta").addEventListener("click", () => { zona.innerHTML = ""; });

    zona.querySelector("#cm-calc").addEventListener("click", async () => {
      const rez = zona.querySelector("#cm-rezultat");
      rez.innerHTML = "";
      const inceput = zona.querySelector("#cm-inceput").value;
      const zile = parseInt(zona.querySelector("#cm-zile").value, 10);
      const ven6 = parseFloat(zona.querySelector("#cm-ven6").value);
      const zile6 = parseInt(zona.querySelector("#cm-zile6").value, 10);
      // validari preventive cu mesaj (Design System cap.6)
      if (!inceput) { rez.innerHTML = `<span class="msg-eroare">Completeaz\u0103 data de \u00eenceput a concediului.</span>`; return; }
      if (!zile || zile < 1) { rez.innerHTML = `<span class="msg-eroare">Zilele lucr\u0103toare CM trebuie s\u0103 fie cel pu\u021bin 1.</span>`; return; }
      if (!ven6 || ven6 <= 0) { rez.innerHTML = `<span class="msg-eroare">Completeaz\u0103 veniturile brute pe 6 luni (baza de calcul).</span>`; return; }
      if (!zile6 || zile6 < 1) { rez.innerHTML = `<span class="msg-eroare">Completeaz\u0103 zilele lucr\u0103toare din cele 6 luni.</span>`; return; }

      const inc = new Date(inceput);
      const payload = {
        serie: zona.querySelector("#cm-serie").value,
        numar: zona.querySelector("#cm-numar").value,
        cod: zona.querySelector("#cm-cod").value,
        data_acordare: zona.querySelector("#cm-acord").value || null,
        data_inceput: inceput,
        data_sfarsit: zona.querySelector("#cm-sfarsit").value || null,
        diagnostic: zona.querySelector("#cm-diag").value,
        spitalizare: zona.querySelector("#cm-spital").checked,
        zile_cm: zile,
        venituri_6_luni: ven6,
        zile_6_luni: zile6,
        an: inc.getFullYear(),
        luna: inc.getMonth() + 1,
      };
      const btn = zona.querySelector("#cm-calc");
      btn.disabled = true; btn.textContent = "Se salveaz\u0103\u2026";
      try {
        const r = await api.post(`/tenants/${t.id}/salariati/${sal.id}/concedii`, payload);
        const c = r.calcul || {};
        rez.innerHTML = `
          <div style="background:#fff;border:1px solid var(--linie);border-radius:var(--raza);padding:12px;margin-top:12px;max-width:520px">
            <div class="pf-frand-nume" style="color:#1d7a4d;margin-bottom:8px">\u2713 Concediu salvat</div>
            <div class="pac-rez-rand"><span>Media zilnic\u0103</span><b>${Number(c.media_zilnica || 0).toFixed(2)} lei</b></div>
            <div class="pac-rez-rand"><span>Procent</span><b>${Number(c.procent || 0).toFixed(0)}%</b></div>
            <div class="pac-rez-rand"><span>Zile pl\u0103tite (dup\u0103 diminuare ${c.diminuare ? "1 zi" : "0"})</span><b>${c.zile_platite || 0}</b></div>
            <div class="pac-rez-rand"><span>Suportat angajator (zile 2\u20136)</span><b>${Number(c.brut_ang || 0).toFixed(2)} lei</b></div>
            <div class="pac-rez-rand"><span>Suportat FNUASS (din ziua 7)</span><b>${Number(c.brut_fnuass || 0).toFixed(2)} lei</b></div>
            <div class="pac-rez-rand" style="border-top:1px solid var(--linie);margin-top:6px;padding-top:6px"><span>Indemniza\u021bie brut\u0103</span><b>${Number(c.brut || 0).toFixed(2)} lei</b></div>
            <div class="pac-rez-rand"><span>CASS</span><b>${Number(c.cass || 0).toFixed(2)} lei</b></div>
            <div class="pac-rez-rand"><span>Impozit</span><b>${Number(c.impozit || 0).toFixed(2)} lei</b></div>
            <div class="pac-rez-rand"><span><b>Net</b></span><b>${Number(c.net || 0).toFixed(2)} lei</b></div>
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
