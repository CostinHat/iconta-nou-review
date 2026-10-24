# -*- coding: utf-8 -*-
"""[lotul 12, C136] „Scoate firma” arăta „Dispar și: 3 × `audit_log` · 1 × `user_tenants` …, plus schema de date a firmei”, iar „Firme
scoase” „schema `tenant_368` · S-au curățat: 1 × `user_tenants`” — numele tabelelor și ale schemei din bază, pe ecranul contabilului.

Acum serverul dă textul (`tenant_stergere.ETICHETE_RANDURI` + `ce_dispare`, acordat cu `common.cate`): previzualizarea poartă
`ce_dispare`, lista firmelor scoase `curatate` (`uc_firme_scoase`). Garda: fiecare tabelă curățată are etichetă fără „_”; cele două ecrane
(`firme.js`: `ecranScoateFirma`, `randeazaFirmeScoase`) nu mai pun nicio cheie de tabelă / schemă în `<code>`.
Temei: N/A — regulă de produs (CLAUDE.md §9: texte în limba contabilului, fără termeni de programator).
"""
import io
import os
import re

from core import tenant_stergere as ts

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_def_c136_fiecare_tabela_curatata_are_eticheta_pentru_contabil():
    """MUTAȚIE: „audit_log” scos din `ETICHETE_RANDURI` -> pică (tabelă fără etichetă)."""
    fara = sorted(set(ts.TABELE_TENANT) - set(ts.ETICHETE_RANDURI))
    assert not fara, "tabele curățate fără etichetă pentru contabil: %s" % fara
    for k, (sg, pl) in ts.ETICHETE_RANDURI.items():
        assert sg and pl and "_" not in sg + pl and k not in sg + pl, (k, sg, pl)
    toate = ts.ce_dispare({k: 1 for k in ts.ETICHETE_RANDURI})
    assert len(toate) == len(ts.ETICHETE_RANDURI) and not [t for t in toate if "_" in t], toate


def test_def_c136_ce_dispare_e_acordat_si_fara_nume_de_tabel():
    """„3 rânduri din jurnalul de activitate · 1 acces al unui utilizator la firmă”, „20 de …”; zero-urile nu se arată; rândul firmei
    (`tenants`) nu e printre ce „dispare și”. MUTAȚIE: în `ce_dispare` `cate(randuri[k], *…)` -> `"%d × %s" % (randuri[k], k)` -> pică."""
    assert ts.ce_dispare({"audit_log": 3, "user_tenants": 1, "spv_token": 0, "tenants": 1}) == [
        "3 rânduri din jurnalul de activitate", "1 acces al unui utilizator la firmă"]
    assert ts.ce_dispare({"audit_log": 20}) == ["20 de rânduri din jurnalul de activitate"]


def test_def_c136_ecranele_nu_mai_arata_numele_tabelelor():
    """Previzualizarea și lista „Firme scoase” citesc textul serverului (`ce_dispare` / `curatate`), fără `<code>` cu chei de tabelă sau
    numele schemei. Pică până când `firme.js` folosește textul serverului (petecul cerut în raportul pachetului `diverse`)."""
    js = io.open(os.path.join(RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    for fn, camp in (("async function ecranScoateFirma(", "p.ce_dispare"), ("function randeazaFirmeScoase(", "f.curatate")):
        i = js.index(fn)
        j = js.find("\nfunction ", i + 10)
        k = js.find("\nasync function ", i + 10)
        corp = js[i:min(x for x in (j, k, len(js)) if x > 0)]
        assert camp in corp, "%s nu citește textul serverului (%s)" % (fn, camp)
        assert not re.search(r"<code>\$\{esc\((?:k|f\.schema_name[^)]*)\)\}</code>", corp), "%s arată numele tabelelor / schemei" % fn
        assert "schema de date" not in corp and "tabelele comune" not in corp, fn
    # pe ARBORE: lista „Firme scoase” primește textul serverului — câmpul `curatate` al fiecărei firme e chiar `_ts.ce_dispare(…)`
    import ast
    uc = ast.parse(io.open(os.path.join(RAD, "core", "uc_firme_scoase.py"), encoding="utf-8").read())
    curatate = [(ast.unparse(n.value.func) if isinstance(n.value, ast.Call) else ast.unparse(n.value)) for n in ast.walk(uc)
                if isinstance(n, ast.Assign) and [ast.unparse(x) for x in n.targets] == ["f['curatate']"]]
    assert curatate == ["_ts.ce_dispare"], curatate
