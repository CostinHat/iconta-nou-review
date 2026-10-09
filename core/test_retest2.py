# -*- coding: utf-8 -*-
"""GARDA lotului „Retest 2” (comanda Costin 09.10.2026, verbatim în DECIZII) — retestul în aplicație al lotului „Retest 08.10”.

Fiecare test numește punctul din comandă, citează fraza lui Costin și mutația care îl face roșu. Schema efemeră din
`tenant_template.sql`, ștearsă la ieșire; date în 2099. Nimic în tabele partajate în afara rândurilor de coadă ale schemei efemere
(tenant_id sintetic, șterse la ieșire).
"""
import datetime
import io
import re
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_retest2"
TENANT_SINTETIC = 990000002   # rândurile de coadă ale schemei efemere; șterse la ieșire


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def lume():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, tip_decont) "
                        "VALUES (1, 'RETEST DOI SRL', 'RO14399840', true, 'L')" % SCH)
        c.commit()
    yield SCH
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute("DELETE FROM public.declaratii_coada WHERE tenant_id = %s", (TENANT_SINTETIC,))
        c.commit()


def _nota(cur, data, linii, status="validata", sursa="jurnal", autor=None, descriere="n"):
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, creat_de_id, document_ref) VALUES (%s, %s, %s, %s, %s, 'NC n') "
                "RETURNING id", (data, descriere, sursa, status, autor))   # [09.10.2026, regulile de fond R3] nota validată are documentul justificativ
    nid = cur.fetchone()[0]
    for d, c, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
                    (nid, d, c, Decimal(str(s))))
    return nid


# ── pct.1 (A1) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct1_marcarea_reincarca_pe_pozitie():
    """„După «Salvează» sau «Anulează marcarea» grupul «Înainte de preluare» rămâne cum l-a lăsat omul, iar ecranul rămâne pe rândul
    atins.” Ambele acte reîncarcă prin `reincarcaPePozitie` (care ține minte grupurile deschise și rândul atins), nu prin redesenarea
    de la zero. MUTAȚIE: un handler înapoi pe `reincarca(corp, firma)` -> pică. Proba pe ecran: captura a1 din raport."""
    js = io.open("static/js/ecrane/control_verdict.js", encoding="utf-8").read()
    assert re.findall(r"async function (reincarcaPePozitie)\(corp, firma, atins\)", js) == ["reincarcaPePozitie"]
    acte = dict(re.findall(r"api\.post\(`/control-fiscal/\$\{firma\.tenant_id\}(/depusa-extern(?:/anuleaza)?)`[^;]*;\s*await (\w+)\(corp, firma, b\)", js))
    assert acte == {"/depusa-extern": "reincarcaPePozitie", "/depusa-extern/anuleaza": "reincarcaPePozitie"}, acte


# ── pct.2 (A2) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("text,fel", [
    ("Categorie: incasare_client", "cod"),                 # enumerare afișată brut
    ("Metoda: liniara", "diacritice"),
    ("Total sume 1000.00", "suma"),
    ("Operațiune din 2026-08-14", "data"),
    ("Perioada 03.2026", "perioada"),
    ("Trimestrul T3", "perioada"),
    ("1 parteneri TVA RO", "acord"),
    ("2 fact.vânz", "abreviere"),
    ("Refacere NIR 2 (decizia Costin 08.10, pct.4)", "cod"),
    ("rânduri persistate", "jargon"),
    ("sold DEBITOR", "majuscule"),
    ("locul prestării în afară României", "diacritice"),
])
def test_pct2_limba_ecranului_prinde_fiecare_exemplu_din_comanda(text, fel):
    """„Pct.14 nu e închis. […] verificarea se face pe ecranul afișat, cu valorile din date și din enumerări”. Fiecare exemplu numit
    de Costin e prins de `core/limba_ecran.py` cu felul lui. MUTAȚIE: un detector scos din `defecte` -> cazul lui pică."""
    from core.limba_ecran import defecte
    assert fel in [f for f, _ in defecte(text)], (text, defecte(text))


def test_pct2_proza_corecta_si_datele_omului_trec():
    from core.limba_ecran import defecte
    for t in ("Sold inițial 1.000,00 lei la 31.07.2026", "D300 pentru 08/2026, T3/2026, anul 2026", "1 partener · 3 parteneri",
              "Conform CF art.146 alin.(5), OMFP 1802/2014 pct.69", "nimeni în afară de contabil"):
        assert not defecte(t), (t, defecte(t))
    assert not defecte("Client: ALFA_BETA SRL", date_excluse={"ALFA_BETA SRL"}), "numele introdus de om nu e textul aplicației"


def test_pct2_diferentele_de_reconciliere_sunt_in_cuvinte():
    """„generator=9999 vs cale2=1500” nu mai ajunge pe ecran: `pdf_util.diferenta` e sursa unică a celor nouă porți.
    MUTAȚIE: formatul vechi înapoi într-o poartă -> testul porții ei pică (test_d*_reconciliere)."""
    from core.pdf_util import diferenta
    from core.limba_ecran import defecte
    s = diferenta("colectat 21%, TVA", 9999, 1500, 8499)
    assert s == "colectat 21%, TVA: în declarație 9.999,00 lei, recalculat 1.500,00 lei (diferență 8.499,00 lei)"
    assert not defecte(s)
    for p in ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406"):
        src = io.open("core/%s_reconciliere.py" % p, encoding="utf-8").read()
        assert "cale2=" not in re.sub(r"#.*", "", src).replace('"cale2"', ""), p


def test_pct2_notele_de_refacere_nir_se_rescriu_si_se_retrimit(lume):
    """„Notele 121/122 se refac cu descrierea în limbaj de contabil și se retrimit la validare.” Pe o notă de refacere NIR cu
    proveniența internă în descriere și respinsă în coadă: descrierea se rescrie din sursa unică, iar nota intră din nou `la_senior`.
    MUTAȚIE: retrimiterea scoasă din `note_refacere_nir` -> starea rămâne `respinsa` -> pică."""
    from core import coada_api, migrare_retest2 as m
    from core.migrare_retest_0810 import descriere_refacere_nir
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO nir (numar, data, furnizor) VALUES ('2', '2099-10-07', 'F') RETURNING id")
            nir_id = cur.fetchone()[0]
            nid = _nota(cur, "2099-10-07", [("371", "401", -100), ("371", "408", 100)], status="ciorna", sursa="stocuri",
                        descriere="Refacere NIR 2 pe 408 / 4428.01 (decizia Costin 08.10, pct.4): stornarea costului")
            cur.execute("UPDATE inregistrari SET numar = %s WHERE id = %s", ("REFACERE-NIR-%d" % nir_id, nid))
            cur.execute("SELECT id FROM public.accounting_firms ORDER BY id LIMIT 1")
            cab = cur.fetchone()[0]
            cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, fel, perioada, stare, payload, hash, creat_de, "
                        "creat_de_id, motiv_respingere) VALUES (%s, %s, %s, 'nota', %s, 'respinsa', '{}'::jsonb, 'h', '1', 1, 'descriere')",
                        (cab, TENANT_SINTETIC, coada_api.TIP_NOTA, coada_api.perioada_nota(nid)))
        conn.commit()
        rez = m.note_refacere_nir(conn, SCH, TENANT_SINTETIC, cab)
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT descriere FROM inregistrari WHERE id = %s", (nid,))
            desc = cur.fetchone()[0]
            cur.execute("SELECT stare FROM public.declaratii_coada WHERE tenant_id = %s ORDER BY id DESC LIMIT 1", (TENANT_SINTETIC,))
            stare = cur.fetchone()[0]
    assert desc == descriere_refacere_nir("2") and "decizia Costin" not in desc
    assert stare == "la_senior", rez
    with _db.get_conn(SCH) as conn:
        assert m.note_refacere_nir(conn, SCH, TENANT_SINTETIC, cab) == [], "a doua rulare nu mai găsește nimic"


# ── pct.3 (A3) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct3_contoarele_pe_o_singura_regula():
    """„Contoarele de sus folosesc două reguli […] Una dintre reguli, aplicată peste tot.” Fiecare contor = firmele care AU faptul;
    o firmă cu restanță și un necunoscut intră în amândouă; „la zi” = fără niciun fapt. MUTAȚIE: „nu se pot verifica” înapoi pe
    starea principală gri -> F1 (roșie, cu 2 necunoscute) iese din contor -> pică."""
    from core.uc_control_fiscal import contoare_portofoliu
    firme = [{"stare": "rosu", "lipsa": 1, "urmarit": 0, "neclar": 2, "contabil": []},                 # F1: restanță + necunoscut
             {"stare": "galben", "lipsa": 0, "urmarit": 3, "neclar": 0, "contabil": [{"stare": "rosu"}]},
             {"stare": "verde", "lipsa": 0, "urmarit": 0, "neclar": 0, "contabil": [{"stare": "gri"}]},
             {"stare": "verde", "lipsa": 0, "urmarit": 0, "neclar": 0, "contabil": [], "prospetime": {"stare": "veche"}},
             {"stare": "verde", "lipsa": 0, "urmarit": 0, "neclar": 0, "contabil": [{"stare": "verde"}]}]
    assert contoare_portofoliu(firme) == {"restante": 1, "de_urmarit": 1, "neconcordante": 1, "nu_se_pot_verifica": 3, "la_zi": 1}


# ── pct.4 (B4) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct4_operatiunea_cu_nota_validata_nu_se_sterge_se_storneaza(lume):
    """„O operațiune de casă cu notă validată nu trebuie să se poată șterge; corectarea se face prin stornare.” OMFP 1802/2014 pct.69
    (corectarea cu semnul minus). MUTAȚIE: refuzul din `casa_api.sterge` scos -> operațiunea dispare -> pică."""
    from core import casa_api as ca
    with _db.get_conn(SCH) as conn:
        r = ca.adauga(conn, SCH, {"data": "2099-08-14", "categorie": "incasare_client", "suma": 500, "document": "CH 7", "partener": "X"})
        with conn.cursor() as cur:
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (r["inregistrare_id"],))
        s = ca.sterge(conn, SCH, r["id"])
        assert s["eroare"].startswith("Nota operațiunii e validată, deci operațiunea nu se mai șterge: se corectează prin stornare")
        st = ca.storneaza(conn, SCH, r["id"], "2099-08-20")
        with conn.cursor() as cur:
            cur.execute("SELECT suma, storno_de, document FROM casa_operatiuni WHERE id = %s", (st["id"],))
            op = cur.fetchone()
            cur.execute("SELECT status FROM inregistrari WHERE id = %s", (st["inregistrare_id"],))
            stare = cur.fetchone()[0]
            cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s", (st["inregistrare_id"],))
            linii = cur.fetchall()
        assert (op[0], op[1], op[2]) == (Decimal("-500"), r["id"], "STORNO CH 7")
        assert stare == "ciorna" and linii == [("5311", "4111", Decimal("-500.00"))]
        assert ca.storneaza(conn, SCH, r["id"], "2099-08-21") == {"eroare": "Operațiunea e deja stornată."}
        conn.rollback()


def test_pct4_aceeasi_regula_pe_toate_sursele_de_note():
    """„Aceeași regulă pentru toate sursele de note.” Celelalte surse refuzau deja ștergerea unei note validate: jurnalul, banca,
    factura (contarea) — se verifică textul refuzului la sursă. Casa era singura care ștergea nota validată odată cu operațiunea."""
    surse = {"core/jurnal_api.py": "validat", "core/casa_api.py": "se corectează prin stornare"}
    for fn, frag in surse.items():
        assert frag in io.open(fn, encoding="utf-8").read(), fn


# ── pct.5 (B5) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct5_amortizarea_pana_la_ultima_luna_incheiata():
    """„Calculul merge până la ultima lună încheiată, aceeași regulă ca la închiderea lunii.” MUTAȚIE: `ultima_zi_incheiata`
    întoarce azi -> 31.10 în loc de 30.09 -> pică."""
    from core.inchidere_luna import ultima_zi_incheiata, luna_in_curs
    assert ultima_zi_incheiata(datetime.date(2026, 10, 9)) == datetime.date(2026, 9, 30)
    assert ultima_zi_incheiata(datetime.date(2026, 1, 1)) == datetime.date(2025, 12, 31)
    assert luna_in_curs(2026, 10) and not luna_in_curs(2026, 9)   # aceeași frontieră ca închiderea


# ── pct.6-7 (B6, B7) ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct6_jurnal_totalurile_numai_pe_validat(lume, monkeypatch):
    """„Totalurile registrului se fac numai pe notele validate; ciornele se arată separat.” MUTAȚIE: totalul pe toate notele -> pică."""
    from core import uc_tenants
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            _nota(cur, "2099-08-10", [("401", "5121", 300)])
            _nota(cur, "2099-08-11", [("6022", "401", 50)], status="ciorna")
        conn.commit()
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant_citire", lambda conn, uid, tid: SCH)
    r = uc_tenants.tenant_jurnal(1, 2099, 8, {"uid": 1, "firm": 1, "rol": "admin_firma"})
    assert (r["total_debit"], r["ciorne"]) == (300.0, {"note": 1, "total": 50.0})


def test_pct7_nota_de_validat_arata_rulajul(lume):
    """„Note de validat: arată rulajul notei, nu «total 0,00».” O notă de stornare + înregistrare (−100 / +100) are totalul 0, dar
    rulajul pe cele două părți. MUTAȚIE: `rulaj` scos din `_SELECT_NOTE` -> ecranul cade pe total -> pică."""
    import psycopg2.extras as _E
    from core import coada_api
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            nid = _nota(cur, "2099-08-10", [("371", "401", -100), ("371", "408", 100)], status="ciorna")
        with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
            cur.execute(coada_api._SELECT_NOTE + "WHERE i.id = %s", (nid,))
            n = cur.fetchone()
        conn.rollback()
    assert (n["total"], n["rulaj_storno"], n["rulaj"]) == (0, 100, 100)
    js = io.open("static/js/ecrane/validat.js", encoding="utf-8").read()
    assert re.findall(r"function (rulajNota)\(n\)", js) == ["rulajNota"]


# ── pct.9-10 (B9, B10) ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct9_d390_neplatitor_numai_lunile_cu_operatiuni_si_temeiul():
    """„Restanțele D390 arată pe ce se bazează (lunile cu operațiuni intracomunitare), ca D301.” Temei: OPANAF 705/2020 anexa 2
    pct.1.2 („depun declaraţia recapitulativă numai pentru lunile calendaristice în care ia naştere exigibilitatea taxei”).
    MUTAȚIE: callback-ul ignorat (toate lunile) -> apar și alte luni decât 08 -> pică."""
    from core.control_fiscal_api import obligatii_datorate
    vector = {"regim_fiscal": "micro", "platitor_tva": False, "tip_decont": None, "operatiuni_ic": True, "inreg_art317": True,
              "tip_firma": "SRL"}
    r = obligatii_datorate(vector, False, datetime.date(2026, 10, 9), d390_fapt=lambda a, m: None,
                           d390_luni_neplatitor=lambda a: {8} if a == 2026 else set())
    d390 = [d for d in r["datorate"] if d["tip"] == "d390"]
    assert [(d["an"], d["luna"]) for d in d390] == [(2026, 8)], d390
    assert d390[0]["fapt"] == "operațiuni intracomunitare înregistrate în 08/2026"


def test_pct9_d300_nu_se_aplica_la_neplatitor_si_se_spune(lume):
    """„F3 (neplătitor, D301): «D390 față de D300» arată «nu se aplică».” Verdictul îl spune, iar ecranul îl randează.
    MUTAȚIE: `nu_se_aplica` scos din verdictul neplătitorului -> pică."""
    from core import control_incrucisat as ci
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE firma_profil SET platitor_tva = false WHERE id = 1")
        r = ci.verifica_tva(conn, SCH, 2099, 8)
        conn.rollback()
    assert r["nu_se_aplica"] == ["D300 față de contabilitate: nu se aplică — firma nu e plătitoare de TVA, deci nu depune decontul D300."]
    js = io.open("static/js/ecrane/control_verdict.js", encoding="utf-8").read()
    assert re.findall(r"=> v\.(nu_se_aplica) \|\| \[\]", js) == ["nu_se_aplica"]


def test_pct10_inainte_de_preluare_cu_termen_perioada_si_rand():
    """„D100 / D406 / D205 au «termen» fără dată, n-au perioada pe rând și n-au buton individual de marcare.” Domeniul D205 pe 2025
    se desface în perioada lui (anul), cu termenul (ultima zi a lui februarie) și luna de marcare. MUTAȚIE: `termen` scos -> pică."""
    from core.control_fiscal_api import separa_neclar_inainte_de_preluare
    neclar = [{"tip": "d205", "domeniu_de": "2025-01", "domeniu_pana": "2025-12", "motiv": "nu pot verifica"},
              {"tip": "d100", "domeniu_de": "2025-01", "domeniu_pana": "2025-06", "motiv": "x"}]
    ramase, inainte = separa_neclar_inainte_de_preluare(neclar, (2026, 9))
    assert ramase == []
    d205 = [x for x in inainte if x["tip"] == "d205"]
    from core import scadente
    # 28.02.2026 e sâmbătă: termenul trece pe prima zi lucrătoare (aceeași funcție de scadență ca restul semaforului)
    assert [(x["perioada"], x["termen"], x["luna"]) for x in d205] == [("2025", scadente.scadenta_data("d205", 2025).isoformat(), 12)]
    assert d205[0]["termen"] == "2026-03-02"
    assert [x["perioada"] for x in inainte if x["tip"] == "d100"] == ["T1/2025", "T2/2025"]


# ── pct.11 (B11) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct11_declaratia_nedepusa_cu_termen_in_luna_e_avertisment(monkeypatch):
    """„O declarație care are termenul în luna respectivă și nu e depusă apare ca avertisment.” Restanța D300 pentru 08/2026, cu
    termen 25.09.2026, apare la închiderea lui 09/2026; cea cu termen în octombrie nu. MUTAȚIE: filtrul pe termen scos -> pică."""
    from core import uc_comun, control_fiscal_api as cf

    class _C:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def cursor(self): return self
        def execute(self, *a): pass
        def fetchone(self): return (1, 1)
    monkeypatch.setattr(uc_comun.db, "get_conn", lambda *a, **k: _C())
    monkeypatch.setattr(cf, "evalueaza_firma", lambda *a, **k: {
        "lipsa": [{"tip": "d300", "an": 2026, "luna": 8, "perioada": "08/2026", "termen": "2026-09-25"}],
        "urmarit": [{"tip": "d112", "an": 2026, "luna": 9, "perioada": "09/2026", "termen": "2026-10-25"}]})
    r = uc_comun.declaratii_nedepuse_cu_termen_in_luna("x", 2026, 9, azi=datetime.date(2026, 10, 9))
    assert r == [("d300", "D300 pentru 08/2026, cu termen pe 25.09.2026, nu e depusă — depune-o sau marchează-o depusă în Control fiscal")]


# ── pct.12 (B12) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct12_ciornele_proprii_se_vad(lume):
    """„Ciornele proprii ale contabilului trebuie să fie vizibile undeva fără căutare.” Numai notele lui, numai ciornele, cu starea din
    coadă. MUTAȚIE: filtrul pe autor scos -> apare și nota altcuiva -> pică."""
    from core import coada_api
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            a = _nota(cur, "2099-08-10", [("6022", "401", 70)], status="ciorna", autor=7, descriere="a mea")
            _nota(cur, "2099-08-10", [("6022", "401", 80)], status="ciorna", autor=8, descriere="a altuia")
            _nota(cur, "2099-08-10", [("6022", "401", 90)], status="validata", autor=7, descriere="validată")
        r = coada_api.ciorne_proprii(conn, TENANT_SINTETIC, 7)
        conn.rollback()
    assert [(n["id"], n["descriere"], n["rulaj"], n["in_coada"]) for n in r] == [(a, "a mea", 70.0, None)]
    for fn in ("static/js/ecrane/validat.js", "static/js/ecrane/cabinet.js"):
        assert re.findall(r'api\.get\("(/eu/ciorne)"\)', io.open(fn, encoding="utf-8").read()) == ["/eu/ciorne"], fn


# ── pct.13 (B13) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct13_planul_de_conturi_analitice_sub_sintetic_si_stergerea(lume, monkeypatch):
    """Decizia Costin O12: „listă cu căutare după cont sau denumire, analiticele afișate sub contul sintetic, adăugare de analitic de
    către contabil, iar un cont folosit în note nu se poate șterge”. MUTAȚIE: verificarea `conturi_folosite` scoasă din
    `tenant_plan_conturi_sterge` -> contul folosit se șterge -> pică."""
    from core import uc_tenants as ut, erori
    assert (ut.sintetic_al("4111.01"), ut.sintetic_al("401_7"), ut.sintetic_al("4111")) == ("4111", "401", None)
    monkeypatch.setattr(ut._uc_comun, "_schema_sau_404", lambda ctx, tid: SCH)
    ctx = {"uid": 1, "firm": 1}
    ut.tenant_plan_conturi_adauga(1, type("D", (), {"simbol": "4111.01", "denumire": "Clienți interni", "tip": "Activ"}), ctx)
    ut.tenant_plan_conturi_adauga(1, type("D", (), {"simbol": "4111.02", "denumire": "Clienți externi", "tip": "Activ"}), ctx)
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            _nota(cur, "2099-08-10", [("4111.01", "707", 10)])
        conn.commit()
    for gresit in ("4111.", "4111..01", "4111.01.", "41110000001"):
        with pytest.raises(erori.DateInvalide):                                            # prins la proba din ecran: „4111.” trecea
            ut.tenant_plan_conturi_adauga(1, type("D", (), {"simbol": gresit, "denumire": "x", "tip": "Activ"}), ctx)
    lista = {c["simbol"]: c for c in ut.tenant_plan_conturi_lista(1, None, ctx)["conturi"]}
    assert len(lista) > 100, "tot planul, nu primele 100"
    assert (lista["4111.01"]["sintetic"], lista["4111.01"]["folosit"], lista["4111.02"]["folosit"]) == ("4111", True, False)
    with pytest.raises(erori.Conflict, match="apare în note contabile"):
        ut.tenant_plan_conturi_sterge(1, "4111.01", ctx)
    with pytest.raises(erori.Conflict, match="are analitice în plan"):
        ut.tenant_plan_conturi_sterge(1, "4111", ctx)
    assert ut.tenant_plan_conturi_sterge(1, "4111.02", ctx) == {"ok": True, "simbol": "4111.02"}
    js = io.open("static/js/ecrane/firme.js", encoding="utf-8").read()
    assert re.findall(r'cheie: "(planconturi)", regim: "(\w+)", grup: "(\w+)"', js) == [("planconturi", "dubla", "firma")]
    assert re.findall(r'nav\.deschide\("Plan de conturi", \(c2\) => (\w+)\(c2, nav, t\)\)', js) == ["ecranPlanConturi"]


# ── pct.14 (B14) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct14_confirmarea_respingerii_numeste_nota_scurt():
    """„Confirmarea respingerii repetă tot titlul notei.” Confirmarea folosește `numeScurt` (documentul sau data), nu eticheta
    întreagă. MUTAȚIE: `c.eticheta` înapoi în confirmare -> pică."""
    js = io.open("static/js/ecrane/validat.js", encoding="utf-8").read()
    assert re.findall(r"`Ai respins \$\{(\w+)\(c\)\}", js) == ["numeScurt"]   # nota; declarația își numește tipul și perioada
    assert re.findall(r"Motivul respingerii pentru \$\{esc\((\w+)\(c\)\)\}", js) == ["numeScurt"]   # și dialogul de respingere


def test_pct14_numeralul_acordat():
    """„«1 parteneri» în Rezumat D394.” `common.cate` acordă numeralul (cu „de” de la 20)."""
    from core.common import cate
    assert [cate(n, "partener", "parteneri") for n in (1, 2, 19, 20, 101, 120)] == [
        "1 partener", "2 parteneri", "19 parteneri", "20 de parteneri", "101 parteneri", "120 de parteneri"]


# ── pct.15-16 (C15, C16) ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct15_factura_cu_doua_cote_se_numara_o_data_si_se_spune():
    """„Rândul 11% arată «număr facturi 0», deși factura 2 are o linie de 11%.” OPANAF 2194/2025, instrucțiuni, secțiunea a 2-a pct.5:
    „Prin excepţie, în situaţia în care în cuprinsul unei facturi emise/primite există operaţiuni cu cote de TVA diferite, la rubrica
    «număr de facturi» se vor înscrie: valoarea 1 în dreptul operaţiunii cu valoarea cea mai mare a TVA şi valoarea 0 pentru restul
    operaţiunilor”. Deci 0 e corect; nou e că ecranul o spune. MUTAȚIE: nota din `sinteza` scoasă -> pică."""
    from core import d394
    from core.common import Perioada
    prof = {"cui": "14399840", "nume": "RETEST DOI SRL", "platitor_tva": True, "tip_decont": "L"}
    comun = {"cui": "RO14399840", "nume": "ALFA SRL", "directie": "emisa", "taxare_inversa": False, "platitor_tva": True,
             "factura_id": 2, "document": "FCT2", "cote_factura": [11, 21], "cota_numarata": 21}
    facturi = [dict(comun, cota=11, baza=Decimal(100), tva=Decimal(11), nrFact=0),
               dict(comun, cota=21, baza=Decimal(100), tva=Decimal(21), nrFact=1)]
    res = d394.calcul_d394(prof, Perioada(2099, luna=8), {"facturi": facturi, "serii": []})
    nr = {k[2]: v[0] for k, v in res.op1.items()}
    assert nr == {11: 0, 21: 1}
    assert any(s.startswith("Factura FCT2 are operațiuni pe cotele 11%, 21%: se numără o singură dată, la cota cu TVA-ul cel mai "
                            "mare (21%); la 11% apare cu 0 facturi") for s in res.sinteza), res.sinteza


def test_pct16_codul_tva_cu_ro_in_antetul_raportului():
    """„CUI fără «RO» în antetul PDF-ului balanței, la plătitorul de TVA.” CF art.318 alin.(1): „Codul de înregistrare în scopuri de
    TVA, atribuit conform art. 316 și 317, are prefixul RO”. MUTAȚIE: `platitor_tva` ignorat în `antet_raport` -> pică."""
    from core.documente_api import antet_raport
    t = datetime.datetime(2026, 10, 9, 10, 0)
    assert antet_raport("F2 SRL", "14399840", t, platitor_tva=True) == "F2 SRL · Cod TVA RO14399840 — Generată la 09.10.2026 10:00"
    assert antet_raport("F3 SRL", "14399840", t, platitor_tva=False) == "F3 SRL · CIF 14399840 — Generată la 09.10.2026 10:00"


# ── găsit la proba „după” (09.10): verificarea TVA pe perioada decontului ───────────────────────────────────────────────────
def test_verificarea_tva_la_trimestrial_genereaza_decontul_trimestrului(lume):
    """La firma cu decont trimestrial, luna 10 e în T4, al cărui decont poartă eticheta 12. Generat pe luna 10, D300 cădea în
    DUK regula R18 („Decontul trimestrial se depune pentru una din lunile …”) și firma apărea „nu se poate verifica” în fiecare lună
    din mijlocul trimestrului (13 firme gri pe cabinetul de test). MUTAȚIE: generarea înapoi pe `Perioada(an, luna=luna)` -> pică."""
    from core import control_incrucisat as ci
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE firma_profil SET tip_decont = 'T', banca = 'ING Bank', iban = 'RO63INGB0000999910907330', caen = '6202', "
                        "declarant_nume = 'Popescu', declarant_prenume = 'Ion', declarant_functie = 'ADMINISTRATOR', adresa = 'Str. A 1', "
                        "judet = 'B', oras = 'Bucuresti' WHERE id = 1")
        r = ci.verifica_tva(conn, SCH, 2099, 10)
        conn.rollback()
    regula_r18 = [c for c in r.get("constatari") or [] if re.search(r"R18|Decontul trimestrial se depune", str(c.get("mesaj")))]
    assert regula_r18 == [], regula_r18


def test_pct4_ruta_de_stornare_scrie_in_luna_deschisa(lume, monkeypatch):
    """Ruta `POST …/casa/operatiuni/{op_id}/storneaza` (use-case `casa_storneaza`): stornarea se scrie, pe nota validată; pe una
    ciornă se refuză cu motivul (se șterge, nu se stornează). MUTAȚIE: `_c.storneaza` ocolit -> nimic scris -> pică."""
    from core import casa_api as ca, uc_tenants as ut, erori
    monkeypatch.setattr(ut.auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    with _db.get_conn(SCH) as conn:
        r = ca.adauga(conn, SCH, {"data": "2099-08-14", "categorie": "incasare_client", "suma": 300, "document": "CH 9"})
        c = ca.adauga(conn, SCH, {"data": "2099-08-15", "categorie": "incasare_client", "suma": 40, "document": "CH 10"})
        with conn.cursor() as cur:
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (r["inregistrare_id"],))
    rez = ut.casa_storneaza(1, r["id"], {"data": "2099-08-20"}, {"uid": 1, "firm": 1})
    with pytest.raises(erori.CerereGresita, match="se șterge, nu se stornează"):
        ut.casa_storneaza(1, c["id"], {"data": "2099-08-20"}, {"uid": 1, "firm": 1})
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT suma, storno_de FROM casa_operatiuni WHERE id = %s", (rez["id"],))
            assert cur.fetchone() == (Decimal("-300.00"), r["id"])


def test_pct2_componentele_declaratiei_in_cuvinte():
    """„Din ce e făcută declarația” nu mai arată codurile fișierului: rândul D300 e rândul formularului, tipul D394 / D390 e cuvântul
    din legenda formularului, jurnalul D406 e numele lui. MUTAȚIE: `cheie_om` / `chei_om` scoase din hartă -> codurile -> pică."""
    from types import SimpleNamespace as NS
    from core.declaratii_componente import componente
    r = componente("d300", NS(R={"R17_2": 210, "R26_1": 0}))["sectiuni"][0]["randuri"]
    assert r == [{"rând": "rândul 19, coloana TVA", "valoare": 210}]
    r = componente("d394", NS(op1={("C", 1, 21, "95141537", "ALFA"): [1, 8000, 1680]}, serii=[{"tip": 2, "serieI": "-", "nrI": 4, "nrF": 4}]))
    assert r["sectiuni"][0]["randuri"][0]["tip"] == "achiziții cu taxare inversă"
    assert (r["sectiuni"][0]["randuri"][0]["tip partener"], r["sectiuni"][0]["randuri"][0]["cotă"]) == (
        "înregistrat în scopuri de TVA în România", "21%")
    assert r["sectiuni"][1]["randuri"][0]["tip"] == "facturi emise"
    r = componente("d390", NS(ops={("A", "DE", "DE123", "GMBH"): 1500}))["sectiuni"][0]["randuri"]
    assert r[0]["tip"] == "achiziții intracomunitare de bunuri"
