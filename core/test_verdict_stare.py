# test_verdict_stare.py — mecanismul culorii de verdict: deriva DIN nivelul motorului, nu literal.
# Reparat 23.07: _flag("galben",...) slabea un BLOCANT de trezorerie la galben. Culoarea =
# common.stare_din_nivel(nivel), mapare UNICA. Vezi DECIZII 23.07.
from decimal import Decimal

from core.common import stare_din_nivel, pastila_firma, BLOCANT, AVERTISMENT
from core import verificatoare as vf


def _c(stare):
    return {"stare": stare}


def test_pastila_nu_depaseste_max_constatari():
    # Intrastat AVERTISMENT (galben) singur -> pastila galben, NU rosu (supra-escaladare = minciuna).
    assert pastila_firma("verde", [_c("galben")]) == "galben"
    # trezorerie BLOCANT (rosu) -> pastila rosu (nu se sub-escaladeaza la galben).
    assert pastila_firma("verde", [_c("rosu")]) == "rosu"
    # max intre mai multe: galben + rosu -> rosu.
    assert pastila_firma("verde", [_c("galben"), _c("rosu")]) == "rosu"


def test_pastila_gri_nu_escaladeaza():
    # stocuri gri ('nu pot verifica') NU face firma verde sa para problematica.
    assert pastila_firma("verde", [_c("gri")]) == "verde"
    # dar un confirmat bate baza gri (necompletat) -> galben.
    assert pastila_firma("gri", [_c("galben")]) == "galben"


def test_verificator_esuat_da_gri_cu_temei_nu_absenta():
    # Un verificator care crapa NU e "nimic de raportat" - e "nu am putut verifica" = GRI cu temei.
    import main
    contabil = []
    main._verificator_esuat(contabil, "Verificare stocuri — eșuată", "stocurile", ValueError("boom"),
                            2026, 7)
    assert len(contabil) == 1
    c = contabil[0]
    assert c["stare"] == "gri"                         # gri, nu absenta si nu verde
    assert "Nu am putut verifica" in c["mesaj"]
    assert "boom" in c["temei"] and "nu am putut verifica" in c["temei"].lower()
    # gri nu escaladeaza -> nu doboara semaforul (rezistenta pastrata)
    assert pastila_firma("verde", [c]) == "verde"


def test_construieste_contabil_verificator_care_arunca_da_gri(monkeypatch):
    # Integrare: un verificator care ARUNCA (ex. DB down) -> constatare gri in contabil, NU tacere.
    import main
    monkeypatch.setattr(main, "_verificari_contabile", lambda *a, **k: {})
    monkeypatch.setattr(main, "intrastat_praguri", lambda *a, **k:
                        {"introduceri": {"status": "sub_prag"}, "expedieri": {"status": "sub_prag"}, "nivel": None})
    def _boom(*a, **k):
        raise RuntimeError("stoc DB down")
    monkeypatch.setattr(main, "verificare_stocuri", _boom)
    contabil, vc = main._construieste_contabil("tenant_x", 1, {"uid": 0}, 2026, 7, {})
    gri = [c for c in contabil if c["stare"] == "gri" and "stocuri" in c["eticheta"].lower()]
    assert gri, "verificator picat trebuie sa dea o constatare gri, nu absenta"
    assert "stoc DB down" in gri[0]["temei"]


def test_constatare_esuata_e_gri_cu_temei():
    # documente_pozate care crapa -> gri cu temei, nu tacere (main.py _verificari_contabile).
    import main
    c = main._constatare_esuata("Documente pozate — verificare eșuată", "documentele pozate",
                                ValueError("x"), 2026, 7)
    assert c["stare"] == "gri" and "Nu am putut verifica" in c["mesaj"] and "x" in c["temei"]


def test_audit_regim_nedeterminat_e_gri_cu_straturi_sarite():
    # audit_preluare: regimul necitibil (eroare) -> gri + lista straturilor nerulate, NU report fals-curat.
    from core import audit_preluare as ap
    r = ap._audit_regim_nedeterminat(RuntimeError("DB down"))
    assert r["stare"] == "gri"
    assert "INCOMPLET" in r["constatari"][0]["mesaj"] and r["neverificat"] == 1
    assert "Straturi nerulate" in r["limita"] and "balanță" in r["limita"]


def test_header_nu_poate_fi_verde_cu_blocant_dedesubt():
    # Motivul incarnat: header "la zi" + banner verde peste un BLOCANT e cea mai grava minciuna. Un
    # sold creditor 5121 (BLOCANT) devine constatare rosie (stare_din_nivel(BLOCANT)); pastila_firma peste
    # o baza verde NU poate ramane verde - severitatea de sus nu poate fi mai buna decat ce e sub ea.
    blocant = {"stare": stare_din_nivel(BLOCANT)}   # trezorerie -> rosu
    assert pastila_firma("verde", [blocant]) != "verde"
    assert pastila_firma("verde", [blocant]) == "rosu"


def test_pastila_pastreaza_baza_daca_nimic_confirmat():
    assert pastila_firma("gri", [_c("gri")]) == "gri"      # necompletat ramane necompletat
    assert pastila_firma("verde", []) == "verde"
    assert pastila_firma("rosu", [_c("gri")]) == "rosu"    # baza rosu (restanta) nu se coboara


def test_mapare_nivel_stare():
    assert stare_din_nivel(BLOCANT) == "rosu"
    assert stare_din_nivel(AVERTISMENT) == "galben"
    assert stare_din_nivel(None) == "gri"        # nivel absent -> gri, nu inventa severitate
    assert stare_din_nivel("necunoscut") == "gri"


def test_trezorerie_negativa_e_BLOCANT_deci_rosu():
    # sold creditor pe 5121 = imposibilitate contabila certa -> BLOCANT -> rosu (NU galben).
    bal = {"5121": {"debit": Decimal(0), "credit": Decimal(100), "sold": Decimal("-100")}}
    probleme = vf.verifica_trezorerie(bal)
    assert len(probleme) == 1
    assert probleme[0]["nivel"] == BLOCANT
    assert stare_din_nivel(probleme[0]["nivel"]) == "rosu"


def test_balanta_dezechilibrata_e_BLOCANT_deci_rosu():
    bal = {"401": {"debit": Decimal(100), "credit": Decimal(0), "sold": Decimal(100)}}
    p = vf.verifica_balanta(bal)
    assert p["nivel"] == BLOCANT
    assert stare_din_nivel(p["nivel"]) == "rosu"


def test_stocuri_fara_nivel_e_gri():
    # verificare_stocuri intoarce {conturi, ok, nota} FARA nivel (cauze legitime: note ciorna
    # nevalidate) -> maparea din cheia absenta da gri. Nu se inventeaza un nivel la randare.
    rez_stocuri = {"conturi": [], "ok": False, "nota": "..."}
    assert stare_din_nivel(rez_stocuri.get("nivel")) == "gri"


def test_intrastat_depasit_e_AVERTISMENT_deci_galben():
    # depasirea pragului INS = obligatie de declarare (situatie determinata, legal dar riscanta) ->
    # motorul declara nivel=AVERTISMENT -> galben. NU gri (verificarea A determinat), NU rosu (nu blocheaza).
    from core import intrastat as _is
    from core.common import AVERTISMENT
    r = _is.analiza_flux({1: 600000, 2: 600000})   # cumulat 1.2M > prag 1M -> depasit
    assert r["status"] == "depasit" and r["nivel"] == AVERTISMENT
    assert stare_din_nivel(r["nivel"]) == "galben"


def test_intrastat_atentie_e_AVERTISMENT():
    from core import intrastat as _is
    from core.common import AVERTISMENT
    r = _is.analiza_flux({1: 850000})              # 85% din prag -> atentie
    assert r["status"] == "atentie" and r["nivel"] == AVERTISMENT


def test_intrastat_sub_prag_fara_nivel_e_gri():
    from core import intrastat as _is
    r = _is.analiza_flux({1: 100000})              # sub 80% -> sub_prag, fara nivel (nu genereaza constatare)
    assert r["status"] == "sub_prag" and r["nivel"] is None
    assert stare_din_nivel(r["nivel"]) == "gri"
