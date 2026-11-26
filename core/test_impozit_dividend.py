# -*- coding: utf-8 -*-
"""PAS 0 versionare formule: cotele = COTE period-aware, nu petic 'if ref>=2026 else 10'.
DIVIDENDE (art.97 alin.7): 16% de la 01.01.2026 (Legea 141/2025), 10% in 2025, 8% pre-2025.
LICHIDARE (art.97 alin.5) e DISTINCTA: cota FIXA 10%, impozit final, NU regimul dividendelor -
corectat 23.09.2026 (aplicatia folosea gresit cota dividendelor pentru castigul din lichidare)."""
from datetime import date

from core import common as c, decontari_asociati as da, lichidare as li


def test_impozit_dividend_period_aware_din_cote():
    assert c.cota("impozit_dividend", date(2026, 1, 1))[0] == c.Decimal("0.16") if hasattr(c, "Decimal") else True
    from decimal import Decimal
    assert c.cota("impozit_dividend", date(2026, 6, 1))[0] == Decimal("0.16")
    assert c.cota("impozit_dividend", date(2025, 6, 1))[0] == Decimal("0.10")  # OUG 156/2024 (2025, de la 01.01.2025)


def test_cota_dividend_si_lichidare_sursa_din_cote():
    """Ambele functii intorc procentul din common.COTE, nu literal. DIVIDENDELE (decontari_asociati)
    urmeaza art.97 alin.7 (16%/10%); LICHIDAREA (lichidare) e cota FIXA 10% (art.97 alin.5), DISTINCTA."""
    assert int(da.cota_dividend(date(2026, 6, 1))) == 16
    assert int(da.cota_dividend(date(2025, 6, 1))) == 10
    # lichidare = 10% FIX (art.97 alin.5), pe orice an - NU cota dividendelor (16% din 2026)
    assert int(li._cota_lichidare(date(2026, 6, 1))) == 10
    assert int(li._cota_lichidare(date(2024, 6, 1))) == 10


def test_peticul_if_pe_data_a_disparut():
    """Regula 0a: peticul (COTA_2026/COTA_VECHE + if ref>=2026) a fost ELIMINAT, nu comentat."""
    src = open("core/decontari_asociati.py", encoding="utf-8").read()
    assert "COTA_2026" not in src and "COTA_VECHE" not in src
    assert "if ref >= date(2026" not in open("core/lichidare.py", encoding="utf-8").read()


# [17.5-C9, C-ghid pct.4] GARDA DE PUBLICARE A GHIDURILOR pentru cheia `impozit_dividend` (CLAUDE.md §10): orice ghid din ghid/ (și cele
# vechi, din afara clichetului de citări) cu o afirmație datată despre cota dividendelor sau cu un exemplu cu dividende se confruntă cu
# registrul (`core.common.COTE`); o diferență pică aici, deci în poarta lotului care publică ghidul sau registrul. Fișierele numite, ca
# selecția țintită să ruleze testul și când se schimbă numai ghidul: ghid/impozit-dividende-2026.md,
# ghid/impozit-dividende-2026-exceptia-interimare.md, ghid/cota-impozitului-dividende-2026.md, ghid/termenul-plata-impozitului-veniturile-dividende.md,
# ghid/simulare-plateste-asociat-dividende-2026.md, ghid/impozit-dividende-cota-gresita.md, ghid/impoziteaza-dividendele-pfa-2026.md.
def test_ghidurile_cheii_impozit_dividend_urmeaza_registrul():
    from core import ghid_poarta as gp
    afectate = gp.ghiduri_afectate()
    assert "impozit-dividende-2026" in afectate and len(afectate) >= 50, "garda nu mai vede ghidurile cheii (%d)" % len(afectate)
    rele = ["%s: %s" % (s, gp._mesaj_valoare(s, a)) for s, ab in sorted(afectate.items()) for a in ab]
    assert not rele, "ghiduri care contrazic registrul impozit_dividend:\n  " + "\n  ".join(rele)


def test_ghidul_dividendelor_2026_exemplul_si_cele_patru_cote():
    """[17.5-C9, C-ghid pct.3] Exemplul PF de 100.000 lei: decembrie 2025 = 10.000 / 90.000, ianuarie 2026 = 16.000 / 84.000, diferența
    6.000; cotele 5%, 8%, 10%, 16%; termenul de 25 ianuarie pentru suma distribuită și neplătită; `modified` la editare."""
    from core import ghid_poarta as gp
    txt = open("ghid/impozit-dividende-2026.md", encoding="utf-8").read()
    meta, corp = gp._frontmatter(txt)
    assert meta["published"] == "2026-08-12" and meta["modified"] >= "2026-11-26"
    for s in ("impozit 10% = **10.000 lei**, dividend net **90.000 lei**", "impozit 16% = **16.000 lei**", "**84.000 lei**",
              "**6.000 lei**", "25 ianuarie inclusiv", "art. LXIV pct. 9", "art. II pct. 5", "art. VII alin. (2)"):
        assert s in corp, s
    assert gp.verifica_valori_fiscale(corp) == []
