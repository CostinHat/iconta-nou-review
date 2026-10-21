# -*- coding: utf-8 -*-
"""[deficiența 412, decizia Costin 19.10.2026, verbatim în DECIZII „Închiderea lotului 9”] „Adeverință: Funcția, Tipul contractului,
Nr./Data CIM se precompletează din fișă.” — „Da, în fișa salariatului”: tipul contractului și Nr. / Data CIM sunt coloane ale
salariatului (`core/migrare_cim_salariat.py` + oglinda din tenant_template.sql), se salvează și se citesc pe toate drumurile, iar
adeverința le ia de acolo, modificabile. (Funcția din COR: `core/test_411_net_cu_cm.py::test_412_functia_din_cor_pe_adeverinta`.)

Temei (anaf_surse/legea_53_2003_codul_muncii.txt, Portal Legislativ):
- Legea 53/2003 art.12 alin.(1)–(2): „Contractul individual de muncă se încheie pe durată nedeterminată. (2) Prin excepție, contractul
  individual de muncă se poate încheia și pe durată determinată, în condițiile expres prevăzute de lege.” — cele două valori;
- Legea 53/2003 art.16 alin.(1): „Contractul individual de muncă se încheie în baza consimțământului părților, în formă scrisă [...]”
  — actul scris are număr și dată;
- Legea 53/2003 art.34 alin.(5): angajatorul eliberează documentul care atestă „activitatea desfășurată [...], durata activității”.
Schemă efemeră din template, în tranzacție anulată (nimic nu rămâne în bază)."""
import io as _io

import psycopg2
import pytest

from core import db as _db, tenant_provisioning as _tp

SCHEMA = "ztest_412_cim"
CNP = "1900101410011"   # cifra de control verificată (algoritmul din CLAUDE.md)
COR = "241107"          # auditor financiar — în public.cor_ocupatii (ca în test_411_net_cu_cm)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,declarant_nume,declarant_prenume,declarant_functie,patron_nume) "
                            "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Pop','Ion','administrator','Pop Ion')")
            yield c
        finally:
            c.rollback()


def _salariat_nou(c, **cim):
    import main
    from core import salariati_api as sa
    corp = main.SalariatIn(nume="IONESCU", prenume="VASILE", cnp=CNP, data_angajare="2024-01-01", tip_norma="intreaga",
                           ore_zi=8, salariu_brut=4050, judet_casa="B", cor=COR, functie_baza=True, scutit_contrib_minim=False,
                           **cim)
    return sa.creeaza_salariat(c, **corp.model_dump())["salariat_id"]


def _text_pdf(pdf):
    from pypdf import PdfReader
    return " ".join(" ".join(p.extract_text().split()) for p in PdfReader(_io.BytesIO(pdf)).pages)


def test_migrarea_adauga_coloanele_pe_o_firma_veche_idempotent(conn):
    """O firmă creată înainte de 412 (fără coloane) le primește; a doua rulare nu schimbă nimic; durata e numai din art.12.
    MUTAȚIA: rândul `nr_cim` scos din `_DDL` -> `verifica` rămâne False -> ROȘU."""
    from core import migrare_cim_salariat as m
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE salariati DROP COLUMN tip_contract, DROP COLUMN nr_cim, DROP COLUMN data_cim")
    assert m.verifica(conn, SCHEMA) is False
    m.aplica(conn, SCHEMA)
    assert m.verifica(conn, SCHEMA) is True
    m.aplica(conn, SCHEMA)                                   # idempotent: ADD COLUMN IF NOT EXISTS
    assert m.verifica(conn, SCHEMA) is True
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg2.errors.CheckViolation):  # Legea 53/2003 art.12: numai nedeterminată / determinată
            cur.execute("INSERT INTO salariati (nume, tip_contract) VALUES ('X', 'sezonier')")
        cur.execute("ROLLBACK TO SAVEPOINT s")


def test_creare_si_citire_poarta_cim_si_campurile_trimise_de_ecran(conn):
    """Ecranul „Salariat nou” trimite CIM-ul; modelul rutei (`main.SalariatIn`) și `creeaza_salariat` îl duc în bază, iar fișa
    (`detalii_salariat`) îl întoarce. În același drum: data nașterii, copiii școlarizați și declarația (deducerile CF art.77), pe care
    `SalariatIn` le pierdea tăcut. MUTAȚIA: `tip_contract`, `nr_cim`, `data_cim` scoase din `_CAMPURI_API` -> ROȘU."""
    from core import salariati_api as sa
    sid = _salariat_nou(conn, tip_contract="determinata", nr_cim="12/2023", data_cim="2023-12-20",
                        data_nastere="2003-05-01", copii_scolarizati=2, declaratie_copii=True)
    d = sa.detalii_salariat(conn, sid)
    assert (d["tip_contract"], d["nr_cim"], str(d["data_cim"])) == ("determinata", "12/2023", "2023-12-20"), d
    with conn.cursor() as cur:
        cur.execute("SELECT data_nastere::text, copii_scolarizati, declaratie_copii FROM salariati WHERE id = %s", (sid,))
        assert cur.fetchone() == ("2003-05-01", 2, True)


def test_editarea_schimba_si_goleste_cim(conn):
    """„Corectează datele” trimite CIM-ul citit din fișă; `null` trimis explicit golește (R51, `_golite`). MUTAȚIA: `nr_cim` scos din
    `main.SalariatEdit` -> pydantic îl ignoră, numărul rămâne cel vechi -> ROȘU."""
    import main
    from core import salariati_api as sa
    sid = _salariat_nou(conn, tip_contract="determinata", nr_cim="12/2023", data_cim="2023-12-20")
    corp = main.SalariatEdit(tip_contract="nedeterminata", nr_cim="7", data_cim=None)
    trimise = corp.model_dump(exclude_unset=True)
    sa.actualizeaza_salariat(conn, sid, _golite=[k for k, v in trimise.items() if v is None], **corp.model_dump())
    d = sa.detalii_salariat(conn, sid)
    assert (d["tip_contract"], d["nr_cim"], d["data_cim"]) == ("nedeterminata", "7", None), d


def test_validarea_refuza_durata_din_afara_art12_si_data_inexistenta():
    from core import salariati_api as sa
    er = dict(e for e in sa.valideaza_salariat({"nume": "X", "tip_contract": "sezonier", "data_cim": "2023-13-45"}) if isinstance(e, tuple))
    assert set(er) >= {"tip_contract", "data_cim"}, er
    assert sa.valideaza_salariat({"nume": "X", "tip_contract": "determinata", "data_cim": "2023-12-20"}) == []


def test_reimportul_salariatilor_nu_sterge_cim_de_pe_fisa(conn):
    """Importul (UPSERT pe CNP) nu are coloanele CIM în fișier: actualizarea fișei existente le lasă cum le-a scris contabilul."""
    import main
    from core import salariati_api as sa, salariati_import_api as imp
    sid = _salariat_nou(conn, tip_contract="determinata", nr_cim="12/2023", data_cim="2023-12-20")
    rand = main.SalariatRand(nume="IONESCU", prenume="VASILE", cnp=CNP, data_angajare="2024-01-01", tip_norma="intreaga",
                             functie_baza=True, scutit_contrib_minim=False, ore_zi=8, salariu_brut=4050, judet_casa="B",
                             cor=COR, rand_fisier=2).model_dump()
    # [lotul 10, 426] actualizarea salariaților existenți din fișier se face numai confirmat („Confirmă înlocuirea”)
    imp.importa(conn, [rand], inlocuieste=True)
    d = sa.detalii_salariat(conn, sid)
    assert (d["tip_contract"], d["nr_cim"], str(d["data_cim"])) == ("determinata", "12/2023", "2023-12-20"), d


def test_adeverinta_ia_cim_din_fisa_si_lasa_formularul_sa_schimbe(conn):
    """PDF-ul: fără nimic scris în formular -> durata și Nr./Data CIM de pe fișă; ce scrie omul în formular are întâietate.
    MUTAȚIA: bucla „necompletat = din fișă” scoasă din `adeverinta.pdf` -> PDF-ul iese fără „nr. 12/2023 din 20.12.2023” -> ROȘU."""
    from core import adeverinta as ad
    sid = _salariat_nou(conn, tip_contract="determinata", nr_cim="12/2023", data_cim="2023-12-20")
    text = _text_pdf(ad.pdf(conn, SCHEMA, sid, {"scop": "grădiniță", "tip_contract": "", "nr_cim": "", "an": 2026, "luna": 10}))
    assert text.count("în baza contractului individual de muncă nr. 12/2023 din 20.12.2023, încheiat pe durată determinată") == 1, text
    text = _text_pdf(ad.pdf(conn, SCHEMA, sid, {"scop": "grădiniță", "tip_contract": "nedeterminata", "nr_cim": "99",
                                                "an": 2026, "luna": 10}))
    assert text.count("nr. 99 din 20.12.2023, încheiat pe durată nedeterminată") == 1, text
