# -*- coding: utf-8 -*-
"""[lotul 17.5] Acțiunile din rând (DS v2.110) pe cele cinci ecrane martor, eticheta D104 și acțiunea principală a ferestrei.

Static: citește sursele din static/js, fără rețea și fără 8019.

Temei: N/A — reguli de interfață (DS cap.9 v2.110 „Acțiunile unui rând stau într-un meniu”; CLAUDE.md §9).
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js")
DISTRUCTIVE = ("Șterge", "Scoate", "Revocă", "Casează", "Respinge", "Stornează")


def _sursa(*cale):
    with open(os.path.join(JS, *cale), encoding="utf-8") as h:
        return h.read()


def _bloc(sursa, inceput, sfarsit):
    i = sursa.index(inceput)
    return sursa[i:sursa.index(sfarsit, i)]


def _in_afara_meniului(bloc):
    """Textul blocului fără apelurile `meniuActiuni([...])` și fără `<details>…</details>` (adică ce stă liber pe rând)."""
    bloc = re.sub(r"<details\b.*?</details>", "", bloc, flags=re.S)
    out, i = [], 0
    while True:
        j = bloc.find("meniuActiuni(", i)
        if j < 0:
            out.append(bloc[i:])
            break
        out.append(bloc[i:j])
        adanc, k = 0, j + len("meniuActiuni")
        while k < len(bloc):
            if bloc[k] == "(":
                adanc += 1
            elif bloc[k] == ")":
                adanc -= 1
                if adanc == 0:
                    break
            k += 1
        i = k + 1
    return "".join(out)


def test_piesa_comuna_exista_o_singura_data():
    ds = _sursa("ds_piese.js")
    assert len(re.findall(r"export function meniuActiuni\(", ds)) == 1
    assert '<summary>${titlu}</summary>' in ds and 'details class="dec-xml' in ds
    # nicio dublură: ecranele nu-și mai desenează meniul "Acțiuni" cu un șablon propriu
    for fis in ("clienti_ecran.js", "produse_ecran.js", "validat.js", "firme.js"):
        assert "<summary>Acțiuni</summary>" not in _sursa("ecrane", fis), fis


def test_plan_de_conturi_sterge_numai_in_meniu():
    firme = _sursa("ecrane", "firme.js")
    rand = _bloc(firme, "const rand = (c, analitic) =>", "// [589] „avertismentul apare după salvare”")
    liber = _in_afara_meniului(rand)
    assert "data-sterge=" not in liber and ">Șterge<" not in liber and '"Șterge"' not in liber
    assert re.search(r'meniuActiuni\(\[butonRand\([^\n]*data-sterge=', rand)
    assert 'data-analitic=' in liber   # acțiunea obișnuită rămâne la vedere


def test_casa_ambele_actiuni_numai_in_meniu():
    firme = _sursa("ecrane", "firme.js")
    td = _bloc(firme, '<td class="tn-actiuni">', "</td>")
    liber = _in_afara_meniului(td)
    assert "data-storno=" not in liber and "data-del=" not in liber
    assert "meniuActiuni([" in td and "data-storno=" in td and "data-del=" in td


def test_produse_sterge_numai_in_meniu():
    pr = _sursa("ecrane", "produse_ecran.js")
    drept = _bloc(pr, '<div class="pr-rand-drept">', "</div>\n    </div>`).join")
    assert "pr-sterge" not in _in_afara_meniului(drept)
    assert "meniuActiuni([" in drept and "pr-sterge" in drept
    assert "\\u00d7" not in drept   # nu mai e „×” liber pe rând


def test_de_validat_respinge_numai_in_meniu_validare_ramane():
    v = _sursa("ecrane", "validat.js")
    nota = _bloc(v, "function randNotaCoada(", "// [622] Rândul unei ciorne proprii")
    liber = _in_afara_meniului(nota)
    assert "val-aproba" in liber                       # „Validează” rămâne vizibilă
    assert "val-respinge" not in liber and "respinge-nota" not in liber
    assert "meniuActiuni([" in nota and "val-respinge" in nota
    decl = _bloc(v, "// Aprobă — doar dacă pot valida", "} else {\n    // depune")
    assert "val-respinge" not in _in_afara_meniului(decl)


def test_clienti_pastreaza_meniul_si_actiunea_obisnuita():
    cl = _sursa("ecrane", "clienti_ecran.js")
    td = _bloc(cl, '<td><button class="buton-secundar ${P}-salveaza"', "</td>")
    liber = _in_afara_meniului(td)
    assert "-salveaza" in liber and "${P}-sterge" not in liber and "fisa-anaf" not in liber
    assert "meniuActiuni([" in td


def test_nicio_actiune_distructiva_libera_pe_ecranele_martor():
    """Pe cele cinci ecrane martor, un buton cu text distructiv sau cu clasa de ștergere nu stă în afara meniului, în celula/rândul de rând."""
    pr = _in_afara_meniului(_bloc(_sursa("ecrane", "produse_ecran.js"), '<div class="pr-rand-drept">', "</div>\n    </div>`).join"))
    cl = _in_afara_meniului(_bloc(_sursa("ecrane", "clienti_ecran.js"), '<td><button class="buton-secundar ${P}-salveaza"', "</td>"))
    for text in (pr, cl):
        for cuv in DISTRUCTIVE:
            assert f">{cuv}<" not in text


def test_d104_eticheta_vizibila_cu_semn():
    d = _sursa("ecrane", "declaratii.js")
    m = re.search(r'<span class="camp-eticheta"[^>]*>([^<]*)<span class="oblig">\*</span></span><input id="d104-profit"', d)
    assert m, "câmpul d104-profit nu mai are eticheta în forma așteptată"
    assert m.group(1).strip() == "Profit(+)/pierdere(-)"


def test_un_singur_data_actiune_principala_pe_ferestrele_cu_marcaj():
    """Niciun șablon de ecran nu marchează două butoane `data-actiune-principala` în același corp."""
    for fis in sorted(os.listdir(os.path.join(JS, "ecrane"))):
        if not fis.endswith(".js"):
            continue
        for sablon in re.findall(r"`[^`]*`", _sursa("ecrane", fis), flags=re.S):
            assert len(re.findall(r"<button\b[^>]*\bdata-actiune-principala\b", sablon)) <= 1, fis


def test_export_pdf_nu_ia_locul_actiunii_proprii():
    """`_exportTabel` alege butonul principal propriu al ferestrei (unul singur, eligibil, nu „Descarcă PDF”) și lasă ferestrele din EXPORT_PDF cu PDF-ul."""
    cadru = _sursa("cadru.js")
    f = _bloc(cadru, "function _exportTabel(", "// o urmă (comentariu)")
    assert "EXPORT_PDF.test(titlu" in f and "proprii.length === 1" in f and 'button.buton-primar' in f
    assert "__slab = true" in f and "__catalog = true" in f   # drumul butoanelor găsite de catalog: fără id rămâne în fereastră (X07 e.1: 13 copii în #ss-butoane), în bară stă un proxy
    assert "_eligibilPrincipal(bara, liber)" in cadru
