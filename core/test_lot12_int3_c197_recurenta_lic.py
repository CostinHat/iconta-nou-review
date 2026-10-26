# -*- coding: utf-8 -*-
"""C197 (lotul 12, găsită de Code la fx3) — un șablon recurent cu o linie „livrare intracomunitară” (posibilă de la 12.3 pct.9: cota și
categoria pe linia șablonului) se emitea din cron fără întrebarea / avertismentul C84: `emite_factura` punea avertismentul numai când
răspunsul era „Nu” (`dovada_transport=False`), iar cronul nu întreabă. Decizia Costin 12.3 pct.7 (verbatim): „C84: livrarea
intracomunitară de bunuri fără dovada transportului primește avertisment la emitere, nu refuz.” Acum: (1) emiterea pe un drum care nu
întreabă poartă avertismentul `intracomunitar.AVERTISMENT_LIC_NEINTREBAT` (nu „nu ai dovada”, pe care aplicația n-o știe); (2) cronul
duce orice avertisment al emiterii la contabil, ca refuzul C109 (clopoțel + email), cu tipul lui, `factura_recurenta_avertisment` — tip
separat, fiindcă eticheta refuzului („nu s-a emis”) ar fi falsă pe email pentru o factură emisă.

Temei (anaf_surse/cod_fiscal_227_2015_consolidat.txt, citit la sursă): CF art.294 alin.(2) lit.a — „Sunt, de asemenea, scutite de taxă
următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă […] în alt stat membru”; CF art.294 alin.(3) — „Prin ordin
al ministrului finanțelor publice se stabilesc, acolo unde este cazul, documentele necesare pentru a justifica scutirea”.

Mediul (schemă efemeră, firmă / cabinet / utilizator sintetice, totul anulat, perioade 2099) e cel din `core/test_lot12_fe3_recurente.py`.
Clientul din DE: DE811907980 (cel al probelor C78 / C110 / C154 / C160)."""
import re

from core.test_lot12_fe3_recurente import AZI, COD_DE, LINIE, SCH, _adauga, _notificari, _stare, mediu  # noqa: F401 — `mediu` e fixture

LIC = {"descriere": "Piese de schimb livrate in Germania", "cantitate": 1, "um": "buc", "pret_unitar": 1000, "cota_tva": 0, "categorie_tva": "livrare_ic",
       "cont_venit": "707"}


def test_def_c197_recurenta_cu_livrare_ic_se_emite_si_avertismentul_ajunge_in_clopotel_si_pe_email(mediu):
    """Șablonul cu livrarea intracomunitară către clientul din DE: cronul emite factura (avertisment, nu refuz — 12.3 pct.7), iar
    avertismentul ajunge în clopoțelul administratorului (firma, clientul, numărul, textul C84 pentru drumul fără întrebare) și pe email
    (eticheta tipului, fără conținut fiscal). Un șablon obișnuit (21%) nu dă nicio notificare.
    MUTAȚII: în cron, ramura `if _avert:` -> `if False:` -> nicio notificare -> ROȘU; în `emite_factura`, `dovada_transport is not True` ->
    `dovada_transport is False` -> factura fără avertisment -> ROȘU."""
    from core import facturi_recurente as fr, intracomunitar as ic, notificari
    r = _adauga(mediu, tert_nume="Kunde GmbH", tert_cui=COD_DE, tert_tara="DE", linii=[dict(LIC)])
    assert set(r) == {"id"}, r                         # salvarea nu e refuzată: avertisment, nu refuz
    sid = r["id"]
    e = fr.emite_scadente(SCH, AZI)
    emisa = [x for x in e if x.get("sablon") == sid]
    assert len(emisa) == 1 and emisa[0].get("factura") and emisa[0]["avertismente"] == [ic.AVERTISMENT_LIC_NEINTREBAT], e
    assert _stare(mediu, sid)[0] == AZI                # emisă: luna nu se mai încearcă
    n = _notificari(mediu)
    assert n == [(fr.TIP_AVERTISMENT, fr.text_avertisment("Firma FE3 SRL", {"tert_nume": "Kunde GmbH"}, emisa[0]["factura"],
                                                          [ic.AVERTISMENT_LIC_NEINTREBAT], AZI), True)], n
    assert n[0][1].startswith("Firma FE3 SRL: factura recurentă pentru Kunde GmbH s-a emis (%s, 10.03.2099), cu 1 avertisment: Factura "
                              "s-a emis automat cu scutirea livrării intracomunitare" % emisa[0]["factura"]), n[0][1]
    # CF art.294 alin.(3): documentele care justifică scutirea — textul le cere, fără să afirme că lipsesc
    assert n[0][1].endswith(ic.AVERTISMENT_LIC_NEINTREBAT) and "nu ai încă dovada" not in n[0][1], n[0][1]
    assert re.search(r"art\.294 alin\.\(3\) din Codul fiscal\): verifică-le și păstrează-le la dosar", ic.AVERTISMENT_LIC_NEINTREBAT)
    assert notificari.livreaza_in_asteptare() == {"email": 1}
    assert [(a, s) for a, s, _h in mediu["emailuri"]] == [("ztest_fe3_admin@invalid", "iConta.eu — o factură recurentă s-a emis cu un avertisment")]
    assert "scutirea" not in mediu["emailuri"][0][2]   # eticheta, nu conținutul fiscal
    # șablonul obișnuit, fără avertisment: nicio notificare în plus
    sid2 = _adauga(mediu, linii=[dict(LINIE)])["id"]
    e2 = fr.emite_scadente(SCH, AZI)
    assert [(x.get("avertismente"), bool(x.get("factura"))) for x in e2 if x.get("sablon") == sid2] == [(None, True)], e2
    assert len(_notificari(mediu)) == 1


def test_c197_avertismentul_c84_pe_fiecare_raspuns(mediu):
    """`emite_factura` pe livrarea intracomunitară: „Da” (`dovada_transport=True`) -> fără avertisment; „Nu” -> `AVERTISMENT_LIC_FARA_DOVADA`;
    neîntrebat (`intreaba_dovada=False`, fără răspuns — cronul) -> `AVERTISMENT_LIC_NEINTREBAT`; întrebat fără răspuns -> întrebarea.
    MUTAȚIE: `_ic.AVERTISMENT_LIC_FARA_DOVADA if dovada_transport is False else _ic.AVERTISMENT_LIC_NEINTREBAT` -> numai primul -> ROȘU."""
    import pytest
    from core import facturi_api, intracomunitar as ic
    from core.test_lot12_fe3_recurente import _Prox
    c = _Prox(mediu["c"])
    with mediu["c"].cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)

    def emite(**k):
        r = facturi_api.emite_factura(c, [dict(LIC)], tert_nume="Kunde GmbH", tert_cui=COD_DE, tert_tara="DE",
                                      data_emitere=AZI.isoformat(), platitor_tva=True, tert_platitor_tva=True, **k)
        return [a for a in r.get("avertismente") or [] if a in (ic.AVERTISMENT_LIC_FARA_DOVADA, ic.AVERTISMENT_LIC_NEINTREBAT)]
    assert emite(intreaba_dovada=True, dovada_transport=True) == []
    assert emite(intreaba_dovada=True, dovada_transport=False) == [ic.AVERTISMENT_LIC_FARA_DOVADA]
    assert emite() == [ic.AVERTISMENT_LIC_NEINTREBAT]
    with pytest.raises(ValueError) as ei:
        emite(intreaba_dovada=True)
    assert ei.value.cod == facturi_api.COD_INTREABA_DOVADA


def test_c197_tipul_avertismentului_e_al_celor_care_pregatesc_si_bifat_din_oficiu():
    """Grupa „Facturi și SPV”, celor care pregătesc (ca refuzul C109), bifat din oficiu; eticheta spune că factura S-A emis."""
    from core import facturi_recurente as fr, notificari as N
    t = N.TIPURI[fr.TIP_AVERTISMENT]
    assert t["grup"] == "Facturi și SPV" and t["cine"] == "pregatire" and N.implicit(fr.TIP_AVERTISMENT)
    assert t["eticheta"] == "o factură recurentă s-a emis cu un avertisment" and "nu s-a emis" not in t["eticheta"]
    vede = lambda a: fr.TIP_AVERTISMENT in [x["cheie"] for g in N.lista_pentru(a, None) for x in g["tipuri"]]   # noqa: E731
    assert vede({"rol": "admin_firma"}) and vede({"rol": "angajat", "poate_pregati": True})
    assert not vede({"rol": "angajat", "poate_valida": True}) and not vede({"rol": "client"})
