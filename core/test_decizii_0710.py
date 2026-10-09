# -*- coding: utf-8 -*-
"""GARDA lotului „Deciziile 07.10” + retestul Costin pe F1 (comenzile din 07.10.2026, verbatim în DECIZII).

  D1  combinațiile de stoc nesuportate se refuză clar la setarea firmei („nesuportat încă”); restanța e în test_datorie.
  D2  NIR legat de factura primită, la global-valoric: numai 371=378 și 371=4428, costul vine din factură.
  D4  salariatul pe API și la import: funcția de bază, scutirea de contribuția minimă și norma se cer explicit.
  D5  seria chitanței: fără „CH” din oficiu; cerută la prima chitanță.
  R1  respingerea unui document cu mișcare de stoc o stornează în fișă (în roșu, cu valoarea ei); documentul se reface.

Testele cu coada rulează într-o SINGURĂ tranzacție anulată la final (scriu în `public.tenants` / `public.declaratii_coada`,
tabele partajate — CLAUDE.md: fixture pe tabel partajat = rollback); datele sunt în 2099, perioadă evident sintetică.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_decizii_0710"
_L = {"cantitate": 10, "pret_achizitie": 55, "cota_tva": 21}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def tx():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email='asistent@prisma-cont.test'")
    r = cur.fetchone()
    if not r:
        p.putconn(conn)
        pytest.skip("utilizatorul de test lipsește")
    asist, cab = r
    cur.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s AND poate_valida AND id<>%s ORDER BY id LIMIT 1",
                (cab, asist))
    valid = cur.fetchone()[0]
    cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false WHERE id=%s", (asist,))
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO %s.firma_profil (id, nume, cui) VALUES (1, 'DECIZII SRL', '14399840')" % SCH)
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Decizii 07.10',%s) "
                "RETURNING id", (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET search_path TO "%s", public' % SCH)
    try:
        yield conn, cur, tid, cab, asist, valid
    finally:
        conn.rollback()
        cur = conn.cursor()
        cur.execute("RESET iconta.utilizator")
        cur.execute("RESET search_path")
        conn.commit()
        p.putconn(conn)


def _ca(cur, uid):
    cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(uid),))


def _metoda(cur, m):
    cur.execute("UPDATE firma_profil SET metoda_stoc = %s", (m,))


def _note(cur, ids):
    cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = ANY(%s) ORDER BY id",
                (list(ids),))
    return [tuple(x) for x in cur.fetchall()]


def _factura_primita(cur, net="550.00", tva="115.50", numar="FP1"):
    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, total_lei, tva_lei, tert_nume, tert_cui) "
                "VALUES (%s, '2099-10-07', 'primita', %s, %s, %s, %s, 'DANTE INTERNATIONAL SA', '14399840') RETURNING id",
                (numar, Decimal(net) + Decimal(tva), tva, Decimal(net) + Decimal(tva), tva))
    return cur.fetchone()[0]


def _stoc(cur, articol="Marfa A"):
    from core import repo_stocuri, stocuri_cv
    cur.execute("SELECT id FROM articole WHERE denumire = %s", (articol,))
    aid = cur.fetchone()[0]
    import psycopg2.extras as _E
    with cur.connection.cursor(cursor_factory=_E.RealDictCursor) as c2:
        f = stocuri_cv.fisa_magazie(repo_stocuri.miscari_ale_articolului(c2, SCH, aid))
    return (str(f[-1]["sold_cantitate"]), str(f[-1]["sold_valoare"])) if f else ("0", "0.00")


# ── D1 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_d1_metoda_nesuportata_se_refuza_la_setarea_firmei(tx):
    """Decizia pct.1: „Combinațiile nesuportate se refuză clar la setarea firmei («nesuportat încă»)”. MUTAȚIE: ramura
    `NESUPORTATE` scoasă din `salveaza_date` -> metoda se salvează -> pică."""
    from core import firma_profil_api as fp, metoda_stoc as ms
    conn, cur, tid, cab, asist, valid = tx
    assert set(ms.NESUPORTATE) == {"cantitativ_valoric_pret_vanzare", "cantitativ_valoric_fifo"}   # decizia pct.1, numit
    for m in ms.NESUPORTATE:
        r = fp.salveaza_date(conn, {"metoda_stoc": m}, tenant_id=tid, user_id=asist)
        assert (r.get("ok"), r.get("cod"), r.get("camp")) == (False, ms.COD_NESUPORTATA, "metoda_stoc"), r
    cur.execute("SELECT metoda_stoc FROM firma_profil")
    assert cur.fetchone()[0] is None


# ── D4 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_d4_salariatul_pe_api_cere_cele_trei_fapte_numite():
    """Decizia pct.4: „functie_baza, scutit_contrib_minim și tip_norma se cer explicit; un rând fără ele se refuză cu câmpul
    numit” (funcția de bază: CF art.77 alin.(1) — deducerea personală numai la funcția de bază). MUTAȚIE: verificarea
    `functie_baza` scoasă din `valideaza_salariat` -> pică."""
    from core import salariati_api as sa
    baza = {"nume": "POP", "prenume": "I", "cnp": "1900101410011", "data_angajare": "2099-01-01", "salariu_brut": 5000,
            "cor": "522101"}
    er = sa.valideaza_salariat(baza, la_creare=True)
    txt = str(er)
    for nume in ("Tipul normei", "Funcția de bază", "Scutirea de contribuția minimă"):
        assert nume in txt, txt


def test_d4_importul_refuza_randul_fara_cele_trei_cu_coloana_numita():
    """MUTAȚIE: regula `functie_baza_lipsa` scoasă din `verifica_randuri` -> pică."""
    from core import salariati_import_api as si
    rand = {"nume": "POP", "prenume": "I", "cnp": "1900101410011", "cnp_valid": True, "data_angajare": "2099-01-01",
            "salariu_brut": 5000, "judet_casa": "B", "cor": "522101", "tip_norma": "partiala", "ore_zi": None,
            "functie_baza": None, "scutit_contrib_minim": None}
    reguli = {e.get("regula") for e in si.verifica_randuri([rand])}
    assert {"functie_baza_lipsa", "scutire_minim_lipsa", "ore_lipsa"} <= reguli, reguli
    r = si.extrage(b"nume,prenume,cnp,data angajare,norma,brut\nPOP,I,1900101410011,2099-01-01,partiala,5000\n", "x.csv")[0]
    assert (r["functie_baza"], r["scutit_contrib_minim"], r["ore_zi"] or None) == (None, None, None)   # nimic presupus


# ── D5 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_d5_seria_chitantei_fara_implicit_si_ceruta_la_prima_chitanta(tx):
    """Decizia pct.5: „Seria chitanței: cerută la prima folosire, ca seria facturii; fără «CH» din oficiu.” Temei: OMFP
    2634/2015 anexa 1 pct.24 — numărul sau seria „stabilit(ă) de entitate”. MUTAȚIE: `COALESCE(serie_chitanta,'CH')` pus
    înapoi în `seria_chitantei` -> pică."""
    from core import repo_firma_profil
    conn, cur, *_ = tx
    cur.execute("SELECT column_default FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil' "
                "AND column_name='serie_chitanta'", (SCH,))
    assert cur.fetchone()[0] is None
    assert (repo_firma_profil.seria_chitantei(cur, SCH) or (None,))[0] is None
    from core import firma_profil_api as fp
    tid, asist = tx[2], tx[4]
    r = fp.salveaza_date(conn, {"serie_chitanta": "ch 1"}, tenant_id=tid, user_id=asist)       # numai litere și cifre
    assert (r.get("ok"), r.get("camp")) == (False, "serie_chitanta"), r
    r = fp.salveaza_date(conn, {"serie_chitanta": "chf"}, tenant_id=tid, user_id=asist)
    assert r.get("ok") is not False, r
    assert repo_firma_profil.seria_chitantei(cur, SCH)[0] == "CHF"


# ── D2 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_d2_nir_legat_scrie_numai_adaosul_si_tva_neexigibila(tx):
    """Decizia pct.2: „NIR-ul legat scrie numai adaosul (371=378) și TVA neexigibilă (371=4428); costul vine din factură.
    Un NIR nelegat rămâne complet.” MUTAȚIE: filtrul notelor NIR-ului legat scos -> apar 371=401 și 4426=401 -> pică."""
    from core import stocuri_api as s
    conn, cur, *_ = tx
    _metoda(cur, "global_valoric")
    fid = _factura_primita(cur)
    lin = [dict(_L, denumire="Marfa A", pret_vanzare=80)]
    r = s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-07", "factura_id": fid, "linii": lin})
    assert "eroare" not in r, r
    assert _note(cur, r["inregistrari"]) == [("371", "378", "111.16"), ("371", "4428.02", "138.84")]
    assert (r["factura_id"], r["factura_ref"]) == (fid, "FP1")
    r2 = s.adauga_nir(conn, SCH, {"numar": "2", "data": "2099-10-07", "linii": lin})       # nelegat: complet
    # [decizia Costin 08.10 §6 pct.1 + pct.3] fără factură: datoria pe 408 („Furnizori - facturi nesosite”), TVA neexigibil pe
    # analiticul de achiziție al lui 4428 până la factură — OMFP 1802/2014, funcțiunea contului 408: „În creditul contului 408 …
    # se înregistrează: – valoarea bunurilor aprovizionate … (… 371, …, 4428, …)”
    assert [n[:2] for n in _note(cur, r2["inregistrari"])] == [("371", "408"), ("4428.01", "408"), ("371", "378"), ("371", "4428.02")]


def test_d2_nir_legat_refuzuri_numite(tx):
    """Costul NIR-ului legat = netul facturii (altfel 371 n-ar mai fi valoarea de vânzare, iar K ar ieși greșit); o factură, un
    NIR; fără transport/taxe pe NIR-ul legat; la cantitativ-valoric legarea se refuză; factura legată nu se șterge.
    MUTAȚIE: verificarea costului scoasă -> NIR-ul de 600 trece pe factura de 550 -> pică."""
    from core import stocuri_api as s, facturi_api as fa, contare_facturi as cf
    conn, cur, *_ = tx
    _metoda(cur, "global_valoric")
    fid = _factura_primita(cur)
    lin = lambda pa: [dict(_L, pret_achizitie=pa, denumire="Marfa A", pret_vanzare=80)]  # noqa: E731
    r = s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-07", "factura_id": fid, "linii": lin(60)})
    assert (r["cod"], r["erori_campuri"][0]["camp"]) == ("COST_DIFERIT_DE_FACTURA", "sn-factura")
    r = s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-07", "factura_id": fid, "transport": 10, "linii": lin(55)})
    assert (r["cod"], r["erori_campuri"][0]["camp"]) == ("TRANSPORT_LA_NIR_LEGAT", "sn-transport")
    assert "eroare" not in s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-07", "factura_id": fid, "linii": lin(55)})
    r = s.adauga_nir(conn, SCH, {"numar": "2", "data": "2099-10-07", "factura_id": fid, "linii": lin(55)})
    assert r["cod"] == "FACTURA_DEJA_LEGATA"
    with pytest.raises(cf.RefuzContare) as e:
        fa.sterge_factura(conn, fid)
    assert e.value.cod == "LEGATA_DE_NIR"
    _metoda(cur, "cantitativ_valoric")
    f2 = _factura_primita(cur, numar="FP2")
    r = s.adauga_nir(conn, SCH, {"numar": "3", "data": "2099-10-07", "factura_id": f2,
                                 "linii": [dict(_L, denumire="Marfa B", articol_nou=True)]})
    assert r["cod"] == "NIR_LEGAT_LA_COST"


# ── R1: motorul ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_r1_stornarea_in_rosu_scoate_intrarea_cu_valoarea_ei_si_recalculeaza_cmp():
    """OMFP 1802/2014 pct.69: stornarea „prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu)”. Intrarea
    10 × 55 stornată scoate 550,00 (valoarea ei), nu 10 × CMP. MUTAȚIE: ramura stornării calculează la CMP -> pică."""
    from core import stocuri_cv as cv
    m = [{"id": 1, "tip": "intrare", "cantitate": 100, "pret_unitar": 50, "data": "2099-01-01"},
         {"id": 2, "tip": "iesire", "cantitate": 10, "data": "2099-01-02"},
         {"id": 3, "tip": "intrare", "cantitate": 10, "pret_unitar": 60, "data": "2099-01-03"},
         {"id": 4, "tip": "intrare", "cantitate": -10, "pret_unitar": 60, "valoare": "-600.00", "anuleaza_id": 3,
          "data": "2099-01-04"},
         {"id": 5, "tip": "iesire", "cantitate": -10, "valoare": "-500.00", "anuleaza_id": 2, "data": "2099-01-05"}]
    f = cv.fisa_magazie(m)
    assert [(str(x["sold_cantitate"]), str(x["sold_valoare"])) for x in f] == \
        [("100", "5000.00"), ("90", "4500.00"), ("100", "5100.00"), ("90", "4500.00"), ("100", "5000.00")]
    with pytest.raises(ValueError):            # o intrare a cărei marfă a ieșit nu se stornează (stoc negativ)
        cv.fisa_magazie([m[0], {"id": 6, "tip": "iesire", "cantitate": 100, "data": "2099-01-02"},
                         {"id": 7, "tip": "intrare", "cantitate": -100, "valoare": "-5000", "anuleaza_id": 1, "data": "2099-01-03"}])
    with pytest.raises(ValueError):            # cantitatea negativă fără `anuleaza_id` rămâne invalidă
        cv.fisa_magazie([{"tip": "intrare", "cantitate": -1, "pret_unitar": 1, "valoare": "-1", "data": "2099-01-01"}])


# ── R1: respingerea în coadă ─────────────────────────────────────────────────────────────────────────────────────────────
def _nir_cv_in_coada(conn, cur, tid, cab, asist, numar="1", cant=10):
    from core import stocuri_api as s, coada_api as c
    _metoda(cur, "cantitativ_valoric")
    _ca(cur, asist)
    cur.execute("SELECT id FROM articole WHERE denumire='Marfa A'")
    a = cur.fetchone()
    linie = dict(_L, cantitate=cant, **({"articol_id": a[0]} if a else {"denumire": "Marfa A", "articol_nou": True}))
    r = s.adauga_nir(conn, SCH, {"numar": numar, "data": "2099-10-07", "furnizor": "DANTE INTERNATIONAL SA", "linii": [linie]})
    assert "eroare" not in r, r
    el = c.pune_notele_in_coada(conn, cab, tid, asist)
    return r, el[0]["coada_id"]


def test_r1_respingerea_nir_storneaza_intrarea_si_il_marcheaza_respins(tx):
    """Decizia (retest 07.10, pct.1): „respingerea anulează mișcarea de stoc printr-o înregistrare inversă în fișa de magazie
    (nu prin ștergere), cu CMP recalculat. Documentul respins rămâne în listă, marcat «respins», cu motivul vizibil”.
    MUTAȚIE: apelul `stocuri_anulare.storneaza` scos din `coada_api.respinge` -> stocul rămâne 10 -> pică."""
    from core import coada_api as c, stocuri_api as s
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    assert _stoc(cur) == ("10.000", "550.00")
    _ca(cur, valid)
    rez = c.respinge(conn, cid, str(valid), "NIR greșit", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)
    assert rez["ok"], rez
    assert _stoc(cur) == ("0.000", "0.00")
    cur.execute("SELECT tip, cantitate::text, valoare::text, anuleaza_id IS NOT NULL, nir_id FROM miscari_stoc ORDER BY id")
    assert [tuple(x) for x in cur.fetchall()] == [("intrare", "10.000", "550.00", False, r["id"]),
                                                  ("intrare", "-10.000", "-550.00", True, r["id"])]   # nimic șters
    lst = s.stare_validare_nir(s.lista_nir(conn, SCH, 2099, 10), c.stari_note(conn, tid, r["inregistrari"]), {})
    assert lst[0]["respins"]["motiv_respingere"] == "NIR greșit" and lst[0]["refacut_in"] is None
    assert c.respinge(conn, cid, str(valid), "x", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"] is False


def test_r1_nota_de_corectie_respinsa_nu_storneaza_documentul_contat(tx):
    """[neconformitatea 09.10.2026, prinsă pe producție la migrarea Retest 2] NIR-ul cu notele VALIDATE primește ulterior o notă
    de corecție (refacerea pe 408 din `migrare_retest_0810`, „Stornare cost NIR” din `nir_legare.leaga` — amândouă o adaugă în
    `nir.inregistrari_ids`, deci în grupul `nir-<id>`). Respingerea ei respinge NOTA, nu documentul: marfa e în evidență pe 371,
    deci rămâne și în fișă (pe tenant_049, respingerea notelor 121/122 a scos din fișă NIR 2 și NIR 1, cu 371 = 1.150 lei).
    NIR-ul nu devine „respins” și nu se reface (refacerea i-ar dubla intrarea). OMFP 1802/2014 pct.69: corectarea se face prin
    stornare, cu notă — nu prin desfacerea în fișă a unei operațiuni contate.
    MUTAȚIE: `AND NOT IN_EVIDENTA` scos din `stocuri_anulare.miscari_vii` -> stocul ajunge 0 -> pică."""
    from core import coada_api as c, stocuri_api as s
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    _ca(cur, valid)
    ap = c.aproba(conn, cid, str(valid), aprobat_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)   # tot documentul
    assert ap["ok"], ap
    cur.execute("SELECT count(*) FROM inregistrari WHERE id = ANY(%s) AND status = 'validata'", (r["inregistrari"],))
    assert cur.fetchone()[0] == len(r["inregistrari"]) > 0
    _ca(cur, asist)                                  # nota de corecție, adăugată la document cum o adaugă migrarea și legarea
    cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status, document_ref) VALUES "
                "('2099-10-07', 'REFACERE-NIR-%s', 'Refacere NIR nr. 1 fără factură', 'stocuri', 'ciorna', 'NIR nr 1') "
                "RETURNING id" % r["id"])
    corectie = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '371', '401', -550)",
                (corectie,))
    cur.execute("UPDATE nir SET inregistrari_ids = inregistrari_ids || to_jsonb(%s::int) WHERE id = %s", (corectie, r["id"]))
    el = c.pune_notele_in_coada(conn, cab, tid, asist)
    assert len(el) == 1
    cur.execute("SELECT payload->>'grup' FROM public.declaratii_coada WHERE id = %s", (el[0]["coada_id"],))
    assert cur.fetchone()[0] == "nir-%s" % r["id"]   # în grupul documentului: exact drumul care a stornat pe producție
    _ca(cur, valid)
    rez = c.respinge(conn, el[0]["coada_id"], str(valid), "descrierea", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)
    assert rez["ok"], rez
    assert _stoc(cur) == ("10.000", "550.00")        # marfa contată rămâne în fișă
    cur.execute("SELECT count(*) FROM miscari_stoc WHERE anuleaza_id IS NOT NULL")
    assert cur.fetchone()[0] == 0
    lst = s.stare_validare_nir(s.lista_nir(conn, SCH, 2099, 10), c.stari_note(conn, tid, r["inregistrari"] + [corectie]), {})
    assert [(x["numar"], x["in_evidenta"], x["respins"]) for x in lst] == [("1", True, None)]
    _ca(cur, asist)
    nou = {"numar": "1", "data": "2099-10-07", "refacut_din_id": r["id"], "confirma_neschimbata": True,
           "linii": [dict(_L, articol_id=r.get("articol_id") or _articol(cur))]}
    assert s.adauga_nir(conn, SCH, nou)["cod"] == "NIR_IN_EVIDENTA"


def test_r1_reparatia_pe_date_scoate_stornarea_gresita_si_retrimite_nota(tx):
    """[09.10.2026, comanda Costin pct.1] „aprob ștergerea rândurilor 8 și 9 din miscari_stoc (mișcări de sistem fără notă
    contabilă) … Apoi retrimite notele 121 și 122 la validare, cu descrierea în limbaj de contabil.” Starea din producție, refăcută:
    NIR contat, nota de refacere respinsă pentru descriere („decizia Costin”), stornarea scrisă de codul vechi peste intrare.
    `migrare_nota_corectie` scoate stornarea (stocul revine la 10 / 550,00, ca 371), întoarce rândul întreg (pentru jurnal) și
    retrimite nota cu descrierea nouă; o stornare legitimă (NIR nevalidat) rămâne. A doua rulare nu mai găsește nimic.
    MUTAȚII: definiția `IN_EVIDENTA` scoasă din selecție -> se șterge și stornarea legitimă -> pică; filtrul pe motiv scos ->
    nota respinsă pentru altceva se retrimite -> pică."""
    from core import coada_api as c, migrare_nota_corectie as m
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    _ca(cur, valid)
    assert c.aproba(conn, cid, str(valid), aprobat_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    _ca(cur, asist)

    def refacere(motiv, descriere="Refacere NIR 1 pe 408 (decizia Costin 08.10, pct.4)", nir=None):
        nir = nir or r
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status, document_ref) VALUES ('2099-10-07', "
                    "'REFACERE-NIR-' || %s, %s, 'stocuri', 'ciorna', 'NIR nr 1') RETURNING id", (nir["id"], descriere))
        n = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'371','401',-550)", (n,))
        cur.execute("UPDATE nir SET inregistrari_ids = inregistrari_ids || to_jsonb(%s::int) WHERE id = %s", (n, nir["id"]))
        el = c.pune_notele_in_coada(conn, cab, tid, asist)
        _ca(cur, valid)
        assert c.respinge(conn, el[0]["coada_id"], str(valid), motiv, respins_de_id=valid, cabinet_id_apelant=cab,
                          schema_nota=SCH)["ok"]
        _ca(cur, asist)
        return n
    nota = refacere("Descrierea conține referințe interne („decizia Costin 08.10, pct.4”).")
    cur.execute("SELECT id FROM miscari_stoc WHERE nir_id = %s", (r["id"],))
    intrare = cur.fetchone()[0]
    # starea de dinainte de regulile de fond (R5 ar refuza azi stornarea asta — exact cum trebuie): regula de stoc oprită numai cât
    # se reconstituie starea veche și rulează reparația, ca pe producție, unde reparația vine ÎNAINTEA regulilor
    cur.execute("ALTER TABLE miscari_stoc DISABLE TRIGGER trg_regula_stoc")
    cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, nir_id, anuleaza_id) "
                "SELECT articol_id, '2099-10-09', tip, -cantitate, pret_unitar, -valoare, 'Stornare: NIR nr 1 (respins la validare)', "
                "nir_id, id FROM miscari_stoc WHERE id = %s RETURNING id", (intrare,))
    gresita = cur.fetchone()[0]                      # exact ce scrisese codul vechi (rândurile 8, 9 de pe tenant_049)
    assert _stoc(cur) == ("0.000", "0.00")
    r2, cid2 = _nir_cv_in_coada(conn, cur, tid, cab, asist, numar="2")      # contraproba: NIR nevalidat, respins -> stornare legitimă
    _ca(cur, valid)
    assert c.respinge(conn, cid2, str(valid), "NIR greșit", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    cur.execute("SELECT count(*) FROM miscari_stoc WHERE anuleaza_id IS NOT NULL")
    assert cur.fetchone()[0] == 2

    _ca(cur, asist)
    r3, cid3 = _nir_cv_in_coada(conn, cur, tid, cab, asist, numar="3")   # NIR contat cu o refacere respinsă pentru ALTCEVA
    _ca(cur, valid)
    assert c.aproba(conn, cid3, str(valid), aprobat_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    _ca(cur, asist)
    alta = refacere("Suma nu e cea din NIR.", descriere="Refacere NIR nr. 3 fără factură", nir=r3)

    scoase = m.stornari_gresite(conn, SCH)
    assert [x["id"] for x in scoase] == [gresita] and str(scoase[0]["valoare"]) == "-550.00" and scoase[0]["anuleaza_id"] == intrare
    assert _stoc(cur) == ("20.000", "1100.00")       # NIR 1 contat înapoi în fișă (+ NIR 3); NIR 2 respins rămâne stornat
    assert m.stornari_gresite(conn, SCH) == []
    cur.execute("ALTER TABLE miscari_stoc ENABLE TRIGGER trg_regula_stoc")
    rez = m.retrimite_refaceri(conn, SCH, tid, cab)
    assert [(x[0], isinstance(x[2], int)) for x in rez] == [(nota, True)], rez   # `alta` (motivul e suma) nu se atinge
    assert alta not in [x[0] for x in rez]
    cur.execute("SELECT descriere FROM inregistrari WHERE id = %s", (nota,))
    assert "decizia Costin" not in cur.fetchone()[0]
    cur.execute("SELECT stare FROM public.declaratii_coada WHERE id = %s", (rez[0][2],))
    assert cur.fetchone()[0] == "la_senior"
    assert m.retrimite_refaceri(conn, SCH, tid, cab) == []                   # a doua rulare: nimic


def _articol(cur, den="Marfa A"):
    cur.execute("SELECT id FROM articole WHERE denumire = %s", (den,))
    return cur.fetchone()[0]


def test_r1_respingerea_se_refuza_cand_marfa_a_iesit_si_nu_scrie_nimic(tx):
    """MUTAȚIE: `ROLLBACK TO SAVEPOINT stornare` scos -> rândul de stornare rămâne scris -> pică."""
    from core import coada_api as c, stocuri_cv_api as cva
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    cur.execute("SELECT id FROM articole WHERE denumire='Marfa A'")
    aid = cur.fetchone()[0]
    assert "eroare" not in cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-08", "cantitate": 6, "document": "BC 1"})
    _ca(cur, valid)
    rez = c.respinge(conn, cid, str(valid), "NIR greșit", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)
    assert (rez["ok"], rez["cod"]) == (False, "STOC_IESIT")
    cur.execute("SELECT count(*) FROM miscari_stoc WHERE anuleaza_id IS NOT NULL")
    assert cur.fetchone()[0] == 0


def test_r1_nota_documentului_stornat_nu_mai_intra_in_evidenta_pe_alt_drum(tx):
    """Validarea din jurnal și retrimiterea refuză nota unui document cu stocul stornat (altfel nota ar fi validată, iar marfa ei
    n-ar mai fi în fișă). MUTAȚIE: verificarea `document_stornat` scoasă din `jurnal_api.valideaza` -> nota se validează -> pică."""
    from core import coada_api as c, jurnal_api as j
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    _ca(cur, valid)
    assert c.respinge(conn, cid, str(valid), "NIR greșit", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    v = j.valideaza(conn, SCH, r["inregistrari"][0])
    assert (v["cod"], v["regula"]) == ("DOCUMENT_STORNAT", "OMFP 1802/2014 pct.69")
    _ca(cur, asist)
    rt = c.retrimite_nota(conn, cab, tid, r["inregistrari"][0], asist)
    assert (rt["ok"], rt["cod"]) == (False, "DOCUMENT_STORNAT")


def test_r1_nir_respins_se_reface_o_singura_data_si_ciornele_vechi_ies(tx):
    """„… și poate fi refăcut de asistent.” MUTAȚIE: ștergerea ciornelor respinse la refacere scoasă -> rămân -> pică."""
    from core import coada_api as c, stocuri_api as s
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    lin = [dict(_L, articol_id=None)]
    cur.execute("SELECT id FROM articole WHERE denumire='Marfa A'")
    lin[0]["articol_id"] = cur.fetchone()[0]
    nou = {"numar": "1", "data": "2099-10-07", "refacut_din_id": r["id"], "linii": lin, "confirma_neschimbata": True}
    assert s.adauga_nir(conn, SCH, dict(nou))["cod"] == "NIR_NERESPINS"
    _ca(cur, valid)
    assert c.respinge(conn, cid, str(valid), "NIR greșit", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    _ca(cur, asist)
    r2 = s.adauga_nir(conn, SCH, dict(nou))
    assert "eroare" not in r2, r2
    cur.execute("SELECT count(*) FROM inregistrari WHERE id = ANY(%s)", (r["inregistrari"],))
    assert cur.fetchone()[0] == 0
    assert _stoc(cur) == ("10.000", "550.00")
    assert s.adauga_nir(conn, SCH, dict(nou))["cod"] == "NIR_DEJA_REFACUT"
    lst = s.stare_validare_nir(s.lista_nir(conn, SCH, 2099, 10), c.stari_note(conn, tid, r["inregistrari"]),
                               s.refaceri_nir(conn, SCH, [r["id"]]))
    assert [(x["numar"], bool(x["respins"]), x["refacut_in"]) for x in lst] == [("1", True, "1"), ("1", False, None)]


def test_r1_factura_stornata_isi_reface_intrarea_la_refacere(tx):
    """Factura primită cu intrare în stoc, respinsă (stornată), refăcută: intrarea se scrie din nou (verificarea de idempotență
    ignoră mișcările stornate). MUTAȚIE: filtrul „vie” scos din `intrare_din_factura` -> „deja_intrat” -> pică."""
    from core import stocuri_anulare as sa, stocuri_cv_api as cva
    conn, cur, *_ = tx
    _metoda(cur, "cantitativ_valoric")
    fid = _factura_primita(cur)
    cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) VALUES (%s,'Marfa A',10,55,21)",
                (fid,))
    assert cva.intrare_din_factura(conn, SCH, fid, "371", "2099-10-07")["stare"] == "intrat"
    assert sa.storneaza(conn, SCH, "factura-%d" % fid, [], "factură greșită")["stornate"]
    assert _stoc(cur) == ("0.000", "0.00")
    assert sa.reface_factura(conn, SCH, fid)["stare"] == "intrat"
    assert _stoc(cur) == ("10.000", "550.00")
    assert sa.reface_factura(conn, SCH, fid) is None                      # o singură dată


def test_r1_miscarea_in_evidenta_nu_se_storneaza_pe_niciuna_din_cele_trei_legaturi(tx):
    """[neconformitatea 09.10.2026] `stocuri_anulare.IN_EVIDENTA`, pe fiecare legătură a mișcării cu nota ei: (1) nota proprie
    (`inregistrare_id`) validată; (2) intrarea din NIR (fără notă proprie) — acoperită de testul notei de corecție; (3) intrarea din
    factura primită (fără notă proprie), cu nota facturii validată. Contraproba: aceeași mișcare cu nota în CIORNĂ se stornează.
    MUTAȚII: clauza (1) scoasă -> ieșirea contată se stornează -> pică; clauza (3) scoasă -> intrarea din factură se stornează."""
    from core import stocuri_anulare as sa, stocuri_cv_api as cva
    conn, cur, *_ = tx
    _metoda(cur, "cantitativ_valoric")
    fid = _factura_primita(cur)
    cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) VALUES (%s,'Marfa A',10,55,21)",
                (fid,))
    assert cva.intrare_din_factura(conn, SCH, fid, "371", "2099-10-07")["stare"] == "intrat"

    def nota(status, factura_id=None):
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, factura_id, document_ref) VALUES ('2099-10-07', 'proba', "
                    "'stocuri', 'ciorna', %s, %s) RETURNING id", (factura_id, None if factura_id else "BC proba"))
        i = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '371', '401', 1)", (i,))
        if status == "validata":
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (i,))
        return i
    contare = nota("validata", fid)                                     # (3) nota facturii, validată
    assert sa.storneaza(conn, SCH, "factura-%d" % fid, [contare], "x") == {"stornate": []}
    assert _stoc(cur) == ("10.000", "550.00")
    aid = _articol(cur)
    for status, stornata in (("validata", False), ("ciorna", True)):    # (1) nota proprie; contraproba pe ciornă
        n = nota(status)
        cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, document, inregistrare_id) "
                    "VALUES (%s, '2099-10-08', 'iesire', 1, 55, 'BC proba', %s)", (aid, n))
        assert bool(sa.storneaza(conn, SCH, None, [n], "x")["stornate"]) is stornata, status


# ── R2 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_r2_titlul_documentului_e_scurt_document_partener_numar_de_note(tx):
    """Comanda (retest 07.10, pct.2): titlul „trebuie să fie scurt, de forma «NIR nr 1 din 07.10.2026 · DANTE INTERNATIONAL SA ·
    4 note». La fel în mesajul de confirmare după respingere” (ecranul folosește aceeași `eticheta`). MUTAȚIE: forma veche
    („Document · … · 4 note: NIR 1 …; NIR 1 …”) -> pică."""
    from core import coada_api as c, stocuri_api as s
    conn, cur, tid, cab, asist, valid = tx
    _metoda(cur, "global_valoric")
    _ca(cur, asist)
    r = s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-07", "furnizor": "DANTE INTERNATIONAL SA",
                                 "linii": [dict(_L, denumire="Marfa A", pret_vanzare=80)]})
    adaugate = c.pune_notele_in_coada(conn, cab, tid, asist)
    assert [a["eticheta"] for a in adaugate] == ["NIR nr 1 din 07.10.2099 · DANTE INTERNATIONAL SA · 4 note"]
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert [x["eticheta"] for x in el] == ["NIR nr 1 din 07.10.2099 · DANTE INTERNATIONAL SA · 4 note"]
    assert len(r["inregistrari"]) == 4


def test_r2_migrarea_pune_partenerul_pe_elementele_vechi(tx):
    """Elementele scrise înainte (fără `partener`) primesc partenerul și hash-ul refăcut; starea nu se schimbă.
    MUTAȚIE: `p["partener"] = …` scos din migrare -> titlul rămâne fără partener -> pică."""
    from core import coada_api as c, stocuri_api as s, migrare_decizii_0710 as m
    conn, cur, tid, cab, asist, valid = tx
    _metoda(cur, "global_valoric")
    _ca(cur, asist)
    s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-07", "furnizor": "DANTE INTERNATIONAL SA",
                             "linii": [dict(_L, denumire="Marfa A", pret_vanzare=80)]})
    c.pune_notele_in_coada(conn, cab, tid, asist)
    cur.execute("UPDATE public.declaratii_coada SET payload = payload - 'partener' WHERE tenant_id = %s", (tid,))
    assert len(m.partener_in_coada(conn, tid)) == 4
    cur.execute('SET search_path TO "%s", public' % SCH)
    cur.execute("SELECT DISTINCT stare, payload->>'partener', hash IS NOT NULL FROM public.declaratii_coada WHERE tenant_id=%s", (tid,))
    assert cur.fetchall() == [("la_senior", "DANTE INTERNATIONAL SA", True)]
    assert m.partener_in_coada(conn, tid) == []


# ── S4 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_s4_notificarea_se_rezolva_cand_elementul_isi_schimba_starea(tx):
    """Comanda (retest 07.10 seara, pct.4): „O notificare se marchează rezolvată (validat / respins / înlocuit) când elementul
    își schimbă starea; o notă înlocuită nu lasă o a doua notificare activă.” Triggerul de pe coadă rezolvă pe ORICE drum de
    schimbare a stării. MUTAȚIE: triggerul scos (DROP TRIGGER) -> notificarea rămâne activă -> pică."""
    from core import coada_api as c, notificari_api as nt, note_derivate as nd, jurnal_api as j
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    # [09.10.2026, regulile de fond R3] nota se validează numai cu documentul justificativ
    n1 = j.creeaza(conn, SCH, "Chirie", "2099-10-05", [{"debit": "612", "credit": "401", "suma": 100}], document_ref="Contract chirie 1")["id"]
    n2 = j.creeaza(conn, SCH, "Telefon", "2099-10-05", [{"debit": "626", "credit": "401", "suma": 50}], document_ref="FCT tel 1")["id"]
    el = {a["eticheta"]: a["coada_id"] for a in c.pune_notele_in_coada(conn, cab, tid, asist)}
    c1 = next(v for k, v in el.items() if k.startswith("Notă · Chirie"))
    c2 = next(v for k, v in el.items() if k.startswith("Notă · Telefon"))
    # [09.10.2026] notificările sunt un tabel PARTAJAT: baza de test are deja necitite ale acelorași conturi (rulările plasei) —
    # testul măsoară DIFERENȚA, nu presupune gol (CLAUDE.md, „Testele nu presupun gol un interval”)
    v0, a0 = nt.contor(conn, valid)["necitite"], nt.contor(conn, asist)["necitite"]
    for cid in (c1, c2):
        nt.adauga(conn, valid, "de_validat", "de validat", link="validat:%d" % cid)
    assert nt.contor(conn, valid)["necitite"] == v0 + 2
    _ca(cur, valid)
    assert c.aproba(conn, c1, str(valid), valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    assert c.respinge(conn, c2, str(valid), "lipsește factura", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    rez = {x["link"]: x["rezolvata"] for x in nt.lista(conn, valid)["notificari"]}
    assert (rez["validat:%d" % c1], rez["validat:%d" % c2]) == ("validat", "respins")
    assert nt.contor(conn, valid)["necitite"] == v0 and nt.sumar(conn, valid)["necitite"] == v0
    # cel care a pregătit-o: „a fost respinsă” rămâne activă până când nota e ÎNLOCUITĂ
    nt.adauga(conn, asist, "respinsa", "a fost respinsă", link="jurnal:%d:%d:2099:10" % (tid, n2))
    assert nt.contor(conn, asist)["necitite"] == a0 + 1
    assert nd.sterge_respinsa(cur, SCH, n2) == 1
    assert [x["rezolvata"] for x in nt.lista(conn, asist)["notificari"]
            if x["tip"] == "respinsa" and x.get("link") == "jurnal:%d:%d:2099:10" % (tid, n2)] == ["inlocuit"]
    assert nt.contor(conn, asist)["necitite"] == a0
    assert n1


# ── S3 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_s3_retrimiterea_notei_neschimbate_cere_confirmare_si_cardul_o_spune(tx):
    """Comanda (retest 07.10 seara, pct.3): „dacă recontabilizarea produce aceeași notă ca cea respinsă, asistentul vede un
    avertisment («nimic nu s-a schimbat de la respingere», cu motivul alături) și confirmă explicit; nu se blochează. În coadă,
    cardul unei note retrimise arată «retrimisă după respingere», motivul respingerii anterioare și dacă nota s-a schimbat”.
    MUTAȚIE: `avertisment_neschimbata` întoarce mereu None -> retrimiterea trece fără confirmare -> pică."""
    from core import coada_api as c, jurnal_api as j
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    nid = j.creeaza(conn, SCH, "Chirie", "2099-10-05", [{"debit": "612", "credit": "401", "suma": 100}])["id"]
    cid = c.pune_notele_in_coada(conn, cab, tid, asist)[0]["coada_id"]
    _ca(cur, valid)
    assert c.respinge(conn, cid, str(valid), "lipsește factura", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    _ca(cur, asist)
    av = c.retrimite_nota(conn, cab, tid, nid, asist)
    assert (av["ok"], av["cod"], av["cere_confirmare"], av["motiv"]) == (False, "NESCHIMBATA", True, "lipsește factura")
    assert c.retrimite_nota(conn, cab, tid, nid, asist, confirma=True)["ok"]
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert el[0]["retrimisa"]["motiv_respingere"] == "lipsește factura" and el[0]["retrimisa"]["schimbata"] is False
    # schimbată: cardul o spune, iar retrimiterea nu mai cere confirmare
    _ca(cur, valid)
    assert c.respinge(conn, el[0]["id"], str(valid), "suma greșită", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    cur.execute("UPDATE inregistrari_linii SET suma = 120 WHERE inregistrare_id = %s", (nid,))
    _ca(cur, asist)
    assert c.retrimite_nota(conn, cab, tid, nid, asist)["ok"]
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert (el[0]["retrimisa"]["motiv_respingere"], el[0]["retrimisa"]["schimbata"]) == ("suma greșită", True)


def test_s3_nir_refacut_identic_cere_confirmare(tx):
    """Aceeași regulă la NIR-ul refăcut (documentul care îl reface pe cel respins). MUTAȚIE: verificarea scoasă din
    `adauga_nir` -> NIR-ul identic se scrie fără confirmare -> pică."""
    from core import coada_api as c, stocuri_api as s
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    _ca(cur, valid)
    assert c.respinge(conn, cid, str(valid), "NIR greșit", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    _ca(cur, asist)
    cur.execute("SELECT id FROM articole WHERE denumire='Marfa A'")
    nou = {"numar": "1", "data": "2099-10-07", "refacut_din_id": r["id"], "linii": [dict(_L, articol_id=cur.fetchone()[0])]}
    av = s.adauga_nir(conn, SCH, dict(nou))
    assert (av["cod"], av["motiv"]) == ("NESCHIMBATA", "NIR greșit")
    r2 = s.adauga_nir(conn, SCH, dict(nou, confirma_neschimbata=True))
    assert "eroare" not in r2 and r2.get("cod") != "NESCHIMBATA", r2
    c.pune_notele_in_coada(conn, cab, tid, asist)
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert el[0]["retrimisa"]["motiv_respingere"] == "NIR greșit" and el[0]["retrimisa"]["schimbata"] is False



def test_199_retrimisa_compara_notele_documentului_oricare_ar_fi_capul_grupului(tx):
    """[deficiența 199, 09.10.2026] Cardul NIR-ului refăcut spune dacă notele s-au schimbat față de cele respinse. Capul grupului din
    listă e elementul cel mai NOU; când el nu era primul membru, `lista_coada` îi înlocuia nota cu payload-ul grupului ÎNAINTE de a
    citi amprentele membrilor -> amprenta primului apărea de două ori, iar NIR-ul refăcut identic ieșea „schimbat”. Aici capul e
    forțat să fie ultimul membru (cazul care strica), deci rezultatul nu mai depinde de ordinea întâmplătoare a notelor.
    MUTAȚIE: amprentele citite după suprascriere (codul vechi) -> „schimbată” True -> pică."""
    from core import coada_api as c, stocuri_api as s
    conn, cur, tid, cab, asist, valid = tx
    r, cid = _nir_cv_in_coada(conn, cur, tid, cab, asist)
    _ca(cur, valid)
    assert c.respinge(conn, cid, str(valid), "NIR greșit", respins_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    _ca(cur, asist)
    nou = {"numar": "1", "data": "2099-10-07", "refacut_din_id": r["id"], "confirma_neschimbata": True,
           "linii": [dict(_L, articol_id=_articol(cur))]}
    assert "eroare" not in s.adauga_nir(conn, SCH, nou)
    el = c.pune_notele_in_coada(conn, cab, tid, asist)
    ids = sorted(m for m, _p in c.membri_grup(cur, el[0]["coada_id"]))
    assert len(el) == 1 and len(ids) == 2, (el, ids)
    cur.execute("UPDATE public.declaratii_coada SET creat_la = now() + interval '1 second' WHERE id = %s", (ids[-1],))
    lst = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert len(lst) == 1 and lst[0]["membri_ids"] == ids
    assert (lst[0]["retrimisa"]["motiv_respingere"], lst[0]["retrimisa"]["schimbata"]) == ("NIR greșit", False)

# ── D3 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _z(cur, numar="Z-1"):
    from core import repo_contabilitate as rc
    iid = rc.nota_horeca_z_ciorna(cur, SCH, "2099-10-07", numar, "Raport Z", "Raport Z nr 1 din 07.10.2099")[0]
    rc.adauga_linie_3(cur, SCH, iid, "5311", "707", 121)
    rc.adauga_linie_3(cur, SCH, iid, "707", "4427", 21)
    rc.adauga_z_amef(cur, SCH, iid, "8000000001", 3)
    return iid


def test_d3_z_la_cantitativ_valoric_nu_se_valideaza_fara_descarcare(tx):
    """Decizia pct.3: „Raportul Z la cantitativ-valoric: fără refuz. Descărcarea pe articol se cere explicit (manual sau prin
    rețetă); Z-ul nu se validează fără ea.” MUTAȚIE: apelul `z_descarcare.refuz_validare` scos din `jurnal_api.valideaza` ->
    Z-ul nedescărcat se validează -> pică."""
    from core import jurnal_api as j, stocuri_api as s, stocuri_cv_api as cva, z_descarcare as zd
    conn, cur, *_ = tx
    _metoda(cur, "cantitativ_valoric")
    s.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-01", "linii": [dict(_L, denumire="Marfa A", articol_nou=True)]})
    cur.execute("SELECT id FROM articole WHERE denumire='Marfa A'")
    aid = cur.fetchone()[0]
    z1, z2 = _z(cur, "Z-1"), _z(cur, "Z-2")
    v = j.valideaza(conn, SCH, z1)
    assert (v.get("cod"), v.get("regula")) == (zd.COD_NEDESCARCAT, "OMFP 1802/2014 pct.287 alin.(1)-(2)"), v
    assert "eroare" not in cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-07", "cantitate": 2, "z_id": z1})
    assert zd.stare(cur, SCH, z1) == {"iesiri": 1, "fara_marfa": None}
    assert j.valideaza(conn, SCH, z1) == {"ok": True}
    with pytest.raises(ValueError, match="deja validat"):                        # Z validat: nu mai primește descărcări
        cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-07", "cantitate": 1, "z_id": z1})
    assert zd.marcheaza_fara_marfa(conn, SCH, z2, True)["fara_marfa"] is True     # declarație explicită
    assert j.valideaza(conn, SCH, z2) == {"ok": True}


def test_d3_z_la_global_valoric_ramane_neschimbat(tx):
    """La global-valoric Z-ul rămâne pe descărcarea lunară cu K: validarea nu cere descărcare pe articol. MUTAȚIE: condiția de
    metodă scoasă din `refuz_validare` -> pică."""
    from core import jurnal_api as j
    conn, cur, *_ = tx
    _metoda(cur, "global_valoric")
    assert j.valideaza(conn, SCH, _z(cur)) == {"ok": True}
