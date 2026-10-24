# -*- coding: utf-8 -*-
"""[lotul 12, pachetul ctrl] D112 și statul de plată: C97 (pensionarul, B1_2), 482 (luna cu concediu medical: baza CAM, deducerea
personală, reținerile din indemnizație pe fluturaș).

SURSE (locale, citite integral pe rândurile folosite):
- OPANAF 605/2026 anexa 2 (`anaf_surse/opanaf_605_2026_d112.txt`), B.1 rândul 2: „"Pensionar"- se completează cu "1" în cazul
  asiguraţilor care au şi statutul de pensionar şi "0" pentru celelalte situaţii”; secțiunea E pct.12, motivul exceptării „"4" - pentru
  persoana fizică prevăzută la art.146 alin. (5^7) lit.d) din Codul fiscal, respectiv, pentru salariaţii care au calitatea de pensionari
  pentru limită de vârstă în sistemul public de pensii”; secțiunea B rândul 4 („Total fond de salarii brute”): „sumele suportate de
  angajator, primele 5 zile de incapacitate temporară de muncă, pentru concedii medicale conform prevederilor O.U.G. nr. 158/2005 […]
  pentru care angajatorul datorează contribuţia asiguratorie pentru muncă”.
- Structura D112 (`anaf_surse/structura_D112_0726_070926.txt`): „baza_AJS=true daca asigSO=1 si B1_2=0 si B1_1=(1,…,51,…)”, „B1_10 …
  daca baza_AJS = false atunci B1_10=0” (ERR), „B4_3=ΣB1_10”, „B_cnp = … COUNT(asiguratB(cnp_asig)) cu baza_AJS=true”, „B4_14=ΣB1_5”,
  „C4_baza =Σasigurat ( A_5 + B4_14 + C_29) – C5_baza”, „C4_ct =Round(C4_baza * pCAM)”.
- CF (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`): art.76 alin.(1) „… inclusiv indemnizațiile pentru incapacitate temporară de
  muncă …”; art.77 alin.(2) „se acordă în limita venitului impozabil lunar realizat”, alin.(4) „venituri brute lunare din salarii”;
  art.220^4 alin.(1) „suma câștigurilor brute realizate din salarii și venituri asimilate salariilor”; art.220^5 „nu se datorează pentru
  prestațiile suportate din […] Fondul național unic de asigurări sociale de sănătate”.
- OUG 158/2005 art.12 (`anaf_surse/oug_158_2005_consolidat.html`): „A. de către angajator, din prima zi până în a 5-a zi de
  incapacitate temporară de muncă”.

Luna probei: 10/2026 — salariul minim 4.325 lei (HG 146/2026), 22 de zile lucrătoare, CAM 2,25% (CF art.220^3 alin.(1)).
CNP-urile de test au cifra de control verificată cu algoritmul din CLAUDE.md: 1800101410013, 1800202410011, 1500303410017.
"""
from decimal import Decimal

import pytest

from core import d112, db as _db, salarizare, stat_plata_api, tenant_provisioning as _tp
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _LA, structura, unic

_SCHEMA = "test_lot12_ctrl_d112"
_POP = {"cnp": "1800101410013", "nume": "POPESCU", "brut": 6000}
_ION = {"cnp": "1800202410011", "nume": "IONESCU", "brut": 5000}
_PENS = {"cnp": "1500303410017", "nume": "PENSIONAR", "brut": 5000, "scutit": True, "motiv": 4}


def _cnp_valid(cnp):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(cnp[i]) * ch[i] for i in range(12)) % 11
    return cnp[12] == str(1 if c == 10 else c)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _setup(cur, salariati):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,"
                "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA SRL','14399840','Str 1',"
                "'Buc','B','6202',true,'L','Pop','Ion','administrator')")
    for s in salariati:
        assert _cnp_valid(s["cnp"]), s["cnp"]
        s = {"scutit": False, "motiv": None, "pt": False, **s}
        s["ore"] = 4 if s["pt"] else 8
        cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,cor,data_nastere,"
                    "copii_scolarizati,declaratie_copii,tip_asigurat,functie_baza,part_time,persoane_intretinere,scutit_contrib_minim,"
                    "motiv_exceptare) VALUES (%(cnp)s,%(nume)s,'X','2024-01-01',%(ore)s,'B','251401','1980-06-01',0,false,'1',true,%(pt)s,0,"
                    "%(scutit)s,%(motiv)s) RETURNING id, data_angajare), "
                    "i AS (INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) SELECT id, data_angajare, %(brut)s FROM s) "
                    "SELECT id FROM s", s)


#: certificat cod 01, 5 zile lucrătoare (06–12.10.2026), 4 plătite de angajator (ziua de diminuare neplătită), indemnizația angajatorului
#: 1.000 lei; reținerile certificatului din `taxe_cm(1000, "01")`: CAS 250, CASS 100, impozit (1000 − 350) × 10% = 65, net 585
_CM = ("INSERT INTO concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,brut_fnuass,baza,media_zilnica,"
       "cas,cass,impozit,net,serie,numar,data_acordare,data_inceput,data_sfarsit,loc_prescriere) SELECT id,2026,10,'01',5,4,0,1000,0,"
       "30000,250,250,100,65,585,'AB','1','2026-10-06','2026-10-06','2026-10-12',1 FROM salariati WHERE nume='POPESCU'")


def _genereaza(conn, salariati, sql=()):
    with conn.cursor() as cur:
        _setup(cur, salariati)
        for q in sql:
            cur.execute(q)
    conn.commit()
    return d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=10))


def _duk_valid(xml):
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=10)
    assert rez["stare"] == "valid", rez


def _duk_numai_atentionarea_s38_3(xml):
    """Pensionarul (B1_2 = 1, B1_10 = 0): DUKIntegrator J27.0.6 nu dă erori, numai atenționarea S38.3 („Baza Indemnizatie SOMAJ = 0 si
    Ore lucrate efectiv in luna > 0”). Cauza e în validator, citită din bytecode (`javap -c d112validator/v33/AsiguratB1.class`):
    `baza_AJS` se calculează (offset 1543) din câmpul `_B1_2_f` ÎNAINTE ca acesta să fie citit din XML (offset 2021), deci validatorul
    socotește orice asigurat B1_2 = 0. Structura D112 cere B1_10 = 0 la baza_AJS=false („daca baza_AJS = false atunci B1_10=0”, ERR)."""
    import re
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=10)
    assert rez["stare"] == "erori" and rez.get("severitate") == "atentionare", rez
    assert set(re.findall(r"regula: (S[\d.]+)", rez["erori"])) == {"S38.3"}, rez
    assert not re.search(r"(^|\n)E:", rez["erori"]), rez


# ---------------------------------------------------------------- C97 — pensionarul

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c97_pensionar_dedus_din_motivul_exceptarii_4(conn):
    """Salariat scutit de contribuția minimă cu motivul 4 („pensionari pentru limită de vârstă”) -> B1_2 = 1, B1_10 = 0, B4_3 = 0; B_cnp
    numără numai celălalt salariat (2 asigurați, 1 cu baza_AJS). ROȘU pe codul vechi: B1_2 = "0" fix, B1_10 = B4_3 = brutul, B_cnp = 2.
    DUK: fără erori; numai atenționarea S38.3, din defectul validatorului descris la `_duk_numai_atentionarea_s38_3`."""
    xml, _res = _genereaza(conn, [_ION, _PENS])
    st = structura(xml)
    p_b1, p_b4 = unic(st["1500303410017"], "asiguratB1"), unic(st["1500303410017"], "asiguratB4")
    # OPANAF 605/2026 anexa 2, B.1 rândul 2 + secțiunea E pct.12 motivul „4”; structura: „daca baza_AJS = false atunci B1_10=0”
    assert (p_b1["B1_2"], int(p_b1["B1_10"]), int(p_b4["B4_3"])) == ("1", 0, 0), (p_b1, p_b4)
    i_b1, i_b4 = unic(st["1800202410011"], "asiguratB1"), unic(st["1800202410011"], "asiguratB4")
    assert (i_b1["B1_2"], int(i_b1["B1_10"]), int(i_b4["B4_3"])) == ("0", 5000, 5000), (i_b1, i_b4)
    b = unic(st["_angajator"], "angajatorB")
    # structura: „B_cnp = … COUNT(asiguratB(cnp_asig)) cu baza_AJS=true”; B_sanatate / B_pensie rămân pe ambii
    assert (int(b["B_cnp"]), int(b["B_sanatate"]), int(b["B_pensie"])) == (1, 2, 2), b
    _duk_numai_atentionarea_s38_3(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("motiv", [1, 3, 5])
def test_c97_alt_motiv_de_exceptare_nu_e_pensionar(conn, motiv):
    """Scutit cu motivul 1 (elev/student), 3 (dizabilități) sau 5 (mai multe contracte): nu e pensionar -> B1_2 = 0, B1_10 = brutul.
    INTERPRETARE CU TEMEI (d112.MOTIV_EXCEPTARE_PENSIONAR): numai motivul 4 numește pensionarul."""
    xml, _res = _genereaza(conn, [{**_PENS, "motiv": motiv}])
    b1 = unic(structura(xml)["1500303410017"], "asiguratB1")
    assert (b1["B1_2"], int(b1["B1_10"])) == ("0", 5000), b1


# ---------------------------------------------------------------- 482 — baza CAM în luna cu concediu medical

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_482_baza_cam_cuprinde_indemnizatia_angajatorului(conn):
    """POPESCU, salariu 6.000, certificat cod 01 de 5 zile (4 plătite de angajator, 1.000 lei; FNUASS 0): salariul realizat 6.000 × 17 / 22
    = 4.636,36 -> 4.636; baza CAM = 4.636 + 1.000 = 5.636 (B1_5 = B4_14 = C4_baza), CAM = ROUND(5.636 × 2,25%) = ROUND(126,81) = 127
    (C4_ct, obligația 480). ROȘU pe codul vechi: baza CAM 4.636, CAM 104. DUK valid."""
    xml, res = _genereaza(conn, [_POP], [_CM])
    st = structura(xml)
    b1, b4 = unic(st["1800101410013"], "asiguratB1"), unic(st["1800101410013"], "asiguratB4")
    # CF art.220^4 alin.(1) + art.76 alin.(1) („inclusiv indemnizațiile pentru incapacitate temporară de muncă”); art.220^5 exceptează numai
    # partea FNUASS; OUG 158/2005 art.12 lit.A: primele 5 zile, angajatorul
    assert (int(b1["B1_5"]), int(b4["B4_14"])) == (5636, 5636), (b1, b4)
    c4 = unic(st["_angajator"], "angajatorC4")
    assert (int(c4["C4_baza"]), int(c4["C4_ct"])) == (5636, 127), c4   # structura: „C4_ct =Round(C4_baza * pCAM)”
    cam = [o for o in res.obligatii if o.cod_oblig == "480"]
    assert [o.datorat for o in cam] == [127], res.obligatii
    _duk_valid(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_482_partea_fnuass_ramane_in_afara_bazei_cam(conn):
    """Același certificat, dar indemnizația suportată integral din FNUASS (1.000 lei pe FNUASS, 0 la angajator): baza CAM = salariul
    realizat 4.636, CAM 104 — CF art.220^5. DUK valid."""
    cm_fnuass = _CM.replace("'01',5,4,0,1000,0,", "'01',5,0,4,0,1000,")
    xml, _res = _genereaza(conn, [_POP], [cm_fnuass])
    c4 = unic(structura(xml)["_angajator"], "angajatorC4")
    assert (int(c4["C4_baza"]), int(c4["C4_ct"])) == (4636, 104), c4
    _duk_valid(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_482_cam_pe_stat_egal_cu_cam_declarat(conn):
    """Statul de plată împarte CAM-ul declarat pe salariați (`_imparte_cam`): un singur salariat -> CAM-ul lui = 127 = obligația 480. ROȘU
    pe codul vechi: 104 pe stat (baza fără indemnizația angajatorului)."""
    _xml, res = _genereaza(conn, [_POP], [_CM])
    st = stat_plata_api.stat_plata(conn, _SCHEMA, 2026, 10)
    assert [r["cam"] for r in st] == [127.0], st
    assert [o.datorat for o in res.obligatii if o.cod_oblig == "480"] == [127]


# ---------------------------------------------------------------- 482 — deducerea personală în luna cu concediu medical

def test_482_deducerea_se_stabileste_pe_salariu_plus_indemnizatia_impozabila():
    """Salariul lucrat 2.000 + indemnizația impozabilă 2.400 (netă de CAS/CASS 1.560): venitul brut lunar din salarii 4.400 = salariul
    minim 4.325 + 75 -> ceil(75 / 50) = 2 trepte -> 20% − 2 × 0,5% = 19% × 4.325 = 821,75 -> 822 (CF art.77 alin.(4)). Baza impozitului
    pe salariu = 2.000 × 65% − 822 = 478 -> impozit 47,80 -> 48. ROȘU pe codul vechi: deducerea pe 2.000 (sub minim) = 20% × 4.325 = 865."""
    r = salarizare.calcul_salariu(2000, la_data=_LA, exceptat_suprataxare=True,
                                  cm_impozabil=(Decimal("2400"), Decimal("1560")))
    assert r["deducere"]["total"] == Decimal("822.00"), r["deducere"]
    assert (r["baza_impozabila"], r["impozit"]) == (Decimal("478.00"), Decimal("48.00")), r


def test_482_limita_deducerii_cuprinde_netul_indemnizatiei():
    """Salariul lucrat 500 (net 325) + indemnizația impozabilă 3.000 (netă 1.950): venit brut 3.500 sub minim -> 20% × 4.325 = 865;
    limita (CF art.77 alin.(2), „în limita venitului impozabil lunar realizat”) = 325 + 1.950 = 2.275 -> acordată întreagă, 865. ROȘU pe
    codul vechi: plafonată la netul salariului, 325."""
    r = salarizare.calcul_salariu(500, la_data=_LA, exceptat_suprataxare=True,
                                  cm_impozabil=(Decimal("3000"), Decimal("1950")))
    assert r["deducere"]["total"] == Decimal("865.00"), r["deducere"]
    assert r["impozit"] == Decimal("0.00"), r


def test_482_indemnizatia_neimpozabila_nu_intra_in_deducere():
    """Certificatele cod 08 (maternitate, neimpozabil — CF art.62 lit.c) nu intră în `cm_impozabil_luna`; cod 01 intră, cu brutul la leu
    pe părți și contribuțiile din `taxe_cm`: 1.000,40 + 0 -> 1.000; CAS 250, CASS 100 -> net 650."""
    assert salarizare.cm_impozabil_luna([{"cod": "08", "brut_ang": 0, "brut_fnuass": 3000}], _LA) is None
    assert salarizare.cm_impozabil_luna([{"cod": "01", "brut_ang": Decimal("1000.40"), "brut_fnuass": 0},
                                         {"cod": "08", "brut_ang": 0, "brut_fnuass": 3000}], _LA) == (Decimal("1000"), Decimal("650"))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_482_d112_declara_deducerea_pe_venitul_cu_indemnizatia(conn):
    """POPESCU (salariu 6.000, 4.636,36 lucrați, certificatul cod 01 de 1.000 lei): venitul brut lunar 5.636,36 -> ceil(1.311,36 / 50) =
    27 trepte -> 20% − 13,5% = 6,5% × 4.325 = 281,13 -> 281 = E3_12 (rândul 4 al E.1: „deduceri personale acordate … în limita venitului
    impozabil lunar realizat”). ROȘU pe codul vechi: pe 4.636,36 -> 7 trepte -> 16,5% -> 714. DUK valid."""
    xml, _res = _genereaza(conn, [_POP], [_CM])
    e3 = unic(structura(xml)["1800101410013"], "asiguratE3")
    assert int(e3["E3_12"]) == 281, e3
    _duk_valid(xml)


# ---------------------------------------------------------------- 482 — reținerile din indemnizație pe fluturaș

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_482_compozitia_arata_retinerile_din_indemnizatie(conn):
    """Compoziția netului (ecran și fluturaș) are, sub „Indemnizație CM (netă)”, brutul indemnizației și reținerile din ea pe fel —
    CAS, CASS, impozit — iar brutul minus reținerile = netul. Reținerile sunt cele DECLARATE (`stat_final`: D112 pe salariat minus
    salariul). ROȘU pe codul vechi: rândurile lipseau (numai netul)."""
    _genereaza(conn, [_POP], [_CM])
    r = next(x for x in stat_plata_api.stat_final(conn, _SCHEMA, 2026, 10) if x["cm_zile"])
    assert r["cm_retineri_sursa"] == "D112", r
    rand = {c["eticheta"].strip(): c["valoare"] for c in stat_plata_api.compozitie_fluturas(r)}
    brut, cas = rand["din indemnizația CM brută"], rand["reținut din indemnizație: CAS (25%)"]
    cass, imp = rand["reținut din indemnizație: CASS (10%)"], rand["reținut din indemnizație: impozit pe venit"]
    assert (brut, cas, cass) == (1000.0, -250.0, -100.0), rand   # CF art.139 alin.(1) lit.o + CASS cod 01 (art.155 alin.(1) lit.i)
    assert round(brut + cas + cass + imp, 2) == rand["Indemnizație CM (netă)"], rand  # round-ok: sumă de bani, zgomot float
    assert -(cas + cass + imp) == r["cm_retineri"], (rand, r)


def test_482_exemplar_inghetat_fara_campuri_nu_arata_retinere_zero():
    """Un fluturaș înghețat de dinaintea câmpurilor `cm_cas` / `cm_cass` / `cm_impozit` nu primește rânduri de reținere cu 0."""
    r = {"brut": 3000.0, "cas": 750.0, "cass": 300.0, "impozit_salariu": 100.0, "net": 1850.0, "cm_zile": 3, "cm_net": 400.0,
         "cm_brut": 600.0, "deducere": 0.0}
    etichete = [c["eticheta"] for c in stat_plata_api.compozitie_fluturas(r)]
    # sub „Indemnizație CM (netă)” nu vine niciun rând de compoziție (nici brutul, nici vreo reținere): urmează direct „Net de plată”
    assert etichete[etichete.index("Indemnizație CM (netă)") + 1] == "Net de plată (salariu + indemnizație CM)", etichete
    assert not {e.strip() for e in etichete} & {"din indemnizația CM brută", "reținut din indemnizație: CAS (25%)",
                                                "reținut din indemnizație: CASS (10%)", "reținut din indemnizație: impozit pe venit"}, etichete


# ---------------------------------------------------------------- 69 — pragul contribuției minime la normă parțială, la arbitru

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_69_pragul_part_time_valid_la_duk_fara_atentionare(conn):
    """Normă parțială de 4 ore, 2.000 lei (sub salariul minim), toată luna 10/2026: B4_5P = B4_7P = 4.325 − 200 = 4.125 (OUG 89/2025
    art.III alin.(5) lit.b: „pentru veniturile aferente perioadei 1 iulie-31 decembrie 2026, cu suma de 200 lei lunar”), iar
    DUKIntegrator-ul instalat dă `valid`, FĂRĂ atenționare (validatorul vechi J27.0.1 semnala SP1B4_1 „B4_5P(4125) diferit de suma
    calculata 3750”; corecția regulii a venit în J27.0.2, „corectie regula salmin”). Mutația probată: pragul pe salariul minim întreg
    (4.325) -> DUK nu mai dă `valid` pe atenționarea SP1B4_1."""
    xml, _res = _genereaza(conn, [{**_ION, "brut": 2000, "pt": True}])
    b4 = unic(structura(xml)["1800202410011"], "asiguratB4")
    assert (int(b4["B4_5P"]), int(b4["B4_7P"])) == (4125, 4125), b4
    _duk_valid(xml)
