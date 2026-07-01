// sesiune.js — SURSA UNICĂ pentru sesiune: token, user, rol.
// Tot ce ține de "cine ești" trece pe aici. Nimeni altcineva nu citește
// localStorage direct. Asta omoară problema veche (token citit din locuri
// diferite, rol dedus greșit).

const CHEIE_TOKEN = "iconta_token";
const CHEIE_USER = "iconta_user";

let _abonati = [];  // callback-uri notificate la schimbarea sesiunii

function _user() {
  try { return JSON.parse(localStorage.getItem(CHEIE_USER)); }
  catch { return null; }
}

function _anunta() {
  for (const f of _abonati) try { f(); } catch (e) { console.error(e); }
}

export const sesiune = {
  token() {
    return localStorage.getItem(CHEIE_TOKEN);
  },

  user() {
    return _user();
  },

  rol() {
    const u = _user();
    return u ? u.rol : null;
  },

  esteLogat() {
    return !!localStorage.getItem(CHEIE_TOKEN);
  },

  // setează sesiunea după login reușit (token + user din răspunsul serverului)
  intra(token, user) {
    localStorage.setItem(CHEIE_TOKEN, token);
    localStorage.setItem(CHEIE_USER, JSON.stringify(user));
    _anunta();
  },

  // șterge sesiunea (logout sau token expirat)
  iesi() {
    localStorage.removeItem(CHEIE_TOKEN);
    localStorage.removeItem(CHEIE_USER);
    _anunta();
  },

  // [p48_compet] actualizeaza campuri ale userului fara re-login (ex: competente)
  actualizeazaUser(partial) {
    const u = _user() || {};
    const nou = Object.assign({}, u, partial || {});
    localStorage.setItem(CHEIE_USER, JSON.stringify(nou));
    _anunta();
    return nou;
  },
  // ascultă schimbările de sesiune (login/logout) -> re-randare
  laSchimbare(callback) {
    _abonati.push(callback);
  },
};
