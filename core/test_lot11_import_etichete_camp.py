# -*- coding: utf-8 -*-
"""[lotul 11, clasa găsită de scanul textului de pe ecrane: eticheta scrisă din cheia internă] Refuzul coloanelor ambigue
(`import_tabel.coloana`, „Coloanele «A», «B» se potrivesc toate la „…””) numea câmpul prin cheia lui internă, cu `_` înlocuit prin spațiu:
„cont stoc”, „cd”, „pif”, „valoare inventar”. Fiecare import care trimite câmpul primește acum eticheta lui, din `ETICHETE_CAMP`.
GARD: (1) fiecare cheie din `CAMPURI` a unui import care cheamă `coloana(…, camp=…)` are etichetă, și nicio etichetă nu e cheia însăși;
(2) `import_tabel` nu mai face din cheie text (`replace("_", " ")`). MUTAȚIE: o cheie scoasă din `ETICHETE_CAMP` -> (1) pică."""
import ast
import importlib
import io
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPORTURI = ("articole_import_api", "asociati_import_api", "istoric_declaratii_import_api", "mijloace_fixe_import_api",
             "retete_import_api", "rip_migrare_api", "salariati_import_api")


def _cu_campul_trimis():
    """Modulele din core/ care trimit în `coloana` aliasurile unei chei variabile din `CAMPURI` (`coloana(antet, CAMPURI[camp], …)`)."""
    out = []
    for f in sorted(os.listdir(os.path.join(_RAD, "core"))):
        if f.endswith(".py") and not f.startswith("test_"):
            arb = ast.parse(io.open(os.path.join(_RAD, "core", f), encoding="utf-8").read())
            if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "coloana" and len(n.args) > 1
                   and isinstance(n.args[1], ast.Subscript) and getattr(n.args[1].value, "id", None) == "CAMPURI"
                   and isinstance(n.args[1].slice, ast.Name) for n in ast.walk(arb)):
                out.append(f[:-3])
    return out


def test_importurile_cu_campul_trimis_sunt_cele_stiute():
    assert _cu_campul_trimis() == list(IMPORTURI), _cu_campul_trimis()


def test_fiecare_camp_de_import_are_eticheta_lui():
    rele = []
    for m in IMPORTURI:
        M = importlib.import_module("core." + m)
        et = getattr(M, "ETICHETE_CAMP", {})
        rele += ["%s.%s fără etichetă" % (m, k) for k in M.CAMPURI if not str(et.get(k) or "").strip()]
        rele += ["%s.%s: eticheta e cheia" % (m, k) for k, v in et.items() if v.replace(" ", "_") == k]
    assert not rele, rele


def _cheie_ca_text(arb):
    """Apelurile `x.replace("_", " ")` din arbore (cheia internă făcută text pentru om)."""
    return [n.lineno for n in ast.walk(arb) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "replace" and [getattr(a, "value", None) for a in n.args] == ["_", " "]]


def test_import_tabel_nu_scrie_cheia_ca_text():
    arb = ast.parse(io.open(os.path.join(_RAD, "core", "import_tabel.py"), encoding="utf-8").read())
    assert _cheie_ca_text(arb) == []
    assert _cheie_ca_text(ast.parse('x = (camp or a).replace("_", " ")')) == [1]   # anti-vacuu


def test_bunurile_art331_din_produse_au_denumirea_nu_cheia():
    """Aceeași clasă, pe ecranul Produse (449): lista bunurilor cu taxare inversă scria eticheta din cheia `d394.CODPR`
    („masa lemnoasa”, „aur investitii”, „cladiri terenuri” — prinse de `frontend_test/vizual/text_ecran_scan.py`). Eticheta vine acum din
    `taxare_inversa.CATEGORII[...]["eticheta"]`. MUTAȚIE: `coduri_331` readus la `k.replace("_", " ")` -> pică."""
    from core import produse_api, taxare_inversa
    et = {k: e for k, (e, _c) in produse_api.coduri_331().items() if k in taxare_inversa.CATEGORII}
    assert et and all(e == taxare_inversa.CATEGORII[k]["eticheta"] for k, e in et.items()), et
    assert et["masa_lemnoasa"] == "Masă lemnoasă" and et["aur_investitii"] == "Aur de investiții", et
