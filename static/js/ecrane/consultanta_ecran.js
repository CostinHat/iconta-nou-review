// consultanta_ecran.js — [17.5-F5, funcția 502] fereastra «Consultanță fiscală» a firmei: cinci rânduri, M1–M5, în ordinea fixă.
// Fiecare rând: numele, starea exactă (pastila), motivul sau datele lipsă cu locul completării, suma în lei cu sensul ei și perioada; la
// «Detalii»: pașii de calcul, ipotezele, condițiile, temeiul (act, articol, citat scurt, data de aplicare) și ce poate face contabilul.
// Fereastra doar citește (`GET /tenants/{id}/consultanta-fiscala`): nimic nu se scrie, nimic nu se trimite.

import { api, esc, bani, baniSemn, dataRo, arataMesaj } from "../api.js?v=3c07c7414f";

const TON = { "Se aplică": "ok", "Nu se aplică": "info", "Lipsesc date": "avertisment", "Lipsesc date — temei neverificat": "eroare" };
const REGIM = { micro: "microîntreprindere", profit: "impozit pe profit" };

function lista(titlu, elemente, fn = (x) => esc(x)) {
  if (!elemente || !elemente.length) return "";
  return `<h4 class="cs-det-titlu">${esc(titlu)}</h4><ul class="cs-det-lista">${elemente.map((x) => `<li>${fn(x)}</li>`).join("")}</ul>`;
}

function randMasura(m) {
  const suma = m.suma !== null && m.suma !== undefined
    ? `<p class="cs-suma"><span class="cs-suma-valoare">${esc(baniSemn(m.suma))} lei</span> · ${esc(m.sens || "")}${m.perioada ? ` · ${esc(m.perioada)}` : ""}</p>` : "";
  // M4: plafonul în lei și perioada lui, fiecare într-un singur element (D5)
  const plafon = m.cod === "M4" && m.valori && m.valori.plafon_lei
    ? `<p class="cs-plafon">Plafon: <span data-valoare="plafon_lei">${esc(bani(m.valori.plafon_lei))} lei</span> · <span data-perioada="plafon_lei">${esc(m.perioada || "")}</span></p>` : "";
  const motiv = m.stare !== "Se aplică" && m.motiv ? `<p class="cs-motiv" data-masura-motiv>${esc(m.motiv)}</p>` : "";
  const temei = lista("Temei", m.temei, (t) => `${esc(t.act)}, ${esc(t.articol)}: „${esc(t.citat)}” (${esc(t.aplicare)})`);
  const lipsuri = lista("Ce lipsește și unde se completează", m.lipsuri, (l) => `${esc(l.ce)} — ${esc(l.unde)}`);
  const det = [lista("Pașii calculului", m.pasi), lista("Ipoteze", m.ipoteze), lista("Condiții", m.conditii), temei, lipsuri,
    m.ce_poti_face ? `<h4 class="cs-det-titlu">Ce poți face</h4><p class="cs-det-p">${esc(m.ce_poti_face)}</p>` : ""].join("");
  return `<section class="cs-masura" data-masura="${esc(m.cod)}">
    <div class="cs-cap"><span class="cs-nume" data-masura-nume>${esc(m.cod)} · ${esc(m.nume)}</span>
      <span class="ds-pastila cs-stare ds-pastila-${TON[m.stare] || "info"}" data-masura-stare>${esc(m.stare)}</span></div>
    ${motiv}${suma}${plafon}
    ${det ? `<p class="cs-det-rand"><button type="button" class="buton-secundar cs-det-btn" aria-expanded="false" data-fara-actiune="arată detaliile măsurii; nu scrie nimic">Detalii</button></p>
    <div class="cs-detalii" hidden>${det}</div>` : ""}
  </section>`;
}

// [17.5-F6, BB] cele cinci rânduri sunt detaliile măsurilor, nu o listă de înregistrări: `data-fara-piesa` le ține în afara piesei de listă (care,
// la lățimi de peste 900 px, le-ar fi făcut tabel DS, iar tabelul ar fi adus în bară exportul PDF de rezervă: fereastra de consultare n-are buton principal)
// [17.5-F6, pct.6 (502)] data calculului se alege în fereastră: fiecare schimbare cere măsurile la data aleasă (`?data=AAAA-LL-ZZ`), iar
// fereastra arată data primită de la server; implicit, ziua de azi a serverului
export async function ecranConsultanta(corp, nav, t, data = "") {
  corp.innerHTML = `<h2 class="pf-titlu">Consultanță fiscală</h2><p class="ecran-nota">Se calculează măsurile…</p>`;
  let r;
  try {
    r = await api.get(`/tenants/${t.id}/consultanta-fiscala${data ? `?data=${encodeURIComponent(data)}` : ""}`);
  } catch (e) {
    corp.innerHTML = `<h2 class="pf-titlu">Consultanță fiscală</h2><div id="cs-mesaj"></div>`;
    arataMesaj(corp.querySelector("#cs-mesaj"), (e && e.mesaj) || "Măsurile nu s-au putut calcula.", "eroare");
    return;
  }
  corp.innerHTML = `<h2 class="pf-titlu">Consultanță fiscală</h2>
    <p class="pf-intro">${esc(REGIM[r.firma.regim] || r.firma.regim || "regim necompletat")} · datele firmei la <span id="cs-data-afisata">${esc(dataRo(r.data))}</span></p>
    <div class="pf-frand"><div class="camp"><label class="camp-eticheta" for="cs-data">Data calculului</label><input type="date" id="cs-data" class="camp-input" value="${esc(r.data)}"></div></div>
    <div class="cs-masuri" data-fara-piesa>${r.masuri.map(randMasura).join("")}</div>
    <p class="cs-fraza">${esc(r.fraza)}</p>`;
  corp.querySelectorAll(".cs-det-btn").forEach((b) => b.addEventListener("click", () => {
    const d = b.closest(".cs-masura").querySelector(".cs-detalii");
    d.hidden = !d.hidden;
    b.setAttribute("aria-expanded", String(!d.hidden));
    b.textContent = d.hidden ? "Detalii" : "Ascunde detaliile";
  }));
  const camp = corp.querySelector("#cs-data");
  camp.addEventListener("change", () => {
    if (/^\d{4}-\d{2}-\d{2}$/.test(camp.value) && camp.value !== r.data) ecranConsultanta(corp, nav, t, camp.value);
  });
}
