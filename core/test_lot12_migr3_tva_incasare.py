# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 252, decizia Costin 12.3 pct.5, verbatim: „252: coloana TVA la încasare e opțională în fișierul de preluare; dacă
lipsește, se ia regimul firmei la data facturii.”]

DEFECTUL. Facturile deschise preluate (`facturi.tip = 'preluata'`, 12.1) se scriau fără TVA, iar motorul TVA la încasare le trata pe
regulile generale (tipul nu era `factura`). La o firmă în sistemul TVA la încasare, TVA-ul cuprins în restul lor stă pe 4428 în balanța de
deschidere: încasarea din bancă / casă / compensare stingea factura, dar nu muta TVA-ul pe 4427 (emisă) / 4426 (primită), iar D300 și D394
nu-l declarau niciodată — 4428 rămânea cu sold pe viață.

REPARAȚIA. Coloana opțională „TVA la încasare” (da / nu; 1 / 0, D / N, x) pe fiecare factură; nespusă -> regimul firmei la data facturii
(`regim_tva_incasare.aplica_la`, perioadele din Date firmă). TVA-ul neexigibil = restul × cotă / (100 + cotă), cota standard la data facturii,
înghețat în `facturi.tva` (`solduri_parteneri_api.cu_regimul_tva`); motorul (`tva_incasare.regim_din_date`) îl citește -> banca / casa /
compensarea îl mută prin punctul unic (`linii_la_incasare`), D300 (`_pull_la_incasare`, secțiunea A/B) și D394 (tvaCol / tvaDed) îl declară.

CIFRELE (sintetice, CUI-uri cu cifra de control verificată — CLAUDE.md §10; cota standard 21% la 08/2026 — Legea 141/2025 art.II pct.42,
`common.COTE["tva_standard"]`): firma în sistem de la 01.01.2026; balanța la 31.08.2026: 4111 D 4.235 (ALFA FA-101 1.210 «da», FA-102 2.420
«nu»; BETA FB-7 605, celulă goală), 401 C 1.210 (GAMMA G-55, celulă goală), 4428 C 105 (= 210 + 105 − 210), 5121 D 10.000, 1012 C 12.920.

TEMEI (citat din `anaf_surse/cod_fiscal_227_2015_consolidat.txt`):
  CF art.282 alin.(3): „exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a
    prestării de servicii, în cazul persoanelor impozabile care optează în acest sens”;
  CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă”;
  CF art.282 alin.(3^1) lit.a): eligibile sunt „persoanele impozabile înregistrate în scopuri de TVA conform art. 316”;
  CF art.297 alin.(2): deducerea TVA-ului achiziției de la o persoană care aplică sistemul „este amânat până la data la care taxa [...] a fost
    plătită furnizorului/prestatorului său”; alin.(3): la fel pentru achizițiile persoanei care aplică sistemul;
  CF art.291 alin.(5): „În cazul operațiunilor supuse sistemului TVA la încasare, cota aplicabilă este cea în vigoare la data la care intervine
    faptul generator”.
Schemă efemeră din template, tranzacție anulată; perioadele pe tabelele partajate (declarații depuse) sintetice (2099).
"""
import datetime as _dt
import os
from decimal import Decimal

import pytest

from core import db as _db, solduri_parteneri_api as sp
from core.import_tabel import FisierNecitit

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot12_migr3"
ALFA, BETA, GAMMA = ("25200012", "ALFA DISTRIBUTIE SRL"), ("25200020", "BETA CONSTRUCT SRL"), ("25200039", "GAMMA LOGISTIC SRL")
DATA = "2026-08-31"
#: finalul refuzului de regim (`MESAJ_TVA_INCASARE_REFUZ`), scris aici, nu importat
COADA_REFUZ = "Soldurile pe parteneri nu se salvează până nu corectezi fișierul (în coloană «nu», sau celula goală pentru regimul din Date firmă) și nu-l încarci din nou."

FISIER = ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată;TVA la încasare\n"
          "4111;RO%s;%s;FA-101;10.08.2026;09.09.2026;1210,00;da\n"
          "4111;RO%s;%s;FA-102;20.08.2026;19.09.2026;2420,00;nu\n"
          "4111;%s;%s;FB-7;25.08.2026;;605,00;\n"
          "401;%s;%s;G-55;15.08.2026;14.09.2026;1210,00;\n"
          % (ALFA + ALFA + BETA + GAMMA)).encode("utf-8")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _firma(cur, platitor=True, in_sistem=True):
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA MIGR3 SRL','14399840','Str 1','Buc','B',"
                "'4690','BCR','RO49RNCB0000000000000001','0700000000',%s,'L','Popescu','Ion','ADMINISTRATOR')", (platitor,))
    if in_sistem:
        # CF art.282 alin.(3^1) lit.a): „de la” = prima zi a unei perioade fiscale
        cur.execute("INSERT INTO tva_incasare_perioade (de_la, sursa) VALUES ('2026-01-01', 'manual')")
        cur.execute("UPDATE firma_profil SET tva_la_incasare = true WHERE id = 1")
    for cont, d, cr in (("4111", 4235, 0), ("401", 0, 1210), ("4428", 0, 105), ("5121", 10000, 0), ("1012", 0, 12920)):
        cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (%s,%s,%s,%s)",
                    (cont, d, cr, DATA))


@pytest.fixture
def schema_goala():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


@pytest.fixture
def conn(schema_goala):
    with schema_goala.cursor() as cur:
        _firma(cur)
    return schema_goala


def _importa(c, continut=FISIER, nume="situatie_clienti_furnizori.csv"):
    return sp.importa(c, sp.extrage(continut, nume), DATA, schema=SCHEMA)


def _preluate(c):
    with c.cursor() as cur:
        cur.execute("SELECT numar, directie, total, tva, tva_lei, furnizor_tva_incasare FROM facturi WHERE tip = 'preluata' ORDER BY numar")
        return cur.fetchall()


def _id(c, numar):
    with c.cursor() as cur:
        cur.execute("SELECT id FROM facturi WHERE tip = 'preluata' AND numar = %s", (numar,))
        return cur.fetchone()[0]


# ── citirea coloanei ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_252_coloana_tva_la_incasare_se_citeste_pe_fiecare_factura():
    """da / nu / gol, pe fiecare factură; fișierul fără coloană nu poartă cheia (ecranul nu arată coloana). MUTAȚIE: `i_tvai` = -1 ->
    cheile lipsesc -> pică."""
    r = sp.extrage(FISIER, "situatie.csv")
    pe = {d["numar"]: d["tva_la_incasare"] for x in r for d in x["documente"]}
    assert pe == {"FA-101": True, "FA-102": False, "FB-7": None, "G-55": None}, pe
    fara = FISIER.replace(b";TVA la \xc3\xaencasare", b"").replace(b";da\n", b"\n").replace(b";nu\n", b"\n").replace(b";\n", b"\n")
    assert all("tva_la_incasare" not in d for x in sp.extrage(fara, "situatie.csv") for d in x["documente"])
    # forma pe solduri: pe rândul partenerului
    sol = ("cont;cui;denumire;sold debitor;sold creditor;TVA la incasare\n4111;RO%s;%s;605;0;D\n" % ALFA).encode()
    assert sp.extrage(sol, "parteneri.csv")[0]["tva_la_incasare"] is True


@pytest.mark.parametrize("v,asteptat", [("da", True), ("DA", True), ("1", True), ("x", True), ("D", True), ("nu", False), ("N", False),
                                         ("0", False), ("", None), ("  ", None)])
def test_252_valorile_acceptate(v, asteptat):
    assert sp.valoare_tva_incasare(v) is asteptat


def test_def_252_valoarea_necunoscuta_e_refuzata_cu_randul():
    """«poate» nu se ghicește: refuzul numește rândul, partenerul, factura și valoarea. MUTAȚIE: `valoare_tva_incasare` întoarce None pe
    necunoscut -> nu mai pică -> testul pică."""
    f = FISIER.replace(b"FB-7;25.08.2026;;605,00;\n", b"FB-7;25.08.2026;;605,00;poate\n")
    with pytest.raises(FisierNecitit) as e:
        sp.extrage(f, "situatie.csv")
    assert str(e.value) == ("Rândul 4 (%s, factura FB-7): în coloana „TVA la încasare” scrie „poate”. Se acceptă «da» sau «nu» (și 1 / 0, "
                            "D / N, x); lasă celula goală ca să se ia regimul firmei la data facturii, din Date firmă. Corectează celula și "
                            "încarcă fișierul din nou." % BETA[1]), str(e.value)


# ── regimul, înghețat la preluare ──────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_252_tva_neexigibil_din_coloana_si_din_regimul_firmei(conn):
    """FA-101 «da» -> 1.210 × 21 / 121 = 210,00 (CF art.282 alin.(8); art.291 alin.(5): cota la data facturii); FA-102 «nu» -> 0; FB-7 gol
    -> regimul firmei la 25.08.2026 (în sistem) -> 105,00; G-55 gol -> firma în sistem -> deducerea amânată (CF art.297 alin.(3)) 210,00,
    nu „furnizor la încasare”. 4428 din balanță (C 105) = 210 + 105 − 210 -> nicio atenție.
    ROȘU înainte: toate cu TVA 0. MUTAȚIE: `cu_regimul_tva` scos din `importa` -> TVA 0 -> pică."""
    rez = _importa(conn)
    assert _preluate(conn) == [("FA-101", "emisa", Decimal("1210.00"), Decimal("210.00"), Decimal("210.00"), False),
                               ("FA-102", "emisa", Decimal("2420.00"), Decimal("0.00"), Decimal("0.00"), False),
                               ("FB-7", "emisa", Decimal("605.00"), Decimal("105.00"), Decimal("105.00"), False),
                               ("G-55", "primita", Decimal("1210.00"), Decimal("210.00"), Decimal("210.00"), False)]
    d = rez["documente"]
    assert (d["la_incasare"], d["tva_emise"], d["tva_primite"]) == (3, 315.0, 210.0), d
    assert "atentie_tva" not in d, d


def test_def_252_firma_in_afara_sistemului_coloana_lipsa_regulile_generale(schema_goala):
    """Firma fără TVA la încasare, coloana goală -> TVA 0 pe toate (regimul firmei la data facturii); furnizorul spus «da» -> deducerea
    amânată numai pentru că el aplică sistemul (CF art.297 alin.(2)) -> `furnizor_tva_incasare`."""
    with schema_goala.cursor() as cur:
        _firma(cur, in_sistem=False)
    f = FISIER.replace(b"1210,00;da\n", b"1210,00;\n").replace(b"G-55;15.08.2026;14.09.2026;1210,00;\n",
                                                           b"G-55;15.08.2026;14.09.2026;1210,00;da\n")
    rez = _importa(schema_goala, f)
    assert [(n, t, fu) for n, _d, _t, t, _tl, fu in _preluate(schema_goala)] == [
        ("FA-101", Decimal("0.00"), False), ("FA-102", Decimal("0.00"), False), ("FB-7", Decimal("0.00"), False),
        ("G-55", Decimal("210.00"), True)]
    # balanța are 4428 C 105, facturile preluate dau 4428 D 210 -> atenția numește diferența (nu oprește)
    assert rez["documente"]["atentie_tva"] == (
        "TVA-ul neexigibil al facturilor deschise preluate: 0,00 lei din facturile emise, 210,00 lei din cele primite, adică 4428 debitor "
        "210,00 lei; 4428 din balanța de deschidere: creditor 105,00 lei. Diferența de 315,00 lei: verifică facturile cu altă cotă decât "
        "cea standard, cele scutite sau cu taxare inversă (în coloana „TVA la încasare”: «nu») și TVA-ul neexigibil al facturilor nesosite "
        "sau de întocmit (408 / 418)."), rez


def test_def_252_da_pe_emisa_in_afara_sistemului_e_refuzat_si_nimic_scris(schema_goala):
    """Emisă «da» la o dată la care firma nu aplica sistemul (CF art.282 alin.(3)) -> refuz numit, soldurile vechi neatinse."""
    with schema_goala.cursor() as cur:
        _firma(cur, in_sistem=False)
    with pytest.raises(ValueError) as e:
        _importa(schema_goala)
    assert str(e.value) == ("Coloana „TVA la încasare” nu se potrivește cu firma: %s, factura FA-101 din 10.08.2026: «TVA la încasare: "
                            "da», dar în Date firmă firma nu aplica sistemul TVA la încasare la această dată — scrie perioada în Date firmă "
                            "sau corectează coloana. " + COADA_REFUZ) % ALFA[1], str(e.value)
    assert _preluate(schema_goala) == []
    # previzualizarea spune același refuz, înainte de salvare (aceeași regulă, `refuz_tva_incasare`); pe firma în sistem: niciunul
    assert sp.refuz_tva_incasare(schema_goala, SCHEMA, sp.extrage(FISIER, "situatie.csv")) == str(e.value)


def test_252_previzualizarea_fara_refuz_pe_firma_in_sistem(conn):
    assert sp.refuz_tva_incasare(conn, SCHEMA, sp.extrage(FISIER, "situatie.csv")) is None


def test_def_252_da_la_firma_neplatitoare_e_refuzat(schema_goala):
    """«da» la o firmă neînregistrată în scopuri de TVA (CF art.282 alin.(3^1) lit.a) -> refuz numit."""
    with schema_goala.cursor() as cur:
        _firma(cur, platitor=False, in_sistem=False)
    with pytest.raises(ValueError) as e:
        _importa(schema_goala)
    assert str(e.value) == ("Coloana „TVA la încasare” nu se potrivește cu firma: %s, factura FA-101 din 10.08.2026: «TVA la încasare: "
                            "da», dar firma nu e înregistrată în scopuri de TVA (Date firmă). " + COADA_REFUZ) % ALFA[1], str(e.value)


# ── încasarea / plata mută TVA-ul; D300 și D394 îl declară ─────────────────────────────────────────────────────────────────────────
def _incaseaza(c):
    from core import reconciliere_api as rec
    r = rec.importa_extras(c, SCHEMA, [
        {"data": "10.09.2026", "suma": 1210, "detalii": "Incasare FA-101 CUI RO%s" % ALFA[0], "cui": ALFA[0]},
        {"data": "11.09.2026", "suma": 2420, "detalii": "Incasare FA-102 CUI RO%s" % ALFA[0], "cui": ALFA[0]},
        {"data": "12.09.2026", "suma": -1210, "detalii": "Plata G-55 CUI RO%s" % GAMMA[0], "cui": GAMMA[0]}], fisier="extras_092026.csv")
    for x in r["linii"]:
        assert x["status"] == "potrivit", r
        rec.conteaza(c, SCHEMA, x["id"])
    # încasarea parțială a lui FB-7 (300 din 605) prin casă: partea de TVA = 105 × 300 / 605 = 52,07 (alin.(8))
    from core import casa_api
    casa_api.adauga(c, SCHEMA, {"data": "2026-09-15", "categorie": "incasare_client", "suma": 300, "partener": BETA[1], "cui": BETA[0],
                                "document": "CH 1", "facturi": [{"factura_id": _id(c, "FB-7"), "suma": 300}]})
    with c.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata'")
        cur.execute("SELECT f.numar, l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l "
                    "ON l.inregistrare_id = i.id JOIN facturi f ON f.id = i.factura_id ORDER BY f.numar, l.id")
        return cur.fetchall()


def test_def_252_incasarea_muta_tva_si_d300_d394_il_declara(conn):
    """Banca: FA-101 +1.210 -> 5121 = 4111 1.210 și 4428 = 4427 210,00; FA-102 «nu» -> numai 5121 = 4111; G-55 −1.210 -> 401 = 5121 și
    4426 = 4428 210,00; casa: FB-7 300 -> 4428 = 4427 52,07. D300 09/2026: TVA colectată 21% din încasări 262,07 -> R9_2 262 (baza 1.248),
    deductibilă 21% 210 (R22_2, baza 1.000); secțiunea A: 105 − 52,07 = 52,93 rămas neexigibil (-> 53). D394 09/2026: tvaCol21 = 262,
    tvaDed21 = 210 (firma în sistem, OPANAF 2194/2025 D394 pct.5.1 / 5.2).
    ROȘU înainte: nicio linie 4428, D300 / D394 zero. MUTAȚIE: ramura `preluata` din `tva_incasare.regim_din_date` scoasă -> pică."""
    from core.common import Perioada
    from core import d300, d394
    _importa(conn)
    note = _incaseaza(conn)
    tva = [(n, d, cr, s) for n, d, cr, s in note if d == "4428" or cr == "4428"]
    assert tva == [("FA-101", "4428", "4427", Decimal("210.00")), ("FB-7", "4428", "4427", Decimal("52.07")),
                   ("G-55", "4426", "4428", Decimal("210.00"))], note
    assert [(d, cr, s) for n, d, cr, s in note if n == "FA-102"] == [("5121", "4111", Decimal("2420.00"))], note
    import psycopg2.extras as _E
    prof, fac = d300.pull(conn, SCHEMA, Perioada(2026, luna=9))
    rez = d300.calcul_d300(prof, Perioada(2026, luna=9), fac)
    R = rez.R
    assert (R.get("R9_1"), R.get("R9_2"), R.get("R22_1"), R.get("R22_2")) == (1248, 262, 1000, 210), {k: v for k, v in R.items() if v}
    assert (rez.neexigibil.get("tva_a"), rez.neexigibil.get("valoare_a"), rez.neexigibil.get("tva_b", 0)) == (53, 252, 0), rez.neexigibil
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        t = d394._tva_la_decontare(cur, "2026-09-01", "2026-10-01")
    assert (t["col"].get(21), t["ded"].get(21)) == (262, 210), t


# ── datele existente: migrarea 12.1 (soldurile salvate înainte) primește regimul firmei ────────────────────────────────────────────
def _solduri_vechi(c):
    with c.cursor() as cur:
        sp.asigura_tabel(c)
        cur.execute("INSERT INTO solduri_parteneri (cont, cui, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                    "('4111', %s, %s, 4235, 0, %s), ('401', %s, %s, 0, 1210, %s)", (ALFA[0], ALFA[1], DATA, GAMMA[0], GAMMA[1], DATA))


def test_def_252_migrarea_da_documentelor_vechi_regimul_firmei(conn):
    """Firma în sistem la 31.08.2026 -> „Sold la 31.08.2026” ALFA 4.235 cu TVA neexigibil 735,00 (4.235 × 21 / 121), GAMMA 1.210 cu TVA
    nededus 210,00. MUTAȚIE: `cu_regimul_tva` scos din migrare -> TVA 0 -> pică."""
    from core import migrare_documente_preluate as m
    _solduri_vechi(conn)
    r = m.aplica(conn, SCHEMA)
    assert r["documente"] == 2 and not r["sarite"], r
    assert [(n, t) for n, _d, _t, t, _tl, _f in _preluate(conn)] == [("Sold la 31.08.2026", Decimal("735.00")),
                                                                     ("Sold la 31.08.2026", Decimal("210.00"))]


def test_def_252_migrarea_nu_atinge_firma_cu_d300_depus_dupa_preluare(conn):
    """Firma cu un D300 depus pe o perioadă de după preluare (sintetic: 01/2099) -> documentele se scriu fără TVA, iar motivul se spune:
    secțiunea „TVA neexigibilă” a declarației depuse nu se schimbă. MUTAȚIE: garda `d300_depus_dupa` scoasă -> TVA 735 -> pică."""
    from core import migrare_documente_preluate as m
    _solduri_vechi(conn)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.tenants (schema_name, nume) VALUES (%s, 'PROBA MIGR3') RETURNING id", (SCHEMA,))
        tid = cur.fetchone()[0]
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, nr_depunere) VALUES (%s, 2099, 1, 'd300', '<x/>', 1)",
                    (tid,))
        assert m.d300_depus_dupa(cur, SCHEMA, _dt.date(2026, 8, 31)) == (2099, 1)
        assert m.d300_depus_dupa(cur, SCHEMA, _dt.date(2100, 1, 31)) is None
    r = m.aplica(conn, SCHEMA)
    assert r["documente"] == 2, r
    assert [t for _n, _d, _t, t, _tl, _f in _preluate(conn)] == [Decimal("0.00"), Decimal("0.00")]
    assert r["sarite"] == ["firma aplica sistemul TVA la încasare la 2026-08-31, dar are D300 depus pe 01/2099: documentele se scriu fără "
                           "TVA neexigibil (declarația depusă rămâne neatinsă); reîncarcă soldurile pe parteneri din ecran, cu coloana "
                           "„TVA la încasare”, dacă TVA-ul lor trebuie să devină exigibil la încasare"], r
