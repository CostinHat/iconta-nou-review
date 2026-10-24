// [lotul 10, deficiența 428, decizia Costin 20.10.2026 „Bifă pe client”] Clienții firmei, cu bifa „Persoană afiliată (Cod fiscal art.7
// pct.26)”: „factura către el ia regulile generale (4427) chiar dacă firma e în sistem” — CF art.282 alin.(6) lit.d): sistemul TVA la încasare
// nu se aplică „livrărilor de bunuri/prestărilor de servicii pentru care beneficiarul este o persoană afiliată furnizorului/prestatorului
// potrivit art. 7 pct. 26”. Bifa se îngheață pe factură la emitere (`facturi.beneficiar_afiliat`); o bifă schimbată nu mută facturile vechi.
// [lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”] „Localitatea și județul la PF și la firmele neînregistrate se
// completează în fișa partenerului; refuzul declarației trimite direct acolo.” Același ecran pentru Furnizori (`ecranFurnizori`): fișa are
// numele, localitatea și județul (D406 / D394 le citesc din fișă când factura nu le are); refuzul D406 / D394 deschide ecranul cu câmpul lipsă
// adus în vedere (`opt.camp` = „partener:<cheie>:<camp>”, cheia din `clienti_api.cheie_partener`).
// [lotul 11, deficiența 444, comanda Costin 11.1 pct.20] „când numele de la ANAF diferă de fișa partenerului, se spune și se propune
// actualizarea.” — „Verifică la ANAF” pe rândul cu CUI: diferența o spune serverul (`clienti_api.nume_diferit`, prin `verifica-cui?nume=`),
// butonul o aplică.
// Lista: fișele + partenerii facturilor fără fișă (salvarea le creează fișa).
// DS: fereastra cu tabel (cap.9 v2.96) — rezumatul și zona de mesaj a acțiunilor de pe rânduri lipite sus (`.rezumat-fix`), acțiunea pe rând
// stă în celula ei; cifrele în `.fd-td-num`; rândul adus în vedere de un refuz poartă `.val-evidentiat` (aceeași evidențiere ca nota adusă
// în vedere din „De validat”).
// [lotul 12, deficiența 461, comanda Costin 12.1 pct.8: „461 lista de parteneri” cerută] PARTENERII FIRMEI (`ecranParteneriFirmei`): clienții
// și furnizorii, din fișe și din toate documentele (facturi emise / primite, casă, bancă, note, soldurile de preluare — `clienti_api.
// parteneri_firmei`), cu căutare după nume sau cod fiscal; fișa partenerului (`ecranFisaPartener`): datele (verificarea la ANAF, ruta
// existentă `verifica-cui`, cu propunerea numelui de la ANAF — 444), documentele lui și soldul din contabilitate, cu aceeași regulă ca balanța
// (`clienti_api.sold_partener`: soldul de preluare + notele validate; ciornele separat). Nimic nu se recalculează în ecran.
import { api, arataMesaj, esc, selectDaNu, daNu, eroareCamp, curataEroriCamp, focusFaraSalt, bani, dataRo, cate } from "../api.js?v=309f4d66ae";

const FEL = {
  clienti: {
    titlu: "Clienți", pre: "cl", cheieLista: "clienti", eticheta: "Client", deFacturi: "emise",
    // căile API scrise întregi (garda rutelor fără apelant le caută literal)
    url: (tid) => `/tenants/${tid}/clienti`, urlUna: (tid, id) => `/tenants/${tid}/clienti/${id}`,
    act: "PUT /tenants/{tenant_id}/clienti/{client_id}", actNou: "POST /tenants/{tenant_id}/clienti",
    intro: `Fișele clienților: numele, localitatea și județul — D406 și D394 le iau de aici când factura nu le are (persoanele fizice și
      firmele fără cod de TVA). Bifează clienții care sunt persoane afiliate firmei (Cod fiscal art.7 pct.26): pentru ei, chiar dacă firma
      aplică TVA la încasare, factura ia regulile generale — TVA-ul e exigibil la emitere, pe 4427 (Cod fiscal art.282 alin.(6) lit.d). Bifa
      se aplică facturilor emise de acum înainte; cele emise rămân cum au fost emise.`,
    gol: "Niciun client încă: clienții apar aici din facturile emise.",
  },
  furnizori: {
    titlu: "Furnizori", pre: "fz", cheieLista: "furnizori", eticheta: "Furnizor", deFacturi: "primite",
    url: (tid) => `/tenants/${tid}/furnizori`, urlUna: (tid, id) => `/tenants/${tid}/furnizori/${id}`,
    act: "PUT /tenants/{tenant_id}/furnizori/{furnizor_id}", actNou: "POST /tenants/{tenant_id}/furnizori",
    intro: `Fișele furnizorilor: numele, localitatea și județul — D406 și D394 le iau de aici când factura sau borderoul de achiziție nu le
      are (persoanele fizice și firmele fără cod de TVA).`,
    gol: "Niciun furnizor încă: furnizorii apar aici din facturile primite și din borderourile de achiziție.",
  },
};

export async function ecranClienti(corp, nav, t, opt = {}) {
  return ecranParteneri(corp, nav, t, "clienti", opt);
}

export async function ecranFurnizori(corp, nav, t, opt = {}) {
  return ecranParteneri(corp, nav, t, "furnizori", opt);
}

async function ecranParteneri(corp, nav, t, fel, opt) {
  const F = FEL[fel];
  const P = F.pre;
  const actiune = (x) => (x.id ? F.act : F.actNou);
  let mesajDupa = null;
  let campTinta = opt.camp || null;
  const deseneaza = async () => {
    corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
    let r;
    try {
      r = await api.get(F.url(t.id));
    } catch (e) {
      corp.innerHTML = `<h2 class="pf-titlu">${F.titlu}</h2><div id="${P}-mesaj"></div>`;
      arataMesaj(corp.querySelector(`#${P}-mesaj`), `${F.titlu} nu s-au putut citi` + (e && e.mesaj ? ": " + e.mesaj : "") + ".", "eroare");
      return;
    }
    const judete = r.judete || [];
    const randuri = [
      ...(r[F.cheieLista] || []).map((c) => ({ cheie: "c" + c.id, id: c.id, nume: c.nume, cui: c.cui, oras: c.oras || "", judet: c.judet || "",
        afiliat: !!c.afiliat, facturi: null, partener: c.cheie })),
      ...(r.parteneri_fara_fisa || []).map((p, i) => ({ cheie: p.cui ? "p" + p.cui : "n" + i, id: null, nume: p.nume, cui: p.cui,
        oras: p.oras || "", judet: p.judet || "", afiliat: false, facturi: p.facturi, partener: p.cheie })),
    ];
    const optJud = (sel) => `<option value="">— alege —</option>` + judete.map(([c, n]) =>
      `<option value="${esc(c)}"${c === sel ? " selected" : ""}>${esc(n)}</option>`).join("");
    const rand = (x) => `<tr data-cheie="${esc(x.cheie)}" data-partener="${esc(x.partener || "")}">
        <td><input class="camp-input" id="${P}-nume-${esc(x.cheie)}" value="${esc(x.nume || "")}" aria-label="Numele partenerului">
          ${x.id ? "" : `<div class="tip-desc">fără fișă — din facturile ${F.deFacturi}</div>`}</td>
        <td>${esc(x.cui || "—")}</td>
        <td><input class="camp-input" id="${P}-oras-${esc(x.cheie)}" value="${esc(x.oras)}" aria-label="Localitatea: ${esc(x.nume || x.cui || "")}"></td>
        <td><select class="camp-input" id="${P}-judet-${esc(x.cheie)}" aria-label="Județul: ${esc(x.nume || x.cui || "")}">${optJud(x.judet)}</select></td>
        <td class="fd-td-num">${x.facturi === null ? "" : x.facturi}</td>
        ${fel === "clienti" ? `<td>${selectDaNu(`class="cl-afiliat" id="cl-afiliat-${esc(x.cheie)}" data-cheie="${esc(x.cheie)}"`, x.afiliat,
          `Persoană afiliată (Cod fiscal art.7 pct.26): ${x.nume || x.cui || ""}`)}</td>` : ""}
        <td>${x.cui ? `<button type="button" class="buton-secundar ${P}-anaf fisa-anaf" id="${P}-anaf-${esc(x.cheie)}" data-cheie="${esc(x.cheie)}"
            data-actiune="GET /tenants/{tenant_id}/verifica-cui/{cui}">Verifică la ANAF</button> ` : ""}<button class="buton-secundar ${P}-salveaza"
            id="${P}-salveaza-${esc(x.cheie)}" data-cheie="${esc(x.cheie)}" disabled data-actiune="${actiune(x)}">Salvează</button>
          <div id="${P}-anaf-stare-${esc(x.cheie)}"></div></td>
      </tr>`;
    corp.innerHTML = `
      <div class="rezumat-fix" id="${P}-rezumat">
        <h2 class="pf-titlu">${F.titlu}</h2>
        <p class="pf-intro">${F.intro}</p>
        <div id="${P}-mesaj"></div>
      </div>
      ${randuri.length ? `<table class="fd-tabel" id="${P}-tabel"><thead><tr><th>${F.eticheta}</th><th>CUI</th><th>Localitatea</th><th>Județul</th>
        <th class="fd-td-num">Facturi ${F.deFacturi}</th>${fel === "clienti" ? "<th>Persoană afiliată (Cod fiscal art.7 pct.26)</th>" : ""}
        <th>Acțiune</th></tr></thead><tbody>${randuri.map(rand).join("")}</tbody></table>`
        : `<div class="stare-goala" id="${P}-gol">${F.gol}</div>`}`;
    const zonaM = corp.querySelector(`#${P}-mesaj`);
    if (mesajDupa) {
      arataMesaj(zonaM, mesajDupa, "ok");
      // deschis dintr-un refuz (declarația): drumul înapoi, la ecranul de plecare, cu datele lui intacte (ca Date firmă, `inapoiLa`)
      if (opt.inapoiLa && nav && nav.inapoi) {
        const bi = document.createElement("button");
        bi.type = "button"; bi.className = "buton-primar"; bi.id = `${P}-inapoi-la`; bi.style.marginLeft = "10px";
        bi.textContent = "← Înapoi la " + opt.inapoiLa;
        bi.addEventListener("click", () => nav.inapoi());
        zonaM.appendChild(bi);
      }
    }
    const dupaCheie = Object.fromEntries(randuri.map((x) => [x.cheie, x]));
    const el = (camp, x) => corp.querySelector(`#${P}-${camp}-${CSS.escape(x.cheie)}`);
    // ce s-a schimbat pe rând, față de ce e înregistrat (numai acelea se trimit)
    const schimbari = (x) => {
      const ch = {};
      const nume = el("nume", x).value.trim(), oras = el("oras", x).value.trim(), judet = el("judet", x).value;
      if (nume !== (x.nume || "")) ch.nume = nume;
      if (oras !== (x.oras || "")) ch.oras = oras;
      if (judet !== (x.judet || "")) ch.judet = judet;
      if (fel === "clienti") {
        const af = daNu(corp.querySelector(`#cl-afiliat-${CSS.escape(x.cheie)}`));
        if (af !== null && af !== !!x.afiliat) ch.afiliat = af;
      }
      return ch;
    };
    // rândul fără fișă se salvează (fișa nouă) și cu localitatea / județul propuse de pe factură, neschimbate
    const actualizeazaButon = (x) => {
      el("salveaza", x).disabled = !Object.keys(schimbari(x)).length && !(x.id === null && (x.oras || x.judet));
    };
    randuri.forEach((x) => {
      ["nume", "oras", "judet"].forEach((c) => el(c, x).addEventListener(c === "judet" ? "change" : "input", () => actualizeazaButon(x)));
      actualizeazaButon(x);
    });
    corp.querySelectorAll(".cl-afiliat").forEach((cb) => cb.addEventListener("change", () => actualizeazaButon(dupaCheie[cb.dataset.cheie])));
    const salveaza = async (x, ch) => {
      curataEroriCamp(corp.querySelector(`tr[data-cheie="${CSS.escape(x.cheie)}"]`));
      try {
        if (x.id) await api.put(F.urlUna(t.id, x.id), ch);
        else await api.post(F.url(t.id), { nume: (ch.nume ?? x.nume) || x.cui, cui: x.cui,
          oras: ch.oras ?? (x.oras || null), judet: ch.judet ?? (x.judet || null), ...(fel === "clienti" ? { afiliat: !!ch.afiliat } : {}) });
        const ce = [];
        if ("afiliat" in ch) ce.push(ch.afiliat ? "bifat ca persoană afiliată — facturile emise de acum înainte către el iau regulile "
          + "generale (TVA exigibil la emitere)" : "nu mai e persoană afiliată — facturile de acum înainte urmează regimul firmei");
        if ("nume" in ch) ce.push(`numele din fișă e acum „${ch.nume}”`);
        if ("oras" in ch || "judet" in ch || !x.id) ce.push("localitatea și județul sunt în fișă — D406 și D394 le iau de aici");
        mesajDupa = `${(ch.nume ?? x.nume) || x.cui}: ${ce.join("; ")}.`;
        campTinta = null;
        await deseneaza();
      } catch (e) {
        // [440] fiecare refuz cu textul lui, lângă câmp și în casetă
        const ec = (e && e.erori_campuri) || [];
        ec.forEach((c) => eroareCamp(corp, `${P}-${c.camp}-${x.cheie}`, c.mesaj));
        arataMesaj(zonaM, `${x.nume || x.cui}: fișa NU s-a salvat — ` + (ec.length ? ec.map((c) => c.mesaj).join(" ") : ((e && e.mesaj) || "eroare.")), "eroare");
      }
    };
    corp.querySelectorAll(`.${P}-salveaza`).forEach((b) => b.addEventListener("click", () => {
      const x = dupaCheie[b.dataset.cheie];
      const ch = schimbari(x);
      if (!Object.keys(ch).length && x.id) return;
      salveaza(x, ch);
    }));
    // [444] numele de la ANAF față de fișă: serverul spune dacă diferă (`nume` = numele din rând), butonul propune actualizarea
    corp.querySelectorAll(".fisa-anaf").forEach((b) => b.addEventListener("click", async () => {   // clasa fixă: legătura buton–handler se dovedește static (scan_drepturi_ui)
      const x = dupaCheie[b.dataset.cheie];
      const st = el("anaf-stare", x);
      if (b.disabled) return;
      const textB = b.textContent;
      b.disabled = true; b.setAttribute("aria-busy", "true"); b.textContent = "Se verifică…";
      try {
        const r2 = await api.get(`/tenants/${t.id}/verifica-cui/${encodeURIComponent(x.cui)}?nume=${encodeURIComponent(el("nume", x).value.trim())}`);
        if (!(r2 && r2.gasit)) { st.textContent = "CUI negăsit la ANAF."; return; }
        // localitatea și județul de la ANAF (domiciliul fiscal) intră în câmpurile goale — se salvează cu „Salvează”
        if (!el("oras", x).value.trim() && r2.localitate) el("oras", x).value = r2.localitate;
        if (!el("judet", x).value && r2.judet && [...el("judet", x).options].some((o) => o.value === r2.judet)) el("judet", x).value = r2.judet;
        actualizeazaButon(x);
        if (r2.nume_dat_diferit) {
          st.innerHTML = `<span class="em-cui-info">Numele de la ANAF diferă: „${esc(r2.denumire)}” (în fișă: „${esc(el("nume", x).value.trim())}”).</span>
            <button type="button" class="buton-primar" id="${P}-anaf-aplica-${esc(x.cheie)}" data-actiune="${actiune(x)}">Actualizează fișa cu numele de la ANAF</button>`;
          st.querySelector("button").addEventListener("click", () => {
            el("nume", x).value = r2.denumire;
            salveaza(x, schimbari(x));
          });
        } else {
          st.innerHTML = `<span class="em-cui-info">La ANAF: „${esc(r2.denumire)}” · ${r2.platitor_tva ? "plătitor TVA" : "neplătitor TVA"} — numele din fișă e același.</span>`;
        }
      } catch (e) {
        st.innerHTML = `<span class="pe-randuri">${esc((e && e.mesaj) || "Verificarea nu s-a putut face — reîncearcă.")}</span>`;
      } finally { b.disabled = false; b.removeAttribute("aria-busy"); b.textContent = textB; }
    }));
    // deschis dintr-un refuz (D406 / D394): rândul partenerului, cu câmpul lipsă în vedere
    if (campTinta && campTinta.startsWith("partener:")) {
      const [, cheieP, campP] = campTinta.split(":");
      const x = randuri.find((y) => y.partener === cheieP);
      if (x) {
        const tinta = el(campP || "oras", x);
        corp.querySelector(`tr[data-cheie="${CSS.escape(x.cheie)}"]`).classList.add("val-evidentiat");
        tinta.scrollIntoView({ block: "center" });
        focusFaraSalt(tinta);
      } else {
        arataMesaj(zonaM, "Partenerul din refuz nu e în listă (n-are facturi și nici fișă): localitatea și județul lui se scriu pe documentul pe care apare.", "avert");
      }
    }
  };
  await deseneaza();
}


const ROL = { client: "client", furnizor: "furnizor", "client și furnizor": "client și furnizor" };

export async function ecranParteneriFirmei(corp, nav, t) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let r;
  try {
    r = await api.get(`/tenants/${t.id}/parteneri-firma`);   // [461] lista; `/parteneri` e rezumatul soldurilor din migrare
  } catch (e) {
    corp.innerHTML = `<h2 class="pf-titlu">Parteneri</h2><div id="pt-mesaj"></div>`;
    arataMesaj(corp.querySelector("#pt-mesaj"), "Partenerii nu s-au putut citi" + (e && e.mesaj ? ": " + e.mesaj : "") + ".", "eroare");
    return;
  }
  const lista = (r && r.parteneri) || [];
  const rand = (p) => `<tr data-cheie="${esc(p.cheie)}">
      <td>${esc(p.nume || "—")}</td>
      <td>${esc(p.cui || "—")}</td>
      <td>${esc(ROL[p.rol] || "—")}</td>
      <td class="fd-td-num">${p.documente}</td>
      <td>${p.fisa ? "da" : "—"}</td>
      <td><button type="button" class="buton-secundar pt-deschide" id="pt-fisa-${esc(p.cheie)}" data-cheie="${esc(p.cheie)}"
        data-actiune="GET /tenants/{tenant_id}/parteneri-firma/fisa">Fișa partenerului</button></td>
    </tr>`;
  corp.innerHTML = `
    <div class="rezumat-fix" id="pt-rezumat">
      <h2 class="pf-titlu">Parteneri</h2>
      <p class="pf-intro">Clienții și furnizorii firmei, din fișe și din toate documentele: facturi emise și primite, casă, bancă, note
        contabile, soldurile de preluare. Deschide fișa unui partener ca să-i vezi datele, documentele și soldul din contabilitate.</p>
      ${lista.length ? `<input id="pt-cauta" class="camp-input" style="max-width:420px" placeholder="Caută după nume sau cod fiscal"
        aria-label="Caută partenerul după nume sau cod fiscal" autocomplete="off">
      <span class="tip-desc" id="pt-numar" style="margin-left:8px">${esc(cate(lista.length, "partener", "parteneri"))}</span>` : ""}
      <div id="pt-mesaj"></div>
    </div>
    ${lista.length ? `<table class="fd-tabel" id="pt-tabel"><thead><tr><th>Partener</th><th>Cod fiscal</th><th>Rol</th>
      <th class="fd-td-num">Documente</th><th>Are fișă</th><th>Acțiune</th></tr></thead><tbody>${lista.map(rand).join("")}</tbody></table>`
      : `<div class="stare-goala" id="pt-gol">Niciun partener încă: partenerii apar aici din fișele de clienți și furnizori și din documentele
        firmei (facturi, casă, bancă, note).</div>`}`;
  const norm = (x) => String(x || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const cauta = corp.querySelector("#pt-cauta");
  if (cauta) cauta.addEventListener("input", () => {
    const q = norm(cauta.value.trim());
    let vazute = 0;
    lista.forEach((p) => {
      const tr = corp.querySelector(`tr[data-cheie="${CSS.escape(p.cheie)}"]`);
      const da = !q || norm(p.nume).includes(q) || norm(p.cui).includes(q);
      tr.hidden = !da;
      vazute += da ? 1 : 0;
    });
    corp.querySelector("#pt-numar").textContent = q ? `${vazute} din ${cate(lista.length, "partener", "parteneri")}` : cate(lista.length, "partener", "parteneri");
    const zm = corp.querySelector("#pt-mesaj");
    if (!vazute) arataMesaj(zm, "Niciun partener cu acest nume sau cod fiscal.", "info"); else zm.innerHTML = "";
  });
  corp.querySelectorAll(".pt-deschide").forEach((b) => b.addEventListener("click", () => {
    const p = lista.find((x) => x.cheie === b.dataset.cheie);
    nav.deschide("Fișa partenerului", (c2) => ecranFisaPartener(c2, nav, t, p.cheie), { lat: "tabel" });
  }));
}

export async function ecranFisaPartener(corp, nav, t, cheie) {
  corp.innerHTML = `<p class="ecran-nota">Se încarcă…</p>`;
  let f;
  try {
    f = await api.get(`/tenants/${t.id}/parteneri-firma/fisa?cheie=${encodeURIComponent(cheie)}`);
  } catch (e) {
    corp.innerHTML = `<h2 class="pf-titlu">Fișa partenerului</h2><div id="pp-mesaj"></div>`;
    arataMesaj(corp.querySelector("#pp-mesaj"), "Fișa nu s-a putut citi" + (e && e.mesaj ? ": " + e.mesaj : "") + ".", "eroare");
    return;
  }
  const s = f.sold || { conturi: [] };
  const fisaText = (x) => {
    const parti = [x.adresa, x.oras, x.judet].filter(Boolean).map(esc).join(", ");
    return `<div class="pf-frand" id="pp-fisa-${esc(x.fel)}-${x.id}"><div class="pf-frand-text">
      <div class="pf-frand-nume">Fișa de ${x.fel === "clienti" ? "client" : "furnizor"}: ${esc(x.nume || "")}</div>
      <div class="pf-frand-sub">${parti || "adresa necompletată"}${x.email ? " · " + esc(x.email) : ""}${x.telefon ? " · " + esc(x.telefon) : ""}${
        x.fel === "clienti" ? " · persoană afiliată (Cod fiscal art.7 pct.26): " + (x.afiliat ? "da" : "nu") : ""}</div></div></div>`;
  };
  const randSold = (c) => `<tr><td>${esc(c.cont)}</td><td>${esc(c.denumire || "")}</td>
      <td class="fd-td-num">${c.debitor ? bani(c.debitor) : ""}</td><td class="fd-td-num">${c.creditor ? bani(c.creditor) : ""}</td></tr>`;
  const randDoc = (d) => `<tr><td>${dataRo(d.data)}</td><td>${esc(d.fel)}</td><td>${esc(d.document || "—")}</td>
      <td class="fd-td-num">${bani(d.suma)} ${d.moneda === "RON" ? "lei" : esc(d.moneda)}${d.suma_valuta != null ? ` <div class="tip-desc">${bani(d.suma_valuta)} ${esc(d.moneda)}</div>` : ""}</td>
      <td>${esc(d.stare || "")}</td></tr>`;
  corp.innerHTML = `
    <div class="rezumat-fix" id="pp-rezumat">
      <h2 class="pf-titlu">Fișa partenerului</h2>
      <p class="pf-intro" id="pp-antet"><b id="pp-nume">${esc(f.nume || "Partener")}</b> · Cod fiscal: ${esc(f.cui || "fără cod (persoană fizică sau firmă neînregistrată)")}${f.rol ? " · " + esc(f.rol) : ""}
        ${f.cui ? `<button type="button" class="buton-secundar" id="pp-anaf" style="margin-left:10px"
          data-actiune="GET /tenants/{tenant_id}/verifica-cui/{cui}">Verifică la ANAF</button>` : ""}</p>
      <div id="pp-anaf-stare"></div>
      <div id="pp-mesaj"></div>
    </div>
    <h3 class="pf-subtitlu">Datele partenerului</h3>
    ${(f.fise || []).length ? `<div class="pf-lista">${f.fise.map(fisaText).join("")}</div>`
      : `<p class="pf-intro" id="pp-fara-fisa">Partenerul n-are fișă: datele lui vin din documente. Fișa se face din Clienți sau Furnizori.</p>`}
    ${t.regim_contabil === "simpla" ? `<p class="pf-intro" id="pp-sold-simpla">Firma ține contabilitatea în partidă simplă: nu are conturi de
      clienți și furnizori, deci nici sold pe partener.</p>` : `
    <h3 class="pf-subtitlu">Soldul din contabilitate la ${dataRo(s.la)}</h3>
    <p class="pf-intro" id="pp-sold-sursa">Ca în balanța de verificare: ${s.preluare ? `soldul de preluare de la ${dataRo(s.preluare)}, pe parteneri, și
      notele validate de după el` : "notele validate (evidența firmei e întreagă în aplicație)"}, pe conturile de clienți și furnizori.</p>
    ${(s.nedefalcat || []).length ? `<div id="pp-nedefalcat"></div>` : ""}
    ${s.conturi.length ? `<table class="fd-tabel" id="pp-sold"><thead><tr><th>Cont</th><th>Denumire</th><th class="fd-td-num">Sold debitor</th>
      <th class="fd-td-num">Sold creditor</th></tr></thead><tbody>${s.conturi.map(randSold).join("")}</tbody></table>`
      : `<div class="stare-goala" id="pp-sold-gol">Niciun sold pe conturile de clienți și furnizori ale partenerului.</div>`}
    ${s.ciorne ? `<p class="tip-desc" id="pp-ciorne">${esc(cate(s.ciorne, "notă", "note"))} în ciornă ${s.ciorne === 1 ? "atinge" : "ating"} partenerul: nu intră în sold până la validare.</p>` : ""}
    ${s.note_fara_partener ? `<p class="tip-desc" id="pp-fara-partener">Pe conturile de clienți și furnizori ale firmei sunt și note validate fără
      partener (${esc(cate(s.note_fara_partener, "notă", "note"))}): ele nu intră în soldul niciunui partener (în balanță sunt).</p>` : ""}`}
    <h3 class="pf-subtitlu">Documentele partenerului</h3>
    ${(f.documente || []).length ? `<table class="fd-tabel" id="pp-documente"><thead><tr><th>Data</th><th>Document</th><th>Număr</th>
      <th class="fd-td-num">Sumă</th><th>Stare</th></tr></thead><tbody>${f.documente.map(randDoc).join("")}</tbody></table>`
      : `<div class="stare-goala" id="pp-documente-gol">Niciun document cu acest partener.</div>`}`;
  if ((s.nedefalcat || []).length) {
    arataMesaj(corp.querySelector("#pp-nedefalcat"), `Soldul de preluare al ${s.nedefalcat.length === 1 ? "contului" : "conturilor"} `
      + `${s.nedefalcat.join(", ")} nu e defalcat pe parteneri: partea partenerului din soldul de la ${dataRo(s.preluare)} nu se cunoaște, `
      + "deci soldul de mai jos cuprinde numai notele de după preluare. Importă soldurile pe parteneri (Import date).", "avert");
  }
  // [444] verificarea la ANAF, pe ruta existentă: numele de la ANAF față de fișă — dacă diferă, se spune și se propune actualizarea
  const bA = corp.querySelector("#pp-anaf");
  if (bA) bA.addEventListener("click", async () => {
    const st = corp.querySelector("#pp-anaf-stare");
    if (bA.disabled) return;
    const textB = bA.textContent;
    bA.disabled = true; bA.setAttribute("aria-busy", "true"); bA.textContent = "Se verifică…";
    try {
      const r2 = await api.get(`/tenants/${t.id}/verifica-cui/${encodeURIComponent(f.cui)}?nume=${encodeURIComponent(f.nume || "")}`);
      if (!(r2 && r2.gasit)) { st.innerHTML = `<span class="em-cui-info">CUI-ul ${esc(f.cui)} nu e găsit la ANAF.</span>`; return; }
      const dif = (r2.fise || []).filter((x) => x.diferit);
      st.innerHTML = `<span class="em-cui-info">La ANAF: „${esc(r2.denumire)}” · ${r2.platitor_tva ? "plătitor de TVA" : "neplătitor de TVA"}${
        dif.length ? "" : (f.fise || []).length ? " — numele din fișă e același." : ""}</span>${dif.length ? `
        <div class="em-cui-info pe-randuri">${esc(r2.mesaj_nume || "")}</div>
        <button type="button" class="buton-primar" id="pp-anaf-aplica" data-actiune="PUT /tenants/{tenant_id}/clienti/{client_id}">Actualizează fișa cu numele de la ANAF</button>` : ""}`;
      const ba = st.querySelector("#pp-anaf-aplica");
      if (ba) ba.addEventListener("click", async () => {
        try {
          for (const x of dif) {
            await api.put(x.fel === "clienti" ? `/tenants/${t.id}/clienti/${x.id}` : `/tenants/${t.id}/furnizori/${x.id}`, { nume: r2.denumire });
          }
          await ecranFisaPartener(corp, nav, t, cheie);
          arataMesaj(corp.querySelector("#pp-mesaj"), `Fișa are acum numele de la ANAF: „${r2.denumire}”.`, "ok");
        } catch (e) {
          arataMesaj(corp.querySelector("#pp-mesaj"), "Fișa NU s-a actualizat — " + ((e && e.mesaj) || "eroare."), "eroare");
        }
      });
    } catch (e) {
      st.innerHTML = `<span class="pe-randuri">${esc((e && e.mesaj) || "Verificarea nu s-a putut face — reîncearcă.")}</span>`;
    } finally { bA.disabled = false; bA.removeAttribute("aria-busy"); bA.textContent = textB; }
  });
}
