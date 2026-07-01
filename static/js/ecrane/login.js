// login.js — poarta de intrare. Un singur formular pentru toate rolurile;
// serverul întoarce rolul, routerul decide unde mergi.

import { api } from "../api.js";
import { sesiune } from "../sesiune.js";

export function ecranLogin(radacina) {
  const shell = document.createElement("div");
  shell.className = "login-shell";

  const card = document.createElement("div");
  card.className = "login-card";

  card.innerHTML = `
    <div class="login-brand">
      <img class="login-logo-img" src="/static/logo_login.png" alt="iConta">
      <span class="login-tagline">Contabilitatea cu control fiscal</span>
    </div>
    <label class="camp">
      <span class="camp-eticheta">Email</span>
      <input type="email" class="camp-input" id="login-email" autocomplete="username" autofocus>
    </label>
    <label class="camp">
      <span class="camp-eticheta">Parolă</span>
      <input type="password" class="camp-input" id="login-parola" autocomplete="current-password">
    </label>
    <div class="login-eroare" id="login-eroare" hidden></div>
    <button class="buton-primar" id="login-buton">Autentificare</button>
  `;

  shell.appendChild(card);
  radacina.appendChild(shell);

  const email = card.querySelector("#login-email");
  const parola = card.querySelector("#login-parola");
  const buton = card.querySelector("#login-buton");
  const eroare = card.querySelector("#login-eroare");

  function arataEroare(text) {
    eroare.textContent = text;
    eroare.hidden = false;
  }

  async function intra() {
    eroare.hidden = true;
    if (!email.value || !parola.value) {
      arataEroare("Completează email și parolă.");
      return;
    }
    buton.disabled = true;
    buton.textContent = "Se verifică…";
    try {
      const r = await api.post("/auth/login", {
        email: email.value.trim(),
        parola: parola.value,
      });
      sesiune.intra(r.token, r.user);  // routerul preia de aici
    } catch (e) {
      arataEroare(e.mesaj || "Autentificare eșuată.");
      buton.disabled = false;
      buton.textContent = "Autentificare";
    }
  }

  buton.addEventListener("click", intra);
  parola.addEventListener("keydown", (e) => { if (e.key === "Enter") intra(); });
  email.addEventListener("keydown", (e) => { if (e.key === "Enter") parola.focus(); });
}
