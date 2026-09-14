# -*- coding: utf-8 -*-
"""Fiecare „DUK regula <cod>" se confruntă cu validatorul DECLARAȚIEI unde e scrisă.

DE CE EXISTĂ. Pe 30.07.2026 opt mențiuni au fost canonizate la forma `DUK regula <cod>` — s-a
schimbat MARCAJUL, nu s-a verificat conținutul. Datoria scrisă atunci spunea limpede riscul: *dacă
vreuna cita o regulă greșită înainte, canonizarea a făcut-o să arate corect și să rămână greșită.*
Verificată la sursă pe 14.09.2026, frica s-a adeverit de trei ori din opt. Cea mai curată instanță:
`A91b` era citată ca temei al rotunjirii în D300 și D390, dar A91b **nu există** în
`D300Validator.jar` și nici în `D390Validator.jar` — e o regulă din D112 („Contribuția angajator CAM
nu este calculată corect"), care într-adevăr respinsese rotunjirea bancară, dar pe D112.

CE MĂSOARĂ, scris îngust ca să nu fie citit mai larg decât e: **codul citat există în jarul
declarației în care e citat?** Atât. Nu poate spune dacă regula înseamnă ce credem noi că înseamnă
— pentru asta se rulează validatorul pe un XML mutat, cum s-a făcut azi la D100, D119 și D710.

UNDE E OARB, prin construcție:
  * Codurile scurte (`R4`, `R15`) apar aproape sigur ca subșir undeva într-un jar de câțiva MB.
    Deci instrumentul greșește spre INDULGENȚĂ: raportează „prezent" și când e coincidență. Puterea
    lui e pe codurile distinctive (`A91b`, `F10_68`, `SP1B4_1`) — exact clasa care s-a dovedit
    greșită. Numărul de coduri pe care le poate discrimina e RAPORTAT, nu presupus (`discriminante`).
  * Un jar neinstalat nu e o mențiune greșită: se raportează separat, ca lipsă de dovadă.
  * Fișierele fără declarație proprie în nume (`temeiuri.py`, `test_cale_a_doua.py`) se verifică pe
    TOATE validatoarele instalate — deci pentru ele instrumentul e și mai indulgent.
"""
from __future__ import annotations

import io
import os
import re
import zipfile

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_URI = ("/opt/duk/dist", os.path.expanduser("~/duk/dist"),
            "/opt/duk/saft/val/duk_SAFT_an_luna/dist")   # SAF-T (D406) e un pachet separat

# Citarea canonică, așa cum o cere `core/test_temeiuri.py`, plus marca de declarație: o regulă
# împrumutată de la alt formular ÎȘI NUMEȘTE formularul — `DUK regula A91b (D112)`. Fără marcă,
# codul se caută în validatorul fișierului, care e presupunerea implicită a oricărui cititor.
MENTIUNE = re.compile(r"DUK regula ([A-Za-z][A-Za-z0-9_.]*[A-Za-z0-9])(?:\s*\((D\d+[A-Za-z]?|S\d{4})\))?")
# Numele declarației din numele fișierului: `d112_reconciliere.py` -> d112, `test_d101_x.py` -> d101.
DIN_NUME = re.compile(r"(?:^|_)(d\d+[a-z]*|s\d{4})(?:_|$|\.)")

# Fișiere fără declarație în nume. Motivul, lângă fiecare — nu o listă tăcută.
FARA_DECLARATIE = {
    "core/bilant.py": ("s1005", "s1003"),          # F10 e formularul comun al celor două kituri
}
# Declarații ale căror reguli NU stau într-un jar. Verificat pe disc: `S.I.26` nu apare în niciunul
# din cele trei jaruri D406 instalate — SAF-T se validează pe schemă + documentația ANAF, nu pe un
# catalog de reguli compilat. Absența de acolo nu e o citare greșită, e altă sursă.
SURSA_NU_E_JAR = {"d406": "SAF-T: regulile vin din documentația ANAF, nu din jar"}
# Un cod de regulă are o CIFRĂ. „DUK regula suprafata" e proză prinsă de tipar, nu o citare — iar
# un instrument care o numără greșit învață pe cineva să-l ocolească.
ARE_CIFRA = re.compile(r"\d")

_BLOB = {}


def _dist_pentru(cheie):
    """Primul dist care are `<Cheie>Validator.jar`. Discul e sursa, nu o listă în cod."""
    for d in DIST_URI:
        cale = os.path.join(d, "lib", "%sValidator.jar" % cheie.upper().replace("D", "D", 1))
        for nume in (cheie.upper(), cheie.capitalize(), cheie):
            c = os.path.join(d, "lib", "%sValidator.jar" % nume)
            if os.path.isfile(c):
                return c
        if os.path.isfile(cale):
            return cale
    return None


def jar_declaratiei(decl):
    """Calea jarului instalat pentru declarație, sau None. `d101g` -> D101GValidator.jar."""
    v = _dist_pentru(decl)
    if v:
        return v
    # cheile ANAF nu sunt uniform majuscule (D169n, S1005): se caută case-insensitive pe disc
    tinta = ("%svalidator.jar" % decl).lower()
    for d in DIST_URI:
        lib = os.path.join(d, "lib")
        if not os.path.isdir(lib):
            continue
        for f in os.listdir(lib):
            if f.lower() == tinta:
                return os.path.join(lib, f)
    return None


def _continut(jar):
    """Toți octeții claselor dintr-un jar, o singură dată pe proces."""
    if jar not in _BLOB:
        bucati = []
        with zipfile.ZipFile(jar) as z:
            for info in z.infolist():
                if info.filename.endswith(".class"):
                    bucati.append(z.read(info))
        _BLOB[jar] = b"".join(bucati)
    return _BLOB[jar]


def codul_e_in_jar(cod, jar):
    return cod.encode("ascii", "ignore") in _continut(jar)


def _surse(radacini=None):
    for rad in (radacini or [RAD]):
        for dirpath, dirnames, files in os.walk(rad):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "venv", "__pycache__", "node_modules", ".lant_tmp")]
            for f in files:
                if f.endswith(".py"):
                    cale = os.path.join(dirpath, f)
                    yield (os.path.relpath(cale, rad).replace("\\", "/"),
                           io.open(cale, encoding="utf-8", errors="ignore").read())


def mentiuni(surse=None):
    """[{fisier, linia, cod, declaratii}] — fiecare citare canonică, cu declarația ei."""
    out = []
    for rel, text in (surse if surse is not None else _surse()):
        if rel.startswith("scripts/scan_coduri_validator") or rel.endswith("test_coduri_validator.py"):
            continue  # instrumentul și garda lui citează coduri ca EXEMPLE, nu ca temei
        baza = os.path.basename(rel)[:-3]
        m = DIN_NUME.search(baza)
        decl = (m.group(1),) if m else FARA_DECLARATIE.get(rel, ())
        for nr, linie in enumerate(text.splitlines(), 1):
            for cod, marca in MENTIUNE.findall(linie):
                if not ARE_CIFRA.search(cod):
                    continue
                out.append({"fisier": rel, "linia": nr, "cod": cod,
                            "declaratii": (marca.lower(),) if marca else decl})
    return out


def confrunta(surse=None):
    """(necorelate, fara_validator, discriminante) — ce spune discul despre fiecare citare."""
    necorelate, fara_validator, discriminante = [], [], 0
    for m in mentiuni(surse):
        if any(d in SURSA_NU_E_JAR for d in m["declaratii"]):
            fara_validator.append(m)
            continue
        decls = m["declaratii"] or tuple(sorted(_instalate()))
        jare = [(d, jar_declaratiei(d)) for d in decls]
        instalate = [(d, j) for d, j in jare if j]
        if not instalate:
            fara_validator.append(m)
            continue
        if len(m["cod"]) >= 4:
            discriminante += 1        # sub 4 caractere, prezența e aproape sigur coincidență
        if not any(codul_e_in_jar(m["cod"], j) for _d, j in instalate):
            necorelate.append(dict(m, cautat_in=[d for d, _j in instalate]))
    return necorelate, fara_validator, discriminante


def _instalate():
    chei = set()
    for d in DIST_URI:
        lib = os.path.join(d, "lib")
        if os.path.isdir(lib):
            for f in os.listdir(lib):
                if f.endswith("Validator.jar") and ".bak" not in f and f != "Validator.jar":
                    chei.add(f[:-len("Validator.jar")].lower())
    return chei


if __name__ == "__main__":
    nec, fara, disc = confrunta()
    print("citari: %d · discriminante (cod >= 4 car.): %d · fara validator instalat: %d"
          % (len(mentiuni()), disc, len(fara)))
    print("NECORELATE (codul nu apare in validatorul declaratiei): %d" % len(nec))
    for m in nec:
        print("  %s:%d  %s  (cautat in %s)" % (m["fisier"], m["linia"], m["cod"],
                                               "/".join(m["cautat_in"])))
