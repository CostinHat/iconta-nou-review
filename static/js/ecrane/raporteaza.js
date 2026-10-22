// raporteaza.js — cardul Raporteaza (perspectiva utilizatorului care proceseaza).
// Trimite o observatie catre Admin iConta; vede firul cu raspunsuri; bec rosu = raspunsuri necitite.
// Strat 2 (text + fir). Imagini: strat 3.
// [270d, comanda Costin 15.10.2026] A doua optiune langa „Sesizare noua”: „Cerere import din alta aplicatie” — aplicatia, capturi si
// exporturi (CSV, XLS/XLSX, ZIP). [C36] Fisierele firului stau in depozitul privat: se arata si se descarca numai prin ruta
// autentificata `/raportari/fisiere/{id}` (echipa iConta si autorul), iar autorul le poate sterge.

import { api, dataRo, arataMesaj, esc, cereBlob, descarca, deschideLupa, confirmaCaseta, eroareCamp, curataEroriCamp, cate, refuzPeRand } from "../api.js?v=58f26a3fc4";

function dataScurta(iso) {
  return dataRo(iso, "cu_ora");
}

const CAPTURI = ["png", "jpg", "webp"];
const MARIME_MAXIMA = 8 * 1024 * 1024;   // aceeași ca `core/fisiere_private.MARIME_MAXIMA`

// [C36] fișierele unui mesaj: capturile ca imagini (încărcate prin ruta autentificată), celelalte ca nume de descărcat;
// autorul sesizării primește și „Șterge”. Folosit și de ecranul echipei iConta (admin_raportari.js).
export function fisiereHTML(atasamente, poateSterge) {
  return (atasamente || []).map((a) => {
    const sterge = poateSterge
      ? ` <button type="button" class="buton-sters buton-mic" data-sterge-fisier="${a.id}" data-actiune="DELETE /raportari/fisiere/{fid}" aria-label="Șterge fișierul ${esc(a.nume)}">Șterge</button>`
      : "";
    if (CAPTURI.includes(a.tip)) {
      return `<span class="rap-fisier" data-fisier="${a.id}"><a href="#" class="rap-img-link" data-deschide-fisier="${a.id}"><img class="rap-img" data-captura="${a.id}" alt="captura ${esc(a.nume)}"></a>${sterge}</span>`;
    }
    return `<span class="rap-fisier" data-fisier="${a.id}"><button type="button" class="btn-link" data-descarca-fisier="${a.id}" data-nume="${esc(a.nume)}" data-fara-actiune="descărcarea unui fișier al sesizării — echipa iConta.eu și autorul">${esc(a.nume)}</button>${sterge}</span>`;
  }).join(" ");
}

// leagă imaginile și butoanele dintr-un fir deja randat; `dupaStergere` reîncarcă firul
export function legaFisiere(zona, dupaStergere) {
  zona.querySelectorAll("img[data-captura]").forEach(async (img) => {
    try {
      const r = await cereBlob(`/raportari/fisiere/${img.dataset.captura}`);
      img.src = URL.createObjectURL(await r.blob());
    } catch { img.alt = "captura nu s-a putut încărca"; }
  });
  zona.querySelectorAll("[data-deschide-fisier]").forEach((a) => a.addEventListener("click", (e) => {
    e.preventDefault();
    const img = a.querySelector("img");
    if (img && img.src) deschideLupa(img.src);
  }));
  zona.querySelectorAll("[data-descarca-fisier]").forEach((b) => b.addEventListener("click", () =>
    descarca(`/raportari/fisiere/${b.dataset.descarcaFisier}`, b.dataset.nume).catch(() => {})));
  zona.querySelectorAll("[data-sterge-fisier]").forEach((b) => b.addEventListener("click", () => {
    confirmaCaseta(b, "Ștergi fișierul? Se scoate și din iConta.eu, nu doar din fir.", async () => {
      try { await api.del(`/raportari/fisiere/${b.dataset.stergeFisier}`); if (dupaStergere) await dupaStergere(); }
      catch (e) { refuzPeRand(b, (e && e.mesaj) || "Fișierul nu s-a putut șterge."); }
    }, { textOk: "Șterge fișierul" });
  }));
}

export async function randeazaRaporteaza(corp, nav) {
  corp.innerHTML = `
    <p class="mig-intro">Ai observat ceva care nu merge, nu e corect sau nu se înțelege? Trimite-ne o sesizare. Îți răspundem aici.</p>

    <div class="rap-nou panou" style="max-width:640px">
      <div class="rap-tabs" role="tablist" aria-label="Ce trimiți">
        <button type="button" class="rap-tab rap-tab-activ" role="tab" aria-selected="true" aria-controls="rap-zona-sesizare" data-tab="sesizare" data-fara-actiune="alegerea formularului — orice cont">Sesizare nouă</button>
        <button type="button" class="rap-tab" role="tab" aria-selected="false" aria-controls="rap-zona-import" data-tab="import" data-fara-actiune="alegerea formularului — orice cont">Cerere import din altă aplicație</button>
      </div>
      <div id="rap-zona-sesizare" role="tabpanel">
      <label class="camp">
        <span class="camp-eticheta">Ce ai observat?</span>
        <textarea id="rap-text" class="camp-input rap-autogrow" rows="6" style="min-height:130px;overflow:hidden;resize:none" placeholder="Descrie ce ai observat, ce nu merge sau ce nu se înțelege... (poți lipi o captură de ecran cu Ctrl+V)"></textarea>
      </label>
      <div class="rap-poze" id="rap-poze-noi"></div>
      <p class="ecran-nota" style="margin:0 0 8px">Opțional: atașează capturi de ecran — cu butonul de mai jos sau lipite direct cu Ctrl+V.</p>
      <div class="rap-actiuni" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <button class="buton-primar" id="rap-trimite">Trimite sesizarea</button>
        <button class="buton-secundar" id="rap-add-poza" data-fara-actiune="captură într-o sesizare către iConta.eu — orice cont" type="button">Adaugă captură</button>
        <input type="file" id="rap-file" accept="image/png,image/jpeg,image/webp" multiple style="display:none">
      </div>
      <div id="rap-msg"></div>
      </div>
      <div id="rap-zona-import" role="tabpanel" hidden>
        <p class="ecran-nota" style="margin:8px 0">Trimite-ne o captură cu meniul de export din aplicația ta și exportul unei singure firme (balanța de verificare, partenerii cu soldurile lor, salariații, mijloacele fixe). Analizăm exportul și îți răspundem aici dacă și când îl putem prelua automat.</p>
        <label class="camp"><span class="camp-eticheta">Aplicația din care migrezi <span class="oblig">*</span></span>
          <input type="text" id="imp-aplicatie" class="camp-input" maxlength="80" aria-required="true" placeholder="de exemplu WinMentor, Ciel, SmartBill"></label>
        <div class="camp"><span class="camp-eticheta">Capturi și fișiere de export <span class="oblig">*</span></span>
          <div id="imp-fisiere-noi"></div>
          <span class="camp-ajutor">Capturi PNG, JPG sau WEBP și exporturi CSV, XLS, XLSX sau ZIP, până la 8 MB fiecare. Fișierele le vede doar echipa iConta.eu, se folosesc numai pentru import și le poți șterge oricând.</span></div>
        <div class="rap-actiuni" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:8px">
          <button class="buton-primar" id="imp-trimite" data-fara-actiune="cerere de import către iConta.eu — orice cont">Trimite cererea</button>
          <button class="buton-secundar" id="imp-adauga" data-fara-actiune="fișier într-o cerere de import către iConta.eu — orice cont" type="button">Adaugă fișiere</button>
          <input type="file" id="imp-file" accept=".png,.jpg,.jpeg,.webp,.csv,.xls,.xlsx,.zip" multiple style="display:none">
        </div>
        <div id="imp-msg"></div>
      </div>
    </div>

    <div class="rap-titlu-lista">Sesizările mele</div>
    <div id="rap-lista" class="rap-lista"><div class="rap-gol">Se încarcă...</div></div>
  `;

  const lista = corp.querySelector("#rap-lista");

  // [270d] cele două opțiuni: sesizarea și cererea de import din altă aplicație
  corp.querySelectorAll(".rap-tab[data-tab]").forEach((b) => b.addEventListener("click", () => {
    corp.querySelectorAll(".rap-tab[data-tab]").forEach((x) => {
      const ales = x === b;
      x.classList.toggle("rap-tab-activ", ales);
      x.setAttribute("aria-selected", String(ales));
    });
    corp.querySelector("#rap-zona-sesizare").hidden = b.dataset.tab !== "sesizare";
    corp.querySelector("#rap-zona-import").hidden = b.dataset.tab !== "import";
  }));

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
      lista.innerHTML = `<div class="rap-gol">Nu s-au putut încărca sesizarile.</div>`;
    }
  }

  function renderFir(f) {
    // [deficiența 291] bulina = o veste de la iConta necitită (răspuns sau stare schimbată), nu cererea mea în așteptare — aia o spune
    // starea de lângă („în așteptare”)
    const badge = f.necitite > 0 ? `<span class="rap-badge-pct rap-badge-verde" title="răspuns sau stare nouă de la iConta.eu, necitită"></span>` : "";
    const stareEt = { noua: "în așteptare", raspuns: "răspuns primit", inchisa: "închisă" }[f.stare] || f.stare;
    // titlul firului = inceputul primului mesaj (al meu)
    const primul = f.tip === "cerere_import" ? `Cerere import din ${f.aplicatie || ""}`
      : ((f.mesaje.find((m) => m.rol_autor === "utilizator") || f.mesaje[0] || {}).text || "");
    const titlu = primul.length > 70 ? primul.slice(0, 70) + "…" : primul;
    const mesaje = f.mesaje.map((m) => {
      const cls = m.rol_autor === "utilizator" ? "rap-msg-eu" : "rap-msg-admin";
      const cine = m.rol_autor === "admin" ? "iConta.eu" : (m.rol_autor === "ai" ? "Asistent AI" : "Eu");
      const poze = fisiereHTML(m.atasamente, true);   // [C36] prin ruta autentificată; autorul firului le poate șterge
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
            <textarea aria-label="Mesaj nou" class="rap-replica-text camp-input" rows="2" style="overflow:hidden;resize:none" placeholder="Adaugă un mesaj..."></textarea>
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
    legaFisiere(el, async () => {   // după ștergerea unui fișier: firul se reîncarcă și rămâne deschis
      await incarcaFire();
      const elNou = lista.querySelector(`.rap-fir[data-id="${f.id}"] .rap-fir-corp`);
      if (elNou) elNou.style.display = "block";
    });
    cap.addEventListener("click", async () => {
      const deschis = corpFir.style.display !== "none";
      corpFir.style.display = deschis ? "none" : "block";
      if (!deschis && f.necitite > 0) {   // [291] firul deschis = vestea văzută: bulina (aici și pe „Suport”) se stinge
        try {
          await api.post(`/raportari/${f.id}/citit`, {});
          f.necitite = 0;
          const b = cap.querySelector(".rap-badge-pct"); if (b) b.remove();
          document.dispatchEvent(new CustomEvent("raportari:schimbat"));
        } catch (e) {
          const z = document.createElement("div");
          corpFir.prepend(z);
          arataMesaj(z, `Vestea nu s-a putut marca drept citită (${e.mesaj || "eroare"}): bulina rămâne până la următoarea deschidere.`, "avert");
        }
      }
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
      } catch { btn.disabled = false; refuzPeRand(btn, "Nu s-a putut trimite răspunsul. Reîncearcă."); }
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
      if (_pozeEsuate) { arataMesaj(msg, "Sesizarea a fost trimisă, dar " + cate(_pozeEsuate, "imagine", "imagini") + (_pozeEsuate === 1 ? " nu s-a încărcat" : " nu s-au încărcat") + ". Deschide firul și reîncarcă-le.", "avert"); }
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
    } catch { arataMesaj(msg, "Nu s-a putut trimite.", "eroare"); }
  });

  // --- [270d] cererea de import din altă aplicație ---
  let fisiereNoi = [];   // File
  const zonaFis = corp.querySelector("#imp-fisiere-noi");
  const inputImp = corp.querySelector("#imp-file");
  function randeazaFisiereNoi() {
    zonaFis.innerHTML = fisiereNoi.map((f, i) =>
      `<div class="rap-img-nume">${esc(f.name)} <button type="button" class="btn-link" data-scoate="${i}" data-fara-actiune="scoaterea unui fișier încă netrimis" aria-label="Scoate ${esc(f.name)}">Scoate</button></div>`).join("");
    zonaFis.querySelectorAll("[data-scoate]").forEach((b) => b.addEventListener("click", () => {
      fisiereNoi.splice(+b.dataset.scoate, 1); randeazaFisiereNoi();
    }));
  }
  corp.querySelector("#imp-adauga").addEventListener("click", () => inputImp.click());
  inputImp.addEventListener("change", () => {
    const msg = corp.querySelector("#imp-msg");
    const mari = [...inputImp.files].filter((f) => f.size > MARIME_MAXIMA).map((f) => f.name);
    fisiereNoi.push(...[...inputImp.files].filter((f) => f.size <= MARIME_MAXIMA));
    inputImp.value = "";
    randeazaFisiereNoi();
    if (mari.length) arataMesaj(msg, `Peste 8 MB, nu se trimit: ${mari.join(", ")}.`, "avert");
  });
  corp.querySelector("#imp-trimite").addEventListener("click", async () => {
    const msg = corp.querySelector("#imp-msg");
    curataEroriCamp(corp.querySelector("#rap-zona-import"));
    msg.textContent = "";
    const aplicatie = corp.querySelector("#imp-aplicatie").value.trim();
    let lipsa = false;
    if (!aplicatie) { eroareCamp(corp, "imp-aplicatie", "Scrie aplicația din care migrezi."); lipsa = true; }
    if (!fisiereNoi.length) { arataMesaj(msg, "Adaugă cel puțin o captură sau un fișier de export.", "eroare"); lipsa = true; }
    if (lipsa) return;
    arataMesaj(msg, "Se trimite...", "info");
    try {
      const r = await api.post("/raportari", { tip: "cerere_import", aplicatie });
      const esuate = [];
      for (const f of fisiereNoi) {
        const fd = new FormData();
        fd.append("fisier", f);
        try { await api.postForm(`/raportari/mesaj/${r.mesaj_id}/fisier`, fd); }
        catch (e) {
          esuate.push(`${f.name} (${(e && e.mesaj) || "nu s-a încărcat"})`);
          arataMesaj(msg, `Nu s-a încărcat: ${esuate.join("; ")}.`, "avert");   // se vede pe loc; rezumatul vine la capăt
        }
      }
      if (esuate.length) arataMesaj(msg, `Cererea a fost trimisă, dar ${esuate.length === 1 ? "un fișier nu s-a încărcat" : cate(esuate.length, "fișier", "fișiere") + " nu s-au încărcat"}: ${esuate.join("; ")}.`, "avert");
      else arataMesaj(msg, "Cererea de import a fost trimisă. Îți răspundem aici.", "ok");
      corp.querySelector("#imp-aplicatie").value = "";
      fisiereNoi = [];
      randeazaFisiereNoi();
      await incarcaFire();
      document.dispatchEvent(new CustomEvent("raportari:schimbat"));
    } catch (e) { arataMesaj(msg, (e && e.mesaj) || "Cererea nu s-a putut trimite.", "eroare"); }
  });

  await incarcaFire();
}

// audit_cab_lot1_v1
