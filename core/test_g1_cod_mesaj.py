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


def test_g3_garduri_rol_explicite():
    """G3: gardurile de rol/acces (403) telegrafice -> mesaje explicite cu dreptul lipsă + cine îl acordă."""
    src = _read("main.py")
    for lit in ('"rol insuficient pentru această acțiune"', '"Doar Admin iConta."',
                '"nu ai acces la acest tenant"', '"Doar patronul."', '"Nu ai acces."',
                'detail="nu ai permisiunea de a valida declarații"'):
        assert lit not in src, "G3: gard rol telegrafic inca prezent: %s" % lit
    from core import mesaje
    for c in (mesaje.ROL_INSUFICIENT, mesaje.FARA_ACCES_TENANT, mesaje.FARA_DREPT_VALIDARE, mesaje.FARA_DREPT_DEPUNERE):
        assert "cabinetului" in c, c


def test_g5_input_guards_cu_constrangere():
    """G5: input-guards telegrafice din core/ (`suma invalida`/`valori invalide`/etc.) au acum
    constrângerea în mesaj (surfaced la user prin str(e) passthrough)."""
    import glob
    bare = []
    for f in glob.glob("core/*.py"):
        if f.split("/")[-1].startswith("test_"):
            continue
        s = _read(f)
        for lit in ('raise ValueError("suma invalida")', 'raise ValueError("valori invalide")',
                    'raise ValueError("valoare invalida")', 'raise ValueError("brut invalid")',
                    'raise ValueError("sume invalide")', 'raise ValueError("preturi invalide")'):
            if lit in s:
                bare.append("%s: %s" % (f.split("/")[-1], lit))
    assert not bare, "G5: input-guard telegrafic ramas: %s" % bare


def test_g12b_niciun_cod_brut_in_httpexception():
    """G12b (regulă durabilă, baseline=0 pe starea reparată după G1): niciun HTTPException din main.py
    nu surfacează un cod de business brut. ORICE `.get("cod")` dintr-un HTTPException trebuie să treacă
    prin `mesaj_din_cod`. Prinde reapariția clasei la commit (nu doar cele 2 tipare din G1)."""
    import re
    src = _read("main.py")
    rele = []
    # doar cod-ul folosit DIRECT ca detail (nu in conditionalul de status, nu deja tradus prin mesaje.get)
    for m in re.finditer(r'detail=\w+\.get\("cod"\)|HTTPException\(\d+,\s*\w+\.get\("cod"\)', src):
        frag = m.group(0)
        if "mesaj_din_cod" not in frag:
            rele.append(frag[:64])
    assert not rele, "G12b: cod brut in HTTPException (fara mesaj_din_cod): %s" % rele
