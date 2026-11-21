# -*- coding: utf-8 -*-
"""core/migrari_registru.py — gardul „codul nu repornește înaintea migrării lui” (comanda Costin 09.10.2026, pct.2, verbatim în
DECIZII: „Clasa «cod publicat înaintea migrării»: gard în post-commit. Dacă un commit conține o migrare nerulată pe producție,
aplicația nu repornește. Nu procedură scrisă.”).

DE CE: pe 09.10.2026 post-commit-ul a repornit producția pe d0abd48f, al cărui `casa_api` citea `casa_operatiuni.storno_de`, iar
migrarea care adaugă coloana (`core.migrare_retest2`) era încă nerulată pe producție — ecranul Casă a căzut pe toate firmele până la
rularea ei manuală.

DRUMURILE prin care codul nou poate cere o schemă/date pe care producția nu le are încă (căutate: `ls core/migrare_*.py` — 84 de
migrări în 39fde2bc, cu blocul `__main__`; `grep -lE "ALTER TABLE|CREATE TABLE" core/*.py` în afara testelor și a migrărilor — 13
module cu DDL LA RULARE, toate `IF NOT EXISTS` (cron, firma_rezumat, instante, salariati_import_api, solduri_parteneri_api,
supervizor_cache, raport_z, solduri_api, sonda_scrieri, stare_partajata, stat_plata_emis; d394/d301 numai în comentarii), deci se
creează singure la primul apel și nu pot rămâne în urmă; `tenant_template.sql`, care ajunge numai la firmele NOI):
  (a) un modul `core/migrare_*.py` (nou sau schimbat, în acest commit SAU într-unul anterior) nerulat pe producție -> REGISTRUL:
      `public.migrari_rulate` (fișier, amprenta sha256 a conținutului, când, commitul). Fiecare migrare din HEAD trebuie să aibă un rând
      cu amprenta conținutului ei din HEAD. Se scrie numai prin rulatorul de aici (`ruleaza`) sau printr-o marcare explicită cu motiv
      (`marcheaza`: o schimbare care nu cere rulare, ex. un text de mesaj);
  (b) o tabelă / coloană adăugată în `tenant_template.sql` fără migrare (sau cu migrarea rulată numai pe baza de test) -> AUDITUL DE
      SCHEMĂ pe producție, cu șablonul din HEAD (`audit_schema.auditeaza`, sub ROLLBACK): orice lipsă template -> firmă oprește restartul.
Verificarea e FAIL-CLOSED: dacă nu se poate ști (baza de neatins, acreditare spre altă bază), aplicația NU repornește.

LIMITĂ DECLARATĂ: registrul pornește pe 09.10.2026 cu o BAZĂ — migrările din `39fde2bc` sunt trecute ca rulate fără dovadă (producția
a mers pe ele; registrul nu poate dovedi trecutul). Baza o scrie `baza` o singură dată (nu suprascrie nimic).

CLI (rulat de om, cu `--productie` pentru baza de producție din `~/.iconta/db.env`):
  python -m core.migrari_registru ruleaza [--productie] core/migrare_x.py   -> rulează migrarea, apoi îi scrie rândul
  python -m core.migrari_registru marcheaza [--productie] core/migrare_x.py "motiv"
  python -m core.migrari_registru verifica <sha>                           -> 0 = poate reporni; 1 = nerulate / drift; 2 = nu se știe
  python -m core.migrari_registru baza --productie <sha>                    -> baza registrului (o dată)
[17.5-P0] Migrarea DECLARATĂ a unui lot (docs/dovezi/<lot>/migrare_asteptata.json, operația deschisă de scripts/publica_lot.sh):
  python -m core.migrari_registru verifica <sha> --publicare             -> publica_prod.sh, prima publicare: 75 = așteaptă migrarea declarată
  python -m core.migrari_registru verifica <sha> --confirmare <operație> -> 0 numai cu rândul exact (fișier, amprentă, rulata, E) și schema la zi
  python -m core.migrari_registru backup-inainte --productie <fișier>     -> după acordul semnat: starea serviciului de backup înaintea comenzii lui Costin
  python -m core.migrari_registru ruleaza --productie <fișier>            -> acord + backup + DDL + registru; NU repornește: restartul îl face numai
                                                                            `sh scripts/publica_lot.sh --confirma-migrare <lot> <E>`
Fără opțiune, `verifica` păstrează codurile 0/1/2. Garda oricărei scrieri `--productie` vine înaintea mediului bazei (`_env_productie`).
[16.1-C3, pct.7] ORICE comandă cu `--productie` (ruleaza, marcheaza, baza) REFUZĂ fără verdictul `PASS <sha>` al lui scripts/publica_lot.py pentru commitul curent al lui `main`
(<git-common-dir>/publica_verdicte.log). `verifica` (citire, sub ROLLBACK) nu e păzită. Restartul amânat de o migrare îl face scripts/publica_prod.sh (cere și el PASS), nu rulatorul.
După o rulare reușită pe producție, dacă hook-ul a oprit restartul (`.git/RESTART_OPRIT_MIGRARE`) și HEAD nu mai are nimic de rulat,
rulatorul repornește aplicația — exact pasul pe care hook-ul l-a amânat.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTINELA = os.path.join(RAD, ".git", "RESTART_OPRIT_MIGRARE")
PASS_LOG = None   # None = <git-common-dir>/publica_verdicte.log; numai calibrarea îl mută (pe o bază de probă)
_RE_FISIER = re.compile(r"^core/migrare_[a-z0-9_]+\.py$")

DDL = ("CREATE TABLE IF NOT EXISTS public.migrari_rulate (fisier text NOT NULL, amprenta text NOT NULL, "
       "rulat_la timestamptz NOT NULL DEFAULT now(), commit text, fel text NOT NULL CHECK (fel IN ('rulata', 'marcata', 'baza')), "
       "motiv text, PRIMARY KEY (fisier, amprenta))")


def e_migrare(cale, text):
    """PURĂ. Un fișier e migrare dacă e `core/migrare_<nume>.py` și se rulează ca program (are blocul `__main__`)."""
    return bool(_RE_FISIER.match(cale)) and re.search(r"""^if\s+__name__\s*==\s*["']__main__["']\s*:""", text, re.M) is not None


def amprenta(text):
    """PURĂ. sha256 al conținutului (text)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git(*args):
    return subprocess.run(("git",) + args, cwd=RAD, capture_output=True, text=True, check=True).stdout


def migrari_la_commit(sha):
    """{fișier: amprentă} — toate migrările din arborele commitului `sha`."""
    out = {}
    for cale in _git("ls-tree", "-r", "--name-only", sha, "core/").splitlines():
        if _RE_FISIER.match(cale):
            text = _git("show", "%s:%s" % (sha, cale))
            if e_migrare(cale, text):
                out[cale] = amprenta(text)
    return out


def _tabel(cur):
    cur.execute(DDL)


def inregistreaza(cur, fisier, amp, fel, commit=None, motiv=None):
    _tabel(cur)
    cur.execute("INSERT INTO public.migrari_rulate (fisier, amprenta, fel, commit, motiv) VALUES (%s,%s,%s,%s,%s) "
                "ON CONFLICT (fisier, amprenta) DO NOTHING", (fisier, amp, fel, commit, motiv))


#: [18.10.2026, poarta 1 a lotului 7] ORDINEA migrărilor: migrarea-cheie folosește o tabelă, o coloană sau o funcție pe care o CREEAZĂ
#: migrarea din valoare, deci se rulează după ea. Poarta a picat la cifrele F1–F5: copia rula nerulatele în ordine alfabetică, iar `migrare_ciorne_proprii`
#: (`eticheta_nota` citește `registru_jurnal_numere`) a mers înaintea lui `migrare_nr_curent_note`, care creează tabela — ordinea era
#: scrisă numai în docstringul migrării. Aici, nu în fișierele migrărilor: o linie nouă acolo le-ar schimba amprenta și le-ar cere din
#: nou pe producție. Perechile se derivă din cod (SQL-ul executat al unei migrări numește ce creează alta) și sunt păzite de
#: `core/test_migrari_registru.py::test_ordinea_numeste_tot_ce_creeaza_alta_migrare`; `nerulate` le pune în ordine, iar
#: `ruleaza` refuză o migrare cât timp una din cele de dinaintea ei e nerulată pe aceeași bază.
DUPA = {
    # [lotul 12] migrările noi, după cele ale tabelelor pe care le citesc
    "core/migrare_lot13_salarii.py": ("core/migrare_decizii_0710.py",),
    "core/migrare_anunturi_trimiteri.py": ("core/migrare_invitatii_cabinet.py",),   # [lotul 13, 646] coloanele trimiterilor pe tabela anunțurilor creată acolo
    "core/migrare_d301_cod_tva_fara_prefix.py": ("core/migrare_d301_partener.py",),   # [lotul 13, 539] rescrie codul de TVA al partenerului D301, coloana creată acolo
    "core/migrare_triaj_sesizari.py": ("core/migrare_fisiere_private.py",),   # [lotul 13, 572–573] coloanele triajului pe sesizări, tabela atinsă acolo
    "core/migrare_vanzari_stoc.py": ("core/migrare_decizii_0710.py",),   # [lotul 13, 548] vânzările din stoc citesc tabela creată acolo   # [lotul 13, 679] adaugă `elemente_salariale.spor_procent`; tabela o creează decizii_0710
    "core/migrare_mesaje_spv_tehnice.py": ("core/migrare_efactura_trimiteri.py", "core/migrare_etransport_trimiteri.py", "core/migrare_spv_citiri.py"),
    "core/migrare_um_linii_xml.py": ("core/migrare_punte_stoc.py",),
    "core/migrare_um_borderou.py": ("core/migrare_punte_stoc.py",),   # [lotul 12, C115] citește `miscari_stoc.factura_id`
    "core/migrare_nir_tva_transport.py": ("core/migrare_stoc_lot4.py",),
    "core/migrare_extras_dubluri_trezorerie.py": ("core/migrare_extras_miscare.py",),
    # [lotul 12, 252] facturile deschise preluate: legăturile lor citesc `compensari` (refacerea indexului numerotării e a ei)
    "core/migrare_documente_preluate.py": ("core/migrare_compensari_afiliat.py", "core/migrare_d300_b1.py"),
    # [lotul 12, firme2] 475 (articolele dublate) și C133 (motivul scutirii), după tabelele / coloanele pe care le citesc
    "core/migrare_articole_dublate.py": ("core/migrare_cont_linie_primita.py", "core/migrare_nir_cost.py", "core/migrare_punte_stoc.py",
                                         "core/migrare_stoc_lot4.py"),
    "core/migrare_motiv_scutire.py": ("core/migrare_salariati_de_verificat.py",),
    "core/migrare_2b_coloana.py": ("core/migrare_salariu_istoric.py",),
    "core/migrare_avans_nir_ajustare_nota.py": ("core/migrare_ajustari_fiscale.py",),
    "core/migrare_borderou_tip_vechi.py": ("core/migrare_punte_stoc.py", "core/migrare_reguli_fond.py", "core/migrare_tert_platitor_tva.py"),
    "core/migrare_canal_notificari.py": ("core/migrare_inregistrare_libera.py",),
    # [lotul 13, 566] bifa „solicitare_client” pusă la loc citește `users.notificari_tipuri` / `notificari_salvate_la`
    "core/migrare_notificari_solicitare_client.py": ("core/migrare_canal_notificari.py",),
    "core/migrare_ciorne_proprii.py": ("core/migrare_nr_curent_note.py", "core/migrare_validare_note.py"),
    "core/migrare_cui_fara_ro.py": ("core/migrare_efactura_primite.py", "core/migrare_intocmitor_bilant.py", "core/migrare_partener_linie.py",
                                    "core/migrare_tert_platitor_tva.py"),
    "core/migrare_curs_precizie.py": ("core/migrare_reevaluari_valuta.py",),
    "core/migrare_decizii_0710.py": ("core/migrare_punte_stoc.py", "core/migrare_validare_note.py"),
    "core/migrare_decizii_0810.py": ("core/migrare_decizii_0710.py", "core/migrare_declaratii_depuse_randuri.py", "core/migrare_validare_note.py"),
    "core/migrare_fapte_date_firma.py": ("core/migrare_art317.py", "core/migrare_d394_i2.py", "core/migrare_firma_profil_jurnal.py"),
    "core/migrare_grup_coada.py": ("core/migrare_validare_note.py",),
    "core/migrare_inregistrari_email.py": ("core/migrare_inregistrare_libera.py",),
    "core/migrare_intrare_date_garduri.py": ("core/migrare_efactura_primite.py", "core/migrare_stoc_lot4.py"),
    "core/migrare_nota_corectie.py": ("core/migrare_decizii_0710.py", "core/migrare_validare_note.py"),
    "core/migrare_reevaluare_partener.py": ("core/migrare_reevaluari_valuta.py",),
    "core/migrare_reguli_fond.py": ("core/migrare_ciorne_proprii.py", "core/migrare_decizii_0710.py"),
    "core/migrare_reguli_fond_2.py": ("core/migrare_declaratii_depuse_randuri.py", "core/migrare_declaratii_depuse_versiune.py"),
    "core/migrare_retest2.py": ("core/migrare_validare_note.py",),
    "core/migrare_retest_0810.py": ("core/migrare_metoda_stoc.py",),
    "core/migrare_tva_incasare_perioade_optiune.py": ("core/migrare_tva_incasare_perioade.py",),   # [lotul 13, 541] ALTER pe tabela ei
    "core/migrare_schema_seq.py": ("core/migrare_firme_scoase.py",),
    "core/migrare_serie_nr_descrieri.py": ("core/migrare_compensari_afiliat.py", "core/migrare_punte_stoc.py", "core/migrare_reguli_fond.py"),
}


def in_ordine(perechi):
    """PURĂ. [(fișier, amprentă)] în ordinea rulării: alfabetic, dar fiecare după migrările din `DUPA` ei aflate în listă."""
    toate = dict(sorted(perechi))
    out, puse = [], set()

    def pune(f):
        if f in puse:
            return
        puse.add(f)
        for d in DUPA.get(f, ()):
            if d in toate:
                pune(d)
        out.append((f, toate[f]))
    for f in toate:
        pune(f)
    return out


def nerulate(cur, migrari):
    """[(fișier, amprentă)] din `migrari` fără rând în registru (tabela absentă = toate), în ordinea rulării (`in_ordine`)."""
    cur.execute("SELECT to_regclass('public.migrari_rulate') IS NOT NULL")
    if not cur.fetchone()[0]:
        return in_ordine(migrari.items())
    cur.execute("SELECT fisier, amprenta FROM public.migrari_rulate")
    are = {(f, a) for f, a in cur.fetchall()}
    return in_ordine((f, a) for f, a in migrari.items() if (f, a) not in are)


def inainte_nerulate(cur, cale):
    """[fișier] — migrările din `DUPA[cale]` al căror conținut de pe disc n-are rând în registrul bazei: `ruleaza` nu pornește peste ele."""
    dep = {}
    for d in DUPA.get(cale, ()):
        if os.path.exists(os.path.join(RAD, d)):
            dep[d] = amprenta(open(os.path.join(RAD, d), encoding="utf-8").read())
    return [f for f, _a in nerulate(cur, dep)]


def drift_schema(conn, template_sql):
    """{schemă: drift dur} — lipsurile template -> firmă (sub ROLLBACK; apelantul anulează)."""
    from core import audit_schema as au
    with conn.cursor() as cur:
        schemas = au._schemele_tenant(cur)
    rapoarte, _ref = au.auditeaza(conn, schemas, template_sql)
    return {s: d for s, d in rapoarte.items() if au.are_drift_hard(d)}


def _conexiune_productie():
    """(conn, None) sau (None, motivul pentru care nu se poate ști)."""
    import psycopg2
    from core import mediu_test as _m
    url = _m.dsn_productie()
    if not url:
        return None, "%s n-are DATABASE_URL" % _m.CALE_DB_ENV
    if _m.desface_dsn(url)["dbname"] != _m.PRODUCTIE_DBNAME:
        return None, "acreditarea din %s duce la altă bază decât %s" % (_m.CALE_DB_ENV, _m.PRODUCTIE_DBNAME)
    try:
        return psycopg2.connect(url), None
    except Exception as e:  # noqa: BLE001 — fail-closed: motivul se tipărește, restartul nu se face
        return None, "baza de producție nu răspunde: %s" % str(e).split("\n")[0]


def criteriu_coloana(cur, schemas, tabel, coloana):
    """[17.5-P0, B.3] [] dacă în fiecare schemă reală coloana declarată e `text`, nullable, fără implicit (auditorul generic ignoră DEFAULT);
    altfel motivele, pe schemă."""
    if not schemas:
        return ["nicio schemă de firmă"]
    motive = []
    for s in schemas:
        cur.execute("SELECT data_type, is_nullable, column_default FROM information_schema.columns "
                    "WHERE table_schema = %s AND table_name = %s AND column_name = %s", (s, tabel, coloana))
        r = cur.fetchone()
        if r is None:
            motive.append("%s: %s.%s lipsește" % (s, tabel, coloana))
        elif tuple(r) != ("text", "YES", None):
            motive.append("%s: %s.%s este %s" % (s, tabel, coloana, tuple(r)))
    return motive


def evalueaza(sha, conn=None, plan=None):
    """[17.5-P0, B.3] O SINGURĂ evaluare structurată, pe aceeași conexiune și sub ROLLBACK: migrările nerulate ale lui `sha`, deriva dură a
    schemelor față de șablonul lui `sha` și, pentru un plan declarat, rândurile registrului ale fișierului declarat și criteriul coloanei.
    -> dict(lipsa, drift, randuri, schema); None = baza de neatins (cu motivul în `motiv`)."""
    proprie = conn is None
    if proprie:
        conn, motiv = _conexiune_productie()
        if conn is None:
            return dict(lipsa=None, drift=None, randuri=None, schema=None, motiv=motiv)
    try:
        with conn.cursor() as cur:
            lipsa = nerulate(cur, migrari_la_commit(sha))
            randuri = schema = None
            if plan is not None:
                randuri = []
                cur.execute("SELECT to_regclass('public.migrari_rulate') IS NOT NULL")
                if cur.fetchone()[0]:
                    cur.execute("SELECT fisier, amprenta, fel, commit FROM public.migrari_rulate WHERE fisier = %s", (plan.fisier,))
                    randuri = [tuple(r) for r in cur.fetchall()]
                from core import audit_schema as au
                schema = criteriu_coloana(cur, au._schemele_tenant(cur), plan.tabel, plan.coloana)
        drift = drift_schema(conn, _git("show", "%s:tenant_template.sql" % sha))
    finally:
        conn.rollback()
        if proprie:
            conn.close()
    return dict(lipsa=lipsa, drift=drift, randuri=randuri, schema=schema, motiv=None)


def verifica(sha, conn=None):
    """(cod, rânduri de tipărit): 0 = HEAD poate porni pe producție; 1 = migrări nerulate / schemă în urmă; 2 = nu se poate ști.
    `conn` dat = baza pe care se întreabă (testele); altfel producția. Totul sub un singur ROLLBACK (schema de referință a
    auditului e temporară; nimic nu se scrie)."""
    ev = evalueaza(sha, conn)
    if ev["lipsa"] is None:
        return 2, ["NU SE POATE ȘTI dacă producția are migrările lui %s: %s" % (sha[:8], ev["motiv"])]
    return _linii_verificare(ev)


def _linii_verificare(ev):
    lipsa, drift = ev["lipsa"], ev["drift"]
    linii = ["migrare nerulată pe producție: %s (amprenta %s) — rulează: ./venv/bin/python -m core.migrari_registru ruleaza "
             "--productie %s" % (f, a[:12], f) for f, a in lipsa]
    for s, d in sorted(drift.items()):
        linii.append("schema %s e în urma șablonului: tabele lipsă %s, coloane lipsă %s, triggere lipsă %s" % (
            s, d["tabele_lipsa"] or "-", dict(d["coloane_lipsa"]) or "-", d.get("triggere_lipsa") or "-"))
    return (1 if linii else 0), linii


def _reguli():
    """scripts/reguli_publicare_migrare.py: contractul livrat și adaptorii oficiali ai operației (17.5-P0)."""
    d = os.path.join(RAD, "scripts")
    if d not in sys.path:
        sys.path.insert(0, d)
    import reguli_publicare_migrare as r
    return r


def decizie_plan(ev, plan):
    """[17.5-P0, B.3] PURĂ. (stare, motiv) pentru un plan declarat: «asteapta_migrare» numai cu perechea fișier/SHA a planului singura
    nerulată și deriva limitată la coloana declarată; «pregatit» numai cu rândul exact (fișier, amprentă, rulata, E complet) și criteriul
    coloanei în toate schemele reale; orice altceva = «refuz» cu motivul. Datele incomplete = «necunoscut»."""
    r = _reguli()
    if ev["lipsa"] is None or ev["drift"] is None:
        return "necunoscut", ev.get("motiv") or "stare necunoscută"
    try:
        stare = r.situatie(plan, ev["lipsa"], ev["drift"])
    except r.Refuz as ex:
        return "refuz", str(ex)
    if stare == "asteapta_migrare":
        if [x for x in (ev["randuri"] or []) if x[1] == plan.digest]:
            return "refuz", "registrul are deja un rând pentru migrarea declarată"
        return stare, ""
    exacte = [x for x in (ev["randuri"] or []) if x[1] == plan.digest]
    if exacte != [(plan.fisier, plan.digest, "rulata", plan.e)]:
        return "refuz", "registrul nu are rândul exact (fișier, amprentă, rulata, E): %s" % (exacte or "niciun rând")
    if ev["schema"]:
        return "refuz", "schema: %s" % "; ".join(ev["schema"])
    return "pregatit", ""


def verifica_plan(sha, mod, operatie=None, conn=None):
    """`verifica <sha> --publicare | --confirmare <op>` -> (cod, rânduri, dicționar JSON). Fără plan pentru `sha`: codurile 0/1/2 de mai sus
    (la --publicare) sau refuz (la --confirmare). Cu plan: --publicare dă 75 numai pe așteptarea demonstrată (niciodată 0: restartul unei
    operații cu plan îl face numai continuarea); --confirmare dă 0 numai pe «pregatit»."""
    r = _reguli()
    try:
        po = r.plan_pentru_head(RAD) if _git("rev-parse", "HEAD").strip() == sha else None
    except r.Refuz as ex:
        return 1, ["planul migrării declarate e corupt sau discordant: %s" % ex], dict(stare="refuz", motiv=str(ex), plan=True)
    if po is None:
        if mod == "--confirmare":
            return 1, ["nicio operație de migrare deschisă pentru %s" % sha[:8]], dict(stare="refuz", motiv="fara operatie", plan=False)
        cod, linii = verifica(sha, conn)
        return cod, linii, dict(stare=("pregatit" if cod == 0 else "nepregatit"), plan=False)
    plan, o, _d = po
    if mod == "--confirmare" and operatie != o["operatie"]:
        return 1, ["operația %s nu e cea deschisă pentru %s (%s)" % (operatie, sha[:8], o["operatie"])], \
            dict(stare="refuz", motiv="alta operatie", plan=True)
    ev = evalueaza(sha, conn, plan)
    stare, motiv = decizie_plan(ev, plan)
    exacte = [list(x) for x in (ev["randuri"] or []) if x[1] == plan.digest]
    date = dict(stare=stare, motiv=motiv, plan=True, lot=o["lot"], e=sha, operatie=o["operatie"], fisier=plan.fisier,
                rand=(exacte[0] if len(exacte) == 1 else None))
    linii = [] if ev["lipsa"] is None else _linii_verificare(ev)[1]
    if stare == "necunoscut":
        return 2, linii + ["NU SE POATE ȘTI: %s" % motiv], date
    if stare == "asteapta_migrare":
        return (75 if mod == "--publicare" else 1), linii + [
            "AȘTEAPTĂ MIGRAREA %s pe %s — operația %s: %s nerulată (acord semnat, backup, apoi ruleaza --productie)" % (
                o["lot"], sha, o["operatie"], plan.fisier)], date
    if stare == "pregatit" and mod == "--confirmare":
        return 0, linii, date
    if stare == "pregatit":
        return 1, linii + ["migrarea declarată e deja rulată: restartul îl face numai sh scripts/publica_lot.sh --confirma-migrare %s %s"
                           % (o["lot"], sha)], date
    return 1, linii + ["REFUZ: %s" % motiv], date


def _env_productie():
    from core import mediu_test as _m
    url = _m.dsn_productie()
    if not url:
        raise SystemExit("nu se găsește DATABASE_URL în %s" % _m.CALE_DB_ENV)
    os.environ["DATABASE_URL"] = url
    _ev("acces_scriere", baza=_m.desface_dsn(url)["dbname"])


def _cu_registrul(scrie):
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            scrie(cur)
        conn.commit()


def _reporneste_daca_e_cazul(productie):
    """[16.1-C3, pct.7] Restartul amânat de o migrare îl face numai scripts/publica_prod.sh (cere PASS pentru HEAD, verifică migrările, publică statica ÎNAINTEA restartului, apoi
    restartul și four-way-ul; își scrie singur sentinelele)."""
    if not (productie and os.path.exists(SENTINELA)):
        return
    r = subprocess.run(["sh", os.path.join(RAD, "scripts", "publica_prod.sh")], capture_output=True, text=True, cwd=RAD)
    print((r.stdout + r.stderr).strip())


def refuz_fara_pass(log=None, main="main"):
    """[16.1-C3, pct.7] None dacă `log` (implicit <git-common-dir>/publica_verdicte.log) are `PASS <sha>` pentru commitul curent al lui `main`; altfel motivul refuzului."""
    sha = _git("rev-parse", main).strip()
    if log is None:
        log = os.path.join(_git("rev-parse", "--path-format=absolute", "--git-common-dir").strip(), "publica_verdicte.log")
    try:
        ok = any(ln.startswith("PASS %s " % sha) for ln in open(log, encoding="utf-8"))
    except OSError:
        ok = False
    return None if ok else "REFUZ: fără verdictul PASS al lui scripts/publica_lot.py pentru commitul curent al lui %s (%s) în %s; nimic nu se scrie pe producție" % (main, sha[:8], log)


def _ev(nume, **date):
    """[17.5-P0] Rândul de eveniment al rulatorului: o linie JSON pe ieșire (calibrarea o citează exact; fără secrete)."""
    print(json.dumps(dict(eveniment=nume, pid=os.getpid(), **date), ensure_ascii=False, sort_keys=True), flush=True)


def _git_bytes(*args):
    return subprocess.run(("git",) + args, cwd=RAD, capture_output=True, check=True).stdout


def _declarat_la_head(head):
    """Fișierul migrării declarate de lotul al cărui PASS numește HEAD (din obiectele Git ale lui HEAD); None = niciunul."""
    log = PASS_LOG or os.path.join(_git("rev-parse", "--path-format=absolute", "--git-common-dir").strip(), "publica_verdicte.log")
    loturi = []
    try:
        for ln in open(log, encoding="utf-8"):
            c = ln.split()
            if len(c) >= 3 and c[0] == "PASS" and c[1] == head:
                loturi.append(c[2])
    except OSError:
        return None
    if not loturi:
        return None
    r = _reguli()
    try:
        d = r.declaratie(RAD, head, loturi[-1])
    except r.Refuz:
        return "?"
    return d["fisier"] if d else None


def garda_productie(cmd, rest):
    """[17.5-P0, C.5] Garda oricărei scrieri `--productie`, ÎNAINTEA mediului bazei (`_env_productie`), a registrului, a oricărui DDL sau runpy:
    depozitul principal pe `main`, HEAD = main = origin/main (versiunea țintă), cod urmărit nemodificat; `ruleaza`/`marcheaza`/`backup-inainte`
    cer un fișier regulat cu aceiași octeți ca în versiunea țintă, `baza` cere SHA-ul țintă complet din istoria lui main. O migrare declarată
    drept necesară nu se marchează și nu intră în baza registrului; un plan corupt, discordant sau fără operație e refuz. -> motivul sau None."""
    try:
        comun_ = _git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()
        if os.path.realpath(comun_) != os.path.realpath(os.path.join(RAD, ".git")):
            return "REFUZ: scrierea pe producție se face numai din depozitul principal, nu dintr-un worktree (%s)" % comun_
        if _git("symbolic-ref", "--short", "HEAD").strip() != "main":
            return "REFUZ: scrierea pe producție se face numai de pe main"
        head = _git("rev-parse", "HEAD").strip()
        for ref in ("refs/heads/main", "refs/remotes/origin/main"):
            if _git("rev-parse", ref).strip() != head:
                return "REFUZ: %s diferă de HEAD %s: versiunea țintă nu e publicată" % (ref, head[:8])
        if _git("diff", "--name-only", "HEAD", "--").strip():
            return "REFUZ: cod local diferit de versiunea țintă %s (fișiere urmărite modificate)" % head[:8]
        if _git("ls-files", "--others", "--exclude-standard", "--", "core", "scripts").strip():
            return "REFUZ: fișiere neurmărite în core/ sau scripts/ pot schimba ce rulează"
    except (subprocess.CalledProcessError, OSError) as e:
        return "REFUZ: identitatea Git a versiunii țintă nu se poate citi: %s" % str(e).split("\n")[0]
    if cmd in ("ruleaza", "marcheaza", "backup-inainte"):
        if not rest or not _RE_FISIER.match(rest[0]):
            return "REFUZ: lipsește fișierul migrării (core/migrare_<nume>.py)"
        plin = os.path.join(RAD, rest[0])
        if os.path.islink(plin) or not os.path.isfile(plin):
            return "REFUZ: %s nu e un fișier regulat în versiunea țintă %s" % (rest[0], head[:8])
        if not _git("ls-tree", head, "--", rest[0]).startswith(("100644 blob ", "100755 blob ")):
            return "REFUZ: %s nu există în versiunea țintă %s" % (rest[0], head[:8])
        with open(plin, "rb") as f:
            if f.read() != _git_bytes("show", "%s:%s" % (head, rest[0])):
                return "REFUZ: %s de pe disc diferă de versiunea țintă %s" % (rest[0], head[:8])
    elif cmd == "baza":
        if not rest or not re.fullmatch(r"[0-9a-f]{40}", rest[0]):
            return "REFUZ: baza registrului cere SHA-ul țintă complet"
        if subprocess.run(["git", "merge-base", "--is-ancestor", rest[0], head], cwd=RAD, capture_output=True).returncode:
            return "REFUZ: SHA-ul țintă %s nu e în istoria lui main" % rest[0][:8]
    else:
        return "REFUZ: comanda %s nu scrie pe producție" % cmd
    r = _reguli()
    try:
        po = r.plan_pentru_head(RAD)
    except (r.Refuz, OSError) as ex:
        return "REFUZ: planul migrării declarate e corupt sau discordant: %s" % ex
    declarat = _declarat_la_head(head)
    if po is None:
        if declarat == "?":
            return "REFUZ: declarația migrării lotului e coruptă"
        if declarat and cmd != "baza" and rest[0] == declarat:
            return ("REFUZ: %s e declarată de lot, dar operația publicării lipsește: se rulează numai pe operația deschisă de "
                    "scripts/publica_lot.sh" % declarat)
        if cmd == "backup-inainte":
            return "REFUZ: nicio operație de migrare deschisă pentru %s" % head[:8]
        return None
    plan = po[0]
    if cmd == "baza":
        return "REFUZ: baza registrului nu se scrie cât e deschisă operația migrării declarate %s" % plan.fisier
    if cmd == "marcheaza" and rest[0] == plan.fisier:
        return "REFUZ: %s e declarată drept necesară: marcarea nu satisface obligația de rulare" % plan.fisier
    if cmd == "backup-inainte" and rest[0] != plan.fisier:
        return "REFUZ: operația deschisă e a migrării %s" % plan.fisier
    return None


# ---------- [17.5-P0, B4] backupul manual al bazei, decis de Costin: adaptorul care corelează serviciul, jurnalul PID 1, backup.log și arhiva ----------
BACKUP_DIR = "/var/backups/iconta"
BACKUP_LOG = os.path.join(BACKUP_DIR, "backup.log")
BACKUP_UNITATE = "iconta-backup.service"
BACKUP_PROPRIETAR = "postgres"
_MSG_PORNIT = "7d4958e842da4a758f6c1cdc7b36dcc5"    # systemd: «Starting <unit>…» (JOB_TYPE=start)
_MSG_INCHEIAT = "39f53479d3a045ac8e11786248231fbf"  # systemd: «Finished <unit>» (JOB_RESULT=done)
_RE_DUMP = re.compile(r"^iconta_v2_\d{8}_\d{6}\.dump$")


def _proprietar_backup():
    """`postgres`; numai în spațiul privat de calibrare (HOME=/lab/home, fără utilizatorul postgres în /etc/passwd) proprietarul e cel al
    calibrării, numit în ICONTA_PROBA_BACKUP_PROPRIETAR (limită declarată a calibrării)."""
    if os.environ.get("HOME") == "/lab/home" and os.path.isdir("/lab/work/dubluri") and os.environ.get("ICONTA_PROBA_BACKUP_PROPRIETAR"):
        return os.environ["ICONTA_PROBA_BACKUP_PROPRIETAR"]
    return BACKUP_PROPRIETAR


def _arata_unitatea():
    p = subprocess.run(["systemctl", "show", BACKUP_UNITATE, "-p", "InvocationID", "-p", "ExecMainStatus", "-p", "Result", "-p",
                        "ActiveState", "-p", "ExecMainStartTimestamp", "-p", "ExecMainExitTimestamp"],
                       capture_output=True, text=True, timeout=30)
    if p.returncode:
        raise SystemExit("REFUZ: systemctl show %s a eșuat: %s" % (BACKUP_UNITATE, p.stderr.strip()[:200]))
    return dict(ln.split("=", 1) for ln in p.stdout.splitlines() if "=" in ln), p.stdout


def _arhive():
    return sorted(n for n in os.listdir(BACKUP_DIR) if _RE_DUMP.match(n))


def backup_inainte(d):
    """Înaintea comenzii manuale a lui Costin: InvocationID anterior, identitatea și cursorul lui backup.log, inventarul arhivelor (B4 pct.9)."""
    r = _reguli()
    if (d / "backup_inainte.json").exists():
        print("[migrari] starea dinaintea backupului e deja păstrată în %s" % d)
        return 0
    props, brut = _arata_unitatea()
    st = os.stat(BACKUP_LOG)
    date = dict(versiune=1, invocatie_anterioara=props.get("InvocationID", ""), log_dev=st.st_dev, log_ino=st.st_ino,
                log_cursor=st.st_size, inventar=_arhive(), la_ns=time.time_ns())
    r.scrie_atomic(d / "backup_inainte_show.txt", brut.encode())
    if not r.scrie_exclusiv(d / "backup_inainte.json", r.canon(date)):
        raise SystemExit("REFUZ: starea dinaintea backupului s-a scris concurent")
    _ev("backup_inainte", invocatie_anterioara=date["invocatie_anterioara"], cursor=date["log_cursor"])
    print("[migrari] Costin pornește acum, interactiv: sudo systemctl start %s ; apoi: ./venv/bin/python -m core.migrari_registru "
          "ruleaza --productie <fișier>" % BACKUP_UNITATE)
    return 0


def _ora_arhivei(antet):
    m = re.search(r"^;\s*Archive created at (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", antet, re.M)
    if not m:
        return None
    return int(time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")))


def backup_confirmat(d, plan, o, acord_ns):
    """Backupul aferent operației, corelat din serviciu, jurnalul PID 1, rândul unic «backup LOCAL OK» și arhivă (B4 pct.8–9); -> Backup.
    La recuperare se citește recipisa aceleiași operații (backup.json)."""
    import pwd
    import stat as _stat
    r = _reguli()
    import canal_migrare as canal
    if (d / "backup.json").exists():
        b = r.json_strict((d / "backup.json").read_bytes())
        return r.Backup(plan.e, "iconta_v2", BACKUP_UNITATE, b["invocatie"], True, b["sfarsit_ns"], b["sha256"]), b
    try:
        pre = r.json_strict((d / "backup_inainte.json").read_bytes())
    except FileNotFoundError:
        raise SystemExit("REFUZ: lipsește starea dinaintea backupului (python -m core.migrari_registru backup-inainte --productie %s)"
                         % plan.fisier)
    props, brut1 = _arata_unitatea()
    if props.get("ActiveState") in ("activating", "deactivating", "reloading"):
        raise SystemExit("REFUZ: backupul e încă în lucru (%s)" % props.get("ActiveState"))
    inv = props.get("InvocationID", "")
    if not re.fullmatch(r"[0-9a-f]{32}", inv) or inv == pre["invocatie_anterioara"]:
        raise SystemExit("REFUZ: Invocatie veche sau inlocuita: serviciul de backup nu are o invocație nouă după starea păstrată")
    j = subprocess.run(["journalctl", "-o", "json", "--no-pager", "_PID=1", "UNIT=" + BACKUP_UNITATE, "INVOCATION_ID=" + inv],
                       capture_output=True, text=True, timeout=60)
    intrari = []
    for ln in j.stdout.splitlines():
        try:
            intrari.append(json.loads(ln))
        except ValueError:
            pass
    pornit = [x for x in intrari if x.get("MESSAGE_ID") == _MSG_PORNIT and x.get("JOB_TYPE") == "start"]
    incheiat = [x for x in intrari if x.get("MESSAGE_ID") == _MSG_INCHEIAT and x.get("JOB_TYPE") == "start" and x.get("JOB_RESULT") == "done"]
    if j.returncode or len(pornit) != 1 or len(incheiat) != 1:
        raise SystemExit("REFUZ: jurnalul PID 1 nu are o singură pereche Starting/Finished pentru invocația %s" % inv)
    inv_jurnal = pornit[0].get("INVOCATION_ID", "")
    if incheiat[0].get("INVOCATION_ID") != inv_jurnal:
        raise SystemExit("REFUZ: perechea Starting/Finished are invocații diferite")
    inceput_ns, sfarsit_ns = int(pornit[0]["__REALTIME_TIMESTAMP"]) * 1000, int(incheiat[0]["__REALTIME_TIMESTAMP"]) * 1000
    with open(BACKUP_LOG, "rb") as f:
        st = os.fstat(f.fileno())
        if (st.st_dev, st.st_ino) != (pre["log_dev"], pre["log_ino"]) or st.st_size < pre["log_cursor"]:
            raise SystemExit("REFUZ: backup.log s-a rotit sau s-a trunchiat între citiri: asocierea nu e univocă")
        f.seek(pre["log_cursor"])
        noi = f.read()
    props2, brut2 = _arata_unitatea()
    linii = noi.decode("utf-8", errors="replace").splitlines()
    try:
        cale = canal.cale_backup_manual(pre["invocatie_anterioara"], inv, props2.get("InvocationID", ""), inceput_ns, sfarsit_ns, linii)
    except ValueError as ex:
        raise SystemExit("REFUZ: %s" % ex)
    try:
        lst = os.lstat(cale)
    except OSError:
        raise SystemExit("REFUZ: arhiva %s lipsește" % cale)
    proprietar = _proprietar_backup()
    try:
        nume_prop = pwd.getpwuid(lst.st_uid).pw_name
    except KeyError:
        nume_prop = str(lst.st_uid)
    if not _stat.S_ISREG(lst.st_mode) or os.path.dirname(cale) != BACKUP_DIR or nume_prop != proprietar or lst.st_size <= 0:
        raise SystemExit("REFUZ: arhiva %s nu e un fișier regulat nou al lui %s sub %s" % (cale, proprietar, BACKUP_DIR))
    noi_arhive = [os.path.join(BACKUP_DIR, n) for n in _arhive() if n not in pre["inventar"]]
    pg = subprocess.run(["pg_restore", "-l", cale], capture_output=True, text=True, timeout=120)
    antet = "\n".join(ln for ln in pg.stdout.splitlines() if ln.startswith(";"))
    m = re.search(r"^;\s*dbname: (\S+)\s*$", antet, re.M)
    creata = _ora_arhivei(antet)
    if creata is None or not (inceput_ns // 10**9 - 1 <= creata <= sfarsit_ns // 10**9 + 1):
        raise SystemExit("REFUZ: ora de creare a arhivei nu e în fereastra invocației")
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    info = dict(serviciu=BACKUP_UNITATE, rc=int(props.get("ExecMainStatus", "-1") or -1) if props.get("Result") == "success" else -1,
                baza=(m.group(1) if m else None), e=plan.e, invocatie=inv, invocatie_jurnal=inv_jurnal, inceput_ns=inceput_ns,
                sfarsit_ns=sfarsit_ns, cale=cale, cale_invocatie=cale, arhive_noi=noi_arhive, pg_restore_l_rc=pg.returncode,
                db_antet=(m.group(1) if m else None), sha256=h.hexdigest(), octeti=lst.st_size)
    try:
        digest = canal.coroboreaza_backup(info, plan.e, o["deschisa_ns"], acord_ns, time.time_ns())
    except (ValueError, KeyError) as ex:
        raise SystemExit("REFUZ: backup neconfirmat: %s" % ex)
    for nume, text in (("backup_show_dupa.txt", brut1 + "---\n" + brut2), ("backup_jurnal_pid1.json", j.stdout),
                       ("backup_log_nou.txt", noi.decode("utf-8", errors="replace")), ("backup_antet.txt", antet)):
        r.scrie_atomic(d / nume, text.encode())
    b = dict(versiune=1, invocatie=inv, inceput_ns=inceput_ns, sfarsit_ns=sfarsit_ns, cale=cale, sha256=digest, octeti=lst.st_size)
    if not r.scrie_exclusiv(d / "backup.json", r.canon(b)):
        raise SystemExit("REFUZ: recipisa backupului s-a scris concurent")
    return r.Backup(plan.e, "iconta_v2", BACKUP_UNITATE, inv, True, sfarsit_ns, digest), b


def _rand_exact(plan):
    """Rândul registrului pentru perechea declarată, citit sub ROLLBACK (None = niciunul; baza de neatins = SystemExit)."""
    ev = evalueaza(plan.e, None, plan)
    if ev["lipsa"] is None:
        raise SystemExit("NU SE POATE ȘTI starea registrului: %s" % ev["motiv"])
    exacte = [x for x in ev["randuri"] if x[1] == plan.digest]
    return exacte, ev


def ruleaza_declarata(cale):
    """[17.5-P0, C.5–C.7] Rulatorul migrării declarate, sub lacătul publicării: identitatea E (verifica_git), acordul semnat al lui Costin
    (canal_migrare.verifica_acord), backupul operației, starea «asteapta_migrare» recitită, apoi DDL și rândul (fișier, amprentă, rulata,
    E complet). Starea durabilă se scrie înainte de DDL; o rulare cu rezultat necunoscut nu se repetă (reconciliere). NU repornește:
    singurul restart e `sh scripts/publica_lot.sh --confirma-migrare <lot> <E>`."""
    r = _reguli()
    import canal_migrare as canal
    import datetime as _dt
    head = _git("rev-parse", "HEAD").strip()
    _ev("intrare", argv=sys.argv[:1] + ["ruleaza", "--productie", cale])
    with r.lacat(r.comun(RAD), "ruleaza %s e=%s" % (cale, head)):
        plan, o, d = r.operatie_curenta(RAD, head)
        op = o["operatie"]
        try:
            r.verifica_git(RAD, plan, o["baza"])
        except (r.Refuz, OSError, subprocess.CalledProcessError) as ex:
            raise SystemExit("REFUZ: identitatea versiunii țintă: %s" % ex)
        if r.are_stadiu(d, "rulata"):
            print("[migrari] %s e deja rulată în operația %s; continuă: sh scripts/publica_lot.sh --confirma-migrare %s %s"
                  % (cale, op, plan.lot, plan.e))
            return 0
        if r.are_stadiu(d, "ddl_inceput"):
            _env_productie()
            exacte, ev = _rand_exact(plan)
            if exacte == [(plan.fisier, plan.digest, "rulata", plan.e)]:
                r.adauga_stadiu(d, "rulata", recuperat="registru")
                print("[migrari] rândul registrului există; continuă: sh scripts/publica_lot.sh --confirma-migrare %s %s" % (plan.lot, plan.e))
                return 0
            r.adauga_stadiu(d, "reconciliere", motiv="DDL început fără rând de registru", schema="; ".join(ev["schema"] or []) or "la zi")
            _ev("reconciliere", operatie=op, registru=[list(x) for x in exacte], schema=ev["schema"])
            print("[migrari] RECONCILIERE: DDL-ul operației %s a început, dar registrul nu are rândul exact; rezultatul e necunoscut. Nu se "
                  "reexecută și nu se scrie rândul: decizia o ia omul pe dovezile din %s" % (op, d))
            return 3
        if not r.are_stadiu(d, "asteapta_migrare"):
            raise SystemExit("REFUZ: operația %s nu e în așteptarea migrării" % op)
        try:
            raw = (d / "aprobare.json").read_bytes()
            sig = (d / "aprobare.json.sig").read_bytes()
        except OSError:
            raise SystemExit("REFUZ: lipsește acordul semnat al lui Costin în %s (aprobare.json, aprobare.json.sig)" % d)
        inceput = _dt.datetime.fromtimestamp(o["deschisa_ns"] / 1e9, _dt.timezone.utc)
        try:
            sha_acord, emis = canal.verifica_acord(RAD, o["baza"], raw, sig, plan, op, inceput, _dt.datetime.now(_dt.timezone.utc))
        except (ValueError, OSError, subprocess.CalledProcessError) as ex:
            raise SystemExit("REFUZ: acordul nu e valid pentru această operație: %s" % ex)
        acord_ns = int(emis.timestamp()) * 10**9
        _ev("acord", operatie=op, sha256_acord=sha_acord, emis_la=emis.isoformat())
        if not r.are_stadiu(d, "acord_verificat"):
            r.adauga_stadiu(d, "acord_verificat", sha256=sha_acord)
        backup, b = backup_confirmat(d, plan, o, acord_ns)
        try:
            r.permite_ddl(plan, (plan.lot, plan.e, plan.fisier, plan.digest), backup, max(o["deschisa_ns"], acord_ns), time.time_ns())
        except r.Refuz as ex:
            raise SystemExit("REFUZ: %s" % ex)
        _ev("backup", operatie=op, invocatie=backup.invocatie, cale=b["cale"], sha256=backup.digest)
        if not r.are_stadiu(d, "backup_confirmat"):
            r.adauga_stadiu(d, "backup_confirmat", sha256=backup.digest)
        _env_productie()
        exacte, ev = _rand_exact(plan)
        stare, motiv = decizie_plan(ev, plan)
        if stare != "asteapta_migrare":
            r.adauga_stadiu(d, "refuz_rulator", motiv=motiv or stare)
            raise SystemExit("REFUZ: starea bazei nu e așteptarea migrării declarate: %s" % (motiv or stare))
        inainte = []
        _cu_registrul(lambda cur: inainte.extend(inainte_nerulate(cur, cale)))
        if inainte:
            raise SystemExit("REFUZ: %s se rulează după %s, nerulată încă" % (cale, ", ".join(inainte)))
        r.adauga_stadiu(d, "ddl_inceput")
        _ev("scriere_db", operatie=op, fisier=cale)
        import runpy
        sys.argv = [cale]
        runpy.run_path(os.path.join(RAD, cale), run_name="__main__")   # o excepție oprește aici: nimic scris în registru
        r.punct_proba("dupa_ddl")
        _cu_registrul(lambda cur: inregistreaza(cur, cale, plan.digest, "rulata", plan.e))
        _ev("registru", operatie=op, fisier=cale, amprenta=plan.digest, fel="rulata", commit=plan.e)
        r.punct_proba("dupa_registru")
        r.adauga_stadiu(d, "rulata")
        print("[migrari] registrul migrărilor: %s rulată (amprenta %s, E %s). Restartul îl face numai: sh scripts/publica_lot.sh "
              "--confirma-migrare %s %s" % (cale, plan.digest[:12], plan.e, plan.lot, plan.e))
        return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    productie = "--productie" in rest
    rest = [x for x in rest if x != "--productie"]
    if cmd == "verifica":
        if len(rest) >= 2 and rest[1] in ("--publicare", "--confirmare"):
            cod, linii, date = verifica_plan(rest[0], rest[1], rest[2] if len(rest) > 2 else None)
            for ln in linii:
                print(ln)
            print(json.dumps(dict(eveniment="schema", cod=cod, **date), ensure_ascii=False, sort_keys=True))
            return cod
        cod, linii = verifica(rest[0])
        for ln in linii:
            print(ln)
        return cod
    if productie:
        motiv = refuz_fara_pass(PASS_LOG)
        if motiv:
            print(motiv)
            return 1
        motiv = garda_productie(cmd, rest)   # [17.5-P0] înaintea mediului bazei, a registrului, a oricărui DDL sau runpy
        if motiv:
            print(motiv)
            return 1
        if cmd in ("ruleaza", "backup-inainte"):
            po = _reguli().plan_pentru_head(RAD)
            if po is not None and rest[0] == po[0].fisier:
                if cmd == "backup-inainte":
                    with _reguli().lacat(_reguli().comun(RAD), "backup-inainte"):
                        return backup_inainte(_reguli().operatie_curenta(RAD, po[1]["e"])[2])
                return ruleaza_declarata(rest[0])
        _env_productie()
    elif cmd == "backup-inainte":
        print("backup-inainte se folosește numai cu --productie")
        return 2
    commit = _git("rev-parse", "--short", "HEAD").strip()
    if cmd == "baza":
        migrari = migrari_la_commit(rest[0])
        _cu_registrul(lambda cur: [inregistreaza(cur, f, a, "baza", rest[0][:8], "baza registrului 09.10.2026: rulată înainte "
                                                 "de registru, fără dovadă") for f, a in migrari.items()])
        print("baza registrului: %d migrări din %s" % (len(migrari), rest[0][:8]))
        return 0
    if cmd in ("ruleaza", "marcheaza"):
        cale = rest[0]
        text = open(os.path.join(RAD, cale), encoding="utf-8").read()
        if not e_migrare(cale, text):
            raise SystemExit("%s nu e o migrare (core/migrare_<nume>.py cu bloc __main__)" % cale)
        if cmd == "ruleaza":
            # [lotul 11, comanda Costin 11.2 pct.2 — 409] pe PRODUCȚIE o migrare cu aceeași amprentă nu se rulează a doua oară: reparația
            # pe datele F1 s-a aplicat de două ori (lotul 9 și lotul 10), fiindcă nimic nu refuza o rulare repetată. Pe baza de TEST rularea
            # repetată rămâne admisă (plasa și subagenții refac schemele).
            if productie:
                deja = []
                _cu_registrul(lambda cur: deja.extend([] if nerulate(cur, {cale: amprenta(text)}) else [cale]))
                if deja:
                    raise SystemExit("%s (amprenta %s) e deja rulată pe producție — o a doua rulare a aceleiași migrări nu se face "
                                     "(reparația 409 aplicată de două ori, lotul 11)." % (cale, amprenta(text)[:12]))
            inainte = []
            _cu_registrul(lambda cur: inainte.extend(inainte_nerulate(cur, cale)))
            if inainte:
                raise SystemExit("%s se rulează după %s, nerulată încă pe această bază — rulează întâi: %s" % (
                    cale, ", ".join(inainte), "; ".join("python -m core.migrari_registru ruleaza%s %s" % (
                        " --productie" if productie else "", f) for f in inainte)))
            import runpy
            sys.argv = [cale]
            runpy.run_path(os.path.join(RAD, cale), run_name="__main__")   # o excepție oprește aici: nimic scris în registru
            _cu_registrul(lambda cur: inregistreaza(cur, cale, amprenta(text), "rulata", commit))
            print("registrul migrărilor: %s rulată (amprenta %s)" % (cale, amprenta(text)[:12]))
        else:
            if len(rest) < 2 or not rest[1].strip():
                raise SystemExit("marcarea fără rulare cere motivul (de ce schimbarea nu cere rulare)")
            _cu_registrul(lambda cur: inregistreaza(cur, cale, amprenta(text), "marcata", commit, rest[1].strip()))
            print("registrul migrărilor: %s marcată fără rulare — %s" % (cale, rest[1].strip()))
        _reporneste_daca_e_cazul(productie)
        return 0
    print("comandă necunoscută: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.path.insert(0, RAD)
    sys.exit(main(sys.argv[1:]))
