# -*- coding: utf-8 -*-
"""Lotul 13 (comanda Costin 13.1), salarizarea: 671 (zilele lunii dintr-o singură sursă), 679 (suma orelor suplimentare calculată),
670 b (excedentul de diurnă, venit salarial), C174 (E3_8 cuprinde tichetele), 677 (compoziția netului pe trei coloane, aceleași cifre).

Schemă efemeră din `tenant_template.sql` + `core/migrare_lot13_salarii.py` (ca la publicare), în tranzacție anulată; perioadele sunt
lunile 2026 ale firmei efemere (tabelele ei, nu tabele partajate)."""
import io
import os
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp
from core.common import Perioada

SCH = "efemer_lot13_sal"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:   # MASCA MOTIVATA: fără bază de test testele de aici se sar (cele pure rulează)
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import migrare_lot13_salarii as _m
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
        _m.aplica(c, SCH)
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)   # [lotul 10, garda pool-ului] numai pe tranzacția de pregătire
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,"
                        "tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA L13 SRL','14399840',"
                        "'Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001','profit',true,'L','Pop','Ion','administrator')")
            # CNP verificat cu cifra de control (cheia 279146358279): 1900101410011
            cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa,functie_baza,"
                        "scutit_contrib_minim) VALUES ('1900101410011','IONESCU','VASILE','2026-01-05',8,'B',true,false) "
                        "RETURNING id, data_angajare), i AS (INSERT INTO salariu_istoric (salariat_id, valabil_din, "
                        "salariu_brut) SELECT id, data_angajare, 5000 FROM s) SELECT id FROM s")
        c.commit()
    try:
        with _db.get_conn(SCH) as c:
            try:
                yield c
            finally:
                c.rollback()
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


def _sid(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM salariati")
        return cur.fetchone()[0]


def _certificat(conn, sid, di, ds, zile, an=2026, luna=10):
    """Certificatul din proba lui Costin (Ionescu Vasile, 13–15.10.2026), scris prin funcția aplicației."""
    from core import salariati_api as sa
    r = sa.salveaza_concediu(conn, sid, {"serie": "CCMAM", "numar": "1234567", "cod": "01", "data_acordare": di, "data_inceput": di,
                                         "data_sfarsit": ds, "zile_cm": zile, "venituri_6_luni": 30000, "zile_6_luni": 125,
                                         "este_continuare": False, "spitalizare": False, "program_national": False,
                                         "an": an, "luna": luna})
    assert r["ok"], r


# ── 671: pontajul, statul și tichetele pornesc din aceleași zile ───────────────────────────────────────────────────────────────
def test_671_pontajul_arata_concediul_medical_din_certificat(conn):
    """Proba lui Costin: certificat 13–15.10.2026 -> în pontaj 13, 14, 15 sunt „concediu medical” (din certificat, nu se schimbă de
    aici), 22 de zile lucrătoare - 3 = 19 de prezență; statul arată 19 zile lucrate din 22. MUTAȚIE: certificatele scoase din
    `pontaj.zilele_lunii` -> 13–15 „prezent”, 22 de prezență -> pică."""
    from core import pontaj, stat_plata_api as sp
    sid = _sid(conn)
    _certificat(conn, sid, "2026-10-13", "2026-10-15", 3)
    g = pontaj.grila(conn, SCH, sid, 2026, 10)
    zile = {z["zi"]: z for z in g["zile"]}
    for zi in ("2026-10-13", "2026-10-14", "2026-10-15"):
        assert (zile[zi]["stare"], zile[zi]["sursa"], zile[zi]["editabil"]) == ("concediu_medical", "certificat", False), zile[zi]
    assert (g["rezumat"]["concediu_medical"], g["rezumat"]["prezent"]) == (3, 19)
    assert g["regula"] == pontaj.REGULA_PONTAJ
    rand = next(x for x in sp.stat_plata(conn, SCH, 2026, 10) if x["id"] == sid)
    assert (rand["zile_lucrate"], rand["zile_lucratoare_luna"], rand["cm_zile"]) == (19, 22, 3)
    assert rand["regula_pontaj"] == pontaj.REGULA_PONTAJ                      # aceeași frază în pontaj și în stat
    assert [x["cod"] for x in rand["semne"]][:1] == ["cm"]


def test_671_ziua_de_concediu_medical_nu_se_marcheaza_de_mana(conn):
    """Concediul medical vine din certificate: „concediu medical” pus de mână se refuză, iar ziua din certificat nu se poate marca altfel
    (altfel tichetele ar scădea ziua de două ori). MUTAȚIE: refuzul pentru zilele needitabile scos din `seteaza` -> trece -> pică."""
    from core import pontaj
    sid = _sid(conn)
    _certificat(conn, sid, "2026-10-13", "2026-10-15", 3)
    r = pontaj.seteaza(conn, SCH, sid, "2026-10-20", "concediu_medical")
    assert r == {"ok": False, "mesaj": pontaj.MESAJ_CM_MANUAL}
    r = pontaj.seteaza(conn, SCH, sid, "2026-10-14", "concediu_odihna")
    assert r["ok"] is False and "certificat" in r["mesaj"]
    assert pontaj.seteaza(conn, SCH, sid, "2026-10-20", "concediu_odihna")["ok"] is True


def test_671_tichetele_nu_scad_de_doua_ori_ziua_din_certificat(conn):
    """HG 1045/2018 art.10 alin.(3): tichetul se acordă pe zilele efectiv lucrate. 22 de zile - 3 CM (certificat) - 2 CO (pontaj) = 17;
    un CO marcat înainte pe o zi a certificatului (date vechi) nu mai scade a doua oară. MUTAȚIE: `zile_fara_tichet` pe pontajul brut
    (fără sursa unică) -> 16 tichete -> pică."""
    from core import pontaj, stat_plata_api as sp, perioada as per
    sid = _sid(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET tichet_masa_valoare = 40 WHERE id = %s", (sid,))
        # o zi marcată CO ÎNAINTE de certificat (datele existente): ziua 14 intră apoi sub certificat
        cur.execute("INSERT INTO pontaj (salariat_id, zi, stare) VALUES (%s, '2026-10-14', 'concediu_odihna')", (sid,))
    _certificat(conn, sid, "2026-10-13", "2026-10-15", 3)
    assert pontaj.seteaza(conn, SCH, sid, "2026-10-20", "concediu_odihna")["ok"]
    assert pontaj.seteaza(conn, SCH, sid, "2026-10-21", "concediu_odihna")["ok"]
    per.confirma(conn, SCH, 2026, 10, "pontaj", user_id=1)
    assert pontaj.zile_fara_tichet(conn, SCH, sid, 2026, 10) == 2
    rand = next(x for x in sp.stat_plata(conn, SCH, 2026, 10) if x["id"] == sid)
    assert (rand["tichete_zile"], rand["tichete_nominal"]) == (17, 680.0)


def test_671_concediu_medical_vechi_fara_certificat_se_semnaleaza_si_nu_da_tichet(conn):
    """Datele existente: o zi marcată „concediu medical” de mână înainte de 671 (fără certificat) se arată ca de verificat și nu dă
    tichet; statul o semnalează. MUTAȚIE: `cm_fara_certificat` scos din `fara_tichet` -> pică."""
    from core import pontaj, stat_plata_api as sp, perioada as per
    sid = _sid(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET tichet_masa_valoare = 40 WHERE id = %s", (sid,))
        cur.execute("INSERT INTO pontaj (salariat_id, zi, stare) VALUES (%s, '2026-10-06', 'concediu_medical')", (sid,))
    g = pontaj.grila(conn, SCH, sid, 2026, 10)
    assert g["rezumat"]["cm_fara_certificat"] == 1 and g["avertismente"]
    per.confirma(conn, SCH, 2026, 10, "pontaj", user_id=1)
    rand = next(x for x in sp.stat_plata(conn, SCH, 2026, 10) if x["id"] == sid)
    assert rand["tichete_zile"] == 21
    assert any(x["cod"] == "verifica" and "fără certificat" in x["titlu"] for x in rand["semne"])


# ── 679: suma orelor suplimentare se calculează ───────────────────────────────────────────────────────────────────────────────
def test_679_suma_orelor_suplimentare_se_calculeaza_din_ore_tarif_si_spor(conn):
    """Exemplul comenzii: 5.000 lei / (22 zile lucrătoare în 10/2026 × 8 ore) = 28,409… lei/oră × 10 ore × 175% = 497,16 lei (Codul
    muncii art.123 alin.(1)-(2)); suma trimisă de ecran se ignoră. MUTAȚIE: sporul scos din `suma_ore_suplimentare` -> 284,09 -> pică."""
    from core import elemente_salariale as es, stat_plata_api as sp
    sid = _sid(conn)
    r = es.adauga(conn, SCH, sid, 2026, 10, {"tip": "ore_suplimentare", "denumire": "ore suplimentare octombrie", "ore": 10,
                                            "spor_procent": 75, "suma": 1})
    assert (r["ok"], r["suma"], r["tarif_orar"]) == (True, "497.16", "28.4091")
    assert "avertisment" not in r
    sub = es.adauga(conn, SCH, sid, 2026, 10, {"tip": "ore_suplimentare", "denumire": "ore", "ore": 2, "spor_procent": 50})
    assert sub["suma"] == "85.23" and "75%" in sub["avertisment"]        # 28,409 × 2 × 150% = 85,227 -> 85,23; sub minimul legal
    rand = next(x for x in sp.stat_plata(conn, SCH, 2026, 10) if x["id"] == sid)
    e = rand["elemente"][0]
    assert (e["suma"], e["spor_procent"], e["tarif_orar"]) == ("497.16", "75.00", "28.41")


def test_679_randul_vechi_fara_spor_isi_arata_sporul_din_suma(conn):
    """Datele existente (rândul 497,16 al lui Ionescu, scris înainte de 679, fără spor salvat): ecranul arată sporul care rezultă din
    suma scrisă — 75% —, marcat ca dedus; suma nu se rescrie. MUTAȚIE: `cu_calculul` fără ramura `spor_dedus` -> spor None -> pică."""
    from core import stat_plata_api as sp
    sid = _sid(conn)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO elemente_salariale (salariat_id, an, luna, tip, denumire, ore, suma) "
                    "VALUES (%s, 2026, 10, 'ore_suplimentare', 'ore suplimentare octombrie', 10, 497.16)", (sid,))
    rand = next(x for x in sp.stat_plata(conn, SCH, 2026, 10) if x["id"] == sid)
    e = rand["elemente"][0]
    assert (e["suma"], e["spor_procent"], e.get("spor_dedus")) == ("497.16", "75.00", True)


def test_679_ore_suplimentare_cer_orele_si_sporul_nu_suma():
    from core import elemente_salariale as es
    _, er = es.valideaza({"tip": "ore_suplimentare", "denumire": "x"})
    assert [e["camp"] for e in er] == ["ore", "spor"]
    d, er = es.valideaza({"tip": "ore_suplimentare", "denumire": "x", "ore": "7.5", "spor_procent": "100"})
    assert (er, d["suma"], d["ore"], d["spor_procent"]) == ([], None, Decimal("7.50"), Decimal("100.00"))


# ── 670 b: excedentul de diurnă e venit salarial ──────────────────────────────────────────────────────────────────────────────────
def test_670b_excedentul_de_diurna_intra_in_brut_baze_d112_dar_nu_in_net_si_nu_pe_641(conn):
    """CF art.76 alin.(2) lit.k (venit asimilat salariilor, partea peste plafon) + art.139 alin.(1) lit.j / art.157 alin.(1) lit.m /
    art.220^4 alin.(1) lit.h (bazele CAS, CASS, CAM); OPANAF 605/2026 anexa 2, E.3 rândul 8.2.1 (E3_52). 5.000 + 300 excedent: CAS
    1.325, CASS 530; netul în bani scade numai cu reținerile excedentului (excedentul s-a plătit prin decont), 641 = 421 rămâne 5.000.
    MUTAȚIE: `exces_diurna` scos din `b_imp` (salarizare) -> CAS 1.250 -> pică."""
    from core import diurna_salariat as ds, stat_plata_api as sp, d112, salarii_contare as sc, duk, salarizare as sz
    sid = _sid(conn)
    with conn.cursor() as cur:
        i1 = ds.adauga_excedent(cur, SCH, sid, 2026, 9, Decimal("300"), "decont:7", "decont final 7, deplasare internă")
        i2 = ds.adauga_excedent(cur, SCH, sid, 2026, 9, Decimal("300.00"), "decont:7", "decont final 7, refăcut")   # idempotent
        assert i1 == i2
        assert ds.total(ds.excedente_luna(cur, SCH, 2026, 9)[sid]) == Decimal("300.00")
    fara = sz.calcul_salariu(5000, la_data=__import__("datetime").date(2026, 9, 1), venit_brut_total=5000)
    rand = next(x for x in sp.stat_plata(conn, SCH, 2026, 9) if x["id"] == sid)
    assert (rand["brut"], rand["cas"], rand["cass"], rand["exces_diurna"]) == (5300.0, 1325.0, 530.0, 300.0)
    assert rand["net"] == pytest.approx(5000 - 1325 - 530 - rand["impozit"])          # în bani: fără excedent
    assert rand["net"] < float(fara["net"])                                           # reținerile excedentului ies din salariu
    xml, _r = d112.genereaza(conn, SCH, Perioada(an=2026, luna=9))
    assert 'E3_59="300" E3_52="300"' in xml and 'E3_8="5300"' in xml
    if duk.poate_valida("d112"):
        rez = duk.valideaza(xml, "d112", an=2026, luna=9)
        assert rez["stare"] == "valid", rez
    note = dict(((n[0], n[1]), n[2]) for n in sc.note_lunare(conn, SCH, 2026, 9, xml)[0])
    assert note[("641", "421")] == Decimal("5000.00")
    with conn.cursor() as cur:
        ds.sterge_excedent(cur, SCH, "decont:7")
        assert ds.excedente_luna(cur, SCH, 2026, 9) == {}


def test_670b_adauga_excedent_refuza_ce_nu_e_venit():
    from core import diurna_salariat as ds
    with pytest.raises(ValueError):
        ds._suma("0")
    with pytest.raises(ValueError):
        ds._suma("abc")


# ── 684: excedentul cade odată cu nota decontului ──────────────────────────────────────────────────────────────────────────────────
def _nota_decont(cur):
    from core import repo_contabilitate as rc
    r = rc.nota_operatiune_ciorna(cur, SCH, "2026-09-20", "Decont deplasare proba 684")
    return int(r["id"] if isinstance(r, dict) else r[0])


def test_684_stergerea_notei_decontului_scoate_excedentul_din_stat_si_d112(conn):
    """684 (găsită de OPS la integrare): nota decontului ștearsă din jurnal lăsa excedentul de diurnă în statul de plată și în D112 —
    venit salarial fără decont. Acum excedentul e legat de notă (`inregistrare_id`, ON DELETE CASCADE): ștergerea ei prin jurnal
    (`jurnal_api.sterge`) îl scoate, iar statul revine la 5.000. Temeiul venitului: CF art.76 alin.(2) lit.k (excedentul există numai
    ca parte a unei indemnizații de delegare acordate — fără decont, nu există). MUTAȚIE: `ON DELETE CASCADE` scos din `DDL_NOTA`
    (cheia străină fără acțiune) -> ștergerea notei e refuzată de bază -> pică."""
    from core import diurna_salariat as ds, jurnal_api, stat_plata_api as sp
    sid = _sid(conn)
    with conn.cursor() as cur:
        nid = _nota_decont(cur)
        ds.adauga_excedent(cur, SCH, sid, 2026, 9, Decimal("300"), "decont-deplasare:%d" % nid, "proba 684", nota_id=nid)
    assert next(x for x in sp.stat_plata(conn, SCH, 2026, 9) if x["id"] == sid)["brut"] == 5300.0
    assert jurnal_api.sterge(conn, SCH, nid) == {"ok": True}
    with conn.cursor() as cur:
        assert ds.excedente_luna(cur, SCH, 2026, 9) == {}
    assert next(x for x in sp.stat_plata(conn, SCH, 2026, 9) if x["id"] == sid)["brut"] == 5000.0
    # și pe un drum care nu trece prin jurnal (ex. ștergerea ciornelor derivate): baza o face, nu o chemare care se poate uita
    with conn.cursor() as cur:
        nid2 = _nota_decont(cur)
        ds.adauga_excedent(cur, SCH, sid, 2026, 9, Decimal("120"), "decont-deplasare:%d" % nid2, "proba 684 b", nota_id=nid2)
        cur.execute("DELETE FROM %s.inregistrari WHERE id = %%s" % SCH, (nid2,))
        assert ds.excedente_luna(cur, SCH, 2026, 9) == {}
        with pytest.raises(ValueError):
            ds.adauga_excedent(cur, SCH, sid, 2026, 9, Decimal("50"), "decont-deplasare:%d" % nid2, "nota ștearsă", nota_id=nid2)


def test_684_datele_existente_primesc_nota_iar_orfanele_se_scot(conn):
    """Datele de dinainte de 684: rândul scris de decont (`decont-deplasare:<nota>`) primește nota; cel a cărui notă fusese ștearsă
    (orfanul defectului) iese; excedentul cu altă referință (fără notă) rămâne. MUTAȚIE: DELETE-ul scos din `REPARA_LEGATURA` ->
    orfanul rămâne -> pică."""
    from core import diurna_salariat as ds
    sid = _sid(conn)
    with conn.cursor() as cur:
        nid = _nota_decont(cur)
        cur.execute("SELECT COALESCE(max(id), 0) + 1000 FROM %s.inregistrari" % SCH)
        lipsa = cur.fetchone()[0]
        for ref in ("decont-deplasare:%d" % nid, "decont-deplasare:%d" % lipsa, "decont:7"):
            cur.execute("INSERT INTO %s.diurna_excedent (salariat_id, an, luna, suma, referinta) VALUES (%%s, 2026, 9, 100, %%s)" % SCH,
                        (sid, ref))
        cur.execute(ds.REPARA_LEGATURA.format(s=SCH))
        cur.execute("SELECT referinta, inregistrare_id FROM %s.diurna_excedent" % SCH)
        assert {tuple(r) for r in cur.fetchall()} == {("decont-deplasare:%d" % nid, nid), ("decont:7", None)}


def test_684_firmele_noi_au_aceeasi_legatura_ca_migrarea():
    """Firmele noi (`tenant_template.sql`) și cele migrate (`DDL_NOTA`) au aceeași cheie străină, cu ON DELETE CASCADE. MUTAȚIE:
    CASCADE scos numai din `DDL_NOTA` -> textele diferă -> pică."""
    from core import diurna_salariat as ds
    tpl = io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tenant_template.sql"), encoding="utf-8").read()
    assert "ON DELETE CASCADE" in ds.DDL_NOTA
    assert ds.DDL_NOTA.replace('"{s}"', "TENANT_PLACEHOLDER") in tpl, "tenant_template.sql nu are legătura excedentului de notă (684)"


def test_684_orice_chemare_de_productie_leaga_excedentul_de_nota():
    """Garda statică: fiecare `adauga_excedent(` din codul de producție (core/*.py fără teste, main.py) trimite `nota_id=` — un drum nou
    care scrie excedent fără notă l-ar lăsa în stat după ștergerea decontului. CALIBRARE: chemarea fără `nota_id` e prinsă."""
    rele, n = _chemari_fara_nota()
    assert n >= 1, "ANTI-VACUU: nicio chemare de producție a lui adauga_excedent"
    assert not rele, "excedent de diurnă scris fără nota decontului (684): %s" % rele
    rele2, _n = _chemari_fara_nota({"core/x.py": 'ds.adauga_excedent(cur, s, 1, 2026, 9, d, "decont-deplasare:%d" % i, "x")\n'})
    assert rele2 == ["core/x.py:1"], rele2


def _chemari_fara_nota(surse=None):
    import glob
    import re
    if surse is None:
        rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fis = [f for f in glob.glob(os.path.join(rad, "core", "*.py")) if not os.path.basename(f).startswith("test_")
               and os.path.basename(f) != "diurna_salariat.py"] + [os.path.join(rad, "main.py")]
        surse = {os.path.relpath(f, rad): io.open(f, encoding="utf-8").read() for f in fis if os.path.exists(f)}
    rele, n = [], 0
    for cale, txt in surse.items():
        for m in re.finditer(r"\badauga_excedent\(", txt):
            # textul chemării: până la paranteza care o închide
            niv, i = 1, m.end()
            while niv and i < len(txt):
                niv += {"(": 1, ")": -1}.get(txt[i], 0)
                i += 1
            n += 1
            if "nota_id=" not in txt[m.end():i]:
                rele.append("%s:%d" % (cale, txt.count("\n", 0, m.start()) + 1))
    return rele, n


# ── C174: E3_8 cuprinde tichetele ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_c174_e3_8_cuprinde_tichetele_de_masa_si_d112_e_valid(conn):
    """OPANAF 605/2026 anexa 2, E.3 rândul 8 „Total venit brut, din care:” … rândul 8.3.1 „Contravaloarea tichetelor de masă”; structura:
    „E3_8>= E3_61 + E3_59 + E3_60 + E3_69+E3_90”. 5.000 + 22 tichete × 40 = 880 -> E3_8 = E1_1 = B1_sal2 = 5.880, E3_10 = 880; DUK fără
    erori. MUTAȚIE: avantajele scoase din `brute` -> E3_8 = 5.000 -> pică."""
    from core import d112, duk, perioada as per
    sid = _sid(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET tichet_masa_valoare = 40 WHERE id = %s", (sid,))
    per.confirma(conn, SCH, 2026, 10, "pontaj", user_id=1)
    xml, _r = d112.genereaza(conn, SCH, Perioada(an=2026, luna=10))
    import re
    e3 = re.search(r"<asiguratE3 [^>]*/>", xml).group(0)
    e1 = re.search(r"<asiguratE1 [^>]*/>", xml).group(0)
    b1 = re.search(r"<asiguratB1 [^>]*/>", xml).group(0)
    assert 'E3_8="5880"' in e3 and 'E3_10="880"' in e3 and 'E3_60="880"' in e3, e3
    assert 'E1_1="5880"' in e1 and 'B1_sal2="5880"' in b1 and 'B1_sal1="5000"' in b1
    if duk.poate_valida("d112"):
        rez = duk.valideaza(xml, "d112", an=2026, luna=10)
        assert rez["stare"] == "valid", rez


# ── 677: compoziția pe trei coloane, aceleași cifre ───────────────────────────────────────────────────────────────────────────────
def test_677_compozitia_pe_trei_coloane_are_cifrele_fluturasului_si_se_inchide(conn):
    """„Cifrele de azi sunt corecte — se schimbă doar organizarea.” Pe un salariat cu concediu medical, ore suplimentare și tichete:
    veniturile în bani − reținerile = netul de plată (la ban); netul de plată, costul și indemnizația CM sunt aceleași cifre ca pe fluturaș;
    indemnizația CM apare o singură dată, cu brut și net pe același rând; rândul „Zile de concediu medical” fără sumă nu mai e.
    MUTAȚIE: reținerile CM scoase din coloana „Rețineri” -> coloanele nu se mai închid -> pică."""
    from core import stat_plata_api as sp, elemente_salariale as es, perioada as per
    sid = _sid(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET tichet_masa_valoare = 40 WHERE id = %s", (sid,))
    _certificat(conn, sid, "2026-10-13", "2026-10-15", 3)
    assert es.adauga(conn, SCH, sid, 2026, 10, {"tip": "ore_suplimentare", "denumire": "ore", "ore": 10, "spor_procent": 75})["ok"]
    per.confirma(conn, SCH, 2026, 10, "pontaj", user_id=1)
    r = next(x for x in sp.stat_final(conn, SCH, 2026, 10) if x["id"] == sid)
    c = r["compozitie_coloane"]
    ven = {x["eticheta"]: x for x in c["venituri"]}
    ret = {x["eticheta"]: x for x in c["retineri"]}
    rez = {x["eticheta"]: x for x in c["rezultat"]}
    in_bani = ven["Venituri în bani"]["valoare"]
    q = lambda v: Decimal(str(v)).quantize(Decimal("0.01"))   # noqa: E731
    assert q(in_bani) - q(ret["Total rețineri"]["valoare"]) == q(r["net_de_plata"])
    assert rez["Net de plată"]["valoare"] == r["net_de_plata"]
    assert rez["Cost total angajator (cu indemnizația CM suportată de angajator)"]["valoare"] == r["cost_total"]
    assert ret["CAS (25%)"]["valoare"] == r["cas"] and ret["reținut din indemnizație: CAS (25%)"]["valoare"] == r["cm_cas"]
    assert rez["CAM — contribuția asiguratorie pentru muncă (2,25%), plătită de angajator"]["valoare"] == r["cam"]
    assert rez["Total disponibil"]["valoare"] == r["total_disponibil"]
    cm = [x for x in c["venituri"] if x["eticheta"].startswith("Indemnizație")]
    assert len(cm) == 1 and (cm[0]["valoare"], cm[0]["net"]) == (r["cm_brut"], r["cm_net"])
    assert ven["Salariu pe zile lucrate"]["detaliu"] == "19 zile lucrate din 22"
    toate = [x["eticheta"] for col in c.values() for x in col]
    assert not any(e.startswith("Zile de concediu medical") for e in toate)
    ore = next(x for x in c["venituri"] if x["eticheta"].startswith("Ore suplimentare"))
    assert ore["detaliu"] == "10 ore × 28,41 lei × 175%" and ore["valoare"] == 497.16
    # aceleași cifre ca fluturașul (compozitie_fluturas, care rămâne sursa hârtiei)
    flut = {x["eticheta"]: x["valoare"] for x in sp.compozitie_fluturas(r)}
    assert flut["Net de plată (salariu + indemnizație CM)"] == r["net_de_plata"]
