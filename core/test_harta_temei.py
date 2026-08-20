# -*- coding: utf-8 -*-
"""GARD (R5, 20.08.2026): în harta casetelor, temeiul legal nu se amestecă cu regula de produs.

DE CE. Cele două SE REVIZUIESC DIFERIT. Un temei legal se schimbă când se schimbă legea, și nu decizi
tu nimic. O regulă de produs se schimbă când decizi tu, iar „mai e bună?" e o întrebare legitimă
oricând. Amestecate, o regulă de produs devine imposibil de repus în discuție — nimeni nu contestă un
articol de lege — iar o prevedere legală devine negociabilă, ceea ce e mai rău.

INSTANȚA CARE A PRODUS REGULA: indicatorul de patru ochi. Etichetat drept temei legal în loc de control
intern, nimeni n-ar fi întrebat dacă „posibil" înseamnă ≥2 validatori, și fundătura rămânea.

STAREA LA INSTALARE, măsurată: toate cele 6 intrări `TEMEI` trimiteau la COD — `core/scadente.py`,
`control_fiscal_api._stare(...)`, „soldurile 4426/4427". Zero citări de act. Iar `TEMEI` n-avea niciun
consumator: o regulă scrisă care nu era o regulă păzită. Gardul ăsta e primul ei cititor.

CE PĂZEȘTE ȘI CE NU. Păzește că fiecare intrare face o AFIRMAȚIE explicită despre temeiul legal — o
citare, un `None` asumat, sau o `DATORIE` care spune unde se urmărește — și că citările aterizează pe un
document care există în corpus. NU păzește că documentul chiar spune ce pretinzi: aia e treaba
arbitrului, nu a unui gard sintactic. Distincția e reală și se pierde ușor.
"""
import json
import os
import re
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VIZ = os.path.join(_RAD, "frontend_test", "vizual")
if _VIZ not in sys.path:
    sys.path.insert(0, _VIZ)


def _harta():
    import harta_casete
    return harta_casete


def _acte_din_corpus():
    """Perechile `<nr>_<an>` care apar în numele fișierelor din corpus + în `acopera`.

    Cheia e `nr_an`, nu numele complet: `1802/2014` trebuie să prindă `omfp_1802_2014.pdf`, iar
    `227/2015` să prindă `cod_fiscal_227_2015_consolidat.html` — prefixele diferă, perechea nu.
    """
    idx = os.path.join(_RAD, "anaf_surse", "INDEX.json")
    with open(idx, encoding="utf-8") as f:
        d = json.load(f)
    acte = set()
    for nume, meta in d["fisiere"].items():
        for m in re.finditer(r"(?<!\d)(\d{1,5})_(19|20)(\d{2})(?!\d)", nume):
            acte.add("%s/%s%s" % (m.group(1), m.group(2), m.group(3)))
        for a in meta.get("acopera") or []:
            for m in re.finditer(r"(?<!\d)(\d{1,5})/((?:19|20)\d{2})", a.get("temei", "")):
                acte.add("%s/%s" % (m.group(1), m.group(2)))
    return acte


def test_fiecare_intrare_are_ambele_campuri():
    """Structura. Un câmp lipsă e mai rău decât unul gol: golul e o afirmație, absența e o scăpare."""
    h = _harta()
    rele = [k for k, v in h.TEMEI.items()
            if not isinstance(v, dict) or "temei_legal" not in v or "regula_produs" not in v]
    assert not rele, "intrări fără ambele câmpuri (vezi R5): %s" % rele


def test_temeiul_legal_e_o_afirmatie_explicita():
    """`None` e permis — înseamnă «nu are temei legal, e produs curat». Ce NU e permis e ABSENȚA
    afirmației: un câmp care lipsește, sau un text care doar trimite la cod fără să spună că e datorie."""
    h = _harta()
    rele = []
    for k, v in h.TEMEI.items():
        t = v["temei_legal"]
        if t is None:
            continue
        if isinstance(t, dict):
            if t.get("stare") != "datorie" or not t.get("unde"):
                rele.append("%s: datorie fără `unde`" % k)
            continue
        if not isinstance(t, str) or not re.search(r"\d{1,5}/(?:19|20)\d{2}", t):
            rele.append("%s: `%r` nu e nici citare de act, nici datorie declarată, nici None asumat" % (k, t))
    assert not rele, "\n".join(rele)


def test_citarile_aterizeaza_in_corpus():
    """Un act citat trebuie să existe pe disc. NU verifică dacă actul spune ce pretinzi — aia cere
    arbitrul. Verifică doar că citarea e rezolvabilă, adică nu e o trimitere în gol."""
    h = _harta()
    corpus = _acte_din_corpus()
    lipsa = []
    for k, v in h.TEMEI.items():
        t = v["temei_legal"]
        if not isinstance(t, str):
            continue
        for m in re.finditer(r"(\d{1,5})/((?:19|20)\d{2})", t):
            act = "%s/%s" % (m.group(1), m.group(2))
            if act not in corpus:
                lipsa.append("%s: `%s` citat în `%s` nu are document în anaf_surse/" % (k, act, t))
    assert not lipsa, "\n".join(lipsa)


def test_regula_de_produs_poarta_decizia_si_data():
    """Funcția spune CE face; decizia spune DE CE și CÂND. Fără dată, peste șase luni nu se știe dacă
    regula a fost gândită sau a apărut din inerție. `NEDOCUMENTATA` e un răspuns valid — tăcerea nu."""
    h = _harta()
    rele = []
    for k, v in h.TEMEI.items():
        p = v["regula_produs"]
        if p is None:
            continue
        if not isinstance(p, dict) or not p.get("regula") or "decizie" not in p or "data" not in p:
            rele.append("%s: regulă de produs fără `regula`/`decizie`/`data`" % k)
            continue
        if p["decizie"] != h.NEDOCUMENTATA and not p["data"]:
            rele.append("%s: decizia `%s` n-are dată" % (k, p["decizie"]))
        if p["decizie"] == h.NEDOCUMENTATA and p["data"]:
            rele.append("%s: decizie NEDOCUMENTATA dar cu dată — contradicție" % k)
    assert not rele, "\n".join(rele)


def test_o_intrare_nu_poate_fi_tacuta_pe_amandoua():
    """Nu se poate ca și temeiul legal, și regula de produs să lipsească. O casetă guvernată de o
    regulă e guvernată de ceva; dacă nu se poate numi, intrarea n-are ce căuta în TEMEI."""
    h = _harta()
    mute = [k for k, v in h.TEMEI.items() if v["temei_legal"] is None and not v["regula_produs"]]
    assert not mute, "intrări fără nicio regulă numită: %s" % mute


# ─────────── ANTI-VACUU ───────────
def test_gardul_chiar_vede_harta_si_corpusul():
    """Dacă importul se rupe sau INDEX.json își schimbă forma, toate testele de mai sus trec pe gol."""
    h = _harta()
    assert len(h.TEMEI) >= 6, "harta s-a golit: %d intrări" % len(h.TEMEI)
    corpus = _acte_din_corpus()
    assert len(corpus) >= 30, "corpusul văzut e implauzibil de mic (%d acte) — verifică INDEX.json" % len(corpus)
    assert "1802/2014" in corpus, "OMFP 1802/2014 e pe disc dar nu e văzut — parserul de nume s-a rupt"
    # și că gardul vede efectiv fiecare fel din cele trei, altfel ramurile lui n-au fost exercitate
    feluri = {("datorie" if isinstance(v["temei_legal"], dict) else
               "citare" if isinstance(v["temei_legal"], str) else "produs_curat")
              for v in h.TEMEI.values()}
    assert feluri == {"datorie", "citare", "produs_curat"}, \
        "harta nu mai conține toate cele trei feluri de temei: %s" % feluri
