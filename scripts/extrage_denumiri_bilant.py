# -*- coding: utf-8 -*-
"""scripts/extrage_denumiri_bilant.py — denumirile rândurilor din formularele de bilanț, extrase din documentul de STRUCTURĂ ANAF
(`anaf_surse/structura_SC_1225_270126.pdf`, „Structura” de pe pagina S1002-S1003-S1004-S1005 / 2025, static.anaf.ro;
textul: `pdftotext -layout` -> `anaf_surse/structura_SC_1225_270126.txt`). Deficiența 227 (comanda Costin 12.10.2026, verbatim în
DECIZII): „la completarea manuală a coloanei «An precedent» din bilanț, fiecare rând arată denumirea de pe formular, nu doar «rândul 41».”

Codul câmpului e `F<sec>_<RRR><C>`: RRR = rândul formularului, C = coloana (1 = an precedent, 2 = an curent). Denumirea = textul
rândului, fără formula de conturi dintre paranteze („(ct. …)”, „(din ct. …)”) și fără notele formularului; trimiterile la rânduri
(„(rd. 01 + 02 + 03)”) rămân, ca la totaluri. Secțiunile: F10_BS (S1003, S1005), F20_micro (S1005), F20 (rd.1-70; S1003), F30 cap.I-XII (datele informative).

Uz: python scripts/extrage_denumiri_bilant.py           -> tipărește dicționarul
    python scripts/extrage_denumiri_bilant.py --scrie   -> rescrie `core/bilant_denumiri.py` (pazit de core/test_bilant_denumiri.py)
"""
import io
import os
import pprint
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA = os.path.join(RAD, "anaf_surse", "structura_SC_1225_270126.txt")
TINTA = os.path.join(RAD, "core", "bilant_denumiri.py")
#: (formular, secțiune) -> antetul secțiunii din structură; secțiunea se încheie la primul antet de secțiune următor
SECTIUNI = {("s1005", "F10"): "F10_BS (rd.1-49,301,302) S1003, S1005", ("s1003", "F10"): "F10_BS (rd.1-49,301,302) S1003, S1005",
            ("s1005", "F20"): "F20_micro (rd.1-9) S1005", ("s1003", "F20"): "F20 (rd.1-70) S1002, S1003, S1004",
            # [C11, 12.10.2026] și datele informative (F30, cap.I-XII), pe care „Ce se depune” le arată tot cu numărul rândului
            ("s1005", "F30"): "F30_capital (rd.1-148, 301-303, 305, 306,316-321) cap.I-XII S1005",
            ("s1003", "F30"): "F30_capital_MM (rd.1- 152,301-311,313,314,316-321) cap.I-XII S1002-S1003-S1004"}
_ANTET = re.compile(r"^\s{0,12}(F10_|F20|F30_|F40)\S*\s*\(rd\.")
_CAMP = re.compile(r"^(?:\S+\s+)?(?:\d+[a-z]?\.?\s+)?(F[12]0_(\d{3})([12]))\b(.*)$")
RANDURI_F30 = (1, 2, 3)
_GENERICE = {"SOLD C", "SOLD D", "CHELTUIELI", "VENITURI"}
_NUMAR = re.compile(r"^\s*(?:\S+\s+)?\d+[a-z]?\.\s")        # orice rând numerotat din structură (câmp sau titlu de grupă)


def _text(rest, col):
    """Coloana denumirii: de la `col` până la coloana tipului „N(15)”."""
    t = rest[col:] if len(rest) > col else ""
    return re.split(r"\s{2,}N\(\d+\)|\s{3,}", t.strip(), maxsplit=1)[0].strip()


def _fara_eticheta(u):
    """Coloana din stânga a structurii (eticheta regulii de validare, „F10_42”) nu face parte din denumire."""
    return re.sub(r"^(F[1-4]0\w*)\s", lambda m: " " * len(m.group(0)), u)


def _curata(s):
    s = s.replace("ş", "ș").replace("ţ", "ț").replace("Ş", "Ș").replace("Ţ", "Ț")
    s = re.sub(r"\s+", " ", s).strip()
    while True:                                   # parantezele cu conturi sau cu note, oricât de imbricate
        n = re.sub(r"\((?:[^()]*?(?:ct\.|Sumele|din ct|cont)[^()]*?)\)", "", s)
        if n == s:
            break
        s = n
    s = re.sub(r"\s*Rd\.\s*\d+ si \d+ se exclud reciproc.*$", "", s)
    s = re.sub(r"\s*\((?:din )?ct\.[^)]*$", "", s)                    # paranteza de conturi tăiată de pagină
    s = re.sub(r"\s+([,.;:])", r"\1", s)
    s = re.sub(r"\*+$", "", s)                                          # trimiterea la nota de subsol a formularului
    s = re.sub(r"\s+", " ", s).strip(" -–")
    return s


def extrage(text=None):
    linii = (text if text is not None else io.open(SURSA, encoding="utf-8").read()).splitlines()
    out = {}
    for (form, sec), antet in SECTIUNI.items():
        i0 = next(i for i, ln in enumerate(linii) if " ".join(re.sub(r"[\ue000-\uf8ff]", " ", ln).split()) == antet)   # pdftotext: un glif privat
        i1 = next((i for i in range(i0 + 1, len(linii)) if _ANTET.match(linii[i])), len(linii))
        rez, grupa, i = {}, "", i0 + 1
        while i < i1:
            ln = linii[i]
            m = re.search(r"\b(F[1-3]0_(\d{3})1)\b", ln)
            if m and m.group(1).startswith(sec):
                col = m.end()
                parti = [_text(ln, col)]
                j = i + 1
                while j < i1:
                    u = _fara_eticheta(linii[j])
                    if re.search(r"\bF[1-3]0_\d{4}\b", u[:col]) or _NUMAR.match(u) or not u.strip():
                        break
                    st = len(u) - len(u.lstrip())
                    if col - 2 <= st <= col + 4 and not re.fullmatch(r"\s*\d+\s*", u):      # continuarea denumirii, nu formula din dreapta
                        parti.append(_text(u, st))
                    j += 1
                rand = int(m.group(2))
                den = _curata(" ".join(p for p in parti if p))
                if den.upper() in _GENERICE and grupa:                     # „SOLD C”, „Cheltuieli” … se citesc numai sub grupa lor
                    den = "%s — %s" % (re.sub(r"\s+Sold [CD]$", "", grupa, flags=re.I), den)
                else:
                    grupa = den
                rez.setdefault(rand, den)
                i = j
                continue
            g = re.match(r"^\s*(?:\S+\s+)?\d+[a-z]?\.\s+(?!F[1-3]0_|<)(\S.*)$", ln)
            if g:                                                          # titlu de grupă: rândul numerotat fără câmp, cu continuarea lui
                st0 = len(ln) - len(g.group(1))
                parti, j = [_text(ln, st0)], i + 1
                while j < i1 and linii[j].strip() and not _NUMAR.match(linii[j]) and not re.search(r"\bF[1-3]0_\d{4}\b", linii[j]):
                    parti.append(_text(_fara_eticheta(linii[j]), 0))
                    j += 1
                grupa = _curata(" ".join(parti))
                i = j
                continue
            i += 1
        if sec == "F30":                 # numai rândurile pe care le scrie generatorul (`bilant.xml_s1005`: F30 rd.1-3, cap.I)
            rez = {k: v for k, v in rez.items() if k in RANDURI_F30}
        out.setdefault(form, {})[sec] = dict(sorted(rez.items()))
    return out


def modul(d):
    return ('# -*- coding: utf-8 -*-\n"""GENERAT de `scripts/extrage_denumiri_bilant.py --scrie` din structura ANAF a formularelor de bilanț 2025\n'
            '(`anaf_surse/structura_SC_1225_270126.pdf`). NU se scrie cu mâna — `core/test_bilant_denumiri.py` îl compară cu extragerea.\n'
            'NOMENCLATOR_DENUMIRI[formular][secțiune][rând] = denumirea rândului de pe formular (deficiența 227, comanda Costin 12.10.2026)."""\n'
            "NOMENCLATOR_DENUMIRI = " + pprint.pformat(d, width=140, sort_dicts=True) + "\n")


if __name__ == "__main__":
    d = extrage()
    if "--scrie" in sys.argv[1:]:
        io.open(TINTA, "w", encoding="utf-8").write(modul(d))
        print("scris %s" % TINTA)
    else:
        pprint.pprint(d, width=160)
