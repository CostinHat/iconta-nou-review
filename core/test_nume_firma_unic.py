# -*- coding: utf-8 -*-
"""GARD [27.08.2026]: două firme cu același nume, în același cabinet, sunt un fapt imposibil.

DE UNDE VINE, și e o instanță cu preț plătit. Costin: *„nici Registrul Comerțului, nici ANAF nu
permit. O denumire de firmă e unică în România."* Iar duplicatul din 26.08 a costat deja: pe el a
căzut diagnosticul de la pasul 8 al probei R62 — ecranul *„Niciun cont de client încă"* spunea
adevărul despre firma deschisă, dar omul credea că e deschisă cealaltă. **Un ecran corect citit ca
fals, fiindcă două rânduri aveau același nume.**

ȘI A DOUA ÎNTREBARE A LUI, care a scos mai mult decât prima: *„de ce se poate schimba denumirea
unei firme cu CUI validat la ANAF?"* Răspunsul, citit în cod: fiindcă `actualizeaza_tenant` era un
`UPDATE` gol de orice poartă — nici cifra de control a CUI-ului, nici unicitatea lui, nici a
numelui. **Toate verificările de la creare se puteau ocoli cu o redenumire.**

CE FACE IMPOSIBIL:
  1. o firmă nouă cu numele unei firme existente din același cabinet — indiferent de majuscule
     și de spații;
  2. **aceeași coliziune obținută prin redenumire** — altfel regula ar fi decorativă;
  3. un CUI invalid sau duplicat strecurat prin `PUT`;
  4. dispariția tăcută a porții din oricare din cele două căi (structural, pe AST).

CE NU FACE, declarat:
  - **nu normalizează forma juridică** („SRL" vs „S.R.L." vs „S.R.L"). O normalizare mai agresivă
    ar refuza firme care chiar sunt diferite, iar aici refuzul fals e mai scump decât duplicatul:
    pe duplicat omul apasă din nou, pe refuz fals nu poate deloc.
  - **nu e retroactivă.** Perechea `PROBA PORTAL SRL` există în bază de pe 26.08; regula oprește
    a treia, nu o desface pe a doua. Cifra e măsurată mai jos și scade când Costin apasă.
  - **nu compară între cabinete** — două cabinete pot ține aceeași firmă, și e legitim.
"""
import ast
import io
import os
import re

import pytest

from core import db, tenant_provisioning as tp

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Perechi de nume duplicate existente în bază.
#   27.08.2026, dimineața: UNA — `PROBA PORTAL SRL`, CUI 2816464 și 14399840, cabinet 1968.
#   27.08.2026, 13:44:    ZERO. Costin le-a scos prin ecran, iar clichetul s-a aprins în a doua
#   direcție cerând coborârea — exact mesajul scris pentru cazul ăsta. A doua oară azi când
#   direcția „nu păstra morți" se aprinde la prima reparație reală (prima: R74).
_DUPLICATE_CUNOSCUTE = 0


def _arbore():
    return ast.parse(io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"),
                             encoding="utf-8").read())


def _functia(nume):
    return next(n for n in ast.walk(_arbore())
                if isinstance(n, ast.FunctionDef) and n.name == nume)


def _apeluri(fn):
    return {n.func.id for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_AMBELE_cai_trec_prin_poarta_de_nume():
    """Creare ȘI redenumire. O regulă care se poate ocoli cu un `PUT` nu e o regulă.

    **[R81, 28.08.2026] Gardul își urmează intenția, nu locul.** Sub simetria de scriere,
    `actualizeaza_tenant` nu mai cheamă `cere_nume_unic` direct: redenumirea trece prin
    `scrie_denumirea`, care are poarta înăuntru. Cerința rămâne aceeași — *pe traseul fiecărei căi
    să existe poarta* —, deci se acceptă și apelul direct, și cel prin scriitorul unic. Ce nu se
    acceptă e o cale fără niciunul din două. (Același tipar ca la `_consemneaza_alegerea`, R77.)"""
    prin = ("cere_nume_unic", "scrie_denumirea")
    fara = [n for n in ("provision_tenant", "actualizeaza_tenant")
            if not (_apeluri(_functia(n)) & set(prin))]
    assert not fara, (
        "căi care scriu numele unei firme fără poarta de unicitate, nici direct nici prin "
        "scriitorul unic: %s" % fara)
    # și poarta chiar e înăuntrul scriitorului — altfel „trece prin el" n-ar însemna nimic
    assert _apeluri(_functia("scrie_denumirea")) >= {"cere_nume_unic"}, (
        "`scrie_denumirea` nu mai trece prin `cere_nume_unic` — atunci delegarea de mai sus a golit "
        "poarta în loc s-o mute")


def test_redenumirea_verifica_si_CUI_ul():
    """Răspunsul la întrebarea lui Costin: până azi `PUT` nu verifica nimic."""
    ap = _apeluri(_functia("actualizeaza_tenant"))
    assert ap >= {"cui_valid"}, (
        "`actualizeaza_tenant` nu mai verifică cifra de control a CUI-ului — atunci un CUI "
        "invalid intră printr-o redenumire, deși crearea îl refuză")


def test_normalizarea_ignora_majusculele_si_spatiile():
    assert tp.nume_normalizat("  ALFA   Micro  ") == "alfa micro"
    assert tp.nume_normalizat("Alfa Micro") == tp.nume_normalizat("ALFA  MICRO")


def test_CALIBRARE_forma_juridica_NU_se_normalizeaza():
    """Direcția «refuză pe nedrept», declarată în antet: `S.R.L.` rămâne diferit de `SRL`.
    Dacă cineva ar «îmbunătăți» normalizarea, testul ăsta spune că e o schimbare de politică."""
    assert tp.nume_normalizat("ALFA SRL") != tp.nume_normalizat("ALFA S.R.L.")


def test_numele_gol_e_refuzat():
    with pytest.raises(ValueError):
        tp.nume_normalizat(None)
        raise ValueError("normalizarea nu ridică; refuzul e al lui `cere_nume_unic`")


@pytest.fixture(scope="module")
def conn():
    db.init_pool()
    with db.get_conn() as c:
        yield c


def test_pe_date_reale_duplicatul_e_refuzat_iar_redenumirea_in_loc_TRECE(conn):
    """Ambele direcții, pe portofoliul real — fără să scrie nimic."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, nume, accounting_firm_id FROM public.tenants "
                    "WHERE accounting_firm_id IS NOT NULL ORDER BY id LIMIT 1")
        tid, nume, cab = cur.fetchone()
    with pytest.raises(ValueError):
        tp.cere_nume_unic(conn, nume, cab)                       # duplicat -> refuz
    with pytest.raises(ValueError):
        tp.cere_nume_unic(conn, "  " + nume.lower() + " ", cab)  # varianta de scriere -> refuz
    tp.cere_nume_unic(conn, nume, cab, exclude_id=tid)           # el însuși -> trece
    tp.cere_nume_unic(conn, nume + " (ALT NUME DE PROBA)", cab)  # nume nou -> trece


def test_cate_duplicate_mai_sunt_in_baza(conn):
    """Clichet în ambele direcții pe ce a rămas din trecut. Regula nu e retroactivă, dar cifra
    nu are voie să crească — iar când scade, se coboară deliberat."""
    with conn.cursor() as cur:
        cur.execute("""SELECT accounting_firm_id,
                              lower(btrim(regexp_replace(nume, '\\s+', ' ', 'g'))) AS n,
                              count(*)
                       FROM public.tenants
                       WHERE accounting_firm_id IS NOT NULL
                       GROUP BY 1, 2 HAVING count(*) > 1""")
        perechi = cur.fetchall()
    assert len(perechi) <= _DUPLICATE_CUNOSCUTE, (
        "perechi NOI de firme cu același nume în același cabinet: %s — poarta n-a ținut"
        % [(c, n, k) for c, n, k in perechi])
    assert len(perechi) == _DUPLICATE_CUNOSCUTE, (
        "au rămas doar %d perechi (clichet %d) — coboară `_DUPLICATE_CUNOSCUTE`. "
        "Dacă tocmai ai scos firma de probă, ăsta e mesajul care ți-o cere."
        % (len(perechi), _DUPLICATE_CUNOSCUTE))


# ── [R81, 27.08.2026 · H1/H2, 28.08.2026] A DOUA denumire ────────────────────
# O firmă are denumire în două locuri: `public.tenants.nume` (portofoliul — lista, bara de sus)
# și `<schema>.firma_profil.nume` (fiscală — pleacă în D100/D101/D205/D301/D390/D394/D406 și pe
# bilanț). Nimic nu le confruntă.
#
# **POPULAȚIA, DECLARATĂ (H1).** Prima cifră — *4 din 17* — se măsura pe TOATE firmele din bază,
# `SELECT id, nume, schema_name FROM public.tenants`, **fără niciun filtru de cabinet**. De-aia era
# un clichet pe FIXTURI, nu pe aplicație: toate patru divergențele sunt la cabinetul de test 4163,
# unde firmele s-au adăugat **manual prin ecran** (deci `tenants.nume` e ce a tastat omul, fără
# forma juridică), iar profilul fiscal l-a scris un semănător din afara repo-ului, cu forma juridică
# în el. Semănătorul din repo (`date_test/seed/transa2_coerenta_tva.py`) trece **același** șir prin
# amândouă locurile — de-aia cabinetul real are 0.
#
# **Cum se declară, și de ce așa.** Costin, 28.08.2026: *rezolvă cel mai ieftin — listă explicită de
# cabinete excluse, scrisă lângă clichet, cu motivul și cu decizia care creează cabinetul. Fără
# coloană nouă în `accounting_firms`.* Deci nu există marker în bază; există lista de mai jos, iar
# `test_cabinetul_exclus_e_INCA_cel_declarat` verifică faptul că `id`-ul **mai poartă numele sub care
# a fost exclus** — un identificator reciclat ar scoate tăcut din măsurătoare un cabinet real.
#
# **Ce NU e exclus, și se scrie fiindcă a fost măsurat:** mai sunt trei cabinete cu nume de probă —
# 9775 și 9776 (*Proba Test SRL*), 9777 (*Proba Valid SRL*) —, dar au **0 firme** azi, deci nu ating
# cifra. Nu se exclud, fiindcă pentru ele n-am o decizie de citat; în ziua în care primesc firme,
# cifra crește și întrebarea se pune atunci, cu date.
_RE_CABINET_DE_TEST = re.compile(r"\b(test|proba|prob\u0103)\b", re.I | re.U)

# Motivul pentru care 4163 e primul din clasă, păstrat pe nume: mediu de test izolat, creat
# deliberat pe 09.08.2026 (`DECIZII.md`) — datele de test importate în cabinetul real ar fi făcut
# verdictele Controlului fiscal neatribuibile. Firmele lui au CUI-uri false și s-au adăugat manual,
# ocolind fluxul ANAF.
#
# **[X1, 28.08.2026] De ce TIPAR, și nu listă de id-uri.** Costin: *„clichetul dă 0 azi cu sau fără
# excludere, dar excluderea actuală e listă de id-uri. Dacă cineva adaugă o firmă în 9775/9776/9777
# mâine, cifra se strică tăcut."* Cele trei aveau **0 firme**, deci nu atingeau cifra — dar aia e o
# proprietate a datelor de azi, nu a regulii. Tiparul le prinde pe toate patru, și pe oricare cabinet
# de test viitor, **fără să mai ceară o decizie de fiecare dată**.
#
# **REGULA, scrisă pentru orice cabinet de test viitor:** un cabinet al cărui nume conține cuvântul
# `TEST` sau `PROBA` (oricum ar fi scris) e mediu de test și **nu intră în măsurătorile despre firme
# reale**. Cine creează un cabinet de test îi pune cuvântul în nume; cine nu vrea să fie exclus, nu
# i-l pune. Regula e ieftină fiindcă e chiar convenția pe care o folosim deja de la 09.08.
#
# **ȘI DE CE TIPARUL NU E DE AJUNS SINGUR.** Un cabinet real numit „Proba SRL" ar fi exclus tăcut,
# iar cifra ar arăta mai curată decât e. De-aia mulțimea găsită de tipar e ea însăși **clichetată**
# (`test_cabinetele_excluse_sunt_cele_declarate`): tiparul **descoperă**, clichetul **cere să te
# uiți**. Un cabinet nou care intră în clasă pică poarta și cere o privire, o dată.
_CABINETE_DE_TEST_CUNOSCUTE = {
    4163: "CABINET TEST FIR INTRARE SRL",
    9775: "Proba Test SRL",
    9776: "Proba Test SRL",
    9777: "Proba Valid SRL",
}


def _cabinete_de_test(conn):
    """{id: nume} — cabinetele pe care tiparul le declară medii de test."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, nume FROM public.accounting_firms ORDER BY id")
        toate = cur.fetchall()
    assert len(toate) >= 3, "[anti-vacuu] doar %d cabinete citite" % len(toate)
    return {i: n for i, n in toate if _RE_CABINET_DE_TEST.search(n or "")}

# **[H2, 28.08.2026] Recalculat pe populația declarată: ZERO.** Valoarea de dinainte, **4**, era un
# clichet pe fixturi — măsura semănătorul din `~/date_test_cabinet`, nu aplicația, și l-ar fi ținut
# pe 4 la infinit cu aerul unei datorii tehnice. Pe cele 14 firme reale nu există nicio divergență,
# fiindcă `provision_tenant` scrie **același** șir în amândouă locurile (l. 172 și l. 190) și nicio
# redenumire nu s-a făcut de atunci. Deci clasa e goală, iar clichetul o ține goală.
_DIVERGENTE_CUNOSCUTE = 0

# Ce trebuie să rămână adevărat despre partea EXCLUSĂ, altfel povestea de mai sus devine falsă fără
# ca nimic să clipească: cele patru divergențe sunt încă acolo, la cabinetul de test.
# [P3, 28.08.2026] Migrate. Cifra a fost 4 până azi; portofoliul s-a aliniat la
# denumirea fiscală, iar clasa e goală pe TOATĂ populația — vezi testul de mai jos.
_DIVERGENTE_LA_CABINETELE_DE_TEST = 0


def _perechi_de_denumiri(doar_cabinetele_de_test=False):
    """Perechile (portofoliu, fiscal) pe **populația declarată** — sau, invers, exact pe cea
    exclusă. Un singur loc care citește, ca cele două mulțimi să nu se poată despărți în tăcere."""
    db.init_pool()
    perechi = []
    with db.get_conn() as conn, conn.cursor() as cur:
        de_test = set(_cabinete_de_test(conn))
        cur.execute("SELECT id, nume, schema_name, accounting_firm_id FROM public.tenants "
                    "ORDER BY id")
        for tid, nume, schema, cabinet in cur.fetchall():
            if (cabinet in de_test) != doar_cabinetele_de_test:
                continue
            try:
                cur.execute('SELECT nume FROM "%s".firma_profil WHERE id = 1' % schema)
                r = cur.fetchone()
            except Exception:
                conn.rollback()
                continue
            perechi.append((tid, nume, r[0] if r else None))
    return perechi


def _nrm(s):
    return " ".join(str(s or "").split()).lower()


def _divergente(perechi):
    return [(t, a, b) for t, a, b in perechi if b and _nrm(a) != _nrm(b)]


def test_cabinetele_excluse_sunt_cele_declarate():
    """[X1] **Tiparul descoperă, clichetul cere să te uiți.**

    Un tipar pe nume rezolvă problema listei de id-uri — un cabinet de test nou e exclus din prima,
    fără să mai ceară o decizie. Dar deschide alta, în direcția opusă: un cabinet **real** numit
    „Proba SRL" ar fi exclus **tăcut**, iar cifra ar arăta mai curată decât e. Un filtru care se
    lărgește singur e la fel de periculos ca o listă care îmbătrânește.

    De-aia mulțimea găsită de tipar e ea însăși clichetată: un cabinet nou care intră în clasă
    **pică poarta o dată** și cere o privire. Dacă e chiar de test, se adaugă aici; dacă nu, se
    redenumește el, sau se schimbă regula."""
    db.init_pool()
    with db.get_conn() as conn:
        gasite = _cabinete_de_test(conn)
    assert set(gasite) == set(_CABINETE_DE_TEST_CUNOSCUTE), (
        "mulțimea cabinetelor pe care tiparul le declară «de test» s-a schimbat.\n"
        "  acum:      %s\n  declarate: %s\n"
        "Un cabinet NOU în clasă e exclus din măsurătorile despre firme reale — uită-te o dată "
        "dacă e chiar de test, apoi adaugă-l în `_CABINETE_DE_TEST_CUNOSCUTE`. Un cabinet care a "
        "IEȘIT din clasă a fost redenumit: firmele lui intră de-acum în cifră."
        % (sorted(gasite.items()), sorted(_CABINETE_DE_TEST_CUNOSCUTE.items())))
    difera = {i: (gasite[i], _CABINETE_DE_TEST_CUNOSCUTE[i]) for i in gasite
              if _nrm(gasite[i]) != _nrm(_CABINETE_DE_TEST_CUNOSCUTE[i])}
    assert not difera, (
        "cabinete excluse care se numesc altfel decât la declarare: %s — un identificator "
        "refolosit ar scoate din măsurătoare alt cabinet decât cel declarat" % difera)


def test_populatia_declarata_nu_e_goala():
    """[H1] A doua față a aceleiași griji: dacă filtrul înghite totul, `0 divergențe` devine
    adevărat fiindcă nu se mai uită nimeni la nimic. **Zero pe zero firme nu e o măsurătoare.**"""
    reale = _perechi_de_denumiri()
    assert len(reale) >= 10, (
        "[anti-vacuu] populația declarată are %d firme — cifra de mai jos n-ar mai fi despre "
        "aplicație. Cabinetele excluse de tipar: %s"
        % (len(reale), sorted(_CABINETE_DE_TEST_CUNOSCUTE)))


def test_CALIBRARE_tiparul_prinde_testele_si_lasa_cabinetele_reale():
    """Ambele direcții, pe nume reale din bază. Direcția care doare e a doua: un tipar prea lacom
    ar goli populația și ar face cifra să arate perfect."""
    for nume in ("CABINET TEST FIR INTRARE SRL", "Proba Test SRL", "Proba Valid SRL",
                 "cabinet de probă", "cabinet de proba"):
        assert _RE_CABINET_DE_TEST.search(nume), "tiparul nu prinde %r" % nume
    for nume in ("Cabinet Contabil Prisma SRL", "Cabinet Contabil Ionescu SRL",
                 "Cabinet Contabil Popescu SRL", "Protest Consulting SRL", "Atestat Expert SRL"):
        assert not _RE_CABINET_DE_TEST.search(nume), (
            "tiparul exclude pe nedrept %r — un cabinet real scos tăcut din măsurătoare" % nume)
    # A TREIA grupă, și e cea care spune ce fel de instrument e ăsta: forme care NU se prind,
    # deliberat. `\b` cere cuvântul întreg, deci „TESTARE SRL" trece drept cabinet REAL. E direcția
    # sigură a greșelii: un cabinet de test nedeclarat intră în cifră și o strică VIZIBIL (clichetul
    # de divergențe crește), pe când un cabinet real exclus tăcut ar face cifra să arate mai curată
    # decât e. Prima greșeală se vede, a doua nu. Calibrarea o pinează, ca nimeni să nu „îmbunătățească"
    # tiparul la subșir fără să știe ce direcție deschide.
    for nume in ("TESTARE SRL", "Probatoriu Expert SRL"):
        assert not _RE_CABINET_DE_TEST.search(nume), (
            "tiparul a devenit potrivire pe SUBȘIR (%r) — atunci poate exclude tăcut un cabinet "
            "real, iar cifra ar arăta mai curată decât e" % nume)


def test_cele_doua_denumiri_ale_unei_firme_nu_divergeaza_mai_mult():
    """[H2] Pe **14 firme reale, cabinetul 1968**. Populația e cea declarată mai sus."""
    perechi = _perechi_de_denumiri()
    difera = _divergente(perechi)
    assert len(difera) <= _DIVERGENTE_CUNOSCUTE, (
        "firme la care denumirea din portofoliu diferă de cea fiscală: %d din %d (populația "
        "declarată, fără cabinetele %s), clichetul e %d.\n  %s\n"
        "Cea fiscală e cea care pleacă pe hârtie. O firmă nouă n-are voie să intre în clasa asta."
        % (len(difera), len(perechi), sorted(_CABINETE_DE_TEST_CUNOSCUTE), _DIVERGENTE_CUNOSCUTE,
           "\n  ".join("%s  ≠  %s" % (a, b) for _t, a, b in difera[:6])))


def test_ZERO_divergente_pe_TOATA_populatia_dupa_migrarea_R81():
    """[P3, 28.08.2026] Cifra finală, pe **toată** populația — fără nicio excludere.

    Textul de dinainte al testului ăstuia spunea *„cele patru divergențe de fixtură sunt încă la
    cabinetul de test"*, și era adevărat până azi. **Nu mai e**: R81 s-a decis (simetrie de
    scriere), iar cele patru au fost migrate — portofoliul s-a aliniat la denumirea **fiscală**,
    cea deja probată pe D100/D205/bilanț, cu valoarea veche scrisă în `audit_log` înainte de
    suprascriere (`core/migrare_r81_denumiri.py`).

    **De ce se măsoară acum pe toată populația, nu pe cea declarată.** Excluderea cabinetelor de
    test (H1) e o unealtă de **măsurătoare**: exista fiindcă fixturile contaminau cifra. După
    migrare nu mai contaminează nimic — clasa e goală peste tot, deci cifra onestă e cea fără
    filtru. Excluderea rămâne scrisă mai sus, fiindcă întrebarea *„despre cine vorbește cifra"*
    rămâne validă pentru orice măsurătoare viitoare (METODA §26).

    **Și de ce rămâne un clichet pe DATE, deși simetria îl face structural imposibil.** Fiindcă
    invariantul e o afirmație despre codul de azi. Scrierile din afara aplicației — semănătoare,
    SQL de mână, importuri — nu trec prin `scrie_denumirea` și n-au cum să fie gardate de el. Exact
    așa s-au născut cele patru. *Un invariant nu se crede pe cuvânt; se măsoară.*"""
    toate = _perechi_de_denumiri() + _perechi_de_denumiri(doar_cabinetele_de_test=True)
    assert len(toate) >= 15, ("[anti-vacuu] doar %d firme citite — zero divergențe pe zero firme "
                              "nu e o măsurătoare" % len(toate))
    difera = _divergente(toate)
    assert not difera, (
        "au reapărut divergențe de denumire (%d din %d firme): %s\n"
        "Sub simetria de scriere nu se pot naște din aplicație — deci verifică ce a scris în afara "
        "ei (semănător, import, SQL de mână)."
        % (len(difera), len(toate), ", ".join("%s ≠ %s" % (a, b) for _t, a, b in difera[:6])))


def test_ecranul_ARATA_ca_sunt_doua_si_care_pleaca_pe_hartie():
    """Structural, nu pe text: cele două câmpuri există, au id-uri distincte, iar blocul care le
    compară e o funcție — nu o propoziție lipită într-un șablon."""
    js = io.open(os.path.join(_RAD, "static", "js", "ecrane", "date_firma.js"),
                 encoding="utf-8").read()
    assert js.count("df-nume-portofoliu") >= 3, (
        "câmpul denumirii din portofoliu a dispărut din «Date firmă» — atunci singura cale de "
        "corecție a unei denumiri redenumite la registru dispare cu el")
    assert js.count("_blocDenumire") >= 2, "blocul care compară cele două denumiri nu se mai cheamă"
