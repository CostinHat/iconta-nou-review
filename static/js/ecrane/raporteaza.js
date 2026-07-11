// raporteaza.js — cardul Raporteaza (perspectiva utilizatorului care proceseaza).
// Trimite o observatie catre Admin iConta; vede firul cu raspunsuri; bec rosu = raspunsuri necitite.
// Strat 2 (text + fir). Imagini: strat 3.

import { api, dataRo } from "../api.js";

function dataScurta(iso) {
  return dataRo(iso, "cu_ora");
}

export async function randeazaRaporteaza(corp, nav) {
  corp.innerHTML = `
    <p class="mig-intro">Ai observat ceva care nu merge, nu e corect sau nu se intelege? Trimite-ne o sesizare. Iti raspundem aici.</p>

    <div class="rap-nou set-sectiune" style="max-width:640px">
      <div class="set-titlu">Sesizare nouă</div>
      <label class="set-camp">
        <span class="set-eticheta">Ce ai observat?</span>
        <textarea id="rap-text" class="set-input rap-autogrow" rows="6" style="min-height:130px;overflow:hidden;resize:none" placeholder="Descrie ce ai observat, ce nu merge sau ce nu se intelege... (poti lipi o captura de ecran cu Ctrl+V)"></textarea>
      </label>
      <div class="rap-poze" id="rap-poze-noi"></div>
      <p class="ecran-nota" style="margin:0 0 8px">Opțional: atașează capturi de ecran — cu butonul de mai jos sau lipite direct cu Ctrl+V.</p>
      <div class="rap-actiuni" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <button class="buton-primar" id="rap-trimite">Trimite sesizarea</button>
        <button class="buton-secundar" id="rap-add-poza" type="button">Adaugă captură</button>
        <input type="file" id="rap-file" accept="image/png,image/jpeg,image/webp" multiple style="display:none">
      </div>
      <div class="set-mesaj" id="rap-msg"></div>
    </div>

    <div class="rap-titlu-lista">Sesizarile mele</div>
    <div id="rap-lista" class="rap-lista"><div class="rap-gol">Se încarcă...</div></div>
  `;

  const lista = corp.querySelector("#rap-lista");

  // caseta creste automat cu textul, fara limita
  function autoGrow(ta) {
    const ajusteaza = () => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + "px"; };
    ta.addEventListener("input", ajusteaza);
    ajusteaza();
  }
  autoGrow(corp.querySelector("#rap-text"));

  // --- imagini de atasat la sesizarea noua (in memorie pana la trimitere) ---
  let pozeNoi = [];  // {file, url}
  const zonaPoze = corp.querySelector("#rap-poze-noi");
  const inputFile = corp.querySelector("#rap-file");
  const taText = corp.querySelector("#rap-text");

  function randeazaPozeNoi() {
    zonaPoze.innerHTML = pozeNoi.map((p, i) =>
      `<div class="rap-thumb"><img src="${p.url}" alt=""><button class="buton-sters rap-thumb-x" data-i="${i}" type="button">×</button></div>`
    ).join("");
    zonaPoze.querySelectorAll(".rap-thumb-x").forEach((b) => {
      b.addEventListener("click", () => {
        const i = +b.dataset.i;
        URL.revokeObjectURL(pozeNoi[i].url);
        pozeNoi.splice(i, 1);
        randeazaPozeNoi();
      });
    });
  }
  function adaugaPoze(files) {
    for (const f of files) {
      if (!/^image\/(png|jpe?g|webp)$/i.test(f.type)) continue;
      if (f.size > 8 * 1024 * 1024) continue;
      pozeNoi.push({ file: f, url: URL.createObjectURL(f) });
    }
    randeazaPozeNoi();
  }
  corp.querySelector("#rap-add-poza").addEventListener("click", () => inputFile.click());
  inputFile.addEventListener("change", () => { adaugaPoze(inputFile.files); inputFile.value = ""; });
  // paste captura direct in caseta
  taText.addEventListener("paste", (e) => {
    const items = (e.clipboardData || {}).items || [];
    const imgs = [];
    for (const it of items) {
      if (it.type && it.type.indexOf("image") === 0) {
        const f = it.getAsFile();
        if (f) imgs.push(f);
      }
    }
    if (imgs.length) { e.preventDefault(); adaugaPoze(imgs); }
  });

  async function urcaPoze(mesajId, files) {
    for (const f of files) {
      const fd = new FormData();
      fd.append("fisier", f);
      try { await api.postForm(`/raportari/mesaj/${mesajId}/imagine`, fd); } catch {}
    }
  }

  async function incarcaFire() {
    try {
      const r = await api.get("/raportari/eu");
      const fire = (r && r.raportari) || [];
      if (!fire.length) {
        lista.innerHTML = `<div class="rap-gol">Nu ai trimis nicio sesizare încă.</div>`;
        return;
      }
      lista.innerHTML = fire.map(renderFir).join("");
      // legaturi pe fiecare fir: deschidere/raspuns/citire
      fire.forEach((f) => legaFir(f));
    } catch {
      lista.innerHTML = `<div class="rap-gol">Nu am putut încărca sesizarile.</div>`;
    }
  }

  function renderFir(f) {
    const inAsteptare = f.necitite > 0;
    const badge = inAsteptare ? `<span class="rap-badge-pct" title="in asteptarea raspunsului"></span>` : "";
    const stareEt = { noua: "in asteptare", raspuns: "raspuns primit", inchisa: "inchisa" }[f.stare] || f.stare;
    // titlul firului = inceputul primului mesaj (al meu)
    const primul = (f.mesaje.find((m) => m.rol_autor === "utilizator") || f.mesaje[0] || {}).text || "";
    const titlu = primul.length > 70 ? primul.slice(0, 70) + "…" : primul;
    const mesaje = f.mesaje.map((m) => {
      const cls = m.rol_autor === "admin" ? "rap-msg-admin" : "rap-msg-eu";
      const cine = m.rol_autor === "admin" ? "iConta" : "Eu";
      const poze = (m.atasamente || []).map((a) =>
        `<a href="${a.cale}" target="_blank" class="rap-img-link"><img class="rap-img" src="${a.cale}" alt="captura"></a>`
      ).join("");
      return `
        <div class="rap-mesaj ${cls}">
          <div class="rap-mesaj-cap"><b>${cine}</b><span class="rap-mesaj-data">${dataScurta(m.cand)}</span></div>
          <div class="rap-mesaj-text">${escapeHtml(m.text)}</div>
          ${poze ? `<div class="rap-mesaj-poze">${poze}</div>` : ""}
        </div>`;
    }).join("");
    return `
      <div class="rap-fir" data-id="${f.id}">
        <div class="rap-fir-cap" data-rol="cap">
          <span class="rap-fir-subiect">${escapeHtml(titlu || "(sesizare)")}</span>
          ${badge}
          <span class="rap-fir-stare rap-stare-${f.stare}">${stareEt}</span>
          <span class="rap-fir-data">${dataScurta(f.ultim_mesaj_la)}</span>
        </div>
        <div class="rap-fir-corp" style="display:none">
          <div class="rap-mesaje">${mesaje}</div>
          <div class="rap-replica">
            <textarea class="rap-replica-text set-input" rows="2" style="overflow:hidden;resize:none" placeholder="Adaugă un mesaj..."></textarea>
            <button class="buton-primar rap-replica-btn">Trimite</button>
          </div>
        </div>
      </div>`;
  }

  function legaFir(f) {
    const el = lista.querySelector(`.rap-fir[data-id="${f.id}"]`);
    if (!el) return;
    const cap = el.querySelector(".rap-fir-cap");
    const corpFir = el.querySelector(".rap-fir-corp");
    cap.addEventListener("click", () => {
      const deschis = corpFir.style.display !== "none";
      corpFir.style.display = deschis ? "none" : "block";
    });
    const btn = el.querySelector(".rap-replica-btn");
    const ta = el.querySelector(".rap-replica-text");
    if (ta) autoGrow(ta);
    btn.addEventListener("click", async () => {
      const text = (ta.value || "").trim();
      if (!text) return;
      btn.disabled = true;
      try {
        await api.post(`/raportari/${f.id}/mesaj`, { text });
        await incarcaFire();
        // redeschide firul
        const elNou = lista.querySelector(`.rap-fir[data-id="${f.id}"] .rap-fir-corp`);
        if (elNou) elNou.style.display = "block";
      } catch { btn.disabled = false; }
    });
  }

  // trimitere sesizare noua
  corp.querySelector("#rap-trimite").addEventListener("click", async () => {
    const msg = corp.querySelector("#rap-msg");
    const text = corp.querySelector("#rap-text").value.trim();
    msg.className = "set-mesaj";
    if (!text) { msg.textContent = "Scrie ce ai observat."; msg.className = "set-mesaj set-err"; return; }
    msg.textContent = "Se trimite...";
    try {
      const r = await api.post("/raportari", { text });
      // urc pozele la primul mesaj al raportarii
      if (pozeNoi.length && r && r.mesaj_id) {
        msg.textContent = "Se încarcă imaginile...";
        await urcaPoze(r.mesaj_id, pozeNoi.map((p) => p.file));
      }
      msg.textContent = "Sesizare trimisa."; msg.className = "set-mesaj set-ok";
      corp.querySelector("#rap-text").value = "";
      pozeNoi.forEach((p) => URL.revokeObjectURL(p.url));
      pozeNoi = [];
      randeazaPozeNoi();
      await incarcaFire();
    } catch { msg.textContent = "Nu am putut trimite."; msg.className = "set-mesaj set-err"; }
  });

  await incarcaFire();
}

// reactualizeaza badge-ul rosu de pe cardul Raporteaza din desktop (daca e vizibil)
function actualizeazaBadgeCard() {
  document.dispatchEvent(new CustomEvent("raportari:schimbat"));
}

function escapeHtml(s) {
  return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// audit_cab_lot1_v1
