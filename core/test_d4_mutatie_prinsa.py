# -*- coding: utf-8 -*-
"""[D4, 18.09.2026] GARDA-MUTAȚIE PERMANENTĂ. O rută nouă care dublează `facturi.total`, numită doar
într-un comentariu, trebuie PRINSĂ de clichetele din `test_rute_probate.py`. Auditul (D4) a arătat că
pe scanerul orb de dinainte o astfel de rută trecea toate trei clichetele. Aici pinăm MECANISMELE care
o prind acum — la nivel de instrument, fără a muta aplicația vie:

  (1) SUBSET_FISCAL o prinde: SQL-ul `UPDATE facturi SET total=total*2` -> tabelul `facturi` e extras,
      iar `facturi` E un tabel de declarație -> ruta intră în subset (10 -> 11, clichetul EGALITATE cade).
  (2) NICAIERI/IN_SUITA o prind: numele într-un COMENTARIU nu mai probează (D3 comment-strip), iar un
      SUBȘIR al numelui nu numește (D3 graniță de cuvânt) -> ruta rămâne nenumită.

Dacă vreunul din mecanisme se rupe, mutația redevine invizibilă. De-aia sunt aici, nu în capul meu.
"""
from __future__ import annotations

import sys

from scripts import scan_scrieri_declaratii as _sd
from scripts import scan_rute_fara_proba as _sr

if _sd.RAD not in sys.path:
    sys.path.insert(0, _sd.RAD)


def test_D4_subset_prinde_o_scriere_in_facturi():
    """(1) SQL-ul mutației -> tabelul `facturi`; și `facturi` E tabel de declarație."""
    tab = _sd._tabele(["UPDATE facturi SET total = total * 2 WHERE id = %s"], _sd.SCRIE)
    assert tab == {"facturi"}, "mutația de dublare a facturii nu mai dă tabelul facturi: %s" % tab
    # intersecția tabelului scris cu tabelele de declarație e NEVIDĂ -> o rută cu acest SQL intră în
    # subset (aserție pe STRUCTURĂ — mulțimi — nu pe prezența unui șir).
    assert tab & set(_sd.citite_de_generatoare()), (
        "tabelul scris de mutație nu intersectează tabelele de declarație — o rută care-l scrie n-ar "
        "mai intra în subset")


def test_D4_comentariul_si_subsirul_nu_numesc_ruta():
    """(2) O rută numită DOAR într-un comentariu sau ca SUBȘIR rămâne nenumită; numele întreg în cod
    o numește (control pozitiv, ca garda să nu treacă degeaba raportând tot ca nenumit)."""
    tot = _sr.rute()
    cale, _m, nume = next(r for r in tot if r[2] and "{" not in r[0] and len(r[2]) >= 6)

    def _nenumita(surse):
        return any(x[2] == nume for x in _sr.nenumite(surse=surse))

    assert _nenumita(["# ruta %s este testata mai jos" % nume]), (
        "o rută numită doar într-un comentariu trece drept probată — D3 comment-strip e rupt")
    assert _nenumita(["%s_extins_altceva()" % nume]), (
        "un subșir al numelui (`%s_extins...`) trece drept numire — D3 graniță de cuvânt e ruptă" % nume)
    assert not _nenumita(["def proba(): cheama_main.%s()" % nume]), (
        "numele întreg, în cod, nu contează ca numire — calibrarea e ruptă în cealaltă direcție")
