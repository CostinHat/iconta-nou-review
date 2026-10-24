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
    # [lotul „Retestul plasei”, 09.10.2026] 312 -> 313, cu apelul numit: repo_contabilitate.profil_tva (uc_comun.
    #   _tva_balanta_sau_nu_se_aplica) — deficiența 211, coerența TVA față de balanță se spune „nu se aplică” la neplătitor: întâi se
    #   citește dacă firma e plătitoare de TVA. Pas NOU, citire.
    # [același lot] 313 -> 316, cu apelurile numite (planul de conturi, deficiențele 218 și 219):
    #   repo_contabilitate.conturi_cu_sold_initial (tenant_plan_conturi_lista + tenant_plan_conturi_sterge) — „niciun cont cu sold nu se
    #     șterge”: lista nu oferă „Șterge”, serverul refuză; repo_contabilitate.conturi_dupa_inceputul_simbolului (tenant_plan_conturi_lista)
    #     — „căutarea după simbol potrivește începutul”. Citiri NOI. (Lista citea planul de două ori fără căutare: o citire, refolosită.)
    # [lotul 2, 15.10.2026] 316 -> 317, cu apelul numit: repo_utilizatori.contul_dupa_email (uc_auth.invitatie_creeaza) — invitația nu
    #   se creează pentru un email care are deja cont (Conflict). Citire NOUĂ (comanda Costin 14.10.2026 pct.3).
    # [lotul 3, 15.10.2026] 317 -> 318, cu apelul numit: repo_contabilitate.ciorne_altui (uc_tenants.tenant_jurnal) — jurnalul îi
    #   arată asistentului care ciorne sunt ale altuia, cu aceeași funcție din bază ca refuzul (deficiența 246).
    # [lotul 4, 15.10.2026] 318 -> 322, cu apelurile numite (înregistrarea liberă cu confirmarea emailului, DECIZII „Lotul 4”):
    #   repo_utilizatori.contul_dupa_email x2 (uc_auth._register_liber, uc_auth.confirma_inregistrarea) — nicio cerere / niciun cont
    #   pentru un email care are deja cont (Conflict), citiri NOI; repo_utilizatori.scrie_acordul_termenilor (confirma_inregistrarea) —
    #   dovada acordului, în aceeași tranzacție cu contul creat la confirmare, scriere NOUĂ; repo_main.select_public_2
    #   (uc_auth._anunta_cabinet_nou) — emailul superadminului pentru anunțul de cabinet nou, citire NOUĂ.
    # [lotul 6, 16.10.2026] 322 -> 332, cu apelurile numite (DECIZII „Lotul 6”):
    #   repo_declaratii.inchide_asteptarea_deschisa + insereaza_asteptare (uc_coada.asteapta_notele) — 284, declarația care așteaptă
    #     validarea notelor numite se ține minte (o singură așteptare deschisă pe firmă / tip / perioadă), scrieri NOI;
    #   repo_declaratii.asteptari_deschise + revendica_asteptarea + scrie_rezultatul_asteptarii, repo_contabilitate.cate_nevalidate_dintre
    #     (uc_coada.reia_declaratiile_in_asteptare) — 284, după validarea notelor declarația se generează din nou și intră singură în
    #     coadă: citirea așteptărilor, revendicarea (o singură reluare), rezultatul; notele încă nevalidate. Pași NOI;
    #   repo_declaratii.autorul_elementului (uc_coada.coada_respinge) — 293, „Renunță” e al celui care a pregătit-o sau al celui care
    #     depune; citire NOUĂ;
    #   repo_facturi.actualizeaza_clasificarea (uc_tenants.factura_primita_valideaza) — 273c, tipul furnizorului și categoria art.331,
    #     cerute la validare, se scriu pe factură (D394); scriere NOUĂ;
    #   repo_firma_profil.cui_firma (uc_tenants.spv_stare_firma) — 273a, starea SPV a firmei se citește pe CUI-ul ei; citire NOUĂ;
    #   repo_contabilitate.search_path_firma (uc_tenants.tenant_amortizare_restanta) — 281, amortizarea lunilor rămase în urmă se
    #     generează pe schema firmei; apel de CONTROL NOU.
    # [lotul 7, 17.10.2026] 332 -> 334, cu apelurile numite (DECIZII „Comanda 7.2”):
    #   repo_declaratii.numele_utilizatorului (uc_coada._cine) — 297 / 299, elementul înlocuit („Înlocuiește”, „Generează din nou”)
    #     poartă motivul „Înlocuită de declarația generată din nou (<numele celui care a generat-o>)”; citire NOUĂ;
    #   repo_declaratii.autorul_elementului (uc_coada.coada_depune) — 320, cine a pregătit declarația află că a depus-o altcineva
    #     (notificarea „declarație depusă”); citire NOUĂ, după depunere, în afara tranzacției ei.
    # [lotul 9, 19.10.2026] 334 -> 339, cu apelurile numite (DECIZII „Comanda 9.1”):
    #   repo_firma_profil.profil_fiscal (uc_tenants.istoric_cu_perioada) — 389, perioada „T1/2026” din istoricul declarațiilor se scrie după
    #     profilul firmei (decontul, regimul); citire NOUĂ;
    #   repo_contabilitate.search_path_firma + repo_firma_profil.profil_fiscal (uc_tenants._z_in_rip) — 368, raportul Z la PFA intră în
    #     registrul de încasări și plăți: regimul firmei se citește pe schema ei; apel de CONTROL NOU + citire NOUĂ;
    #   repo_contabilitate.search_path_firma (uc_tenants.ajustari_fiscale_lista) — 378, rândurile luate din conturi (6581 -> rd.25) se
    #     citesc pe schema firmei; apel de CONTROL NOU;
    #   repo_d101.select_inregistrari_linii (uc_tenants.ajustari_fiscale_lista) — 378, rulajul 6581 al anului, arătat pe ecranul
    #     ajustărilor înainte de D100 / D101; citire NOUĂ (aceeași interogare ca generatorul D101, nu una paralelă).
    # [lotul 9, comenzile 9.2 / 9.3, 19.10.2026] 339 -> 342 (DECIZII „Comanda 9.2”, „Comanda 9.3”):
    #   repo_efactura.primita_pentru_validare (uc_tenants.factura_primita_valideaza) — 418a, citirea scurtă a facturii primite, ÎNAINTE
    #     de apelul ANAF (statutul furnizorului din XML și ANAF, cu conexiunea închisă); citire NOUĂ;
    #   repo_facturi.actualizeaza_conturi_linii (uc_tenants.factura_primita_valideaza) — 418b, contul fiecărei linii; scriere NOUĂ;
    #   repo_facturi.seteaza_act_identitate (uc_tenants.achizitie_neinregistrat) — 402, actul de identitate al vânzătorului PF pe
    #     borderou; scriere NOUĂ.
    # [lotul 10, comanda 10.1, 20.10.2026] 342 -> 349 (DECIZII „Comanda 10.1”):
    #   repo_contabilitate.documentul_notei (uc_reevaluare.reevaluare_valuta_genereaza) — 429, documentul ciornei înlocuite a lunii
    #     trece pe nota nouă; citire NOUĂ;
    #   repo_contabilitate.search_path_firma (uc_reevaluare.reevaluare_valuta_genereaza) — 429 / 430d, nota care păstrează documentul
    #     ciornei înlocuite se scrie pe schema firmei; apel de CONTROL NOU;
    #   repo_contabilitate.nota_cu_sursa_si_status (uc_reevaluare.reevaluare_valuta_genereaza) — 429 / 430d, nota de reevaluare cu
    #     documentul vechi; scriere NOUĂ;
    #   repo_contabilitate.nota_operatiune_ciorna (uc_reevaluare.reevaluare_valuta_genereaza) — 429 / 430d, nota de reevaluare propusă
    #     de aplicație, fără document vechi; scriere NOUĂ;
    #   repo_contabilitate.adauga_linie (uc_reevaluare.reevaluare_valuta_genereaza) — 429, rândurile notei (câte unul pe element în
    #     valută cu diferență); scriere NOUĂ;
    #   repo_contabilitate.adauga_linie_partener (uc_tenants.nota_asociati) — 430b, câte un rând de dividend pe fiecare asociat, cu
    #     asociatul ca partener; scriere NOUĂ;
    #   repo_contabilitate.dividende_nevalidate_din (uc_tenants._sursa_profitului) — 430a, dividendele încă nevalidate din contul de
    #     profit, rezervate din profitul disponibil; citire NOUĂ;
    #   repo_tenants.nume_si_cui_spatiat (uc_regim_tva_incasare._rtvai_firma) — 428, CUI-ul firmei pentru registrul ANAF al TVA la
    #     încasare; citire NOUĂ;
    #   MINUS repo_d101.select_inregistrari_linii (uc_tenants.ajustari_fiscale_lista) — 425, înlocuit cu `d101.rulaje_fereastra`
    #     (notele + rulajele preluate, aceeași bază ca generatorul D101), care nu e repository: −1.
    #   Neutre (aceeași numărătoare): `nota_facturi_ciorna` / `nota_facturi_ciorna_2` / `nota_banca_ciorna` / `nota_casa_ciorna` /
    #   `nota_salarii_ciorna` -> `nota_operatiune_ciorna` în 29 de use-case-uri (430d, sursa notei); `cate_nevalidate_dintre` mutat din
    #   `uc_coada.reia_declaratiile_in_asteptare` în funcția ei internă `_ramase` (firma ștearsă între timp). Nenumărat de instrument:
    #   `uc_declaratii.aduce_localitati_parteneri` -> `_repo_d406.parteneri_si_localitati` (C69), fiindcă e chemat printr-un alias
    #   (`_repo_d406`), nu prin numele modulului.
    # [lotul 10, prins de e2e 430, 20.10.2026] 349 -> 350:
    #   repo_contabilitate.search_path_firma (uc_tenants._dividend_propus) — 430, `dividende_impartire` / `nota_asociati` țin conexiunea pe
    #     `public`, iar SQL-ul asociaților e necalificat (500 „relation asociati does not exist” pe ecran); apel de CONTROL NOU.
    # [lotul 10, deficiența C73, 21.10.2026] 350 -> 352: două citiri NOI, ambele `repo_mijloace_fixe.cod_liber` — codul de inventar
    #   implicit, primul liber („NEC-LIC”, „NEC-LIC-2”, …; „MF-PLUS”, „MF-PLUS-2”, …), în `uc_tenants.achizitie_necorporala` și
    #   `uc_tenants.nota_inventariere` (plus_mf). Ecranele n-au câmp de cod, iar codul fix făcea ca a doua operațiune să cadă cu 500 pe
    #   `mijloace_fixe_cod_uniq`.
    # [lotul 11, comanda 11.1, 21.10.2026] 352 -> 353, cu apelurile numite (diferența față de HEAD, apel cu apel):
    #   + repo_contabilitate.nota_facturi_cu_factura, + repo_contabilitate.adauga_linie (uc_tenants.borderou_storneaza) — decizia 10.3
    #     „Borderoul se corectează prin stornare, ca factura”: nota inversă a borderoului stornat și rândurile ei; scrieri NOI;
    #   + repo_facturi.seteaza_act_identitate (uc_tenants.borderou_storneaza) — borderoul de stornare (BA-n nou) poartă actul de identitate
    #     al vânzătorului PF, ca borderoul inițial (402); scriere NOUĂ;
    #   + tranzactie.fixeaza_schema (uc_tenants.borderou_storneaza) — stornarea emite o factură cu INSERT necalificat (ca `vanzare_ic`,
    #     R187); apel de CONTROL NOU;
    #   − repo_contabilitate.nota_operatiune_ciorna, − repo_contabilitate.adauga_linie (uc_tenants.reevaluare_valuta) — 429, formularul
    #     manual al reevaluării și use-case-ul lui au plecat (un singur formular, cu propunerea): −2;
    #   − repo_mijloace_fixe.de_amortizat (uc_tenants.tenant_amortizare) — 451, rândurile amortizării vin din sursa unică
    #     `amortizare_lunii.linii` (aceeași cu regenerarea pe uscat a ciornei depășite), care nu e repository: −1;
    #   neutru: repo_contabilitate.adauga_linie -> adauga_linie_partener (uc_reevaluare.reevaluare_valuta_genereaza) — decizia 10.3, rândul
    #     de reevaluare al unui partener poartă partenerul.
    # [lotul 11, subagentul x] 353 -> 375, cu apelurile numite:
    #   − repo_contabilitate.nota_facturi_cu_factura, − repo_contabilitate.adauga_linie_client (uc_tenants.vanzare_ic) — C78, nota proprie
    #     a livrării intracomunitare dubla contarea de la emitere; nota e acum `fres["contare"]["inregistrare_id"]`: −2;
    #   + 24 de apeluri NOI, niciunul SQL nou: regula straturilor (`core/straturi.py`, e2a D4b) — SQL-ul scris în lotul 11 direct în
    #     use-case a trecut în repository, instrucțiune cu instrucțiune, aceeași ordine:
    #     uc_tenants.stocuri_adauga: repo_stocuri.blocheaza_nir_urile / savepoint_nir_numar_repetat / inapoi_la_nir_numar_repetat (3);
    #     uc_tenants._nir_cu_numarul: repo_stocuri.nir_cu_numarul (1);
    #     uc_tenants.achizitie_neinregistrat: repo_stocuri.articolul_ales, repo_borderou.blocheaza_borderourile (2);
    #     uc_tenants._borderou_identic: repo_borderou.vii_cu_data_si_valoarea / descriere_si_cantitate (2);
    #     uc_tenants.borderouri_lista: repo_borderou.ale_lunii / prima_linie / nota_si_valoarea (3);
    #     uc_tenants.borderou_storneaza: repo_borderou.blocheaza_borderourile / de_stornat / stornarea_lui / linii_de_stornat /
    #       liniile_notei / intrari_vii / savepoint_stornare / inapoi_la_stornare / leaga_stornarea / storneaza_intrarea,
    #       repo_stocuri.denumirea_articolului (11);
    #     uc_cabinet.citeste_intocmitor_conn / salveaza_intocmitor_conn: repo_cabinet.intocmitorul / scrie_intocmitorul (2).
    # [lotul 11] 375 -> 377, cu apelurile numite:
    #   + repo_efactura.salveaza_tva_cote (uc_tenants._factura_importata) — C79: importul e-Factura păstrează TVA-ul pe cote al facturii
    #     (BG-23, BT-116..119) în `factura_tva_cote`; scriere NOUĂ;
    #   + repo_efactura.moneda_si_data (uc_tenants.factura_contabilizeaza) — C83: factura din XML în valută rămasă fără curs; moneda și
    #     data se citesc înaintea tranzacției, ca cursul BNR să fie adus (`_preincalzeste_cursul`); citire NOUĂ.
    # [lotul 11, deficiența 456] 377 -> 381, cu apelurile numite: încasarea facturii din Casă emite automat chitanța
    #   (`uc_tenants.chitante_pe_incasare`): + repo_casa.urmatorul_numar_chitanta, + repo_facturi.factura_pentru_chitanta (citiri NOI),
    #   + repo_casa.data_si_documentul_operatiunii (citire NOUĂ), + repo_casa.documentul_chitantei (scriere NOUĂ: documentul operațiunii
    #   și al notei = numărul chitanței). Neutre: repo_firma_profil.seria_chitantei, repo_casa.adauga_chitanta,
    #   repo_facturi.marcheaza_platita mutate din `chitanta_emite` în ajutoarele comune `chitanta_serie_sau_refuz` / `chitanta_scrie`.
    # [lotul 12, comanda 12.1] 381 -> 386, cu apelurile numite (diferența față de d850db00, apel cu apel):
    #   + repo_facturi.cursul_fixat (uc_factura_primita._anunt_curs) — decizia Costin „cursul vechi la validare (a)”: factura primită în
    #     valută validată cu un curs mai vechi decât cel al zilei primește anunțul, ca la emitere; citire NOUĂ;
    #   + repo_tenants.nume_si_cui_spatiat (uc_migrare.firma_fisier) — 599, firma din antetul fișierului de migrare, față de firma
    #     aleasă; citire NOUĂ;
    #   + repo_firma_profil.caen (uc_tenants.cv_articole) — 473, etichetele „alimentație publică” ale ecranului Stocuri numai la CAEN-ul
    #     HoReCa; citire NOUĂ;
    #   + repo_reevaluari.rezerva_si_pierderea (uc_tenants.reevaluare_imobilizare) — C116, rezerva 105 și descreșterea trecută pe 655 ale
    #     activului, din reevaluările lui aplicate (OMFP 1802/2014 pct.111 alin.(1)-(2)), când cererea nu le dă; citire NOUĂ;
    #   + repo_firma_profil.cui_firma_3 (uc_tenants.factura_primita_valideaza) — C120, factura primită între alte două firme refuzată și
    #     la validare (CUI-ul din Date firmă, ca la import); citire NOUĂ;
    #   neutre: repo_efactura.marcheaza_primita_validata, repo_facturi.actualizeaza_clasificarea ×2 / actualizeaza_destinatii_linii /
    #     actualizeaza_conturi_linii mutate din `uc_tenants.factura_primita_valideaza` în `uc_factura_primita.valideaza` (477, drumul
    #     comun cu factura primită introdusă de mână).
    assert _apeluri_catre_repository() == 386


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
