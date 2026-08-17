// recomanda.js — cardul Recomanda: invita un cabinet in iConta.
// Trimite email(uri) de invitatie cu buton "Incearca iConta".
// "Vezi ce trimite" = preview exact al emailului (acelasi HTML ca cel trimis).
import { api, esc, arataMesaj } from "../api.js?v=427bd69bf5";

export function randeazaRecomanda(corp, nav) {
  corp.innerHTML = `
    <p class="mig-intro">Invită un cabinet prieten să încerce iConta.eu. Îi trimitem un email cu o invitație.</p>
    <div class="panou" style="max-width:560px">
      <div class="rec-cap">
        <h3 class="cap-titlu">Adrese de email</h3>
        <button class="buton-secundar rec-vezi" id="rec-vezi">Vezi ce trimitem</button>
      </div>
      <label class="camp">
        <span class="camp-eticheta">Email (poți pune mai multe, separate prin virgulă sau enter)</span>
        <textarea id="rec-emails" class="camp-input" rows="4" placeholder="prieten@exemplu.ro, alt.cabinet@exemplu.ro"></textarea>
      </label>
      <button class="buton-primar" id="rec-trimite">Trimite invitația</button>
      <div id="rec-msg"></div>
    </div>
  `;

  // Vezi ce trimitem -> modal preview cu HTML-ul exact
  corp.querySelector("#rec-vezi").addEventListener("click", async () => {
    let date;
    try { date = await api.get("/recomanda/preview"); } catch { const m = corp.querySelector("#rec-msg"); arataMesaj(m, "Nu am putut încărca previzualizarea.", "eroare"); return; }  // portal_ds_audit_a_v1
    if (!date || !date.ok) return;
    const ov = document.createElement("div");
    ov.className = "rec-overlay";
    ov.innerHTML = `
      <div class="rec-modal">
        <div class="rec-modal-cap">
          <div>
            <div class="rec-modal-titlu">Așa arată invitația</div>
            <div class="rec-modal-sub">Subiect: ${esc(date.subiect)}</div>
          </div>
          <button class="rec-modal-x" id="rec-modal-x" aria-label="Închide">✕</button>
        </div>
        <div class="rec-modal-corp">${date.html || ""}</div>
        <div class="rec-modal-bara"><button class="buton-primar" id="rec-modal-ok">Am înțeles</button></div>
      </div>`;
    document.body.appendChild(ov);
    const inchide = () => ov.remove();
    ov.querySelector("#rec-modal-x").addEventListener("click", inchide);
    ov.querySelector("#rec-modal-ok").addEventListener("click", inchide);
    ov.addEventListener("click", (e) => { if (e.target === ov) inchide(); });
  });

  corp.querySelector("#rec-trimite").addEventListener("click", async () => {
    const msg = corp.querySelector("#rec-msg");
    const raw = corp.querySelector("#rec-emails").value || "";
    const emails = raw.split(/[\s,;]+/).map((e) => e.trim()).filter(Boolean);
    if (!emails.length) {
      arataMesaj(msg, "Adaugă cel puțin o adresă de email.", "eroare"); return;
    }
    if (emails.length > 20) {
      arataMesaj(msg, "Maxim 20 de adrese odată.", "eroare"); return;
    }
    arataMesaj(msg, "Se trimite...", "info");
    try {
      const r = await api.post("/recomanda", { emails });
      if (r && r.ok) {
        const trimise = (r.rezultate || []).filter((x) => x.stare === "trimis").length;
        const esuate = (r.rezultate || []).filter((x) => x.stare === "esuat").length;
        arataMesaj(msg, esuate
          ? `${trimise} trimise, ${esuate} eșuate.`
          : `Invitație trimisă către ${trimise} ${trimise === 1 ? "adresă" : "adrese"}.`, esuate ? "eroare" : "ok");
        if (!esuate) corp.querySelector("#rec-emails").value = "";
      } else {
        arataMesaj(msg, "Nu am putut trimite.", "eroare");
      }
    } catch (e) {
      arataMesaj(msg, "Eroare la trimitere.", "eroare");
    }
  });
}

// portal_ds_audit_b_v1
