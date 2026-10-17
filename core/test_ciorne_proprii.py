# -*- coding: utf-8 -*-
"""GARD — deficiența 246: un asistent nu modifică, nu șterge și nu trimite la validare ciorna ALTUI utilizator (comanda Costin 14.10.2026,
verbatim în DECIZII „Lotul 3”; `core/migrare_ciorne_proprii.py`).

Regula se probează pe o schemă EFEMERĂ creată din `tenant_template.sql` (deci și oglinda din șablon), direct în SQL — fără drumul
aplicației: triggerul trebuie să țină pe orice drum, inclusiv unul viitor. Utilizatorul cererii e cel pe care îl scrie `db.get_conn`
(`SET iconta.utilizator`). Conturile sunt cele de test ale cabinetului Prisma (patron = administrator, asistent = `angajat`).
Tranzacție anulată la final; perioade în 2099. MUTAȚII: triggerul notei fără ramura DELETE -> ROȘU; `ciorna_altui` fără condiția de rol
-> administratorul refuzat -> ROȘU; ramura „decizia validatorului” scoasă -> validarea seniorului refuzată -> ROȘU."""
import io

import psycopg2
import pytest

from core import db as _db
from core import drepturi as _dr
from core import migrare_ciorne_proprii as mc
from core import repo_contabilitate as _rc
from core import tenant_provisioning as _tp

SCH = "efemer_ciorne_proprii"
D = "DREPT_CIORNA: "


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
    conn.commit()
    c.execute('SET search_path TO "%s", public' % SCH)
    try:
        yield c
    finally:
        conn.rollback()
        c = conn.cursor()
        c.execute("RESET iconta.utilizator")
        c.execute("RESET search_path")
        c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()
        p.putconn(conn)


def _id(cur, email):
    cur.execute("SELECT id, COALESCE(NULLIF(btrim(concat_ws(' ', prenume, nume)), ''), email) FROM public.users WHERE email = %s", (email,))
    return cur.fetchone()


def _ca(cur, uid):
    """Utilizatorul cererii (ca `db.get_conn` într-o cerere de modificare); None = în afara unei cereri."""
    if uid is None:
        cur.execute("RESET iconta.utilizator")
    else:
        cur.execute("SET iconta.utilizator TO %s", (str(uid),))


def _nota(cur, autor):
    _ca(cur, None)
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref, creat_de_id) VALUES ('2099-10-07', 'proba', "
                "'manual', 'ciorna', 'FCT 1', %s) RETURNING id", (autor,))
    n = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '371', '401', 100)", (n,))
    return n


def _refuz(cur, sql, args, asteptat):
    cur.execute("SAVEPOINT p")
    try:
        cur.execute(sql, args)
    except psycopg2.Error as e:
        cur.execute("ROLLBACK TO SAVEPOINT p")
        assert str(e).split("\n")[0] == asteptat
        return
    cur.execute("ROLLBACK TO SAVEPOINT p")
    raise AssertionError("a trecut, trebuia refuzat: %s %r" % (sql, args))


def test_oglinda_din_sablon_e_cea_generata_de_migrare():
    """O singură definiție: blocul din `tenant_template.sql` e exact `migrare_ciorne_proprii.sql('TENANT_PLACEHOLDER')`."""
    t = io.open("tenant_template.sql", encoding="utf-8").read()
    i, j = t.index(mc.MARCAJ_INCEPUT), t.index(mc.MARCAJ_SFARSIT) + len(mc.MARCAJ_SFARSIT)
    assert t[i:j] == mc.sql("TENANT_PLACEHOLDER")


def test_asistentul_nu_schimba_nu_sterge_ciorna_altuia_pe_niciun_drum(cur):
    """Editarea (antetul și rândurile) și ștergerea — cu textul refuzului IDENTIC cu cel arătat de ecran (`drepturi.MESAJ_CIORNA_ALTUI`)."""
    pat, nume_pat = _id(cur, "patron@prisma-cont.test")
    asi, _ = _id(cur, "asistent@prisma-cont.test")
    n = _nota(cur, pat)
    _ca(cur, asi)
    # [258] nota numită ca în Registrul jurnal, nu prin id-ul ei; [302] ciorna n-are număr: „din 07.10.2099”
    refuz = D + _dr.MESAJ_CIORNA_ALTUI % ("din 07.10.2099", nume_pat, nume_pat)
    _refuz(cur, "UPDATE inregistrari SET descriere = 'alta' WHERE id = %s", (n,), refuz)
    _refuz(cur, "DELETE FROM inregistrari WHERE id = %s", (n,), refuz)
    _refuz(cur, "UPDATE inregistrari_linii SET suma = 5 WHERE inregistrare_id = %s", (n,), refuz)
    _refuz(cur, "DELETE FROM inregistrari_linii WHERE inregistrare_id = %s", (n,), refuz)
    _refuz(cur, "INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4426', '401', 21)", (n,), refuz)
    assert _rc.ciorne_altui(cur, SCH, [n], asi) == [(n, nume_pat)]       # jurnalul o semnalează asistentului
    assert _rc.ciorne_altui(cur, SCH, [n], pat) == []                    # dar nu autorului


def test_trec_autorul_administratorul_si_scrierea_din_afara_unei_cereri(cur):
    pat, _ = _id(cur, "patron@prisma-cont.test")
    asi, _ = _id(cur, "asistent@prisma-cont.test")
    proprie = _nota(cur, asi)
    _ca(cur, asi)
    cur.execute("UPDATE inregistrari SET descriere = 'a mea' WHERE id = %s", (proprie,))
    cur.execute("DELETE FROM inregistrari WHERE id = %s", (proprie,))
    a_asistentului = _nota(cur, asi)
    _ca(cur, pat)                                                         # administratorul cabinetului: orice ciornă
    cur.execute("UPDATE inregistrari SET descriere = 'corectată' WHERE id = %s", (a_asistentului,))
    cur.execute("DELETE FROM inregistrari WHERE id = %s", (a_asistentului,))
    fara_cerere = _nota(cur, pat)
    _ca(cur, None)                                                        # import / cron: nimeni nu cere
    cur.execute("DELETE FROM inregistrari WHERE id = %s", (fara_cerere,))
    cur.execute("SELECT count(*) FROM inregistrari WHERE id IN (%s, %s, %s)", (proprie, a_asistentului, fara_cerere))
    assert cur.fetchone()[0] == 0


def test_asistentul_cu_poate_valida_valideaza_dar_nu_editeaza_ciorna_altuia(cur):
    """Decizia validatorului (schimbarea stării) trece; o modificare de conținut, nu."""
    pat, nume_pat = _id(cur, "patron@prisma-cont.test")
    asi, _ = _id(cur, "asistent@prisma-cont.test")
    cur.execute("UPDATE public.users SET poate_valida = true WHERE id = %s", (asi,))   # anulat la final (ROLLBACK)
    n = _nota(cur, pat)
    _ca(cur, asi)
    _refuz(cur, "UPDATE inregistrari SET descriere = 'alta' WHERE id = %s", (n,),
           D + _dr.MESAJ_CIORNA_ALTUI % ("din 07.10.2099", nume_pat, nume_pat))
    cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (n,))
    cur.execute("SELECT status FROM inregistrari WHERE id = %s", (n,))
    assert cur.fetchone()[0] == "validata"


def test_registrul_de_incasari_si_plati_aceeasi_regula(cur):
    pat, nume_pat = _id(cur, "patron@prisma-cont.test")
    asi, _ = _id(cur, "asistent@prisma-cont.test")
    _ca(cur, None)
    cur.execute("INSERT INTO rip_operatiuni (data_operatiune, tip, suma, explicatie, categorie, metoda, creat_de) VALUES "
                "('2099-10-07', 'plata', 10, 'proba', 'cheltuiala', 'numerar', %s) RETURNING id", (pat,))
    op = cur.fetchone()[0]
    _ca(cur, asi)
    _refuz(cur, "DELETE FROM rip_operatiuni WHERE id = %s", (op,),
           D + _dr.MESAJ_RIP_ALTUI % ("plata din 07.10.2099 de 10,00 RON", nume_pat, nume_pat))   # [258] cum o arată rândul, nu id-ul
    _ca(cur, pat)
    cur.execute("DELETE FROM rip_operatiuni WHERE id = %s", (op,))
