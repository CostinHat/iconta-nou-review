// coada_trimite.js — trimiterea unei declarații în coada de validare, din ORICE ecran (Declarații, Bilanț).
//
// [comanda Costin 07.10.2026] UN singur drum, ca ecranele să nu poată diverge:
//  - C3: „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului. O eroare DUK oprește.”
//    Serverul răspunde `ATENTIONARI_NECONFIRMATE` -> aici se arată atenționările și se cere confirmarea (retrimisă ca
//    `motiv_trecere`, păstrată cu numele omului); `ERORI_DUK` -> se arată, fără portiță.
//  - C1: refuzul spune motivul REAL venit de la server, nu o presupunere („Poate există deja o declarație…” apărea și la o eroare 500).
//  - C11: bilanțul intră în coadă pe același drum ca orice declarație.
import { api, esc, arataMesaj, aduInVedere } from "../api.js?v=72aa1cbbdb";

// [deficiența 222, comanda Costin 10.10.2026] confirmarea intrării în coadă e ACEEAȘI casetă din orice ecran (Declarații, Bilanț) —
// nu un rând de text: bifa, „Trimisă în coada de validare”, declarația și perioada. `cine` = ce urmează („a fost trimisă seniorului …”).
export function casetaTrimisa(tip, perioada, cine) {
  return `<div class="dec-gata">
      <div class="dec-gata-bif">✓</div>
      <div class="dec-gata-titlu">Trimisă în coada de validare</div>
      <div class="dec-gata-sub"><b>${esc(tip)}</b> · ${esc(perioada)} ${esc(cine)}</div>
    </div>`;
}

export async function trimiteInCoada(zona, body, laSucces, confirmare) {
  const corp = Object.assign({}, body);
  if (confirmare) corp.motiv_trecere = confirmare;
  try {
    const r = await api.post("/coada", corp);
    laSucces(r);
    // [08.10.2026, decizia Costin §6 pct.7 — R36] ciornele perioadei nu opresc coada: avertismentul porții se arată după intrare
    // (ecranul care se redesenează la succes îl arată el, din `r`; aici numai dacă zona a rămas pe ecran)
    if (zona.isConnected && r && (r.avertismente_poarta || []).length) arataMesaj(zona, r.avertismente_poarta.join(" "), "avert");
    return r;
  } catch (e) {
    const det = (e && e.detaliu && typeof e.detaliu === "object") ? e.detaliu : {};
    if (det.cod === "ATENTIONARI_NECONFIRMATE") {
      zona.innerHTML = `<div class="caseta-atentie"><div class="ca-mesaj">${esc(det.mesaj || "")}
          <pre class="dec-atentionari">${esc(det.erori || "")}</pre>
          <label class="camp"><span class="camp-eticheta">Confirmarea ta (se păstrează cu numele tău) *</span>
          <textarea id="coada-confirmare" class="camp-input" rows="3" aria-label="Confirmarea atenționărilor"></textarea></label>
          <button class="buton-primar" id="coada-confirma" data-actiune="POST /coada">Confirm și trimit în coadă</button></div></div>`;
      zona.querySelector("#coada-confirma").addEventListener("click", () => {
        const t = (zona.querySelector("#coada-confirmare").value || "").trim();
        if (!t) { arataMesaj(zona.querySelector(".ca-mesaj"), "Scrie confirmarea: de ce declarația e corectă așa.", "eroare"); return; }
        trimiteInCoada(zona, body, laSucces, t);
      });
      aduInVedere(zona);
      return null;
    }
    const text = (typeof (e && e.mesaj) === "string" && e.mesaj) || det.mesaj || "Nu s-a putut trimite în coadă.";
    arataMesaj(zona, text + (det.erori ? " — " + det.erori : ""), "eroare");
    return null;
  }
}
