# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.1, pachetul `ctrl` — deficiența 484 (grav): „Control încrucișat: confruntarea declarații–contabilitate nu
rulează”.

CE ERA. Toate confruntările declarație–evidență din Control fiscal rulau pe LUNA ÎN CURS (`azi.year, azi.month`): pe 23.10 se
confrunta un D300 pe 10/2026 — care nu există încă — cu o evidență pe jumătate, deci „TVA colectată: D300 și contul 4427 coincid”
pe 0 cu 0, pe orice firmă. Luna care chiar se declară (09/2026, termen 25.10) nu se confrunta nicăieri pe ecran. În plus:
  * reconcilierea fiecărei declarații datorate cu documentele perioadei (`control_incrucisat.reconciliaza_declaratii`: D300, D394, D390,
    D301, D112, D406, D100, D101, D205) se calcula în `evalueaza_firma` și NU se arăta deloc;
  * alertele zilnice (`alerte_control_fiscal.ruleaza`) și supervizorul (cronul de 08:00, ecranul) tot pe luna în curs;
  * lucrătorul supervizorului (`supervizor_cache.recalculeaza_lot`) nu era chemat de nimeni: ecranul Supervizor arăta la fiecare firmă
    „rezultatul nu a fost calculat încă”;
  * detaliul Control fiscal înghițea orice eroare a verificărilor (`except Exception: pass`).

CE E ACUM. O singură sursă a perioadei — `control_fiscal_api.luna_confruntata` (ultima lună încheiată) —, folosită de toți cei care
confruntă; ecranul spune luna confruntată și arată reconcilierea pe declarații; lucrătorul supervizorului rulează în tura de 5 minute a
modelului de portofoliu; eroarea verificărilor devine constatare vizibilă.

Temei (perioada declarației care se confruntă): CF art.323 alin.(1) — decontul de taxă se depune „până la data de 25 inclusiv a lunii
următoare celei în care se încheie perioada fiscală respectivă”; termenele din aplicație vin din `core/scadente.py`. Schema efemeră e
COMISĂ (verificatorii își deschid singuri conexiunile) și ștearsă la final; perioadă sintetică nu se poate folosi aici, fiindcă testul
e chiar despre „luna încheiată față de luna zilei” — de aceea ziua e dată explicit (`azi` = 23.10.2026), nu luată din ceas.
"""
import collections
import datetime
import signal

import pytest

from core import db as _db, tenant_provisioning as _tp
from core import control_fiscal_api as _cf

SCH = "ztest_l12c_484"
AZI = datetime.date(2026, 10, 23)
CUI = "14399840"   # DANTE INTERNATIONAL SA — cifra de control verificată cu algoritmul din CLAUDE.md


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def test_luna_confruntata_e_ultima_luna_incheiata():
    # CF art.323 alin.(1): pe 23.10 se depune decontul lunii 09 — aceea se confruntă, nu 10 (neîncheiată)
    assert _cf.luna_confruntata(2026, 10) == (2026, 9)
    assert _cf.luna_confruntata(2027, 1) == (2026, 12)   # în ianuarie, decembrie anului trecut


@pytest.fixture()
def firma_cu_septembrie():
    """SRL micro plătitor de TVA lunar, cu O factură emisă pe 10.09.2026 (1.000 + TVA 21% = 210), contabilizată și VALIDATĂ
    (4111 = 707 1.000, 4111 = 4427 210). Octombrie n-are nimic."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
        cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
        cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,tip_firma,
             regim_fiscal,declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'ZTEST L12 484 SRL',%s,'Str 1','Buc','B','4719',
             'Banca Test','RO49AAAA1B31007593840000','lunar',true,'srl','micro','Ada','Ada','ADMINISTRATOR')""", (CUI,))
        cur.execute("""INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status)
            VALUES ('L12-484','2026-09-10','emisa',1210,210,%s,'CLIENT SRL','emisa') RETURNING id""", ("RO" + CUI,))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id,descriere,cantitate,pret_unitar,cota_tva) VALUES (%s,'marfa',1,1000,21)",
                    (fid,))
        cur.execute("INSERT INTO inregistrari (data, descriere, status, factura_id) VALUES ('2026-09-10','Factura L12-484','validata',%s) "
                    "RETURNING id", (fid,))
        nid = cur.fetchone()[0]
        for deb, cre, suma in (("4111", "707", 1000), ("4111", "4427", 210)):
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                        (nid, deb, cre, suma))
        c.commit()
    try:
        yield SCH
    finally:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


def test_declaratie_vs_contabilitate_confrunta_luna_incheiata(firma_cu_septembrie):
    """Ziua 23.10.2026: «Declarație vs contabilitate» confruntă 09/2026 — TVA colectată declarată 210,00 (factura din 10.09), nu 0 —,
    iar reconcilierea pe declarații (arătată acum pe ecran) e pe aceeași lună, cu numele fiecărei declarații."""
    from core import uc_comun
    contabil, vc = uc_comun._construieste_contabil(SCH, 987654, {"uid": None}, AZI.year, AZI.month, None)
    tva = vc["tva_incrucisat"]
    assert (tva["an"], tva["luna"]) == (2026, 9), (tva.get("an"), tva.get("luna"))
    colectata = next(c for c in tva["constatari"] if c.get("eticheta") == "TVA colectată")
    # CF art.281 (fapt generator la livrare) + art.323 alin.(1): decontul lunii 09 cuprinde factura din 10.09 — 210,00 lei TVA
    assert colectata["declarat"] == 210 and colectata["contabil"] == 210, colectata
    assert colectata["stare"] == "verde", colectata
    with _db.get_conn(SCH) as cs, _db.get_conn() as cp:
        r = _cf.evalueaza_firma(cs, cp, 987654, SCH, AZI)
    rec = r["reconciliere_surse"]
    assert (rec["an"], rec["luna"]) == (2026, 9), rec
    d300 = next(c for c in rec["constatari"] if c.get("declaratie") == "d300")
    assert d300["eticheta"] == "D300 (decont TVA)" and d300["stare"] == "verde", d300
    # faptul confirmat (`_c_verde`: recalculul din sursă confirmă declarația), pe luna confruntată — pe structura afirmației, nu pe frază
    assert (d300["fel"], d300["tip"], d300["an"], d300["luna"]) == ("fapt", "d300", 2026, 9), d300


def test_alertele_zilnice_confrunta_luna_incheiata(monkeypatch):
    """Cronul de alerte (08:00) rulează verificatorii pe luna confruntată, nu pe luna zilei."""
    from core import alerte_control_fiscal as A
    vazut = []

    class _Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, *a):
            pass

        def fetchall(self):
            return [(1, "Firma probă", "tenant_1", 7)]

    class _Conn(_Cur):
        def cursor(self):
            return _Cur()

    class _Db:
        @staticmethod
        def get_conn(*a):
            return _Conn()

    monkeypatch.setattr(A, "db", _Db)
    monkeypatch.setattr(A, "emite_pentru_firma", lambda tid, nume, schema, cab, an, luna: vazut.append((an, luna)) or
                        {"rosii": 0, "notificat": False})
    A.ruleaza(azi=AZI)
    assert vazut == [(2026, 9)], vazut


def test_supervizorul_calculeaza_si_citeste_luna_incheiata(monkeypatch):
    """Ecranul Supervizor citește rezultatul lunii confruntate, iar lucrătorul de 5 minute (`firma_rezumat.main`) chiar îl calculează
    pe aceeași lună. Înainte, `supervizor_cache.recalculeaza_lot` nu era chemat de nimeni."""
    from core import uc_supervizor, supervizor_cache, firma_rezumat, cron, common
    citit, calculat = [], []
    monkeypatch.setattr(uc_supervizor, "azi_ro", lambda: datetime.date(2027, 1, 15))
    monkeypatch.setattr(uc_supervizor.auth_api, "tenantii_userului", lambda conn, uid: [])
    monkeypatch.setattr(supervizor_cache, "citeste", lambda conn, ids, an, luna: citit.append((an, luna)) or {})
    if _db_ok():
        r = uc_supervizor.supervizor_la_cerere({"uid": 1})
        assert citit == [(2026, 12)] and (r["an"], r["luna"]) == (2026, 12), (citit, r.get("an"), r.get("luna"))
    monkeypatch.setattr(firma_rezumat, "recalculeaza_lot", lambda **k: collections.defaultdict(int))
    monkeypatch.setattr(cron, "bate", lambda nume: None)
    monkeypatch.setattr(common, "azi_ro", lambda: AZI)
    monkeypatch.setattr(supervizor_cache, "recalculeaza_lot",
                        lambda an, luna: calculat.append((an, luna)) or {"invalidate": 0, "recalculate": 0, "fara_firma": []})
    vechi = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        assert firma_rezumat.main() == 0
    finally:
        for s, h in vechi.items():
            signal.signal(s, h)
    assert calculat == [(2026, 9)], calculat


def test_detaliul_nu_inghite_eroarea_verificarilor(monkeypatch):
    """O eroare a verificărilor contabile nu mai lasă fereastra fără niciun cuvânt: devine constatarea gri „Verificări contabile —
    eșuate”, cu eroarea în temei."""
    from core import uc_control_fiscal as U

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(U._uc_comun, "_schema_sau_404", lambda ctx, tid: "tenant_1")
    monkeypatch.setattr(U.db, "get_conn", lambda *a: _Ctx())
    monkeypatch.setattr(U.control_fiscal_api, "evalueaza_firma", lambda *a, **k: {"stare": "verde", "regim_tva_anaf": None})

    eroare = RuntimeError("probă 484")

    def _crapa(*a, **k):
        raise eroare
    monkeypatch.setattr(U._uc_comun, "_construieste_contabil", _crapa)
    construita, esuata = [], U._uc_comun._constatare_esuata
    monkeypatch.setattr(U._uc_comun, "_constatare_esuata",
                        lambda eticheta, nume, e, an, luna: construita.append((e, esuata(eticheta, nume, e, an, luna))) or construita[-1][1])
    r = U.control_fiscal_detaliu(1, {"uid": 1})
    assert [c["eticheta"] for c in r.get("contabil") or []] == ["Verificări contabile — eșuate"], r
    # chiar eroarea verificărilor (același obiect) ajunge în constatarea gri, iar constatarea e cea arătată în fereastră
    assert len(construita) == 1 and construita[0][0] is eroare and r["contabil"] == [construita[0][1]], (construita, r["contabil"])


def test_textele_reconcilierii_sunt_in_limba_contabilului():
    """Rândurile reconcilierii ajung acum pe ecran: fără nume de funcții / fișiere, cu diacritice, cu rândul din formular și cu
    salariatul numit."""
    from core import control_incrucisat as ci
    rupt = ci._c_rupt("d300", "D300 (decont TVA)", TypeError("x"))
    vizibil = " ".join([rupt["eticheta"], rupt["mesaj"], rupt["temei"], rupt["remediu"]["cauza"], rupt["remediu"]["actiune"]])
    assert rupt["eticheta"] == "D300 (decont TVA) — verificare întreruptă", rupt["eticheta"]
    for interzis in ("core/", ".py", "reconciliaza", "D300 mort", "INTRERUPTA", "semnătur"):
        assert interzis not in vizibil, (interzis, vizibil)
    d300 = ci._descrie_div({"rand": "R17_2", "eticheta": "TVA colectată", "generator": 310, "cale2": 210})
    # propoziția întreagă e lucrul verificat (textul care ajunge pe ecran): rândul din formular, ambele cifre, diferența
    assert d300 == ("rândul 19, coloana TVA (TVA colectată): declarația generată are 310,00 lei, recalculul din documente 210,00 lei "
                    "(diferența 100,00 lei)."), d300
    d112 = ci._descrie_div({"salariat": 5, "cine": "Popescu Ion", "camp": "cas", "generator": 1250, "cale2": 1240})
    assert d112.startswith("salariatul Popescu Ion, CAS: declarația generată are 1.250,00 lei"), d112
    assert " declarat " not in d300 + d112, (d300, d112)   # [123] fără declarație depusă nu se spune „declarat”
