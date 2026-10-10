# -*- coding: utf-8 -*-
"""Lotul „Retestul plasei” (comanda Costin 09.10.2026, verbatim în DECIZII) — probele fără browser ale reparațiilor din lot."""
import datetime

import pytest


@pytest.mark.parametrize("ruta,ce", [("salarii_contare_scrie", "Salariile lunii"), ("tenant_amortizare", "Amortizarea lunii")])
def test_216_nota_lunii_se_scrie_dupa_ce_luna_se_incheie(monkeypatch, ruta, ce):
    """[deficiența 216: „Note de salarii contate pe luni neîncheiate (F5 10/2026 ciornă, 11/2026 validată)”] Pe 09.10.2026, salariile
    și amortizarea lui 10/2026 și 11/2026 se refuză înaintea oricărei scrieri; 09/2026 trece de poartă (aici: până la schema, absentă).
    Regula e a închiderii lunii (decizia Costin 08.10.2026 pct.11, `inchidere_luna.luna_in_curs`). MUTAȚIE: poarta scoasă -> pică."""
    from core import common, erori, uc_comun, uc_tenants
    monkeypatch.setattr(common, "azi_ro", lambda: datetime.date(2026, 10, 9))

    class _Oprit(Exception):
        pass

    def _schema(*a, **k):
        raise _Oprit()
    monkeypatch.setattr(uc_comun, "_schema_cabinet_sau_404", _schema)
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", _schema)
    for luna in (10, 11):
        with pytest.raises(erori.CerereGresita, match="%s %02d/2026 se contează după ce luna se încheie" % (ce, luna)):
            getattr(uc_tenants, ruta)(1, 2026, luna, {"uid": 1})
    with pytest.raises(_Oprit):
        getattr(uc_tenants, ruta)(1, 2026, 9, {"uid": 1})


def test_9_directorul_bonurilor_are_o_singura_sursa_si_e_refuzat_in_afara_testului(tmp_path, monkeypatch):
    """[deficiența 9 + comanda Costin 09.10.2026 pct.7: „director separat pentru bonuri”] Calea pozelor bonurilor stă într-un singur loc
    (`common.dir_bonuri`, era scrisă de patru ori); plasa o mută prin `ICONTA_BON_DIR`, pe care un mediu nedovedit de test o refuză.
    MUTAȚIE: a doua definiție a căii pusă la loc -> pică; refuzul scos -> pică."""
    import ast
    import glob
    import io
    from core import common

    def scrie_calea(f):   # o constantă de șir din cod (nu comentariu, nu docstring de modul) care numește directorul pozelor
        arb = ast.parse(io.open(f, encoding="utf-8").read())
        return [n for n in ast.walk(arb) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and n.value.rstrip("/").endswith("iconta_date/bonuri")]
    surse = [f for f in glob.glob("core/*.py") + ["main.py"] if not f.split("/")[-1].startswith("test_") and scrie_calea(f)]
    assert surse == ["core/common.py"], surse
    monkeypatch.setenv("ICONTA_BON_DIR", str(tmp_path))
    assert common.dir_bonuri() == str(tmp_path)
    monkeypatch.setenv("ICONTA_MEDIU", "productie")
    with pytest.raises(RuntimeError, match="nu e de test"):
        common.dir_bonuri()


def test_jurnalul_si_inchiderea_isi_leaga_butoanele_inaintea_cererilor():
    """[proba plasei, 58 și 96, 10.10.2026] Un clic dat cât ecranul își citește starea se pierdea: butoanele jurnalului (← luna, luna →,
    „Validează”) se legau după `await legaBlocareLuna(...)`, iar navigarea „Închidere lună” după trei cereri. Cursa nu se probează
    stabil în browser (iese la întâmplare), deci gardul e pe forma codului. MUTAȚIE: `await` pus la loc în jurnal -> pică; legarea
    navigării mutată după cereri -> pică."""
    import io
    import re
    js = io.open("static/js/ecrane/firme.js", encoding="utf-8").read()
    jurnal = js[js.index("export async function ecranJurnal("):]
    jurnal = jurnal[:jurnal.index("\nexport ") if "\nexport " in jurnal else len(jurnal)]
    apel = re.search(r"^\s*(await\s+)?legaBlocareLuna\(corp\.querySelector\(\"#j-lock\"\)", jurnal, re.M)
    assert apel and not apel.group(1), "jurnalul așteaptă blocarea înainte să-și lege butoanele"
    il = js[js.index("async function ecranInchidereLuna("):js.index("export async function ecranJurnal(")]
    corp_desen = il[il.index("const deseneaza = async () => {"):]
    assert -1 < corp_desen.find('querySelector("#il-prev").addEventListener') < corp_desen.find("await "), (
        "„Închidere lună” își leagă navigarea după cererile ecranului")
