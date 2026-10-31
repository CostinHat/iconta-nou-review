// intocmitor_bilant.js — [lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”] „Întocmitorul bilanțului: calitatea
// întocmitorului în profilul cabinetului, interesul public în Date firmă; ambele blochează dacă lipsesc.”
// Întocmitorul e al cabinetului (îl întocmește cabinetul, pentru toate firmele lui): calitatea din nomenclatorul ANAF al bilanțului,
// numele, CIF-ul (cerut la persoanele autorizate CECCAR) și numărul de înregistrare în organizația profesională. Structura ANAF
// (anaf_surse/structura_SC_1225_270126.txt): „20. nume_intocmit … DA”, „21. calit_intocmit … DA Nomenclator calitate - Intocmit”,
// „22. nri_intocmit”, „22a cif_intocmit … daca calit_intocmit=(21,22) atunci cif_intocmit#null altfel cif_intocmit=null”.
// Locul: Setări cont → Date cabinet (`setari.js` îl pune sub numele și CUI-ul cabinetului) și refuzul bilanțului („Deschide Date cabinet”,
// `ecran_destinatie.js`, cheia `date_cabinet`), cu câmpul lipsă adus în vedere (`camp`, id-urile `cab-…`).
// DS: cap.6 (asterisc pe obligatorii, ajutor sub etichetă, refuzul lângă câmp), cap.17 (lista cu „— alege —” când nu e nimic salvat).
import { api, arataMesaj, esc, eroareCamp, curataEroriCamp, alegeDacaLipseste, focusFaraSalt } from "../api.js?v=ec2094fd4f";
import { sesiune } from "../sesiune.js?v=898215e0ee";

export async function panouIntocmitor(zona, opt = {}) {
  zona.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let d;
  try {
    d = await api.get("/cabinet/intocmitor");
  } catch (e) {
    zona.innerHTML = `<div id="cab-msg-intocmitor"></div>`;
    arataMesaj(zona.querySelector("#cab-msg-intocmitor"), (e && e.mesaj) || "Întocmitorul bilanțului nu s-a putut citi.", "eroare");
    return;
  }
  const rol = (sesiune.user() || {}).rol;
  const poateScrie = rol === "admin_firma" || rol === "superadmin";
  const it = d.intocmitor || {};
  const cuCif = (c) => (d.cu_cif || []).includes(Number(c));
  zona.innerHTML = `
    <h3 class="pf-titlu" id="cab-intocmitor-titlu">Întocmitorul bilanțului</h3>
    <p class="pf-intro">Bilanțul firmelor cabinetului poartă întocmitorul lui: calitatea (din nomenclatorul ANAF), numele și, la persoanele
      autorizate CECCAR, CIF-ul. Fără ele, bilanțul nu se generează.</p>
    <div class="grila-doc">
      <label class="camp">
        <span class="camp-eticheta">Calitatea întocmitorului<span class="oblig">*</span></span>
        <select class="camp-input" id="cab-calit_intocmit"${poateScrie ? "" : " disabled"}>${alegeDacaLipseste(it.calit_intocmit)}${(d.calitati || []).map(([k, t]) =>
          `<option value="${esc(k)}"${Number(k) === Number(it.calit_intocmit) ? " selected" : ""}>${esc(t)}</option>`).join("")}</select>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Numele întocmitorului<span class="oblig">*</span></span>
        <span class="camp-ajutor">Numele și prenumele persoanei, sau denumirea cabinetului autorizat (cel mult 75 de caractere).</span>
        <input class="camp-input" id="cab-nume_intocmit" maxlength="75" value="${esc(it.nume_intocmit || "")}"${poateScrie ? "" : " disabled"}>
      </label>
      <label class="camp" id="cab-cif_intocmit-camp"${cuCif(it.calit_intocmit) ? "" : ' style="display:none"'}>
        <span class="camp-eticheta">CIF-ul întocmitorului<span class="oblig">*</span></span>
        <span class="camp-ajutor">Cerut la persoanele fizice și juridice autorizate, membre CECCAR.</span>
        <input class="camp-input" id="cab-cif_intocmit" maxlength="16" value="${esc(it.cif_intocmit || "")}"${poateScrie ? "" : " disabled"}>
      </label>
      <label class="camp">
        <span class="camp-eticheta">Nr. de înregistrare în organizația profesională</span>
        <input class="camp-input" id="cab-nri_intocmit" maxlength="15" value="${esc(it.nri_intocmit || "")}"${poateScrie ? "" : " disabled"}>
      </label>
    </div>
    ${poateScrie
      ? `<button type="button" class="buton-primar" id="cab-salveaza-intocmitor" data-actiune="POST /cabinet/intocmitor">Salvează întocmitorul</button>`
      : `<p class="ecran-nota drept-motiv">Întocmitorul îl completează administratorul cabinetului.</p>`}
    <div id="cab-msg-intocmitor"></div>`;
  const selC = zona.querySelector("#cab-calit_intocmit");
  selC.addEventListener("change", () => {
    zona.querySelector("#cab-cif_intocmit-camp").style.display = cuCif(selC.value) ? "" : "none";
  });
  const tinta = opt.camp ? zona.querySelector("#" + CSS.escape(opt.camp)) : null;
  if (tinta) {
    if (tinta.id === "cab-cif_intocmit") zona.querySelector("#cab-cif_intocmit-camp").style.display = "";
    tinta.scrollIntoView({ block: "center" });
    focusFaraSalt(tinta);
  }
  const b = zona.querySelector("#cab-salveaza-intocmitor");
  if (!b) return;
  b.addEventListener("click", async () => {
    const msg = zona.querySelector("#cab-msg-intocmitor");
    curataEroriCamp(zona);
    b.disabled = true;
    try {
      await api.post("/cabinet/intocmitor", {
        calit_intocmit: selC.value || null,
        nume_intocmit: zona.querySelector("#cab-nume_intocmit").value.trim() || null,
        cif_intocmit: zona.querySelector("#cab-cif_intocmit").value.trim() || null,
        nri_intocmit: zona.querySelector("#cab-nri_intocmit").value.trim() || null,
      });
      await panouIntocmitor(zona, { ...opt, camp: null });
      arataMesaj(zona.querySelector("#cab-msg-intocmitor"), "Întocmitorul bilanțului a fost salvat.", "ok");
      // deschis dintr-un refuz al bilanțului: drumul înapoi, la ecranul de plecare (ca Date firmă, `inapoiLa`)
      if (opt.inapoiLa && opt.nav && opt.nav.inapoi) {
        const bi = document.createElement("button");
        bi.type = "button"; bi.className = "buton-primar"; bi.id = "cab-inapoi-la"; bi.style.marginLeft = "10px";
        bi.textContent = "← Înapoi la " + opt.inapoiLa;
        bi.addEventListener("click", () => opt.nav.inapoi());
        zona.querySelector("#cab-msg-intocmitor").appendChild(bi);
      }
    } catch (e) {
      b.disabled = false;
      const ec = (e && e.erori_campuri) || [];
      // [440] fiecare refuz cu textul lui, lângă câmp ȘI în casetă — nu „vezi mai sus”
      ec.forEach((c) => eroareCamp(zona, "cab-" + c.camp, c.mesaj));
      arataMesaj(msg, "Întocmitorul NU s-a salvat: " + (ec.length ? ec.map((c) => c.mesaj).join(" ") : ((e && e.mesaj) || "eroare.")), "eroare");
    }
  });
}
