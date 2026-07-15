# -*- coding: utf-8 -*-
"""
core/duk.py — validare XML la DUKIntegrator (ANAF).

Sursa parametrilor: doc/Instructiuni.txt din pachetul ANAF instalat (15.07.2026):
    java -jar DUKIntegrator.jar [-c caleConfig] -v tipDeclaratie fisierXML [fisierRezultat]
Exemplu literal din Instructiuni.txt: `-v D112 C:/D112.xml`.
Dovedit pe server: `-v D112` acceptat; cheie gresita -> "sectiune necunoscuta".
(Buildul vechi folosea `-p` = validare + PDF, cu fisierZIP=0 la declaratiile fara ZIP.)

Validatoarele sunt jar-uri OFICIALE ANAF din lib/, descarcate dupa
config/config.properties -> urlVersiuni. NU se scriu de mana: un validator propriu
ar valida impotriva presupunerii noastre, nu a regulii ANAF.
Instalate 15.07.2026 din versiuni.xml: D100_75, D101_56, D112_209, D205_36, D300_27,
D301_9, D390_11, D394_31, D406_35, S1003_38, S1005_41.

TREI STARI, ca la verificatoarele incrucisate:
  valid — validatorul a rulat, fara erori
  erori — validatorul a rulat si a gasit erori (textul lor)
  gri   — NU PUTEM valida (validator neinstalat / java lipsa / timeout). Un XML
          nevalidat NU se declara valid: ar fi verde imprumutat.
"""
import os
import subprocess
import tempfile

MODUL = "duk"
REGULI = "2026.1"

DIST = "/home/costin/duk/dist"
JAR = os.path.join(DIST, "DUKIntegrator.jar")

CHEIE_DUK = {
    "d100": "D100", "d101": "D101", "d112": "D112", "d205": "D205",
    "d300": "D300", "d301": "D301", "d390": "D390", "d394": "D394",
    "d406": "D406", "s1003": "S1003", "s1005": "S1005",
}


def validatoare_instalate(dist=DIST):
    """Cheile pentru care exista <cheie>Validator.jar in lib/. Sursa de adevar e
    DISCUL, nu o lista in cod: pachetul se actualizeaza de la ANAF."""
    lib = os.path.join(dist, "lib")
    if not os.path.isdir(lib):
        return set()
    # Validator.jar (fara prefix) e biblioteca de baza DUK, nu o declaratie:
    # fara filtrul pe cheie goala, poate_valida("") ar raspunde True.
    return {f[:-len("Validator.jar")] for f in os.listdir(lib)
            if f.endswith("Validator.jar") and ".bak" not in f
            and f != "Validator.jar"}


def poate_valida(tip, dist=DIST):
    cheie = CHEIE_DUK.get(tip)
    return bool(cheie) and cheie in validatoare_instalate(dist)


def _gri(cheie, temei, limita="XML-ul a fost generat, dar NU validat la ANAF."):
    return {"stare": "gri", "erori": "", "cheie": cheie, "temei": temei,
            "limita": limita, "modul": MODUL, "reguli": REGULI}


LIMITA = ("Validare structura si reguli ANAF. NU verifica daca cifrele corespund "
          "evidentei contabile - pentru asta e controlul incrucisat.")


def valideaza(xml, tip, dist=DIST, timeout=180):
    """Intoarce {stare, erori, cheie, temei, limita}. Esecul rularii = 'gri', nu 'valid'."""
    cheie = CHEIE_DUK.get(tip)
    if not cheie:
        return _gri(None, "Tip necunoscut: %r." % tip)
    if cheie not in validatoare_instalate(dist):
        return _gri(cheie, "Validatorul %s nu e instalat in pachetul DUKIntegrator." % cheie,
                    "XML generat, NU validat. Instaleaza validatorul de la ANAF "
                    "(config/config.properties -> urlVersiuni).")
    td = tempfile.mkdtemp(prefix="duk_%s_" % tip)
    xp = os.path.join(td, "d.xml")
    lp = os.path.join(td, "r.txt")
    try:
        with open(xp, "w", encoding="utf-8") as fh:
            fh.write(xml)
        subprocess.run(["java", "-Djava.awt.headless=true", "-jar",
                        os.path.join(dist, "DUKIntegrator.jar"), "-v", cheie, xp, lp],
                       cwd=td, capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return _gri(cheie, "Validatorul nu a putut fi rulat: %s." % e)
    rez = ""
    for f in (lp, xp + ".err.txt"):
        if os.path.exists(f):
            with open(f, encoding="utf-8", errors="replace") as fh:
                rez = (rez + "\n" + fh.read()).strip()
    # Validatorul scrie literalmente "ok" in fisierul de rezultat cand nu gaseste erori
    # (dovedit 15.07.2026 pe D394). Fara asta, o declaratie VALIDA era raportata ca
    # avand eroarea "ok" - fals negativ care ar fi trimis contabilul sa caute o
    # problema inexistenta. Fisier gol = idem valid (unele validatoare nu-l scriu).
    if rez.lower() in ("", "ok", "ok."):
        rez = ""
    temei = "DUKIntegrator -v %s (pachet oficial ANAF)." % cheie
    stare = "erori" if rez else "valid"
    return {"stare": stare, "erori": rez, "cheie": cheie, "temei": temei,
            "limita": LIMITA, "modul": MODUL, "reguli": REGULI}
