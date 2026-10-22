# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 440 pe server (comanda Costin 11.1 pct.16, verbatim): „toate erorile apar deodată, fiecare cu textul ei, în casetă
și lângă câmp.” — colectorul unic `core.erori.ErorileFormularului` (DS cap.6 v2.30 pct.4: „fail-fast e INTERZIS pe formularele multi-câmp”).

Temei: N/A — contractul refuzului (G10, `erori_campuri`).

CE FACE IMPOSIBIL: (1) colectorul care refuză la prima problemă sau pierde una; (2) refuzul fără `erori_campuri` (ecranul n-ar ști
câmpurile); (3) `mesaj` care numește numai prima problemă (ecranul care citește numai fraza ar arăta una); (4) refuzul fără probleme.
Plus clasa „lista adunată, trimisă trunchiată” (`er[0]`): inventarul lotului 11 a găsit `firma_profil_api.salveaza_date` (capitalul) și
`regim_tva_incasare.salveaza` — garda de la capăt le numește până se repară (lista de lucru U0).
"""
import ast
import glob
import io
import os

import pytest

from core import erori

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_colectorul_refuza_o_data_cu_toate_erorile():
    """1 + 2 + 3. MUTAȚIE: `camp` care ridică imediat (`raise DateInvalide(...)` în `camp`) -> a doua eroare lipsește -> pică."""
    er = erori.ErorileFormularului()
    er.camp("df-nume", "Numele firmei lipsește.").camp("df-cui", "CUI-ul nu are cifra de control corectă.")
    er.fara_camp("Perioada 09/2026 e încheiată.")
    with pytest.raises(erori.DateInvalide) as ex:
        er.refuza()
    d = ex.value.detaliu
    assert d["erori_campuri"] == [{"camp": "df-nume", "mesaj": "Numele firmei lipsește."},
                                  {"camp": "df-cui", "mesaj": "CUI-ul nu are cifra de control corectă."}]   # 440: „toate erorile deodată”
    assert d["mesaj"] == ("Formularul nu s-a salvat:\n— Perioada 09/2026 e încheiată.\n— Numele firmei lipsește.\n"
                          "— CUI-ul nu are cifra de control corectă.")                                       # „fiecare cu textul ei”


def test_o_singura_eroare_are_fraza_ei_iar_fara_erori_nu_refuza():
    """4. MUTAȚIE: `if self:` scos din `refuza` -> refuză și formularul corect -> pică."""
    erori.ErorileFormularului().refuza()   # nimic de refuzat
    er = erori.ErorileFormularului().camp("cui", "CUI-ul lipsește.").camp("cui", "CUI-ul lipsește.")
    assert er.detaliu() == {"mesaj": "CUI-ul lipsește.", "erori_campuri": [{"camp": "cui", "mesaj": "CUI-ul lipsește."}]}


def _trunchiate_in(src, nume):
    """`return {..., "camp": X[0][0], "mesaj": X[0][1]}` în sursa `src` — lista de erori adunată, trimisă numai cu prima."""
    out = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Dict):
            chei = [getattr(k, "value", None) for k in n.keys]
            if set(chei) >= {"camp", "mesaj"}:   # operator de mulțime (core/test_garzi_pe_text.py)
                v = n.values[chei.index("camp")]
                if (isinstance(v, ast.Subscript) and isinstance(v.value, ast.Subscript)
                        and getattr(v.value.slice, "value", None) == 0):
                    out.append("%s:%d" % (nume, n.lineno))
    return out


def _trunchiate():
    fisiere = [p for p in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))) if not os.path.basename(p).startswith("test_")]
    assert len(fisiere) > 100, "scanul vede %d module în core/ — domeniul s-a rupt (anti-vacuu)" % len(fisiere)
    out = []
    for p in fisiere:
        out += _trunchiate_in(io.open(p, encoding="utf-8").read(), os.path.basename(p))
    return out


def test_calibrare_forma_trunchiata_e_prinsa_iar_lista_intreaga_nu():
    """Anti-vacuu al gărzii de mai jos: forma veche e găsită (o garda care n-ar găsi nimic ar trece pe orice), forma întreagă nu."""
    assert _trunchiate_in('def f(_er):\n    return {"ok": False, "camp": _er[0][0], "mesaj": _er[0][1]}\n', "x.py") == ["x.py:2"]
    assert _trunchiate_in('def f(er):\n    return {"ok": False, "erori_campuri": er, "camp": None, "mesaj": "x"}\n', "y.py") == []


def test_lista_adunata_nu_se_trimite_trunchiata():
    """Clasa: `return {"ok": False, "camp": _er[0][0], "mesaj": _er[0][1]}` — validarea le adunase pe toate, refuzul trimitea una.
    MUTAȚIE: forma veche repusă oriunde în core/ -> pică. (Roșu până la lista de lucru U0: firma_profil_api.py:516,
    regim_tva_incasare.py:284.)"""
    rele = _trunchiate()
    assert not rele, "lista de erori trimisă numai cu prima (440: „toate erorile apar deodată”): %s" % rele
