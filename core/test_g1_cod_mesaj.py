# -*- coding: utf-8 -*-
"""core/test_g1_cod_mesaj.py — G1: codul-mașină de business nu mai ajunge brut la utilizator.

Un HTTPException cu `detail=r.get("cod")` afișa un cod (ex. "MOTIV_LIPSA") ca mesaj — neinteligibil.
Fix: `mesaj_din_cod` traduce codul într-o propoziție cap.6. Gardul: niciun cod brut ca detail; maparea
întoarce propoziții umane.
"""
import io


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_g1_niciun_cod_brut_ca_detail():
    src = _read("main.py")
    assert 'detail=r.get("cod")' not in src, "G1: cod brut ca detail (netradus) inca prezent"
    assert 'r.get("cod", "eroare")' not in src, "G1: cod brut ca detail (fallback 'eroare') inca prezent"


def test_g1_mesaj_din_cod_e_uman():
    from core.mesaje import mesaj_din_cod, MESAJ_COD
    # coduri cunoscute -> propozitie (macar un spatiu), diferita de codul brut
    for c in ("MOTIV_LIPSA", "EMAIL_EXISTA", "CURS_INDISPONIBIL", "REGIM_INVALID", "DESCRIERE_GOALA"):
        m = mesaj_din_cod(c)
        assert " " in m and m != c, c
    # cod necunoscut / None -> fallback generic (nu codul, nu gol, nu None)
    assert mesaj_din_cod("COD_INEXISTENT_XYZ") == mesaj_din_cod(None)
    assert isinstance(mesaj_din_cod(None), str) and " " in mesaj_din_cod(None)


def test_g2_g4_literale_consolidate():
    """G2/G4: literalele repetate (fara-cabinet ×5, email, CUI ×3, perioada-hard) au fost inlocuite cu
    constante canonice explicite (cap.6, cu remediu)."""
    src = _read("main.py")
    for lit in ('"fara cabinet asociat"', '"email deja folosit"', '"exista deja un cont cu acest email"',
                '"CUI firma lipsa in Profil firma"', '"CUI firma lipsa in firma_profil"',
                '"perioada este blocată (luna închisă)"'):
        assert lit not in src, "G2/G4: literal necanonic inca prezent: %s" % lit
    from core import mesaje
    assert "Contactează" in mesaje.FARA_CABINET and "administratorul" in mesaje.PERIOADA_INCHISA
    assert mesaje.CUI_FIRMA_LIPSA.startswith("CUI") and "Completează" in mesaje.CUI_FIRMA_LIPSA
