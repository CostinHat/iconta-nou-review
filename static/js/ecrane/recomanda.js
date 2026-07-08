// recomanda.js — cardul Recomanda: invita un cabinet in iConta.
// Trimite email(uri) de invitatie cu buton "Incearca iConta".
// "Vezi ce trimite" = preview exact al emailului (acelasi HTML ca cel trimis).
import { api } from "../api.js";

export function randeazaRecomanda(corp, nav) {
  corp.innerHTML = `
    <p class="mig-intro">Invita un cabinet prieten sa incerce iConta. Ii trimitem un email cu o invitatie.</p>
    <div class="set-sectiune" style="max-width:560px">
      <div class="rec-cap">
        <div class="set-titlu">Adrese de email</div>
        <button class="rec-vezi" id="rec-vezi">Vezi ce trimitem</button>
      </div>
      <label class="set-camp">
        <span class="set-eticheta">Email (poti pune mai multe, separate prin virgula sau enter)</span>
        <textarea id="rec-emails" class="set-input" rows="4" placeholder="prieten@exemplu.ro, alt.cabinet@exemplu.ro"></textarea>
      </label>
      <button class="buton-primar" id="rec-trimite">Trimite invitatia</button>
      <div class="set-mesaj" id="rec-msg"></div>
    </div>
  `;

  // Vezi ce trimitem -> modal preview cu HTML-ul exact
  corp.querySelector("#rec-vezi").addEventListener("click", async () => {
    let date;
    try { date = await api.get("/recomanda/preview"); } catch { alert("Nu am putut incarca previzualizarea."); return; }
    if (!date || !date.ok) return;
    const ov = document.createElement("div");
    ov.className = "rec-overlay";
    ov.innerHTML = `
      <div class="rec-modal">
        <div class="rec-modal-cap">
          <div>
            <div class="rec-modal-titlu">Așa arată invitația</div>
            <div class="rec-modal-sub">Subiect: ${(date.subiect||"").replace(/[<>&]/g,"")}</div>
          </div>
          <button class="rec-modal-x" id="rec-modal-x" aria-label="Inchide">✕</button>
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
    msg.className = "set-mesaj";
    if (!emails.length) {
      msg.textContent = "Adauga cel putin o adresa de email.";
      msg.className = "set-mesaj set-err"; return;
    }
    if (emails.length > 20) {
      msg.textContent = "Maxim 20 de adrese odata.";
      msg.className = "set-mesaj set-err"; return;
    }
    msg.textContent = "Se trimite...";
    try {
      const r = await api.post("/recomanda", { emails });
      if (r && r.ok) {
        const trimise = (r.rezultate || []).filter((x) => x.stare === "trimis").length;
        const esuate = (r.rezultate || []).filter((x) => x.stare === "esuat").length;
        msg.textContent = esuate
          ? `${trimise} trimise, ${esuate} esuate.`
          : `Invitatie trimisa catre ${trimise} ${trimise === 1 ? "adresa" : "adrese"}.`;
        msg.className = "set-mesaj " + (esuate ? "set-err" : "set-ok");
        if (!esuate) corp.querySelector("#rec-emails").value = "";
      } else {
        msg.textContent = "Nu am putut trimite."; msg.className = "set-mesaj set-err";
      }
    } catch (e) {
      msg.textContent = "Eroare la trimitere."; msg.className = "set-mesaj set-err";
    }
  });
}
