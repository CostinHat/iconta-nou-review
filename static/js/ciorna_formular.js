// [deficiența 267, comanda Costin 15.10.2026 noaptea, verbatim în DECIZII „Lotul 5 — comanda 3”: „formularul «Înregistrează cabinetul
// tău» pierde tot ce s-a completat dacă e închis sau dacă utilizatorul iese din pagină. Se păstrează și se reface la redeschidere, mai
// puțin parolele; se șterge după crearea contului. Verifici clasa la formularele lungi.”]
// Ciorna unui formular de creare: câmpurile numite, la fiecare tastă; refăcute la redeschidere (și după ieșirea din pagină); șterse când
// documentul s-a creat. Parolele nu se numesc, deci nu se păstrează niciodată. O ciornă mai veche de PASTRARE_ZILE se aruncă. Folosită
// de: înregistrarea cabinetului (login.js), salariatul nou (firme.js), concediul medical (flux_concediu.js).
// [deficiența 495, lotul 12, cu clasa ei] „Ciorna facturii e salvată doar în browser; pe alt calculator nu se regăsește.” Un formular
// al unei FIRME (`server` = {tenantId, formular}) își ține ciorna pe SERVER, pe utilizator + firmă (`core/ciorne_formular.py`):
// browserul păstrează doar copia NETRIMISĂ (o reîncărcare imediată nu pierde ultima tastă), care pleacă la server și apoi se șterge;
// la deschidere se reface ciorna serverului, sau copia din browser dacă e mai nouă (ciorna veche, de dinainte de 495, urcă așa pe
// server). Transportul (`ciornaPeServer`) e același pentru ciorna facturii (`emitere_ecran.js`). Înregistrarea cabinetului rămâne în
// browser: înaintea contului nu există utilizator pe server. Gard: core/test_ciorna_formular.py, core/test_lot12_emit_ciorna.py + e2e
// test_def_267_*, test_def_495_*.
import { api } from "./api.js?v=9bcf50c899";
import { sesiune } from "./sesiune.js?v=898215e0ee";

const PASTRARE_ZILE = 7;

function _proaspata(c) {
  return !!c && !!c.campuri && Date.now() - (Number(c.salvat_la) || 0) <= PASTRARE_ZILE * 86400000;
}
function _local(cheie) {
  try { return JSON.parse(localStorage.getItem(cheie) || "null"); } catch { return null; }
}
function _stergeLocal(cheie) {
  try { localStorage.removeItem(cheie); } catch { /* stocare blocată */ }
}

const _transporturi = new Map();   // aceeași ciornă (cheie + adresă) = același șir de cereri, peste redeschideri

/**
 * [495] Transportul unei ciorne spre server. `cheie` = locul copiei netrimise în browser (pe utilizator + firmă + formular), `url` =
 * `/tenants/{id}/ciorne-formular/{formular}`. Cererile pleacă pe rând: o ștergere nu e întrecută de o scriere mai veche.
 *   incarca() -> ciorna de refăcut: a serverului, sau copia din browser dacă e mai nouă (și atunci urcă pe server); null = nimic
 *   scrie(c)  -> copia în browser acum, la server după o pauză de tastare; trimisă, copia din browser se șterge
 *   sterge(cuServer) -> scoate copia din browser și (dacă `cuServer`) ciorna de pe server
 */
export function ciornaPeServer(cheie, url) {
  const id = cheie + " " + url;
  if (_transporturi.has(id)) return _transporturi.get(id);
  let ceas = null;
  let coada = Promise.resolve();
  const laServer = (fn) => { coada = coada.then(fn).catch(() => { /* rămâne copia din browser; pleacă la următoarea scriere */ }); return coada; };
  const trimite = () => {
    clearTimeout(ceas);
    return laServer(async () => {
      const c = _local(cheie);
      if (!c) return;
      await api.put(url, { continut: c });
      const acum = _local(cheie);
      if (acum && acum.salvat_la === c.salvat_la) _stergeLocal(cheie);   // trimisă; o modificare de după rămâne de trimis
    });
  };
  const t = {
    async incarca() {
      clearTimeout(ceas);
      await coada;
      let server = null;
      try { server = ((await api.get(url)) || {}).ciorna || null; } catch { server = null; }
      const local = _local(cheie);
      if (local && (!server || String(local.salvat_la || "") >= String(server.salvat_la || ""))) { await trimite(); return local; }
      if (local) _stergeLocal(cheie);   // lăsată aici, continuată între timp pe alt calculator: rămâne cea continuată
      return server;
    },
    scrie(c) {
      try { localStorage.setItem(cheie, JSON.stringify(c)); } catch { /* stocare blocată: pleacă direct la server */ }
      clearTimeout(ceas);
      ceas = setTimeout(trimite, 600);
    },
    sterge(cuServer = true) {
      clearTimeout(ceas);
      _stergeLocal(cheie);
      if (cuServer) laServer(() => api.del(url));
    },
  };
  _transporturi.set(id, t);
  return t;
}

/**
 * @param {Element} radacina   formularul (ascultă `input` / `change` pe el)
 * @param {string} cheie       cheia din localStorage (una pe formular și, unde e cazul, pe firmă)
 * @param {string[]} campuri   id-urile câmpurilor păstrate — FĂRĂ parole
 * @param {{tenantId: number, formular: string}} [server]  [495] formularul unei firme: ciorna stă pe server (utilizator + firmă)
 * @returns {{refacuta: boolean, sterge: Function, gata: Promise<boolean>}}  `refacuta`: ce s-a refăcut pe loc, din browser; `gata`:
 *          true dacă ciorna de pe server (scrisă pe alt calculator) a refăcut formularul după deschidere
 */
export function ciornaFormular(radacina, cheie, campuri, server = null) {
  let t = null;
  if (server) {
    const u = sesiune.user();
    const cheieVeche = cheie;
    cheie = `${cheie}:u${u && u.id != null ? u.id : "anonim"}`;   // [495, 65] pe utilizator: alt cont din același browser n-o vede
    try {   // ciorna de dinainte de 495 (cheia fără utilizator) devine a celui care deschide primul formularul
      const v = localStorage.getItem(cheieVeche);
      if (v && !localStorage.getItem(cheie)) localStorage.setItem(cheie, v);
      localStorage.removeItem(cheieVeche);
    } catch { /* stocare blocată */ }
    t = ciornaPeServer(cheie, `/tenants/${server.tenantId}/ciorne-formular/${encodeURIComponent(server.formular)}`);
  }
  const umple = (c) => {
    let ceva = false;
    for (const id of campuri) {
      const el = radacina.querySelector("#" + id);
      if (!el || el.readOnly || el.disabled || !(id in c.campuri)) continue;
      if (el.type === "checkbox") el.checked = !!c.campuri[id];
      else el.value = c.campuri[id];
      ceva = ceva || !!c.campuri[id];
    }
    return ceva;
  };
  const c = _local(cheie);
  const local = _proaspata(c) ? c : null;
  if (c && !local) _stergeLocal(cheie);   // mai veche de PASTRARE_ZILE: nu se reface și nu urcă pe server
  const refacuta = local ? umple(local) : false;
  let exista = !!local;
  let atins = false;   // omul a scris deja: ciorna sosită de pe server nu-i mai înlocuiește ce a scris
  const salveaza = () => {
    atins = true;
    const v = {};
    let are = false;
    for (const id of campuri) {
      const el = radacina.querySelector("#" + id);
      if (!el || el.readOnly) continue;
      v[id] = el.type === "checkbox" ? el.checked : el.value;
      are = are || (el.type !== "checkbox" && String(el.value).trim() !== "");
    }
    const ciorna = { v: 1, salvat_la: Date.now(), campuri: v };
    if (t) {
      if (are) { t.scrie(ciorna); exista = true; } else if (exista) { t.sterge(true); exista = false; }
      return;
    }
    try {
      if (are) localStorage.setItem(cheie, JSON.stringify(ciorna));
      else localStorage.removeItem(cheie);
    } catch { /* stocare plină sau blocată: formularul merge mai departe, numai ciorna lipsește */ }
  };
  // [495] ciorna de pe server (scrisă pe alt calculator) reface formularul după deschidere; copia locală mai nouă urcă și rămâne
  const gata = !t ? Promise.resolve(false) : t.incarca().then((s) => {
    if (!s || atins || !_proaspata(s) || (local && s.salvat_la === local.salvat_la)) return false;
    exista = true;
    return umple(s);
  });
  radacina.addEventListener("input", salveaza);
  radacina.addEventListener("change", salveaza);
  return {
    refacuta,
    gata,
    sterge: () => {
      if (t) { t.sterge(true); exista = false; return; }
      try { localStorage.removeItem(cheie); } catch { /* idem */ }
    },
  };
}
