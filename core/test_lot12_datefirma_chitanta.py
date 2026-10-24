# -*- coding: utf-8 -*-
"""Lotul 12, pachetul datefirma — 168: „Descrierea notei chitanței doar numele clientului” (comanda Costin 12.1); retest 08.10 pct.19
(verbatim în DECIZII): „Nota chitanței (F1, nr. crt. 17): descrierea e doar numele clientului; trebuie să conțină chitanța și factura
stinsă.”

Drumul găsit în lotul 12: încasarea facturii din Casă (456, lotul 11) emite singură chitanța (`uc_tenants.chitante_pe_incasare`), dar nota se
scrie ÎNAINTE de chitanță (`casa_api.adauga`), deci descrierea ei era „Încasare de la client — factura F1A nr. 4 din … — Client”, fără
chitanță. Reparația: `casa_api.nota_numeste_chitanta` (aceeași formulă ca la scriere, `descriere_nota`), chemată după emiterea chitanței și de
migrarea datelor existente (`core/migrare_descriere_nota_chitanta.py`, numai ciorne — nota validată nu se modifică, OMFP 1802/2014 pct.69;
decizia Costin 09.10.2026 „Nota 118 rămâne neschimbată”).

Temei: OMFP 2634/2015 anexa 2, Chitanța (cod 14-4-1) — „documente justificative de înregistrare în registrul de casă [...] și în
contabilitate a încasărilor și plăților efectuate în numerar” (de aceea nota o numește); Registrul-jurnal col.3 „Felul, numărul și data
documentului justificativ” (OMFP 2634/2015 anexa 1 pct.45). Schemă efemeră din `tenant_template.sql`, în ROLLBACK; date sintetice (2099).
"""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot12_chitanta"
CLIENT = "CLIENT PROBA SRL"


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
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                c.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                c.execute("SET LOCAL search_path TO %s, public" % SCH)
                c.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'CASA PROBA SRL', '14399840') ON CONFLICT (id) DO NOTHING")
                yield c
        finally:
            conn.rollback()


def _factura(c, nr=4):
    c.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, tip, tert_nume, tert_cui, total, status) "
              "VALUES (%s, 'F1A', '2099-10-06', 'emisa', 'factura', %s, '14399840', 121.00, 'emisa') RETURNING id", ("F1A%d" % nr, CLIENT))
    return c.fetchone()[0]


def _incasare(c, fid, descriere, status="ciorna", data="2099-10-08", document=None, categorie="incasare_client"):
    """Nota și operațiunea de casă, cum le scrie `casa_api.adauga` pentru încasarea facturii `fid` (fără document scris de contabil)."""
    c.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref, factura_id) VALUES (%s, %s, 'casa', 'ciorna', %s, %s) "
              "RETURNING id", (data, descriere, document, fid))
    nid = c.fetchone()[0]
    c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5311', '4111', 121.00)", (nid,))
    c.execute("INSERT INTO casa_operatiuni (data, tip, categorie, document, partener, cui, suma, inregistrare_id) "
              "VALUES (%s, 'incasare', %s, %s, %s, '14399840', 121.00, %s) RETURNING id", (data, categorie, document, CLIENT, nid))
    op = c.fetchone()[0]
    if status != "ciorna":   # nota validată are documentul (regula de fond R3: nicio notă validată fără document justificativ)
        c.execute("UPDATE inregistrari SET status = %s, document_ref = COALESCE(document_ref, 'PRB-V') WHERE id = %s", (status, nid))
    return op, nid


def _descriere(c, nid):
    c.execute("SELECT descriere FROM inregistrari WHERE id = %s", (nid,))
    return c.fetchone()[0]


ASTEPTAT = "Încasare de la client — chitanța PRB-1 — factura F1A nr. 4 din 06.10.2099 — " + CLIENT


def test_def_168_incasarea_facturii_din_casa_numeste_chitanta_in_nota(cur):
    """Pașii, pe drumul rutei „Casă -> + Dispoziție nouă -> încasare de la client, factura bifată, fără document -> Adaugă”
    (`uc_tenants.casa_adauga`: `casa_api.adauga`, apoi `chitante_pe_incasare`): chitanța PRB-1 se emite, documentul notei devine PRB-1, iar
    descrierea notei numește chitanța și factura stinsă. MUTAȚIE: chemarea lui `casa_api.nota_numeste_chitanta` scoasă din
    `chitante_pe_incasare` -> descrierea rămâne „Încasare de la client — factura … — Client” -> pică."""
    from core import uc_tenants
    fid = _factura(cur)
    op, nid = _incasare(cur, fid, "Încasare de la client — factura F1A nr. 4 din 06.10.2099 — " + CLIENT)
    ch = uc_tenants.chitante_pe_incasare(cur, SCH, "PRB", {"operatiuni": [{"id": op, "factura_id": fid, "inregistrare_id": nid,
                                                                           "suma": "121.00"}]})
    assert [(x["serie"], x["numar"]) for x in ch] == [("PRB", 1)]
    cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (nid,))
    assert cur.fetchone()[0] == "PRB-1"
    assert _descriere(cur, nid) == ASTEPTAT     # retest 08.10 pct.19: „trebuie să conțină chitanța și factura stinsă”


def test_def_168_functia_numeste_chitanta_numai_pe_ciorna_si_numai_la_incasare(cur):
    """`casa_api.nota_numeste_chitanta`: ciorna primește descrierea cu chitanța; nota VALIDATĂ nu se scrie (OMFP 1802/2014 pct.69, triggerul
    `regula_nota`) — se întoarce numai planul; vânzarea fără factură nu se atinge (textul „reprezentând” al omului). MUTAȚIE: condiția
    `status == "ciorna"` scoasă -> nota validată primește descrierea nouă -> pică (pe o firmă reală triggerul `regula_nota` ar refuza
    UPDATE-ul; aici nota e din aceeași tranzacție, `nota_din_tranzactia_curenta`, deci garda e chiar condiția din funcție)."""
    from core import casa_api
    fid = _factura(cur)
    op, nid = _incasare(cur, fid, CLIENT)
    assert casa_api.nota_numeste_chitanta(cur, SCH, op, "PRB-1")[3] == ASTEPTAT
    assert _descriere(cur, nid) == ASTEPTAT
    op2, nid2 = _incasare(cur, _factura(cur, 5), CLIENT, status="validata")
    r = casa_api.nota_numeste_chitanta(cur, SCH, op2, "PRB-2")
    assert (r[1], r[2], r[3]) == ("validata", CLIENT, ASTEPTAT.replace("PRB-1", "PRB-2").replace("nr. 4", "nr. 5"))
    assert _descriere(cur, nid2) == CLIENT
    op3, _nid3 = _incasare(cur, None, "Vânzare fără factură — chitanța PRB-3 — marfă — " + CLIENT, categorie="vanzare_fara_factura")
    assert casa_api.nota_numeste_chitanta(cur, SCH, op3, "PRB-3") is None


def test_def_168_migrarea_rescrie_ciornele_scrise_de_aplicatie_si_lasa_restul(cur):
    """Datele existente (`core/migrare_descriere_nota_chitanta.py`): ciorna cu descrierea aplicației (doar clientul — forma de dinainte de
    08.10 — sau „Încasare de la client — factura …”) se rescrie; nota validată, ciorna cu text scris de om și ciorna din luna închisă se
    lasă, numite. Idempotentă. MUTAȚIE: filtrul `_scrisa_de_aplicatie` scos din `plan` -> textul omului se rescrie -> pică."""
    from core import migrare_descriere_nota_chitanta as m
    def chitanta(op, nid, nr):
        cur.execute("INSERT INTO chitante (serie, numar, data, client_nume, suma, casa_operatiune_id, inregistrare_id) "
                    "VALUES ('PRB', %s, '2099-10-08', %s, 121.00, %s, %s)", (nr, CLIENT, op, nid))
    vechi = {}
    for nr, (descr, status, data) in enumerate((
            (CLIENT, "ciorna", "2099-10-08"),                                                          # 1: forma de dinainte de 08.10
            ("Încasare de la client — factura F1A nr. 5 din 06.10.2099 — " + CLIENT, "ciorna", "2099-10-08"),   # 2: forma 456
            (CLIENT, "validata", "2099-10-08"),                                                        # 3: validată -> lăsată
            ("Încasare chirie octombrie, scris de mână", "ciorna", "2099-10-08"),                       # 4: textul omului -> lăsat
            (CLIENT, "ciorna", "2099-09-08")), start=1):                                               # 5: luna închisă -> lăsată
        op, nid = _incasare(cur, _factura(cur, nr + 3), descr, status=status, data=data)
        chitanta(op, nid, nr)
        vechi[nr] = nid
    cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2099, 9)")
    p = m.aplica(cur.connection, SCH)
    assert sorted(n for _o, n, _v, _x, _c in p["ciorne"]) == [vechi[1], vechi[2]]
    assert _descriere(cur, vechi[1]) == "Încasare de la client — chitanța PRB-1 — factura F1A nr. 4 din 06.10.2099 — " + CLIENT
    assert _descriere(cur, vechi[2]) == "Încasare de la client — chitanța PRB-2 — factura F1A nr. 5 din 06.10.2099 — " + CLIENT
    assert [n for n, _v, _x in p["validate"]] == [vechi[3]] and _descriere(cur, vechi[3]) == CLIENT
    assert sorted((n, mot) for n, _v, mot in p["lasate"]) == [(vechi[4], "descrierea e scrisă de om"), (vechi[5], "luna 09/2099 e închisă")]
    assert _descriere(cur, vechi[4]) == "Încasare chirie octombrie, scris de mână"
    assert m.verifica(cur.connection, SCH) and not m.plan(cur, SCH)["ciorne"]     # idempotentă
