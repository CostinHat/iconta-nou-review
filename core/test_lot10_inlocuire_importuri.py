# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 426 — CLASA, comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”] „al doilea import de balanță pentru aceeași
firmă o înlocuiește pe prima fără avertisment. Înainte de înlocuire: spune că există deja o balanță, arată totalurile vechi și noi, cere
confirmare; dacă există note pe lunile de după preluare, spune că soldurile lor se recalculează.”

Clasa (CICLUL DE NECONFORMITATE pas 2): importul de migrare care înlocuiește pe tăcute ce exista. Balanța e reparată în
`core/test_lot10_import_inlocuire.py`; aici celelalte patru drumuri: soldurile pe parteneri (DELETE + INSERT), registrul mijloacelor fixe
(DELETE + INSERT), istoricul declarațiilor preluat (DELETE sursa='migrare' + INSERT), fișele salariaților (ON CONFLICT (cnp) DO UPDATE).
Fiecare: refuz fără confirmare (409, cu ce există și ce aduce fișierul, plus datele dependente), datele vechi neatinse, înlocuire cu
`inlocuieste=True`; previzualizarea spune același text. Gardul de clasă: `core/test_lot10_inlocuire_clasa.py`.

TEMEI: N/A — regulă de produs (nimic nu se înlocuiește pe tăcute, comanda 8.2 pct.4 și comanda 10.1). Schemă efemeră din template,
tranzacție anulată; `public.declaratii_depuse` pe tenant sintetic (990426), în ROLLBACK."""
import contextlib
import json
import os

import pytest

from core import db as _db, migrare_api, solduri_parteneri_api as sp, mijloace_fixe_import_api as mf, \
    istoric_declaratii_import_api as ist, salariati_import_api as si

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot10_inlocuire_cls"
T = 990426                                      # tenant sintetic (public.declaratii_depuse), în ROLLBACK
# CUI-uri cu cifra de control verificată (algoritmul din CLAUDE.md): 14399840, 4221306, 18189442
P1 = [{"cont": "4111", "cui": "RO14399840", "denumire": "DEDEMAN", "debit": 1000, "credit": 0},
      {"cont": "401", "cui": "RO4221306", "denumire": "FURNIZOR", "debit": 0, "credit": 400}]
P2 = [{"cont": "4111", "cui": "RO18189442", "denumire": "ALT CLIENT", "debit": 2500, "credit": 0}]
M1 = [{"cod": "100", "denumire": "Laptop", "valoare": 6000, "rezidual": 0, "dnf_luni": 36, "data_pif": "2025-01-10", "metoda": "liniara",
       "cont_imobilizare": "2141", "cont_amortizare": "2814", "amortizat_preluat": 1500}]
M2 = [dict(M1[0], cod="200", denumire="Server", valoare=12000, amortizat_preluat=2000), dict(M1[0], cod="201", valoare=3000,
                                                                                            amortizat_preluat=None)]
I1 = [{"tip": "D300", "an": 2025, "luna": 3, "data_depunere": "2025-04-20"},
      {"tip": "D100", "an": 2025, "luna": 6, "data_depunere": "2025-07-20", "suma": 500}]
I2 = [{"tip": "D300", "an": 2025, "luna": 6, "data_depunere": "2025-07-21"}]
CNP1 = "1900101410011"      # cifra de control verificată (test_412_cim_salariat)
CNP2 = "1960101078916"      # cifra de control verificată (test_import_saga.CNP_OK)


def _sal(cnp, nume, brut):
    return {"nume": nume, "prenume": "ANA", "cnp": cnp, "data_angajare": "2024-01-15", "tip_norma": "intreaga", "ore_zi": 8,
            "functie_baza": True, "scutit_contrib_minim": False, "salariu_brut": brut, "judet_casa": "B", "cor": "251401"}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
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
def uc(conn, monkeypatch):
    """Use-case-urile pe conexiunea efemeră (aceeași tranzacție, anulată)."""
    from core import uc_tenants, uc_comun

    @contextlib.contextmanager
    def _gc(schema=None):
        yield conn
    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCHEMA)
    return uc_tenants


def _balanta_4111(c):
    """Balanța de deschidere cu 4111 = 2.500 lei: soldurile pe parteneri din P2 se potrivesc cu ea (poarta [346] a use-case-ului)."""
    with c.cursor() as cur:
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) "
                    "VALUES ('4111', 'Clienți', 2500, 0, '2025-12-31'), ('1012', 'Capital', 0, 2500, '2025-12-31')")


def _unu(c, sql):
    with c.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()


# ── soldurile pe parteneri ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_426_parteneri_al_doilea_import_cere_confirmare(conn):
    """ROȘU înainte: `importa` făcea DELETE + INSERT fără întrebare (proba: al doilea import lăsa 1 partener, 2.500 lei). MUTAȚIA:
    `cere_confirmarea_inlocuirii` scos din `solduri_parteneri_api.importa` -> DID NOT RAISE."""
    sp.importa(conn, P1, "2025-12-31")
    with pytest.raises(migrare_api.InlocuireNeconfirmata) as e:
        sp.importa(conn, P2, "2025-12-31")
    # comanda 10.1: „spune că există deja […], arată totalurile vechi și noi, cere confirmare”
    # [lotul 12, 252] ce se șterge se numește întreg: și facturile deschise preluate ale primului import (DEDEMAN 1.000, FURNIZOR 400)
    assert str(e.value) == ("Firma are deja solduri pe parteneri la 31.12.2025: 2 parteneri, debit 1.000,00 lei, credit 400,00 lei, cu 2 "
                            "facturi deschise preluate. "
                            "Fișierul nou: 1 partener, debit 2.500,00 lei, credit 0,00 lei. Salvarea le înlocuiește pe cele vechi. "
                            "Confirmă înlocuirea și salvează din nou."), str(e.value)
    assert _unu(conn, "SELECT count(*), sum(sold_debitor) FROM solduri_parteneri") == (2, 1000)     # cele vechi, neatinse
    rez = sp.importa(conn, P2, "2025-12-31", inlocuieste=True)
    assert rez["inlocuita"]["randuri"] == 2
    assert _unu(conn, "SELECT count(*), sum(sold_debitor) FROM solduri_parteneri") == (1, 2500)


# ── registrul mijloacelor fixe ──────────────────────────────────────────────────────────────────────────────────────────────────
def _note_amortizare(c):
    with c.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, status, sursa) VALUES ('2026-01-31','A1','Amortizare','validata',"
                    "'amortizare'), ('2026-03-31','A3','Amortizare','validata','amortizare')")


def test_def_426_mijloace_fixe_al_doilea_import_cere_confirmare_si_numeste_amortizarile(conn):
    """ROȘU înainte: DELETE + INSERT tăcut (proba: registrul devenea 2 mijloace, 15.000 lei). MUTAȚIA: poarta scoasă din
    `mijloace_fixe_import_api.importa` -> DID NOT RAISE; MUTAȚIA 2: notele de amortizare scoase din text -> textul diferă."""
    mf.importa(conn, M1)
    _note_amortizare(conn)
    with pytest.raises(migrare_api.InlocuireNeconfirmata) as e:
        mf.importa(conn, M2)
    # comanda 10.1: totalurile vechi și noi (valoarea de intrare, amortizarea preluată) + datele dependente (amortizările înregistrate)
    assert str(e.value) == (
        "Firma are deja un registru de mijloace fixe: 1 mijloc fix, valoare de intrare 6.000,00 lei, amortizare preluată 1.500,00 lei. "
        "Fișierul nou: 2 mijloace fixe, valoare de intrare 15.000,00 lei, amortizare preluată 2.000,00 lei. Salvarea înlocuiește registrul "
        "vechi. În contabilitate sunt 2 note de amortizare (din 01/2026 până în 03/2026), calculate pe registrul vechi: rămân cum sunt, iar "
        "amortizarea lunilor încă negenerate se calculează pe registrul nou. Confirmă înlocuirea și salvează din nou."), str(e.value)
    assert _unu(conn, "SELECT count(*), sum(valoare) FROM mijloace_fixe") == (1, 6000)
    rez = mf.importa(conn, M2, inlocuieste=True)
    assert rez["importati"] == 2 and rez["inlocuit"]["randuri"] == 1
    assert _unu(conn, "SELECT count(*), sum(valoare) FROM mijloace_fixe") == (2, 15000)


def test_426_mijloace_fixe_cu_istoric_pe_fisa_nu_se_inlocuiesc_prin_import(conn):
    """Jurnalul fișei (`mijloace_fixe_jurnal.mijloc_id`, cheie străină) și reevaluările (`reevaluari.mijloc_fix_id`) țin de rândul
    mijlocului fix: înainte, ștergerea cădea pe cheia străină (eroare internă) sau lăsa reevaluarea pe un mijloc inexistent. Acum: refuz
    numit, chiar confirmat; registrul rămâne. MUTAȚIA: `if refuz_inlocuire(vechi)` scos -> ForeignKeyViolation / fără ValueError."""
    mf.importa(conn, M1)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO mijloace_fixe_jurnal (mijloc_id, camp, valoare_veche, valoare_noua, user_id) "
                    "SELECT id, 'destinatie_cd', 'false', 'true', 7 FROM mijloace_fixe")
    with pytest.raises(ValueError) as e:
        mf.importa(conn, M2, inlocuieste=True)
    assert not isinstance(e.value, migrare_api.InlocuireNeconfirmata)
    assert str(e.value).startswith("Registrul existent nu se poate înlocui prin import: 1 mijloc fix are reevaluări sau schimbări "
                                   "consemnate pe fișă (100)"), str(e.value)
    assert _unu(conn, "SELECT count(*) FROM mijloace_fixe") == (1,)


# ── istoricul declarațiilor preluat ─────────────────────────────────────────────────────────────────────────────────────────────
def test_def_426_istoricul_al_doilea_import_cere_confirmare_si_numeste_depunerile(conn):
    """ROȘU înainte: DELETE sursa='migrare' + INSERT tăcut (proba: istoricul de 2 declarații devenea 1). MUTAȚIA: poarta scoasă din
    `istoric_declaratii_import_api.importa` -> DID NOT RAISE."""
    ist.importa(conn, T, I1)
    with conn.cursor() as cur:
        # fixtura-sintetica-ok: tenant sintetic T = 990426 (nicio firmă reală), tranzacția fixturii `conn` se anulează (ROLLBACK)
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa) VALUES (%s, 2025, 9, 'd300', 'iconta')", (T,))
    with pytest.raises(migrare_api.InlocuireNeconfirmata) as e:
        ist.importa(conn, T, I2)
    # comanda 10.1: ce există (declarații, perioade) și ce aduce fișierul + datele dependente (depunerile prin iConta din anii istoricului)
    assert str(e.value) == (
        "Firma are deja un istoric de declarații preluat: 2 declarații (D100, D300), din 03/2025 până în 06/2025. Fișierul nou: 1 "
        "declarație (D300), pe 06/2025. Salvarea înlocuiește istoricul preluat; declarațiile depuse prin iConta rămân. În anul 2025 s-a "
        "depus o declarație prin iConta: termenele, restanțele și suma D100 deja declarată pe trimestrele anterioare se socotesc pe "
        "istoricul nou. Confirmă înlocuirea și salvează din nou."), str(e.value)
    assert _unu(conn, "SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id=%d AND sursa='migrare'" % T) == (2,)
    assert ist.importa(conn, T, I2, inlocuieste=True)["importati"] == 1
    assert _unu(conn, "SELECT count(*) FILTER (WHERE sursa='migrare'), count(*) FILTER (WHERE sursa='iconta') "
                      "FROM public.declaratii_depuse WHERE tenant_id=%d" % T) == (1, 1)


# ── fișele salariaților ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_426_salariatii_existenti_se_actualizeaza_numai_confirmat(conn):
    """ROȘU înainte: ON CONFLICT (cnp) DO UPDATE tăcut (proba: POPESCU devenea POPA, salariul 5.000 -> 7.000). MUTAȚIA: poarta scoasă din
    `salariati_import_api.importa` -> DID NOT RAISE."""
    si.importa(conn, [_sal(CNP1, "POPESCU", 5000)])
    with conn.cursor() as cur:
        cur.execute("INSERT INTO state_plata (salariat_id, luna, venit_brut) SELECT id, '2026-09-01', 5000 FROM salariati")
    with pytest.raises(migrare_api.InlocuireNeconfirmata) as e:
        si.importa(conn, [_sal(CNP1, "POPA", 7000), _sal(CNP2, "IONESCU", 4000)])
    # comanda 10.1: cine există deja și ce se rescrie + datele dependente (statele de plată deja emise)
    assert str(e.value) == (
        "Firma are deja 1 salariat; din cei 2 din fișier, unul există deja după CNP: POPESCU ANA. Salvarea îi actualizează fișa cu datele "
        "din fișier — numele, data angajării, codul COR, casa de sănătate, norma, persoanele în întreținere, scutirea, funcția de bază și "
        "salariul de bază de la data angajării (un câmp lipsă din fișier și IBAN-ul gol nu șterg ce era). Pentru acest salariat este deja "
        "emis un stat de plată (pe 09/2026), calculat pe fișa veche. Confirmă înlocuirea și salvează din nou."), str(e.value)
    assert _unu(conn, "SELECT count(*), min(nume) FROM salariati") == (1, "POPESCU")
    rez = si.importa(conn, [_sal(CNP1, "POPA", 7000), _sal(CNP2, "IONESCU", 4000)], inlocuieste=True)
    assert rez["importati"] == 2 and rez["actualizati"]["nume"] == ["POPESCU ANA"]
    assert _unu(conn, "SELECT nume FROM salariati WHERE cnp = '%s'" % CNP1) == ("POPA",)


def test_426_prima_preluare_nu_cere_confirmare(conn):
    """O firmă fără date: niciun import nu cere confirmare (poarta e numai pe înlocuire)."""
    assert sp.importa(conn, P1, "2025-12-31")["inlocuita"] is None
    assert mf.importa(conn, M1)["inlocuit"] is None
    assert ist.importa(conn, T, I1)["inlocuit"] is None
    assert si.importa(conn, [_sal(CNP1, "POPESCU", 5000)])["actualizati"] is None


# ── use-case-urile: 409 la salvare, același text la previzualizare ─────────────────────────────────────────────────────────────
def test_426_salvarile_raspund_409_fara_confirmare(conn, uc):
    """`InlocuireNeconfirmata` -> `erori.Conflict` (409) în fiecare use-case de salvare; cu `inlocuieste` -> scris. MUTAȚIA: handlerul
    `except migrare_api.InlocuireNeconfirmata` scos dintr-un use-case -> DateInvalide (422), nu Conflict -> pică."""
    import main
    from core import erori
    _balanta_4111(conn)
    sp.importa(conn, P1, "2025-12-31")
    mf.importa(conn, M1)
    ist.importa(conn, T, I1)
    si.importa(conn, [_sal(CNP1, "POPESCU", 5000)])
    cazuri = [
        (uc.parteneri_salveaza, main.ParteneriIn(randuri=[main.PartenerRand(**r) for r in P2], data_referinta="2025-12-31"),
         "Firma are deja solduri pe parteneri", "randuri"),
        (uc.mijloace_import_salveaza, main.MijloaceFixeImportIn(randuri=[main.MijlocFixRand(**r) for r in M2]),
         "Firma are deja un registru de mijloace fixe", "importati"),
        (uc.istoric_import_salveaza, main.IstoricDeclImportIn(randuri=[main.IstoricDeclRand(**r) for r in I2]),
         "Firma are deja un istoric de declarații preluat", "importati"),
        (uc.salariati_import_salveaza, main.SalariatiImportIn(randuri=[main.SalariatRand(**_sal(CNP1, "POPA", 7000))]),
         "Firma are deja 1 salariat", "importati"),
    ]
    for f, corp, inceput, cheie in cazuri:
        with pytest.raises(erori.Conflict) as e:
            f(T, corp, {"uid": 7})
        assert str(e.value).startswith(inceput) and str(e.value).endswith(migrare_api.CERE_CONFIRMAREA), (f.__name__, str(e.value))
        corp.inlocuieste = True
        assert f(T, corp, {"uid": 7})[cheie] >= 1, f.__name__


def test_426_previzualizarile_spun_ce_exista_inainte(conn, uc):
    """Previzualizarea fiecărui import întoarce `existenta` + `avertisment_inlocuire` (același text ca refuzul, fără fraza de final), pe
    rândurile care intră. MUTAȚIA: `avertisment_inlocuire` scos dintr-o previzualizare -> KeyError / None -> pică."""
    _balanta_4111(conn)
    sp.importa(conn, P1, "2025-12-31")
    mf.importa(conn, M1)
    ist.importa(conn, T, I1)
    si.importa(conn, [_sal(CNP1, "POPESCU", 5000)])
    # „același text ca refuzul, fără fraza de final”: refuzul salvării pe aceleași rânduri (P2), în aceeași stare a firmei — al cărui
    # text întreg (vechi 2 parteneri / nou 1 partener, debit 2.500,00 lei) e fixat de `test_def_426_parteneri_al_doilea_import_cere_confirmare`
    with pytest.raises(migrare_api.InlocuireNeconfirmata) as refuz:
        sp.importa(conn, P2, "2025-12-31")
    r = json.loads(uc.parteneri_incarca(T, "cont;cui;denumire;sold debitor;sold creditor\n4111;RO18189442;ALT CLIENT;2500;0\n".encode(),
                                        "p.csv", {"uid": 7}).body)
    assert r["existenta"]["randuri"] == 2
    assert "%s %s" % (r["avertisment_inlocuire"], migrare_api.CERE_CONFIRMAREA) == str(refuz.value), r["avertisment_inlocuire"]
    csv_mf = ("cod;denumire;valoare;durata;data pif;metoda;cont imobilizare;cont amortizare\n"
              "200;Server;12000;36;10.01.2025;liniara;2141;2814\n").encode()
    r = json.loads(uc.mijloace_import_incarca(T, csv_mf, "mf.csv", {"uid": 7}).body)
    assert r["existenta"]["randuri"] == 1 and r["inlocuire_refuzata"] is None
    assert r["avertisment_inlocuire"].startswith("Firma are deja un registru de mijloace fixe: 1 mijloc fix, valoare de intrare 6.000,00")
    with pytest.raises(migrare_api.InlocuireNeconfirmata) as refuz:     # refuzul salvării pe aceleași rânduri (I2), în aceeași stare
        ist.importa(conn, T, I2)
    r = uc.istoric_inlocuire(T, [dict(x, rand_fisier=i) for i, x in enumerate(I2, start=2)], [], {"uid": 7})
    assert r["existenta"]["randuri"] == 2
    assert "%s %s" % (r["avertisment_inlocuire"], migrare_api.CERE_CONFIRMAREA) == str(refuz.value), r["avertisment_inlocuire"]
    assert str(refuz.value).startswith(   # ce aduce fișierul: „Fișierul nou: 1 declarație (D300), pe 06/2025.”
        "Firma are deja un istoric de declarații preluat: 2 declarații (D100, D300), din 03/2025 până în 06/2025. Fișierul nou: 1 "
        "declarație (D300), pe 06/2025."), str(refuz.value)
    csv_sal = ("nume;prenume;cnp;data angajare;norma;ore pe zi;brut;judet;functie de baza;persoane in intretinere;"
               "scutit contributie minima\nPOPA;ANA;%s;2024-01-15;intreaga;8;7000;B;da;0;nu\n" % CNP1).encode()
    r = json.loads(uc.salariati_import_incarca(T, csv_sal, "s.csv", {"uid": 7}).body)
    assert r["existenta"]["nume"] == ["POPESCU ANA"], r.get("erori")
    assert r["avertisment_inlocuire"].startswith("Firma are deja 1 salariat; salariatul din fișier există deja după CNP: POPESCU ANA.")
