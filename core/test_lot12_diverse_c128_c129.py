# -*- coding: utf-8 -*-
"""[lotul 12, pachetul diverse] C128 și C129 — refuzurile numite, pe drumul use-case-ului.

C128 — achiziția intracomunitară din Operațiuni accepta un furnizor cu cod de TVA românesc („RO” e în `intracomunitar.TARI_UE`, lista
statelor membre — corect ca listă), fără refuzul pe care îl are livrarea (`valideaza_lic`): o cumpărare internă intra ca achiziție
intracomunitară (taxare inversă pe notă, D390). Temei: CF art.273 alin.(1) „Se consideră achiziție intracomunitară de bunuri obținerea
dreptului de a dispune, ca și un proprietar, de bunuri mobile corporale expediate sau transportate […] către un stat membru, altul decât
cel de plecare a transportului sau de expediere a bunurilor.”; CF art.307 alin.(2) — beneficiarul datorează taxa pentru serviciile
„furnizate de către o persoană impozabilă care nu este stabilită pe teritoriul României”. Clasa (căutat: `grep -rn "desparte_cod_tva\\|TARI_UE"
core main.py`): livrarea (`valideaza_lic`, `valideaza_prestare_ic`) și emiterea (`categorii_tva.verifica_linii`, livrare_ic) refuzau deja
RO; linia manuală D390 (`d390_clasificare_api`) folosește `d390.TARI_UE`, fără RO; singura intrare fără refuz era `achizitie_ic`.

C129 — o fișă din registru cu contul de imobilizare gol (importul registrului îl păstrează gol, „neclasificat”) dădea la reevaluare o notă
fără contul activului („ = 105”, „2813 = ”). Clasa — notele scrise din conturile fișei: reevaluarea, casarea din registru (Inventariere),
amortizarea lunii (cădea tăcut pe 2813). Toate iau acum conturile prin `amortizare_lunii.conturile_fisei`: fără cont, refuz numit, nicio notă.
Temei: N/A — integritatea notei (un rând de notă fără cont nu e o înregistrare), nu o valoare fiscală.
"""
import pytest

from core import amortizare_lunii as mfr, erori, intracomunitar as ic


# ── C128 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c128_achizitia_ic_refuza_furnizorul_din_romania():
    """CF art.273 alin.(1) / art.307 alin.(2): furnizorul AIC e dintr-un ALT stat membru. MUTAȚIE: în `valideaza_aic` `tara == "RO"` ->
    `tara == "XX"` -> „RO14399840” trece -> pică."""
    with pytest.raises(ValueError) as e:
        ic.valideaza_aic("RO14399840")   # DANTE INTERNATIONAL SA — CUI cu cifra de control verificată (CLAUDE.md „Date de test”)
    assert str(e.value) == ic.MESAJ_AIC_RO and ic.MESAJ_AIC_RO.split(": ", 1)[1].startswith(
        "cumpărarea de la el nu e achiziție intracomunitară "), e.value
    assert ic.valideaza_aic("DE123456789") == ("DE", "123456789")
    assert ic.valideaza_aic("GR123456789") == ("EL", "123456789")   # Grecia pe VIES = EL (`desparte_cod_tva`)


def test_def_c128_ruta_refuza_pe_campul_codului_inainte_de_orice_scriere(monkeypatch):
    """Use-case-ul (`uc_tenants.achizitie_ic`): refuzul stă pe câmpul `op-cod_tva_furnizor`, cu `MESAJ_AIC_RO`, ridicat ÎNAINTE de
    scrieri (nicio factură, nicio notă). MUTAȚIE: ramura `else: … valideaza_aic` scoasă -> nu se refuză pe câmp -> pică."""
    import contextlib
    from core import uc_tenants as ut

    class _Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, *a, **k):
            raise AssertionError("achiziția a ajuns la o scriere în bază: %r" % (a[:1],))

    class _Conn:
        def cursor(self, **k):
            return _Cur()

    @contextlib.contextmanager
    def _get_conn(schema=None):
        yield _Conn()

    monkeypatch.setattr(ut.db, "get_conn", _get_conn)
    monkeypatch.setattr(ut.auth_api, "schema_tenant", lambda conn, uid, tid: "tenant_proba")
    monkeypatch.setattr(ut._uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
    corp = {"data": "2099-03-10", "valoare": 1000, "cota": 21, "cod_tva_furnizor": "RO14399840", "numar": "F-1", "tip": "bunuri",
            "cont_destinatie": "371"}
    with pytest.raises(erori.DateInvalide) as e:
        ut.achizitie_ic(1, corp, {"uid": 1})
    campuri = {c["camp"]: c["mesaj"] for c in e.value.detaliu["erori_campuri"]}
    assert campuri.get("op-cod_tva_furnizor") == ic.MESAJ_AIC_RO, e.value.detaliu


# ── C129 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c129_fisa_fara_cont_de_imobilizare_nu_scrie_nota():
    """Contul gol (sau numai spații) -> refuz numit, cu mijlocul fix și locul unde se completează; contul de amortizare se cere numai unde
    nota îl scrie. MUTAȚIE: în `conturile_fisei` `if lipsa:` -> `if False:` -> („”, „2813”) întors -> pică."""
    with pytest.raises(ValueError) as e:
        mfr.conturile_fisei("Excavator", "  ", "2813")
    refuz = "Mijlocul fix Excavator nu are %s în registru, deci nota n-ar avea contul. Completează ce lipsește din %s, apoi reia operația."
    m = str(e.value)
    assert m == refuz % ("contul de imobilizare", mfr.UNDE_SE_COMPLETEAZA), m   # mijlocul fix, contul care lipsește, locul completării
    with pytest.raises(ValueError) as e:
        mfr.conturile_fisei("Excavator", None, None)
    m = str(e.value)
    assert m == refuz % ("contul de imobilizare și contul de amortizare", mfr.UNDE_SE_COMPLETEAZA), m
    assert mfr.conturile_fisei("Excavator", " 2131 ", "2813") == ("2131", "2813")
    assert mfr.conturile_fisei("Excavator", "2131", "", cu_amortizare=False) == ("2131", "")   # nimic amortizat: 28xx nu apare pe notă
    assert mfr.conturile_fisei("Excavator", "", "2813", cu_imobilizare=False) == ("", "2813")  # amortizarea lunii: 6811 = 28xx


def test_def_c129_toate_notele_din_fisa_trec_prin_conturile_fisei():
    """Garda clasei: reevaluarea, casarea din registru și amortizarea lunii iau conturile fișei prin `conturile_fisei`; `amortizare_lunii`
    nu mai pune 2813 tăcut. Un drum nou care citește fișa (`pentru_reevaluare` / `pentru_inventariere` / `de_amortizat`) fără ea pică."""
    import ast
    import io
    import os
    import re
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def apel(n, obiect, nume):
        return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == nume
                and isinstance(n.func.value, ast.Name) and n.func.value.id == obiect)
    # pe ARBORE: fiecare cititor al fișei e chemat într-un singur loc din `uc_tenants`, iar funcția care îl cheamă ia conturile prin
    # `_amc.conturile_fisei(den, ci, ca, …)`
    uc = ast.parse(io.open(os.path.join(rad, "core", "uc_tenants.py"), encoding="utf-8").read())
    for cititor in ("pentru_reevaluare", "pentru_inventariere"):
        gazde = [f for f in uc.body if isinstance(f, ast.FunctionDef) and any(apel(n, "repo_mijloace_fixe", cititor) for n in ast.walk(f))]
        chemari = [n for n in ast.walk(uc) if apel(n, "repo_mijloace_fixe", cititor)]
        conturi = [[ast.unparse(a) for a in n.args[:3]] for f in gazde for n in ast.walk(f) if apel(n, "_amc", "conturile_fisei")]
        assert (len(chemari), len(gazde), conturi) == (1, 1, [["den", "ci", "ca"]]), \
            "%s: conturile fișei nu trec prin `conturile_fisei` (%s)" % (cititor, [(f.name, conturi) for f in gazde])
    al = ast.parse(io.open(os.path.join(rad, "core", "amortizare_lunii.py"), encoding="utf-8").read())
    atribuiri = [ast.unparse(n) for n in ast.walk(al) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                 and getattr(n.value.func, "id", None) == "conturile_fisei"]
    assert atribuiri == ["_ci, cont_am = conturile_fisei(den, cont_imob, cont_am, cu_imobilizare=False)"], atribuiri
    assert not re.search(r"cont_am or \"2813\"", io.open(os.path.join(rad, "core", "amortizare_lunii.py"), encoding="utf-8").read()), \
        "amortizarea lunii pune din nou 2813 tăcut pe o fișă fără cont"


def test_def_c129_reevaluarea_refuza_fisa_fara_cont(monkeypatch):
    """Use-case-ul reevaluării pe o fișă cu contul de imobilizare gol: refuz numit (`DateInvalide`), nicio notă. MUTAȚIE: apelul
    `_amc.conturile_fisei` din reevaluare scos -> nota se scrie cu contul gol -> pică."""
    import contextlib
    from core import uc_tenants as ut
    scrieri = []

    class _Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, *a, **k):
            scrieri.append(a[:1])

    class _Conn:
        def cursor(self, **k):
            return _Cur()

    @contextlib.contextmanager
    def _get_conn(schema=None):
        yield _Conn()

    import datetime as _dt
    fisa = ("Excavator", "", "2813", 12000, 0, 60, _dt.date(2026, 1, 10), "liniara", [], False, None, None)
    monkeypatch.setattr(ut.db, "get_conn", _get_conn)
    monkeypatch.setattr(ut.auth_api, "schema_tenant", lambda conn, uid, tid: "tenant_proba")
    monkeypatch.setattr(ut._uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
    monkeypatch.setattr(ut.repo_mijloace_fixe, "pentru_reevaluare", lambda cur, schema, mid: fisa)
    monkeypatch.setattr(ut, "_cere_amortizarea_inregistrata", lambda *a, **k: None)
    monkeypatch.setattr(ut.repo_contabilitate, "nota_operatiune_ciorna",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("s-a scris nota reevaluării cu contul gol")))
    with pytest.raises(erori.DateInvalide) as e:
        ut.reevaluare_imobilizare(1, {"operatie": "reevaluare", "mijloc_fix_id": 7, "data": "2026-09-30", "valoare_justa": 15000,
                                      "sold_105_activ": 0, "pierdere_655_anterioara": 0}, {"uid": 1})
    with pytest.raises(ValueError) as refuzul_fisei:   # nimic amortizat (fișa are 0): se cere numai contul activului
        mfr.conturile_fisei("Excavator", "", "2813", cu_amortizare=False)
    assert e.value.detaliu == str(refuzul_fisei.value), e.value.detaliu   # refuzul numit al fișei ajunge întreg la contabil
