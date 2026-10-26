# -*- coding: utf-8 -*-
"""GARD — ghidurile publice nu descriu drumurile din aplicație scoase în lotul 11 (comanda Costin 11.1, verbatim în DECIZII „Comanda 11.1”;
deficiențele 429 și 450):
  1. reevaluarea în valută are UN SINGUR formular, în „Închidere lună → Reevaluare valută” (propunerea, cursul BNR din ultima zi bancară
     a lunii, diferența pe 665/765, ajustarea manuală); intrarea „Reevaluare lunară solduri valută” din „Operațiuni speciale” a fost scoasă;
  2. borderoul de achiziție de la persoana fizică neînregistrată stă în „Stocuri → Borderou de achiziție” (cu stornare din lista lunii),
     nu mai e „Achiziție de la neînregistrat” în „Operațiuni speciale › TVA regimuri speciale”;
  3. cursul BNR al unei operațiuni din ziua Z e ultimul curs comunicat ÎNAINTEA zilei Z (HG 1/2016 pct.35 alin.(1): „cursul de schimb
     comunicat de respectiva bancă în ziua anterioară și care este valabil pentru operațiunile care se vor desfășura în ziua următoare”),
     nu „cel mai recent curs cu data ≤ Z”.
CE FACE IMPOSIBIL: un ghid (titlu, descriere, corp) care trimite contabilul pe drumul vechi sau descrie regula veche a cursului; și
dispariția tăcută a drumului nou din ecrane (atunci formulările de înlocuire ar deveni ele false).
CE NU VEDE: o formulare nouă, altfel scrisă, a drumului vechi — lista e a formulărilor găsite la 21.10.2026 (`grep -rln` pe ghid/)."""
import glob
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: formulările drumurilor vechi, găsite în ghiduri la 21.10.2026 și corectate (fiecare cu motivul)
INTERZISE = (
    ("Operațiuni speciale → Reevaluare", "reevaluarea valutei e în «Închidere lună → Reevaluare valută» (429)"),
    ("Reevaluare lunară solduri valută", "intrarea din Operațiuni speciale a fost scoasă (429)"),
    ("reevaluarea soldului în valută (Operațiuni speciale)", "reevaluarea valutei nu mai e în Operațiuni speciale (429)"),
    ("reevaluarea în valută (Operațiuni speciale)", "reevaluarea valutei nu mai e în Operațiuni speciale (429)"),
    ("Achiziție de la neînregistrat", "borderoul e în «Stocuri → Borderou de achiziție» (450)"),
    ("bonuri/borderouri, fără ecran propriu", "borderoul are ecranul lui (450)"),
    ("data cursului ≤", "cursul operațiunii = ultimul comunicat înaintea zilei (HG 1/2016 pct.35 alin.(1))"),
    ("data cursului mai mică sau egală", "cursul operațiunii = ultimul comunicat înaintea zilei (HG 1/2016 pct.35 alin.(1))"),
    ("cursul BNR al zilei din aplicație", "cursul operațiunii = ultimul comunicat înaintea zilei (HG 1/2016 pct.35 alin.(1))"),
    ("cursul BNR al zilei încasării", "cursul operațiunii = ultimul comunicat înaintea zilei (HG 1/2016 pct.35 alin.(1))"),
    ("cursul BNR al zilei de decontare", "cursul operațiunii = ultimul comunicat înaintea zilei (HG 1/2016 pct.35 alin.(1))"),
    ("nu are câmp pentru contul de bancă", "formularul „Decontare în valută” are câmpul „Contul bancar”"),
    ("nu are un câmp pentru contul de bancă", "formularul „Decontare în valută” are câmpul „Contul bancar”"),
    # [lotul 13, deficiențele 524 + 504] formularul se face pe FACTURĂ (moneda, contul de terț, cursul de evidență vin de la ea), iar
    # „Contul bancar” e o alegere între 5124 și 5121, fără nimic precompletat — formulările vechi, găsite la 26.10.2026 în ghid/
    ("câmpul „Cont bancă\"", "câmpul se numește „Contul bancar” și nu propune nimic (504)"),
    ("propus 5124", "contul bancar nu e precompletat: se alege între 5124 și 5121 (504)"),
    ("valoarea în valută, moneda și cursul de evidență", "moneda și cursul de evidență vin de la factura aleasă (524)"),
)


def _text_public(t):
    """Titlul, descrierea și corpul (celelalte chei din front-matter nu ajung pe pagină)."""
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return t
    fm = "\n".join(l for l in m.group(1).splitlines() if l.startswith(("title:", "description:")))
    return fm + "\n" + t[m.end():]


def drumuri_vechi(text):
    """[(formularea, motivul)] găsite în textul public al unui ghid. PURĂ."""
    return [(f, motiv) for f, motiv in INTERZISE if f in _text_public(text)]


def test_CALIBRARE_formularea_veche_e_prinsa_cea_noua_trece():
    vechi = ("---\ntitle: X\ndescription: Y\n---\n# X\n\nDin ecranul **Operațiuni speciale → Reevaluare valuta**, introduci lista "
             "soldurilor. Motorul alege ultimul curs BNR comunicat cu data cursului ≤ data respectivă.")
    nou = ("---\ntitle: X\ndescription: Y\n---\n# X\n\nDin **Închidere lună → Reevaluare valută**, aplicația propune soldurile; cursul "
           "operațiunii e ultimul curs comunicat de BNR înaintea zilei operațiunii.")
    assert [f for f, _m in drumuri_vechi(vechi)] == ["Operațiuni speciale → Reevaluare", "data cursului ≤"]
    assert drumuri_vechi(nou) == []


def test_niciun_ghid_nu_descrie_drumurile_scoase():
    """MUTAȚIE: formularea veche („Din ecranul **Operațiuni speciale → Reevaluare valuta**”) scrisă înapoi într-un ghid -> pică, cu
    ghidul și motivul."""
    fisiere = sorted(glob.glob(os.path.join(RAD, "ghid", "*.md")))
    assert len(fisiere) > 6000, len(fisiere)   # anti-vacuu: ghidurile sunt acolo
    gasite = []
    for f in fisiere:
        for formulare, motiv in drumuri_vechi(io.open(f, encoding="utf-8").read()):
            gasite.append("%s: „%s” — %s" % (os.path.basename(f), formulare, motiv))
    assert not gasite, "ghiduri pe drumul vechi:\n  " + "\n  ".join(gasite)


def _elemente_cu_text(arb, noduri, cu_clasa=False):
    """[(eticheta, id, textul direct al elementului[, clasa])] din șabloanele HTML ale arborelui acorn; o interpolare `${…}` taie textul."""
    import html.parser

    class _P(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.stiva, self.out = [], []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            self.stiva.append([tag, a.get("id"), "", a.get("class")])

        def handle_data(self, data):
            if self.stiva:
                self.stiva[-1][2] += data

        def handle_endtag(self, tag):
            while self.stiva:
                e = self.stiva.pop()
                t = " ".join(e[2].split("\x00")[0].split())
                self.out.append((e[0], e[1], t, e[3]) if cu_clasa else (e[0], e[1], t))
                if e[0] == tag:
                    break

    p = _P()
    for tl in noduri(arb, "TemplateLiteral"):
        p.feed("\x00".join(q["value"]["cooked"] or "" for q in tl["quasis"]))
        p.stiva = []
    return p.out


def test_drumurile_noi_numite_in_ghiduri_exista_pe_ecrane():
    """Ghidurile corectate trimit la „Închidere lună → Reevaluare valută”, „Stocuri → Borderou de achiziție” și „Operațiuni speciale →
    Decontare în valută” (cu câmpul „Contul bancar” — „Cont bancă” până la lotul 13, 524). Dacă un ecran se mută, garda pică aici — înainte
    ca ghidul să mintă."""
    firme = io.open(os.path.join(RAD, "static/js/ecrane/firme.js"), encoding="utf-8").read()
    oper = io.open(os.path.join(RAD, "static/js/ecrane/operatiuni_ecran.js"), encoding="utf-8").read()
    import ast
    from core.arbore_js import apeluri, arbore_js, elemente_html, noduri
    # butoanele ca elemente HTML cu id-ul lor (arborele acorn), nu șiruri în sursă (core/test_garzi_pe_text.py)
    arb_f, _cod_f = arbore_js("firme.js")
    butoane = {at.get("id") for tag, at in elemente_html(arb_f) if tag == "button"}
    assert {"il-reevaluare", "s-borderou"} <= butoane, sorted(butoane & {"il-reevaluare", "s-borderou"})
    # eticheta fiecărui buton și titlurile ecranelor: textul ELEMENTULUI (parserul HTML peste șabloanele acorn), egal cu ce numește ghidul
    el = _elemente_cu_text(arb_f, noduri)
    assert ("button", "il-reevaluare", "Reevaluare valută") in el and ("button", "s-borderou", "Borderou de achiziție") in el
    titluri = [t for tag, _id, t, cls in ((e[0], e[1], e[2], e[3]) for e in _elemente_cu_text(arb_f, noduri, cu_clasa=True))
               if tag == "h2" and cls == "pf-titlu"]
    assert set(titluri) >= {"Închidere lună"} and any(t.startswith("Stocuri") for t in titluri), sorted(set(titluri))[:20]
    # operațiunea „Decontare în valută” cu câmpul „Contul bancar”: obiectul din `REGISTRU` și apelul `C(...)` din câmpurile lui
    arb_o, cod_o = arbore_js("operatiuni_ecran.js")
    reg = [d for d in noduri(arb_o, "VariableDeclarator") if d["id"].get("name") == "REGISTRU"]
    assert len(reg) == 1, "REGISTRU: %d declarații" % len(reg)
    decont = [o for o in reg[0]["init"]["elements"] if any(p["key"].get("name") == "titlu" and p["value"].get("value") ==
                                                          "Decontare în valută (665/765)" for p in o.get("properties", []))]
    assert len(decont) == 1, "operațiunea „Decontare în valută (665/765)” nu mai e în REGISTRU"
    assert any(a[:2] == ('"cont_banca"', '"Contul bancar"') for a in apeluri(decont[0], cod_o, "C")), apeluri(decont[0], cod_o, "C")
    # intrările scoase nu se întorc în Operațiuni speciale
    assert 'cheie: "reeval_valuta"' not in oper and 'cheie: "neinregistrat"' not in oper
    # regula cursului (CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1): cursul zilei anterioare) ca noduri AST, nu șiruri în sursă
    arb_c = ast.parse(io.open(os.path.join(RAD, "core/curs_bnr.py"), encoding="utf-8").read())
    assert any(isinstance(n, ast.Assign) and [getattr(t, "id", None) for t in n.targets] == ["REGULA_OPERATIUNE"]
               and getattr(n.value, "value", None) == "operatiune" for n in arb_c.body), "REGULA_OPERATIUNE lipsește din curs_bnr"
    assert any(isinstance(n, ast.IfExp) and getattr(n.test, "id", None) == "strict"
               and isinstance(n.body, ast.Compare) and isinstance(n.body.ops[0], ast.Lt)
               and isinstance(n.orelse, ast.Compare) and isinstance(n.orelse.ops[0], ast.LtE) for n in ast.walk(arb_c)), \
        "alegerea cursului nu mai deosebește data operațiunii (strict <) de sfârșitul lunii (<=)"
