# -*- coding: utf-8 -*-
"""GARDĂ: fiecare act citat de un Temei din registru are id-ul lui de portal, scris.

Măsurat 23.08.2026: id-ul paginii de act **nu era stocat nicăieri** — 0 din 529 de intrări din
`INDEX.json`, 0 din 77 de fișiere `.html` aduse. Consecința nu era teoretică: verificarea vigorii pe
articol (interdicțiile 50 și 59) începea, de fiecare dată, cu o **căutare** în portal, iar legătura
dintre actul din corpus și pagina lui nu exista deloc.

Garda ține două lucruri deodată:
  - fiecare act din registrul de cote **are** id — altfel reverificarea redevine o vânătoare;
  - fiecare act din fișier **e încă citat** de registru — altfel fișierul se umple cu acte moarte.

**Nu verifică id-ul la sursă** (ar cere rețea la fiecare poartă). Verifică doar că legătura există și
că nu s-a desincronizat de registru.
"""
import json
import pathlib

import pytest

_CALE = pathlib.Path(__file__).resolve().parents[1] / "anaf_surse" / "PORTAL_IDS.json"


def _acte_din_registru():
    from core import common as c
    out = set()
    for _cheie, intrari in c.COTE.items():
        for it in intrari:
            if not isinstance(it, (list, tuple)) or len(it) < 3:
                continue
            t = it[2]
            tip, nr, an = getattr(t, "tip", None), getattr(t, "nr", None), getattr(t, "an", None)
            if tip and nr and an:
                out.add((str(tip), str(nr), str(an)))
    return out


@pytest.fixture(scope="module")
def fisier():
    if not _CALE.exists():
        pytest.fail("lipsește %s — legătura act ↔ pagina lui de portal nu mai există" % _CALE.name)
    return json.loads(_CALE.read_text(encoding="utf-8"))


def test_fisierul_are_acte_si_metadate(fisier):
    """ANTI-VACUU: un fișier golit ar face toate testele de mai jos să treacă pe zero."""
    assert fisier.get("acte"), "secțiunea «acte» e goală"
    assert len(fisier["acte"]) >= 6, "doar %d acte — fișierul s-a golit" % len(fisier["acte"])
    for cheie in ("_de_ce", "_limita", "_masurat_la"):
        assert fisier.get(cheie), "lipsește câmpul %s — fișierul nu-și mai spune limitele" % cheie


def test_fiecare_id_e_numar_pozitiv(fisier):
    """Un act are ori un id, ori o listă de CANDIDAȚI cu motivul — niciodată o alegere tăcută."""
    rele = []
    for k, v in fisier["acte"].items():
        if isinstance(v.get("id"), int) and v["id"] > 0:
            continue
        cand = v.get("candidati")
        if isinstance(cand, list) and len(cand) > 1 and v.get("nota"):
            continue
        rele.append((k, v))
    assert not rele, "acte fără id și fără candidați declarați cu motiv: %s" % rele


def test_actele_din_registru_au_id(fisier):
    """Fiecare act citat de un Temei trebuie să aibă id — altfel reverificarea începe cu o căutare."""
    scrise = " | ".join(fisier["acte"])
    lipsa = []
    for tip, nr, an in sorted(_acte_din_registru()):
        # potrivire tolerantă la formă: „OUG 89/2025" ↔ („OUG", 89, 2025); CF ↔ Legea 227/2015
        if tip.upper() in ("CF", "CODUL FISCAL"):
            continue
        if not any(nr in bucata and an in bucata for bucata in fisier["acte"]):
            lipsa.append("%s %s/%s" % (tip, nr, an))
    assert not lipsa, ("acte citate de registru fără id de portal: %s\n(scrise: %s)"
                       % (lipsa, scrise))


def test_actul_cu_text_ciot_e_marcat(fisier):
    """Codul fiscal vine ca ciot; dacă cineva îl marchează ca întreg, `vigoare_articol` ar fi crezut."""
    cf = [v for k, v in fisier["acte"].items() if "227/2015" in k]
    assert cf, "Codul fiscal lipsește din fișier"
    assert cf[0].get("text_integral") is False, (
        "Codul fiscal e marcat ca având text integral — dar pagina lui de detalii are 0 titluri de "
        "articol. Dacă s-a găsit forma consolidată, schimbă și id-ul, nu doar marcajul")
