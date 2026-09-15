# -*- coding: utf-8 -*-
"""E2a — universul se declară, amestecul se OBSERVĂ.

CONSTATAREA (L1 din auditul din 14.09.2026). Registrul straturilor acoperea un univers derivat din
două definiții de „fiscal" plus modulele cu rute. Întrebarea care contează e alta: **orice modul al
aplicației care conține SQL**. Pe universul acela, 78 de module nu aveau strat declarat — adică
nimeni nu spusese ce sunt.

CE FACE E2a, și ce NU face: **numește**. Nu mută nicio linie de cod. Separarea e E2b, iar mărimea ei
se citește din cifrele de aici, nu se estimează.

DE CE DOUĂ CIFRE CU NUME DIFERITE — și ăsta e miezul etapei. `D4`, criteriul canonic al lui P7
(`CLOSED_ACCEPTED`), numără câte module **declară** două straturi și trebuie să rămână **0**. Dacă
cele 78 de declarații noi ar fi primit `mixt_cu`, D4 ar fi sărit de la 0, iar o fază închisă s-ar fi
redeschis printr-o cifră, fără ca nimeni s-o fi cerut. Amestecul EXISTĂ totuși în cod, și se măsoară
aici, pe observație, sub alt nume: **`D4b_MIXT_OBSERVAT`**.

CLASA DE EXCLUDERE E NUMITĂ: `MIGRARE_UNICA` (`core/migrare_*.py`) — 51 de migrări care rulează o
dată. Numărul lor se raportează, ca să nu se ascundă nimic în excludere.
"""
from __future__ import annotations

import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)
import pytest  # noqa: E402

from scripts import scan_univers_sql as _u  # noqa: E402

#: Măsurate la 15.09.2026. `D4b` scade prin SEPARARE (E2b), nu prin redefinirea cuvântului
#: „amestec". Cele 18 rămase sunt ACTE — cron-uri, lucrători, sonde, conectori — care își dețin
#: tranzacția fiindcă aia e treaba lor (`PLAN_HARDENING.md:840`).
PLAFON_D4B = 18                        # 41 înainte de E2b
#: **ZERO, și rămâne zero.** Un depozit care își deschide singur conexiunea sau comite taie
#: tranzacția apelantului în două (P4) — iar `db.get_conn` comite oricum la ieșirea din bloc.
PLAFON_REPOSITORY_CU_CONEXIUNE = 0     # 32 înainte de E2b


def test_CRITERIU_niciun_modul_cu_SQL_nu_e_nedeclarat():
    """Criteriul de ieșire al lui E2a. Nu clichet: zero, și rămâne zero — un modul nou cu SQL care
    intră fără declarație pică aici."""
    fara = _u.fara_strat()
    assert not fara, ("module cu SQL fără strat declarat (%d):\n  %s"
                      % (len(fara), "\n  ".join(fara)))


def test_D4_ramane_ZERO_desi_universul_s_a_largit():
    """Legătura dintre cifra veche și cea nouă, scrisă ca probă: lărgirea NU redeschide P7.

    Dacă cineva pune `mixt_cu` pe una din declarațiile noi, D4 sare de la 0 și cade poarta lui P7 —
    iar asta trebuie să fie o decizie, nu un efect colateral al unei etichetări."""
    from core import straturi
    mixte = straturi.mixte()
    assert not mixte, ("D4 (module care DECLARĂ două straturi) nu mai e zero: %s — amestecul se "
                       "măsoară cu D4b, pe cod, nu declarându-l"
                       % [d.cale for d in mixte])


def test_CLICHET_amestecul_observat_nu_creste():
    """`D4b_MIXT_OBSERVAT`: module cu SQL care își deschid singure conexiunea sau comit."""
    d4b = _u.d4b_mixt_observat()
    assert len(d4b) <= PLAFON_D4B, (
        "amestec observat: %d > %d\n  %s"
        % (len(d4b), PLAFON_D4B,
           "\n  ".join("%s (get_conn=%d commit=%d, declarat %s)" % x for x in d4b)))


def test_CLICHET_contradictia_declaratie_cod_nu_creste():
    """Un modul declarat REPOSITORY care își deschide singur conexiunea contrazice contractul
    (`PLAN_HARDENING.md:842`): depozitul primește cursorul apelantului. Cele 32 sunt pozițiile de
    lucru ale lui E2b — numărate, nu ascunse."""
    repo = _u.repository_care_isi_deschid_conexiunea()
    assert len(repo) <= PLAFON_REPOSITORY_CU_CONEXIUNE, (
        "REPOSITORY care își deschid conexiunea sau comit: %d > %d\n  %s"
        % (len(repo), PLAFON_REPOSITORY_CU_CONEXIUNE,
           "\n  ".join("%s (get_conn=%d commit=%d)" % (c, g, cm) for c, g, cm, _s in repo)))


def test_ANTI_VACUU_universul_e_cel_real():
    """O gardă cu domeniul greșit raportează verde despre o lume pe care n-o vede."""
    u = _u.universul()
    assert len(u) > 150, "doar %d module cu SQL — enumerarea s-a rupt" % len(u)
    mg = _u.migrari(u)
    assert 40 <= len(mg) <= 80, ("clasa de excludere MIGRARE_UNICA are %d module — dacă crește "
                                 "necontrolat, universul se golește prin excludere" % len(mg))
    assert len(u) - len(mg) > 100, "universul de declarat s-a subțiat"


def test_CALIBRARE_pe_univers_fabricat_in_patru_directii():
    """Fabricat, nu pe depozit: SQL + conexiune proprie → prins; SQL fără conexiune → tăcut;
    fără SQL → nu intră deloc în univers; iar `commit` singur (fără `get_conn`) tot atinge
    orchestrarea."""
    cu_tot = "def f(x):\n    with db.get_conn() as c:\n        c.execute('SELECT 1 FROM t')\n"
    assert _u.sql_din("zt.py", cu_tot), "SQL-ul dintr-o sursă fabricată nu e văzut"
    assert _u.deschide_sau_comite("zt.py", cu_tot) == (1, 0)

    doar_sql = "def f(cur):\n    cur.execute('SELECT 1 FROM t')\n"
    assert _u.sql_din("zt.py", doar_sql)
    assert _u.deschide_sau_comite("zt.py", doar_sql) == (0, 0), (
        "un depozit care primește cursorul e raportat ca amestec")

    fara_sql = "def f(cur):\n    return cur\n"
    assert not _u.sql_din("zt.py", fara_sql), "un modul fără SQL intră în univers"

    doar_commit = "def f(conn):\n    conn.execute('UPDATE t SET a=1')\n    conn.commit()\n"
    assert _u.deschide_sau_comite("zt.py", doar_commit) == (0, 1), (
        "`commit` fără `get_conn` nu e văzut — jumătate din amestec ar scăpa")


# ── E2b: fiecare depozit dovedește că tranzacția și schema vin din strat ─────────────────────

def _depozite_cu_sql():
    from core import straturi
    u = _u.universul()
    mg = _u.migrari(u)
    return sorted(c for c in u if c not in mg and straturi.strat(c) == "REPOSITORY")


def test_ANTI_VACUU_chiar_exista_depozite_de_probat():
    assert len(_depozite_cu_sql()) > 40, (
        "doar %d depozite cu SQL — universul s-a rupt, iar probele de mai jos ar trece pe gol"
        % len(_depozite_cu_sql()))


@pytest.mark.parametrize("cale", _depozite_cu_sql())
def test_DEPOZITUL_nu_deschide_conexiunea_si_nu_comite(cale):
    """Câte o probă pentru FIECARE depozit, nu o cifră pe toate: când cade, spune care.

    `db.get_conn` comite la ieșirea din bloc (`core/db.py`), deci un `commit` în depozit nu adaugă
    nimic — taie tranzacția apelantului în două. Iar un `get_conn` propriu ar însemna că depozitul
    hotărăște singur granița, adică exact ce contractul dă use-case-ului."""
    g, cm = _u.deschide_sau_comite(cale)
    assert (g, cm) == (0, 0), (
        "%s: get_conn=%d commit=%d — tranzacția trebuie să vină de la apelant "
        "(PLAN_HARDENING.md:842)" % (cale, g, cm))


@pytest.mark.parametrize("cale", _depozite_cu_sql())
def test_DEPOZITUL_nu_isi_afla_singur_schema_tenantului(cale):
    """A doua jumătate a întrebării lui E2b: schema vine tot din strat.

    Rezolvarea schemei (`schema_tenant`, `_schema_sau_404`, `_schema_cabinet_sau_404`) e o decizie
    de ACCES — cine are voie la ce firmă. Un depozit care și-ar afla singur schema ar decide, pe
    tăcute, și cine are acces."""
    import ast
    arb = _u._arbore(cale)
    gasite = {n.func.attr for n in ast.walk(arb)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr in ("schema_tenant", "_schema_sau_404", "_schema_cabinet_sau_404",
                                  "schema_tenant_citire")}
    gasite |= {n.func.id for n in ast.walk(arb)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id in ("_schema_sau_404", "_schema_cabinet_sau_404")}
    assert not gasite, ("%s își află singur schema tenantului (%s) — aia e o decizie de acces, "
                        "a stratului de deasupra" % (cale, ", ".join(sorted(gasite))))
