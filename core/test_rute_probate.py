# -*- coding: utf-8 -*-
"""O rută care SCRIE și pe care nicio probă n-o numește — clichet, ca să nu mai crească.

DE UNDE. E3 din `PLAN_E1_E6.md`, constatarea R1 a auditului: rutele sunt acoperite **structural**
(sweep-urile generice le trec pe toate, deci nimeni nu poate adăuga una fără gardă sau fără model de
corp), dar **comportamentul** lor nu e probat nicăieri.

CIFRA AUDITULUI ȘI CIFRA DE AICI NU SUNT ACEEAȘI, și se spune de ce. Auditul a scris *„59 de rute
nenumite, din care 21 scriu"*, măsurat pe `core/` + `frontend_test/` + `scripts/`. Instrumentul ăsta,
pe aceeași întrebare, găsește **3**. N-am putut reproduce 21: măsurătoarea aceea n-a lăsat un
instrument, deci nu se poate recalcula — exact lucrul despre care METODA spune că e o amintire, nu o
măsurătoare. Ce se poate recalcula, și de-aia se pune clichet aici, sunt **două** cifre:

  * `nenumite nicăieri` = 3 — nicio probă, niciun fișier, nicăieri;
  * `nenumite în suită` = **131** — nicio probă pe care s-o ruleze POARTA. Asta e cifra care
    contează pentru E3: `frontend_test/` nu e cules de pytest, deci o rută „probată" acolo nu e
    păzită de nimic la commit.

Clichetul lui E3 e deci mai mare decât plănuit (131, nu 21), și asta e chiar ce trebuie să se vadă.
"""
from __future__ import annotations

import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)
from scripts import scan_rute_fara_proba as _s  # noqa: E402

# Măsurate la 15.09.2026, după lotul „scrierile care ajung în cifre de declarație" (41 de rute).
# Scad doar cu probe scrise, niciodată prin lărgirea definiției lui „numită".
PLAFON_IN_SUITA = 76          # 131 la 14.09 · 88 la 15.09 · 82 la 16.09 · 76 la 18.09 (scaner onest)
#: [16.09.2026] 88 -> 82 -> 77, în două jumătăți ale aceleiași lucrări. Și o corectură de-a mea:
#: **88 era un PLAFON, nu o cifră.** Măsurat pe commitul de bază printr-un `git worktree`, la
#: `cfdd00ae` realul era **86** — scrisesem întâi „a scăzut 88 -> 86", ceea ce era fals: nu scăzuse
#: nimic, plafonul era doar mai sus decât cifra. Cele nouă rute care au ieșit azi au ieșit cu probe
#: SCRISE (`test_rute_stoc_pana_in_declaratie.py`, `test_rute_fiscale_lot3b.py`), nu prin lărgirea
#: definiției lui „numită". Clichetul stă acum pe cifra reală, nu peste ea.
#: [18.09.2026 · runda 2, D5] **3 era un ARTEFACT, nu o cifră.** `_fisiere_de_proba(doar_suita=False)`
#: lua TOATE `.py` din `core/`, deci chiar modulul care DEFINEȘTE ruta o „numea" prin propria
#: definiție — „nicăieri" ajunsese să însemne „în niciun fișier", nu „în niciun fișier care PROBEAZĂ".
#: Cu modulele de implementare scoase (D5) + granița de cuvânt + fără comentarii (D3) + `%d`/`%s` în
#: cale (D10), realul e **21**. Nu au apărut rute noi; s-a corectat un scaner orb. Clichetul stă acum
#: pe cifra reală, ca o rută nou-nenumită să se vadă.
PLAFON_NICAIERI = 21

# Clichetul care contează cel mai tare: rute care scriu în tabele din care se RIDICĂ DECLARAȚII,
# derivate din cod de `scripts/scan_scrieri_declaratii.py` (tabele scrise ∩ tabele citite de
# generatoare). 49 la derivare, 8 rămase. Cele opt cer fiecare o lume pregătită (articol de stoc,
# linie de extras bancar, bon pozat, mijloc fix, rețetă, fișier de migrare) — sunt numite în
# GARZI.md, nu lăsate să se piardă în cifră.
#: [16.09.2026] 8 -> 4 -> **0**, în două jumătăți ale aceleiași lucrări. Fiecare din cele opt a
#: primit probă care merge PÂNĂ ÎN CIFRA DECLARAȚIEI, nu până la `200`: apasă ruta prin HTTP,
#: VALIDEAZĂ nota (ciorna nu e evidență), și citește rulajul contului — sursa din care se ridică
#: `GeneralLedgerEntries`. `core/test_rute_stoc_pana_in_declaratie.py` (stocuri ×3 +
#: reevaluare-imobilizare) și `core/test_rute_fiscale_lot3b.py` (migrare/importa,
#: banca/…/conteaza, bonuri/…/stinge, retete/descarca).
#:
#: **ȘI DE-AIA E UN CRITERIU (EGALITATE), NU UN PLAFON.** Prima rută nouă care ar scrie într-un tabel
#: de declarație fără probă ar încăpea sub un `<=`. Scris ca EGALITATE, creșterea se vede în ziua în
#: care se produce.
#:
#: [18.09.2026 · runda 2, D1+D2] **0 era FALS — scanerul era orb pe trei drumuri.** (a) urmărea UN
#: singur nivel de apeluri, deci `wc_sinc` (-> `sincronizeaza` -> `_importa(facturi_api)` ->
#: `emite_factura`) și `stocuri_descarcare` ieșeau cu ZERO tabele; (b) `citite_de_generatoare` nu
#: vedea tabelele citite prin helperi/`FROM %s` (beneficii_lunare, pontaj, salariu_istoric, d300_manual)
#: ori de sub-generatoarele D406 (mijloace_fixe, reevaluari, miscari_stoc); (c) rutele „numite" doar
#: într-un comentariu ori ca subșir treceau drept probate. Cu recursia call-graph + suplimentele
#: DECLARATE pentru dispatch-ul prin parametru/`%s` (D1/D2) + granița de cuvânt/fără comentarii (D3),
#: realul e **10**: articole_import_salveaza, jurnal_sterge, jurnal_editeaza, mijloace_import_salveaza,
#: nota_avans, salariat_beneficiu_lunar, tenant_pontaj_set, stocuri_descarcare, cv_transfer, wc_sinc.
#: (jurnal_sterge/jurnal_editeaza erau „numite" de un comentariu; nota_avans e subșir al lui
#: `nota_avans_platit` — exact cele scoase la iveală de D3.) Cele zece scriu în tabele de declarație și
#: NU au probă de comportament în suită — restanță NUMITĂ (nu o zero falsă). O a unsprezecea se vede.
PLAFON_SUBSET_FISCAL = 10


def test_CLICHET_rutele_care_scriu_fara_proba_in_suita_nu_cresc():
    """Cifra care contează pentru E3: fără probă pe care s-o ruleze poarta."""
    n = _s.nenumite(doar_suita=True)
    assert len(n) <= PLAFON_IN_SUITA, (
        "rute care scriu, fără nicio probă în suită: %d > %d\n  %s"
        % (len(n), PLAFON_IN_SUITA,
           "\n  ".join("%-6s %s (%s)" % (m, c, f) for c, m, f in n[:20])))


def test_CLICHET_rutele_nenumite_NICAIERI_nu_cresc():
    """Clasa cea mai rea: nicio urmă, în niciun fișier de probă din depozit."""
    n = _s.nenumite()
    assert len(n) <= PLAFON_NICAIERI, (
        "rute care scriu, nenumite nicăieri: %d > %d\n  %s"
        % (len(n), PLAFON_NICAIERI, "\n  ".join("%-6s %s (%s)" % (m, c, f) for c, m, f in n)))


def test_ANTI_VACUU_scanul_vede_aplicatia_si_probele():
    """Un scan cu domeniul greșit raportează verde despre o lume pe care n-o vede."""
    tot = _s.rute()
    assert len(tot) > 200, "doar %d rute care scriu — enumerarea din `main.app.routes` s-a rupt" % len(tot)
    numite = len(tot) - len(_s.nenumite(doar_suita=True))
    assert numite > 50, ("doar %d rute apar în suită — căutarea în fișierele de probă s-a rupt, iar "
                         "clichetul ar deveni un plafon fără conținut" % numite)


def test_CALIBRARE_pe_univers_fabricat_in_patru_directii():
    """Fără probe → totul raportat. Cu numele funcției → tăcut. Cu calea → tăcut. Cu un PREFIX al
    căii → raportat (aici a fost greșeala: `/tenants/{id}/produse` se potrivea într-o probă care
    cheamă `/tenants/5/produse/7`, deci o rută era declarată „numită" de proba alteia)."""
    tot = _s.rute()
    assert len(_s.nenumite(surse=[])) == len(tot), "cu ZERO probe, nu raportează tot — scanul e orb"

    cale, _metoda, nume = next((r for r in tot if r[2] and "{" in r[0]), tot[0])
    assert not [x for x in _s.nenumite(surse=["cheama %s()" % nume]) if x[0] == cale], (
        "numele funcției nu contează ca numire")

    concreta = cale.replace("{", "").replace("}", "")
    concreta = "/".join("7" if s in cale.split("/") and "{" in s else s for s in cale.split("/"))
    assert not [x for x in _s.nenumite(surse=['cl.post("%s")' % concreta]) if x[0] == cale], (
        "calea concretă (`%s`) nu contează ca numire" % concreta)

    mai_lunga = concreta.rstrip("/") + "/7"
    assert [x for x in _s.nenumite(surse=['cl.post("%s")' % mai_lunga]) if x[0] == cale], (
        "o cale MAI LUNGĂ (`%s`) trece drept numirea rutei scurte — tiparul nu e ancorat la capăt"
        % mai_lunga)


def test_CLICHET_rutele_care_scriu_IN_CIFRE_DE_DECLARATIE_nu_cresc():
    """Subsetul derivat din cod: tabelele scrise de rută ∩ tabelele citite de generatoare.

    E clichetul cu cel mai mare preț per unitate: o rută de aici greșește **într-un fișier depus la
    ANAF**, nu pe un ecran. De-aia probele lui merg până în rândul declarației, nu până la `200`.
    """
    import sys
    if _s.RAD not in sys.path:
        sys.path.insert(0, _s.RAD)
    from scripts import scan_scrieri_declaratii as _sd
    sub, fara = _sd.subsetul()
    assert len(sub) == PLAFON_SUBSET_FISCAL, (
        "rute care scriu în tabele de declarație, fără probă în suită: %d, așteptat %d.\n"
        "  E un CRITERIU, nu un clichet: o rută nouă care scrie într-un tabel din care se ridică o "
        "declarație are nevoie de probă ÎNAINTE de a intra, nu după.\n  %s"
        % (len(sub), PLAFON_SUBSET_FISCAL,
           "\n  ".join("%-6s %s -> %s" % (m, c, ",".join(d)) for c, m, _f, _tb, d in sub)))
    # anti-vacuum: dacă intersecția se golește (alt domeniu, alt tipar), clichetul ar deveni gol
    assert len(_sd.citite_de_generatoare()) >= 5, "generatoarele nu mai declară niciun tabel citit"
    assert len(fara) < 40, ("prea multe rute fără niciun tabel văzut (%d): scanul de SQL efectiv "
                            "s-a rupt, iar subsetul s-ar goli fără ca lumea să se fi schimbat"
                            % len(fara))
