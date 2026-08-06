// raporteaza.js — cardul Raporteaza (perspectiva utilizatorului care proceseaza).
// Trimite o observatie catre Admin iConta; vede firul cu raspunsuri; bec rosu = raspunsuri necitite.
// Strat 2 (text + fir). Imagini: strat 3.

import { api, dataRo, arataMesaj, esc } from "../api.js";

function dataScurta(iso) {
  return dataRo(iso, "cu_ora");
}

export async function randeazaRaporteaza(corp, nav) {
  corp.innerHTML = `
    <p class="mig-intro">Ai observat ceva care nu merge, nu e corect sau nu se înțelege? Trimite-ne o sesizare. Îți răspundem aici.</p>

    <div class="rap-nou panou" style="max-width:640px">
      <h3 class="cap-titlu">Sesizare nouă</h3>
      <label class="camp">
        <span class="camp-eticheta">Ce ai observat?</span>
        <textarea id="rap-text" class="camp-input rap-autogrow" rows="6" style="min-height:130px;overflow:hidden;resize:none" placeholder="Descrie ce ai observat, ce nu merge sau ce nu se înțelege... (poți lipi o captură de ecran cu Ctrl+V)"></textarea>
      </label>
      <div class="rap-poze" id="rap-poze-noi"></div>
      <p class="ecran-nota" style="margin:0 0 8px">Opțional: atașează capturi de ecran — cu butonul de mai jos sau lipite direct cu Ctrl+V.</p>
      <div class="rap-actiuni" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <button class="buton-primar" id="rap-trimite">Trimite sesizarea</button>
        <button class="buton-secundar" id="rap-add-poza" type="button">Adaugă captură</button>
        <input type="file" id="rap-file" accept="image/png,image/jpeg,image/webp" multiple style="display:none">
      </div>
      <div id="rap-msg"></div>
    </div>

    <div class="rap-titlu-lista">Sesizările mele</div>
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
    let esuate = 0;
    for (const f of files) {
      const fd = new FormData();
      fd.append("fisier", f);
      try { await api.postForm(`/raportari/mesaj/${mesajId}/imagine`, fd); }
      catch { esuate++; }   /* [B14] nu inghiti: numara esecurile; apelantul semnaleaza pierderea */
    }
    return esuate;
  }

  async function incarcaFire() {
    try {
      const r = await api.get("/raportari/eu");
      const fire = (r && r.raportari) || [];
      window._rapFire = fire;  // [triaj_ai] pollingul verifica reactia AI pe firul cel mai nou
      if (!fire.length) {
        lista.innerHTML = `<div class="rap-gol">Nu ai trimis nicio sesizare încă.</div>`;
        return;
      }
      const inchise = fire.filter((f) => f.stare === "inchisa").length;
      const activeF = fire.filter((f) => window._rapCuInchise || f.stare !== "inchisa");
      lista.innerHTML = activeF.map(renderFir).join("");
      if (inchise) lista.insertAdjacentHTML("beforeend",
        `<button class="btn-link" id="rap-istoric">${window._rapCuInchise ? "Ascunde \u00eenchisele" : `Arat\u0103 \u0219i \u00eenchisele (${inchise})`}</button>`);
      const bi = lista.querySelector("#rap-istoric");
      if (bi) bi.addEventListener("click", () => { window._rapCuInchise = !window._rapCuInchise; incarcaFire(); });
      // legaturi pe fiecare fir: deschidere/raspuns/citire
      fire.forEach((f) => legaFir(f));
    } catch {
      lista.innerHTML = `<div class="rap-gol">Nu am putut încărca sesizarile.</div>`;
    }
  }

  function renderFir(f) {
    const badge = f.stare === "noua"
      ? `<span class="rap-badge-pct" title="în așteptarea răspunsului"></span>`
      : (f.necitite > 0 ? `<span class="rap-badge-pct rap-badge-verde" title="răspuns primit, necitit"></span>` : "");
    const stareEt = { noua: "în așteptare", raspuns: "răspuns primit", inchisa: "închisă" }[f.stare] || f.stare;
    // titlul firului = inceputul primului mesaj (al meu)
    const primul = (f.mesaje.find((m) => m.rol_autor === "utilizator") || f.mesaje[0] || {}).text || "";
    const titlu = primul.length > 70 ? primul.slice(0, 70) + "…" : primul;
    const mesaje = f.mesaje.map((m) => {
      const cls = m.rol_autor === "utilizator" ? "rap-msg-eu" : "rap-msg-admin";
      const cine = m.rol_autor === "admin" ? "iConta.eu" : (m.rol_autor === "ai" ? "Asistent AI" : "Eu");
      const poze = (m.atasamente || []).map((a) =>
        `<a href="${a.cale}" target="_blank" class="rap-img-link"><img class="rap-img" src="${a.cale}" alt="captura"></a>`
      ).join("");
      return `
        <div class="rap-mesaj ${cls}">
          <div class="rap-mesaj-cap"><b>${cine}</b><span class="rap-mesaj-data">${dataScurta(m.cand)}</span></div>
          <div class="rap-mesaj-text">${esc(m.text)}</div>
          ${poze ? `<div class="rap-mesaj-poze">${poze}</div>` : ""}
        </div>`;
    }).join("");
    return `
      <div class="rap-fir" data-id="${f.id}">
        <div class="rap-fir-cap" data-rol="cap">
          <span class="rap-fir-subiect">${esc(titlu || "(sesizare)")}</span>
          ${badge}
          <span class="rap-fir-stare rap-stare-${f.stare}">${stareEt}</span>
          <span class="rap-fir-data">${dataScurta(f.ultim_mesaj_la)}</span>
        </div>
        <div class="rap-fir-corp" style="display:none">
          <div class="rap-mesaje">${mesaje}</div>
          <div class="rap-replica">
            <textarea class="rap-replica-text camp-input" rows="2" style="overflow:hidden;resize:none" placeholder="Adaugă un mesaj..."></textarea>
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
      const ta2 = el.querySelector(".rap-replica-text"); if (!deschis && ta2) { ta2.style.height = "auto"; ta2.style.height = Math.max(ta2.scrollHeight, 44) + "px"; }  // [fix_autogrow] scrollHeight e 0 cat firul e ascuns
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
    if (!text) { arataMesaj(msg, "Scrie ce ai observat.", "eroare"); return; }
    arataMesaj(msg, "Se trimite...", "info");
    try {
      const r = await api.post("/raportari", { text });
      // urc pozele la primul mesaj al raportarii
      let _pozeEsuate = 0;
      if (pozeNoi.length && r && r.mesaj_id) {
        arataMesaj(msg, "Se încarcă imaginile...", "info");
        _pozeEsuate = await urcaPoze(r.mesaj_id, pozeNoi.map((p) => p.file));
      }
      if (_pozeEsuate) { arataMesaj(msg, "Sesizarea a fost trimisă, dar " + _pozeEsuate + " imagine(i) nu s-au încărcat. Deschide firul și reîncarcă-le.", "avert"); }
      else arataMesaj(msg, "Sesizare trimisă.", "ok");
      corp.querySelector("#rap-text").value = "";
      pozeNoi.forEach((p) => URL.revokeObjectURL(p.url));
      pozeNoi = [];
      randeazaPozeNoi();
      await incarcaFire();
      // [triaj_ai] polling suplu: la 3s pana apare reactia AI (max 10 incercari)
      let ramase = 10;
      const asteaptaAI = async () => {
        if (ramase-- <= 0) return;
        await incarcaFire();
        const f0 = (window._rapFire || [])[0];
        if (!f0 || !(f0.mesaje || []).some((m) => m.rol_autor === "ai")) setTimeout(asteaptaAI, 3000);
        else document.dispatchEvent(new CustomEvent("raportari:schimbat"));  // cifra cardului se actualizeaza la sosirea raspunsului
      };
      setTimeout(asteaptaAI, 3000);
    } catch { arataMesaj(msg, "Nu am putut trimite.", "eroare"); }
  });

  await incarcaFire();
}

// audit_cab_lot1_v1
