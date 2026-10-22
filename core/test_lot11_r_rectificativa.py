# -*- coding: utf-8 -*-
"""[lotul 11, deficiența C77] A doua depunere pe aceeași perioadă pleca la ANAF marcată „inițială”.

Generatoarele scriau `d_rec="0"` constant (D101, D112, D205, D301, D390) sau numai din bifa formularului (D216, D395, D397, …), iar
coada dă celei de-a doua depuneri `nr_depunere` = MAX + 1. Acum `core.rectificativa` decide, din `public.declaratii_depuse` (oricare
sursă: iconta / extern / contabil_anterior / istoric), iar ecranul spune „Rectificativă la declarația depusă …”.

Temeiul general — CPF art.105 alin.(3): „Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații
rectificative.” Forma fiecărui formular: `core.rectificativa.TEMEI_PE_TIP` (textul citat).

Datele: o firmă SINTETICĂ (schema `ztest_lot11_r` din `tenant_template.sql` + un rând nou în `public.tenants`, deci un tenant_id
sintetic), totul într-o tranzacție ANULATĂ la final — depunerile scrise în tabela partajată `public.declaratii_depuse` nu pot ciocni o
depunere reală (CLAUDE.md, „Testele nu presupun gol un interval”)."""
import importlib
import os
import re

import pytest

from core import db as _db, duk, rectificativa as R, tenant_provisioning as _tp
from core.common import Perioada
from core.erori import RefuzGenerare

_SCHEMA = "ztest_lot11_r"
_CNP = "1900101410011"      # CNP rezident, cifra de control verificată (cnp_valid din CLAUDE.md) — folosit și în test_d205_imp_manual
_CNP2 = "2900101410011"     # idem
_CUI = "14399840"           # CUI cu cifra de control verificată (cui_valid din CLAUDE.md)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DBOK = _db_ok()
nevoie_db = pytest.mark.skipif(not _DBOK, reason="DB indisponibil")


def _duk_sau_skip(tip):
    if not duk.poate_valida(tip):
        pytest.skip("DUK %s indisponibil" % tip)


def _valid(xml, tip, an, luna=None):
    v = duk.valideaza(xml, tip, an=an, luna=luna, timeout=180)
    if v.get("stare") == "gri":
        pytest.skip("validator %s indisponibil: %s" % (tip, v.get("temei")))
    assert v.get("stare") == "valid", "%s pe DUK nu e valid: %s" % (tip, (v.get("erori") or "")[:600])


def _drec(xml):
    return R.marcaj_xml("x", xml)


def _atribut(xml, nume):
    """Valorile atributului `nume` pe elementele XML-ului, din arbore (xml.etree) — nu „șirul apare undeva” (core/test_garzi_pe_text.py).
    O cale independentă de `R.marcaj_xml` (care e chiar codul aplicației)."""
    import xml.etree.ElementTree as _ET
    rad = _ET.fromstring(re.sub(r"^\s*<\?xml[^>]*\?>", "", xml))
    return [e.get(nume) for e in rad.iter() if e.get(nume) is not None]


def _atribute_respinse(erori):
    """Atributele numite de DUK în liniile „eroare atribut: <atribut>: …” / „attribute error: <atribut>: …” ale verdictului."""
    out = set()
    for linie in (erori or "").splitlines():
        parti = [x.strip() for x in linie.split(":")]
        if len(parti) >= 3 and parti[0] in ("eroare atribut", "attribute error"):
            out.add(parti[1])
    return out


def _drec_radacina(xml):
    """`d_rec` scris pe elementul rădăcină al declarației (acolo îl cer structurile ANAF)."""
    import xml.etree.ElementTree as _ET
    return _ET.fromstring(re.sub(r"^\s*<\?xml[^>]*\?>", "", xml)).get("d_rec")


@pytest.fixture
def firma():
    """Firmă sintetică: schema din template, profilul complet, un rând în `public.tenants` (tenant_id sintetic). ROLLBACK la final."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)   # pe tranzacție: nu rămâne pe conexiunea din pool (core/test_lot10_search_path_pool.py)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA C77 SRL',%s,'Str 1','Buc','B','6202',"
                            "'BCR','RO49RNCB0000000000000001','profit',true,'L','Pop','Ion','administrator')", (_CUI,))
                cur.execute("INSERT INTO public.tenants (schema_name, nume, cui) VALUES (%s, 'PROBA C77 SRL', %s) RETURNING id",
                            (_SCHEMA, _CUI))
                tid = cur.fetchone()[0]
            yield {"conn": conn, "schema": _SCHEMA, "tid": tid}
        finally:
            conn.rollback()


# fixtura-sintetica-ok: tenant_id sintetic (rândul nou din public.tenants al fixturii `firma`), totul în ROLLBACK
def _depune(f, tip, an, luna, sursa="iconta", xml=None, recipisa=None, data="2026-03-10 10:00+02"):
    with f["conn"].cursor() as cur:
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, sursa, recipisa, data_depunere, nr_depunere) "
                    "SELECT %s,%s,%s,%s,%s,%s,%s,%s, COALESCE(MAX(nr_depunere),0)+1 FROM public.declaratii_depuse "
                    "WHERE tenant_id=%s AND an=%s AND luna=%s AND tip=%s",
                    (f["tid"], an, luna, tip, xml, sursa, recipisa, data, f["tid"], an, luna, tip))


# ============================================================
#  1. Decizia și mențiunea (pe orice sursă)
# ============================================================
@nevoie_db
def test_fara_depunere_e_initiala(firma):
    st = R.stabileste(firma["conn"], firma["schema"], "d112", 2026, 6)
    assert (st.d_rec, st.mentiune, st.nr) == (0, None, None)


@nevoie_db
@pytest.mark.parametrize("sursa,recipisa,text", [
    ("iconta", None, "Rectificativă la declarația depusă prin iConta.eu pe 10.03.2026."),
    ("extern", "123456789", "Rectificativă la declarația depusă în afara iConta.eu pe 10.03.2026, recipisa 123456789."),
    ("contabil_anterior", None, "Rectificativă la declarația depusă de contabilul anterior (data nu e cunoscută în iConta.eu)."),
    ("migrare", None, "Rectificativă la declarația depusă pe 10.03.2026 (preluată din istoricul firmei)."),
])
def test_orice_sursa_face_rectificativa(firma, sursa, recipisa, text):
    # CPF art.105 alin.(3): „Declarațiile […] pot fi corectate prin depunerea unei declarații rectificative” — oricine a depus-o
    _depune(firma, "d390", 2026, 6, sursa=sursa, recipisa=recipisa)
    st = R.stabileste(firma["conn"], firma["schema"], "d390", 2026, 6)
    assert st.d_rec == 1 and st.nr == 1
    assert st.mentiune == text


@nevoie_db
def test_perioada_anuala_si_trimestriala_pe_luna_cheie(firma):
    _depune(firma, "d101", 2025, 12)
    _depune(firma, "d100", 2026, 9)
    assert R.stabileste(firma["conn"], firma["schema"], "d101", 2025).d_rec == 1          # anuală: luna 12
    assert R.stabileste(firma["conn"], firma["schema"], "d100", 2026, trim=3).d_rec == 1  # T3: luna 9
    assert R.stabileste(firma["conn"], firma["schema"], "d100", 2026, trim=2).d_rec == 0


def test_bifa_fara_depunere_inregistrata_ramane_rectificativa():
    st = R.stabileste(None, None, "d395", 2026, 6, bifata=True)
    assert st.d_rec == 1 and st.mentiune == "Rectificativă (bifată în formular): iConta.eu nu are nicio depunere înregistrată pe perioadă."


def test_marcajul_xml():
    assert R.marcaj_xml("d390", '<?xml version="1.0"?>\n<declaratie390 luna="6" d_rec="0" x="1"><a d_rec="1"/></declaratie390>') is False
    assert R.marcaj_xml("d101", '<?xml version="1.0"?><declaratie101 d_rec="2"/>') is True
    assert R.marcaj_xml("d406", '<AuditFile/>') is None
    assert R.marcaj_xml("d100", '<?xml version="1.0"?><declaratie100 luna="3"/>') is None


# ============================================================
#  2. Garda la „Confirmă depunerea” (coada)
# ============================================================
@nevoie_db
def test_depunere_aparuta_dupa_generare_opreste_confirmarea(firma):
    with firma["conn"].cursor() as cur:
        p = {"xml": '<?xml version="1.0"?><declaratie390 d_rec="0"/>', "randuri": {"depunere_anterioara_nr": None}}
        assert R.refuz_la_depunere(cur, firma["tid"], "d390", 2026, 6, p) is None          # nimic depus: trece
        _depune(firma, "d390", 2026, 6, sursa="extern", recipisa="777")
        r = R.refuz_la_depunere(cur, firma["tid"], "d390", 2026, 6, p)
        assert r and r["cod"] == "RECTIFICATIVA_NECESARA" and r["mesaj"] == (
            "Pe D390 06/2026 e înregistrată declarația depusă în afara iConta.eu pe 10.03.2026, după ce declarația aceasta a fost generată: "
            "plecată acum, ar ajunge la ANAF a doua oară ca inițială. Generează-o din nou: iese rectificativă."), r
        p_rect = {"xml": '<?xml version="1.0"?><declaratie390 d_rec="1"/>', "randuri": {"depunere_anterioara_nr": 1}}
        assert R.refuz_la_depunere(cur, firma["tid"], "d390", 2026, 6, p_rect) is None     # generată peste depunerea 1: trece
        # declarație din coada de dinainte (fără cheie): marcajul din XML decide
        assert R.refuz_la_depunere(cur, firma["tid"], "d390", 2026, 6, {"xml": p["xml"]})["cod"] == "RECTIFICATIVA_NECESARA"
        assert R.refuz_la_depunere(cur, firma["tid"], "d390", 2026, 6, {"xml": p_rect["xml"]}) is None


def test_marcheaza_depusa_cheama_garda():
    src = open(os.path.join(os.path.dirname(__file__), "coada_api.py"), encoding="utf-8").read()
    corp = src[src.index("def marcheaza_depusa"):src.index("def _scrie():")]
    assert "_rect.refuz_la_depunere(" in corp, "marcheaza_depusa nu mai oprește declarația generată înaintea unei depuneri"


# ============================================================
#  3. Fiecare generator: inițială și rectificativă, pe DUK
# ============================================================
def _salariat(f):
    with f["conn"].cursor() as cur:
        cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa) VALUES (%s,'P','I','2024-01-01',8,"
                    "'B') RETURNING id, data_angajare) INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) "
                    "SELECT id, data_angajare, 5000 FROM s", (_CNP,))


@nevoie_db
def test_d112_initiala_apoi_rectificativa_pe_duk(firma):
    from core import d112
    _duk_sau_skip("d112")
    _salariat(firma)
    xml0, res0 = d112.genereaza(firma["conn"], firma["schema"], Perioada(an=2026, luna=6))
    assert _drec(xml0) is False and res0.rectificativa is None
    _valid(xml0, "d112", 2026, 6)
    _depune(firma, "d112", 2026, 6, xml=xml0)
    xml1, res1 = d112.genereaza(firma["conn"], firma["schema"], Perioada(an=2026, luna=6))
    # structura D112: „d_rec=1 pt. tip_rec>0 sau null”; OPANAF 605/2026 anexa 2 pct.2.4: rectificativa „se completează integral”
    assert _drec_radacina(xml1) == "1" and "tip_rec" not in xml1
    assert res1.rectificativa == "Rectificativă la declarația depusă prin iConta.eu pe 10.03.2026." and res1.depunere_anterioara_nr == 1
    assert xml1.replace('d_rec="1"', 'd_rec="0"') == xml0, "rectificativa D112 cuprinde tot (pct.2.4)"
    _valid(xml1, "d112", 2026, 6)


def _prof_d301():
    return {"nume": "TEST SRL", "cui": "RO" + _CUI, "banca": "BCR", "iban": "RO49AAAA1B31007593840000", "adresa": "Str 1", "oras": "Buc",
            "judet": "B", "declarant_nume": "POP", "declarant_prenume": "ION", "declarant_functie": "ADMIN"}


@nevoie_db
def test_d301_rectificativa_pe_duk(firma):
    from core import d301
    _duk_sau_skip("d301")
    op = {"tip": 1, "nr_doc": "DOC1", "data_doc": "15.06.2026", "val_valuta": 1000, "tip_valuta": "EUR", "curs": 4.9770, "tva": 1045}
    res = d301.calcul_d301(_prof_d301(), Perioada(2026, luna=6), [op])
    _valid(d301.build_xml(res), "d301", 2026, 6)
    _depune(firma, "d301", 2026, 6, sursa="extern", recipisa="1")
    R.aplica(res, R.stabileste(firma["conn"], firma["schema"], "d301", 2026, 6))
    xml = d301.build_xml(res)
    assert _drec_radacina(xml) == "1"   # OPANAF 592/2016 anexa 2 cap.III: „bifând căsuţa corespunzătoare de pe formular”
    _valid(xml, "d301", 2026, 6)


@nevoie_db
def test_d390_rectificativa_pe_duk(firma):
    from core import d390
    from core.test_d390 import _prof, _oib_valid
    _duk_sau_skip("d390")
    res = d390.calcul_d390(_prof(), 2026, 6, [{"cui": "HR" + _oib_valid(), "nume": "ZAGREB DOO", "directie": "emisa", "total": 5000,
                                                "tva": 0}])
    _valid(d390.build_xml(res), "d390", 2026, 6)
    _depune(firma, "d390", 2026, 6, sursa="contabil_anterior")
    R.aplica(res, R.stabileste(firma["conn"], firma["schema"], "d390", 2026, 6))
    xml = d390.build_xml(res)
    assert _drec_radacina(xml) == "1"   # OPANAF 705/2020 anexa 2 cap.I: „Declaraţia depusă iniţial se rectifică […] bifând căsuţa”
    _valid(xml, "d390", 2026, 6)


@nevoie_db
def test_d101_rectificativa_pe_duk(firma):
    from core import d101
    from core.test_d101 import _prof
    _duk_sau_skip("d101")
    res = d101.calcul_d101(_prof(), 2025, {"P1": 100000, "P2": 60000})
    _valid(d101.build_xml(res), "d101", 2025)
    _depune(firma, "d101", 2025, 12)
    R.aplica(res, R.stabileste(firma["conn"], firma["schema"], "d101", 2025))
    xml = d101.build_xml(res)
    assert _drec_radacina(xml) == "1"   # structura D101: „d_rec =(0,1,2) 0-initiala, 1-rectificativa”
    _valid(xml, "d101", 2025)


def _d205_manual(*benef):
    return {"beneficiari": [{"categ": "1.a", "nume": n, "cif": c, "baza": b, "imp": i, "divid_d": b, "divid_p": b, "tip_plata": "2"}
                            for n, c, b, i in benef]}


@nevoie_db
def test_d205_rectificativa_numai_cu_pozitiile_corectate_pe_duk(firma):
    from core import d205
    _duk_sau_skip("d205")
    an = 2026
    xml0, res0 = d205.genereaza(firma["conn"], firma["schema"], Perioada(an), _d205_manual(("POPESCU ION", _CNP, 10000, 1600),
                                                                                               ("IONESCU ANA", _CNP2, 5000, 800)))
    assert _drec(xml0) is False
    _valid(xml0, "d205", an)
    _depune(firma, "d205", an, 12, xml=xml0, data="2026-10-21 18:00+03")   # după REGULA_DISTRIBUIT_PUBLICATA_LA (decizia 10.3)
    # corecție: Popescu 12.000 (nu 10.000), Ionescu scos din declarație
    xml1, res1 = d205.genereaza(firma["conn"], firma["schema"], Perioada(an), _d205_manual(("POPESCU ION", _CNP, 12000, 1920)))
    assert _drec_radacina(xml1) == "1"
    # OPANAF 179/2022 anexa 3 pct.I.5.2: „va cuprinde numai poziţiile corectate”; pct.I.5.3 lit.a): poziția eliminată, „la col. 7 - 10
    # se va înscrie cifra "0"”
    ben = {b.cif: (b.divid_d, b.divid_p, b.baza1, b.imp1) for b in res1.beneficiari}
    assert ben == {_CNP: (12000, 12000, 12000, 1920), _CNP2: (0, 0, 0, 0)}, ben
    assert res1.rectificativa.startswith("Rectificativă la declarația depusă prin iConta.eu")
    _valid(xml1, "d205", an)
    # a doua rectificativă, față de starea în vigoare (inițiala + prima rectificativă): numai ce s-a mai schimbat
    _depune(firma, "d205", an, 12, xml=xml1, data="2026-10-21 19:00+03")
    with pytest.raises(RefuzGenerare, match="nu e nimic de rectificat"):
        d205.genereaza(firma["conn"], firma["schema"], Perioada(an), _d205_manual(("POPESCU ION", _CNP, 12000, 1920)))


@nevoie_db
def test_d205_peste_depunere_fara_continut_se_refuza(firma):
    from core import d205
    _depune(firma, "d205", 2026, 12, sursa="extern", recipisa="55", data="2026-10-21 18:00+03")
    with pytest.raises(RefuzGenerare, match="numai pozițiile corectate"):
        d205.genereaza(firma["conn"], firma["schema"], Perioada(2026), _d205_manual(("POPESCU ION", _CNP, 10000, 1600)))


@nevoie_db
def test_d100_peste_depusa_numai_obligatiile_nedeclarate_pe_duk(firma):
    from core import d100
    _duk_sau_skip("d100")
    prof = {"cui": _CUI, "nume": "PROBA C77 SRL", "adresa": "Str 1", "declarant_nume": "Pop", "declarant_prenume": "Ion",
            "declarant_functie": "administrator"}
    prima = d100.calcul_d100(prof, 2026, 6, [{"cod_oblig": "121", "suma_dat": 1000, "cota": "1"}])
    xml0 = d100.build_xml(prima)
    _valid(xml0, "d100", 2026, 6)
    _depune(firma, "d100", 2026, 6, xml=xml0)
    acum = d100.calcul_d100(prof, 2026, 6, [{"cod_oblig": "121", "suma_dat": 1200, "cota": "1"}, {"cod_oblig": "103", "suma_dat": 300}])
    d100._peste_depusa(firma["conn"], firma["schema"], Perioada(2026, trim=2), acum, prof)
    # OPANAF 587/2016 anexa 4: „Corectarea obligațiilor declarate eronat în formular se face prin depunerea formularului 710”
    assert [o.cod_oblig for o in acum.obligatii] == ["103"] and acum.total_plata_a == 600
    assert acum.rectificativa == (
        "D100 numai cu obligațiile încă nedeclarate pe T2/2026 (codurile 103), peste declarația depusă prin iConta.eu pe 10.03.2026; "
        "codurile 121, declarate acolo, se corectează numai prin D710."), acum.rectificativa
    _valid(d100.build_xml(acum), "d100", 2026, 6)
    aceleasi = d100.calcul_d100(prof, 2026, 6, [{"cod_oblig": "121", "suma_dat": 1200, "cota": "1"}])
    with pytest.raises(RefuzGenerare, match="codul 121: declarat 1.000,00 lei, acum 1.200,00 lei; se corectează în D710"):
        d100._peste_depusa(firma["conn"], firma["schema"], Perioada(2026, trim=2), aceleasi, prof)


# D216 / D395 / D397: formularele manuale ale lotului 2 (valide pe DUK ca inițiale), acum peste o depunere înregistrată
def _caz_lot2(tip):
    from core.test_declaratii_lot2_duk import CAZURI
    return next(c for c in CAZURI if c[0] == tip)


@nevoie_db
@pytest.mark.parametrize("tip", ["d397", "d216"])
def test_formularele_cu_bifa_devin_rectificative_peste_depunere_pe_duk(firma, tip):
    _t, mod, per, manual = _caz_lot2(tip)
    _duk_sau_skip(tip)
    luna = getattr(per, "luna", None) or 12
    xml0, res0 = mod.genereaza(firma["conn"], firma["schema"], per, dict(manual))
    assert _drec(xml0) is False and res0.rectificativa is None
    # D216 cere indexul de depunere al inițialei (structura XML D216 v1.0.0 rândul 1.1): din recipisa marcării
    _depune(firma, tip, per.an, luna, sursa="extern", recipisa="123456789012")
    xml1, res1 = mod.genereaza(firma["conn"], firma["schema"], per, dict(manual))
    assert _drec(xml1) is True and res1.rectificativa.startswith("Rectificativă la declarația depusă în afara iConta.eu")
    if tip == "d216":
        assert _atribut(xml1, "index_corectie") == ["123456789012"], xml1[:600]
    _valid(xml1, tip, per.an, luna)


@nevoie_db
def test_d395_validatorul_nu_admite_rectificativa_se_refuza(firma):
    """DUK D395 v1, probat 21.10.2026: același XML e valid cu d_rec="0" și respins cu d_rec="1" („d_rec: valoarea '1' nu se incadreaza
    in intervalul cerut”). Peste o depunere înregistrată, a doua D395 ar pleca tot „inițială” (C77) -> nu se generează."""
    _t, mod, per, manual = _caz_lot2("d395")
    xml0, _r = mod.genereaza(firma["conn"], firma["schema"], per, dict(manual))
    assert _drec(xml0) is False
    _depune(firma, "d395", per.an, per.luna, sursa="extern", recipisa="9")
    with pytest.raises(RefuzGenerare, match="nu admite declarație rectificativă"):
        mod.genereaza(firma["conn"], firma["schema"], per, dict(manual))
    with pytest.raises(RefuzGenerare, match="nu admite declarație rectificativă"):
        mod.genereaza(None, None, per, dict(manual, d_rec=1))   # bifa fără depunere: aceeași imposibilitate


@pytest.mark.parametrize("tip", sorted(R.NU_ADMIT_RECTIFICATIVA))
def test_validatorul_respinge_d_rec_1_la_formularele_fara_rectificativa(tip):
    """Proba pe care stă `NU_ADMIT_RECTIFICATIVA`: cazul valid al lotului de probă, cu d_rec="1" scris în XML, e respins de DUK."""
    _duk_sau_skip(tip)
    cazuri = [c for m in ("test_declaratii_lot2_duk", "test_declaratii_lot4_duk", "test_declaratii_lot5_duk")
              for c in importlib.import_module("core." + m).CAZURI if c[0] == tip]
    _t, mod, per, manual = cazuri[0]
    xml, _r = mod.genereaza(None, None, per, dict(manual))
    _valid(xml, tip, per.an, getattr(per, "luna", None))
    xml1 = re.sub(r'\bd_rec="0"', 'd_rec="1"', xml, count=1)
    v = duk.valideaza(xml1, tip, an=per.an, luna=getattr(per, "luna", None), timeout=180)
    # câmpul `erori` al verdictului DUK, citit pe linii „eroare atribut: <atribut>: <motiv>”: singurul atribut respins e d_rec
    assert v.get("stare") == "erori" and _atribute_respinse(v["erori"]) == {"d_rec"}, v


@nevoie_db
def test_dispecerul_refuza_formularele_fara_rectificativa_peste_depunere(firma):
    _depune(firma, "d398", 2024, 3, sursa="extern")
    with pytest.raises(RefuzGenerare, match="D398 pe 03/2024: Declarația depusă în afara iConta.eu"):
        R.pe_cerere(firma["conn"], firma["schema"], "d398", {"an": 2024, "luna": 3, "manual": {}})
    assert R.pe_cerere(firma["conn"], firma["schema"], "d214", {"an": 2025, "manual": {}})[1] is None   # nimic depus: trece


@nevoie_db
def test_d216_rectificativa_fara_index_se_refuza(firma):
    _t, mod, per, manual = _caz_lot2("d216")
    _depune(firma, "d216", per.an, 12, sursa="contabil_anterior")
    with pytest.raises(ValueError, match="cere indexul de depunere al declarației inițiale"):
        mod.genereaza(firma["conn"], firma["schema"], per, dict(manual))
    m = dict(manual, index_corectie="98765")
    xml, _r = mod.genereaza(firma["conn"], firma["schema"], per, m)
    assert _atribut(xml, "index_corectie") == ["98765"], xml[:600]


# Formularele cu bifa din `manual`, prin dispecer: fiecare caz valid al loturilor de probă DUK, rectificativ (d_rec=1)
def _cazuri_dispecer():
    out = []
    for modul in ("test_declaratii_lot2_duk", "test_declaratii_lot4_duk", "test_declaratii_lot5_duk"):
        for tip, mod, per, manual in importlib.import_module("core." + modul).CAZURI:
            if tip in R.DREC_DIN_MANUAL:
                out.append((tip, mod, None, per, manual))
    lot3 = importlib.import_module("core.test_declaratii_lot3_duk")
    for tip, mod, conn, per in lot3.CAZURI:
        if tip in R.DREC_DIN_MANUAL:
            out.append((tip, mod, conn, per, lot3._MANUAL[tip]))
    return out


#: câmpurile pe care rectificativa le cere în plus (de completat de contabil; aici valori de formă, nu fiscale)
_IN_PLUS = {"d213": {"index_init": "123456789"}, "d318": {"reference_number": "RO000000001"}, "d177": {"index": "123456789"}}


@pytest.mark.parametrize("tip,mod,conn,per,manual", _cazuri_dispecer(), ids=lambda x: x if isinstance(x, str) else None)
def test_formularele_dispecerului_rectificative_pe_duk(tip, mod, conn, per, manual):
    _duk_sau_skip(tip)
    m = dict(manual, d_rec=1, **_IN_PLUS.get(tip, {}))
    xml, _res = mod.genereaza(conn, "tenant_013", per, m)
    assert _drec(xml) is True, xml[:300]
    _valid(xml, tip, per.an, getattr(per, "luna", None))


@nevoie_db
def test_pe_cerere_pune_bifa_si_indexul(firma):
    _depune(firma, "d213", 2025, 12, sursa="extern", recipisa="4455")
    body, st = R.pe_cerere(firma["conn"], firma["schema"], "d213", {"an": 2025, "manual": {"x": 1}})
    assert body["manual"] == {"x": 1, "d_rec": 1, "index_init": "4455"} and st.d_rec == 1
    body, st = R.pe_cerere(firma["conn"], firma["schema"], "d114", {"an": 2025, "luna": 3, "manual": {}})
    assert body["manual"] == {} and st.d_rec == 0
    assert R.pe_cerere(firma["conn"], firma["schema"], "d112", {"an": 2025, "luna": 3})[1] is None   # decide singur


# ============================================================
#  4. GARDA: niciun generator cu `d_rec` constant; orice declarație nouă e clasificată
# ============================================================
_CONSTANT = re.compile(r"""\bd_rec\s*=\s*\\?["']0\\?["']|\b(?:_attr|at)\(\s*["']d_rec["']\s*,\s*["']0["']\s*\)""")

#: Formularele fără niciun marcaj de rectificativă în validator (DUK, ultima versiune: niciun atribut d_rec / rectif / referenceNumber)
FARA_MARCAJ_IN_VALIDATOR = {"d169", "d169n", "d230", "d399", "d603", "d710"}


def test_orice_declaratie_e_clasificata():
    """O declarație nouă în registrul dispecerului (`declaratii_api.DECLARATII`) trebuie să-și declare drumul rectificativei."""
    from core import declaratii_api
    clase = (set(R.DECID_SINGURE), set(R.DREC_DIN_MANUAL), set(R.DREC_NEACOPERITE), FARA_MARCAJ_IN_VALIDATOR)
    for a in range(len(clase)):
        for b in range(a + 1, len(clase)):
            assert not clase[a] & clase[b], (a, b, clase[a] & clase[b])
    assert not set(R.NU_ADMIT_RECTIFICATIVA) & set(R.DREC_DIN_MANUAL)
    neclasificate = sorted(set(declaratii_api.DECLARATII) - set().union(*clase, set(R.NU_ADMIT_RECTIFICATIVA)))
    assert not neclasificate, "declarații fără drum de rectificativă (core.rectificativa): %s" % neclasificate


@pytest.mark.parametrize("tip", sorted(set(R.DECID_SINGURE) | set(R.DREC_DIN_MANUAL)))
def test_niciun_generator_nu_scrie_d_rec_constant(tip):
    src = open(os.path.join(os.path.dirname(__file__), "%s.py" % tip), encoding="utf-8").read()
    cod = re.sub(r'"""[\s\S]*?"""', "", src)          # docstring-urile descriu, nu emit
    cod = "\n".join(l.split("#", 1)[0] for l in cod.splitlines())
    m = _CONSTANT.search(cod)
    assert not m, "%s scrie d_rec constant: %r" % (tip, m.group(0))


@pytest.mark.parametrize("tip", R.DECID_SINGURE)
def test_generatoarele_care_decid_singure_cheama_rectificativa(tip):
    import ast
    # apelul ca nod AST (`_rect.stabileste(...)`), nu șirul în sursă — un comentariu care îl pomenește nu e un apel (core/test_garzi_pe_text.py)
    arb = ast.parse(open(os.path.join(os.path.dirname(__file__), "%s.py" % tip), encoding="utf-8").read())
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "stabileste"
               and isinstance(n.func.value, ast.Name) and n.func.value.id == "_rect" for n in ast.walk(arb)), \
        "%s nu mai citește depunerile perioadei (core.rectificativa)" % tip


def test_dispecerul_aplica_bifa_formularelor_manuale():
    import ast
    # apelurile ca noduri AST în corpul `genereaza` (`_rect.pe_cerere(...)`, `_rect.pe_rezultat(...)`), nu șiruri în sursă (core/test_garzi_pe_text.py)
    arb = ast.parse(open(os.path.join(os.path.dirname(__file__), "declaratii_api.py"), encoding="utf-8").read())
    fn = [n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name == "genereaza"]
    assert len(fn) == 1, "declaratii_api.genereaza: %d definiții la nivel de modul" % len(fn)
    chemate = {n.func.attr for n in ast.walk(fn[0]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and isinstance(n.func.value, ast.Name) and n.func.value.id == "_rect"}
    assert chemate >= {"pe_cerere", "pe_rezultat"}, "dispecerul nu pune rectificativa pe formularele cu bifă: %s" % sorted(chemate)


def test_ecranul_primeste_mentiunea():
    from core import uc_declaratii

    class _Res:
        rectificativa = "Rectificativă la declarația depusă pe 10.03.2026."
    assert uc_declaratii.campuri_rezultat("d390", _Res()).get("rectificativa") == _Res.rectificativa
