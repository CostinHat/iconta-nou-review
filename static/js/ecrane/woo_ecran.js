// woo_ecran.js — ecranul WooCommerce (config + sincronizare), reutilizabil.  // wc_extras_v1
// Extras din firme.js ca sa fie folosit si de cabinet (firme.js) si de contul gratuit
// (facturi_ecran.js). O singura sursa (regula DS 0a). Semnatura pe tenantId, nu obiect firma.
import { api } from "../api.js";

export async function ecranMagazin(corp, nav, tenantId) {
  let mesajSucces = "";
  async function randeazaPrincipal() {
    nav.setInapoi(undefined);
    corp.innerHTML = '<p class="ecran-nota">Se încarcă...</p>';
    let cfg = { configurat: false, url: null };
    try { cfg = await api.get(`/tenants/${tenantId}/woocommerce/config`); } catch (e) {}
    corp.innerHTML = `
      <h2 class="pf-titlu">Magazin online</h2>
      <p class="pf-intro">Comenzile din WooCommerce devin facturi emise automat (zilnic la 07:30).</p>
      ${mesajSucces ? '<p style="color:var(--verde);font-weight:600;margin:0 0 14px">' + mesajSucces + '</p>' : ""}
      <p style="margin:0 0 16px"><b>Stare:</b> ${cfg.configurat ? "conectat la " + cfg.url : "neconfigurat"}</p>
      ${cfg.configurat ? '<button class="buton-primar" id="wc-sinc" style="margin-bottom:12px">Sincronizează acum</button><br>' : ""}
      <button class="buton-secundar" id="wc-btn-config">${cfg.configurat ? "Modifică configurarea" : "Configurează magazinul"}</button>
      <div class="em-rezultat" id="wc-rezultat"></div>
    `;
    mesajSucces = "";
    corp.querySelector("#wc-btn-config").addEventListener("click", randeazaConfig);
    const zona = corp.querySelector("#wc-rezultat");
    const bs = corp.querySelector("#wc-sinc");
    if (bs) bs.addEventListener("click", async () => {
      zona.innerHTML = `<p class="ecran-nota">Se sincronizeaza...</p>`;
      try {
        const r = await api.post(`/tenants/${tenantId}/woocommerce/sincronizeaza`, {});
        const n = (r.importate || []).length;
        zona.innerHTML = `<span style="color:var(--verde)">${n} facturi importate, ${r.sarite || 0} deja existente.</span>`;
      } catch (e) { zona.innerHTML = `<span style="color:var(--rosu)">${e.mesaj || "eroare"}</span>`; }
    });
  }
  function randeazaConfig() {
    nav.setInapoi(randeazaPrincipal);
    corp.innerHTML = `
      <h2 class="pf-titlu">Configurare magazin</h2>
      <div class="camp" style="margin-bottom:10px">
        <label class="camp-eticheta">URL magazin</label>
        <input class="camp-input" id="wc-url" placeholder="https://magazin.ro" autocomplete="off" autofocus>
      </div>
      <div class="camp" style="margin-bottom:10px">
        <label class="camp-eticheta">Consumer Key</label>
        <input class="camp-input" id="wc-ck" placeholder="ck_..." autocomplete="off">
      </div>
      <div class="camp" style="margin-bottom:14px">
        <label class="camp-eticheta">Consumer Secret</label>
        <input class="camp-input" id="wc-cs" placeholder="cs_..." type="password" autocomplete="off">
      </div>
      <button class="buton-primar" id="wc-salveaza">Salvează</button>
      <button class="btn-link" id="wc-renunta" style="margin-left:10px">Renunță</button>
      <p class="ecran-nota" id="wc-msg" style="margin:10px 0 0"></p>
    `;
    corp.querySelector("#wc-renunta").addEventListener("click", randeazaPrincipal);
    corp.querySelector("#wc-salveaza").addEventListener("click", async () => {
      const msg = corp.querySelector("#wc-msg");
      try {
        await api.put(`/tenants/${tenantId}/woocommerce/config`, {
          url: corp.querySelector("#wc-url").value.trim() || null,
          ck: corp.querySelector("#wc-ck").value.trim() || null,
          cs: corp.querySelector("#wc-cs").value.trim() || null,
        });
        mesajSucces = "Configurare salvata.";
        randeazaPrincipal();
      } catch (e) { msg.innerHTML = '<span class="msg-eroare">' + (e.mesaj || "eroare") + '</span>'; }
    });
  }
  randeazaPrincipal();
}
