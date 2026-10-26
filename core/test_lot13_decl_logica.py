# -*- coding: utf-8 -*-
"""[lotul 13, subagentul DECL] Logica numerelor 660, 650, 595, 635, 637, 653, 539, 538/591, 658 și C19, probată fără browser (e2e-ul lor e
în `frontend_test/e2e/e2e_lot13_decl.py`). Fiecare test își citează temeiul pe linie; textul legii e căutat în corpus (`anaf_surse/`),
nu presupus."""
import html
import re

import pytest

from core import declaratii_api as DA, declaratii_componente as DC, rectificativa as R

_CF = "anaf_surse/cod_fiscal_227_2015_consolidat.html"


def _text(cale):
    t = open(cale, encoding="utf-8", errors="ignore").read()
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


@pytest.fixture(scope="module")
def cf():
    return _text(_CF)


# ── 660: formularele înlocuite de Declarația unică ──────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("tip", sorted(DA.FORMULARE_INLOCUITE))
def test_660_formularul_inlocuit_nu_se_ofera_si_textul_legii_e_in_corpus(tip, cf):
    den, act, text = DA.FORMULARE_INLOCUITE[tip]
    assert tip not in DA.DECLARATII and tip not in DA.tipuri()      # nu se oferă la nicio firmă (comanda 13.1, 660)
    assert text in cf, "textul citat pentru %s nu e în Codul fiscal din corpus" % tip   # CF art.122 / 130 / 107 / 125 / 151 / 120
    er = DA.valideaza_cerere(tip, {"an": 2025, "manual": {"x": 1}})
    assert len(er) == 1 and "nu se mai depune" in er[0] and act in er[0]


def test_660_cele_sase_formulare_numite_in_comanda_sunt_toate_refuzate():
    """Lista din comanda 13.1 (660), pe nume: fiecare e refuzată la cerere, nu doar „ce se află în dicționar”."""
    numite = {"d200", "d201", "d220", "d221", "d223", "d600"}
    assert set(DA.FORMULARE_INLOCUITE) == numite
    for tip in sorted(numite):
        er = DA.valideaza_cerere(tip, {"an": 2025, "manual": {"x": 1}})
        assert len(er) == 1 and "nu se mai depune" in er[0], (tip, er)


def test_660_generarea_unui_formular_inlocuit_e_refuzata_inainte_de_firma():
    """Dispecerul refuză tipul înainte să citească firma (conexiunea nu e atinsă: `conn=None`)."""
    with pytest.raises(ValueError, match="nu se mai depune"):
        DA.genereaza(None, "nicio_schema", "d221", {"an": 2025, "manual": {}})


# ── 650 / 595 / 635: regimul de TVA ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_650_595_635_neaplicabile_dupa_regimul_de_tva(cf):
    # CF art.324 alin.(10): D311 numai după anularea codului; plătitorul n-o datorează
    assert "trebuie să depună o declarație privind taxa colectată care trebuie plătită" in cf
    assert set(DA.neaplicabile_regim({"platitor_tva": True})) == {"d311"}
    # neplătitor neînregistrat art.317: fără D318 (HG 1/2016 pct.73 alin.(15) lit.c) și fără D398 (CF art.315 alin.(4))
    assert set(DA.neaplicabile_regim({"platitor_tva": False, "inreg_art317": False})) == {"d318", "d398"}
    # neplătitor înregistrat art.317: are cod de TVA (art.315 alin.(4)), deci D398 rămâne — dar cere înregistrarea OSS (595)
    assert set(DA.neaplicabile_regim({"platitor_tva": False, "inreg_art317": True})) == {"d318"}
    assert DA.neaplicabile_regim({}) == {}                                 # vector necompletat: nimic blocat (un gol nu e un răspuns)
    assert "codul de înregistrare utilizat de persoana impozabilă este cel care i-a fost atribuit conform art. 316 sau art. 317" in cf


def test_595_d398_fara_inregistrarea_oss_nu_se_genereaza(cf):
    """CF art.315 alin.(3): „persoana impozabilă respectivă trebuie să depună în format electronic o declarație de începere a activității
    sale supuse regimului special”."""
    assert "trebuie să depună în format electronic o declarație de începere a activității sale supuse regimului special" in cf
    m = {"name": "F", "vat_id_no": "RO1", "ms": [{"mscon_state": "DE"}]}
    # [decizia Costin 26.10.2026 „6 da”] înregistrarea OSS nu mai e în formular: o dă Date firmă (`firma_profil.inregistrat_oss`), verificată
    # la generare (`DA._d398`); poarta cererii verifică numai forma, iar refuzul (nedeclarat / „Nu” / „Da”) e al `d398.refuz_oss`
    # (cu baza: `core/test_lot13_oss_date_firma.py`)
    from core import d398
    assert DA.valideaza_cerere("d398", {"an": 2026, "trim": 3, "manual": m}) == []
    assert "nu ai răspuns" in d398.refuz_oss(None) and "art.315 alin.(3)" in d398.refuz_oss(None)
    assert "nu e înregistrată" in d398.refuz_oss(False) and "art.315 alin.(3)" in d398.refuz_oss(False)
    assert d398.refuz_oss(True) is None


def test_594_d398_mesajele_fara_numele_atributelor_xml():
    from core import d398
    er = d398.erori_generare({}, {"moes_voes_imp": 1, "ms": [{"mscon_state": "DE", "supplies": [{"trade_type": 2, "supply_type": 1}]}]})
    text = " ".join(er)
    for intern in ("msest", "msid", "e_int", "moes_voes_imp", "vat_id_no", "supply_type", "trade_type", "MS[", "SUPPLY"):
        assert intern not in text, (intern, text)


def test_637_d318_refuzul_numeste_numai_ce_lipseste():
    er = DA.valideaza_cerere("d318", {"an": 2026, "manual": {"cui": "404000013", "iban": "RO49AAAA1B31007593840003"}})
    assert er == ["D318 nu are ce genera: completează cel puțin o factură de achiziție sau de import din statul de rambursare."], er


# ── 653: statul de rezidență D207 ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_653_d207_statul_din_lista_validatorului():
    from core import d207
    assert "GR" in d207.STAT_R and "EL" not in d207.STAT_R and "IN" in d207.STAT_R and len(d207.STAT_R) == 249
    b = {"tip_venit": "02", "den": "X", "cif_strain": "1", "act_n": "1"}
    assert any("nu e în lista ANAF" in e for e in d207.erori_generare({}, {"beneficiari": [dict(b, stat="EL")]}))
    assert not any("stat" in e.lower() for e in d207.erori_generare({}, {"beneficiari": [dict(b, stat="GR")]}))


# ── 539: codul de TVA al furnizorului D301, fără prefix ──────────────────────────────────────────────────────────────────────────────
def test_539_codul_de_tva_se_tine_fara_prefixul_tarii():
    from core.d301_operatiuni_api import cod_tva_fara_prefix as f
    assert f("IE", "IE6388047V") == "6388047V" and f("IE", "6388047V") == "6388047V"   # F3, IE-100: „IEIE6388047V” pe ecran
    assert f("EL", "GR123456789") == "123456789" and f("DE", "de 811 569 869") == "811569869" and f("AT", "U12345678") == "U12345678"


def test_539_migrarea_datelor_existente():
    """Schema de probă în tranzacție anulată: rândul cu prefix se corectează, cel fără rămâne; a doua rulare nu mai găsește nimic."""
    from core import db, migrare_d301_cod_tva_fara_prefix as M
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("CREATE SCHEMA tenant_99539")
                cur.execute("CREATE TABLE tenant_99539.d301_operatiuni (id serial PRIMARY KEY, partener_tara text, partener_cod text)")
                cur.execute("INSERT INTO tenant_99539.d301_operatiuni (partener_tara, partener_cod) VALUES ('IE', 'IE6388047V'), ('DE', '811569869')")
            assert M.aplica(c, "tenant_99539") == 1 and M.verifica(c, "tenant_99539")
            with c.cursor() as cur:
                cur.execute("SELECT partener_cod FROM tenant_99539.d301_operatiuni ORDER BY id")
                assert [r[0] for r in cur.fetchall()] == ["6388047V", "811569869"]
            assert M.aplica(c, "tenant_99539") == 0
        finally:
            c.rollback()


# ── 538 / 591: datoratele din operațiile înregistrate ───────────────────────────────────────────────────────────────────────────────
def test_538_d301_din_operatii_intra_in_termene():
    """CF art.324 alin.(1) (D301 „până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea”): la F3 (AIC
    IE-100 pe 09/2026) D301 09/2026 trebuie să apară în lista „Datorate” / Termene, cu termenul ei."""
    import datetime
    from core import termene_api
    azi = datetime.date(2026, 10, 25)
    vector = {"regim_fiscal": "micro", "platitor_tva": False, "operatiuni_ic": True, "tip_firma": "srl", "inreg_art317": True}
    d301 = {"tip": "d301", "an": 2026, "luna": 9, "perioada": "09/2026", "termen": "2026-10-26", "fapt": "operațiuni intracomunitare"}
    vechi = {"tip": "d301", "an": 2026, "luna": 8, "perioada": "08/2026", "termen": "2026-09-25", "fapt": "x"}
    fara = termene_api.termene_firma(vector, False, set(), azi, d390_luni_neplatitor=lambda a: {9})
    cu = termene_api.termene_firma(vector, False, set(), azi, d390_luni_neplatitor=lambda a: {9},
                                   declaratii_fapt=lambda jos, zile: {"datorate": [d301, vechi]})
    assert not [x for x in fara if x["tip"] == "d301"]
    assert [x for x in cu if x["tip"] == "d301"] == [d301]                    # termenul trecut (08/2026) nu e „înainte”
    depusa = termene_api.termene_firma(vector, False, {("d301", 2026, 9)}, azi, declaratii_fapt=lambda jos, zile: {"datorate": [d301]})
    assert not [x for x in depusa if x["tip"] == "d301"]                      # 591: depusă -> nu mai e datorată


def test_592_d390_la_neplatitorul_art317_numai_pe_lunile_cu_operatiuni():
    """CF art.325 alin.(2): „Declarația se întocmește pentru fiecare lună calendaristică în care ia naștere exigibilitatea taxei pentru
    operațiunile prevăzute la alin. (1)” — F3: numai 09/2026, nu 10 și 11 (reparat de C162 în lotul 12; aici gardat pe drumul listei)."""
    import datetime
    from core import termene_api
    vector = {"regim_fiscal": "micro", "platitor_tva": False, "operatiuni_ic": True, "tip_firma": "srl", "inreg_art317": True}
    t = termene_api.termene_firma(vector, False, set(), datetime.date(2026, 10, 25), d390_fapt=lambda a, l: None,
                                  d390_luni_neplatitor=lambda a: {6, 9})
    assert [(x["an"], x["luna"]) for x in t if x["tip"] == "d390"] == [(2026, 9)]


# ── 658: compoziția declarațiilor din formular ─────────────────────────────────────────────────────────────────────────────────────
def test_658_declaratiile_din_formular_nu_mai_spun_harta_de_componente():
    assert DC.componente("d207", object())["acoperire"] == "formular" and DC.componente("d318", object())["acoperire"] == "formular"
    assert set(DA.DECLARATII) <= set(DC.COMPONENTE) | DC.DIN_FORMULAR      # fiecare tip: componente sau formular
    js = open("static/js/ecrane/declaratii.js", encoding="utf-8").read()
    assert "harta de componente" not in js and 'c.acoperire === "formular"' in js


# ── C19: diferențele dinaintea rectificativei, și la D112 ───────────────────────────────────────────────────────────────────────────
_D112 = ('<declaratieUnica xmlns="mfp:anaf:dgti:declaratie_unica:declaratie:v11" luna_r="9" an_r="2026" d_rec="0">'
         '<angajator cif="1"><angajatorA A_codOblig="602" A_datorat="%d"/></angajator>'
         '<asigurat cnpAsig="1800101221144" numeAsig="POPA" prenAsig="ION"><asiguratB1 B1_5="%d"/></asigurat></declaratieUnica>')


def test_c19_d112_diferentele_pe_rubrici():
    """OPANAF 605/2026 anexa nr.2 pct.2.4: rectificativa se completează integral — contabilul vede, rubrică cu rubrică, ce se schimbă."""
    assert "d112" in R.CU_DIFERENTE
    dif = R.diferente_xml(_D112 % (100, 4050), _D112 % (120, 4050))
    assert [(d["sectiune"], d["rand"], d["camp"], d["depus"], d["nou"]) for d in dif] == [
        ("Obligații de plată (secțiunea A)", "obligația cu codul 602", "A_datorat", "100", "120")]
    assert R.diferente_xml(_D112 % (100, 4050), _D112 % (100, 4050)) == []
    assert R.diferente_xml(None, _D112 % (100, 4050)) is None                 # XML-ul depus nepăstrat: nu se poate compara
    tot = R.diferente_xml(None, _D112 % (100, 4050), lipsa_depus=R.NECUNOSCUT)
    assert tot and all(d["depus"] == R.NECUNOSCUT for d in tot)


def test_c19_poarta_e_comuna_si_cheama_diferentele_d112(monkeypatch):
    """Poarta comună (`poarta_diferente`): fără confirmare -> refuz cu diferențele; cu confirmarea amprentei văzute -> trece."""
    from core import coada_api
    monkeypatch.setattr(R, "depuneri", lambda cur, schema, tip, an, luna=None, trim=None: [
        {"nr_depunere": 1, "data_depunere": None, "sursa": "contabil_anterior", "xml": _D112 % (100, 4050), "recipisa": None}])

    class _C:
        def cursor(self):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    nou = _D112 % (120, 4050)
    with pytest.raises(R.RefuzRectificativa) as e:
        R.poarta_diferente(_C(), "s", "d112", {"an": 2026, "luna": 9}, nou, None)
    d = e.value.detaliu()
    assert d["cod"] == "RECTIFICATIVA_DE_CONFIRMAT" and d["diferente"] and "OPANAF 605/2026" in d["mesaj"]
    corp = {"an": 2026, "luna": 9, "date_extra": {"rectificativa_confirmata": coada_api.amprenta_xml(nou)}}
    assert R.poarta_diferente(_C(), "s", "d112", corp, nou, None) is None
