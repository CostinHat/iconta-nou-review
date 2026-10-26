# -*- coding: utf-8 -*-
"""GARD — deficiența 220 (comanda Costin 10.10.2026, verbatim în DECIZII): „Control fiscal: declarațiile apar cu roșu încă dinainte de
termen. Roșu înseamnă termen depășit.” Măsurat pe producție (10.10.2026): F1 roșu cu 0 restanțe și 5 de urmărit — roșul venea din
„TVA nedeclarat” / „Salarii nedeclarate” pe 09/2026, termen 26.10. Regula: DS cap.8 v2.87; aici, două capete ale ei:
  · starea firmei (`common.pastila_firma`) e roșie numai dacă starea de bază e roșie (o restanță); o constatare urcă cel mult la galben;
  · randarea Control fiscal (`control_verdict.js`) nu pune culoare roșie pe nicio constatare; roșul rămâne al „Restanțe”.
Gardul textual al aceleiași reguli e `ROSU_DOAR_RESTANTA` în verificator."""
import io
import itertools
import json
import os
import re
import subprocess

from core.common import pastila_firma

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARI = ("verde", "galben", "rosu", "gri")


def test_firma_e_rosie_numai_cu_o_restanta():
    """Toate combinațiile: bază × până la două constatări. MUTAȚIE: plafonul la galben scos din `pastila_firma` -> o firmă verde cu o
    constatare roșie iese roșie -> pică."""
    for baza in STARI:
        for n in (0, 1, 2):
            for cs in itertools.product(STARI, repeat=n):
                st = pastila_firma(baza, [{"stare": c} for c in cs])
                assert (st == "rosu") == (baza == "rosu"), (baza, cs, st)
    assert pastila_firma("verde", [{"stare": "rosu"}]) == "galben"      # neconcordanța înainte de termen: de urmărit
    assert pastila_firma("gri", [{"stare": "rosu"}]) == "galben"        # o problemă confirmată bate o necunoaștere (20.08)
    assert pastila_firma("gri", [{"stare": "verde"}]) == "gri"


_STUB = {
    r'from "\./verdict\.js[^"]*"': 'from "data:text/javascript,export const VERDICT_POZITIV={control_depus:%22ok%22}"',
    r'from "\.\./api\.js[^"]*"': ('from "data:text/javascript,export const api=0,confirmaCaseta=0,arataMesaj=0,focusFaraSalt=0,refuzPeRand=0;'
                                 'export const atributeInactiv=()=>String();'   # [lotul 13, 675] butonul inactiv cu motiv
                                 'export const esc=(s)=>String(s);export const dataRo=(s)=>String(s);export const bani=(n)=>String(n)"'),
    r'from "\./nir_legare\.js[^"]*"': 'from "data:text/javascript,export const cuLegareaNir=0,interogareLegare=0"',
    # [lotul 12, 463] starea SPV a firmei, randată după inserare (`legaVerdict`): corpul verdictului n-o atinge
    r'from "\./spv_stare\.js[^"]*"': 'from "data:text/javascript,export const randeazaStareSpv=0"',
}
_ROSU = re.compile(r"cf-rosu|pct-rosu|cf-termen-rosu|--rosu-semafor|#ff8a80")


def _randeaza(tmp_path, payload):
    src = io.open(os.path.join(RAD, "static/js/ecrane/control_verdict.js"), encoding="utf-8").read()
    for a, b in _STUB.items():
        src, n = re.subn(a, b, src)
        assert n == 1, a
    # `cate` (numeralul acordat) e cel real din plural.js, reexportat de stubul lui api.js
    (tmp_path / "plural.mjs").write_text(io.open(os.path.join(RAD, "static/js/plural.js"), encoding="utf-8").read(), encoding="utf-8")
    src, n = re.subn(r'export const bani=\(n\)=>String\(n\)"', lambda m: m.group(0)[:-1] + ';export {cate,dupaNumar} from %%22%s%%22"'
                     % (tmp_path / "plural.mjs").as_uri(), src)
    assert n == 1
    (tmp_path / "cv.mjs").write_text(src, encoding="utf-8")
    cod = "import('%s').then((m) => console.log(m.randeazaCorpVerdict(%s)))" % ((tmp_path / "cv.mjs").as_posix(), json.dumps(payload))
    r = subprocess.run(["node", "-e", cod], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    return r.stdout


def test_detaliul_nu_coloreaza_rosu_decat_restantele(tmp_path):
    """F1 de pe producție, în mic: nimic restant, „TVA nedeclarat” roșu la verificator, o verificare contabilă roșie, coerența TVA
    neîndeplinită. Ecranul: nicio culoare roșie. Cu o restanță: „Restanțe” e roșu (anti-vacuu). MUTAȚIE: `stareAfisata` întoarce
    starea neschimbată -> bulina constatării iese roșie -> pică."""
    const = {"stare": "rosu", "mesaj": "TVA nedeclarat (generat azi) ar avea 1.000,00", "temei": "CF art.322"}
    p = {"stare": "galben", "lipsa": [], "urmarit": [{"tip": "d300", "an": 2026, "luna": 9, "perioada": "09/2026", "termen": "2026-10-26"}],
         "verificari_contabile": {"tva_incrucisat": {"stare": "rosu", "constatari": [const]}, "tva": {"suma": 5, "rezultat": None}},
         "contabil": [{"stare": "rosu", "eticheta": "Echilibru", "mesaj": "Balanța nu se închide"}]}
    html = _randeaza(tmp_path, p)
    assert "TVA nedeclarat" in html and "Balanța nu se închide" in html, html[:600]      # anti-vacuu: constatările sunt pe ecran
    assert not _ROSU.search(html), _ROSU.search(html).group(0)
    p["lipsa"] = [{"tip": "d112", "an": 2026, "luna": 8, "perioada": "08/2026", "termen": "2026-09-25"}]
    html = _randeaza(tmp_path, p)
    assert re.search(r'cf-grup-titlu cf-rosu">Restanțe \(1\)', html), html[:600]
