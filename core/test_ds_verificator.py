# -*- coding: utf-8 -*-
"""GARDĂ [R103, 30.08.2026]: legătura `DESIGN_SYSTEM.md` → `verificator_conformitate.py` nu mai
poate slăbi tăcut.

DE UNDE VINE. Regula de proces — *orice regulă din DS intră SIMULTAN în verificator* — exista
**scrisă** și a fost încălcată **de trei ori pe aceeași regulă** (steluțele pe câmpurile
obligatorii: de două ori în iulie, o dată pe 30.08). Nimic nu se aprindea, fiindcă **nimic nu păzea
regula de proces**. Măsurat atunci: din 62 de reguli ale DS, **5** acoperite.

Costin, când a cerut garda: *„Nu pentru cele 24, ci pentru gardă: lipsa ei e cauza, cele 24 sunt
efectul. Fără ea, măsurătoarea de azi îmbătrânește din prima regulă nouă."*

CE FACE IMPOSIBIL: o regulă NOUĂ în DS care numește ceva concret și nu ajunge în verificator ·
o regulă care iese tăcut din acoperire · o regulă scrisă fără nicio ancoră, adăugată peste cele 18
existente.

CE NU FACE, declarat: **nu obligă la acoperire**, ci la **decizie**. Clichetele sunt praguri, nu
zerouri: cele 24 de neacoperite și cele 18 fără ancoră sunt datorie **cunoscută**, iar garda le
îngheață. Nu spune nici că o regulă „ATINSĂ" e bine păzită — pentru asta e starea
`DOAR LA SUPRAFAȚĂ`, care nu se poate închide cu un instrument static (vezi R103).
"""
import io
import os

import pytest

import sys as _sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sys.path.insert(0, os.path.join(_RAD, "scripts"))

import scan_ds_verificator as scan  # noqa: E402

# CLICHETE, măsurate pe `80cebd5` (30.08.2026). Fiecare e un PLAFON, nu o țintă.
PLAFON_NEACOPERITE = 24
PLAFON_FARA_ANCORA = 18
PODEA_ACOPERITE = 5


@pytest.fixture(scope="module")
def masurat():
    regs = scan.masoara()
    assert len(regs) >= 55, (
        "ANTI-VACUU: doar %d reguli extrase din DESIGN_SYSTEM.md — cititorul s-a rupt, iar toate "
        "clichetele de mai jos ar trece pe o mulțime goală" % len(regs))
    capitole = {r["cap"] for r in regs}
    assert len(capitole) >= 20, "ANTI-VACUU: doar %d capitole văzute" % len(capitole)
    return regs


def _cate(regs, stare):
    return sum(1 for r in regs if r["stare"] == stare)


def test_regulile_neacoperite_nu_cresc(masurat):
    """Clichet: o regulă nouă cu ancoră trebuie să ajungă în verificator, ori să fie decisă altfel."""
    n = _cate(masurat, "NEACOPERITĂ")
    assert n <= PLAFON_NEACOPERITE, (
        "reguli din DS necunoscute verificatorului: %d > %d.\n"
        "O regulă nouă care numește ceva concret intră ÎN VERIFICATOR odată cu DS-ul — asta e "
        "regula de proces pe care lipsa gărzii ăsteia a lăsat-o să fie încălcată de trei ori.\n"
        "Dacă nu se poate acoperi, se scrie de ce, iar plafonul se ridică PRIN DECIZIE." % (
            n, PLAFON_NEACOPERITE))


def test_acoperirea_nu_scade(masurat):
    """Cealaltă direcție: o regulă nu are voie să IASĂ tăcut din acoperire."""
    n = _cate(masurat, "ACOPERITĂ")
    assert n >= PODEA_ACOPERITE, (
        "reguli acoperite: %d < %d — ceva a ieșit din acoperire fără să fie observat" % (
            n, PODEA_ACOPERITE))


def test_regulile_fara_ancora_nu_cresc(masurat):
    """O regulă din DS care nu poate fi ancorată e o PREFERINȚĂ, nu o normă (Costin, 30.08.2026).

    Nu e o limită a instrumentului — e un defect al regulii. Clichetul îl îngheață: se pot repara,
    nu se pot înmulți.
    """
    n = _cate(masurat, "FĂRĂ ANCORĂ")
    assert n <= PLAFON_FARA_ANCORA, (
        "reguli din DS care nu numesc nimic concret: %d > %d.\n"
        "O regulă care nu se poate ancora nu se poate verifica — deci nu e normă, e preferință. "
        "Se rescrie ca să numească un artefact, sau se mută din secțiunea de reguli." % (
            n, PLAFON_FARA_ANCORA))


def test_regula_stelutelor_e_INCA_neacoperita_si_se_vede(masurat):
    """ANCORA MĂSURĂTORII: instanța care a cerut garda trebuie să rămână vizibilă până se repară.

    Dacă cineva „repară" instrumentul până când regula steluțelor dispare din listă fără ca
    verificatorul s-o cunoască, aici cade. Când regula chiar intră în verificator, testul ăsta se
    schimbă ODATĂ cu ea — și atunci schimbarea e o reparație, nu o pierdere.
    """
    _ANCORA = "oblig"
    reg = [r for r in masurat if _ANCORA in r["ancore"] and r["cap"] == "6"]
    assert reg, "regula câmpului obligatoriu a dispărut din cititorul de DS"
    assert all(r["stare"] == "NEACOPERITĂ" for r in reg), (
        "regula steluțelor nu mai e neacoperită — dacă a intrat în verificator, actualizează "
        "clichetele și testul ăsta; dacă nu, instrumentul a început să mintă")


def test_cititorul_de_DS_chiar_vede_regulile():
    """ANTI-VACUU pe cealaltă sursă: un cititor rupt ar face toate clichetele să treacă pe zero."""
    text = ("## 6. Test\n\n"
            "- **Câmp inventat (v9.9)**: marcat cu `<span class=\"inventat-xyz\">*</span>`.\n"
            "- o propoziție fără marcaj normativ și fără ancoră\n")
    cap = scan._capitole(text)
    assert len(cap) == 1 and cap[0][0] == "6", cap
    puncte = scan._puncte(text)
    assert len(puncte) == 2, puncte


def test_calibrare_o_ancora_absenta_iese_NEACOPERITA(tmp_path, monkeypatch):
    """CALIBRARE ÎN DIRECȚIA DE EȘEC (regula lui R100).

    Instrumentul își declară direcția: *„randat/acoperit e supra-numărat, deci golul e plafon
    inferior."* Cazul care ar CĂDEA dacă direcția e inversă: o regulă cu o ancoră care sigur NU e în
    verificator trebuie să iasă NEACOPERITĂ. Dacă instrumentul ar începe să raporteze acoperire
    fabricată — cum a făcut prima lui formă, cu ancore generice — aici cade.
    """
    ds = tmp_path / "DESIGN_SYSTEM.md"
    ds.write_text("## 6. Proba\n\n- **Regula inventata (v9.9)**: obligatoriu prin "
                  "`clasa-care-nu-exista-nicaieri`.\n", encoding="utf-8")
    verif = tmp_path / "verificator_conformitate.py"
    verif.write_text("# nimic despre regula aia\nX = 1\n", encoding="utf-8")
    monkeypatch.setattr(scan, "DS", str(ds))
    monkeypatch.setattr(scan, "VERIF", str(verif))
    regs = scan.masoara()
    assert len(regs) == 1, regs
    assert regs[0]["stare"] == "NEACOPERITĂ", regs[0]


def test_calibrare_o_ancora_PREZENTA_iese_acoperita(tmp_path, monkeypatch):
    """Cealaltă direcție: dacă nimic n-ar fi vreodată acoperit, testul de mai sus ar trece degeaba."""
    ds = tmp_path / "DESIGN_SYSTEM.md"
    ds.write_text("## 6. Proba\n\n- **Regula inventata (v9.9)**: canonic prin "
                  "`clasa-inventata-xyz`.\n", encoding="utf-8")
    verif = tmp_path / "verificator_conformitate.py"
    verif.write_text('INTERZISE = ["clasa-inventata-xyz"]\n', encoding="utf-8")
    monkeypatch.setattr(scan, "DS", str(ds))
    monkeypatch.setattr(scan, "VERIF", str(verif))
    regs = scan.masoara()
    assert len(regs) == 1, regs
    assert regs[0]["stare"] in ("ACOPERITĂ", "DOAR LA SUPRAFAȚĂ"), regs[0]


def test_ancora_in_comentariu_nu_e_acoperire(tmp_path, monkeypatch):
    """O ancoră care apare doar în PROZA verificatorului descrie, nu verifică.

    E cazul real al regulii steluțelor: `oblig` apare de trei ori în fișier, toate în comentarii
    despre altceva.
    """
    ds = tmp_path / "DESIGN_SYSTEM.md"
    ds.write_text("## 6. Proba\n\n- **Regula inventata (v9.9)**: canonic prin "
                  "`clasa-doar-in-comentariu`.\n", encoding="utf-8")
    verif = tmp_path / "verificator_conformitate.py"
    verif.write_text("# despre clasa-doar-in-comentariu vorbim, dar n-o verificam\nY = 2\n",
                     encoding="utf-8")
    monkeypatch.setattr(scan, "DS", str(ds))
    monkeypatch.setattr(scan, "VERIF", str(verif))
    regs = scan.masoara()
    assert regs[0]["stare"] == "NEACOPERITĂ", regs[0]
    assert regs[0]["ancore_doar_proza"], "ancora din comentariu trebuie NUMITĂ, nu doar ignorată"


def test_instrumentul_e_langa_garda():
    """Instrumentul trăiește în `scripts/`, garda în `core/`: dacă e mutat, aici se vede."""
    assert os.path.exists(os.path.join(_RAD, "scripts", "scan_ds_verificator.py"))
    assert io.open(os.path.join(_RAD, "DESIGN_SYSTEM.md"), encoding="utf-8").read().count("## ") > 20
