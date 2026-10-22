# -*- coding: utf-8 -*-
"""[lotul 11, T2 — urmarea deficienței 458, comanda Costin 11.3 pct.6: „regenerările automate ale aplicației apar ca greșeli ale
administratorului; numerele de respingeri nu se adună cu rândurile.”]

A458 a reparat calitatea asistentului / Erori — echipa / centralizatorul / jurnalul și a lăsat clichetul `DE_REPARAT` pe celelalte trei
numărători de respingeri pe declarații. Aici se repară și se apără:

- `capacitate_api.capacitate` („% acceptate” al pregătitorului): număra pregătirea înlocuită la „Generează din nou” ca respinsă;
- `sinteza_zilnica.sinteza_cabinet` (emailul de seară): „1 respinsă” pe 18.10 și 19.10 pe cabinetul de test erau înlocuiri;
- `tipare_api.tipare` (Educație pe tipare): motivul nr.1 era „Înlocuită de declarația generată din nou (…)” (n=3), iar totalurile numărau
  RÂNDURI de coadă (o declarație generată de trei ori = 3), nu pregătiri; acum o singură listă de pregătiri, Σ motive = Σ pe tipuri = Σ pe
  firme = `respinse`.

Măsurat pe producție, numai citire, cabinetul de test „Cabinet Test Sesiunea B SRL” (48765), 22.10.2026: tipare înainte motive
[„Înlocuită…” 3, „Depășită, lipsește F1A5…” 1], d300 4 / 5; după [„Depășită…” 1], d300 1 / 1; sinteza 18.10 și 19.10 respinse 1 -> 0.

Datele se fac pe drumul aplicației (`coada_api.adauga_in_coada`, `inlocuieste`, `respinge`), pe un cabinet sintetic creat în tranzacție
(numărătorile sunt exacte, fără bază de pornire), an 2099, totul ANULAT. Date de pornire inserate direct (aplicația nu le produce altfel
într-un test): cabinetul, cei doi oameni și cele două firme — rânduri `public.*` efemere, în aceeași tranzacție anulată.

Notă: într-o tranzacție `now()` e constant; de aceea fiecare caz stă pe altă perioadă (o respingere a omului, cerere separată în
aplicație, ar arăta altfel ca o înlocuire dacă urmașul aceleiași perioade s-ar crea în aceeași tranzacție — exact deosebirea din
`coada_api.sql_inlocuita`, apărată structural de `test_lot11_a458_erori_echipa.py::test_inlocuirea_si_urmasul_sunt_in_aceeasi_tranzactie`).

Temei: N/A — indicatori interni ai cabinetului (nu regulă fiscală).
"""
import pytest

from core import db as _db

MOTIV_INLOCUIRE = "Înlocuită de declarația generată din nou (Probă T2)."


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def tx():
    """Cabinet sintetic (un pregătitor, un validator, două firme fără schemă), totul într-o tranzacție ANULATĂ."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT Lot 11 T2') RETURNING id")
        cab = cur.fetchone()[0]
        cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ,poate_pregati,"
                    "poate_valida,poate_depune) VALUES ('zt_t2_asist@invalid','x','Asistent','T2','angajat',%s,true,true,false,false) "
                    "RETURNING id", (cab,))
        asist = cur.fetchone()[0]
        cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ,poate_pregati,"
                    "poate_valida,poate_depune) VALUES ('zt_t2_valid@invalid','x','Validator','T2','admin_firma',%s,true,false,true,true) "
                    "RETURNING id", (cab,))
        valid = cur.fetchone()[0]
        tids = []
        for i, nume in enumerate(("ZT T2 Unu SRL", "ZT T2 Doi SRL")):
            cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id, activ) VALUES (%s,%s,%s,true) RETURNING id",
                        ("efemer_lot11_t2_%d" % i, nume, cab))
            tids.append(cur.fetchone()[0])
        cur.execute("SELECT now()::date")
        azi = cur.fetchone()[0]
        yield conn, cab, asist, valid, tids, azi
    finally:
        conn.rollback()
        p.putconn(conn)


def _declaratie(conn, cab, tid, uid, luna, tip="d300"):
    from core import coada_api as c
    r = c.adauga_in_coada(conn, cab, tid, tip, 2099, {"xml": "<x/>"}, creat_de=str(uid), creat_de_id=uid, luna=luna)
    assert r["ok"], r
    return r["coada_id"]


def _genereaza_din_nou(conn, cab, tid, uid, coada_id, luna, tip="d300"):
    """„Generează din nou”: pașii din `uc_coada.coada_adauga` — cea veche iese (`inlocuieste`), cea nouă intră, în ACEEAȘI tranzacție."""
    from core import coada_api as c
    with conn.cursor() as cur:
        assert c.inlocuieste(cur, coada_id, cab, uid, MOTIV_INLOCUIRE)
    return _declaratie(conn, cab, tid, uid, luna, tip)


def _respinge(conn, cab, coada_id, valid, motiv):
    from core import coada_api as c
    assert c.respinge(conn, coada_id, str(valid), motiv, respins_de_id=valid, cabinet_id_apelant=cab)["ok"]


def _scenariu(conn, cab, asist, valid, tids):
    """Firma 1: d300 luna 1 generată de TREI ori (două înlocuiri), nedecisă; d300 luna 2 respinsă de om („lipsește F1A5”).
    Firma 2: d300 luna 3 respinsă de om („data greșită”). Deci: 3 pregătiri, 2 respinse (de om), 0 înlocuiri numărate."""
    t1, t2 = tids
    v = _declaratie(conn, cab, t1, asist, 1)
    v = _genereaza_din_nou(conn, cab, t1, asist, v, 1)
    _genereaza_din_nou(conn, cab, t1, asist, v, 1)
    _respinge(conn, cab, _declaratie(conn, cab, t1, asist, 2), valid, "lipsește F1A5")
    _respinge(conn, cab, _declaratie(conn, cab, t2, asist, 3), valid, "data greșită")


def test_t2_capacitate_inlocuirea_nu_e_respingere(tx):
    """ROȘU înainte: pregătirea generată din nou de două ori era „respinsă” (bool_or pe `respins_la`) -> 3 respinse din 3 -> 0% acceptate.
    Acum 2 din 3 respinse -> 33%. MUTAȚIA: `sql_inlocuita` -> `FALSE` -> 0 -> pică."""
    from core import capacitate_api
    conn, cab, asist, valid, tids, _azi = tx
    _scenariu(conn, cab, asist, valid, tids)
    a = next(x for x in capacitate_api.capacitate(conn, cab)["asistenti"] if x["id"] == asist)
    assert a["pregatite_luna"] == 3, a                                   # o pregătire pe declarație, oricâte generări
    assert a["in_lucru"] == 1, a                                          # numai ultima generare a lunii 1 e activă
    assert a["pct_acceptate"] == 33, a                                    # (3 − 2) / 3; cu înlocuirile numărate ar fi 0


def test_t2_sinteza_zilnica_inlocuirea_nu_e_respingere(tx):
    """ROȘU înainte: „respinse azi” = 3 (cele două înlocuiri ale lunii 1 se numărau, ca 18.10 / 19.10 pe cabinetul de test). Acum 2.
    MUTAȚIA: `sql_inlocuita` -> `FALSE` -> 3 -> pică."""
    from core import sinteza_zilnica
    conn, cab, asist, valid, tids, azi = tx
    d0 = sinteza_zilnica.sinteza_cabinet(conn, cab, azi)
    assert (d0["pregatite"], d0["respinse"]) == (0, 0), d0
    _scenariu(conn, cab, asist, valid, tids)
    d = sinteza_zilnica.sinteza_cabinet(conn, cab, azi)
    assert d["pregatite"] == 3, d
    assert d["respinse"] == 2, d
    assert d["de_validat"] == 1, d


def test_t2_sinteza_numai_inlocuiri_ziua_e_fara_respingeri(tx):
    """Ziua în care s-a generat doar din nou (fără nicio respingere a omului) are 0 respinse, nu „1 respinsă”. MUTAȚIA: `FALSE` -> pică."""
    from core import sinteza_zilnica
    conn, cab, asist, valid, tids, azi = tx
    v = _declaratie(conn, cab, tids[0], asist, 5)
    _genereaza_din_nou(conn, cab, tids[0], asist, v, 5)
    d = sinteza_zilnica.sinteza_cabinet(conn, cab, azi)
    assert (d["pregatite"], d["respinse"]) == (1, 0), d


def test_t2_tipare_inlocuirea_nu_e_motiv_si_totalurile_sunt_pregatiri(tx):
    """ROȘU înainte: motivul nr.1 = „Înlocuită de declarația generată din nou” (n=2); d300 total 5 rânduri, 4 „respinse”; firma 1 3 / 4.
    Acum: motivele numai ale omului, totalurile în PREGĂTIRI, iar Σ motive = Σ pe tipuri = Σ pe firme = `respinse` (aceeași listă).
    MUTAȚII: `sql_inlocuita` -> `FALSE` -> pică; cheia pregătirii -> `d.id` (rânduri) -> pică."""
    from core import tipare_api
    conn, cab, asist, valid, tids, _azi = tx
    _scenariu(conn, cab, asist, valid, tids)
    t = tipare_api.tipare(conn, cab)
    mot = {m["motiv"]: m["n"] for m in t["motive"]}
    assert mot == {"lipsește F1A5": 1, "data greșită": 1}, t["motive"]    # înlocuirea nu e un motiv de respingere
    assert t["tipuri"] == [{"tip": "d300", "total": 3, "respinse": 2, "pct": 67}], t["tipuri"]
    fir = {f["tenant_id"]: (f["respinse"], f["total"]) for f in t["firme"]}
    assert fir == {tids[0]: (1, 2), tids[1]: (1, 1)}, t["firme"]
    assert t["respinse"] == 2
    assert t["respinse"] == sum(m["n"] for m in t["motive"]) == sum(x["respinse"] for x in t["tipuri"]) \
        == sum(f["respinse"] for f in t["firme"])
    assert t["are_date"] is True


def test_t2_tipare_numai_inlocuiri_nu_are_date(tx):
    """Un cabinet care doar a generat din nou nu are „respingeri de analizat” (analiza AI nu pornește pe înlocuiri). MUTAȚIA: `FALSE` ->
    pică."""
    from core import tipare_api
    conn, cab, asist, valid, tids, _azi = tx
    v = _declaratie(conn, cab, tids[0], asist, 6)
    _genereaza_din_nou(conn, cab, tids[0], asist, v, 6)
    t = tipare_api.tipare(conn, cab)
    assert (t["motive"], t["firme"], t["respinse"], t["are_date"]) == ([], [], 0, False), t
    assert t["tipuri"] == [{"tip": "d300", "total": 1, "respinse": 0, "pct": 0}], t["tipuri"]


SCH = "efemer_lot11_t2"


@pytest.fixture()
def tx_note():
    """Ca `test_lot11_a458_erori_echipa.tx`: schema efemeră din `tenant_template.sql`, firma ei în cabinetul de test, totul ANULAT."""
    import io
    import os
    from core import tenant_provisioning as _tp
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
    cur.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s AND poate_valida AND id<>%s ORDER BY id LIMIT 1", (cab, asist))
    valid = cur.fetchone()[0]
    cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false, activ=true WHERE id=%s", (asist,))
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Lot 11 T2 Note SRL',%s) RETURNING id",
                (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
    try:
        yield conn, cur, tid, cab, asist, valid
    finally:
        conn.rollback()
        cur = conn.cursor()
        cur.execute("RESET iconta.utilizator")
        conn.commit()
        p.putconn(conn)


def test_t2_capacitate_cabinetul_numara_documente_nu_randuri(tx_note):
    """[clasa lui 458: „numerele nu se adună cu rândurile”] ROȘU înainte: o factură cu două note intrată la validare apărea pe Capacitate
    „2 de validat” / „2 în lucru” (rânduri de coadă), iar rândul asistentului și sinteza zilnică spuneau 1 (pregătiri). Acum 1 peste tot.
    MUTAȚIA: cheia pregătirii scoasă din secțiunea cabinetului (`COUNT(*)`) -> 2 -> pică."""
    from core import capacitate_api, coada_api as c, sinteza_zilnica
    import core.test_lot0710_p2 as _p2
    conn, cur, tid, cab, asist, valid = tx_note
    cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(asist),))
    cap0 = capacitate_api.capacitate(conn, cab)
    cur.execute("SELECT now()::date")
    azi = cur.fetchone()[0]
    sin0 = sinteza_zilnica.sinteza_cabinet(conn, cab, azi)["de_validat"]
    vechi_sch, _p2.SCH = _p2.SCH, SCH            # ajutorul celuilalt fișier scrie pe schema lui; aici, pe a noastră
    try:
        _fid, n1, n2 = _p2._factura_cu_doua_note(conn, cur)
    finally:
        _p2.SCH = vechi_sch
    puse = c.pune_notele_in_coada(conn, cab, tid, asist)
    cur.execute("SELECT COUNT(*) FROM public.declaratii_coada WHERE tenant_id=%s AND stare='la_senior'", (tid,))
    assert cur.fetchone()[0] == 2, puse                                   # două rânduri de coadă …
    cap = capacitate_api.capacitate(conn, cab)
    assert cap["cabinet"]["de_validat"] - cap0["cabinet"]["de_validat"] == 1, (cap0["cabinet"], cap["cabinet"])   # … un document
    assert cap["cabinet"]["in_lucru"] - cap0["cabinet"]["in_lucru"] == 1, (cap0["cabinet"], cap["cabinet"])
    a0 = next(x for x in cap0["asistenti"] if x["id"] == asist)
    a = next(x for x in cap["asistenti"] if x["id"] == asist)
    assert a["in_lucru"] - a0["in_lucru"] == 1                            # același număr ca rândul asistentului
    assert sinteza_zilnica.sinteza_cabinet(conn, cab, azi)["de_validat"] - sin0 == 1   # și ca emailul de seară


def test_t2_sql_inlocuita_sta_in_coada_api():
    """Definiția e una, în `coada_api` (lângă `sql_cheie_pregatire`); `asistenti_api` o importă, nu o redefinește."""
    from core import asistenti_api, coada_api
    assert asistenti_api.sql_inlocuita is coada_api.sql_inlocuita
