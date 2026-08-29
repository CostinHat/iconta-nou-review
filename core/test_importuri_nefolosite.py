# -*- coding: utf-8 -*-
"""CLICHET pe importurile nefolosite (F401). Nu blochează codul existent; oprește creșterea.

DE CE ACUM, și de ce nu în poartă. `ruff.toml` (18.08.2026, `b88b13d`) a pornit poarta **deliberat
minimală** — doar familia „undefined" (F821/F822/F823), fiindcă alea sunt crash-uri care scapă de
pytest. Motivul scris acolo pentru F401: *„prea zgomotoase ca să fie poartă blocantă pe cod existent"*.
**Motivul rămâne valabil pentru o poartă blocantă și e greșit pentru un clichet:** un clichet nu cere
curățenie acum, doar împiedică creșterea.

CE A DECIS CONSTRUCȚIA. Cifra a scăzut de la ~115 (18.08) la 90 (23.08) **incidental** — nimic n-a
păzit direcția, deci nimic nu garanta că nu urcă la loc. Un import mort nu e un defect, dar e un
semnal: `d406.Nota.jurnal` a stat trei săptămâni ca urmă a unei intenții, iar reparația de prag 1 din
R22 a aterizat exact acolo (vezi R23).

CE NU FACE, declarat: nu curăță nimic și nu judecă dacă importul e mort din neglijență sau din
refactorizare. Numără, per fișier, și cere ca numărul să nu urce. F811 (redefinire) și F841 (variabilă
nefolosită) rămân în afara lui — au fost măsurate, nu sunt gardate.
"""
import collections
import os
import subprocess

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RUFF = os.path.join(_RAD, "venv", "bin", "ruff")
_TINTE = ("core", "main.py", "scripts")

# Măsurat 23.08.2026. Se COBOARĂ pe măsură ce importurile mor; nu se ridică.
BASELINE = {
    "core/auth_api.py": 1, "core/banca.py": 3, "core/beneficii_api.py": 1, "core/casa.py": 1,
    "core/curs_bnr.py": 1, "core/d301.py": 1, "core/d390_clasificare_api.py": 1, "core/d397.py": 2,
    "core/d406.py": 1, "core/decontari_asociati.py": 1, "core/documente_api.py": 4,
    "core/factura_pdf.py": 1, "core/facturi.py": 1, "core/lichidare.py": 1,
    "core/scan_constante.py": 1, "core/spv_poll.py": 1, "core/stat_plata_api.py": 3,
    "core/test_a11y_contrast_tokens.py": 1, "core/test_achizitii_factura.py": 1,
    "core/test_amprenta_declaratie.py": 1, "core/test_api_public.py": 2, "core/test_baza_cm.py": 1,
    "core/test_catch_vizibil.py": 1, "core/test_cauza_precisa_business.py": 1,
    "core/test_control_fiscal.py": 1, "core/test_control_incrucisat.py": 2,
    "core/test_cui_cnp_test_valid.py": 1, "core/test_d112.py": 2, "core/test_d112_cnp_angajat.py": 1,
    "core/test_d205_imp_manual.py": 1, "core/test_d300.py": 1, "core/test_d300_reconciliere.py": 1,
    "core/test_d300_zero_rate.py": 1, "core/test_d390.py": 1, "core/test_d390_d301_semnal.py": 1,
    "core/test_d390_nota1.py": 1, "core/test_d394.py": 1, "core/test_d402.py": 1,
    "core/test_datorie.py": 1, "core/test_declaratii_lot3_duk.py": 1,
    "core/test_diacritice_afisate.py": 1, "core/test_edge_canonic_head.py": 1,
    "core/test_expirare_cote_de_baza.py": 1, "core/test_export_cota.py": 1,
    "core/test_faptul_bate_vectorul.py": 1, "core/test_fixturi_shared_period.py": 1,
    "core/test_front_e_editare_identitate.py": 1, "core/test_g1_cod_mesaj.py": 1,
    "core/test_golden_xsd.py": 1, "core/test_harta_ecrane.py": 1,
    "core/test_mesaje_generare_fara_camp_intern.py": 1, "core/test_mutant_zero.py": 2,
    "core/test_numere.py": 1, "core/test_pastila_gri.py": 1, "core/test_perimetru_calculat.py": 1,
    "core/test_perioada.py": 1, "core/test_poarta_gol.py": 1, "core/test_premisa_restanta.py": 1,
    "core/test_preview_salvare_poarta.py": 1, "core/test_provenienta.py": 1, "core/test_q16_cor.py": 1,
    "core/test_rotunjire_fiscala.py": 2, "core/test_spv_poll.py": 1, "core/test_upsert_motivat.py": 1,
    "core/test_versionare_assets.py": 1, "core/test_vigoare_articole_registru.py": 1,
    "core/woocommerce.py": 1, "main.py": 8, "scripts/scan_axa_garzi.py": 1,
}


def _f401():
    if not os.path.exists(_RUFF):
        pytest.skip("ruff neinstalat în venv")
    r = subprocess.run([_RUFF, "check", "--select", "F401", "--output-format", "concise"]
                       + list(_TINTE), cwd=_RAD, capture_output=True, text=True)
    c = collections.Counter()
    for l in r.stdout.splitlines():
        if " F401 " in l:
            c[l.split(":")[0]] += 1
    return c


def test_ANTIVACUU_ruff_chiar_raporteaza():
    """Dacă ruff dispare, se schimbă formatul de ieșire sau se rupe parsarea, contorul devine 0 și
    clichetul ar trece pe gol, raportând curățenie acolo unde nu s-a uitat nimeni."""
    c = _f401()
    assert sum(c.values()) >= 40, (
        "doar %d importuri nefolosite găsite — parsarea s-a rupt, nu codul s-a curățat" % sum(c.values()))
    assert "main.py" in c, "`main.py` nu mai apare în raport — ținta s-a schimbat sub picioare"


def test_clichetul_nu_creste():
    """Miezul. Un fișier nou pornește de la 0: orice import mort în el pică."""
    c = _f401()
    crescut = ["  %s: %d > %d" % (f, n, BASELINE.get(f, 0))
               for f, n in sorted(c.items()) if n > BASELINE.get(f, 0)]
    assert not crescut, (
        "importuri nefolosite în plus față de clichet:\n" + "\n".join(crescut)
        + "\n\nRemediu: scoate importul. Dacă e intenționat (re-export), pune-i `# noqa: F401` cu "
          "motivul — un import păstrat fără motiv scris e o urmă de intenție, nu o decizie (R23).")


def test_baseline_nu_e_stat():
    """Anti-datorie-stătută: ce s-a curățat iese din clichet, altfel poate reveni tăcut."""
    c = _f401()
    stat = ["  %s: clichet %d, real %d" % (f, n, c.get(f, 0))
            for f, n in sorted(BASELINE.items()) if c.get(f, 0) < n]
    assert not stat, ("clichetul e mai larg decât realitatea — coboară-l:\n" + "\n".join(stat))
