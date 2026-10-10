# -*- coding: utf-8 -*-
"""[08.10.2026, decizia Costin U2, verbatim în DECIZII] Control fiscal: luna preluării, „depusă în afara iConta”, „de urmărit” pe 30 de
zile, „nedeclarat”, cardul fără întârziere.

„Control fiscal: restanțele se numără doar de la luna de preluare a firmei în iConta. O declarație anterioară se poate marca
«depusă în afara iConta», cu recipisă opțională. Fără nicio declarație, mesajul e «nedeclarat», nu «diferă de contabilitate».
Declarațiile scadente în următoarele 30 de zile apar la «de urmărit» (acum arată 0, deși sunt 4 scadente pe 26.10). Cardul de pe
ecranul principal arată aceleași cifre ca fereastra, fără întârziere.”

MĂSURAT pe producție 08.10, înainte: F1 avea 32 de „restanțe” din ianuarie–august 2026 (firma adăugată în iConta pe 20.09) și 0 „de
urmărit”, deși D300/D112/D100 pe 09/2026 au termen 26.10.

Schemă efemeră; `public.declaratii_depuse` numai cu un tenant_id SINTETIC (990808), șters la ieșire.
"""
import datetime
import io
import os
import re

import pytest

from core import control_fiscal_api as cf
from core import control_incrucisat as ci
from core import db as _db
from core import tenant_provisioning as _tp
from core import uc_comun

SCH = "efemer_control_preluare"
TID = 990808
AZI = datetime.date(2026, 10, 8)
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


# ── pur ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_de_urmarit_inseamna_30_de_zile():
    # decizia Costin U2: „Declarațiile scadente în următoarele 30 de zile apar la «de urmărit»”
    assert cf.PRAG_URMARIT_ZILE == 30


def test_luna_preluarii_din_soldurile_de_preluare_sau_din_data_adaugarii():
    from core import luna_preluare as lp
    # decizia Costin U2: „restanțele se numără doar de la luna de preluare a firmei în iConta”
    assert lp.deduse(datetime.date(2026, 9, 20)) == (2026, 9)
    # soldurile sunt „la” data lor: evidența în iConta începe a doua zi
    assert lp.deduse(datetime.date(2026, 9, 20), datetime.date(2026, 6, 30)) == (2026, 7)
    assert lp.deduse(None, datetime.date(2026, 8, 31)) == (2026, 9)
    assert lp.deduse(None) is None


def test_propunerea_nu_trece_de_prima_nota_si_luna_salvata_castiga():
    """[08.10 §6 pct.4] „cu valoarea dedusă ca propunere, dar niciodată după luna primei note. Recalculează propunerea pentru F3 (are
    note din iunie).” F3: adăugată în octombrie, prima notă în iunie -> 06/2026. Luna salvată în Date firmă e cea efectivă; una după
    prima notă se refuză. MUTAȚIE: `min(d, p)` -> `d` în `propunere` -> F3 rămâne 10/2026 -> pică."""
    from core import luna_preluare as lp
    f3 = dict(creat_la=datetime.date(2026, 10, 2), data_solduri=None, prima_nota=datetime.date(2026, 6, 15))
    assert lp.propunere(**f3) == (2026, 6)
    assert lp.efectiva(None, **f3) == (2026, 6)
    assert lp.efectiva(datetime.date(2026, 4, 1), **f3) == (2026, 4)
    assert lp.eroare(datetime.date(2026, 6, 1), f3["prima_nota"]) is None
    assert lp.eroare(datetime.date(2026, 7, 1), f3["prima_nota"]) is not None           # 07/2026 e după prima notă
    assert lp.propunere(datetime.date(2026, 10, 2)) == (2026, 10)                      # fără note: dedusa
    assert lp.din_text("2026-06") == datetime.date(2026, 6, 1) and lp.din_text("") is None


def test_perioadele_dinaintea_preluarii_nu_sunt_restante():
    d = lambda tip, an, luna, term: {"tip": tip, "an": an, "luna": luna, "termen": term, "perioada": "", "motiv": ""}
    lipsa = [d("d300", 2026, 8, "2026-09-25"), d("d101", 2025, 12, "2026-06-25"), d("d300", 2026, 9, "2026-10-26")]
    urmarit = [d("d100", 2026, 9, "2026-10-26")]   # trimestrul III cuprinde luna preluării: SE numără
    l, u, inainte = cf.separa_inainte_de_preluare(lipsa, urmarit, (2026, 9))
    assert [(x["tip"], x["luna"]) for x in l] == [("d300", 9)]
    assert [(x["tip"], x["luna"]) for x in u] == [("d100", 9)]
    assert sorted((x["tip"], x["an"]) for x in inainte) == [("d101", 2025), ("d300", 2026)]
    # [deficiența 212, retestul Costin 09.10: „text … repetat pe fiecare rând”] explicația stă o dată, sub titlul grupului (ecranul);
    # rândul își păstrează doar faptul lui (aici: niciunul)
    assert {x["motiv"] for x in inainte} == {""}
    assert cf.separa_inainte_de_preluare(lipsa, urmarit, None)[2] == []


def test_fara_declaratie_depusa_mesajul_e_nedeclarat():
    # decizia Costin U2: „Fără nicio declarație, mesajul e «nedeclarat», nu «diferă de contabilitate».”
    assert ci.declara("D300", "depus") == "D300 declară"
    assert ci.declara("D300", "regenerat") == "D300 nedeclarat (generat azi) ar avea"
    rand = ci.compara_tva({"R17_2": 1180, "R27_2": 0}, {"4427": {"credit": 1180}, "4426": {"debit": 241.5}}, 2026, 10,
                          sursa_declarat="regenerat")
    rosu = [c for c in rand if c["stare"] == "rosu"]
    # mesajul ÎNTREG, cu verbul declarației nedepuse (nu „D300 declară”)
    assert [c["mesaj"] for c in rosu] == ["TVA deductibilă: D300 nedeclarat (generat azi) ar avea 0,00 lei, contul 4426 are 241,50 lei "
                                          "(diferență -241,50 lei)."]
    assert uc_comun.eticheta_incrucisat("tva_incrucisat", rosu[0]) == "TVA nedeclarat"
    assert uc_comun.eticheta_incrucisat("tva_incrucisat", dict(rosu[0], sursa_declarat="depus")) == \
        "TVA declarat diferă de contabilitate"
    assert uc_comun.eticheta_incrucisat("cota_tva_conformitate", {}) == "Facturi emise cu cotă TVA greșită pentru perioadă"
    d390 = ci.compara_d390({"L": 500, "A": 0}, {"emisa": [], "primita": []})
    assert d390 and {c["sursa_declarat"] for c in d390} == {"regenerat"}         # D390 nu se persistă la depunere
    assert ci.declara("D390", ci.SURSA_D390) == "D390 nedeclarat (generat azi) ar avea"


def test_etichetele_filtrate_pe_ecran_sunt_exact_cele_de_pe_server():
    """`control_verdict.js` filtrează din «Verificări contabile» etichetele care stau deja în «Declarație vs contabilitate»; o
    etichetă nouă pe server, nefiltrată pe ecran, ar apărea de două ori."""
    js = io.open(os.path.join(_RAD, "static/js/ecrane/control_verdict.js"), encoding="utf-8").read()
    lista = re.search(r"const DEJA_IN_INCRUCISAT = \[(.*?)\];", js, re.S).group(1)
    pe_ecran = set(re.findall(r'"([^"]+)"', lista))
    pe_server = {e for perechi in uc_comun.ETICHETE_INCRUCISAT.values() for e in perechi}
    assert pe_ecran == pe_server, (pe_ecran ^ pe_server)


# ── pe bază: fereastra firmei și marcarea „depusă în afara iConta” ─────────────────────────────────────────────────────────────
@pytest.fixture()
def firma():
    sablon = io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(sablon, SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, tip_decont, regim_fiscal, tip_firma, "
                        "platitor_tva_anaf_inceput) VALUES (1, 'PRELUARE SRL', '14399840', true, 'L', 'profit', 'srl', '2020-01-01')" % SCH)
            cur.execute("INSERT INTO %s.solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                        "('5311', 'Casa', 100, 0, '2026-08-31'), ('1012', 'Capital', 0, 100, '2026-08-31')" % SCH)
            cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s", (TID,))
        c.commit()
    try:
        yield
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s", (TID,))
                # contorul pe care `marcheaza_sursa_publica` îl ridică la scrierea în declaratii_depuse: altfel rămâne un rând
                # care trimite la o firmă inexistentă (gardul de sesiune din `conftest.py`)
                cur.execute("DELETE FROM public.firma_sursa_versiune WHERE tenant_id = %s", (TID,))
                cur.execute("DELETE FROM public.supervizor_sursa WHERE tenant_id = %s", (TID,))
            c.commit()


def _evalueaza():
    with _db.get_conn(SCH) as cs, _db.get_conn() as cp:
        r = cf.evalueaza_firma(cs, cp, TID, SCH, AZI, cu_reconciliere=False)
        cs.rollback()
        cp.rollback()
    return r


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fereastra_firmei_numara_de_la_preluare_si_vede_30_de_zile(firma):
    r = _evalueaza()
    assert r["luna_preluare"] == "09/2026"
    cheie = lambda lst: {(x["tip"], x["luna"]) for x in lst}
    assert ("d300", 8) in cheie(r["inainte_de_preluare"]) and ("d300", 8) not in cheie(r["lipsa"])
    assert not [x for x in r["lipsa"] if (x["an"], x["luna"]) < (2026, 9)]
    assert ("d300", 9) in cheie(r["urmarit"])        # termen 26.10, la 18 zile: „de urmărit”
    assert r["stare"] != "rosu"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_marcata_depusa_in_afara_iconta_iese_la_zi_cu_recipisa(firma, monkeypatch):
    from core import erori, uc_control_fiscal as ucf
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCH)
    ctx = {"uid": 1, "firm": 1}
    with pytest.raises(erori.DateInvalide):           # fără dată: „la termen / după termen” ar fi o presupunere
        ucf.control_fiscal_depusa_extern(TID, {"tip": "d300", "an": 2026, "luna": 8, "data_depunere": ""}, ctx)
    r = ucf.control_fiscal_depusa_extern(TID, {"tip": "D300", "an": 2026, "luna": 8, "data_depunere": "2026-09-24",
                                               "recipisa": "INTERNT-123"}, ctx)
    assert r["ok"] and r["tip"] == "d300"
    # [retest 08.10 pct.10] „marcarea nu se poate modifica” — acum se poate: o marcare nouă peste o MARCARE e o versiune nouă
    # (peste o depunere prin iConta.eu rămâne refuz 409: core/test_retest_0810_s6.py::test_pct10_…)
    ucf.control_fiscal_depusa_extern(TID, {"tip": "d300", "an": 2026, "luna": 8, "data_depunere": "2026-09-24",
                                           "recipisa": "INTERNT-124"}, ctx)
    ev = _evalueaza()
    la_zi = [x for x in ev["confirmate"] if (x["tip"], x["luna"]) == ("d300", 8)]
    assert la_zi and la_zi[0]["extern"]
    assert la_zi[0]["motiv"] == "Depusă în afara iConta.eu 24.09.2026 la termen · recipisă INTERNT-124"
    assert ("d300", 8) not in {(x["tip"], x["luna"]) for x in ev["inainte_de_preluare"]}


def test_cardul_nu_asteapta_tura_de_5_minute(monkeypatch):
    """„Cardul … arată aceleași cifre ca fereastra, fără întârziere.” După o scriere reușită, lotul pornește imediat, în fundal; o
    a doua scriere în timpul lui cere încă o trecere, nu un al doilea fir. Citirea portofoliului rămâne o interogare (P2)."""
    import threading
    from core import firma_rezumat as fr
    monkeypatch.setenv("ICONTA_RECALCUL_FUNDAL", "1")
    porniri, gata, tine = [], threading.Event(), threading.Event()

    def lot(*a, **k):
        porniri.append(1)
        if len(porniri) == 1:
            tine.wait(5)
        else:
            gata.set()
    monkeypatch.setattr(fr, "recalculeaza_lot", lot)
    assert fr.recalculeaza_in_fundal() is True
    assert fr.recalculeaza_in_fundal() is False       # în timpul rulării: încă o trecere, nu un fir nou
    tine.set()
    assert gata.wait(5) and len(porniri) == 2
    monkeypatch.setenv("ICONTA_RECALCUL_FUNDAL", "0")
    assert fr.recalculeaza_in_fundal() is False
    # și e legată de cererile de modificare (middleware-ul din main.py)
    import ast
    arb = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    mw = next(n for n in ast.walk(arb) if isinstance(n, ast.AsyncFunctionDef) and n.name == "_autor_si_note_in_coada")
    chemate = {x.func.attr for x in ast.walk(mw) if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)}
    assert {"recalculeaza_in_fundal"} <= chemate
