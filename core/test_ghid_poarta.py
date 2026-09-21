# -*- coding: utf-8 -*-
"""GARD — poarta de verificare pre-publicare a ghidurilor (core/ghid_poarta.py).

Cerut de Costin, 21.09.2026 (producția de ghiduri, pasul 2). Face IMPOSIBILĂ publicarea unui ghid nou
care (2a) citează un act ce nu e în corpus, sau (2b) pretinde o funcționalitate care nu e livrată /
nu are sursă / nu e legată bidirecțional.

DOUĂ FELURI DE PROBĂ:
  · CALIBRARE — cazuri construite care confirmă că poarta chiar deosebește verde de roșu (un act real
    trece, unul fabricat pică; o funcție LIVE trece, una nelivrată/inexistentă/nelegată pică).
  · RATCHET — orice ghid din ghid/ care NU e în baseline-ul legacy (`_legacy_pre_poarta.txt`) trebuie
    să poarte `poarta: v1` ȘI să treacă verifica_ghid. Baseline-ul e înghețat (clichet): a-l umfla ca
    să ocolești poarta pică aici. Ghidurile legacy (scrise înainte de poartă) sunt grandfathered și
    declarate ca atare — unele citează acte încă neaduse în corpus (măsurat 21.09: 46 ghiduri).
"""
import io
import os

from core import ghid_poarta as gp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GHID = os.path.join(RAD, "ghid")
BASELINE = os.path.join(GHID, "_legacy_pre_poarta.txt")

# Clichet: numărul de ghiduri legacy la crearea porții (21.09.2026). NU poate crește — altfel un ghid
# nou strecurat în baseline ar ocoli poarta. Scade liber când se retrage un ghid legacy.
CLICHET_LEGACY = 202


def _legacy():
    with io.open(BASELINE, encoding="utf-8") as f:
        return {ln.strip() for ln in f if ln.strip() and not ln.startswith("#")}


def _slugs_pe_disc():
    return {f[:-3] for f in os.listdir(GHID) if f.endswith(".md")}


# ------------------------------------------------------------ CALIBRARE 2a (citări)
def test_CALIBRARE_act_real_din_corpus_trece():
    ac = gp.corpus_acte()
    # OUG 89/2025 e în corpus (oug_89_2025*), la fel Codul fiscal (cf_2015*).
    txt = "Cota e 1% conform OUG 89/2025 și art. 51 din Codul fiscal."
    assert gp.verifica_citari(txt, ac) == [], "un act prezent în corpus a fost respins fals"


def test_CALIBRARE_act_fabricat_pica():
    ac = gp.corpus_acte()
    lipsa = gp.verifica_citari("Potrivit OUG 9999/2099, se aplică regula X.", ac)
    assert any(a == ("oug", "9999", "2099") for _t, a in lipsa), \
        "un act inexistent în corpus a trecut — poarta 2a nu blochează"


def test_CALIBRARE_forma_cu_data_e_extrasa():
    """Regresie 21.09: forma «OUG nr. 89 din 23 decembrie 2025» era ratată (ziua «23» bloca
    ajungerea la an), deci o citare scrisă doar așa nu era verificată. Ambele forme se extrag."""
    assert ("oug", "89", "2025") in [a for _t, a in gp.citari("prin OUG nr. 89 din 23 decembrie 2025")]
    assert ("hg", "146", "2026") in [a for _t, a in gp.citari("HG nr. 146 din 3 martie 2026")]


def test_CALIBRARE_cod_fiscal_pe_articol_e_recunoscut():
    ac = gp.corpus_acte()
    assert gp.verifica_citari("Vezi art. 291 din Codul fiscal.", ac) == []
    assert gp.verifica_citari("Termenul din Codul de procedură fiscală.", ac) == []


# ------------------------------------------------------------ CALIBRARE 2b (funcționalități)
def test_CALIBRARE_functie_live_legata_trece():
    reg = gp._registru_functionalitati()
    # F031 = decont TVA D300, LIVE, sursă core/d300.py, ghid_slug=decont-tva-d300-rezultat.
    assert gp.verifica_functionalitati({"functionalitate": "F031"},
                                       "decont-tva-d300-rezultat", reg) == []


def test_CALIBRARE_functie_inexistenta_pica():
    reg = gp._registru_functionalitati()
    coduri = {c for _f, c, _d in gp.verifica_functionalitati({"functionalitate": "F999999"}, "x", reg)}
    assert gp.COD_INEXISTENT in coduri


def test_CALIBRARE_functie_nelivrata_pica():
    """O funcție cu stare != LIVE nu se poate prezenta ca existentă într-un ghid."""
    reg = gp._registru_functionalitati()
    nelivrate = [fid for fid, r in reg.items() if not (r.get("Stare") or "").startswith("LIVE")]
    assert nelivrate, "fixture invalid: registrul n-are nicio funcție nelivrată de calibrat pe ea"
    coduri = {c for _f, c, _d in gp.verifica_functionalitati({"functionalitate": nelivrate[0]}, "x", reg)}
    assert gp.COD_NELIVRAT in coduri


def test_CALIBRARE_backlink_lipsa_pica():
    reg = gp._registru_functionalitati()
    coduri = {c for _f, c, _d in
              gp.verifica_functionalitati({"functionalitate": "F031"}, "slug-care-nu-e-legat", reg)}
    assert gp.COD_FARA_BACKLINK in coduri


def test_frontmatter_echivalent_cu_parserul_de_servire():
    """Parserul din poartă e auto-conținut (core/ nu importă main), dar TREBUIE să dea exact ce dă
    parserul de servire `main._ghid_frontmatter`, altfel poarta ar valida altă formă decât cea
    randată. Pinat pe toate ghidurile reale. (Testul poate importa main; gardul e doar pe core/.)"""
    import main
    for fn in sorted(os.listdir(GHID)):
        if not fn.endswith(".md"):
            continue
        txt = io.open(os.path.join(GHID, fn), encoding="utf-8").read()
        assert gp._frontmatter(txt) == main._ghid_frontmatter(txt), fn


def test_fara_declaratie_de_functionalitate_nu_e_pretentie():
    assert gp.verifica_functionalitati({}, "orice", gp._registru_functionalitati()) == []


# ------------------------------------------------------------ RATCHET (gardul propriu-zis)
def test_baseline_legacy_nu_creste():
    assert len(_legacy()) <= CLICHET_LEGACY, (
        "baseline-ul legacy a crescut peste clichet (%d) — un ghid nou strecurat în listă ocolește "
        "poarta. Baseline-ul poate doar scădea." % CLICHET_LEGACY)


def test_ghiduri_noi_poarta_verde():
    """Orice ghid care NU e legacy trebuie să poarte `poarta:` și să treacă ambele controale."""
    legacy = _legacy()
    ac, reg = gp.corpus_acte(), gp._registru_functionalitati()
    fara_marcaj, rosii = [], []
    for slug in sorted(_slugs_pe_disc() - legacy):
        cale = os.path.join(GHID, slug + ".md")
        meta, _ = gp._frontmatter(io.open(cale, encoding="utf-8").read())
        if not meta.get("poarta", "").strip():
            fara_marcaj.append(slug)
            continue
        ok, probleme = gp.verifica_ghid(cale, ac, reg)
        if not ok:
            rosii.append("%s:\n    %s" % (slug, "\n    ".join(probleme)))
    assert not fara_marcaj, (
        "ghiduri noi (non-legacy) fără frontmatter `poarta: v1` — un ghid nou trebuie să treacă poarta:\n  "
        + "\n  ".join(fara_marcaj))
    assert not rosii, "ghiduri noi care NU trec poarta:\n  " + "\n  ".join(rosii)
