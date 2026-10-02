# -*- coding: utf-8 -*-
"""GARD — un act din corpus e ÎNTREG: înlocuirea nu pierde articole, iar documentele lui de pe portal sunt toate aici.

  core/test_corpus_continut.py

De ce (02.10.2026, comanda lui Costin, lot 19 pct.3). La Pachetul FiscalOS §1 (01.10) OPANAF 2594/2015 și 878/2022 au
fost „înlocuite cu forma consolidată oficială” — iar forma nouă era documentul-ANEXĂ (procedura), publicat separat pe
portal: 10/10, respectiv 13/13 articole ale ordinului lipseau. Toate gărzile de corpus erau verzi: amprenta era
oficială, titlul confirma numărul, PROVENIENTA era completă. **Niciuna nu întreba dacă CONȚINUTUL e cel dinainte.**
Generalizarea a arătat clasa întreagă: 21 de acte ale manifestului FiscalOS aveau în corpus doar o parte din
documentele lor de pe portal (ordinul fără anexa integrală, sau invers, sau doar un extras), plus facsimilele.

Trei verificări:
  1. **Pe articol, nu pe octeți** — fiecare formă veche din `anaf_surse/_inlocuite_*/` are TOATE articolele/anexele
     regăsite în fișierele actului din corpus (`core.corpus_continut`: PREZENT, sau MODIFICAT declarat de portal).
     Excepțiile sunt NOTE editoriale ale portalului, declarate una câte una, cu motivul verificat.
  2. **Documentele actului** — pentru fiecare act al manifestului corpusului FISCAL prezent în corpus,
     `scripts.import_corpus_fiscal.planifica_materiale()` nu mai găsește niciun document lipsă.
  3. **Identitatea materialelor** — un fișier `<act>__<rol>_<id>` are amprenta unui material al ACELUI act din manifest
     (gardul de identitate pe titlu nu le poate citi: o anexă poartă „PROCEDURĂ din …”, fără număr).

CE NU PRINDE, declarat:
  · o înlocuire care NU arhivează forma veche în `_inlocuite_*` nu are cu ce fi comparată (verificarea 1); o înlocuire
    care o declară în PROVENIENTA („veche in _inlocuite_X/”) fără arhivă e prinsă de `test_inlocuirea_declarata_are_arhiva`;
  · un act care nu e în manifestul FiscalOS nu are listă de documente cu care să fie confruntat (verificarea 2);
  · structura nemarcată (text fără „Articolul N” / `S_ART`) nu are unități — se judecă pe acoperirea textului întreg
    doar la import, nu aici.
"""
import io
import json
import os
import re

import pytest

from core import corpus_continut as cc

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(RAD, "anaf_surse")
MANIFEST = os.path.join(RAD, "import_fiscalos", "active", "manifest.json")

# NOTE editoriale ale portalului (nu text al actului), prezente în forma veche și absente din cea nouă. Fiecare a
# fost citită pe 02.10.2026; `acoperit_de` = fișierul din corpus unde textul citat chiar trăiește (verificat aici).
EXCEPTII = {
    ("legea_136_2020_consolidat.txt", "Art. IV"): dict(
        n=1, acoperit_de=None,
        motiv="Notă care reproduce art.IV din OUG 180/2020 (finanțarea medicilor de familie, COVID-19); consolidarea "
              "nouă a portalului n-o mai poartă. Nu e text al Legii 136/2020 și nu e normă fiscală."),
    ("legea_448_2006_protectia_persoanelor_cu_handicap.txt", "Articolul III"): dict(
        n=1, acoperit_de=None,
        motiv="Notă care reproduce art.III din OUG 90/2025 în forma inițială („până la data de 30 iunie 2026”); forma "
              "nouă reproduce articolul MODIFICAT ulterior — evoluția actului citat, nu pierdere."),
    ("legea_70_2015_consolidat.txt", "Articolul 18"): dict(
        n=1, acoperit_de=None, articol_in="legea_70_2015_consolidat.html",
        motiv="Unitatea txt veche = rând de cuprins + semnături + subsolul paginii („Forma printabilă…”); articolul 18 "
              "există în forma html nouă (verificat: are unitate cu același titlu acolo, iar perechea html n-a pierdut nimic)."),
    ("oug_120_2021.txt", "Articolul 9"): dict(
        n=2, acoperit_de=None, articol_in="oug_120_2021.html",
        motiv="(a) rând de cuprins „Articolul 9 Secţiunea a 4-a” — cuprinsul nou e așezat altfel; (b) nota „începând cu "
              "01.07.2024 conform pct.3 art.LXV din Legea 296/2023…” eliminată din consolidarea nouă. Corpul art.9 e "
              "prezent (html: 0 articole pierdute)."),
    ("oug_120_2021.txt", "Articolul LXXI"): dict(
        n=2, acoperit_de="oug_115_2023_consolidat.txt",
        fragment="În situația în care sistemul național privind factura electronică RO e-Factura nu este funcțional timp "
                 "de minimum 24 de ore",
        motiv="Nota care reproduce art.LXXI din OUG 115/2023 (RO e-Factura nefuncțional ≥ 24h): (a) antetul notei "
              "(„Articolul LXXI, Capitolul II din OUG 115/2023 … prevede:”), (b) textul articolului — care e în corpus în "
              "OUG 115/2023 (verificat: textul citat e acoperit acolo)."),
}


def _stem(f):
    from scripts.import_corpus_fiscal import _stem_act
    return _stem_act(f)


def _arhive():
    return sorted(os.path.join(CORPUS, d) for d in os.listdir(CORPUS)
                  if d.startswith("_inlocuite_") and os.path.isdir(os.path.join(CORPUS, d)))


def _perechi():
    """(cale_veche, [căi noi]) — forma veche și fișierele actului din corpus, de același fel (html↔html, txt↔txt)."""
    top = sorted(os.listdir(CORPUS))
    out = []
    for arh in _arhive():
        for f in sorted(os.listdir(arh)):
            if not f.endswith((".html", ".txt")):
                continue
            ext = os.path.splitext(f)[1]
            st = _stem(f)
            noi = [os.path.join(CORPUS, g) for g in top
                   if g.endswith(ext) and (g == f or (st and _stem(g) == st)) and "__facsimil_" not in g]
            out.append((os.path.join(arh, f), noi))
    return out


@pytest.fixture(scope="module")
def pierderi():
    """{(fișier_vechi, titlu): [unități pierdute]} pe toată arhiva; plus numărul de unități comparate."""
    rez, comparate = {}, 0
    for vechi, noi in _perechi():
        assert noi, "forma veche %s nu are NICIUN fișier al actului în corpus" % os.path.basename(vechi)
        comparate += len(cc.unitati(vechi))
        for u, _a in cc.pierderi_act(vechi, noi):
            rez.setdefault((os.path.basename(vechi), u["titlu"]), []).append(u)
    return rez, comparate


def test_ANTIVACUU_arhiva_are_perechi_si_unitati(pierderi):
    _rez, comparate = pierderi
    assert len(_perechi()) >= 80, "doar %d perechi formă veche/nouă — arhiva nu mai e citită" % len(_perechi())
    assert comparate >= 10000, "doar %d unități comparate — extragerea articolelor s-a rupt" % comparate


def test_nicio_forma_inlocuita_nu_pierde_articole(pierderi):
    rez, _ = pierderi
    rele = []
    for cheie, lista in sorted(rez.items()):
        ex = EXCEPTII.get(cheie)
        if ex and len(lista) <= ex["n"]:
            continue
        rele.append("%s :: %s ×%d — %s" % (cheie[0], cheie[1], len(lista), lista[0]["text"][:160]))
    assert not rele, (
        "articole/anexe din forma VECHE absente din forma nouă a actului (comparate pe conținut):\n  %s\n\n"
        "O formă „oficială” poate fi alt document al aceluiași act (ex. anexa publicată separat pe portal)."
        % "\n  ".join(rele))


def test_exceptiile_sunt_reale_si_textul_citat_traieste_unde_spun(pierderi):
    """O excepție care nu mai e nevoie (unitatea a reapărut) sau al cărei `acoperit_de` nu mai acoperă textul = minciună."""
    rez, _ = pierderi
    for (f, titlu), ex in EXCEPTII.items():
        assert (f, titlu) in rez, "excepția %s :: %s nu mai e folosită — se scoate" % (f, titlu)
        if ex.get("articol_in"):
            chei = {u["cheie"] for u in cc.unitati(os.path.join(CORPUS, ex["articol_in"]))}
            assert cc._titlu(titlu) in chei, "%s nu există în %s, deși excepția o afirmă" % (titlu, ex["articol_in"])
        if ex["acoperit_de"]:
            # fragmentul verbatim al textului citat: e în forma veche (nota) ȘI în actul unde excepția spune că trăiește
            frag = " ".join(cc._cuvinte(cc._norm(ex["fragment"])))
            vechi = " ".join(cc._cuvinte(" ".join(u["text"] for u in rez[(f, titlu)])))
            unde = " ".join(cc._cuvinte(cc.text_integral(os.path.join(CORPUS, ex["acoperit_de"]))))
            assert frag in vechi, "fragmentul excepției %s :: %s nu e în nota veche" % (f, titlu)
            assert frag in unde, "textul citat de %s :: %s nu e în %s, deși excepția o afirmă" % (f, titlu, ex["acoperit_de"])


def test_inlocuirea_declarata_are_arhiva():
    prov = json.load(io.open(os.path.join(CORPUS, "PROVENIENTA.json"), encoding="utf-8"))["fisiere"]
    lipsa = []
    for f, v in prov.items():
        # „(veche in _inlocuite_X/)" = forma veche are ACELAȘI nume; „(veche in _inlocuite_X/<fișier>)" o numește.
        m = re.search(r"\(veche in (_inlocuite_[^/)]+)/([^)\s]*)\)", v.get("motiv", "") if isinstance(v, dict) else "")
        if m and not os.path.isfile(os.path.join(CORPUS, m.group(1), m.group(2) or f)):
            lipsa.append("%s -> %s/%s" % (f, m.group(1), m.group(2) or f))
    assert not lipsa, "înlocuiri declarate fără forma veche arhivată (nu se mai pot compara):\n  " + "\n  ".join(lipsa)


def test_actele_din_manifest_au_toate_documentele():
    from scripts import import_corpus_fiscal as icf
    imp, acoperite, probleme = icf.planifica_materiale()
    assert len(acoperite) >= 150, "doar %d materiale acoperite — planificarea nu mai vede manifestul" % len(acoperite)
    assert not probleme, probleme
    assert not imp, (
        "documente ale unor acte din corpus, publicate separat pe portal, LIPSĂ din corpus:\n  %s\n\n"
        "Se aduc cu: python -m scripts.import_corpus_fiscal --materiale --scrie"
        % "\n  ".join("%s %s %s" % (x["pid"], x["rol"], x["target"]) for x in imp))


def test_materialele_poarta_amprenta_actului_lor():
    import hashlib
    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    from scripts.import_corpus_fiscal import FAM, _provenienta_act
    sha_act, ids_act = {}, {}
    for a in man["acts"]:
        mt = re.match(r"^([A-Z]+)\s+(\d+)/(\d{4})$", a["identity"].get("opis_identity", "").strip())
        if mt and mt.group(1) in FAM:
            st = "%s_%s_%s" % (FAM[mt.group(1)], mt.group(2), mt.group(3))
            for mm in _provenienta_act(a["POSITION_ID"])["materials"]:
                sha_act.setdefault(st, set()).add(mm["source_SHA256"])
                ids_act.setdefault(st, set()).add((mm.get("official_source") or "").rstrip("/").split("/")[-1])
    materiale = [f for f in os.listdir(CORPUS) if re.search(r"__(baza|anexa|istoric|facsimil)_", f)
                 and not f.endswith(".sha256")]
    assert len(materiale) >= 130, "doar %d documente-material în corpus" % len(materiale)
    prov = json.load(io.open(os.path.join(CORPUS, "PROVENIENTA.json"), encoding="utf-8"))["fisiere"]
    rele = []
    for f in materiale:
        st = f.split("__", 1)[0]
        h = hashlib.sha256(io.open(os.path.join(CORPUS, f), "rb").read()).hexdigest()
        if h in sha_act.get(st, ()):
            continue
        # Procedurile 2594/878 au venit din `surse_oficiale` (altă descărcare, alți octeți decât manifestul): identitatea
        # se sprijină atunci pe id-ul DECLARAT — id-ul din nume e al unui document al actului ȘI PROVENIENTA îl poartă.
        idf = re.search(r"__(?:baza|anexa|istoric)_(\d+)\.", f)
        if idf and idf.group(1) in ids_act.get(st, ()) and "id_portal %s" % idf.group(1) in prov.get(f, {}).get("motiv", ""):
            continue
        rele.append("%s: nici amprenta, nici id-ul declarat nu sunt ale unui document al actului %s" % (f, st))
    assert not rele, "\n  ".join(rele)


# ── CALIBRARE: gardul chiar vede pierderea, și nu o vede acolo unde nu e ─────────────────────────────────────

def _html(*art):
    corp = "".join('<span class="S_ART"><span class="S_ART_TTL">Articolul %s</span><span class="S_ART_BDY">%s</span>'
                   "</span>" % (n, t) for n, t in art)
    return "<html><body>%s</body></html>" % corp


def test_CALIBRARE_regresia_reala_2594_e_ACUZATA():
    """Exact cazul care a produs gardul: ordinul arhivat comparat doar cu procedura-anexă."""
    vechi = os.path.join(CORPUS, "_inlocuite_fiscalos_2026-10-01", "ordin_2594_2015.html")
    procedura = os.path.join(CORPUS, "ordin_2594_2015__anexa_269686.html")
    p = cc.pierderi_act(vechi, [procedura])
    assert sum(1 for u, _a in p if u["tip"] == "articol") == 10, [u["titlu"] for u, _a in p]
    assert not cc.pierderi_act(vechi, [procedura, os.path.join(CORPUS, "ordin_2594_2015.html")])


def test_CALIBRARE_articol_scos_e_ACUZAT_modificat_declarat_si_nota_adaugata_nu(tmp_path):
    t1 = "contribuabilul depune declaratia pana la data de 25 a lunii urmatoare celei pentru care se datoreaza impozitul"
    t2 = "organul fiscal competent emite decizia de impunere in termen de 30 de zile de la data depunerii declaratiei"
    t3 = "prezentul ordin se publica in monitorul oficial al romaniei partea i si intra in vigoare la data publicarii"
    v = tmp_path / "v.html"
    v.write_text(_html(("1", t1), ("2", t2), ("3", t3)), encoding="utf-8")
    scos = tmp_path / "scos.html"
    scos.write_text(_html(("1", t1), ("3", t3)), encoding="utf-8")
    assert [u["titlu"] for u, _a in cc.pierderi_act(str(v), [str(scos)])] == ["Articolul 2"]
    modif = tmp_path / "modif.html"
    modif.write_text(_html(("1", t1), ("2", "Abrogat. (la 01-01-2026, Articolul 2 a fost abrogat de ...)"), ("3", t3)),
                     encoding="utf-8")
    assert not cc.pierderi_act(str(v), [str(modif)])
    nota = tmp_path / "nota.html"
    nota.write_text(_html(("1", t1 + " (la 01-01-2026, Articolul 1 a fost completat)"), ("2", t2), ("3", t3)),
                    encoding="utf-8")
    assert not cc.pierderi_act(str(v), [str(nota)])
