# -*- coding: utf-8 -*-
"""GARD [Y, 28.08.2026]: cifrele despre DATE din predare se recalculează, nu se citează.

DE UNDE VINE, cu instanța ei. Am scris în `PREDARE_LANT.md` *„**0 din 18** firme au `nume_anaf`"*.
Recitit pe date, douăzeci de minute mai târziu: **1 din 18**. Cifra fusese **deja invalidată o
dată**, iar corectura era scrisă în tabelul „cifre invalidate" **din aceeași predare**. Am purtat-o
din memorie, peste propriul meu tabel, la douăzeci de minute după ce scrisesem `METODA §10.16` —
regula care interzice exact asta.

Decizia lui Costin, 28.08: *„da, se construiește."* Recitirea nu mai e „mai multă grijă": e **o
comandă rulată**, iar rezultatul ei intră în document ca bloc **generat**.

CE FACE IMPOSIBIL:
  1. o cifră despre date, scrisă în predare, care nu se mai potrivește cu baza;
  2. un bloc editat cu mâna — se compară caracter cu caracter cu ce produce instrumentul;
  3. o cifră **culeasă** din bază și **necuprinsă** în bloc: dacă se măsoară, se și scrie.

CE NU FACE, declarat:
  - **nu acoperă cifrele despre COD** (rute, gărzi, teste) — au instrumentele lor;
  - **nu acoperă cifrele de PROCES** („a câta tură", „câte commituri în urmă") — nu se pot
    interoga; rămân afirmații datate, cu ora citirii (`METODA §10.16b`);
  - **nu interzice o cifră de date în PROZA predării.** Naratiunea are voie să spună „cele patru
    firme"; ce nu mai are voie e ca **tabelul** să fie scris din memorie. Un gard care ar interzice
    orice cifră din proză ar fi zgomot pe fiecare frază.

**LIMITA OPERAȚIONALĂ, și e reală:** blocul e derivat din date **vii**. Dacă portofoliul se schimbă
între generarea blocului și sfârșitul porții (~12,5 minute), garda pică — și pe drept: documentul
chiar nu mai descrie baza. Remediul e regenerarea, nu o toleranță. Diferența față de `TRASEE.md` și
de inventarul din `GARZI.md`, care sunt derivate din **cod**: codul nu se mișcă singur în timpul
porții, datele da.
"""
import io
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import scan_predare_cifre as sc  # noqa: E402

from core import db  # noqa: E402

_DOC = os.path.join(_RAD, "PREDARE_LANT.md")


def _cifre():
    db.init_pool()
    with db.get_conn() as conn:
        return sc.culege(conn)


def test_blocul_de_cifre_e_identic_cu_interogarea_de_ACUM():
    """doc↔cod, caracter cu caracter. Regenerare:
    `./venv/bin/python scripts/scan_predare_cifre.py --md`, rescris între marcaje."""
    doc = io.open(_DOC, encoding="utf-8").read()
    assert sc.MARCA_START in doc and sc.MARCA_STOP in doc, (
        "PREDARE_LANT.md n-are blocul de cifre generate — a fost șters? Fără el, cifrele despre "
        "date se scriu iar din memorie, iar asta a greșit de două ori în două zile.")
    a = doc.index(sc.MARCA_START)
    b = doc.index(sc.MARCA_STOP) + len(sc.MARCA_STOP)
    din_doc, generat = doc[a:b], sc.redare_md(_cifre())
    if din_doc != generat:
        ld, lg = din_doc.split(chr(10)), generat.split(chr(10))
        prima = next((i for i in range(max(len(ld), len(lg)))
                      if (ld[i] if i < len(ld) else None) != (lg[i] if i < len(lg) else None)), 0)
        raise AssertionError(
            "blocul de cifre din PREDARE_LANT.md nu mai descrie baza, prima diferență la linia "
            "%d:%s  doc:     %r%s  acum:    %r%s"
            "Regenerează: ./venv/bin/python scripts/scan_predare_cifre.py --md"
            % (prima + 1, chr(10), ld[prima] if prima < len(ld) else "(lipsește)", chr(10),
               lg[prima] if prima < len(lg) else "(lipsește)", chr(10)))


def test_orice_cifra_CULEASA_ajunge_in_bloc():
    """Direcția pe care doc↔cod n-o vede: o cifră măsurată și **necuprinsă** în tabel. Blocul ar fi
    identic cu el însuși și ar tăcea despre ea — adică exact forma de orbire prin construcție."""
    in_bloc = {c for _titlu, campuri in sc.RANDURI for c, _e in campuri}
    culese = set(_cifre())
    lipsa = sorted(culese - in_bloc)
    assert not lipsa, (
        "cifre interogate din bază și nescrise în bloc: %s — dacă se măsoară, se și scrie" % lipsa)
    inventate = sorted(in_bloc - culese)
    assert not inventate, (
        "rânduri din bloc fără cifră culeasă: %s — tabelul ar afirma ceva ce nu s-a măsurat"
        % inventate)


def test_ANTI_VACUU_instrumentul_chiar_interogheaza():
    d = _cifre()
    assert len(d) >= 15, "doar %d cifre culese — instrumentul s-a rupt" % len(d)
    assert d["firme"] > 5, (
        "[anti-vacuu] doar %d firme — blocul ar descrie o bază goală, iar toate zerourile de mai jos "
        "ar arăta ca o stare curată" % d["firme"])
    assert d["tabele_cu_tenant_id"] > 5


def test_CALIBRARE_o_cifra_schimbata_cu_MANA_e_prinsa():
    """Modul de eșec propriu regulii: cineva (eu) actualizează o cifră „din cap", fără să ruleze
    instrumentul. Se probează pe forma exactă — o singură cifră mutată în blocul generat."""
    d = _cifre()
    corect = sc.redare_md(d)
    stricat = corect.replace("| **%d** | firme în portofoliu |" % d["firme"],
                             "| **%d** | firme în portofoliu |" % (d["firme"] + 1))
    assert stricat != corect, "calibrarea n-a putut strica blocul — s-a schimbat forma tabelului"
    assert stricat != sc.redare_md(d), "o cifră schimbată cu mâna nu se vede"


def test_CALIBRARE_blocul_NU_poarta_ora_masuratorii():
    """A doua direcție, și e cea care ar fi rupt gardul din prima zi: dacă blocul ar purta ora, el
    s-ar schimba la fiecare rulare, comparația ar pica **întotdeauna**, iar cineva ar scoate garda
    ca să poată comite. Ora trăiește în antetul predării și în raport, unde e o afirmație despre
    CÂND, nu o cifră despre CE. (Aceeași lecție ca la inventarul din `GARZI.md`.)"""
    import re
    d = _cifre()
    bloc = sc.redare_md(d)
    assert bloc == sc.redare_md(d), "blocul nu e stabil la două redări pe aceleași cifre"
    ceas = re.findall(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", bloc)
    assert not ceas, "blocul poartă o oră (%s) — s-ar schimba la fiecare rulare" % ceas
    data = re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", bloc)
    assert not data, "blocul poartă o dată (%s) — la fel" % data
