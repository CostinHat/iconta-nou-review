# -*- coding: utf-8 -*-
"""scripts/nomenclator_obligatii.py — generează `core/nomenclator_obligatii.py`: denumirea OFICIALĂ a fiecărei obligații de plată din
D100 / D710 și din D112, pe codul ei din XML (`cod_oblig`), citită din textul ordinelor din `anaf_surse/` (nu scrisă de mână).

[comanda Costin 9.1, A.3, 19.10.2026] „Denumirile obligațiilor D100/D112: descarcă nomenclatorul oficial ANAF și leagă-l.” Două surse,
fiecare pe nivelul ei (CLAUDE.md §3):
- DENUMIREA vine din ordin (nivel 1, Monitorul Oficial), pe POZIȚIA din nomenclator:
  · D100 / D710: OPANAF 587/2016, anexa nr. 3 „Nomenclatorul obligațiilor de plată la bugetul de stat”, forma consolidată 15.05.2026
    (`anaf_surse/opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.html`, legislatie.just.ro);
  · D112: Ordinul comun 605/95/928/2.314/2026 (MO 463 bis / 2.06.2026), anexa nr. 2 Nomenclatorul „Creanţe fiscale”
    (`anaf_surse/opanaf_605_2026_d112.pdf`; cuvintele cu coordonatele lor: `nomenclator_creante_d112_bbox.html`, scos cu
    `pdftotext -bbox -f 22 -l 25`).
- CODUL XML al fiecărei poziții vine din structura publicată de ANAF (nivel 2 — procedură; ordinul numește doar poziția):
  · D100 / D710: `structura_D100-D710_0126_140926.pdf` (static.anaf.ro, 14.09.2026), coloana „Cod Impozit (poz. in ordin)”: „103 (poz.2)”;
  · D112: `structura_D112_0726_070926.pdf` (static.anaf.ro, 07.09.2026), „Nomenclator 3 – Obligatii de plata la BS si BASFS (cf.anexa2
    Ordin comun)”: coloanele „Cod oblig. XML” și „Nr.cr. Mof.” (poziția din ordin).
O poziție pe care ordinul o arată „Eliminată” / „Abrogată” nu intră; un cod din structură fără poziție în ordin nu intră (n-are denumire
oficială) — garda (`core/test_nomenclator_obligatii.py`) cere ca fiecare cod pe care îl emite aplicația să fie aici.

Uz: python scripts/nomenclator_obligatii.py            -> rescrie core/nomenclator_obligatii.py
    python scripts/nomenclator_obligatii.py --verifica -> 0 identic / 1 diferă
"""
import html
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAD, "anaf_surse")
ORDIN_D100 = os.path.join(S, "opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.html")
STRUCT_D100 = os.path.join(S, "structura_D100-D710_0126_140926.txt")
ORDIN_D112 = os.path.join(S, "nomenclator_creante_d112_bbox.html")
STRUCT_D112 = os.path.join(S, "structura_D112_0726_070926.txt")
IESIRE = os.path.join(RAD, "core", "nomenclator_obligatii.py")

_RETRASA = re.compile(r"^(Eliminat|Eliminată|Abrogat|Abrogată)\.?$")


def _txt(c):
    c = re.sub(r"<br\s*/?>", " ", c)
    c = re.sub(r"<[^>]+>", "", c)
    return " ".join(html.unescape(c).split())


def pozitii_d100(text_html):
    """{poziție: denumire} din tabelul anexei nr. 3 a OPANAF 587/2016 (pozițiile retrase lipsesc)."""
    a = text_html.index('<span class="A_PAR">Nomenclatorul obligațiilor de plată la bugetul de stat')
    z = text_html.index("Anexa nr. 3^1", a)
    out = {}
    for rand in re.findall(r"<tr[^>]*>(.*?)</tr>", text_html[a:z], re.S):
        celule = [_txt(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", rand, re.S)]
        if len(celule) < 2 or not re.fullmatch(r"\d+\.", celule[0]) or _RETRASA.match(celule[1]):
            continue
        out[int(celule[0].rstrip("."))] = celule[1]
    return out


#: rândurile din structura D100 al căror „(poz.N)” a căzut pe pagina următoare, departe de cod — listă ÎNCHISĂ, fiecare citită în
#: structura_D100-D710_0126_140926.pdf: „101. 537 Taxa aferentă autorizației …” / „(poz.93)” (p.23–24) și „115. 718 Despagubiri acordate …”
#: / „(poz.107)” (p.27–28); denumirile ordinului la pozițiile 93 și 107 sunt chiar acestea
PAGINA_RUPTA_D100 = (("537", 93), ("718", 107))


def coduri_d100(text):
    """[(cod XML, poziție)] din structura D100-D710 (textul extras din PDF: „103\\n(poz.2)”)."""
    return [(c, int(p)) for c, p in re.findall(r"(?<![\d.])(\d{3})\s*\(\s*poz\.?\s*(\d+)\s*\)", text)] + list(PAGINA_RUPTA_D100)


def pozitii_d112(bbox):
    """{poziție: denumire} din anexa nr. 2 a Ordinului 605/2026: numărul poziției e în coloana din stânga („1.”), denumirea între el și
    coloana „Temei legal” (al cărei început, pe fiecare pagină, e marginea stângă a primului cuvânt „Art.” din dreapta). Cuvintele de sus
    ale unei pagini, dinaintea primului număr, continuă poziția de pe pagina precedentă."""
    a = bbox.index(">Anexa<")
    z = bbox.index(">Anexa<", a + 10)
    out, cur = {}, None
    for pag in re.split(r"<page ", bbox[a:z]):
        cuv = [(float(x0), float(y0), html.unescape(w)) for x0, y0, w in
               re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">(.*?)</word>', pag)]
        nr = sorted((y, int(w.rstrip("."))) for x, y, w in cuv if x < 70 and re.fullmatch(r"\d+\.", w))
        temei = [x for x, y, w in cuv if w == "Art." and x > 300]
        if not temei:
            continue
        lim = min(temei) - 1
        for x, y, w in sorted(((x, y, w) for x, y, w in cuv if 70 <= x < lim), key=lambda t: (round(t[1]), t[0])):
            inainte = [p for yn, p in nr if yn <= y + 0.5]
            if inainte:
                cur = inainte[-1]
            if cur is not None:
                out.setdefault(cur, []).append(w)
    # un cuvânt despărțit la capăt de rând („Decretul-” / „lege”) se lipește la loc; „1945 - 1989” are cratima ca token separat
    return {p: re.sub(r"(\w)- (?=\w)", r"\1-", " ".join(v)) for p, v in out.items()}


_R112 = re.compile(r"^\s{0,6}(\d{1,3})?\s+(\d{3})\s+(\d{1,2})?\s+(\w{9,10})\s+(.*)$")


def coduri_d112(text):
    """[(cod XML, poziție)] din „Nomenclator 3” al structurii D112: rândul are numărul istoric, codul XML, „Nr.cr. Mof.” (poziția din
    ordin) și codul bugetar; la câteva rânduri poziția e tipărită pe rândul următor (celula înaltă)."""
    a = text.index("Nomenclator 3 – Obligatii de plata la BS si BASFS (cf.anexa2")
    z = text.index("Nomenclator 5", a)
    linii = [ln for ln in text[a:z].splitlines() if ln.strip()]
    out = []
    for i, ln in enumerate(linii):
        m = _R112.match(ln)
        if not m:
            continue
        cod, poz = m.group(2), m.group(3)
        if poz is None and i + 1 < len(linii) and not _R112.match(linii[i + 1]):
            m2 = re.match(r"^\s{0,6}(\d{1,3})\s{5,}(\d{1,2})\b", linii[i + 1])
            poz = m2.group(2) if m2 else None
        if poz is not None:
            out.append((cod, int(poz)))
    return out


def leaga(coduri, pozitii):
    """{cod: (poziție, denumire)} — un cod cu mai multe poziții în structură o păstrează pe cea cu denumire (nereatrasă) în ordin."""
    out = {}
    for cod, poz in coduri:
        if poz in pozitii:
            out[cod] = (poz, pozitii[poz])
    return out


def randeaza(d100, d112):
    def bloc(nume, d):
        linii = ["%s = {" % nume]
        for k in sorted(d, key=int):
            linii.append("    %r: (%d, %r)," % (k, d[k][0], d[k][1]))
        return linii + ["}", ""]
    linii = ['# -*- coding: utf-8 -*-',
             '"""core/nomenclator_obligatii.py — GENERAT de `scripts/nomenclator_obligatii.py` din ordinele din `anaf_surse/` (nu se editează de',
             'mână; garda `core/test_nomenclator_obligatii.py` îl compară cu regenerarea). [comanda Costin 9.1, A.3] Denumirea oficială a fiecărei',
             'obligații de plată, pe codul ei din XML: {cod_oblig: (poziția din nomenclatorul ordinului, denumirea creanței fiscale)}."""',
             '',
             '#: D100 / D710 — OPANAF 587/2016, anexa nr. 3 (denumirea) + structura_D100-D710_0126_140926 (codul XML al poziției)']
    linii += bloc("NOMENCLATOR_D100", d100)
    linii += ['#: D112 — Ordinul comun 605/2026, anexa nr. 2 „Creanţe fiscale” (denumirea) + structura_D112_0726_070926, Nomenclator 3 (codul XML)']
    linii += bloc("NOMENCLATOR_D112", d112)
    linii += ['_PE_DECLARATIE = {"d100": NOMENCLATOR_D100, "d710": NOMENCLATOR_D100, "d112": NOMENCLATOR_D112}',
              '',
              '',
              'def denumire(tip, cod):',
              '    """Denumirea oficială a obligației `cod` din declarația `tip` (d100 / d710 / d112); "" dacă nu e în nomenclator."""',
              '    r = _PE_DECLARATIE.get((tip or "").lower(), {}).get(str(cod or "").strip())',
              '    return r[1] if r else ""',
              '']
    return "\n".join(linii)


def genereaza():
    d100 = leaga(coduri_d100(open(STRUCT_D100, encoding="utf-8").read()),
                 pozitii_d100(open(ORDIN_D100, encoding="utf-8").read()))
    d112 = leaga(coduri_d112(open(STRUCT_D112, encoding="utf-8").read()),
                 pozitii_d112(open(ORDIN_D112, encoding="utf-8").read()))
    return d100, d112


def main(argv):
    d100, d112 = genereaza()
    nou = randeaza(d100, d112)
    if "--verifica" in argv:
        vechi = open(IESIRE, encoding="utf-8").read() if os.path.exists(IESIRE) else ""
        print("identic" if vechi == nou else "diferă — regenerează: python scripts/nomenclator_obligatii.py")
        return 0 if vechi == nou else 1
    open(IESIRE, "w", encoding="utf-8").write(nou)
    print("scris %s: D100 %d obligații, D112 %d obligații" % (IESIRE, len(d100), len(d112)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
