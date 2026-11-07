# -*- coding: utf-8 -*-
"""GARD — [lotul 17.3] zero text tăiat în tabelul DS și „Renunță” numai unde nu există „←” (comanda 17.3, pct.2 a și d).

CE FACE IMPOSIBIL
  1. regula `.ds-tabel tbody td`, `.ds-tabel thead th` și orice altă regulă din docs/dovezi/17_3/reguli_atinse.txt cu text pe o linie tăiat cu „…”
     (white-space: nowrap + text-overflow: ellipsis în aceeași regulă); celula și capul tabelului DS se rup (white-space: normal);
  2. „Renunță” generat de bara de jos (`renuntaPiesei`) pentru o fereastră din afara listei PASTREAZA_RENUNTA; funcția rămasă când lista e goală;
  3. textul regulii «fără Renunță în bară» diferit între DESIGN_SYSTEM.md și verificator_conformitate.py;
  4. cele trei liste diferite între ele: PASTREAZA_RENUNTA din cadru.js, PASTREAZA_RENUNTA din scripts/verificator_design.py și ferestrele din
     docs/dovezi/17_3/inapoi.txt cu rând «fără ←» sau «efect propriu: da».

CE NU VEDE (declarat): citește sursa, nu rulează browserul (cifrele le dă matricea de text tăiat și parcursul)."""
import ast
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _citeste(*cale):
    with open(os.path.join(RAD, *cale), encoding="utf-8") as f:
        return f.read()


def _reguli_css():
    """[(lista de selectori, corpul)] din static/stil.css, fără comentarii; regulile din @media rămân (corpul interior, la același nivel)."""
    css = re.sub(r"/\*.*?\*/", "", _citeste("static", "stil.css"), flags=re.S)
    return [(_selectori(m.group(1)), m.group(2)) for m in re.finditer(r"([^{}@]+)\{([^{}]*)\}", css)]


def _selectori(lista):
    """Lista de selectori despărțită la virgulele din afara parantezelor (`:is(th, td)` rămâne întreg)."""
    out, adanc, cur = [], 0, ""
    for ch in lista:
        adanc += ch == "("
        adanc -= ch == ")"
        if ch == "," and not adanc:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return out + [cur.strip()]


def _selectori_atinsi():
    sel = []
    for lin in _citeste("docs", "dovezi", "17_3", "reguli_atinse.txt").splitlines():
        if lin.strip() and not lin.startswith("#"):
            sel.append(lin.split("|")[0].strip())
    return sel


def test_regulile_atinse_nu_mai_taie_cu_puncte_de_suspensie():
    atinse = _selectori_atinsi()
    assert len(atinse) >= 20, "lista regulilor atinse e goală sau trunchiată"
    cu_elipsa = []
    for selectori, corp in _reguli_css():
        if "text-overflow: ellipsis" in corp and "white-space: nowrap" in corp and any(s in atinse for s in selectori):
            cu_elipsa.append(selectori[0])
    assert not cu_elipsa, "reguli din reguli_atinse.txt încă cu nowrap + ellipsis: %s" % cu_elipsa


def test_celula_si_capul_tabelului_ds_se_rup():
    reguli = _reguli_css()
    for tinta in (".ds-tabel tbody td", ".ds-tabel thead th"):
        corpuri = [c for sel, c in reguli if tinta in sel]
        assert corpuri, "lipsește regula %s" % tinta
        # ultima regulă pe selector hotărăște (cascada); înălțimea e minimă, deci textul rupt crește rândul
        assert any("white-space: normal" in c and "overflow-wrap: anywhere" in c for c in corpuri), "%s nu rupe textul" % tinta
        assert not any("text-overflow: ellipsis" in c for c in corpuri), "%s taie cu «…»" % tinta


def test_coloanele_care_nu_se_rup_taie_fara_puncte_de_suspensie():
    grup = [c for sel, c in _reguli_css() if any("ds-tabel-num" in s and ":is(" in s for s in sel)]
    assert grup, "lipsește regula coloanelor care nu se rup (cifră, dată, sumă, acțiuni)"
    assert all("white-space: nowrap" in c and "overflow: hidden" in c and "text-overflow: clip" in c for c in grup)


def _lista_cadru():
    m = re.search(r"export const PASTREAZA_RENUNTA = \[([^\]]*)\]", _citeste("static", "js", "cadru.js"))
    assert m, "cadru.js nu are PASTREAZA_RENUNTA"
    return re.findall(r'"([^"]+)"', m.group(1))


def _lista_verificator():
    arbore = ast.parse(_citeste("scripts", "verificator_design.py"))
    for nod in arbore.body:
        if isinstance(nod, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PASTREAZA_RENUNTA" for t in nod.targets):
            return list(ast.literal_eval(nod.value))
    raise AssertionError("verificator_design.py nu are PASTREAZA_RENUNTA")


def _lista_inapoi():
    nume = set()
    for lin in _citeste("docs", "dovezi", "17_3", "inapoi.txt").splitlines():
        if not lin.strip() or lin.startswith("#"):
            continue
        camp = [x.strip() for x in lin.split("|")]
        if camp[2] == "fără ←" or camp[3].startswith("efect propriu: da"):
            nume.add(camp[1])
    return nume


def test_cele_trei_liste_sunt_identice():
    a, b, c = _lista_cadru(), _lista_verificator(), _lista_inapoi()
    assert a and sorted(a) == sorted(b) == sorted(c), (a, b, sorted(c))
    assert len(a) == len(set(a))


def test_renunta_din_bara_se_genereaza_numai_pentru_ferestrele_din_lista():
    js = _citeste("static", "js", "cadru.js")
    lista = _lista_cadru()
    if not lista:   # lista goală: funcția nu mai are rost și dispare, cu parametrul `renunta`
        assert "renuntaPiesei" not in js and "{ renunta }" not in js
        return
    assert "const inLista = PASTREAZA_RENUNTA.includes(titlu);" in js
    assert re.search(r"else if \(cuFormular && inLista\) \{\s*if \(!loc\.querySelector\(\"\.fj-renunta\"\)\) loc\.prepend\(renuntaPiesei\(\)\);", js), \
        "„Renunță” al piesei trebuie pus numai când fereastra e în PASTREAZA_RENUNTA"
    assert "renuntaPiesei()" in js and js.count("loc.prepend(renuntaPiesei())") == 1
    assert "inLista ? [...corp.querySelectorAll(" in js, "„Renunță” al ecranului se mută în bară numai pentru ferestrele din listă"


def test_textul_regulii_e_identic_in_design_system_si_in_conformitate():
    ds = re.sub(r"\s+", " ", _citeste("DESIGN_SYSTEM.md"))
    conf = _citeste("verificator_conformitate.py")
    m = re.search(r'REGULA_FARA_RENUNTA_IN_BARA = \((.*?)\)\n', conf, flags=re.S)
    assert m, "verificator_conformitate.py nu are REGULA_FARA_RENUNTA_IN_BARA"
    text = "".join(ast.literal_eval(p) for p in re.findall(r'"(?:[^"\\]|\\.)*"', m.group(1)))
    assert text.startswith("Bara de jos a ferestrei cu formular nu are «Renunță»")
    assert text in ds, "textul regulii din verificator_conformitate.py nu se găsește identic în DESIGN_SYSTEM.md"
