# -*- coding: utf-8 -*-
"""Lotul 12, deficiența C139 — „Șterge raportul Z”: raportul Z nevalidat (importat din AMEF sau scris de mână) se șterge de pe rândul lui
din ecranul Raport Z, cu nota lui ciornă și cu descărcările lui din stoc încă necontate, într-o singură tranzacție; Z-ul validat și luna
blocată se refuză numit (`core/z_descarcare.py::plan_stergere` / `sterge_z`, `core/uc_raport_z.py`).

C139 (găsită de Code la scenariul pilot, pasul 13): „Un raport Z importat (ciornă) nu se poate șterge de nicăieri: Registrul jurnal refuză
nota derivată, iar pentru Raport Z nu există drum de ștergere — un fișier AMEF importat greșit rămâne în lună.”

Schemă efemeră din `tenant_template.sql`, într-o tranzacție anulată la final (rândul din `public.tenants` și cel din coadă sunt sintetice,
în ROLLBACK); datele sunt în 2099 (perioadă evident sintetică). CUI-ul firmei efemere: 14399840 (DANTE INTERNATIONAL SA, firmă reală —
cifra de control verificată cu algoritmul din CLAUDE.md).
"""
import io
import re
from contextlib import contextmanager
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot12_zsterge"
DATA = "2099-10-20"
NUI = "8000000001"


# Mesajele se citesc pe STRUCTURA lor, nu prin „șirul apare undeva” (`core/test_garzi_pe_text.py`): refuzul = șablonul `zd.MESAJ_*` ales,
# cu valorile lui; confirmarea = propozițiile ei întregi, sumele din paranteză, lista „Se șterg odată cu el: a; b”.
def _parametri(sablon, text):
    """Valorile `%s` cu care `sablon` dă EXACT `text`; None dacă textul nu e din șablonul acesta."""
    m = re.fullmatch(re.escape(sablon).replace("%s", "(.+?)"), text or "")
    return m.groups() if m else None


def _propozitii(text):
    return re.split(r"(?<=[.?!])\s+", text.strip())


def _odata_cu(confirmare):
    """Elementele listei „Se șterg odată cu el: a; b.”, fiecare fără paranteza de la capăt (notele, care diferă de la o rulare la alta)."""
    lista = [x.split(": ", 1)[1] for x in _propozitii(confirmare) if x.startswith("Se șterg odată cu el: ")]
    assert len(lista) == 1, confirmare
    return [re.sub(r" \([^()]*\)$", "", e) for e in lista[0].rstrip(".").split("; ")]


def _eticheta(cur, z):
    from core import z_descarcare as zd
    # [lotul 13, 605] documentul Z („Raport Z nr 0042 din …”) se numește o dată: „Raportul Z nr 0042 din …”, nu „Raportul Z „Raport Z nr …””
    doc = zd.document_z(cur, SCH, z)
    return ("Raportul Z" + doc[len("Raport Z"):]) if doc.startswith("Raport Z ") else "Raportul Z „%s”" % doc


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _fixtura(tip_firma, metoda):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email='patron@prisma-cont.test'")
    r = cur.fetchone()
    if not r:
        p.putconn(conn)
        pytest.skip("utilizatorul de test lipsește")
    uid, cab = r
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, metoda_stoc, tip_firma) VALUES (1, 'Z STERGE SRL', '14399840', %%s, %%s)"
                % SCH, (metoda, tip_firma))
    # fixtura-sintetica-ok: rândul din public.tenants e scris în tranzacția fixturii, anulată (ROLLBACK) la ieșire
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Lot 12 C139',%s) RETURNING id",
                (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
    return p, conn, cur, tid, uid, cab


@pytest.fixture()
def tx():
    p, conn, cur, tid, uid, cab = _fixtura("srl", "cantitativ_valoric")
    try:
        yield conn, cur, tid, uid, cab
    finally:
        conn.rollback()
        p.putconn(conn)


@pytest.fixture()
def tx_gv():
    p, conn, cur, tid, uid, cab = _fixtura("srl", "global_valoric")
    try:
        yield conn, cur, tid, uid, cab
    finally:
        conn.rollback()
        p.putconn(conn)


@pytest.fixture()
def tx_pfa():
    p, conn, cur, tid, uid, cab = _fixtura("pfa", "cantitativ_valoric")
    try:
        yield conn, cur, tid, uid, cab
    finally:
        conn.rollback()
        p.putconn(conn)


def _articol(conn, den="Marfa A", cant=10, pret="2", data="2099-10-01"):
    from core import stocuri_cv_api as cva
    r = cva.intrare(conn, SCH, {"denumire": den, "um": "buc", "data": data, "cantitate": cant, "pret_unitar": pret,
                                "document": "Inventar inițial probă"})
    assert "eroare" not in r, r
    return r["articol_id"]


def _z_amef(cur, nr="0042"):
    """Raportul Z importat din AMEF, cum îl scrie `uc_tenants.horeca_import_amef` (nota ciornă `amef`, liniile, cotele, casa + bonurile)."""
    from core import repo_contabilitate as rc
    from core import jurnal_api as j
    iid = rc.nota_amef_ciorna(cur, SCH, DATA, "Z-%s-%s" % (NUI, nr), "Raport Z %s AMEF %s nr %s (12 bonuri)" % (DATA, NUI, nr),
                              j.eticheta_document("Raport Z", nr, DATA, "AMEF %s" % NUI))[0]
    rc.adauga_linie_4(cur, SCH, iid, "5311", "707", Decimal("200.00"))
    rc.adauga_linie_4(cur, SCH, iid, "5125", "707", Decimal("31.00"))
    rc.adauga_linie_4(cur, SCH, iid, "707", "4427", Decimal("40.09"))
    rc.adauga_z_cota(cur, SCH, iid, Decimal("21"), Decimal("190.91"), Decimal("40.09"))
    rc.adauga_z_amef(cur, SCH, iid, NUI, 12)
    return iid


def _stoc(cur, aid):
    cur.execute("SELECT COALESCE(SUM(CASE WHEN tip='intrare' THEN cantitate WHEN tip='iesire' THEN -cantitate ELSE 0 END), 0) "
                "FROM miscari_stoc WHERE articol_id = %s", (aid,))
    return cur.fetchone()[0]


def _exista(cur, tabel, cond, *arg):
    cur.execute("SELECT count(*) FROM %s WHERE %s" % (tabel, cond), arg)
    return cur.fetchone()[0]


def _valideaza(cur, nid):
    cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))


# ── ciornă -> se șterge tot, stocul revine ──────────────────────────────────────────────────────────────────────────────────────────
def test_def_c139_z_amef_ciorna_se_sterge_cu_descarcarile_si_stocul_revine(tx):
    """MUTAȚIE: `DELETE FROM miscari_stoc` scos din `sterge_z` -> ieșirea rămâne, stocul nu revine -> pică."""
    from core import retete_api as ra, stocuri_cv_api as cva, z_descarcare as zd
    conn, cur, tid, uid, _cab = tx
    aid = _articol(conn)
    z = _z_amef(cur)
    r1 = cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 2, "z_id": z})
    cur.execute("INSERT INTO retete (denumire) VALUES ('Pachet') RETURNING id")
    rid = cur.fetchone()[0]
    cur.execute("INSERT INTO retete_linii (reteta_id, articol_id, cantitate) VALUES (%s, %s, 1)", (rid, aid))
    r2 = ra.descarca(conn, SCH, {"reteta_id": rid, "portii": 3, "data": DATA, "z_id": z})
    assert _stoc(cur, aid) == 5
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    assert plan["refuz"] is None, plan
    # ce s-a spus înainte, cu cifrele: încasatul, TVA-ul, nota Z-ului, ieșirile și valoarea lor la cost (2 + 3 buc × CMP 2,00 = 10,00 lei)
    assert {"încasat 231,00 lei, TVA 40,09 lei"} <= set(re.findall(r"\(([^()]*)\)", plan["confirmare"])), plan["confirmare"]
    assert _odata_cu(plan["confirmare"])[1:] == ["2 ieșiri din stoc legate de el, necontate, în valoare de 10,00 lei la cost"], (
        plan["confirmare"])
    assert {"Marfa descărcată revine în stoc."} <= set(_propozitii(plan["confirmare"])), plan["confirmare"]
    # Z-ul, nota lui (liniile, cotele, casa + bonurile prin ON DELETE CASCADE), notele descărcărilor și mișcările lor: toate au plecat
    for nid in (z, r1["inregistrare_id"], r2["inregistrare_id"]):
        assert _exista(cur, "inregistrari", "id = %s", nid) == 0
        assert _exista(cur, "inregistrari_linii", "inregistrare_id = %s", nid) == 0
    assert _exista(cur, "rapoarte_z_amef", "inregistrare_id = %s", z) == 0
    assert _exista(cur, "rapoarte_z_cote", "inregistrare_id = %s", z) == 0
    assert _exista(cur, "miscari_stoc", "tip = 'iesire'") == 0
    assert _stoc(cur, aid) == 10                                     # marfa revine în stoc: 10 − 2 − 3 + 5 = 10
    # urma în audit, în aceeași tranzacție, cu ce s-a șters
    cur.execute("SELECT user_id, tenant_id, entitate, detalii FROM public.audit_log WHERE actiune = 'STERGERE raport Z' "
                "AND entitate_id = %s", (str(z),))
    a = cur.fetchall()
    assert len(a) == 1 and a[0][0] == uid and a[0][1] == tid and a[0][2] == "raport_z", a
    assert a[0][3]["fel"] == "fapt" and a[0][3]["incasat"] == "231.00" and sorted(a[0][3]["note_iesiri"]) == sorted(
        [r1["inregistrare_id"], r2["inregistrare_id"]])


def test_def_c139_z_scris_de_mana_la_global_valoric_se_sterge(tx_gv):
    """Clasa: Z-ul scris de mână (`horeca_z`), la stocul global-valoric (fără descărcare pe articol), se șterge pe același drum."""
    from core import repo_contabilitate as rc, z_descarcare as zd
    conn, cur, tid, uid, _cab = tx_gv
    z = rc.nota_horeca_z_ciorna(cur, SCH, DATA, "Z-%s-0050" % NUI, "Raport Z", "Raport Z nr 0050 din 20.10.2099 (casa %s)" % NUI)[0]
    rc.adauga_linie_3(cur, SCH, z, "5311", "707", 121)
    rc.adauga_linie_3(cur, SCH, z, "707", "4427", 21)
    rc.adauga_z_amef(cur, SCH, z, NUI, 3)
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    assert plan["refuz"] is None and "din stoc" not in plan["confirmare"], plan
    assert _exista(cur, "inregistrari", "id = %s", z) == 0


# ── refuzurile numite ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c139_z_validat_se_refuza_numit_si_nu_se_sterge_nimic(tx):
    """MUTAȚIE: verificarea `status != 'ciorna'` scoasă din `plan_stergere` -> Z-ul validat ar intra în ștergere -> pică."""
    from core import z_descarcare as zd
    conn, cur, tid, uid, _cab = tx
    z = _z_amef(cur)
    cur.execute("UPDATE rapoarte_z_amef SET fara_marfa = true WHERE inregistrare_id = %s", (z,))
    _valideaza(cur, z)
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    # OMFP 1802/2014 pct.69: „Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie
    # prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia” — validatul nu
    # se șterge, se stornează
    from core import eticheta_nota as _et
    assert _parametri(zd.MESAJ_Z_VALIDAT, plan["refuz"]) == (_eticheta(cur, z), _et.nota(cur, SCH, z)), plan
    assert {"O greșeală se corectează prin stornare (OMFP 1802/2014 pct.69), în Registru jurnal: o notă cu aceleași conturi și sumele "
            "cu minus."} <= set(_propozitii(plan["refuz"])), plan["refuz"]
    assert plan["cod"] == zd.COD_Z_NU_SE_STERGE
    assert _exista(cur, "inregistrari", "id = %s", z) == 1
    assert _exista(cur, "public.audit_log", "actiune = 'STERGERE raport Z' AND entitate_id = %s", str(z)) == 0


def test_def_c139_luna_blocata_se_refuza_numit(tx):
    """MUTAȚIE: verificarea `luna_blocata` scoasă din `plan_stergere` -> ștergerea ar ajunge la baza care refuză cu PERIOADA_BLOCATA
    (excepție, nu refuz numit) -> pică."""
    from core import stocuri_cv_api as cva, z_descarcare as zd
    conn, cur, tid, uid, _cab = tx
    aid = _articol(conn)
    z = _z_amef(cur)
    cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 2, "z_id": z})
    cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2099, 10)")
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    assert plan["cod"] == zd.COD_LUNA_BLOCATA and _parametri(zd.MESAJ_LUNA_BLOCATA, plan["refuz"]) == (_eticheta(cur, z), "10.2099"), plan
    assert _exista(cur, "inregistrari", "id = %s", z) == 1 and _stoc(cur, aid) == 8


def test_def_c139_descarcarea_validata_se_refuza(tx):
    """Ieșirea legată de Z, cu nota ei validată, a intrat în evidență: Z-ul nu se mai șterge (marfa ieșită nu se desface)."""
    from core import stocuri_cv_api as cva, z_descarcare as zd
    conn, cur, tid, uid, _cab = tx
    aid = _articol(conn)
    z = _z_amef(cur)
    r = cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 2, "z_id": z})
    _valideaza(cur, r["inregistrare_id"])
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    from core import eticheta_nota as _et
    assert _parametri(zd.MESAJ_IESIRE_VALIDATA, plan["refuz"]) == (_eticheta(cur, z), _et.nota(cur, SCH, r["inregistrare_id"])), plan
    assert _exista(cur, "inregistrari", "id = %s", z) == 1 and _stoc(cur, aid) == 8


def test_def_c139_z_la_validare_in_cabinet_se_refuza(tx):
    """Nota Z-ului la validare (coada, `la_senior`): cât așteaptă, nu se șterge — aceeași regulă ca în Registrul jurnal."""
    from core import coada_api, z_descarcare as zd
    conn, cur, tid, uid, cab = tx
    z = _z_amef(cur)
    # fixtura-sintetica-ok: rândul din coada PARTAJATĂ e scris în tranzacția fixturii, anulată (ROLLBACK) la ieșire; perioada 2099
    cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, fel, perioada, stare, payload, hash) "
                "VALUES (%s, %s, 'nota', 'nota', %s, 'la_senior', '{}'::jsonb, 'x')", (cab, tid, "nota-%d" % z))
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    from core import eticheta_nota as _et
    assert plan["cod"] == coada_api.COD_NOTA_LA_VALIDARE, plan
    assert _parametri(zd.MESAJ_LA_VALIDARE, plan["refuz"]) == (_eticheta(cur, z), _et.nota(cur, SCH, z)), plan
    assert _exista(cur, "inregistrari", "id = %s", z) == 1


def test_def_c139_costul_iesirilor_de_dupa_s_ar_schimba_se_refuza(tx):
    """CMP: după ieșirea Z-ului vin o intrare și o altă ieșire; ștergerea ar schimba costul acelei ieșiri în fișă fără să-i schimbe nota.
    Înainte: 8 buc × 2,00 + 5 × 5,00 = 41,00 / 13 -> ieșirea de 1 buc = 3,15; fără ieșirea Z-ului: 45,00 / 15 = 3,00. OMFP 1802/2014 pct.96
    (costul mediu ponderat). MUTAȚIE: `_schimba_costul` întoarce mereu None -> ștergerea trece -> pică."""
    from core import stocuri_cv_api as cva, z_descarcare as zd
    conn, cur, tid, uid, _cab = tx
    aid = _articol(conn)
    z = _z_amef(cur)
    cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 2, "z_id": z})
    cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document) "
                "VALUES (%s, '2099-10-21', 'intrare', 5, 5, 25, 'NIR probă')", (aid,))
    r = cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-22", "cantitate": 1, "document": "Bon probă"})
    assert r["valoare"] == "3.15", r
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    # refuzul de cost, cu articolul și prima ieșire de după (documentul și data ei)
    assert _parametri(zd.MESAJ_COST_SCHIMBAT, plan["refuz"]) == (_eticheta(cur, z), "Marfa A", "Bon probă", "22.10.2099"), plan
    assert _exista(cur, "inregistrari", "id = %s", z) == 1 and _stoc(cur, aid) == 12


def test_def_c139_descarcarea_respinsa_si_stornata_pleaca_odata_cu_z(tx):
    """Ieșirea respinsă la validare are în fișă stornarea ei în roșu (aceeași notă, `anuleaza_id`): pleacă amândouă, iar stocul rămâne."""
    from core import stocuri_anulare as sa, stocuri_cv_api as cva, z_descarcare as zd
    conn, cur, tid, uid, _cab = tx
    aid = _articol(conn)
    z = _z_amef(cur)
    r = cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 2, "z_id": z})
    st = sa.storneaza(conn, SCH, None, [r["inregistrare_id"]], "probă")
    assert st.get("stornate"), st
    assert _stoc(cur, aid) == 10
    plan = zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)
    assert plan["refuz"] is None and _odata_cu(plan["confirmare"])[1:] == ["descărcările lui respinse la validare"], plan
    assert _exista(cur, "miscari_stoc", "articol_id = %s AND tip = 'iesire'", aid) == 0 and _stoc(cur, aid) == 10
    assert _exista(cur, "inregistrari", "id IN (%s, %s)", z, r["inregistrare_id"]) == 0


def test_def_c139_pfa_incasarea_ciorna_din_registru_pleaca_cu_z(tx_pfa):
    """[368] La partidă simplă Z-ul își scrie încasarea în registrul de încasări și plăți: ciornă, pleacă odată cu el; validată, refuz."""
    from core import rip_api, z_descarcare as zd
    conn, cur, tid, uid, _cab = tx_pfa
    z = _z_amef(cur)
    cur.execute("UPDATE rapoarte_z_amef SET fara_marfa = true WHERE inregistrare_id = %s", (z,))
    r = rip_api.adauga(conn, SCH, {"data_operatiune": DATA, "tip": "incasare", "document_tip": "raport Z", "document_numar": "0042",
                                   "document_data": DATA, "explicatie": zd.EXPLICATIE_RIP % ("0042", NUI), "suma": 200,
                                   "metoda": "numerar", "categorie": "activitate"}, user_id=uid)
    assert r.get("id"), r
    p = zd.plan_stergere(cur, SCH, z)
    assert p["rip"] == r["id"] and "nota" not in p["confirmare"], p
    assert _odata_cu(p["confirmare"]) == ["TVA-ul lui pe cote", "încasarea lui din registrul de încasări și plăți"], p
    cur.execute("UPDATE rip_operatiuni SET status = 'validata' WHERE id = %s", (r["id"],))
    assert _parametri(zd.MESAJ_RIP_VALIDATA, zd.plan_stergere(cur, SCH, z)["refuz"]) == (_eticheta(cur, z),)
    cur.execute("UPDATE rip_operatiuni SET status = 'ciorna' WHERE id = %s", (r["id"],))
    assert zd.sterge_z(conn, SCH, z, user_id=uid, tenant_id=tid)["refuz"] is None
    assert _exista(cur, "rip_operatiuni", "id = %s", r["id"]) == 0 and _exista(cur, "inregistrari", "id = %s", z) == 0


# ── lista lunii: ce arată ecranul pe rând ─────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c139_lista_lunii_poarta_confirmarea_pe_ciorna_si_refuzul_pe_validat(tx):
    """MUTAȚIE: cheia `stergere` scoasă din `lista_luna` -> ecranul n-ar avea ce întreba -> pică."""
    from core import z_descarcare as zd
    conn, cur, tid, uid, _cab = tx
    z1 = _z_amef(cur, "0042")
    z2 = _z_amef(cur, "0043")
    cur.execute("UPDATE rapoarte_z_amef SET fara_marfa = true WHERE inregistrare_id = %s", (z2,))
    _valideaza(cur, z2)
    rap = {x["id"]: x for x in zd.lista_luna(conn, SCH, 2099, 10)}
    assert rap[z1]["status"] == "ciorna" and rap[z1]["stergere"]["refuz"] is None
    # [lotul 13, 605] documentul Z se numește o dată („raportul Z Raport Z nr” era deficiența)
    assert rap[z1]["stergere"]["confirmare"].startswith("Ștergi raportul Z nr 0042 din 20.10.2099 (AMEF 8000000001)")
    from core import eticheta_nota as _et
    assert rap[z2]["status"] == "validata"
    assert _parametri(zd.MESAJ_Z_VALIDAT, rap[z2]["stergere"]["refuz"]) == (_eticheta(cur, z2), _et.nota(cur, SCH, z2)), rap[z2]


# ── use-case: traducerea refuzului ────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c139_use_case_traduce_refuzul_in_clasa_de_domeniu(monkeypatch):
    """Luna blocată -> `Blocat` (423, ca restul porții de perioadă); celelalte refuzuri -> `Conflict` (409); Z inexistent -> 404."""
    from core import erori, uc_raport_z as uz, uc_comun, z_descarcare as zd

    @contextmanager
    def _conn(_schema=None):
        yield None
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: "tenant_x")
    monkeypatch.setattr(uz.db, "get_conn", _conn)
    ctx = {"uid": 1}
    for cod, clasa in ((zd.COD_LUNA_BLOCATA, erori.Blocat), (zd.COD_Z_NU_SE_STERGE, erori.Conflict)):
        monkeypatch.setattr(zd, "sterge_z", lambda *a, _c=cod, **k: {"refuz": "nu", "cod": _c, "z": {"document": "Raport Z nr 1"}})
        with pytest.raises(clasa) as e:
            uz.horeca_z_sterge(5, 7, ctx)
        # afirmația tipată (P8) + `mesaj` pentru ecran (G10)
        assert e.value.detaliu == {"fel": "neconformitate", "tip": cod, "motiv": "nu", "unde": "Raport Z nr 1",
                                   "regula": "OMFP 1802/2014 pct.69", "mesaj": "nu", "cod": cod, "temei": "OMFP 1802/2014 pct.69"}
    monkeypatch.setattr(zd, "sterge_z", lambda *a, **k: None)
    with pytest.raises(erori.Inexistent):
        uz.horeca_z_sterge(5, 7, ctx)
    monkeypatch.setattr(zd, "sterge_z", lambda *a, **k: {"refuz": None, "z": {"id": 7}, "note_iesiri": [], "miscari": [1, 2], "rip": None,
                                                        "dupa": "s-a șters"})
    assert uz.horeca_z_sterge(5, 7, ctx) == {"ok": True, "sters": {"id": 7}, "note_iesiri": [], "miscari_stoc": 2, "rip": None,
                                             "mesaj": "s-a șters"}


def test_def_c139_ruta_de_stergere_exista_si_cheama_use_case_ul():
    """Ruta `DELETE /tenants/{tenant_id}/horeca/raport-z/{nota_id}` e în aplicație, cu dreptul „Poate pregăti” (ca importul) și
    delegă la `uc_raport_z.horeca_z_sterge`."""
    import ast
    src = io.open("main.py", encoding="utf-8").read()
    gasit = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and any(
        isinstance(d, ast.Call) and getattr(d.func, "attr", "") == "delete" and d.args
        and getattr(d.args[0], "value", "") == "/tenants/{tenant_id}/horeca/raport-z/{nota_id}" for d in n.decorator_list)]
    assert len(gasit) == 1
    apeluri = [n for n in ast.walk(gasit[0]) if isinstance(n, ast.Call)]
    # delegă la use-case (cu argumentele rutei) și cere dreptul „Poate pregăti”
    assert [[ast.unparse(a) for a in n.args] for n in apeluri if ast.unparse(n.func) == "_uc_raport_z.horeca_z_sterge"] == [
        ["tenant_id", "nota_id", "ctx"]], [ast.unparse(n) for n in apeluri]
    assert [[ast.unparse(a) for a in n.args] for n in apeluri if ast.unparse(n.func) == "cere_drept"] == [["_drepturi.PREGATI"]], (
        [ast.unparse(n) for n in apeluri])
