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
Validatoarele instalate se citesc de pe DISC (validatoare_instalate/poate_valida), NU dintr-o
listă fixă aici (pe disc sunt ~60 de jaruri: toate cele 50 de tipuri din DECLARATII + s1003/s1005
bilanț + câteva necablate). CHEIE_DUK (mai jos) mapează tip→cheie ANAF; gardată cu registrul de
core/test_registru_functionalitati.py.

TREI STARI, ca la verificatoarele incrucisate:
  valid — validatorul a rulat, fara erori
  erori — validatorul a rulat si a gasit erori (textul lor)
  gri   — NU PUTEM valida (validator neinstalat / java lipsa / timeout). Un XML
          nevalidat NU se declara valid: ar fi verde imprumutat.
"""
import os
import subprocess
import tempfile
import shutil

MODUL = "duk"
REGULI = "2026.1"

DIST = "/home/costin/duk/dist"
JAR = os.path.join(DIST, "DUKIntegrator.jar")
# DecValidation 2024 (din pachetul SAF-T) - ceruta de validatoarele de GENERATIE NOUA (ex. D216)
# care crapa cu DecValidation vechi din lib/ ("cod eroare"/NoClassDefFound/DECTag).
_DECVALIDATION_NOU = "/opt/duk/saft/val/duk_SAFT_an_luna/dist/lib/DecValidation.jar"

# D406 (SAF-T) se valideaza cu ALT jar si ALTI parametri: DUKIntegrator_AnLunaUI.jar
# -p D406 fisier.xml $ 0 0 out.pdf an=AAAA luna=LL. Dovedit in buildul vechi
# (/opt/iconta/main.py:10202, care valida D406 cap-coada).
# CU JAR-UL NORMAL SI "-v D406" VALIDATORUL IESE TACUT, FARA FISIER DE ERORI - ceea ce
# insemna "valid" pentru orice XML, INCLUSIV UNUL DE GUNOI (dovedit 15.07.2026: un
# <aiurea/> cu namespace inventat trecea ca "valid"). Un fals verde e mai periculos
# decat o eroare: iti spune ca poti depune ceva ce ANAF va respinge.
DIST_SAFT = "/opt/duk/saft/val/duk_SAFT_an_luna/dist"
JAR_SAFT = os.path.join(DIST_SAFT, "DUKIntegrator_AnLunaUI.jar")
JAVA_SAFT = "/opt/duk/jre8/bin/java"
TIPURI_SAFT = frozenset(("d406",))

CHEIE_DUK = {
    "d100": "D100", "d101": "D101", "d104": "D104", "d107": "D107", "d110": "D110", "d112": "D112", "d177": "D177", "d205": "D205", "d207": "D207", "d220": "D220", "d221": "D221", "d223": "D223", "d230": "D230",
    "d300": "D300", "d301": "D301", "d307": "D307", "d311": "D311", "d390": "D390", "d394": "D394",
    "d406": "D406", "s1003": "S1003", "s1005": "S1005", "d710": "D710",
    "d120": "D120", "d200": "D200", "d201": "D201", "d204": "D204", "d208": "D208",
    "d216": "D216", "d393": "D393", "d395": "D395", "d397": "D397", "d600": "D600",
    "d106": "D106", "d108": "D108", "d114": "D114", "d130": "D130", "d318": "D318", "d603": "D603",
    "d119": "D119", "d169n": "D169n", "d213": "D213", "d214": "D214", "d401": "D401", "d402": "D402",
    "d101g": "D101G", "d169": "D169", "d398": "D398", "d399": "D399", "d403": "D403", "d407": "D407",
    "d212": "D212",
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


def versiune_validator(tip, dist=DIST):
    """CU CE s-a validat: numele jarului ANAF si amprenta lui, sau None daca nu e instalat.

    [R41] Un verdict dat de un validator vechi nu e acelasi lucru cu unul dat de cel curent.
    Pachetul DUKIntegrator se actualizeaza de la ANAF, iar jarurile se schimba sub noi - deci
    versiunea nu se poate citi dintr-o constanta, se citeste de pe DISC, ca si `validatoare_instalate`.
    """
    import hashlib
    cheie = CHEIE_DUK.get(tip)
    if not cheie:
        return None
    cale = os.path.join(dist, "lib", "%sValidator.jar" % cheie)
    if not os.path.exists(cale):
        return None
    h = hashlib.sha256()
    with open(cale, "rb") as fh:
        for bucata in iter(lambda: fh.read(1 << 20), b""):
            h.update(bucata)
    return "%sValidator.jar sha256:%s" % (cheie, h.hexdigest()[:16])


def poate_valida(tip, dist=DIST):
    cheie = CHEIE_DUK.get(tip)
    return bool(cheie) and cheie in validatoare_instalate(dist)


def _gri(cheie, temei, limita="XML-ul a fost generat, dar NU validat la ANAF."):
    return {"stare": "gri", "erori": "", "severitate": None, "cheie": cheie, "temei": temei,
            "limita": limita, "modul": MODUL, "reguli": REGULI}


LIMITA = ("Validare structura si reguli ANAF. NU verifica daca cifrele corespund "
          "evidentei contabile - pentru asta e controlul incrucisat.")


def severitate(rez):
    """Clasifica output-ul DUK pe SEVERITATE reala: 'eroare' (linie E:, blocheaza depunerea la ANAF) vs
    'atentionare' (linie A:, NU blocheaza - dovedit live 08.08: 'A: asigurat...' vs 'E: angajator...') vs
    None (fara output). DUK pune ORICE iesire in stare='erori', dar o atentionare (A:) nu e o eroare.
    FAIL-SAFE: un output prezent dar neclasificat (sau care contine vreo linie E:) -> 'eroare'; niciodata nu
    se retrograda un E: sau un format necunoscut la 'atentionare' (un fals-verde ar fi mai grav decat
    supra-avertizarea)."""
    if not rez or not rez.strip():
        return None
    linii = [l.strip() for l in rez.splitlines() if l.strip()]
    if any(l.startswith("E:") for l in linii):
        return "eroare"
    if any(l.startswith("A:") for l in linii):
        return "atentionare"
    return "eroare"  # output prezent, format nerecunoscut -> tratat ca eroare (fail-safe)


def _valideaza_saft(xml, tip, an=None, luna=None, timeout=300):
    """D406/SAF-T: jar separat, -p cu an/luna, succesul = PDF generat.
    Fara an/luna nu se poate valida -> gri (nu 'valid')."""
    import subprocess as _sp
    if not os.path.exists(JAR_SAFT):
        return _gri("D406", "Validatorul SAF-T (DUKIntegrator_AnLunaUI.jar) nu e instalat.")
    if not an or not luna:
        return _gri("D406", "Validarea D406 cere an si luna (validatorul SAF-T le "
                            "primeste ca parametri).")
    td = tempfile.mkdtemp(prefix="duk_d406_")
    xp = os.path.join(td, "d.xml")
    lp = os.path.join(td, "r.txt")
    pp = os.path.join(td, "o.pdf")
    try:  # try/finally: continutul (r.txt/.err.txt/PDF) se citeste INAINTE de rmtree; tempdir-ul se curata mereu
        try:
            with open(xp, "w", encoding="utf-8") as fh:
                fh.write(xml)
            # Apelul e cel din doc/Instructiuni.txt al pachetului SAF-T (sursa oficiala):
            #   java -Xms250m -Xmx4g -jar DUKIntegrator_AnLunaUI.jar -v D406 d406.xml $ $ an=2025 luna=8
            # "$" = valoare implicita pentru parametrii optionali. Memoria marita e ceruta de ANAF (SAF-T mari).
            _sp.run([JAVA_SAFT, "-Djava.awt.headless=true", "-Xms250m", "-Xmx4g",
                     "-jar", JAR_SAFT, "-v", "D406", xp, lp, "$",
                     "an=%d" % an, "luna=%d" % luna],
                    cwd=DIST_SAFT, capture_output=True, text=True, timeout=timeout)
        except Exception as e:
            return _gri("D406", "Validatorul SAF-T nu a putut fi rulat: %s." % e)
        temei = "DUKIntegrator_AnLunaUI -v D406 (validator SAF-T, pachet oficial ANAF)."
        rez = ""
        for f in (lp, xp + ".err.txt"):
            if os.path.exists(f):
                with open(f, encoding="utf-8", errors="replace") as fh:
                    rez = (rez + "\n" + fh.read()).strip()
        if rez.lower() in ("ok", "ok."):
            rez = ""
        if not rez:
            # Fara fisier de rezultat NU declaram "valid": exact asa aparea D406 verde pe orice gunoi.
            # Cerem o dovada pozitiva - fisier de rezultat sau PDF (citite AICI, inainte de finally/rmtree).
            if os.path.exists(lp) or (os.path.exists(pp) and os.path.getsize(pp) > 0):
                return {"stare": "valid", "erori": "", "severitate": None, "cheie": "D406", "temei": temei,
                        "limita": LIMITA, "modul": MODUL, "reguli": REGULI}
            return _gri("D406", "Validatorul SAF-T nu a produs nici rezultat, nici erori - "
                                "nu putem confirma ca declaratia e valida.")
        return {"stare": "erori", "erori": rez, "severitate": severitate(rez), "cheie": "D406",
                "temei": temei, "limita": LIMITA, "modul": MODUL, "reguli": REGULI}
    finally:
        shutil.rmtree(td, ignore_errors=True)


def valideaza(xml, tip, dist=DIST, timeout=180, an=None, luna=None):
    """Intoarce {stare, erori, cheie, temei, limita}. Esecul rularii = 'gri', nu 'valid'."""
    cheie = CHEIE_DUK.get(tip)
    if not cheie:
        return _gri(None, "Tip necunoscut: %r." % tip)
    if tip in TIPURI_SAFT:
        return _valideaza_saft(xml, tip, an=an, luna=luna, timeout=max(timeout, 300))
    if cheie not in validatoare_instalate(dist):
        return _gri(cheie, "Validatorul %s nu e instalat in pachetul DUKIntegrator." % cheie,
                    "XML generat, NU validat. Instaleaza validatorul de la ANAF "
                    "(config/config.properties -> urlVersiuni).")
    td = tempfile.mkdtemp(prefix="duk_%s_" % tip)
    xp = os.path.join(td, "d.xml")
    lp = os.path.join(td, "r.txt")

    def _citeste():
        r = ""
        for f in (lp, xp + ".err.txt"):
            if os.path.exists(f):
                with open(f, encoding="utf-8", errors="replace") as fh:
                    r = (r + "\n" + fh.read()).strip()
        return r

    _MARK_ESEC = ("cod eroare", "Erori la validare", "NoClassDefFound", "DECTag", "Exception in thread")
    try:  # try/finally: continutul se citeste INAINTE de rmtree; tempdir-ul se curata mereu
        try:
            with open(xp, "w", encoding="utf-8") as fh:
                fh.write(xml)
            p = subprocess.run(["java", "-Djava.awt.headless=true", "-jar",
                                os.path.join(dist, "DUKIntegrator.jar"), "-v", cheie, xp, lp],
                               cwd=td, capture_output=True, text=True, timeout=timeout)
        except Exception as e:
            return _gri(cheie, "Validatorul nu a putut fi rulat: %s." % e)
        rez = _citeste()
        out = (p.stdout or "") + "\n" + (p.stderr or "")
        # Validator de GENERATIE NOUA (ex. D216): DUKIntegrator.jar cu DecValidation.jar VECHI din lib/
        # crapa fara fisier de rezultat -> calea -jar ar raporta FALS "valid" (fisier gol = valid).
        # Reincercam cu DecValidation NOU (2024, pachet SAF-T) pe classpath (general.Main) - metoda
        # dovedita ca da 'ok'/erori reale pe validatoarele noi.
        if (not rez) and any(m in out for m in _MARK_ESEC) and os.path.exists(_DECVALIDATION_NOU):
            try:
                if os.path.exists(lp):
                    os.remove(lp)
                cp = os.pathsep.join([_DECVALIDATION_NOU, os.path.join(dist, "DUKIntegrator.jar"),
                                      os.path.join(dist, "lib", "*")])
                p = subprocess.run(["java", "-Djava.awt.headless=true", "-cp", cp,
                                    "general.Main", "-v", cheie, xp, lp],
                                   cwd=dist, capture_output=True, text=True, timeout=timeout)
                rez = _citeste()
                out = (p.stdout or "") + "\n" + (p.stderr or "")
            except Exception as e:
                return _gri(cheie, "Validator generatie noua: reincercarea cu DecValidation nou a esuat: %s." % e)
        # "ok"/gol in fisierul de rezultat = valid (dovedit 15.07 pe D394).
        if rez.lower() in ("", "ok", "ok."):
            rez = ""
        # FAIL-SAFE anti fals-verde: eroare semnalata pe stdout FARA fisier de rezultat -> NU 'valid'.
        if (not rez) and any(m in out for m in _MARK_ESEC):
            return _gri(cheie, "Validatorul a semnalat eroare fara fisier de rezultat: %s."
                        % out.strip().replace("\n", " ")[:200])
        temei = "DUKIntegrator -v %s (pachet oficial ANAF)." % cheie
        stare = "erori" if rez else "valid"
        return {"stare": stare, "erori": rez, "severitate": severitate(rez), "cheie": cheie,
                "temei": temei, "limita": LIMITA, "modul": MODUL, "reguli": REGULI}
    finally:
        shutil.rmtree(td, ignore_errors=True)
