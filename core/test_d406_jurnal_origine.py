# -*- coding: utf-8 -*-
"""GARD (R22, prag 1): `JournalID` din D406 poartă jurnalul de ORIGINE, nu o constantă.

CE FACE IMPOSIBIL: ca declarația care pleacă la ANAF să afirme că toate înregistrările vin din
același jurnal, când evidența știe altceva. Până la 23.08.2026 `_gl_entries` scria literalul
`GENERAL` pe tot — elementul cerut de OMFP 2634/2015 Anexa 1 pct. 58 lit. i) *(„jurnalul de origine
în care se regăsesc înregistrările contabile")* exista și **nu purta nicio informație**.

DE CE PRAG 1, nu restanță: nu e o absență, e o afirmație falsă, iar destinatarul ei e autoritatea.

CE NU FACE, declarat: nu verifică dacă maparea `sursă → jurnal` e cea potrivită contabilicește —
verifică doar că maparea EXISTĂ, că e respectată, că nu se inventează un jurnal și că valorile
încap în tipurile schemei. Alegerea denumirilor e o decizie de produs, scrisă în `_JURNALE`.

ARBITRU: structura cu mai multe `<Journal>` a fost trecută prin validatorul oficial ANAF
(DUKIntegrator, D406, reguli 2026.1) pe tenant_013/2026-08 — **valid, zero erori**.
"""
import inspect
import io
import re
from datetime import date
from decimal import Decimal

import pytest

from core import d406


def _nota(nid, jurnal):
    n = d406.Nota(id=nid, data=date(2026, 8, 10), descriere="Probă %s" % nid, jurnal=jurnal)
    n.linii = [d406.LinieNota(record_id="1", cont="5311", descriere="", debit=Decimal("100")),
               d406.LinieNota(record_id="2", cont="5121", descriere="", credit=Decimal("100"))]
    return n


class _Res:
    an, luna = 2026, 8
    prof = {"cui": "RO1234567897", "nume": "Probă SRL"}

    def __init__(self, note):
        self.note = note


def _xml(note):
    return "\n".join(d406._gl_entries(_Res(note)))


# ─────────────────────────────────────────────────── maparea sursă → jurnal
def test_sursa_cunoscuta_isi_gaseste_jurnalul():
    """Calibrare pozitivă: fiecare sursă din nomenclator dă jurnalul ei, nu DIVERSE."""
    assert d406.jurnal_din_sursa("casa")[0] == "CASA"
    assert d406.jurnal_din_sursa("banca")[0] == "BANCA"
    assert d406.jurnal_din_sursa("salarii")[0] == "SALARII"
    assert d406.jurnal_din_sursa("amortizare")[0] == "AMORTIZARE"
    assert d406.jurnal_din_sursa("facturi")[0] == "FACTURI"
    assert d406.jurnal_din_sursa("  CASA  ")[0] == "CASA", "sursa se normalizează (spații, majuscule)"


@pytest.mark.parametrize("necunoscut", [None, "", "   ", "migrare", "iconta", "t", "ceva_nou"])
def test_sursa_necunoscuta_cade_in_DIVERSE_nu_intr_un_jurnal_inventat(necunoscut):
    """`migrare` și `iconta` există în coloană și NU sunt jurnale — sunt proveniența unui import."""
    assert d406.jurnal_din_sursa(necunoscut)[0] == "DIVERSE"


def test_valorile_incap_in_tipurile_SCHEMEI():
    """Limitele sunt ale schemei ANAF, citite din `anaf_surse/d406_schema_anaf.xlsx`:
    GL.5 JournalID = SAFshorttextType (18) · GL.6 Description = SAFlongtextType (256) ·
    GL.7 Type = SAFcodeType (9). O denumire prea lungă e respinsă de ANAF, nu de noi."""
    toate = [d406.jurnal_din_sursa(s) for s in list(d406._JURNALE) + ["ceva_nemapat"]]
    assert len(toate) > 1, "nomenclatorul de jurnale e gol — gardul ar trece pe zero rânduri"
    for jid, desc, tip in toate:
        assert 0 < len(jid) <= 18, "JournalID %r depășește SAFshorttextType (18)" % jid
        assert 0 < len(desc) <= 256, "Description pentru %s depășește SAFlongtextType (256)" % jid
        assert 0 < len(tip) <= 9, "Type %r depășește SAFcodeType (9)" % tip


# ─────────────────────────────────────────────────────────────── emiterea
def test_niciun_JournalID_inventat_in_XML():
    """Mutația care readuce constanta face testul roșu: `GENERAL` n-are voie să apară."""
    x = _xml([_nota("1", "CASA"), _nota("2", "BANCA")])
    ids = re.findall(r"<JournalID>([^<]*)</JournalID>", x)
    assert ids, "niciun JournalID emis — detectorul a orbit, nu codul s-a curățat"
    assert "GENERAL" not in ids, "JournalID e din nou o constantă: %r" % ids
    assert set(ids) == {"CASA", "BANCA"}


def test_un_Journal_per_jurnal_de_origine_si_notele_nu_se_amesteca():
    """Anti-vacuu + fond: două surse => două blocuri, iar fiecare tranzacție stă în blocul ei."""
    x = _xml([_nota("1", "CASA"), _nota("2", "BANCA"), _nota("3", "CASA")])
    assert x.count("<Journal>") == 2 == x.count("</Journal>"), "blocurile nu se închid pereche"
    blocuri = re.findall(r"<Journal>(.*?)</Journal>", x, re.S)
    per_jurnal = {}
    for b in blocuri:
        jid = re.search(r"<JournalID>([^<]*)</JournalID>", b).group(1)
        per_jurnal[jid] = re.findall(r"<TransactionID>([^<]*)</TransactionID>", b)
    assert per_jurnal == {"BANCA": ["2"], "CASA": ["1", "3"]}, per_jurnal


def test_o_nota_fara_jurnal_nu_pierde_elementul():
    """Norma cere elementul pe FIECARE înregistrare — o notă fără sursă intră în DIVERSE,
    nu rămâne fără `<Journal>`."""
    x = _xml([_nota("1", "")])
    assert "<JournalID>DIVERSE</JournalID>" in x
    assert x.count("<TransactionID>") == 1


def test_ordinea_notelor_in_interiorul_jurnalului_ramane_cea_din_pull():
    """Gruparea sortează pe jurnal, nu pe notă: în interiorul unui jurnal ordinea e neatinsă."""
    x = _xml([_nota("10", "CASA"), _nota("2", "CASA"), _nota("33", "CASA")])
    assert re.findall(r"<TransactionID>([^<]*)</TransactionID>", x) == ["10", "2", "33"]


# ─────────────────────────────────────────────── ANTI-VACUU pe cablare
def test_pull_chiar_citeste_sursa_si_genereaza_chiar_avertizeaza():
    """Maparea ar fi decorativă dacă `pull` n-ar citi coloana sau `genereaza` n-ar spune nimic
    despre sursele nemapate. Se citește sursa funcțiilor, nu doar existența lor."""
    sp = inspect.getsource(d406.pull)
    assert "i.sursa" in sp, "`pull` nu mai citește coloana `sursa` — maparea rămâne fără intrare"
    assert "jurnal_din_sursa(" in sp, "`pull` nu mai trece sursa prin mapare"
    assert "surse_necunoscute" in sp, "`pull` nu mai colectează sursele nemapate"
    sg = inspect.getsource(d406.genereaza)
    assert "surse_necunoscute" in sg and "avertismente" in sg, \
        "o sursă nemapată ar deveni DIVERSE în tăcere — exact defaultul tacit interzis"


# ──────────────────────────────── FELURILE sunt ale NORMEI, nu ale noastre (interdicția 28)
_CORPUS = "/home/costin/iconta_nou/anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt"


def test_felurile_de_jurnal_sunt_VERBATIM_din_norma():
    """`Description` nu e o denumire inventată de noi: e felul de operațiuni numit de OMFP 2634/2015,
    Anexa 1 pct. 52. Gardul nu citește proză — caută textul LITERAL în corpus. O reformulare, oricât
    de nevinovată, îl face roșu; asta e chiar clasa interdicției 28."""
    corpus = io.open(_CORPUS, encoding="utf-8").read()
    assert d406._FELURI, "nomenclatorul felurilor e gol"
    lipsa = [f for f in d406._FELURI.values() if f not in corpus]
    assert not lipsa, "feluri care NU se regăsesc verbatim în corpus: %r" % lipsa


def test_gardul_verbatim_chiar_ar_prinde_o_reformulare():
    """ANTI-VACUU: dacă textul de căutat ar fi gol sau corpusul lipsă, testul de mai sus ar trece
    degeaba. Se probează pe o reformulare plauzibilă, care NU e în act."""
    corpus = io.open(_CORPUS, encoding="utf-8").read()
    assert len(corpus) > 10000, "corpusul normei e gol sau trunchiat — gardul de mai sus e vid"
    assert "operațiuni de casă și de bancă" not in corpus, "reformularea de probă e totuși în act — alege alta"

def test_fiecare_jurnal_emis_arata_un_fel_al_normei():
    """Legătura dintre cele două: orice JournalID pe care îl putem emite duce la un fel din
    nomenclator, nu la un text liber."""
    feluri = set(d406._FELURI.values())
    for s in list(d406._JURNALE) + [None, "necunoscut"]:
        _jid, desc, _tip = d406.jurnal_din_sursa(s)
        assert desc in feluri, "sursa %r produce o descriere din afara nomenclatorului: %r" % (s, desc)


def test_temeiul_felurilor_e_citabil_si_dateaza():
    """Nomenclatorul poartă temeiul, nu doar textul — altfel la o modificare a normei nu se poate
    face grep după locurile care o citează (rolul lui `Temei`)."""
    tm = d406.TEMEI_JURNALE
    assert tm.tip == "OMFP" and tm.nr == 2634 and tm.an == 2015
    assert "52" in str(tm.art), "temeiul nu numește punctul din anexă: %r" % tm.art
    assert tm.nivel_sursa == "MO"
    assert tm.verificat_la is not None, "temei fără dată de confirmare"

