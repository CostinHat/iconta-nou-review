// sesiune.js — SURSA UNICĂ pentru sesiune: token, user, rol.
// Tot ce ține de "cine ești" trece pe aici. Nimeni altcineva nu citește
// localStorage direct. Asta omoară problema veche (token citit din locuri
// diferite, rol dedus greșit).
// [izolare_tab_v1] sessionStorage = sesiune izolata per-tab: doua cabinete
// in doua taburi nu se mai suprascriu reciproc (bug NISTOR<->BOGDAN, 12.07.2026).

const CHEIE_TOKEN = "iconta_token";
const CHEIE_USER = "iconta_user";

let _abonati = [];  // callback-uri notificate la schimbarea sesiunii

// [F-preview] token de PREVIZUALIZARE portal, tab-local, IN-MEMORY (NU sessionStorage) -> sesiunea
// cabinet din tab-ul ei ramane intacta; nu persista la reload; logout in preview inchide tab-ul.
let _tokenPreview = null, _userPreview = null;

function _user() {
  try { return JSON.parse(sessionStorage.getItem(CHEIE_USER)); }
  catch { return null; }
}

function _anunta() {
  for (const f of _abonati) try { f(); } catch (e) { console.error(e); }
}

export const sesiune = {
  token() {
    return _tokenPreview || sessionStorage.getItem(CHEIE_TOKEN);
  },

  user() {
    return _userPreview || _user();
  },

  rol() {
    const u = _userPreview || _user();
    return u ? u.rol : null;
  },

  esteLogat() {
    return !!(_tokenPreview || sessionStorage.getItem(CHEIE_TOKEN));
  },

  // [F-preview] activeaza previzualizarea portal: token + user DOAR in-memory (nu sessionStorage)
  intraPreview(token, user) {
    _tokenPreview = token;
    _userPreview = Object.assign({ preview: true }, user || {});
    _anunta();
  },

  estePreview() {
    return !!_tokenPreview;
  },

  // setează sesiunea după login reușit (token + user din răspunsul serverului)
  intra(token, user) {
    sessionStorage.setItem(CHEIE_TOKEN, token);
    sessionStorage.setItem(CHEIE_USER, JSON.stringify(user));
    _anunta();
  },

  // șterge sesiunea (logout sau token expirat)
  iesi() {
    if (_tokenPreview) {  // [F-preview] logout in preview = inchide tab-ul, NU sterge sesiunea cabinet
      _tokenPreview = null; _userPreview = null;
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
