# -*- coding: utf-8 -*-
"""[lotul 13, zona firme2, plasa: 577] GARD — orice tabelă de firmă creată de o migrare e și în șablonul firmei noi (`tenant_template.sql`).

Prins de plasa e2e a lotului 13 (`e2e_lot13_firme2::test_def_577_*`, eroare la închidere: răspuns 500): la o firmă PFA NOUĂ, „Registrul de
evidență fiscală” pe varianta persoanei fizice (`registru-evidenta-fiscala?varianta=venituri_pf`) cădea cu „relation registru_fiscal_pf does
not exist”. Tabela o crea numai `core/migrare_registru_fiscal_pf.py` (pe firmele existente); docstringul ei spune „mirror in
`tenant_template.sql`”, dar oglinda lipsea, deci o firmă creată după migrare n-o avea. Reparația: tabela în șablon (peticul `firme2_8`).

CLASA: o migrare care creează o tabelă în schema firmei (`{s}.<tabelă>` / `"{schema}".<tabelă>` / `%s.<tabelă>`) fără aceeași tabelă în
șablon -> firmele noi n-o au. Căutarea pe tot `core/migrare_*.py` (la 26.10.2026): o singură apariție, `registru_fiscal_pf`.
CE FACE IMPOSIBIL: o tabelă de firmă nouă scrisă numai într-o migrare. Tabelele din `public` nu intră (nu țin de firmă).
MUTAȚIE: blocul `registru_fiscal_pf` scos din `tenant_template.sql` -> pică, numind migrarea și tabela.
TEMEI: N/A — schema bazei (CLAUDE.md §7: firmele noi pornesc din șablon).
"""
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RE_SABLON = re.compile(r"CREATE TABLE (?:IF NOT EXISTS )?TENANT_PLACEHOLDER\.(\w+)", re.I)
# tabela creată în schema firmei: `{s}.x`, `"{s}".x`, `{schema}.x`, `%s.x`, `"%s".x` (nu `public.x`)
_RE_MIGRARE = re.compile(r"CREATE TABLE (?:IF NOT EXISTS )?\"?(?:\{\w*\}|%s)\"?\.\"?(\w+)", re.I)


def _tabele_din_migrari():
    out = {}
    for f in sorted(glob.glob(os.path.join(RAD, "core", "migrare_*.py"))):
        for t in _RE_MIGRARE.findall(open(f, encoding="utf-8").read()):
            out.setdefault(t, os.path.relpath(f, RAD))
    return out


def test_tabelele_create_de_migrari_sunt_si_in_sablon():
    sablon = set(_RE_SABLON.findall(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()))
    migrari = _tabele_din_migrari()
    assert len(migrari) > 20, "anti-vacuu: migrările nu mai sunt citite (%d tabele)" % len(migrari)
    lipsa = sorted((f, t) for t, f in migrari.items() if t not in sablon)
    assert not lipsa, ("tabele de firmă create numai de o migrare, absente din `tenant_template.sql` (o firmă nouă nu le are; pățit: "
                       "registru_fiscal_pf -> 500 la Registrul de evidență fiscală al PFA): %s" % lipsa)


def test_calibrare_forma_migrarii_si_public():
    assert _RE_MIGRARE.findall('CREATE TABLE IF NOT EXISTS {s}.x (') == ["x"]
    assert _RE_MIGRARE.findall('CREATE TABLE IF NOT EXISTS "%s".y (') == ["y"]
    assert _RE_MIGRARE.findall('CREATE TABLE IF NOT EXISTS public.z (') == []
