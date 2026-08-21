# -*- coding: utf-8 -*-
"""GARD PESTE GĂRZI (21.08.2026): ancora unui gard trăiește în COD, nu în PROZĂ.

Clasa a apărut de TREI ori într-o singură zi:
  1. Gardul TEMA D căuta „fallback" lângă „21" în docstring — și l-a găsit în fraza care explică DE CE
     fallback-ul e greșit. Un gard care nu deosebește afirmația de negația ei.
  2. `lit.?\\s*[a-z]\\)` din scanul de constante s-a aprins pe cuvântul „po-LIT-e)" din antetul lui
     `d403` și a „sursat" cinci constante cu o coincidență ortografică.
  3. `test_randerul_chiar_o_afiseaza` a rămas VERDE după ce titlul secțiunii a fost șters din randare,
     fiindcă îl găsea în comentariul de deasupra. Prins abia de RED-proof-ul cerut de Costin.

Un gard a cărui ancoră trăiește doar într-un comentariu **rezistă exact la mutația care ar trebui
să-l facă roșu** — deci raportează verde despre o lume pe care n-o vede.

CE VEDE ȘI CE NU (numărat, nu tăcut): din 39 de ancore, 12 se pot rezolva la un fișier unic; 16 sunt
în funcții care citesc MAI MULTE surse (nu se știe care aserțiune se referă la care), iar 11 au căi
pe care rezolvarea nu le prinde. Cele 27 NU sunt raportate ca trecute — sunt raportate ca
neverificate, fiindcă absența unei verificări nu e o verificare.
"""
import pytest

from core import scan_ancore

# Instalat 21.08.2026 pe o lume curată (0 în proză). Acoperirea se RIDICĂ dacă rezolvarea se
# îmbunătățește; nu se coboară tăcut.
ACOPERIRE_BASELINE = 12


@pytest.fixture(scope="module")
def inv():
    return scan_ancore.inventar()


def test_nicio_ancora_nu_traieste_doar_in_proza(inv):
    """Miezul. Dacă șirul căutat există doar într-un comentariu sau docstring al fișierului țintă,
    gardul e ancorat în proză — și va supraviețui ștergerii codului pe care pretinde că-l păzește."""
    rele = ["  %s::%s -> %r" % (f, fn, a[:70]) for f, fn, a, s in inv if s == "PROZA"]
    assert not rele, (
        "gărzi ancorate în PROZĂ (șirul există doar în comentarii/docstring):\n" + "\n".join(rele)
        + "\n\nMută ancora pe ceva ce nu poate fi satisfăcut de un comentariu: un artefact de "
        "randare, o valoare returnată, o structură din payload.")


def test_nicio_ancora_absenta(inv):
    """O ancoră care nu există deloc în fișierul țintă înseamnă că gardul păzește altceva decât crede."""
    rele = ["  %s::%s -> %r" % (f, fn, a[:70]) for f, fn, a, s in inv if s == "absent"]
    assert not rele, "gărzi cu ancoră inexistentă în fișierul citit:\n" + "\n".join(rele)


def test_acoperirea_nu_scade(inv):
    """Clichet pe VEDERE, nu pe defecte: dacă rezolvarea se strică, gardul ar trece pe gol cu tot
    mai puține ancore verificate — verde fiindcă nu se mai uită."""
    n = sum(1 for _f, _fn, _a, s in inv if s in ("cod", "PROZA", "absent"))
    assert n >= ACOPERIRE_BASELINE, (
        "ancore verificabile: %d < %d — rezolvarea fișierelor țintă s-a stricat, iar gardul vede mai "
        "puțin decât vedea." % (n, ACOPERIRE_BASELINE))


def test_ce_nu_se_vede_e_numarat(inv):
    """Zgomotul se NUMĂRĂ, nu se aruncă: cele neverificate trebuie să rămână vizibile ca atare."""
    from collections import Counter
    c = Counter(s for _f, _fn, _a, s in inv)
    assert c["ambiguu"] + c["nerezolvat"] > 0, (
        "toate ancorele sunt rezolvate — dacă e adevărat, ridică ACOPERIRE_BASELINE și scoate testul")
    assert len(inv) >= 30, "prea puține ancore văzute (%d) — verifică domeniul scanului" % len(inv)


def test_detectorul_chiar_deosebeste_proza_de_cod(tmp_path):
    """Anti-vacuu pe mecanism: fără asta, `fara_proza` ar putea întoarce textul neatins și totul ar
    părea „în cod". Se probează pe amândouă limbile pe care le scanăm."""
    py = 'x = 1  # ANCORA_DOAR_IN_COMENTARIU\nreal = "ANCORA_IN_COD"\n'
    curat = scan_ancore.fara_proza(py, "a.py")
    assert "ANCORA_DOAR_IN_COMENTARIU" not in curat and "ANCORA_IN_COD" in curat

    js = '// ANCORA_DOAR_IN_COMENTARIU\nconst t = "ANCORA_IN_COD";\n'
    curat = scan_ancore.fara_proza(js, "a.js")
    assert "ANCORA_DOAR_IN_COMENTARIU" not in curat and "ANCORA_IN_COD" in curat

    doc = '"""ANCORA_DOAR_IN_DOCSTRING."""\nreal = "ANCORA_IN_COD"\n'
    curat = scan_ancore.fara_proza(doc, "a.py")
    assert "ANCORA_DOAR_IN_DOCSTRING" not in curat and "ANCORA_IN_COD" in curat


def test_functiile_cu_mai_multe_surse_nu_sunt_acuzate(inv):
    """Contra-direcția, legată fiindcă s-a întâmplat la calibrare: o funcție care citește DOUĂ fișiere
    a fost raportată „ancoră absentă", deși gardul era corect — ancora era în al doilea fișier.
    Ambiguu ≠ greșit."""
    assert any(s == "ambiguu" for _f, _fn, _a, s in inv), (
        "nicio funcție cu surse multiple — categoria «ambiguu» nu mai e exercitată, deci nu se știe "
        "dacă ar mai fi tratată corect")
