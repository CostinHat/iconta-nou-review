# -*- coding: utf-8 -*-
"""Gard: carantina (cod 07) emite TOATE cele 6 coloane ale randului C2 Rd2.2 (C2_211-216),
inclusiv C2_213 (zile angajator = Sum D_14) si C2_215 (suma angajator = Sum D_20).

Carantina 07 NU e FNUASS-integral (salarizare._CM_COD_FNUASS_INTEGRAL): angajatorul suporta
primele zile lucratoare, deci C2_213/C2_215 > 0 si sunt OBLIGATORII. Inainte de fix generatorul
emitea doar C2_211/212/214/216 -> DUK respingea cu A49c (C2_213 lipsa), A43d.2
(C2_212=C2_213+C2_214) si A49e (C2_215 lipsa). Sursa: anaf_surse/d112_struct_anaf.txt rd.49a-49f
(l.1668-1708); Nomenclator 10 G2 = 07,10,11 (carantina 07 cu portie angajator)."""
import re
from core import d112


def _gen_carantina():
    prof = {"cui": "301111003", "nume": "TEST SRL", "caen": "6202", "judet": "bucuresti"}
    sal = {
        "id": 1, "nume": "TEST", "prenume": "X", "cnp": "1850315400125",
        "data_angajare": "2026-01-15", "brut": 5000, "brut_lucrat": 3810,
        "ore_zi": 8, "judet_casa": "bucuresti", "cas": 0, "cass": 0, "impozit": 0,
        "facilitate": 0, "deducere": 0, "zile_cm": 5,
        "cm": [{"cod": "07", "zile_ang": 3, "zile_fnuass": 2,
                "brut_ang": 714, "brut_fnuass": 476, "baza": 5000,
                "serie": "AA", "numar": "111", "da": "01.08.2026",
                "di": "01.08.2026", "ds": "05.08.2026", "loc_prescriere": 1,
                "diagnostic": "999"}],
    }
    xml, _av = d112._d112_genereaza(prof, [sal], 2026, 8)
    return xml


def test_carantina_c2_emite_coloanele_angajator():
    xml = _gen_carantina()
    m = re.search(r"<angajatorC2 ([^/]*)/>", xml)
    assert m, "lipseste sectiunea angajatorC2"
    attrs = dict(re.findall(r"(\w+)=\"(-?\d+)\"", m.group(1)))
    # coloanele carantina (Rd2.2)
    assert "C2_213" in attrs, "C2_213 (zile angajator) OMIS - DUK A49c"
    assert "C2_215" in attrs, "C2_215 (suma angajator) OMIS - DUK A49e"
    assert int(attrs["C2_213"]) == 3, attrs.get("C2_213")
    assert int(attrs["C2_215"]) == 714, attrs.get("C2_215")
    # corelatie dubla struct rd.49d: C2_212 = C2_213 + C2_214
    assert int(attrs["C2_212"]) == int(attrs["C2_213"]) + int(attrs["C2_214"])
    # C2_216 = suma FNUASS, ramane corect
    assert int(attrs["C2_216"]) == 476
