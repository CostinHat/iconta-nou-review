// reautentificare.js — sesiunea a expirat ÎN TIMPUL lucrului: parola se cere PESTE ecran, nu pe o pagină nouă.
//
// [comanda Costin 05.10.2026 pct.1a] „un contabil nu pierde niciodată ce a completat — nici la expirarea sesiunii”. Măsurat:
// tokenul Anei a expirat la 24 h după logare, în mijlocul unei facturi; `api.js` făcea `sesiune.iesi()`, aplicația se redesena
// de la zero și factura dispărea. Acum: fereastra de aici (același email, doar parola), token nou fără redesenare
// (`sesiune.reinnoieste`), iar cererea care a primit 401 se reia. „Ieși din cont” rămâne o alegere a omului, nu o urmare.
// Mai multe cereri care primesc 401 deodată așteaptă ACEEAȘI fereastră (o singură promisiune).
import { sesiune } from "./sesiune.js?v=38c3e6f6fe";

let _inCurs = null;

export function ceraReautentificare() {
  if (!_inCurs) _inCurs = _deschide().finally(() => { _inCurs = null; });
  return _inCurs;
}

function _deschide() {
  return new Promise((rezolva) => {
    const u = sesiune.user() || {};
    const ov = document.createElement("div");
    ov.className = "reaut-overlay";  /* fereastra-de-lucru: doar X — are un câmp de parolă; X = „Ieși din cont” */
    ov.innerHTML = `
      <div class="reaut" role="dialog" aria-modal="true" aria-labelledby="reaut-titlu">
        <div class="reaut-cap">
          <h2 class="reaut-titlu" id="reaut-titlu">Sesiunea a expirat</h2>
          <button type="button" class="nav-x" id="reaut-x" aria-label="Ieși din cont"><span aria-hidden="true">✕</span></button>
        </div>
        <p class="ecran-nota">Ce ai completat rămâne pe ecran. Introdu parola și continui exact de unde ai rămas.</p>
        <label class="camp"><span class="camp-eticheta">Email</span>
          <input class="camp-input" id="reaut-email" type="email" readonly></label>
        <label class="camp"><span class="camp-eticheta">Parola</span>
          <input class="camp-input" id="reaut-parola" type="password" autocomplete="current-password"></label>
        <p class="msg-eroare" id="reaut-eroare" role="alert"></p>
        <div class="reaut-bara">
          <button type="button" class="buton-secundar" id="reaut-iesi">Ieși din cont</button>
          <button type="button" class="buton-primar" id="reaut-continua">Continuă</button>
        </div>
      </div>`;
    document.body.appendChild(ov);
    const campEmail = ov.querySelector("#reaut-email");
    campEmail.value = u.email || "";
    if (!u.email) campEmail.readOnly = false;   // sesiune deschisă înainte ca emailul să fie în `user`
    const parola = ov.querySelector("#reaut-parola");
    const eroare = ov.querySelector("#reaut-eroare");
    const btn = ov.querySelector("#reaut-continua");
    const gata = (ok) => { ov.remove(); rezolva(ok); };
    const iesi = () => gata(false);
    const continua = async () => {
      eroare.textContent = "";
      if (!parola.value) { eroare.textContent = "Scrie parola."; parola.focus({ preventScroll: true }); return; }
      btn.disabled = true;
      try {
        const r = await fetch("/auth/login", { method: "POST", headers: { "Content-Type": "application/json" },
                                               body: JSON.stringify({ email: campEmail.value.trim(), parola: parola.value }) });
        let d = null;
        try { d = await r.json(); } catch { d = null; }
        if (!r.ok || !d || !d.token) {
          eroare.textContent = (d && (d.detail || d.mesaj)) || "Nu s-a putut verifica parola. Reîncearcă.";
          btn.disabled = false;
          return;
        }
        if (u.id && d.user && d.user.id !== u.id) {
          // alt cont decât cel al ecranului: ce e pe ecran nu-i aparține — aplicația pornește de la zero pentru el
          ov.remove(); rezolva(false); sesiune.intra(d.token, d.user); return;
        }
        sesiune.reinnoieste(d.token, d.user);
        gata(true);
      } catch {
        eroare.textContent = "Serverul nu răspunde — reîncearcă în câteva momente. Ce ai completat rămâne pe ecran.";
        btn.disabled = false;
      }
    };
    ov.querySelector("#reaut-x").addEventListener("click", iesi);
    ov.querySelector("#reaut-iesi").addEventListener("click", iesi);
    btn.addEventListener("click", continua);
    parola.addEventListener("keydown", (e) => { if (e.key === "Enter") continua(); });
    setTimeout(() => parola.focus({ preventScroll: true }), 0);
  });
}
