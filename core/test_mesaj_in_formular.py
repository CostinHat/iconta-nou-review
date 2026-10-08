# -*- coding: utf-8 -*-
"""GARD ÎN BROWSER — un mesaj de stare nu șterge câmpurile formularului în care e pus (găsit 08.10.2026, la proba lotului
„Deciziile 08.10”: „Salvează” fără dată în formularul „depusă în afara iConta” făcea formularul să dispară).

CAUZA: `api.js::arataMesaj` scrie `textContent` pe elementul primit. Primit un CONTAINER cu câmpuri (formularul, rândul, ecranul
întreg — `arataMesaj(corp, …)` apare de mai multe ori în aplicație), îi ștergea conținutul: omul pierdea ce tastase.
CE FACE IMPOSIBIL: ca un mesaj pus pe un container cu câmpuri să le detașeze; zona de mesaj fără câmpuri se rescrie ca înainte.
Modulul real, în Chromium (`test_buton_blocat_structura` e tiparul).
"""
from core.test_buton_blocat_structura import pg  # noqa: F401  (aceeași pagină, același modul real)


def test_mesajul_pe_un_container_cu_campuri_nu_le_sterge(pg):  # noqa: F811
    """MUTAȚIE: ramura `querySelector("input, select, textarea")` scoasă din `arataMesaj` -> câmpul e detașat -> pică."""
    r = pg.evaluate("""async () => {
      const { arataMesaj } = await import('/static/js/api.js');
      document.body.innerHTML = '<div id="f"><input id="d" type="date" value="2026-09-24"><button id="ok">Salvează</button></div>';
      const camp = document.getElementById('d');
      arataMesaj(document.getElementById('f'), 'Scrie data depunerii.', 'avert');
      arataMesaj(document.getElementById('f'), 'Încă o dată.', 'avert');
      const f = document.getElementById('f');
      return { legat: camp.isConnected, valoare: camp.value, mesaje: [...f.querySelectorAll('.msg-in-formular')].map((x) => x.textContent),
               clasa: (f.querySelector('.msg-in-formular') || {}).className || null };
    }""")
    assert r == {"legat": True, "valoare": "2026-09-24", "mesaje": ["Încă o dată."], "clasa": "msg-in-formular msg-avert"}, r


def test_zona_de_mesaj_fara_campuri_se_rescrie_ca_inainte(pg):  # noqa: F811
    """Comportamentul vechi, pe forma lui legitimă: zona goală (sau cu mesajul anterior) primește textul direct."""
    r = pg.evaluate("""async () => {
      const { arataMesaj } = await import('/static/js/api.js');
      document.body.innerHTML = '<div id="z">vechi</div>';
      arataMesaj(document.getElementById('z'), 'nou', 'eroare');
      const z = document.getElementById('z');
      return { text: z.textContent, copii: z.children.length, eroare: z.classList.contains('msg-eroare') };
    }""")
    assert r == {"text": "nou", "copii": 0, "eroare": True}, r
