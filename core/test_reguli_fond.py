# -*- coding: utf-8 -*-
"""GARD — regulile de fond în BAZĂ (comanda Costin 09.10.2026, pct.11, verbatim în DECIZII; `core/migrare_reguli_fond.py`).

Fiecare regulă se probează pe o schemă EFEMERĂ creată din `tenant_template.sql` (deci și oglinda din șablon e probată), direct în SQL
— fără niciun drum al aplicației: regula trebuie să țină oricare ar fi drumul, inclusiv unul viitor. Contraproba (ce e voie) e lângă
fiecare refuz. Tranzacție anulată la final; perioade în 2099.
"""
import io

import psycopg2
import pytest

from core import db as _db
from core import migrare_reguli_fond as rf
from core import tenant_provisioning as _tp

R = "REGULA_CONTABILA: "

SCH = "efemer_reguli_fond"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def cur():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    c = conn.cursor()
    c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    c.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    conn.commit()                                   # R1 judecă nota validată ÎNTR-O TRANZACȚIE ÎNCHEIATĂ: datele se comit de-adevăratelea
    c.execute('SET search_path TO "%s", public' % SCH)
    try:
        yield c
    finally:
        conn.rollback()
        c = conn.cursor()
        c.execute("RESET search_path")
        c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()
        p.putconn(conn)


def _refuz(cur, sql, args=(), incepe="REGULA_CONTABILA: "):
    """Comanda e refuzată de bază, iar mesajul ÎNCEPE exact cu textul regulii (cu numărul notei): un refuz din altă cauză pică."""
    cur.execute("SAVEPOINT p")
    try:
        cur.execute(sql, args)
    except psycopg2.Error as e:
        cur.execute("ROLLBACK TO SAVEPOINT p")
        msg = str(e).split("\n")[0]
        assert msg.startswith(incepe), (msg, incepe)
        return msg
    cur.execute("ROLLBACK TO SAVEPOINT p")
    raise AssertionError("a trecut, trebuia refuzat: %s" % sql)


def _merge(cur, sql, args=()):
    cur.execute(sql, args)
    return cur.fetchone()[0] if cur.description else None


def _nota(cur, status="ciorna", doc="FCT 1", data="2099-10-07"):
    """Nota, construită și COMISĂ — pentru regulă e „validată într-o tranzacție încheiată” (R1 nu scutește decât construirea în
    tranzacția curentă)."""
    n = _merge(cur, "INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'proba', 'manual', 'ciorna', %s) "
                    "RETURNING id", (data, doc))
    _merge(cur, "INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '371', '401', 100)", (n,))
    if status == "validata":
        _merge(cur, "UPDATE inregistrari SET status = 'validata' WHERE id = %s", (n,))
    cur.connection.commit()
    cur.execute('SET search_path TO "%s", public' % SCH)
    return n


def test_r1_nota_validata_nu_se_modifica_nu_se_sterge_nici_randurile(cur):
    """MUTAȚIE: ramura UPDATE scoasă din `regula_nota` -> descrierea se schimbă -> pică."""
    v = _nota(cur, "validata")
    for col, val in (("descriere", "alta"), ("data", "2099-10-08"), ("document_ref", "FCT 2"), ("factura_id", 1), ("status", "ciorna"),
                     ("numar", "X"), ("sursa", "alta")):
        _refuz(cur, "UPDATE inregistrari SET %s = %%s WHERE id = %%s" % col, (val, v), R + "Nota #%d e validată, deci nu se mai modifică" % v)
    _refuz(cur, "DELETE FROM inregistrari WHERE id = %s", (v,), R + "Nota #%d e validată, deci nu se mai șterge" % v)
    rand = R + "Nota #%d e validată, deci rândurile ei nu se mai schimbă" % v
    _refuz(cur, "UPDATE inregistrari_linii SET suma = 1 WHERE inregistrare_id = %s", (v,), rand)
    _refuz(cur, "DELETE FROM inregistrari_linii WHERE inregistrare_id = %s", (v,), rand)
    _refuz(cur, "INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4426', '401', 21)", (v,), rand)
    # contraproba: ciorna se editează și se șterge
    c = _nota(cur)
    _merge(cur, "UPDATE inregistrari SET descriere = 'alta' WHERE id = %s", (c,))
    _merge(cur, "UPDATE inregistrari_linii SET suma = 5 WHERE inregistrare_id = %s", (c,))
    _merge(cur, "DELETE FROM inregistrari WHERE id = %s", (c,))
    # stornarea = notă NOUĂ, cu sumele în roșu: voie
    _nota(cur, "validata")


def test_r1_construirea_in_tranzactia_curenta_nu_e_modificare(cur):
    """INTERPRETARE (DECIZII 09.10): nota validată și rândurile ei se construiesc în tranzacția care o creează; după ce tranzacția
    (aici: sub-tranzacția) s-a încheiat, nu se mai ating. MUTAȚIE: `nota_din_tranzactia_curenta` întoarce mereu true -> R1 nu mai
    păzește nimic -> pică testul R1; întoarce mereu false -> construirea se refuză -> pică acesta."""
    n = _merge(cur, "INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES ('2099-10-07', 'import', 'manual', "
                    "'validata', 'NC 7') RETURNING id")
    _merge(cur, "INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '371', '401', 5)", (n,))
    _merge(cur, "UPDATE inregistrari SET descriere = 'import istoric' WHERE id = %s", (n,))


def test_r3_drum_nou_insertia_directa_a_unei_note_validate():
    """R3 stă la ACTUL de validare (ciornă -> validată). Inserarea directă a unei note deja validate l-ar ocoli — azi nu există în
    aplicație; dacă apare (în afara testelor și a migrărilor), gardul pică și drumul se acoperă întâi (comanda Costin pct.12: „garda
    … pică dacă apare un drum nou neacoperit”). MUTAȚIE: un `INSERT INTO inregistrari … 'validata'` pus într-un modul -> pică."""
    import glob
    import re
    rele = []
    for f in sorted(glob.glob("core/*.py")) + ["main.py"]:
        if f.startswith(("core/test_", "core/migrare_")):
            continue
        t = io.open(f, encoding="utf-8").read()
        for m in re.finditer(r"INSERT\s+INTO\s+[^\s(]*inregistrari\s*\(([^)]*)\)\s*VALUES\s*\(([^)]*)\)", t, re.I | re.S):
            if re.search(r"\bstatus\b", m.group(1)) and re.search(r"'validata'", m.group(2)):
                rele.append("%s:%d" % (f, t.count("\n", 0, m.start()) + 1))
    assert rele == [], "note inserate direct ca validate (ocolesc actul de validare și R3): %s" % rele

def test_r2_luna_blocata_nu_primeste_si_nu_pierde_note_nici_randuri(cur):
    """Golurile închise: mutarea unei note AFARĂ din luna blocată; rândurile unei note din luna blocată.
    MUTAȚIE: data veche scoasă din `verifica_perioada_blocata` -> nota iese din luna blocată -> pică."""
    n = _nota(cur, data="2099-09-15")
    _merge(cur, "INSERT INTO perioade_blocate (an, luna) VALUES (2099, 9)")
    _refuz(cur, "UPDATE inregistrari SET data = '2099-10-15' WHERE id = %s", (n,), "PERIOADA_BLOCATA: luna 09/2099 este inchisa")       # afară din luna blocată
    _refuz(cur, "INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '607', '371', 1)", (n,),
           "PERIOADA_BLOCATA: luna 09/2099 este inchisa")
    _refuz(cur, "DELETE FROM inregistrari_linii WHERE inregistrare_id = %s", (n,), "PERIOADA_BLOCATA: luna 09/2099 este inchisa")
    o = _nota(cur, data="2099-10-15")
    _refuz(cur, "UPDATE inregistrari SET data = '2099-09-30' WHERE id = %s", (o,), "PERIOADA_BLOCATA: luna 09/2099 este inchisa")       # înăuntru
    _merge(cur, "UPDATE inregistrari SET data = '2099-10-20' WHERE id = %s", (o,))                           # contraproba


def test_r3_nota_nu_se_valideaza_fara_documentul_sursa(cur):
    """MUTAȚIE: verificarea documentului scoasă -> nota fără document se validează -> pică."""
    for doc in (None, "", "  "):
        n = _nota(cur, doc=doc)
        _refuz(cur, "UPDATE inregistrari SET status = 'validata' WHERE id = %s", (n,), R + "Nota #%d n-are documentul justificativ" % n)
    _nota(cur, "validata", doc="NIR nr 1")                                                                  # contraproba


def test_r3_documentul_e_cel_al_aplicatiei_paritate_cu_document_justificativ(cur):
    """O singură definiție a documentului justificativ: triggerul acceptă validarea EXACT când `jurnal_api.document_justificativ`
    găsește documentul (scris pe notă, sau factura legată). Prins de proba blocului E (09.10.2026): nota de contare a unei facturi
    are `document_ref` gol — documentul ei e factura. MUTAȚIE: ramura facturii scoasă din `regula_nota` -> pică."""
    from core import jurnal_api as j
    f = _merge(cur, "INSERT INTO facturi (numar, data_emitere, directie, total, tva, total_lei, tva_lei, tert_nume, tert_cui) "
                    "VALUES ('FE1', '2099-10-07', 'emisa', 121, 21, 121, 21, 'Client', '14399840') RETURNING id")
    cazuri = [("NIR nr 1", None), (None, f), ("", f), (None, None), ("  ", None)]
    for doc, fid in cazuri:
        n = _nota(cur, doc=doc)
        if fid:
            _merge(cur, "UPDATE inregistrari SET factura_id = %s WHERE id = %s", (fid, n))
        cur.execute("SELECT f.tip, f.serie, f.numar, f.data_emitere FROM facturi f WHERE f.id = %s", (fid,))
        fr = cur.fetchone() or (None, None, None, None)
        are = j.document_justificativ(doc, *fr) is not None
        cur.execute("SAVEPOINT v")
        try:
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (n,))
            trece = True
        except psycopg2.Error:
            trece = False
        cur.execute("ROLLBACK TO SAVEPOINT v")
        assert trece == are, (doc, fid, trece, are)


def test_r4_randul_are_ambele_conturi(cur):
    """Debit = credit e garantat de model (rândul e o pereche); ce o mai poate strica e un cont gol.
    MUTAȚIE: verificarea contului gol scoasă -> pică."""
    n = _nota(cur)
    for d, c in (("", "401"), ("371", " ")):
        _refuz(cur, "INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, 1)", (n, d, c),
               R + "Un rând de notă are nevoie de ambele conturi")


def _nir_contat(cur, status_nota):
    a = _merge(cur, "INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES ('Marfa R5', 'buc', '371', '607') RETURNING id")
    n = _nota(cur, status_nota, doc="NIR nr 9")
    nir = _merge(cur, "INSERT INTO nir (numar, data, inregistrari_ids) VALUES ('9', '2099-10-07', %s::jsonb) RETURNING id", ("[%d]" % n,))
    m = _merge(cur, "INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, nir_id) "
                    "VALUES (%s, '2099-10-07', 'intrare', 10, 55, 550, 'NIR nr 9', %s) RETURNING id", (a, nir))
    return a, m


def _storno(cur, a, m, nota=None):
    return ("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, nir_id, anuleaza_id, "
            "inregistrare_id) SELECT articol_id, '2099-10-09', tip, -cantitate, pret_unitar, -valoare, 'Stornare', nir_id, id, %s "
            "FROM miscari_stoc WHERE id = %s", (nota, m))


def test_r5_miscarea_documentului_contat_se_desface_numai_cu_document_de_corectie(cur):
    """Exact ce a stricat tenant_049: stornarea intrării unui NIR contat, fără notă de corecție. MUTAȚIE: `regula_stoc` fără ramura
    INSERT -> stornarea fără document trece -> pică."""
    a, m = _nir_contat(cur, "validata")
    corectie_ceruta = R + "Mișcarea de stoc #%d e a unui document contat: se stornează numai cu un document de corecție" % m
    _refuz(cur, *_storno(cur, a, m), corectie_ceruta)
    v = _nota(cur, "validata", doc="NC 1")
    _refuz(cur, *_storno(cur, a, m, v), corectie_ceruta)                                      # nota de corecție trebuie să fie nouă, ciornă
    contata = R + "Mișcarea de stoc „NIR nr 9” e a unui document contat: nu se modifică și nu se șterge"
    _refuz(cur, "UPDATE miscari_stoc SET valoare = 1 WHERE id = %s", (m,), contata)
    _refuz(cur, "DELETE FROM miscari_stoc WHERE id = %s", (m,), contata)
    corectie = _nota(cur, doc="Notă de corecție NIR nr 9")
    cur.execute(*_storno(cur, a, m, corectie))                                               # cu document de corecție: voie
    # contraproba: NIR-ul cu nota încă în ciornă (respins la validare) se stornează fără document nou (decizia 07.10 R1)
    a2, m2 = _nir_contat(cur, "ciorna")
    cur.execute(*_storno(cur, a2, m2))


def test_oglinda_din_sablon_e_cea_generata_de_migrare():
    """O singură definiție: blocul din `tenant_template.sql` e exact `migrare_reguli_fond.sql('TENANT_PLACEHOLDER')`.
    MUTAȚIE: o regulă schimbată numai în migrare -> pică."""
    t = io.open("tenant_template.sql", encoding="utf-8").read()
    i, j = t.index(rf.MARCAJ_INCEPUT), t.index(rf.MARCAJ_SFARSIT) + len(rf.MARCAJ_SFARSIT)
    assert t[i:j] == rf.sql("TENANT_PLACEHOLDER")
    assert t.count("FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata()") == 2   # definiția din bloc + EXECUTE-ul triggerului
