# -*- coding: utf-8 -*-
"""core/test_salariati_import_iban.py — GARD: importul de salariati (stratul 4 migrare) aduce IBAN
(contul de plata SEPA): coloana mapata la parsare, valoare validata mod-97, scrisa la INSERT.

DEFECT (audit tenant_001, 17.08.2026): pana acum importul NU avea IBAN deloc — parserul nu-l mapa
(niciun i_iban), verifica_randuri nu-l valida, writer-ul nu-l scria, iar modelul CSV (migrare.js) nu-l
oferea. Orice firma migrata avea iban=NULL pe TOTI salariatii -> fisierul de plata SEPA ii excludea pe toti
(plata_salarii.meta['fara_iban']). COR era deja mapat+scris (test_q16_cor) — IBAN ramasese pe dinafara.

TEMEI: DS cap.6 (validare preventiva cu mesaj explicativ); plata_salarii ("un IBAN gresit trimite banii
altcuiva - fisierul se genereaza DOAR pentru salariatii cu IBAN valid").
"""
from core import salariati_import_api as _sal

_CSV = (b"nume,prenume,cnp,data angajare,norma,functie de baza,scutit contributie minima,brut,judet,cor,iban\n"
        b"Popescu,Ana,2900215410011,2020-01-15,intreaga,da,nu,5000,B,251401,RO49AAAA1B31007593840000\n")


def test_extrage_mapeaza_iban():
    r = _sal.extrage(_CSV, "x.csv")
    assert r and r[0].get("iban") == "RO49AAAA1B31007593840000", \
        "parserul de import NU mapeaza coloana IBAN: %r" % (r[0] if r else None)


def test_verifica_iban_invalid_semnalat():
    rand = {"nume": "POP", "prenume": "ION", "cnp": "2900215410011", "cnp_valid": True,
            "tip_norma": "intreaga", "ore_zi": 8, "functie_baza": True, "scutit_contrib_minim": False, "iban": "RO00AAAA1B31007593840000"}
    er = _sal.verifica_randuri([rand])
    assert any(e.get("regula") == "iban_invalid" for e in er), \
        "IBAN invalid la import NU e semnalat (banii pot pleca altcuiva): %r" % er


def test_verifica_iban_valid_trece():
    rand = {"nume": "POP", "prenume": "ION", "cnp": "2900215410011", "cnp_valid": True,
            "tip_norma": "intreaga", "ore_zi": 8, "functie_baza": True, "scutit_contrib_minim": False, "iban": "RO49AAAA1B31007593840000"}
    er = _sal.verifica_randuri([rand])
    assert not any(e.get("regula") == "iban_invalid" for e in er), er


def _insert_salariati(sql):
    """Coloanele unui `INSERT INTO salariati (…) VALUES …`, din instrucțiune (verbul, tabela, lista de coloane), sau None pentru orice
    altă instrucțiune — nu „șirul apare în SQL” (core/test_garzi_pe_text.py)."""
    import re
    m = re.match(r"\s*INSERT\s+INTO\s+salariati\s*\(([^)]*)\)", sql or "", re.I)
    return [c.strip() for c in m.group(1).split(",")] if m else None


def test_importa_scrie_iban():
    captured = {}

    class _Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=None):
            self.ultim = sql
            if _insert_salariati(sql) is not None:
                captured["sql"] = sql
                captured["params"] = params

        def fetchone(self):
            # [lotul 10, 426 — clasa] statele de plată ale salariaților existenți (`existent`): niciunul, firma n-are salariați
            # tabela citită (după FROM), nu un sub-șir al instrucțiunii
            if _insert_salariati(self.ultim) is not None:
                return (1, True)                      # [lotul 11, 447] `RETURNING id, (xmax = 0)`: salariat nou
            return (0, None) if self.ultim.upper().partition(" FROM ")[2].split()[:1] == ["STATE_PLATA"] else (1,)

        def fetchall(self):
            return []                                 # [426] niciun salariat cu același CNP: importul nu actualizează nicio fișă

    class _Conn:
        def cursor(self):
            return _Cur()

        def commit(self):
            pass

    rand = {"nume": "POP", "prenume": "ION", "cnp": "2900215410011", "cnp_valid": True,
            "tip_norma": "intreaga", "ore_zi": 8, "functie_baza": True, "scutit_contrib_minim": False, "salariu_brut": 5000, "judet_casa": "B",
            "cor": "251401", "iban": "RO49AAAA1B31007593840000", "data_angajare": "2020-01-15"}
    _sal.importa(_Conn(), [rand])
    coloane = _insert_salariati(captured.get("sql")) or []
    assert coloane.count("iban") == 1, "INSERT-ul salariati NU include coloana iban: %r" % coloane
    params = tuple(captured.get("params") or ())
    assert len(params) == len(coloane) and params[coloane.index("iban")] == "RO49AAAA1B31007593840000", \
        "IBAN-ul nu ajunge in parametrul coloanei iban: %r" % (dict(zip(coloane, params)),)
