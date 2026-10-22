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
PLAFON_D4B = 19                        # 41 înainte de E2b; 18 -> 19 la 09.10.2026: `core/migrari_registru.py`, rulatorul
                                       # migrărilor (comanda Costin pct.2) — un ACT cu tranzacția lui, ca celelalte
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
    # [Retest 2, 09.10.2026] 80 -> 81: `core/migrare_retest2.py` (coloana `casa_operatiuni.storno_de` + notele de refacere NIR)
    # [09.10.2026, comanda Costin pct.1 și pct.11] 81 -> 83: `core/migrare_nota_corectie.py` (reparația tenant_049) și
    # `core/migrare_reguli_fond.py` (regulile de fond în bază)
    # [09.10.2026, „Retestul plasei” pct.6] 83 -> 84: `core/migrare_reguli_fond_2.py` (regulile de fond a, c, d, e, f)
    # [12.10.2026, retestul Costin, deficiența 229] 84 -> 85: `core/migrare_data_infiintare.py` (coloana `firma_profil.data_infiintare`)
    # [14.10.2026, decizia Costin pct.3–4 la lotul 1] 85 -> 86: `core/migrare_salariati_de_verificat.py` (coloana `salariati.de_verificat`)
    # [15.10.2026, lotul 2] 86 -> 87: `core/migrare_invitatii_cabinet.py` (tabela `public.invitatii_cabinet`)
    # [15.10.2026, lotul 3] 87 -> 88: `core/migrare_ciorne_proprii.py` (triggerele ciornei altui utilizator, deficiența 246)
    # [15.10.2026, lotul 4] 88 -> 89: `core/migrare_inregistrare_libera.py` (`public.setari_platforma`, `public.inregistrari_in_asteptare`)
    # [15.10.2026, lotul 5] 89 -> 90: `core/migrare_sanatate_load15.py` (`metrici_sanatate.load15`, `.teste` — alerta de load, 6b)
    # [15.10.2026, lotul 5] 90 -> 91: `core/migrare_emailuri_dezabonate.py` (`public.emailuri_dezabonate` — dezabonarea, 268)
    # [15.10.2026, lotul 5] 91 -> 92: `core/migrare_fisiere_private.py` (`public.fisiere_private`, `raportari.tip/aplicatie` — 270d, C36)
    # [16.10.2026, lotul 5, comanda 4] 92 -> 93: `core/migrare_nume_conturi_vechi.py` (numele întreg al administratorilor vechi, 269);
    # prins numai de poarta lotului — rularea țintită nu vedea un `.py` nou (acum: `perimetru.MOTIV_POPULATIE` -> suita întreagă)
    # [16.10.2026, lotul 6] 93 -> 99: `migrare_extras_miscare` (277, mișcarea extrasului), `migrare_casa_avans` (278, avansul și
    # legătura chitanțelor vechi), `migrare_spv_citiri` (273 / pct.2b, citirile SPV pe CUI), `migrare_declaratii_asteptare` (284),
    # `migrare_inregistrari_email` (282), `migrare_raportari_stare_necitita` (291) — toate DDL idempotent pe o tabelă / coloană, o dată.
    # [16.10.2026 noaptea, lotul 6 — răspunsul la raport] 99 -> 100: `migrare_categorie_tva_linie` (274b, categoria de TVA a liniei cu 0%).
    # [17.10.2026, lotul 7] 100 -> 101: `migrare_canal_notificari` (telefonul, canalul și acordul pe `public.users`, codul de confirmare,
    # cutia de ieșire și jurnalul notificărilor — 2.1–2.2) — DDL idempotent, o dată.
    # [17.10.2026, comanda 7.2] 101 -> 103: `migrare_nr_curent_note` (numărul notei dat la validare, 302) și `migrare_plan_avansuri`
    # (4092–4094 în planul firmelor, C48) — DDL / adăugări idempotente, o dată pe firmă.
    # [18.10.2026, comanda 8.2] 103 -> 106: `migrare_ajustari_fiscale` (ajustările rezultatului fiscal pe trimestru, 378),
    # `migrare_mf_amortizare_preluata` (amortizarea cumulată preluată, 359), `migrare_partener_linie` (partenerul pe linia notei, 381)
    # — DDL idempotent, o dată pe firmă.
    # [19.10.2026, comanda 9.1] 106 -> 107: `migrare_plan_conturi_omfp` (planul de conturi întreg din OMFP 1802/2014 pe firmele existente,
    # 387) — migrare unică, rulată o dată pe firmă.
    # [19.10.2026, comanda 9.3] 107 -> 108: `migrare_cont_linie_primita` (contul pe linia facturii primite, 418b) — DDL idempotent.
    # [19.10.2026, comanda 9.2] 108 -> 109: `migrare_borderou_achizitie` (actul de identitate al vânzătorului PF, 401–402) — DDL idempotent.
    # [19.10.2026, închiderea lotului 9] 109 -> 111: `migrare_avans_nir_ajustare_nota` (plata NIR-ului fără factură, 405; ajustarea fiscală din
    # nota inventarului, 404) și `migrare_cim_salariat` (contractul individual de muncă pe fișa salariatului, 412) — DDL idempotent.
    # [20–21.10.2026, lotul 10] 111 -> 117: `migrare_balanta_rulaje_an` (soldul inițial al anului și rulajele preluate, 425),
    # `migrare_tva_incasare_perioade` (perioadele TVA la încasare, 428), `migrare_reevaluari_valuta` (reevaluările consemnate, 429),
    # `migrare_compensari_afiliat` (compensările și bifa „persoană afiliată”, 428), `migrare_profil_c69` (mare contribuabil, forma de
    # proprietate, fără cont bancar, C69), `migrare_borderou_numar_unic` (numărul borderoului unic pe an, 434) — DDL idempotent, o dată.
    # [21.10.2026, lotul 11] 117 -> 123: `migrare_borderou_storno_unic` (o singură stornare pe borderou, index unic), `migrare_borderou_tip_vechi`
    # (borderourile de dinainte de lotul 9 pe tipul lor, C75), `migrare_cui_fara_ro` (CUI-ul păstrat fără „RO”, decizia 10.3 pct.4),
    # `migrare_intocmitor_bilant` (întocmitorul bilanțului pe cabinet, interesul public pe firmă), `migrare_produse_categorie_tva` (categoria
    # de TVA a produsului cu cota 0, 449), `migrare_reevaluare_partener` (reevaluarea valutei pe partener) — rulate o dată, idempotente.
    # [22.10.2026, lotul 11] 123 -> 125: `migrare_factura_tva_cote` (TVA-ul pe cote al facturii primite, din XML-ul ei — BG-23, C79) și
    # `migrare_valoare_neta_linie` (valoarea netă a liniei de pe factură, păstrată exact — BT-131, C82) — rulate o dată, idempotente.
    # [22.10.2026, lotul 11, subagentul N] 125 -> 126: `migrare_serie_nr_descrieri` (443, datele existente: ciornele cu seria lipită de
    # număr rescrise cu `pdf_util.serie_nr`) — rulată o dată, idempotentă.
    # [22.10.2026, lotul 11, C88] 126 -> 127: `migrare_curs_precizie` (cursul BNR cu precizia lui; cache-ul refăcut din arhivă) — rulată
    # o dată, idempotentă.
    assert 40 <= len(mg) <= 127, ("clasa de excludere MIGRARE_UNICA are %d module — dacă crește "
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
