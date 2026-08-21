# -*- coding: utf-8 -*-
"""GARDĂ: `unde` e o REFERINȚĂ citabilă mecanic, nu proză. (P8, 22.08.2026)

MĂSURAT ÎNAINTE (21.08): `unde` era text liber, în ȘAPTE forme — „rândul 7", „salariatul %s",
„partenerul %s (%s%s)", „vectorul fiscal al firmei", „codul CAEN al firmei (%s)", „facturile emise
%s", un id compus. Nimic nu-l citea mecanic, deci niciun gard nu era păcălit — dar era PRECONDIȚIA
unuia: în clipa în care ceva vrea să verifice „arată afirmația spre ceva real?", ar fi trebuit să
parseze „salariatul 53". Atunci ar fi devenit a cincea instanță de gardă-care-citește-proză.

FORMA, aleasă după `common.Temei` (modelul care există deja în aplicație): subclasă de `str`. Se
randează ca text — deci NICIUN randor nu se atinge — dar poartă `fel` (din nomenclator ÎNCHIS) și
`id`. Grepul „ce afirmații arată spre un salariat" devine posibil.

CE NU FACE, declarat: nu verifică că referentul EXISTĂ în baza de date. Aia cere o conexiune și e o
gardă separată. Aici se închide doar FELUL referentului și se face id-ul accesibil.
"""
import pytest

from core.afirmatii import FELURI, AfirmatieIncompleta, afirmatie
from core.unde import FELURI_REFERENT, Unde


def test_unde_e_un_sir_care_poarta_structura():
    """Ca `Temei`: se comportă ca șirul canonic, dar câmpurile sunt citibile."""
    u = Unde("salariat", 53, "Ionescu Maria")
    assert isinstance(u, str)
    assert u.fel == "salariat" and u.id == 53
    assert "53" in u and "Ionescu" in u, "textul nu-l ajută pe contabil să găsească omul"


def test_nomenclatorul_de_referenti_e_inchis():
    """Un fel de referent inventat pe loc face `unde` iar text liber, doar cu mai mulți pași."""
    with pytest.raises(ValueError):
        Unde("obiect_inventat_pe_loc", 1)
    assert len(FELURI_REFERENT) >= 6, "nomenclator prea mic — cele șapte forme măsurate n-au intrat"


def test_fiecare_fel_de_referent_spune_ce_e():
    for fel, spec in FELURI_REFERENT.items():
        assert fel == fel.lower() and " " not in fel
        assert spec.get("inseamna"), "felul de referent %r nu spune ce e" % fel
        assert "eticheta" in spec, "felul %r n-are cum să se randeze" % fel


def test_referentul_fara_identitate_e_refuzat():
    """„salariatul" fără id nu e o referință, e o categorie. Excepția e felul care NU are id prin
    natura lui (vectorul fiscal al firmei e unul singur)."""
    with pytest.raises(ValueError):
        Unde("salariat", None)
    u = Unde("vector_fiscal", None)
    assert u.id is None and u.fel == "vector_fiscal"


def test_unde_supravietuieste_serializarii_json():
    """Payload-ul rămâne JSON: `Unde` trebuie să treacă prin `json.dumps` ca șir, nu să crape."""
    import json
    u = Unde("rand", 7)
    assert json.loads(json.dumps({"unde": u}))["unde"] == str(u)


# ---------------------------------------------------------------- `fapt` cu domeniu alternativ

def test_faptul_accepta_domeniu_de_obiect():
    """DECIS DE COSTIN (22.08): `unde` ca ALTERNATIVĂ la an+luna, unul dintre cele două obligatoriu.

    Lipsa era a DOMENIULUI, nu a felului: un fapt despre pachetul de preluare și un fapt despre o
    lună sunt același fel de afirmație, cu domenii de forme diferite. Nomenclatorul fusese enumerat
    pe rânduri de DECLARAȚIE, unde domeniul e mereu o perioadă."""
    f = afirmatie("fapt", "preluare", "balanța de deschidere se echilibrează",
                  unde=Unde("pachet_preluare", None),
                  temei_completitudine="balanța importată de la contabilul anterior")
    assert f["fel"] == "fapt" and f["unde"].fel == "pachet_preluare"


def test_faptul_pe_perioada_merge_mai_departe():
    """Contra-direcția: forma veche NU se strică. Altfel „alternativă" ar fi însemnat „înlocuire"."""
    f = afirmatie("fapt", "d390", "nicio operațiune IC", an=2026, luna=7,
                  temei_completitudine="lună închisă")
    assert f["an"] == 2026 and f["luna"] == 7


def test_faptul_fara_niciun_domeniu_ramane_INTERZIS():
    """Miezul deciziei lui Costin: «Un fapt fără niciun domeniu rămâne interzis.» Fără asta,
    alternativa ar fi fost o portiță prin care orice fapt scapă nedatat."""
    with pytest.raises(AfirmatieIncompleta):
        afirmatie("fapt", "d390", "nicio operațiune IC",
                  temei_completitudine="lună închisă")
    with pytest.raises(AfirmatieIncompleta):
        afirmatie("fapt", "d390", "nicio operațiune IC", an=None, luna=None,
                  temei_completitudine="lună închisă")


def test_temeiul_completitudinii_ramane_obligatoriu_in_ambele_forme():
    """Un fapt negativ e o afirmație despre lume; se sprijină pe ce ne face să credem că am văzut tot.
    Alternativa de domeniu nu slăbește asta."""
    with pytest.raises(AfirmatieIncompleta):
        afirmatie("fapt", "preluare", "se echilibrează", unde=Unde("pachet_preluare", None))


def test_nomenclatorul_stie_de_alternativa():
    """DOC↔COD: `FELURI["fapt"]` nu mai poate pretinde că `an` e obligatoriu necondiționat, altfel
    cine citește nomenclatorul află altceva decât ce face codul."""
    assert "an" not in FELURI["fapt"] or "unde" in FELURI["fapt"], (
        "nomenclatorul încă declară an/luna ca singurul domeniu al faptului")
