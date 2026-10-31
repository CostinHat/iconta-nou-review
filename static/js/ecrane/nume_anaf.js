// nume_anaf.js — [lotul 11, deficiența 444, comanda Costin 11.1 pct.20] „când numele de la ANAF diferă de fișa partenerului, se spune și
// se propune actualizarea.” Drumurile care verifică partenerul la ANAF în afara ecranului fișelor (NIR #sn-verifica, casa #c-cui-verif;
// emiterea facturii le poate chema la fel): răspunsul `verifica-cui` poartă fișele firmei cu acel CUI, fiecare cu `diferit`
// (`clienti_api.compara_cu_anaf`, sursa unică a comparației). Pentru fiecare fișă cu alt nume: același mesaj și același buton ca în
// ecranul fișelor (`clienti_ecran.js`): „Numele de la ANAF diferă: «X» (în fișă: «Y»).” + „Actualizează fișa cu numele de la ANAF”.
// DS cap.1 (`.buton-primar` = acțiunea principală a propunerii), cap.6 (refuzul cu textul serverului, lângă propunere).
import { api, esc } from "../api.js?v=4364ee71f3";

// căile API scrise întregi (garda rutelor fără apelant le caută literal)
const FISA = {
  clienti: { url: (tid, id) => `/tenants/${tid}/clienti/${id}`, act: "PUT /tenants/{tenant_id}/clienti/{client_id}" },
  furnizori: { url: (tid, id) => `/tenants/${tid}/furnizori/${id}`, act: "PUT /tenants/{tenant_id}/furnizori/{furnizor_id}" },
};

/** Adaugă în `zona` propunerea de actualizare pentru fiecare fișă cu alt nume decât ANAF (`fel` = numai „clienti” / „furnizori”).
 *  `pre` = prefixul id-urilor (unic pe ecran). Întoarce câte fișe diferă. */
export function propuneNumeAnaf(zona, r, tid, { fel = null, pre = "anaf" } = {}) {
  if (!zona || !r || !r.denumire) return 0;
  const dif = (r.fise || []).filter((f) => f.diferit && FISA[f.fel] && (!fel || f.fel === fel));
  dif.forEach((f) => {
    const d = document.createElement("div");
    d.id = `${pre}-fisa-${f.fel}-${f.id}`;
    d.innerHTML = `<span class="em-cui-info">Numele de la ANAF diferă: „${esc(r.denumire)}” (în fișă: „${esc(f.nume || "")}”).</span>
      <button type="button" class="buton-primar" id="${pre}-anaf-aplica-${f.fel}-${f.id}" data-actiune="${FISA[f.fel].act}">Actualizează fișa cu numele de la ANAF</button>
      <span class="em-cui-rau" id="${pre}-anaf-eroare-${f.fel}-${f.id}"></span>`;
    const b = d.querySelector("button");
    b.addEventListener("click", async () => {
      if (b.disabled) return;
      b.disabled = true; b.setAttribute("aria-busy", "true");
      try {
        await api.put(FISA[f.fel].url(tid, f.id), { nume: r.denumire });
        d.innerHTML = `<span class="em-cui-info">${esc(f.nume || "")}: numele din fișă e acum „${esc(r.denumire)}”.</span>`;
      } catch (e) {
        b.disabled = false; b.removeAttribute("aria-busy");
        const ec = (e && e.erori_campuri) || [];
        d.querySelector(".em-cui-rau").textContent = `${f.nume || ""}: fișa NU s-a salvat — `
          + (ec.length ? ec.map((c) => c.mesaj).join(" ") : ((e && e.mesaj) || "eroare."));
      }
    });
    zona.appendChild(d);
  });
  return dif.length;
}
