# -*- coding: utf-8 -*-
"""scripts/extrage_denumiri_bilant.py — denumirile, ordinea și codurile rândurilor din formularele de bilanț, extrase din FORMULARUL oficial
2025 („soft A”, PDF XFA, `anaf_surse/bilant_SC_1225_XML_270326.pdf`, static.anaf.ro — pagina S1002-S1003-S1004-S1005 / 2025): tabelele
`form1.F10S` (bilanțul prescurtat — S1003 și S1005), `form1.F20S` (contul prescurtat de profit și pierdere — S1005) și `form1.F20` (contul
de profit și pierdere — S1003). Datele informative (F30, cap.I, rândurile pe care le scrie generatorul) — din documentul de STRUCTURĂ ANAF
(`anaf_surse/structura_SC_1225_270126.txt`, `pdftotext -layout`).

[deficiența 227, comanda Costin 12.10.2026] „fiecare rând arată denumirea de pe formular, nu doar «rândul 41»”.
[deficiența 234, comanda Costin 12.10.2026, verbatim în DECIZII] „Denumirile se scriu complete, curate, cu diacritice, în ordinea de pe
formular.” Deci, pe lângă text:
  · formula de conturi dintre paranteze („(ct. …)”), stelele notelor și „din care:” de la capăt se scot; trimiterile la rânduri rămân, ca la
    totaluri („(rd. 01 + 02 + 03)”);
  · majusculele formularului devin scriere obișnuită (cifrele romane și literele de secțiune rămân), cedila devine virgulă, iar cuvintele
    fără diacritice primesc diacriticele din lexiconul aplicației (`core/lexicon_diacritice.json`) și din `_DIACRITICE_CONTEXT` (cuvintele
    ambigue: „si”, „in”, „perioada”);
  · un rând al cărui text se repetă în tabel („Sold C”, „Cheltuieli”, „Profit”, „Sume de reluat într-o perioadă de până la un an”, „din
    care, cheltuielile în relația cu entitățile afiliate”) se citește sub grupa lui: antetul de grupă al formularului (rândurile `RGOL…` /
    `R_PP` fără câmp — la `R_PP` textul pe care scriptul formularului îl pune la situațiile anuale) sau rândul-părinte de deasupra;
  · ordinea = ordinea rândurilor în formular (06a / 06b înaintea totalului 06), iar codul = cel tipărit de formular („06a (301)” -> „06a”).

Uz: python scripts/extrage_denumiri_bilant.py           -> tipărește dicționarele
    python scripts/extrage_denumiri_bilant.py --scrie   -> rescrie `core/bilant_denumiri.py` (pazit de core/test_bilant_denumiri.py)
"""
import io
import json
import os
import pprint
import re
import sys
import unicodedata

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA = os.path.join(RAD, "anaf_surse", "structura_SC_1225_270126.txt")
FORMULAR = os.path.join(RAD, "anaf_surse", "bilant_SC_1225_XML_270326.pdf")
TINTA = os.path.join(RAD, "core", "bilant_denumiri.py")
LEXICON = os.path.join(RAD, "core", "lexicon_diacritice.json")
#: (formular, secțiune) -> tabelul formularului
TABELE = {("s1005", "F10"): "F10S", ("s1003", "F10"): "F10S", ("s1005", "F20"): "F20S", ("s1003", "F20"): "F20"}
#: [C14] F30 cap.XIX „Situația veniturilor și cheltuielilor” (S1005, anual) — subtabelul formularului
TABEL_F30_CAP_XIX = "F30/Table8_an_micro"
#: F30 (datele informative, cap.I) — din structură; numai rândurile scrise de generator (`bilant.xml_s1005`: F30 rd.1-3)
SECTIUNI_F30 = {"s1005": "F30_capital (rd.1-148, 301-303, 305, 306,316-321) cap.I-XII S1005",
                "s1003": "F30_capital_MM (rd.1- 152,301-311,313,314,316-321) cap.I-XII S1002-S1003-S1004"}
RANDURI_F30 = (1, 2, 3)
_TABELE_TOATE = ("F20", "F20S", "F30", "F10L", "F10S")
#: cuvinte pe care lexiconul nu le are (ambigue în general), dar care în formular au o singură citire
_DIACRITICE_CONTEXT = ((r"\bsi\b", "și"), (r"\bin\b", "în"), (r"\b(o|de) perioada\b", r"\1 perioadă"), (r"\bpana\b", "până"),
                       (r"\bintr-o\b", "într-o"), (r"\(a\)", "(ă)"), (r"\bUnităti\b", "Unități"), (r"\bunităti\b", "unități"))
_ROMAN = re.compile(r"^[IVXLC]+$")
#: rânduri care nu se citesc singure („Sold C”, „Profit (rd. 16 - 42)”, „Cheltuieli”): se scriu sub grupa lor, chiar dacă nu se repetă
_GENERICE = ("sold c", "sold d", "profit", "pierdere", "cheltuieli", "venituri")


def sablon_formular(cale=FORMULAR):
    """Șablonul XFA (XML) al formularului: fluxul comprimat din PDF care conține tabelul F20."""
    import zlib
    d = io.open(cale, "rb").read()
    for m in re.finditer(rb"stream\r?\n", d):
        e = d.find(b"endstream", m.end())
        try:
            t = zlib.decompress(d[m.end():e])
        except zlib.error:
            continue
        if b'name="F20"' in t:
            return t.decode("utf-8", "replace")
    raise ValueError("șablonul formularului nu are tabelul F20")


def bloc_tabel(sablon, tabel):
    if "/" in tabel:                                                  # subtabel: „F30/Table8_an_micro”, până la subtabelul următor
        mare, sub = tabel.split("/")
        b = bloc_tabel(sablon, mare)
        p = b.index('name="%s"' % sub)
        i0 = b.rfind("<subform", 0, p)
        m = re.search(r'<subform\b[^>]*\bname="Table', b[p:])
        return b[i0:p + m.start()] if m else b[i0:]
    p = sablon.index('name="%s"' % tabel)
    i0 = sablon.rfind("<subform", 0, p)
    i1 = min((x for x in (sablon.find('name="%s"' % n, p + 10) for n in _TABELE_TOATE + ("F40",)) if x > 0), default=len(sablon))
    return sablon[i0:i1]


def _valori(seg):
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", v)).strip() for v in re.findall(r"<value\s*>(.*?)</value\s*>", seg, re.S)]


def _antet_anual(sablon, tabel):
    """Textul pe care scriptul formularului (`pune_titluri`) îl pune în `R_PP` la situațiile financiare ANUALE (prima ramură, tipAS == 1)."""
    m = re.search(r'form1\.%s\.Table1\.R_PP\.Cell1\.rawValue\s*=\s*"([^"]*)"' % tabel, sablon)
    return m.group(1).strip() if m else ""


def randuri_tabel(sablon, tabel):
    """[(rând, cod, text, antet)] în ordinea formularului; `antet` = antetul de grupă (RGOL / R_PP) de deasupra, dacă vine imediat."""
    b = bloc_tabel(sablon, tabel)
    subf = [(m.start(), m.group(1)) for m in re.finditer(r'<subform\b[^>]*\bname="(R\d+|RGOL\d*|R_PP)"', b)]
    out, antet = [], ""
    for k, (p, nume) in enumerate(subf):
        seg = b[p:subf[k + 1][0] if k + 1 < len(subf) else len(b)]
        v = [x for x in _valori(seg) if x]
        if not nume[1:].isdigit():                                    # antet de grupă (fără câmp)
            text = _antet_anual(sablon, tabel) if nume == "R_PP" else ""
            text = text or next((x for x in v if len(x) > 3 and not re.match(r"^F\d0 - pag", x)), "")
            if text:
                antet = text
            continue
        rand = int(nume[1:])
        # codul din coloana B („Nr. rd.” — la el se referă formulele): „06a (301)” la rândurile cu cod propriu, altfel „41”
        cod = next((x for x in v[1:] if x.endswith("(%d)" % rand)), "%02d" % rand)
        out.append((rand, cod, v[0] if v else "", antet))
        antet = ""
    return out


def _lexicon():
    return json.load(io.open(LEXICON, encoding="utf-8"))


def _ascii(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def diacritice(s, lex=None):
    lex = _lexicon() if lex is None else lex
    s = s.replace("ş", "ș").replace("ţ", "ț").replace("Ş", "Ș").replace("Ţ", "Ț")

    def w(m):
        x = m.group(0)
        y = lex.get(_ascii(x).lower())
        if not y:
            return x
        if x.isupper() and len(x) > 1:
            return y.upper()
        return y[0].upper() + y[1:] if x[0].isupper() else y
    s = re.sub(r"[A-Za-zĂÂÎȘȚăâîșț]+", w, s)
    for rx, rep in _DIACRITICE_CONTEXT:
        s = re.sub(rx, rep, s)
    return s


def curata(s):
    """Textul unui rând de pe formular, fără formula de conturi, fără note și fără „din care:” de la capăt; spațierea trimiterilor la rânduri."""
    s = re.sub(r"\s+", " ", s).strip().replace("ş", "ș").replace("ţ", "ț").replace("Ş", "Ș").replace("Ţ", "Ț")
    while True:                                                       # parantezele cu conturi, oricât de imbricate
        n = re.sub(r"\(\s*(?:din\s*)?ct\.?[^()]*\)", "", s)
        if n == s:
            break
        s = n
    s = re.sub(r"\(\s*(?:din\s*)?ct\.[^()]*$", "", s)                    # paranteza de conturi neînchisă pe formular („(ct. 6053”)
    s = re.sub(r"\(\s*r\s*d\s*\.\s*", "(rd. ", s)
    s = re.sub(r"\s*\*+\s*\)", ")", s)
    s = re.sub(r"\s*\*+", "", s)
    s = re.sub(r"\s+\d\)\s*$", "", s)                                 # „1)” — nota de subsol
    s = re.sub(r"\s*,?\s*din care\s*:?\s*$", "", s)
    s = re.sub(r"(?<=[\d)a-z])\s*([+-])\s*(?=\d|\()", r" \1 ", s) if "(rd." in s or re.search(r"\) - \(", s) else s
    s = re.sub(r"\(rd\. ([^)]*?)\s*\)", lambda m: "(rd. %s)" % re.sub(r"\s*([+-])\s*", r" \1 ", m.group(1)).strip(), s)
    s = re.sub(r",\s*\(rd\.", " (rd.", s)                              # „investiții, (rd. 20 + 21)”
    s = re.sub(r"(\(rd\.[^)]*\))\s*\(rd\.[^)]*\)", r"\1", s)             # a doua paranteză de la rd.49 e corelația dublă
    s = re.sub(r"\s+-\s+(total)\b", r" – \1", s, flags=re.I)
    s = re.sub(r"\s+([,.;:)])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"^-\s*", "", s)
    s = re.sub(r"^din care\s*,\s*", "din care, ", s, flags=re.I)
    s = re.sub(r"([IVX]+)\.(?=[A-ZĂÂÎȘȚ])", r"\1. ", s)                 # „II.CREANȚE” -> „II. CREANȚE”
    s = re.sub(r"(?<=[A-ZĂÂÎȘȚa-zăâîșț]):(?=[A-ZĂÂÎȘȚa-zăâîșț])", ": ", s)  # „DATORII:SUMELE” -> „DATORII: SUMELE”
    s = re.sub(r"\b(\d+)\.(?=[A-Za-zĂÂÎȘȚ])", r"\1. ", s)              # „1.Cifra” -> „1. Cifra”
    return re.sub(r"\s+", " ", s).strip(" ,-–:")


def propozitie(s):
    """Majusculele formularului -> scriere obișnuită; cifrele romane, literele de secțiune („A.”, „J.”) și „C” / „D” din „sold C” rămân."""
    def w(m):
        x = m.group(0)
        if (_ROMAN.match(x) or (len(x) == 1 and x.isupper())) and s[m.end():m.end() + 1] in (".", ""):
            return x
        return x.lower() if x.isupper() else x
    s = re.sub(r"[A-Za-zĂÂÎȘȚăâîșț]+(?:\([ĂAăa]\))?", lambda m: w(m) if "(" not in m.group(0) else m.group(0).lower(), s)
    s = re.sub(r"\b(?:Sold|sold) ([cd])\b", lambda m: "sold " + m.group(1).upper(), s)
    # prima literă a textului (după numerotare: „1.”, „II.”, „A.”, „11.10.”, „8. a)”, „10.a)”, „a.1)”) se scrie mare; „a)” rămâne
    m = re.match(r"^((?:[IVXLC]+\.|[A-Z]\.|\d+(?:\.\d+)*\.)?\s*(?:[a-z](?:\.\d)?\)\s*)?)([a-zăâîșț])(?=[a-zăâîșț])", s)
    if m:
        s = s[:m.start(2)] + m.group(2).upper() + s[m.end(2):]
    return s


def _fara_trimiteri(s):
    return re.sub(r"\s*\(rd\.[^)]*\)(\s*-\s*\([^)]*\))?", "", s).strip(" :")


def denumiri_tabel(sablon, tabel, lex=None):
    """{rând: denumirea curată}, [rândurile în ordinea formularului], {rând: codul tipărit}."""
    lex = _lexicon() if lex is None else lex
    rr = randuri_tabel(sablon, tabel)
    brut = [(r, cod, diacritice(propozitie(curata(t)), lex), diacritice(propozitie(curata(a)), lex) if a else "") for r, cod, t, a in rr]
    cheie = lambda d: re.sub(r"[\s-]*\(rd\..*$", "", d).strip().lower()   # noqa: E731  („Pierdere - (rd. …)” e tot „pierdere”)
    numar = {}
    for _r, _c, d, _a in brut:
        numar[cheie(d)] = numar.get(cheie(d), 0) + 1
    den, ordine, coduri, parinte, grupa = {}, [], {}, "", ""
    for r, cod, d, antet in brut:
        m = re.match(r"^(.*\S)\s+(sold [CD])$", d)
        n = re.match(r"^((?:[IVXLC]+\.)\s*(\S.*?))\s+1\.$", d)
        if m:                                                         # „V. Profitul sau pierderea reportat(ă) sold C” -> grupa + „sold C”
            parinte, d = _fara_trimiteri(m.group(1)), m.group(2)
        elif n:                                                       # „II. Creanțe 1.” -> grupa „II. Creanțe”, rândul „1. Creanțe”
            grupa, d = n.group(1), "1. " + n.group(2)
        elif antet:
            parinte = _fara_trimiteri(antet)
        if grupa and (n or re.match(r"^\d+\. ", d) or re.match(r"^total\b", d, re.I)):
            total = d.lower().startswith("total")
            d = "%s — %s" % (grupa, d[0].lower() + d[1:] if total else d)
            if total:
                grupa = ""                                            # totalul închide grupa numerotată
        elif numar[cheie(d)] > 1 or m or cheie(d) in _GENERICE:
            d = "%s — %s" % (parinte, d[0].lower() + d[1:])
        else:
            parinte = _fara_trimiteri(d)
        den[r], coduri[r] = d, cod
        ordine.append(r)
    return den, ordine, coduri


# ── F30 (din structură) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
_CAMP = re.compile(r"\b(F30_(\d{3})1)\b")


def denumiri_f30(form, text=None, lex=None):
    linii = (text if text is not None else io.open(SURSA, encoding="utf-8").read()).splitlines()
    antet = SECTIUNI_F30[form]
    i0 = next(i for i, ln in enumerate(linii) if " ".join(re.sub(r"[-]", " ", ln).split()) == antet)
    out = {}
    for i in range(i0 + 1, i0 + 40):
        m = _CAMP.search(linii[i])
        if not (m and int(m.group(2)) in RANDURI_F30):
            continue
        parti = [_text(linii[i], m.end())]
        for u in linii[i + 1:i + 4]:                                  # continuarea denumirii, pe coloana ei, până la câmpul următor
            st = len(u) - len(u.lstrip())
            if not u.strip() or re.search(r"\bF\d0_\d{4}\b", u) or not (m.end() - 2 <= st <= m.end() + 4):
                break
            parti.append(_text(u, st))
        out.setdefault(int(m.group(2)), diacritice(propozitie(curata(" ".join(parti))), lex))
    return out


def _text(rest, col):
    """Coloana denumirii din structură: de la `col` până la coloana tipului „N(15)”."""
    t = rest[col:] if len(rest) > col else ""
    return re.split(r"\s{2,}N\(\d+\)|\s{3,}", t.strip(), maxsplit=1)[0].strip()


def extrage(sablon=None):
    t = sablon if sablon is not None else sablon_formular()
    lex = _lexicon()
    den, ordine, coduri = {}, {}, {}
    for (form, sec), tabel in TABELE.items():
        d, o, c = denumiri_tabel(t, tabel, lex)
        den.setdefault(form, {})[sec], ordine.setdefault(form, {})[sec], coduri.setdefault(form, {})[sec] = d, o, c
    for form in SECTIUNI_F30:
        f30 = denumiri_f30(form, lex=lex)
        den[form]["F30"], ordine[form]["F30"], coduri[form]["F30"] = f30, sorted(f30), {r: "%02d" % r for r in f30}
    d, o, c = denumiri_tabel(t, TABEL_F30_CAP_XIX, lex)               # [C14] cap.XIX al S1005, după rândurile 1–3
    den["s1005"]["F30"].update(d)
    ordine["s1005"]["F30"] += o
    coduri["s1005"]["F30"].update(c)
    return den, ordine, coduri


def modul(rez):
    den, ordine, coduri = rez
    f = lambda x: pprint.pformat(x, width=140, sort_dicts=True)   # noqa: E731
    return ('# -*- coding: utf-8 -*-\n"""GENERAT de `scripts/extrage_denumiri_bilant.py --scrie` din FORMULARUL ANAF de bilanț 2025\n'
            '(`anaf_surse/bilant_SC_1225_XML_270326.pdf`; F30 din structura `structura_SC_1225_270126.txt`). NU se scrie cu mâna —\n'
            '`core/test_bilant_denumiri.py` îl compară cu extragerea. Deficiențele 227 și 234 (comenzile Costin 12.10.2026).\n'
            'NOMENCLATOR_DENUMIRI[formular][secțiune][rând] = denumirea curată a rândului; NOMENCLATOR_ORDINE[formular][secțiune] = rândurile\n'
            'în ordinea formularului; NOMENCLATOR_COD[formular][secțiune][rând] = codul tipărit pe formular („06a”)."""\n'
            "NOMENCLATOR_DENUMIRI = " + f(den) + "\n" + "NOMENCLATOR_ORDINE = " + f(ordine) + "\n" + "NOMENCLATOR_COD = " + f(coduri) + "\n")


if __name__ == "__main__":
    sys.path.insert(0, RAD)
    import argumente_script  # noqa: F401  (același parser ca restul scripturilor — `--help` tipărește uzul)
    argv = argumente_script.citeste(sys.argv[1:], __doc__, flaguri=("--scrie",), prefix="[denumiri]")
    rez = extrage()
    if "--scrie" in argv:
        io.open(TINTA, "w", encoding="utf-8").write(modul(rez))
        print("scris %s" % TINTA)
    else:
        pprint.pprint(rez[0], width=160)
