# -*- coding: utf-8 -*-
"""[lotul 12, 171 redeschisă la e2e 25.10.2026] Control fiscal sărea după „Salvează” / „Anulează marcarea”: linia de stare SPV a firmei
(`spv_stare.randeazaStareSpv`, citită la deschidere și la fiecare redesenare a verdictului) se scria cu `arataMesaj`, iar `aduInVedere`
o derula lin în vedere fiindcă apărea în cele 3 s de după clic — fereastra pleca de sub rândul atins (489 -> 846 px). O linie de stare nu
e rezultatul butonului: zona ei poartă `data-stare-ecran`, iar `aduInVedere` n-o derulează (DS cap.6). Proba pe ecran: e2e
`e2e_bloc_f.py::test_def_171_*`. MUTAȚII: excepția scoasă din `aduInVedere` -> primul test pică; marcajul scos din `randeazaStareSpv` ->
al doilea pică."""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _citeste(cale):
    return open(os.path.join(RAD, cale), encoding="utf-8").read()


def _corp_functie(sursa, antet):
    i = sursa.index(antet)
    return sursa[i:sursa.index("\n}\n", i)]


def test_aduinvedere_lasa_pe_loc_linia_de_stare_a_ecranului():
    corp = _corp_functie(_citeste("static/js/api.js"), "export function aduInVedere(el) {")
    assert re.search(r'if \(el\.closest\("\[data-stare-ecran\]"\)\) return;', corp), corp[:400]


def test_starea_spv_e_linie_de_stare_a_ecranului():
    corp = _corp_functie(_citeste("static/js/ecrane/spv_stare.js"), "export async function randeazaStareSpv(zona, nav, tenantId) {")
    i_marcaj, i_mesaj = corp.find('zona.dataset.stareEcran = "1"'), corp.find("arataMesaj(")
    assert 0 <= i_marcaj < i_mesaj, "marcajul `data-stare-ecran` trebuie pus înaintea primului mesaj al stării SPV"
