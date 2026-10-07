# -*- coding: utf-8 -*-
"""Lotul 07.10, partea 2 — retestul Costin din 06.10.2026 (F5 salarii nov. 2026, F1 factură): gărzile pe server.

Fiecare test numește punctul comenzii (DECIZII 06.10.2026, „Lotul 07.10”) și mutația care îl face roșu. Coada rulează pe o
schemă efemeră, într-o tranzacție anulată (aceeași formă ca `core/test_validare_note.py`)."""
import ast
import datetime
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot0710_p2"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


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
    cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false WHERE id=%s", (asist,))
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Lot 0710 SRL',%s) "
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


def _nota(conn, desc, suma, doc=None, data="2026-10-05"):
    from core import jurnal_api
    return jurnal_api.creeaza(conn, SCH, desc, data, [{"debit": "4111", "credit": "707", "suma": suma}], document_ref=doc)["id"]


def _factura_cu_doua_note(conn, cur):
    """Contarea facturii (legată prin `inregistrari.factura_id`) + ieșirea din stoc (legată prin `miscari_stoc.factura_id`)."""
    cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva) VALUES ('ZT1', '2026-10-05', 121, 21) RETURNING id")
    fid = cur.fetchone()[0]
    n_contare = _nota(conn, "Factura ZT1", 121)
    # [lotul 07.10 B, C8] sursele reale: contarea e a facturii (`facturi`), ieșirea e din stoc (`stocuri`)
    cur.execute("UPDATE inregistrari SET factura_id=%s, sursa='facturi' WHERE id=%s", (fid, n_contare))
    n_iesire = _nota(conn, "Ieșire marfă ZT1", 80, doc="Factură ZT1 din 05.10.2026")
    cur.execute("UPDATE inregistrari SET sursa='stocuri' WHERE id=%s", (n_iesire,))
    cur.execute("INSERT INTO articole (denumire) VALUES ('Marfa ZT') RETURNING id")
    aid = cur.fetchone()[0]
    cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, inregistrare_id, factura_id) "
                "VALUES (%s, '2026-10-05', 'iesire', 2, 80, %s, %s)", (aid, n_iesire, fid))
    return fid, n_contare, n_iesire


# ── pct.9: o factură = UN element de validat ─────────────────────────────────────────────────────────────────────────
def test_o_factura_e_un_singur_element_de_validat_si_se_valideaza_o_data(tx):
    """MUTAȚIE: `grup_nota` întoarce mereu cheia notei -> două elemente în listă, două validări -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    _fid, n1, n2 = _factura_cu_doua_note(conn, cur)
    anuntate = c.pune_notele_in_coada(conn, cab, tid, asist)
    assert len(anuntate) == 1                                   # un document anunțat, nu două note
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert len(el) == 1 and len(el[0]["membri_ids"]) == 2       # un element, cu ambele note
    _ca(cur, valid)
    r = c.aproba(conn, el[0]["id"], str(valid), valid, cabinet_id_apelant=cab, schema_nota=SCH)
    assert r["ok"] and len(r["membri"]) == 2
    cur.execute("SELECT count(*) FROM inregistrari WHERE id = ANY(%s) AND status = 'validata'", ([n1, n2],))
    assert cur.fetchone()[0] == 2                               # ambele note validate dintr-o singură aprobare


def test_documentul_se_respinge_si_se_retrimite_intreg(tx):
    """MUTAȚIE: `respinge` pe un singur rând (`WHERE id=%s`) -> a doua notă rămâne la validare -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    _fid, n1, n2 = _factura_cu_doua_note(conn, cur)
    cid = c.pune_notele_in_coada(conn, cab, tid, asist)[0]["coada_id"]
    assert len(c.respinge(conn, cid, str(valid), "lipsește avizul", respins_de_id=valid, cabinet_id_apelant=cab)["membri"]) == 2
    st = c.stari_note(conn, tid, [n1, n2])
    assert {st[n1]["stare_coada"], st[n2]["stare_coada"]} == {"respinsa"}
    assert c.retrimite_nota(conn, cab, tid, n2, asist)["ok"]
    st = c.stari_note(conn, tid, [n1, n2])
    assert {st[n1]["stare_coada"], st[n2]["stare_coada"]} == {"la_senior"}   # retrimisă cu tot documentul


# ── pct.4: retrimiterea nu e o pregătire nouă ────────────────────────────────────────────────────────────────────────
def test_respinsa_apoi_validata_e_o_pregatire_si_zero_la_suta_din_prima(tx):
    """Exemplul din comandă: „2 pregătite · 50% acceptate din prima”; corect 1 pregătită, 0% din prima.
    MUTAȚIE: `sql_cheie_pregatire` pe `id` (rândul) -> 2 pregătite -> pică."""
    from core import asistenti_api, coada_api as c, sinteza_zilnica
    conn, cur, tid, cab, asist, valid = tx
    inainte = asistenti_api.calitate(conn, cab, asist)
    cen0 = asistenti_api.centralizator(conn, cab)["totaluri"]["create"]
    sin0 = sinteza_zilnica.sinteza_cabinet(conn, cab, datetime.date.today())["pregatite"]
    _ca(cur, asist)
    nid = _nota(conn, "Chirie", 500, doc="Contract CH-1")
    cid = c.pune_notele_in_coada(conn, cab, tid, asist)[0]["coada_id"]
    c.respinge(conn, cid, str(valid), "data greșită", respins_de_id=valid, cabinet_id_apelant=cab)
    cid2 = c.retrimite_nota(conn, cab, tid, nid, asist)["coada_id"]
    _ca(cur, valid)
    assert c.aproba(conn, cid2, str(valid), valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    dupa = asistenti_api.calitate(conn, cab, asist)
    assert dupa["pregatite"] - inainte["pregatite"] == 1                     # o pregătire, oricâte rânduri
    assert dupa["din_prima"] - inainte["din_prima"] == 0                     # respinsă o dată: nu „din prima”
    assert dupa["evaluate"] - inainte["evaluate"] == 1
    assert asistenti_api.centralizator(conn, cab)["totaluri"]["create"] - cen0 == 1
    assert sinteza_zilnica.sinteza_cabinet(conn, cab, datetime.date.today())["pregatite"] - sin0 == 1


# ── pct.6: nota la validare nu se modifică ───────────────────────────────────────────────────────────────────────────
def test_nota_la_validare_nu_se_editeaza_nu_se_sterge_iar_dupa_respingere_da(tx):
    """MUTAȚIE: verificarea `nota_la_validare` scoasă din `jurnal_api.editeaza` -> editarea trece -> pică."""
    from core import coada_api as c, jurnal_api as j
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    nid = _nota(conn, "Telefon", 50, doc="Factura T1")
    cid = c.pune_notele_in_coada(conn, cab, tid, asist)[0]["coada_id"]
    r_ed = j.editeaza(conn, SCH, nid, descriere="Telefon corectat")
    r_st = j.sterge(conn, SCH, nid)
    assert (r_ed.get("cod"), r_st.get("cod")) == (c.COD_NOTA_LA_VALIDARE, c.COD_NOTA_LA_VALIDARE)
    c.respinge(conn, cid, str(valid), "suma", respins_de_id=valid, cabinet_id_apelant=cab)
    assert j.editeaza(conn, SCH, nid, descriere="Telefon corectat", data="2026-10-06") == {"ok": True}


def _conn_lipita(conn):
    """`db.get_conn` legat de conexiunea testului (aceeași tranzacție, anulată la final): use-case-ul rutei vede firma și nota
    din fixtură. Fără `commit` — tranzacția o închide fixtura."""
    import contextlib

    @contextlib.contextmanager
    def gc(schema=None):
        with conn.cursor() as c:
            c.execute('SET search_path TO %s' % (('"%s", public' % schema) if schema else "public"))
        yield conn
    return gc


def test_rutele_jurnalului_refuza_luna_inchisa_si_nota_la_validare(tx, monkeypatch):
    """PROBĂ DE COMPORTAMENT pe use-case-urile rutelor (nu pe funcțiile de domeniu): `PUT /jurnal/{nota_id}` cu o dată într-o
    lună ÎNCHISĂ e refuzat (pct.5, R42 (a)); `DELETE /jurnal/{nota_id}` pe o notă la validare e refuzat (pct.6).
    MUTAȚIE: poarta pe `corp.get("data")` scoasă din `jurnal_editeaza` -> editarea trece în luna închisă -> pică."""
    from core import coada_api as c, erori as _erori, uc_tenants
    conn, cur, tid, cab, asist, valid = tx
    cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (asist, tid))
    _ca(cur, asist)
    nid = _nota(conn, "Abonament", 30, doc="Factura AB1")
    cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2026, 9)")
    monkeypatch.setattr(_db, "get_conn", _conn_lipita(conn))
    with pytest.raises(_erori.Blocat):
        uc_tenants.jurnal_editeaza(tid, nid, {"data": "2026-09-15"}, {"uid": asist})       # luna nouă, închisă
    assert uc_tenants.jurnal_editeaza(tid, nid, {"data": "2026-10-02"}, {"uid": asist}) == {"ok": True}
    cur.execute('SET search_path TO "%s", public' % SCH)   # use-case-ul a lăsat conexiunea pe `public`
    c.pune_notele_in_coada(conn, cab, tid, asist)
    with pytest.raises(_erori.CerereGresita) as ei:
        uc_tenants.jurnal_sterge(tid, nid, {"uid": asist})
    assert ei.value.detaliu == c.MESAJ_NOTA_LA_VALIDARE % nid


def test_casa_nu_sterge_nota_de_la_validare(tx):
    """MUTAȚIE: verificarea scoasă din `casa_api.sterge` -> operațiunea și nota dispar -> pică."""
    from core import casa_api, coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    op = casa_api.adauga(conn, SCH, {"data": "2026-10-05", "categorie": sorted(casa_api.CONTURI)[0], "suma": 10,
                                     "document": "DP 1"})
    assert op.get("inregistrare_id"), op
    c.pune_notele_in_coada(conn, cab, tid, asist)
    assert casa_api.sterge(conn, SCH, op["id"]).get("cod") == c.COD_NOTA_LA_VALIDARE


# ── pct.5 / pct.7: data notei ────────────────────────────────────────────────────────────────────────────────────────
def test_editarea_datei_verifica_luna_noua_si_notele_lunare_au_ultima_zi():
    """pct.5: `jurnal_editeaza` cheamă poarta lunii închise pe data NOUĂ. pct.7: notele lunare ale aplicației (salarii,
    amortizare) poartă ultima zi a lunii — decizia Costin 06.10.2026 („dacă nu are [temei], data e ultima zi a lunii”).
    MUTAȚIE: `ultima_zi_a_lunii` întoarce ziua 28 -> pică; apelul pe `corp.get("data")` scos -> pică."""
    from core import uc_comun
    assert [uc_comun.ultima_zi_a_lunii(2026, m).day for m in (2, 10, 11, 12)] == [28, 31, 30, 31]
    assert uc_comun.ultima_zi_a_lunii(2028, 2).day == 29
    src = io.open("core/uc_tenants.py", encoding="utf-8").read()
    arb = ast.parse(src)
    fn = {f.name: f for f in ast.walk(arb) if isinstance(f, ast.FunctionDef)}
    porti = [n for n in ast.walk(fn["jurnal_editeaza"]) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "_cere_luna_deschisa"]
    arg = porti[0].args[2] if len(porti) == 1 else None
    assert isinstance(arg, ast.Call) and getattr(arg.func, "attr", "") == "get" and [x.value for x in arg.args] == ["data"]
    for nume in ("salarii_contare_scrie", "tenant_amortizare"):   # fără `if`: o funcție redenumită face testul roșu, nu vid
        assert sum(1 for n in ast.walk(fn[nume]) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "ultima_zi_a_lunii") >= 1, nume


# ── pct.8 / pct.12: notificarea numește firma și duce la element ─────────────────────────────────────────────────────
def test_notificarile_notei_numesc_firma_si_duc_la_element(tx):
    """MUTAȚIE: `_cu_firma` întoarce textul neschimbat / legătura rămâne „validat” -> pică."""
    from core import coada_api as c, uc_comun
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    nid = _nota(conn, "Curent", 40, doc="Factura E1")
    a = c.pune_notele_in_coada(conn, cab, tid, asist)
    uc_comun._notif_note_de_validat(conn, cab, [x["eticheta"] for x in a], asist, tenant_id=tid, coada_id=a[0]["coada_id"])
    cur.execute("SELECT text, link FROM public.notificari WHERE user_id=%s ORDER BY id DESC LIMIT 1", (valid,))
    text, link = cur.fetchone()
    assert text.split(":", 1)[0] == "ZT Lot 0710 SRL" and link == "validat:%d" % a[0]["coada_id"]
    c.respinge(conn, a[0]["coada_id"], str(valid), "motiv", respins_de_id=valid, cabinet_id_apelant=cab)
    uc_comun._notif_pregatitor(conn, a[0]["coada_id"], "respinsa", motiv="motiv")
    cur.execute("SELECT text, link FROM public.notificari WHERE user_id=%s ORDER BY id DESC LIMIT 1", (asist,))
    text, link = cur.fetchone()
    assert text.split(":", 1)[0] == "ZT Lot 0710 SRL" and link.split(":") == ["jurnal", str(tid), str(nid), "2026", "10"]


# ── pct.13: eticheta nu repetă documentul ────────────────────────────────────────────────────────────────────────────
def test_eticheta_notei_nu_repeta_documentul():
    """„Stat de plata 11/2026 · Stat de plată 11/2026”. MUTAȚIE: verificarea de repetiție scoasă -> trei părți -> pică."""
    from core import coada_api as c
    assert len(c.eticheta_element("nota", "nota", None, {"descriere": "Stat de plata 11/2026",
                                                           "document_ref": "Stat de plată 11/2026"}).split(" · ")) == 2
    assert len(c.eticheta_element("nota", "nota", None, {"descriere": "Salariile lunii 11/2026",
                                                           "document_ref": "Stat de plată nr SAL 11/2026 din 30.11.2026"}).split(" · ")) == 3


# ── pct.2: refuzul care trimite în alt ecran își păstrează ținta ─────────────────────────────────────────────────────
def test_refuzul_metodei_de_stoc_ajunge_cu_ecranul_tinta(tx):
    """Metoda de stoc nedeclarată: refuzul poartă `ecran = date_firma` pe toate drumurile (ieșirea pe articol trece prin
    `_mesaj_intrare`; descărcarea lunară îl întoarce în dicționar). MUTAȚIE: ramura `ecran` scoasă din `_mesaj_intrare` -> pică."""
    from core import metoda_stoc, stocuri_api, uc_comun
    conn, cur, tid, cab, asist, valid = tx
    det = uc_comun._mesaj_intrare(metoda_stoc.refuz(metoda_stoc.COD_NEDECLARATA, "Declar-o în Date firmă"))
    assert (det["ecran"], det["cod"]) == ("date_firma", metoda_stoc.COD_NEDECLARATA)
    cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'ZT', '14399840') ON CONFLICT (id) DO NOTHING")
    assert stocuri_api.descarca_luna(conn, SCH, 2026, 10).get("ecran") == "date_firma"


# ── pct.18: scadența propusă ─────────────────────────────────────────────────────────────────────────────────────────
def test_scadenta_propusa_vine_de_la_server_cu_temeiul():
    """Legea 72/2013 art.3 alin.(3) lit.a): fără termen în contract, dobânda curge „după 30 de zile calendaristice de la data
    primirii … facturii”. MUTAȚIE: zilele schimbate în 60 (plafonul art.5, termen CONTRACTUAL) -> pică."""
    from core import facturi_api
    zile, temei = facturi_api.SCADENTA_PROPUSA
    assert zile == 30                                            # Legea 72/2013 art.3 alin.(3) lit.a)
    assert (temei.tip, temei.nr, temei.an, temei.art, temei.alin, temei.lit) == ("Legea", 72, 2013, "3", "3", "a")


# ── pct.19: cine a schimbat = numele persoanei ───────────────────────────────────────────────────────────────────────
def test_jurnalul_date_firma_arata_numele_nu_emailul(tx):
    """MUTAȚIE: `u.email` pus la loc în `jurnal_firma` -> pică."""
    from core import repo_firma_profil
    conn, cur, tid, cab, asist, valid = tx
    cur.execute("SELECT NULLIF(TRIM(CONCAT_WS(' ', prenume, nume)), ''), email FROM public.users WHERE id=%s", (asist,))
    nume, email = cur.fetchone()
    cur.execute("INSERT INTO firma_profil_jurnal (camp, valoare_veche, valoare_noua, user_id) "
                "VALUES ('metoda_stoc', NULL, 'cantitativ_valoric', %s)", (asist,))
    assert repo_firma_profil.jurnal_firma(cur)[0]["cine"] == (nume or email)
