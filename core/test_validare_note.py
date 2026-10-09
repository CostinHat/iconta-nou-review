# -*- coding: utf-8 -*-
"""GARDA comenzii Costin 06.10.2026 (răspunsul la §6 din LOT_06_10):

  1. „Pct.12: varianta (a) — coada declarațiilor extinsă la note, un singur mecanism prin care cabinetul vede, validează sau
     respinge tot ce pregătește asistentul (inclusiv contorul „pregătite”, notificarea și Activitate cabinet).”
  2. „Concediul medical: indemnizația se contabilizează în nota de salarii (partea angajatorului și partea suportată din
     FNUASS), cu conturile și temeiul verificate la sursă (OUG 158/2005, OMFP 1802/2014), astfel încât 421 se soldează la ban
     și în lunile cu concediu medical.”

Testele de coadă rulează într-o SINGURĂ tranzacție anulată la final (scriu în `public.tenants` / `public.declaratii_coada`,
tabele partajate — CLAUDE.md: fixture pe tabel partajat = rollback). Utilizatorii sunt cei de test ai cabinetului Prisma.
"""
import datetime
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_validare_note"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ── pur ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_eticheta_elementului_e_una_singura():
    """MUTAȚIE: ramura notei scoasă -> „NOTA · nota-7” -> pică."""
    from core import coada_api as c
    assert c.eticheta_element("nota", "nota", "nota-7", {"descriere": "Chirie", "document_ref": "Factura CH1"}) == \
        "Notă · Chirie · Factura CH1"
    assert c.eticheta_element("declaratie", "d300", "25.11.2026", None) == "D300 · 25.11.2026"


# ── autorul cererii pe conexiune ──────────────────────────────────────────────────────────────────────────────────────────
def test_autorul_cererii_ajunge_pe_conexiune_si_se_sterge_la_intoarcere():
    """`db.get_conn` scrie autorul pe sesiune cât ține împrumutul și îl ȘTERGE înainte ca conexiunea să revină în pool —
    altfel cererea următoare, a altcuiva, ar scrie note pe numele lui. MUTAȚIE: RESET scos -> pică."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import autor_cerere
    tok = autor_cerere.seteaza(424242)
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT current_setting('iconta.utilizator', true), pg_backend_pid()")
            val, pid = cur.fetchone()
    finally:
        autor_cerere.reseteaza(tok)
    assert val == "424242"
    for _ in range(4):     # pool-ul poate da aceeași conexiune: acolo valoarea TREBUIE să fi dispărut
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT COALESCE(current_setting('iconta.utilizator', true), ''), pg_backend_pid()")
            v2, pid2 = cur.fetchone()
            if pid2 == pid:
                assert v2 == "", v2


# ── coada, cap-coadă, într-o tranzacție anulată ───────────────────────────────────────────────────────────────────────
@pytest.fixture()
def tx():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email='asistent@prisma-cont.test'")
    r = cur.fetchone()
    if not r:
        p.putconn(conn)
        pytest.skip("utilizatorul de test lipsește")
    asist, cab = r
    cur.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s AND poate_valida AND id<>%s ORDER BY id LIMIT 1",
                (cab, asist))
    valid = cur.fetchone()[0]
    # asistentul ca Ana: „Poate pregăti”, FĂRĂ „Poate valida” (bifa se anulează odată cu tranzacția)
    cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false WHERE id=%s", (asist,))
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Validare Note',%s) "
                "RETURNING id", (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET search_path TO "%s", public' % SCH)
    try:
        yield conn, cur, tid, cab, asist, valid
    finally:
        conn.rollback()
        cur = conn.cursor()
        cur.execute("RESET iconta.utilizator")
        cur.execute("RESET search_path")
        conn.commit()
        p.putconn(conn)


def _ca(cur, uid):
    cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(uid),))


def _nota(conn, desc, suma, doc=None):
    from core import jurnal_api
    r = jurnal_api.creeaza(conn, SCH, desc, "2026-10-05", [{"debit": "612", "credit": "401", "suma": suma}], document_ref=doc)
    return r["id"]


def test_nota_asistentului_intra_o_data_si_aprobarea_o_valideaza(tx):
    """MUTAȚIE: ramura notei din `aproba` scoasă (nota rămâne ciornă) -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    nid = _nota(conn, "Chirie octombrie", 1000, "Factura CH1 din 05.10.2026")
    cur.execute("SELECT creat_de_id FROM inregistrari WHERE id=%s", (nid,))
    assert cur.fetchone()[0] == asist                       # autorul vine din cerere, fără ca drumul de INSERT să-l știe
    adaugate = c.pune_notele_in_coada(conn, cab, tid, asist)
    assert [a["eticheta"] for a in adaugate] == ["Notă · Chirie octombrie · Factura CH1 din 05.10.2026"]
    assert c.pune_notele_in_coada(conn, cab, tid, asist) == []          # o singură dată
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert [(x["fel"], x["stare"]) for x in el] == [("nota", "la_senior")]
    _ca(cur, valid)
    assert c.aproba(conn, el[0]["id"], str(valid), valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    cur.execute("SELECT status FROM inregistrari WHERE id=%s", (nid,))
    assert cur.fetchone()[0] == "validata"
    assert c.stari_note(conn, tid, [nid])[nid]["stare_coada"] == "aprobata"


def test_respingerea_tine_pana_la_retrimitere(tx):
    """Respinsă = rămâne ciornă, cu motivul; NU se repune singură la următoarea cerere; revine numai prin retrimitere.
    MUTAȚIE: filtrul „niciun element” din `pune_notele_in_coada` slăbit la „niciun element activ” -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    nid = _nota(conn, "Telefon", 50)
    cid = c.pune_notele_in_coada(conn, cab, tid, asist)[0]["coada_id"]
    assert c.respinge(conn, cid, str(valid), "lipsește factura", respins_de_id=valid, cabinet_id_apelant=cab)["ok"]
    assert c.pune_notele_in_coada(conn, cab, tid, asist) == []
    st = c.stari_note(conn, tid, [nid])[nid]
    assert (st["stare_coada"], st["motiv_respingere"]) == ("respinsa", "lipsește factura")
    # [retest 07.10 seara, S3, decizia Costin] nota NESCHIMBATĂ față de cea respinsă se retrimite numai confirmată explicit
    assert c.retrimite_nota(conn, cab, tid, nid, asist)["cod"] == "NESCHIMBATA"
    assert c.retrimite_nota(conn, cab, tid, nid, asist, confirma=True)["ok"]
    assert c.stari_note(conn, tid, [nid])[nid]["stare_coada"] == "la_senior"
    assert c.retrimite_nota(conn, cab, tid, nid, asist)["cod"] == "DEJA_IN_COADA"


def test_jurnalul_si_coada_nu_pot_spune_lucruri_diferite(tx):
    """Validată direct din jurnal -> elementul se închide (cu validatorul); ștearsă cât e la validare -> elementul dispare.
    MUTAȚIE: triggerul `coada_nota_sincron` scos -> elementul rămâne „la validare” -> pică."""
    from core import coada_api as c, jurnal_api as j
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    n1, n2 = _nota(conn, "Apă", 20, doc="FCT apă 1"), _nota(conn, "Gaz", 30, doc="FCT gaz 1")   # [09.10, R3] cu documentul
    c.pune_notele_in_coada(conn, cab, tid, asist)
    _ca(cur, valid)
    assert j.valideaza(conn, SCH, n1)["ok"]
    cur.execute("SELECT stare, aprobat_de_id FROM public.declaratii_coada WHERE tenant_id=%s AND perioada=%s",
                (tid, c.perioada_nota(n1)))
    assert cur.fetchone() == ("aprobata", valid)
    _ca(cur, asist)
    # [lotul 07.10 pct.6] cât e la validare, nota nu se șterge din aplicație (cabinetul validează ce a văzut) …
    assert j.sterge(conn, SCH, n2).get("cod") == c.COD_NOTA_LA_VALIDARE
    # … iar dacă dispare totuși direct din bază, triggerul îi scoate elementul: coada și jurnalul tot nu pot diverge
    cur.execute("DELETE FROM inregistrari WHERE id=%s", (n2,))
    assert c.stari_note(conn, tid, [n2]) == {}


def test_nota_nu_se_depune_iar_tiparele_declaratiilor_n_o_vad(tx):
    """MUTAȚIE: filtrul `fel = 'declaratie'` scos din `tipare_api` -> motivul notei apare în tiparele declarațiilor -> pică."""
    from core import coada_api as c, tipare_api
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    _nota(conn, "Curent", 40)
    cid = c.pune_notele_in_coada(conn, cab, tid, asist)[0]["coada_id"]
    c.respinge(conn, cid, str(valid), "ZT-motiv-de-nota-unic", respins_de_id=valid, cabinet_id_apelant=cab)
    assert c.marcheaza_depusa(conn, cid, cabinet_id_apelant=cab)["cod"] == "STARE_GRESITA"
    assert "ZT-motiv-de-nota-unic" not in [m["motiv"] for m in tipare_api.tipare(conn, cab)["motive"]]


def test_validatorul_nu_pregateste_pentru_altcineva(tx):
    """Notele unui utilizator cu „Poate valida” nu intră în coadă (le validează el, în jurnal)."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    assert c.e_validator(conn, valid) is True and c.e_validator(conn, asist) is False


# ── concediul medical în nota de salarii ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def conn_cm():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % (SCH + "_cm"))
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH + "_cm"))
            cur.execute('SET search_path TO "%s", public' % (SCH + "_cm"))
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,declarant_nume,"
                        "declarant_prenume,declarant_functie,patron_nume) VALUES (1,'ZT CM SRL','14399840','Str 1','Buc',"
                        "'B','6202',true,'L','Pop','Ion','administrator','Pop Ion')")
            cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,cor,data_nastere,"
                        "tip_asigurat,functie_baza) VALUES ('1800101410013','IONESCU','X','2024-01-01',8,'B','251401',"
                        "'1980-01-01','1',true) RETURNING id, data_angajare) INSERT INTO salariu_istoric (salariat_id, "
                        "valabil_din, salariu_brut) SELECT id, data_angajare, 6000 FROM s RETURNING salariat_id")
            sid = cur.fetchone()[0]
        c.commit()
    with _db.get_conn(SCH + "_cm") as c:
        yield c, sid
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % (SCH + "_cm"))
        c.commit()


def _cm(conn, sid, **k):
    from core import salariati_api
    d = {"cod": "01", "zile_cm": 5, "venituri_6_luni": 36000, "zile_6_luni": 126, "serie": "CMZT", "numar": "1",
         "data_acordare": "2026-10-06", "data_inceput": "2026-10-06", "data_sfarsit": "2026-10-10", "an": 2026, "luna": 10}
    d.update(k)
    return salariati_api.salveaza_concediu(conn, sid, d)


@pytest.mark.parametrize("sept_zile, oct_zile, pereche_indemnizatie", [
    (4, 5, ("4382", "423")),   # episod din ziua 5 încolo -> FNUASS (OUG 158/2005 art.12 lit.B)
    (1, 3, ("6458", "423")),   # zilele 2-4 ale episodului -> angajatorul (art.12 lit.A)
])
def test_concediul_medical_in_nota_cu_421_si_423_soldate(conn_cm, sept_zile, oct_zile, pereche_indemnizatie):
    """Certificat de CONTINUARE (fără diminuarea primei zile): indemnizația intră în notă (angajator 6458 = 423 / FNUASS
    4382 = 423), reținerile ei pe 423 (OMFP 1802/2014, contul 423), cele din salariu pe 421; 421 și 423 soldate LA BAN cu
    netul salariului și netul indemnizației de pe fluturași.
    MUTAȚIE: împărțirea reținerilor scoasă (totul pe 421) -> divergențe pe 421 și 423 -> pică."""
    from core import salarii_contare as sc
    conn, sid = conn_cm
    _cm(conn, sid, data_acordare="2026-09-%02d" % (31 - sept_zile), data_inceput="2026-09-%02d" % (31 - sept_zile),
        data_sfarsit="2026-09-30", zile_cm=sept_zile, an=2026, luna=9, numar="0")
    _cm(conn, sid, este_continuare=True, serie_initiala="CMZT", numar_initial="0", zile_cm=oct_zile,
        data_sfarsit="2026-10-%02d" % (5 + oct_zile))
    p = sc.propunere(conn, SCH + "_cm", 2026, 10)
    perechi = {(n["debit"], n["credit"]) for n in p["note"]}
    assert {pereche_indemnizatie, ("421", "4315"), ("423", "4315"), ("423", "4316")} <= perechi, p["note"]
    assert p["divergente"] == [], p["divergente"]
    note = [(n["debit"], n["credit"], Decimal(str(n["suma"]))) for n in p["note"]]
    assert sc.sold_421(note) == Decimal(str(p["net_fluturasi"]))
    assert sc.sold_423(note) == Decimal(str(p["net_cm_fluturasi"])) > 0


def test_fisierul_de_plata_inchide_si_421_si_423(conn_cm):
    """OUG 158/2005 art.36 alin.(3) lit.a): indemnizația se plătește de angajator „cel mai târziu odată cu lichidarea
    drepturilor salariale pe luna respectivă” -> totalul fișierului SEPA = soldul 421 + soldul 423 după notă.
    MUTAȚIE: `cm_net` scos din suma plătită -> totalul = doar 421 -> pică."""
    from core import plata_salarii, salarii_contare as sc, salariati_api as _sa
    conn, sid = conn_cm
    iban = "RO49AAAA1B31007593840000"   # IBAN-ul-exemplu publicat pentru România (verificat mai jos, nu presupus)
    assert _sa.iban_valid(iban)
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET iban=%s", (iban,))
        cur.execute("UPDATE salariati SET iban=%s WHERE id=%s", (iban, sid))
    _cm(conn, sid, data_acordare="2026-09-30", data_inceput="2026-09-30", data_sfarsit="2026-09-30", zile_cm=1,
        an=2026, luna=9, numar="0")
    _cm(conn, sid, este_continuare=True, serie_initiala="CMZT", numar_initial="0", zile_cm=3, data_sfarsit="2026-10-08")
    _xml, meta = plata_salarii.genereaza_pain001(conn, SCH + "_cm", 2026, 10, data_executie=datetime.date(2026, 11, 5))
    p = sc.propunere(conn, SCH + "_cm", 2026, 10)
    note = [(n["debit"], n["credit"], Decimal(str(n["suma"]))) for n in p["note"]]
    assert Decimal(str(meta["total"])) == sc.sold_421(note) + sc.sold_423(note), (meta["total"], p["note"])
