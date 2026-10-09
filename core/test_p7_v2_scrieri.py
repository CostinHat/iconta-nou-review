# -*- coding: utf-8 -*-
"""GARDA V2 — nicio scriere și niciun control de tranzacție în corpul unei rute.

CE PĂZEȘTE. După V1, stratul HTTP nu mai citea. V2 a scos și restul: **140 de scrieri** (106 INSERT,
29 UPDATE dintre care unul construit dinamic, 5 DELETE) și **10 instrucțiuni de control de
tranzacție** (6 din familia `SAVEPOINT`, 4 `SET LOCAL search_path`). Cifra ținută aici e zero, pe
toate clasele.

CE **NU** S-A MUTAT, și e important: **proprietatea tranzacției**. Repository-ul primește cursorul
apelantului și nu comite nimic; `core/tranzactie.py` execută instrucțiunile de control pe același
cursor, la același loc în șir. Hotarele `commit`/`rollback` au rămas exact unde erau — contractul P4,
care nu se redeschide aici.

Mutanții ceruți de contract sunt toți mai jos: fiecare formă de scriere și de control, plus dovada
că textul „UPDATE" pe un obiect care nu e cursor nu produce fals pozitiv.
"""
from __future__ import annotations

import ast
import io
import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "scripts"))
sys.path.insert(0, RADACINA)

import scan_p7_straturi as S  # noqa: E402
from core import straturi as R  # noqa: E402

MODULE_V2 = ("repo_banca", "tranzactie")


def _in_ruta(sursa):
    """(gasite, necunoscute) pentru un fragment de rută scris de mână."""
    return S.d1_din_rute(S.rute_din_arbore(ast.parse(sursa), "proba.py"))


def _ruta_cu(instructiune):
    return '''
@app.post("/proba")
def proba(ctx=None):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(%s)
        return {}
''' % instructiune


# ============================================================
#  1. CLICHETUL — zero pe toate clasele
# ============================================================
def test_WRITE_SQL_IN_HTTP_ROUTE_e_zero():
    pe = S.d1_pe_fel()
    assert pe[S.WRITE] == [], (
        "au reapărut scrieri SQL în corpul rutelor: %s"
        % [(i.fisier, i.linie, i.cale) for i in pe[S.WRITE]][:10])


def test_TRANSACTION_CONTROL_IN_HTTP_ROUTE_e_zero():
    pe = S.d1_pe_fel()
    assert pe[S.TRANSACTION_CONTROL] == [], (
        "au reapărut instrucțiuni de control de tranzacție în rute: %s"
        % [(i.fisier, i.linie) for i in pe[S.TRANSACTION_CONTROL]][:10])


def test_D1_e_zero_pe_toate_clasele_si_UNKNOWN_ramane_zero():
    pe = S.d1_pe_fel()
    assert {k: len(v) for k, v in pe.items()} == {S.READ: 0, S.WRITE: 0,
                                                 S.TRANSACTION_CONTROL: 0, S.UNKNOWN: 0}


# ============================================================
#  2. MUTANȚII — fiecare formă, prinsă
# ============================================================
def test_mutant_INSERT_in_ruta():
    gasite, _ = _in_ruta(_ruta_cu('"INSERT INTO t (a) VALUES (%s)", (1,)'))
    assert len(gasite) == 1
    assert S.fel_sql("INSERT INTO t (a) VALUES (%s)") == (S.WRITE, "INSERT")


def test_mutant_UPDATE_in_ruta():
    gasite, _ = _in_ruta(_ruta_cu('"UPDATE t SET a=%s WHERE id=%s", (1, 2)'))
    assert len(gasite) == 1
    assert S.fel_sql("UPDATE t SET a=%s WHERE id=%s") == (S.WRITE, "UPDATE")


def test_mutant_DELETE_in_ruta():
    gasite, _ = _in_ruta(_ruta_cu('"DELETE FROM t WHERE id=%s", (1,)'))
    assert len(gasite) == 1
    assert S.fel_sql("DELETE FROM t WHERE id=%s") == (S.WRITE, "DELETE")


def test_mutant_CTE_care_SCRIE_in_ruta():
    """Un `WITH` care șterge e o scriere, oricât de citire ar părea la primul cuvânt."""
    sql = "WITH x AS (DELETE FROM t RETURNING id) SELECT * FROM x"
    gasite, _ = _in_ruta(_ruta_cu('"%s"' % sql))
    assert len(gasite) == 1
    assert S.fel_sql(sql) == (S.WRITE, "WITH_SCRIERE")


def test_mutant_SAVEPOINT_in_ruta():
    for sql in ("SAVEPOINT x", "RELEASE SAVEPOINT x", "ROLLBACK TO SAVEPOINT x"):
        gasite, _ = _in_ruta(_ruta_cu('"%s"' % sql))
        assert len(gasite) == 1
        assert S.fel_sql(sql) == (S.TRANSACTION_CONTROL, "SAVEPOINT")


def test_mutant_SET_LOCAL_search_path_in_ruta():
    sql = "SET LOCAL search_path TO x"
    gasite, _ = _in_ruta(_ruta_cu('"%s"' % sql))
    assert len(gasite) == 1
    assert S.fel_sql(sql) == (S.TRANSACTION_CONTROL, "SEARCH_PATH")


def test_scrierea_in_REPOSITORY_e_permisa():
    """Cealaltă direcție: aceeași instrucțiune, într-un modul fără rute, NU e item D1."""
    sursa = '''
def salveaza(cur, a):
    cur.execute("INSERT INTO t (a) VALUES (%s)", (a,))
'''
    assert S.rute_din_arbore(ast.parse(sursa), "core/repo_x.py") == []
    gasite, _ = S.d1_din_rute(S.rute_din_arbore(ast.parse(sursa), "core/repo_x.py"))
    assert gasite == []


def test_textul_UPDATE_pe_un_obiect_care_nu_e_cursor_nu_e_fals_pozitiv():
    gasite, necunoscute = _in_ruta(_ruta_cu('"UPDATE t SET a=1"').replace(
        "cur.execute(", "jurnal.execute("))
    assert gasite == [] and len(necunoscute) == 1


def test_ANTI_VACUUM_detectorul_inca_vede_rutele_si_repository_urile():
    """Zero e o veste bună doar dacă universul are obiecte și instrumentul mai vede ceva."""
    assert len(S.rute()) >= 400, "universul rutelor s-a golit"
    apeluri = _apeluri_catre_repository()
    assert apeluri >= 250, "apelurile către repository au dispărut: %d" % apeluri


# ============================================================
#  3. CONSERVAREA — nimic nu s-a pierdut pe drum
# ============================================================
def _apeluri_catre_repository():
    module = {f[:-3] for f in os.listdir(os.path.join(RADACINA, "core"))
              if f.startswith("repo_") or f == "tranzactie.py"}
    # [P7 · valul use-case] Apelurile catre straturile de sub HTTP stau acum si in
    # `core/uc_*.py`. Conservarea (257) e despre APLICATIE, nu despre un fisier — numarate
    # doar in `main.py` ies 72, adica lipsa a 185 de apeluri care n-au plecat nicaieri.
    from core import scan_sql_efectiv as _ef
    n = 0
    for _cale in _ef.straturi_aplicatie():
        arb = ast.parse(io.open(os.path.join(RADACINA, _cale), encoding="utf-8").read())
        for x in ast.walk(arb):
            if (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                    and isinstance(x.func.value, ast.Name) and x.func.value.id in module):
                n += 1
    return n


def test_numarul_de_instructiuni_se_conserva():
    """257 de instrucțiuni SQL stăteau în rute înainte de V1 (107 citiri + 150 scrieri/control).
    Acum sunt **262** de APELURI către straturile de sub HTTP — niciuna pierdută, niciuna dublată,
    plus cinci ADĂUGATE deliberat (R187: `vanzare_ic` fixează schema, fiindcă emite o factură;
    R59: cele patru apeluri prin care reevaluarea ajunge pe registru, la validarea notei).

    *Instrucțiunile din repository sunt mai puține decât apelurile (192), fiindcă 140 de poziții de
    scriere au doar 78 de texte SQL distincte: una singură apare de douăzeci și cinci de ori.*
    """
    # [R187, 16.09.2026] 257 -> 258, cu motivul: `vanzare_ic` a capatat un
    # `tranzactie.fixeaza_schema(cur, schema)`, cerut fiindca `emite_factura` foloseste INSERT
    # NECALIFICAT — aceeasi linie exista deja in `achizitie_ic`, din acelasi motiv. Nu e o
    # instructiune noua de SQL: e un apel de CONTROL, spre `tranzactie.py`, pe care numaratoarea il
    # include. *Clichetul urca fiindca aplicatia face un pas in plus, nu fiindca s-a pierdut ceva.*
    #
    # [R59, 16.09.2026] 258 -> 262, cu cele PATRU apeluri numite, ca sa nu fie o cifra fara continut:
    #   repo_reevaluari.consemneaza             — reevaluarea, consemnata langa ciorna
    #   repo_reevaluari.neaplicata_pentru_nota  — randul neaplicat al notei, la validare
    #   repo_mijloace_fixe.urca_valoarea        — coloana din registru urca (criteriul 1 al lui R59)
    #   repo_reevaluari.marcheaza_aplicata      — faptul devine aplicat, cu momentul lui
    # Niciuna nu muta SQL din alta parte: registrul chiar nu se atingea deloc pana acum, si tocmai
    # asta era restanta. *Clichetul urca fiindca aplicatia face patru pasi in plus, nu fiindca s-a
    # pierdut ceva — conservarea se probeaza de celelalte doua probe ale fisierului.*
    #
    # [B1, 17.09.2026, audit A1] 262 -> 263, cu apelul numit:
    #   repo_declaratii.cabinet_din_coada — poarta de APARTENENTA a lui `coada_depune` intreaba prin
    #   repository cine detine elementul de coada (cabinet_id), inainte sa atinga firma altui cabinet.
    # Nu muta SQL din alta parte: e o citire NOUA, ceruta ca use-case-ul sa nu execute el SELECT (P7).
    # *Clichetul urca fiindca aplicatia verifica un pas in plus (apartenenta), nu fiindca s-a pierdut ceva.*
    # [C2, 17.09.2026, audit C2] 263 -> 266, cu apelurile numite:
    #   tranzactie.savepoint_firma / elibereaza_firma / intoarce_la_firma — SAVEPOINT per firmă la
    #   importul în masă, ca o eroare la una (denumire prea lungă) să nu abortze tranzacția pentru
    #   celelalte și să nu lase commitul final să facă ROLLBACK tăcut peste tot. SQL-ul stă în modulul
    #   de tranzacție (nume literal, ca restul savepoint-urilor), nu în use-case.
    # [A12b, 19.09.2026, restanta R2] 266 -> 267, cu apelul numit:
    #   repo_facturi.actualizeaza_destinatii_linii — la validarea unei facturi primite din SPV,
    #   contabilul clasifica destinatia TVA per linie (taxabil/scutit/mixt); use-case-ul o persista
    #   prin repository, nu executand el UPDATE-ul (P7). SQL-ul (UPDATE factura_linii) sta in
    #   repo_facturi, nu in use-case. *Clichetul urca fiindca aplicatia face un pas in plus
    #   (clasificarea liniilor), nu fiindca s-a pierdut ceva.*
    # [DECIZII 65, 22.09.2026] 267 -> 268, cu apelul numit:
    #   repo_firma_profil.platitor_tva in achizitie_ic — contabilizarea IC (taxare inversa) devine
    #   constienta de platitor (neplatitor art.317 -> TVA in costul achizitiei, nu 4426=4427). Use-case-ul
    #   citeste statutul prin repository, nu executand el SELECT-ul (P7). *Clichetul urca fiindca aplicatia
    #   verifica un pas in plus (statutul de platitor), nu fiindca s-a pierdut ceva.*
    # [lot 19, 02.10.2026] 268 -> 271, cu apelurile numite:
    #   repo_contabilitate.adauga_z_cota ×2 (horeca_import_amef, horeca_raport_z) — defalcarea raportului Z pe cote,
    #   scrisă în aceeași tranzacție cu nota, ca D300 rd.9/10 s-o poată citi (nota 707/4427 n-o poartă);
    #   repo_salariati.suspendari_salariat (salariat_actualizeaza) — setul vechi de suspendări, ca poarta de
    #   perioadă să se aplice lunilor ATINSE de schimbare. Nu mută SQL din altă parte: pași NOI ai aplicației.
    # [D394 op2 Î1, decizia B, 02.10.2026] 271 -> 273, cu apelurile numite:
    #   repo_contabilitate.adauga_z_amef ×2 (horeca_import_amef, horeca_raport_z) — casa și numărul de bonuri ale
    #   raportului Z, în același rând pe ambele rute, ca D394 op2 Î1 să citească o singură sursă. Pași NOI.
    # [lot 19 defectul 11, 03.10.2026] 273 -> 274, cu apelul numit:
    #   repo_mijloace_fixe.seteaza_destinatie_cd (mijloc_fix_destinatie_cd) — bifa „C&D” din registru (CF art.20 alin.(1)
    #   lit.b)), ruta nouă PUT /mijloace-fixe/{id}/destinatie-cd. Pas NOU al aplicației, nu SQL mutat.
    # [D394 Î2, deciziile Costin 03.10.2026] 274 -> 278, cu apelurile numite:
    #   repo_firma_profil.amef_si_cont_venit ×2 (chitanta_emite, chitanta_cota) — bifa de exceptare AMEF + contul de venit;
    #   repo_casa.chitanta_de_clasificat + repo_casa.clasifica_vanzare (chitanta_cota) — ruta nouă PUT
    #   /chitante/{id}/cota: chitanța fără cotă devine vânzare (nota ciornă pe venit + 4427). Pași NOI, nu SQL mutat.
    # [testarea ca asistent, comanda Costin 04.10.2026 pct.3] 278 -> 279, cu apelul numit:
    #   repo_utilizatori.contul_dupa_email (tenant_creeaza) — emailul clientului se judecă ÎNAINTE de crearea firmei
    #   (o adresă cu alt rol se refuză pe câmp, firma nu se mai creează pe jumătate). Pas NOU, citire, nu SQL mutat.
    #   (În `asistent_creeaza`, `id_si_activ_dupa_email` -> `contul_dupa_email` și `creeaza_cont_de_client` ->
    #   `creeaza_cont_asistent` sunt ÎNLOCUIRI unu-la-unu, nu apeluri în plus.)
    # [fluxul de factură F1, comanda Costin 05.10.2026 pct.1a] 279 -> 280, cu apelul numit:
    #   repo_main.select_u (uc_auth.reinnoieste) — reînnoirea sesiunii verifică `sesiuni_valide_de` ca garda de cabinet
    #   (o sesiune invalidată de schimbarea parolei nu primește token nou). Pas NOU, citire, nu SQL mutat.
    # [fluxul de factură F1, comanda Costin 05.10.2026 pct.2–5] 280 -> 282, cu apelurile numite:
    #   repo_facturi.jurnalizeaza_cota_aleasa (facturi_emite) — cota schimbată de contabil față de cea propusă se consemnează
    #   (propus -> ales, cine, când) în aceeași tranzacție cu factura; repo_firma_profil.regim_tva_pentru_schimbare
    #   (firma_profil_regim_tva) — poarta de perioadă închisă se pune numai la o SCHIMBARE reală a statutului. Pași NOI.
    # [lotul 06.10.2026, comanda Costin §6.4] 282 -> 283, cu apelul numit:
    #   repo_firma_profil.jurnal_firma (firma_profil_date) — jurnalul Date firmă, vizibil cabinetului. Pas NOU, citire.
    # [validarea notelor, comanda Costin 06.10.2026 pct.1] 283 -> 286, cu apelurile numite (toate în `uc_coada`, citiri):
    #   repo_declaratii.element_coada (fel + firma elementului, pentru aprobare / conținut), repo_declaratii.
    #   schema_firmei_cabinetului (intrarea notelor în coadă, numai pe firmele cabinetului), repo_declaratii.nota_cu_linii
    #   (conținutul notei pentru validator). Pași NOI.
    # [validarea notelor, poarta de închidere 06.10.2026] 286 -> 287, cu apelul numit: repo_declaratii.nota_cu_linii
    #   (jurnal_retrimite) — retrimiterea citește nota ca să-i verifice existența și luna (R42) înainte de a o pune în coadă.
    #   Pas NOU, citire.
    # [lotul 07.10 pct.15, 06.10.2026] 287 -> 288, cu apelul numit: repo_contabilitate.id_nota_dupa_numar (tenant_stat_plata) —
    #   statul de plată arată la deschidere starea notei lunii în coada de validare (respingerea fără clic). Pas NOU, citire.
    # [lotul „Deciziile 07.10”, 08.10.2026] 288 -> 289, cu apelul numit: repo_contabilitate.nota_horeca_z_ciorna (horeca_raport_z) —
    #     raportul Z scris de mână e CIORNĂ la firma cantitativ-valorică (decizia pct.3), VALIDAT în rest: două apeluri explicite.
    # [lotul „Deciziile 08.10”, 08.10.2026] 289 -> 298, cu cele NOUĂ apeluri numite:
    #   repo_mijloace_fixe.seteaza_cod_catalog (mijloc_fix_cod_catalog) — W2, codul din Catalogul HG 2139/2004, scriere NOUĂ;
    #   repo_contabilitate.liniile_si_data (salarii_contare_propunere) — retest pct.1, ecranul spune „ciorna are alte sume”, citire;
    #   repo_contabilitate.punct_de_revenire + revino_la (salarii_contare_scrie) — retest pct.1, înlocuirea ciornei se retrage
    #     când noua notă are aceeași amprentă (SAVEPOINT; era SQL direct în use-case, mutat aici);
    #   repo_control_fiscal_api.select_depusa_curenta + insert_depusa_extern (control_fiscal_depusa_extern) — U2, „depusă în
    #     afara iConta”: verificarea depunerii existente și scrierea;
    #   repo_contabilitate.search_path_firma (controale_inchidere) — W2, registrul MF citit pe schema firmei (era SQL direct);
    #   repo_contabilitate.profil_tva + note_nevalidate_in_interval (poarta_d406_balanta) — V1, poarta D406 = rulajele balanței
    #     (fereastra D406 și câte ciorne explică diferența), două citiri NOI.
    # [lotul „Deciziile 08.10 §6”, 08.10.2026] 298 -> 301, cu apelurile numite:
    #   repo_contabilitate.documentul_notei (×2), punct_de_revenire, revino_la (tenant_amortizare) — §6 pct.6, clasa T1 (retest 08.10 pct.1): ciorna
    #     nevalidată a amortizării se înlocuiește (SAVEPOINT retras la aceeași amprentă), iar nota nouă preia tabloul ei;
    #   −1: repo_contabilitate.nota_horeca_z_validata (horeca_raport_z) scos — §6 pct.7 (R36), Z-ul tastat e ciornă la ambele metode;
    #   repo_contabilitate.profil_tva + note_nevalidate_in_interval (ciorne_in_perioada, din coada_adauga) — §6 pct.7, porțile
    #     D300/D394/D390/D406 dau avertisment, nu blocaj, când perioada fiscală are ciorne: două citiri NOI. Total 298 -> 303.
    # [lotul „Retest 08.10”, 08.10.2026] 303 -> 307, cu apelurile numite:
    #   repo_control_fiscal_api.select_depusa_curenta + insert_depusa_extern(sursa="contabil_anterior") (control_fiscal_depuse_anterior)
    #     — pct.9, „Marchează toate ca depuse de contabilul anterior”: o perioadă deja depusă nu se marchează peste;
    #   repo_control_fiscal_api.select_depusa_curenta + delete_marcari (control_fiscal_anuleaza_marcare) — pct.10, marcarea se poate
    #     anula (numai marcările; o depunere din iConta.eu rămâne). Total 303 -> 307.
    # [lotul „Retest 2”, 09.10.2026] 307 -> 312, cu apelurile numite (toate în ecranul planului de conturi, pct.13, decizia Costin O12):
    #   repo_contabilitate.conturi_folosite (tenant_plan_conturi_lista) — lista spune care cont e folosit în note;
    #   repo_contabilitate.denumirea_contului + conturi_folosite + toate_conturile + sterge_cont_din_plan
    #     (tenant_plan_conturi_sterge) — ștergerea: contul există, nu e folosit în note, nu are analitice; abia apoi se șterge.
    #   (citirea tenantului din `declaratii_nedepuse_cu_termen_in_luna`, pct.11, trece prin `repo_tenants` dintr-un ajutor, nu dintr-o rută.)
    assert _apeluri_catre_repository() == 312


def test_repository_urile_V2_nu_comit_si_nu_deschid_conexiuni():
    """Contractul P4: hotarele tranzacției rămân la apelant."""
    interzise = {"get_conn", "commit", "rollback", "HTTPException"}
    rele = []
    for f in sorted(os.listdir(os.path.join(RADACINA, "core"))):
        if not (f.startswith("repo_") or f == "tranzactie.py"):
            continue
        arb = ast.parse(io.open(os.path.join(RADACINA, "core", f), encoding="utf-8").read())
        for x in ast.walk(arb):
            if isinstance(x, ast.Call):
                fn = x.func
                nume = fn.id if isinstance(fn, ast.Name) else (
                    fn.attr if isinstance(fn, ast.Attribute) else None)
                if nume in interzise:
                    rele.append((f, x.lineno, nume))
    assert rele == [], "strat care depășește contractul: %s" % rele


def test_modulele_V2_sunt_declarate_in_registru():
    # multime, nu `in`: `>=` crapa pe un sir, `in` s-ar transforma tacut in sub-sir (METODA §23)
    assert R.module_din_strat(R.REPOSITORY) >= {"core/repo_banca.py"}
    assert R.module_din_strat(R.USE_CASE) >= {"core/tranzactie.py"}


# ============================================================
#  4. CAZUL DINAMIC (§6)
# ============================================================
def test_DYNAMIC_UPDATE_pastreaza_compunerea_in_apelant():
    """Singura scriere al cărei SQL se compune la rulare.

    Ce se cere: coloanele se aleg în RUTĂ (acolo e decizia contabilului), iar repository-ul le
    primește gata compuse, cu valorile în aceeași ordine. Dacă cineva ar muta compunerea în
    repository, funcția ar primi altceva decât două liste și proba asta ar pica.
    """
    arb = ast.parse(io.open(os.path.join(RADACINA, "core/repo_facturi.py"),
                            encoding="utf-8").read())
    f = [n for n in ast.walk(arb)
         if isinstance(n, ast.FunctionDef) and n.name == "actualizeaza_clasificarea"]
    assert f, "funcția dinamică a dispărut"
    argumente = [a.arg for a in f[0].args.args]
    assert argumente == ["cur", "schema", "bucati_set", "valori"], (
        "semnătura cazului dinamic s-a schimbat: %s" % argumente)
    # Conditia si absenta alegerii de coloane se cer pe STRUCTURA (§23): literalele din
    # argumentul `execute` al functiei, nu o cautare de text in fisier.
    apel = [n for n in ast.walk(f[0])
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "execute"]
    assert len(apel) == 1, "cazul dinamic are altceva decat o singura executie: %d" % len(apel)
    literale = [n.value for n in ast.walk(apel[0].args[0])
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    # Egalitate exacta pe multimea literalelor: spune si ce ramane fix (sablonul + conditia), si
    # ca NIMIC in plus nu s-a strecurat — deci niciun nume de coloana ales aici.
    assert sorted(set(literale)) == [" WHERE id=%s", ", ", ".facturi SET ", "UPDATE "], (
        "sablonul SQL compus s-a schimbat: %s" % sorted(set(literale)))
