// sesiune.js — SURSA UNICĂ pentru sesiune: token, user, rol.
// Tot ce ține de "cine ești" trece pe aici. Nimeni altcineva nu citește
// localStorage direct. Asta omoară problema veche (token citit din locuri
// diferite, rol dedus greșit).
// [izolare_tab_v1] sessionStorage = sesiune izolata per-tab: doua cabinete
// in doua taburi nu se mai suprascriu reciproc (bug NISTOR<->BOGDAN, 12.07.2026).

const CHEIE_TOKEN = "iconta_token";
const CHEIE_USER = "iconta_user";
// [F-preview] token de PREVIZUALIZARE portal pe cheie PROPRIE in sessionStorage (per-tab izolat, ca
// izolare_tab_v1 - NU localStorage, deci sesiunea cabinet din tab-ul ei ramane intacta). DETERMINIST:
// supravietuieste re-render/reload; are precedenta absoluta -> tab-ul preview foloseste DOAR tokenul
// preview (read-only pe backend), niciodata tokenul real copiat de window.open (bugul in-memory).
const CHEIE_PV_TOKEN = "iconta_pv_token";
const CHEIE_PV_USER = "iconta_pv_user";

let _abonati = [];  // callback-uri notificate la schimbarea sesiunii

function _user() {
  try { return JSON.parse(sessionStorage.getItem(CHEIE_USER)); }
  catch { return null; }
}

function _pvUser() {
  try { return JSON.parse(sessionStorage.getItem(CHEIE_PV_USER)); }
  catch { return null; }
}

function _anunta() {
  for (const f of _abonati) try { f(); } catch (e) { console.error(e); }
}

export const sesiune = {
  token() {
    // preview are PRECEDENTA absoluta (tab-ul preview nu foloseste niciodata tokenul cabinet copiat)
    return sessionStorage.getItem(CHEIE_PV_TOKEN) || sessionStorage.getItem(CHEIE_TOKEN);
  },

  user() {
    return _pvUser() || _user();
  },

  rol() {
    const u = _pvUser() || _user();
    return u ? u.rol : null;
  },

  esteLogat() {
    return !!(sessionStorage.getItem(CHEIE_PV_TOKEN) || sessionStorage.getItem(CHEIE_TOKEN));
  },

  // [F-preview] activeaza previzualizarea portal: token + user pe cheile PV (sessionStorage, per-tab)
  intraPreview(token, user) {
    sessionStorage.setItem(CHEIE_PV_TOKEN, token);
    sessionStorage.setItem(CHEIE_PV_USER, JSON.stringify(Object.assign({ preview: true }, user || {})));
    _anunta();
  },

  estePreview() {
    return !!sessionStorage.getItem(CHEIE_PV_TOKEN);
  },

  // setează sesiunea după login reușit (token + user din răspunsul serverului)
  intra(token, user) {
    sessionStorage.setItem(CHEIE_TOKEN, token);
    sessionStorage.setItem(CHEIE_USER, JSON.stringify(user));
    _anunta();
  },

  // șterge sesiunea (logout sau token expirat)
  iesi() {
    if (sessionStorage.getItem(CHEIE_PV_TOKEN)) {  // [F-preview] logout in preview = curata cheile PV + inchide tab
      sessionStorage.removeItem(CHEIE_PV_TOKEN);
      sessionStorage.removeItem(CHEIE_PV_USER);
      window.close();
      return;
    }
    sessionStorage.removeItem(CHEIE_TOKEN);
    sessionStorage.removeItem(CHEIE_USER);
    _anunta();
  },

  // [p48_compet] actualizeaza campuri ale userului fara re-login (ex: competente)
  actualizeazaUser(partial) {
    const u = _user() || {};
    const nou = Object.assign({}, u, partial || {});
    sessionStorage.setItem(CHEIE_USER, JSON.stringify(nou));
    _anunta();
    return nou;
  },
  // ascultă schimbările de sesiune (login/logout) -> re-randare
  laSchimbare(callback) {
    _abonati.push(callback);
  },
};
