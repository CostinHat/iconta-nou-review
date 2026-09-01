# -*- coding: utf-8 -*-
"""GARD [01.09.2026]: supervizorul — cele două tării, și confirmarea care rămâne scrisă.

**CE PĂZEȘTE, în ordinea în care s-ar putea strica:**

  1. **Tăria nu se deduce.** Costin o dă, pe tip. Un tip fără tărie atribuită **nu are niciun
     efect** — nu cade pe `EURISTICA` (ar tăcea o constatare certă) și nici pe `CERTA` (ar cere
     confirmări pe care nimeni nu le-a decis). Un tip **necunoscut** ridică.
  2. **Mecanismul funcționează deja**, probat pe un tip **sintetic** cu tărie atribuită — altfel
     gardul ar fi verde fiindcă azi nimic nu e confirmat, iar în ziua în care Costin atribuie prima
     tărie nimic n-ar fi fost verificat.
  3. **Confirmarea acoperă CIFRELE, nu tipul.** O reformulare nu invalidează o confirmare; o cifră
     schimbată o invalidează. Fără asta, „confirmare explicită" ar fi devenit o bifă permanentă.
  4. **Supervizorul nu blochează nimic**, niciodată — nici pe certe.

**MUTAȚIA pe care o cere fiecare:** dacă `cere_confirmare` ar întoarce `True` pe tăria neatribuită,
(1) cade. Dacă amprenta ar include mesajul, (3a) cade; dacă ar ignora cifrele, (3b) cade. Dacă
`_stampileaza` din `control_incrucisat` ar uita o cale de retur, (5) cade — iar supervizorul ar sări
constatarea **tăcut**, care e chiar felul de tăcere care arată ca un răspuns.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import control_incrucisat as _ci  # noqa: E402
from core import supervizor as S  # noqa: E402

#: Constatare-etalon: cifrele care intră în amprentă, fără proză.
_C = {"tip_constatare": "D390_VS_D300_IC", "eticheta": "IC livrări", "stare": "rosu",
      "declarat_d390": 1000, "declarat_d300": 0, "diferenta": 1000}


# ── 1. TĂRIA NU SE DEDUCE ──────────────────────────────────────────────────────────────────────

def test_un_tip_NECUNOSCUT_ridica_nu_cade_pe_implicit():
    """MIEZUL primei reguli. O constatare fără tărie declarată n-are voie să circule: cine o citește
    n-ar putea ști dacă cere confirmare sau doar semnalează."""
    with pytest.raises(S.TipNecunoscut):
        S.tarie("TIP_CARE_NU_EXISTA")
    with pytest.raises(S.TipNecunoscut):
        S.amprenta({"tip_constatare": "TIP_CARE_NU_EXISTA"})
    with pytest.raises(S.TipNecunoscut):
        S.amprenta({"eticheta": "fără tip"})


def test_un_tip_NEATRIBUIT_nu_cere_confirmare_si_nu_tace():
    """Cele două direcții ale aceleiași reguli: un tip pe care Costin nu l-a împărțit încă **se
    vede** (tăria e `None`, nu absentă), dar **nu produce niciun efect**. Propunerea mea din
    `motiv_propunere` n-are voie să devină regulă prin trecerea timpului."""
    neatribuite = S.tipuri_neatribuite()
    for tip in neatribuite:
        assert S.tarie(tip) is None
        assert S.cere_confirmare(tip) is False, (
            "tipul %r n-are tărie atribuită, dar cere confirmare — un implicit s-a strecurat" % tip)
        assert S.TIPURI[tip].get("propus") in S.TARII, (
            "tipul %r n-are nici măcar o propunere, deci Costin n-are ce confirma" % tip)


def test_o_tarie_NEVALIDA_nu_trece():
    """Nomenclatorul e ÎNCHIS: o a treia tărie ar fi o decizie de arhitectură, nu o valoare nouă."""
    tip = next(iter(S.TIPURI))
    vechi = S.TIPURI[tip].get("tarie")
    try:
        S.TIPURI[tip]["tarie"] = "APROAPE_CERTA"
        with pytest.raises(ValueError):
            S.tarie(tip)
    finally:
        S.TIPURI[tip]["tarie"] = vechi


# ── 2. MECANISMUL, probat pe un tip SINTETIC ───────────────────────────────────────────────────

def _cu_tip_sintetic(tarie, confirmat):
    """Înregistrează un tip de probă. Fără el, tot fișierul ar fi verde pe o mulțime în care nimic
    nu e încă atribuit — iar în ziua atribuirii nimic n-ar fi fost verificat (METODA §29)."""
    S.TIPURI["_PROBA_SINTETICA"] = {
        "axa": "ORIZONTALA", "ce": "probă", "identitate": "probă",
        "sursa_stanga": "probă", "sursa_dreapta": "probă",
        "tarie": tarie, "confirmat": confirmat, "propus": S.CERTA, "motiv_propunere": "probă",
    }
    return "_PROBA_SINTETICA"


def test_o_CERTA_CONFIRMATA_chiar_cere_confirmare():
    """Direcția care contează: mecanismul nu e mort, doar neatribuit."""
    tip = _cu_tip_sintetic(S.CERTA, True)
    try:
        assert S.tarie(tip) == S.CERTA
        assert S.cere_confirmare(tip) is True
    finally:
        del S.TIPURI[tip]


def test_o_EURISTICA_nu_cere_NICIODATA_confirmare():
    """*„semnalează, nu opresc niciodată"* — nici confirmată, nici neconfirmată."""
    for confirmat in (True, False):
        tip = _cu_tip_sintetic(S.EURISTICA, confirmat)
        try:
            assert S.cere_confirmare(tip) is False
        finally:
            del S.TIPURI[tip]


def test_o_CERTA_NECONFIRMATA_nu_are_efect():
    """O tărie propusă dar neconfirmată e o propunere, nu o regulă."""
    tip = _cu_tip_sintetic(S.CERTA, False)
    try:
        assert S.cere_confirmare(tip) is False
    finally:
        del S.TIPURI[tip]


# ── 3. AMPRENTA: pe cifre, nu pe proză ─────────────────────────────────────────────────────────

def test_amprenta_NU_se_schimba_la_rescrierea_prozei():
    a = S.amprenta(_C)
    for camp, val in (("mesaj", "cu totul altă frază"), ("temei", "alt temei"),
                      ("remediu", {"fel": "sugerat"})):
        assert S.amprenta(dict(_C, **{camp: val})) == a, (
            "amprenta s-a mutat la schimbarea lui %r — o reformulare ar invalida o confirmare bună"
            % camp)


def test_amprenta_SE_SCHIMBA_la_orice_cifra():
    """Cealaltă direcție, și e cea care apără sensul confirmării."""
    a = S.amprenta(_C)
    for camp in ("declarat_d390", "declarat_d300", "diferenta"):
        alt = dict(_C)
        alt[camp] = _C[camp] + 1
        assert S.amprenta(alt) != a, (
            "cifra %r s-a schimbat, amprenta NU — o confirmare veche ar acoperi tăcut o divergență "
            "nouă, iar «confirmare explicită» ar deveni o bifă permanentă" % camp)
    assert S.amprenta(dict(_C, stare="gri")) != a


# ── 4. SUPERVIZORUL NU BLOCHEAZĂ ───────────────────────────────────────────────────────────────

def test_nicio_cale_nu_intoarce_un_blocaj():
    """Contractul, scris în `PLAN_LUCRU`: produce constatări, nu blocaje. Nu există în tot modulul
    vreo valoare care să însemne «oprește-te»; certele cer o **confirmare**, pe care poarta de
    depunere o citește — supervizorul nu e a doua poartă."""
    import inspect
    sursa = inspect.getsource(S)
    for cuv in ("raise HTTPException", "blocheaza", "abort("):
        assert cuv not in sursa, "supervizorul conține %r — a devenit poartă" % cuv


def test_confirmarea_cere_MOTIV_scris():
    """*«iar confirmarea rămâne scrisă»* — o bifă fără motiv nu se poate citi peste șase luni."""
    class _ConnFals:
        def cursor(self):
            raise AssertionError("nu trebuia să ajungă la baza de date: motivul lipsește")
    for motiv in (None, "", "   "):
        with pytest.raises(ValueError):
            S.scrie_confirmare(_ConnFals(), 1, 2026, 9, dict(_C, amprenta="x"), "cine", 1, motiv)


# ── 5. ETICHETA DE TIP, pe TOATE căile de retur ────────────────────────────────────────────────

def test_perechea_orizontala_e_stampilata_pe_TOATE_caile():
    """Dacă o cale de retur pierde eticheta, supervizorul sare constatarea **tăcut**. Se probează
    toate cele patru ieșiri ale comparației, nu una."""
    cazuri = [
        ("fără D300 depus", _ci.compara_d390_vs_d300({"L": 0, "A": 0}, False, None)),
        ("depus fără rânduri", _ci.compara_d390_vs_d300({"L": 0, "A": 0}, True, None)),
        ("divergență", _ci.compara_d390_vs_d300({"L": 1000, "A": 0}, True, {"R": {}})),
        # AMBELE ZERO e TĂCUT prin construcție (fără subiect, nu verde fals) — proba
        # cere cifre egale și NENULE, altfel n-ar exercita calea verde deloc.
        ("coincid", _ci.compara_d390_vs_d300({"L": 1000, "A": 0}, True, {"R": {"R1_1": 1000}})),
    ]
    for eticheta, cs in cazuri:
        assert cs, "[anti-vacuu] cazul %r n-a produs nicio constatare" % eticheta
        fara = [c for c in cs if not c.get("tip_constatare")]
        assert not fara, "cazul %r a produs constatări fără tip: %d" % (eticheta, len(fara))
        assert all(c["tip_constatare"] in S.TIPURI for c in cs), (
            "cazul %r poartă un tip neînregistrat în `TIPURI`" % eticheta)


def test_ANTI_VACUU_exista_cel_putin_o_pereche_ORIZONTALA():
    orizontale = [t for t, v in S.TIPURI.items() if v.get("axa") == "ORIZONTALA"]
    assert orizontale, ("[anti-vacuu] niciun tip orizontal — supervizorul n-ar avea obiect, "
                        "fiindcă gaura măsurată e chiar axa orizontală")


def test_fiecare_tip_isi_declara_cele_doua_surse():
    """O pereche orizontală care nu spune ce compară cu ce nu se poate citi de nimeni."""
    rele = [t for t, v in S.TIPURI.items()
            if not (v.get("sursa_stanga") and v.get("sursa_dreapta") and v.get("identitate"))]
    assert not rele, "tipuri fără cele două surse sau fără identitatea verificată: %s" % rele
