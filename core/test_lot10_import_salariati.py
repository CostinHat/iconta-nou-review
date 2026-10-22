# -*- coding: utf-8 -*-
"""[lotul 10] Importul salariaților și corectarea lor (comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”).

- **420**: „import salariați: rândurile fără normă de lucru și funcție de bază sunt respinse întregi, deci contabilul trebuie să refacă
  fișierul exportat din vechea aplicație. Câmpurile lipsă se completează pe ecran, înainte de import, cu propunere editabilă (normă
  întreagă, funcție de bază Da), la fel cum sunt tratate deja COR, scutirea și persoanele în întreținere (intră marcate «de verificat»).”
- **423 b**: „starea «gata» nu spune câți salariați rămân «de verificat»”.
- **SalariatEdit** (decizia sesiunii principale, observația deschisă din lotul 9): „Corectează datele” primește data nașterii, copiii
  școlarizați, declarația copiilor și funcția de bază — „Salariat nou” le are (C67); `SalariatEdit` le arunca tăcut.

TEMEI: CF art.77 alin.(1) (deducerea personală „pentru veniturile din salarii la locul unde se află funcția de bază”); CF art.77 alin.(10):
„a) 15% din salariul de bază minim brut pe țară garantat în plată pentru persoanele fizice cu vârsta de până la 26 de ani […]; b) 100 de
lei lunar pentru fiecare copil cu vârsta de până la 18 ani, dacă acesta este înscris într-o unitate de învățământ”; alin.(12): „[…] prin
prezentarea documentului care atestă înscrierea copilului într-o unitate de învățământ și a unei declarații pe propria răspundere din
partea părintelui beneficiar”. Norma (întreagă / parțială) intră în D112. Propunerea (întreagă, Da) e decizia comenzii, nu temei fiscal.
CNP-urile de probă au cifra de control verificată (algoritmul din CLAUDE.md). Schemă efemeră din template, tranzacție anulată."""
import os

import pytest

from core import db as _db, salariati_import_api as si

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot10_salariati"
CNP1 = "1900101410011"      # cifra de control verificată (test_412_cim_salariat)
CNP2 = "1960101078916"      # cifra de control verificată (test_import_saga.CNP_OK)
FARA_NORMA = ("nume;prenume;cnp;data angajare;brut;judet;persoane in intretinere;scutit contributie minima\n"
              "POPESCU;ANA;%s;2024-01-15;5000;B;0;nu\nIONESCU;RADU;%s;2024-02-01;6000;CJ;1;nu\n" % (CNP1, CNP2)).encode("utf-8")


def test_def_420_randul_fara_norma_si_functie_de_baza_intra_cu_propunerea_editabila():
    """ROȘU înainte: `verifica_randuri` respingea fiecare rând (`norma_lipsa`, `functie_baza_lipsa`) — „respinse întregi”. Acum: norma
    propusă întreagă (8 ore), funcția de bază propusă „Da”, amândouă marcate „de verificat”, rândul intră CU OBSERVAȚIE.
    MUTAȚIA: propunerea de normă scoasă din `extrage` -> `norma_lipsa` -> rândul respins -> pică."""
    r = si.extrage(FARA_NORMA, "s.csv")
    assert [(x["tip_norma"], x["ore_zi"], x["functie_baza"]) for x in r] == [("intreaga", 8, True), ("intreaga", 8, True)]
    assert all({"tip_norma", "functie_baza"} <= set(x["de_verificat"]) for x in r)        # comanda 10.1: „intră marcate «de verificat»”
    assert si.verifica_randuri(r) == []                                                   # nimic respins
    si.eticheteaza(r)
    assert {x["stare"] for x in r} == {"semnalat"}
    assert ("POPESCU ANA: norma de lucru lipsește din fișier — propusă normă întreagă (8 ore); schimb-o pe rând dacă nu e așa (intră "
            "marcată de verificat)") in r[0]["motive"]
    assert any(m.startswith("POPESCU ANA: funcția de bază lipsește din fișier — propusă „Da”") for m in r[0]["motive"])


def test_420_orele_din_fisier_sub_8_fara_norma_propun_partiala():
    """Orele pe zi din fișier (4) sunt date, nu se înlocuiesc cu 8: propunerea e normă parțială cu 4 ore, tot de verificat."""
    r = si.extrage(("nume;prenume;cnp;ore pe zi;brut;functie de baza\nPOP;ION;%s;4;3000;da\n" % CNP1).encode(), "s.csv")[0]
    assert (r["tip_norma"], r["ore_zi"], r["functie_baza"]) == ("partiala", 4, True)
    # marcajul exact: norma propusă (și câmpurile absente din fișier), dar nu funcția de bază, care e în fișier
    assert r["de_verificat"] == ["tip_norma", "persoane_intretinere", "scutit_contrib_minim"], r["de_verificat"]


def test_420_norma_zero_ore_pe_luna_ramane_refuzata():
    """SAGA „Norma pe zi” = 0 (contract cu ore pe lună) nu e o normă lipsă: rămâne refuzată numit (`norma_ore_luna`), nu propusă."""
    r = si.extrage(("nume;prenume;cnp;norma pe zi;brut\nPOP;ION;%s;0;3000\n" % CNP1).encode(), "s.csv")
    assert r[0]["tip_norma"] == "" and "tip_norma" not in r[0]["de_verificat"]
    assert [e["regula"] for e in si.verifica_randuri(r)] == ["norma_ore_luna"]


# ── scrierea ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def _fisa(c, cnp):
    with c.cursor() as cur:
        cur.execute("SELECT id, part_time, ore_zi, functie_baza, de_verificat FROM salariati WHERE cnp = %s", (cnp,))
        return cur.fetchone()


def test_def_420_salariatii_intra_marcati_si_confirmarea_ii_scoate_din_marcaj(conn):
    """Rândurile cu propunerea intră (nu „respinse întregi”), marcate; salvarea normei / funcției de bază din Stat de plată le confirmă.
    MUTAȚIA: `tip_norma` scos din `DE_VERIFICAT` -> marcajul nu se scrie -> pică."""
    from core import salariati_api as sa
    rez = si.importa(conn, si.extrage(FARA_NORMA, "s.csv"))
    assert (rez["importati"], rez["respinse"]) == (2, [])
    sid, part_time, ore, fb, dv = _fisa(conn, CNP1)
    assert (part_time, float(ore), fb) == (False, 8.0, True)
    assert set(dv) == {"tip_norma", "functie_baza"}
    sa.actualizeaza_salariat(conn, sid, tip_norma="partiala", ore_zi=6)
    assert _fisa(conn, CNP1)[1:] == (True, 6, True, ["functie_baza"])
    sa.actualizeaza_salariat(conn, sid, functie_baza=False)
    assert _fisa(conn, CNP1)[3:] == (False, [])


def test_420_reimportul_cu_propunere_nu_strica_fisa_confirmata(conn):
    """Un reimport (același CNP) în care norma / funcția de bază sunt doar PROPUSE nu suprascrie ce a confirmat contabilul.
    [lotul 11, 420 — PIVOT, retestul Costin 21.10.2026: „norma și funcția de bază lipsă din fișier se pun tăcut. Trebuie […] marcate «de
    verificat»”] valorile rămân, dar câmpurile lipsă din fișier se MARCHEAZĂ din nou: fișa nu deosebește o valoare confirmată de una pusă
    tăcut de un import mai vechi (F6, 19.10.2026). Proba cazului F6: `core/test_lot11_m_salariati.py`."""
    from core import salariati_api as sa
    si.importa(conn, si.extrage(FARA_NORMA, "s.csv"))
    sid = _fisa(conn, CNP1)[0]
    sa.actualizeaza_salariat(conn, sid, tip_norma="partiala", ore_zi=4, functie_baza=False)
    # [426, clasa] reimportul pe CNP-uri existente actualizează fișele numai confirmat (`inlocuieste=True`)
    si.importa(conn, si.extrage(FARA_NORMA, "s.csv"), inlocuieste=True)
    assert _fisa(conn, CNP1)[1:] == (True, 4, False, ["tip_norma", "functie_baza"])


def test_def_423b_rezumatul_numara_salariatii_de_verificat(conn):
    """„starea «gata» nu spune câți salariați rămân «de verificat»” — rezumatul (sursa ecranului Migrare → Salariați) îi numără.
    MUTAȚIA: `de_verificat` scos din `rezumat` -> KeyError / 0 -> pică."""
    from core import salariati_api as sa, firma_rezumat
    si.importa(conn, si.extrage(FARA_NORMA, "s.csv"))
    assert si.rezumat(conn) == {"are_salariati": True, "randuri": 2, "de_verificat": 2}
    sid = _fisa(conn, CNP2)[0]
    sa.actualizeaza_salariat(conn, sid, tip_norma="intreaga", functie_baza=True)
    assert firma_rezumat._salariati(conn, SCHEMA) == {"are_salariati": True, "randuri": 2, "de_verificat": 1}


def test_def_salariat_edit_corecteaza_datele_deducerilor(conn):
    """„Corectează datele” trimite data nașterii, copiii școlarizați, declarația copiilor și funcția de bază; modelul rutei le PĂSTREAZĂ
    (înainte pydantic le arunca tăcut — clasa R51), iar fișa le salvează și le arată. MUTAȚIA: `data_nastere` scos din `SalariatEdit`
    -> câmpul pierdut -> pică."""
    import main
    from core import salariati_api as sa
    si.importa(conn, si.extrage(FARA_NORMA, "s.csv"))
    sid = _fisa(conn, CNP1)[0]
    corp = main.SalariatEdit(data_nastere="2002-05-10", copii_scolarizati=2, declaratie_copii=True, functie_baza=False)
    trimise = corp.model_dump(exclude_unset=True)
    assert trimise == {"data_nastere": "2002-05-10", "copii_scolarizati": 2, "declaratie_copii": True, "functie_baza": False}
    sa.actualizeaza_salariat(conn, sid, **trimise)
    d = sa.detalii_salariat(conn, sid)
    # CF art.77 alin.(10) lit.a (vârsta până la 26 de ani — data nașterii), lit.b + alin.(12) (copiii, declarația părintelui), alin.(1)
    assert (str(d["data_nastere"]), d["copii_scolarizati"], d["declaratie_copii"], d["functie_baza"]) == ("2002-05-10", 2, True, False)
