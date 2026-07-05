// app.js — punctul de pornire. Login -> navigator cu desktopul rolului.

import { sesiune } from "./sesiune.js";
import { ecranLogin } from "./ecrane/login.js";
import { creeazaNavigator } from "./navigator.js";
import { desktopCabinet } from "./ecrane/cabinet.js?v=4";
import { desktopAsistent } from "./ecrane/asistent.js";
import { desktopPortal } from "./ecrane/portal.js?v=5";
import { desktopAdmin } from "./ecrane/admin.js"; // [p37_admin_desktop]

const radacina = document.getElementById("app");

function randeaza() {
  if (!sesiune.esteLogat()) {
    radacina.innerHTML = "";
    ecranLogin(radacina);
    return;
  }

  switch (sesiune.rol()) {
    case "client":
      creeazaNavigator(radacina, desktopPortal);
      break;
    case "angajat":
      creeazaNavigator(radacina, desktopAsistent);
      break;
    case "superadmin": // [p37_admin_desktop]
      creeazaNavigator(radacina, desktopAdmin);
      break;
    default: // admin_firma
      creeazaNavigator(radacina, desktopCabinet);
  }
}

sesiune.laSchimbare(randeaza);
randeaza();
