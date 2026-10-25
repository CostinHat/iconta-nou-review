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
După o rulare reușită pe producție, dacă hook-ul a oprit restartul (`.git/RESTART_OPRIT_MIGRARE`) și HEAD nu mai are nimic de rulat,
rulatorul repornește aplicația — exact pasul pe care hook-ul l-a amânat.
"""
import hashlib
import os
import re
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTINELA = os.path.join(RAD, ".git", "RESTART_OPRIT_MIGRARE")
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


def verifica(sha, conn=None):
    """(cod, rânduri de tipărit): 0 = HEAD poate porni pe producție; 1 = migrări nerulate / schemă în urmă; 2 = nu se poate ști.
    `conn` dat = baza pe care se întreabă (testele); altfel producția. Totul sub un singur ROLLBACK (schema de referință a
    auditului e temporară; nimic nu se scrie)."""
    proprie = conn is None
    if proprie:
        conn, motiv = _conexiune_productie()
        if conn is None:
            return 2, ["NU SE POATE ȘTI dacă producția are migrările lui %s: %s" % (sha[:8], motiv)]
    try:
        with conn.cursor() as cur:
            lipsa = nerulate(cur, migrari_la_commit(sha))
        drift = drift_schema(conn, _git("show", "%s:tenant_template.sql" % sha))
    finally:
        conn.rollback()
        if proprie:
            conn.close()
    linii = ["migrare nerulată pe producție: %s (amprenta %s) — rulează: ./venv/bin/python -m core.migrari_registru ruleaza "
             "--productie %s" % (f, a[:12], f) for f, a in lipsa]
    for s, d in sorted(drift.items()):
        linii.append("schema %s e în urma șablonului: tabele lipsă %s, coloane lipsă %s, triggere lipsă %s" % (
            s, d["tabele_lipsa"] or "-", dict(d["coloane_lipsa"]) or "-", d.get("triggere_lipsa") or "-"))
    return (1 if linii else 0), linii


def _env_productie():
    from core import mediu_test as _m
    url = _m.dsn_productie()
    if not url:
        raise SystemExit("nu se găsește DATABASE_URL în %s" % _m.CALE_DB_ENV)
    os.environ["DATABASE_URL"] = url


def _cu_registrul(scrie):
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            scrie(cur)
        conn.commit()


def _reporneste_daca_e_cazul(productie):
    if not (productie and os.path.exists(SENTINELA)):
        return
    head = _git("rev-parse", "HEAD").strip()
    cod, linii = verifica(head)
    if cod != 0:
        print("restartul rămâne oprit — HEAD %s mai are de rulat:\n  %s" % (head[:8], "\n  ".join(linii)))
        return
    # [10.10.2026, lotul „Retestul plasei”] statica HEAD-ului se publică ÎNAINTEA restartului, aici: cu restartul oprit, post-commit n-o
    # mai publică (ar fi ajuns JS-ul commitului peste backendul vechi), deci procesul nou ar porni altfel pe statica commitului anterior
    ps = subprocess.run([sys.executable, os.path.join(RAD, "scripts", "publica_static.py")], capture_output=True, text=True, cwd=RAD)
    if ps.returncode != 0:
        print("restartul rămâne oprit — statica lui %s nu s-a publicat (%s); rulează: ./venv/bin/python scripts/publica_static.py, "
              "apoi: sudo systemctl restart iconta-nou" % (head[:8], (ps.stdout or ps.stderr).strip().splitlines()[-1:] or "?"))
        return
    print("statica publicată: %s" % ((ps.stdout or "").strip().splitlines()[-1:] or ["?"])[0])
    r = subprocess.run(["sudo", "-n", "systemctl", "restart", "iconta-nou"], capture_output=True, text=True)
    if r.returncode == 0:
        os.remove(SENTINELA)
        print("toate migrările lui %s sunt rulate pe producție: iconta-nou repornit, preia HEAD" % head[:8])
        # [12.10.2026] publicarea se închide abia cu four-way-ul: același script ca post-commit (scrie sau șterge .git/FOUR_WAY_NEINCHIS);
        # fără el sentinela scrisă de post-commit la restartul oprit rămânea după ce toate brațele se închiseseră
        fw = subprocess.run(["sh", os.path.join(RAD, "scripts", "githooks", "four-way")], capture_output=True, text=True, cwd=RAD)
        print((fw.stdout + fw.stderr).strip())
    else:
        print("restartul a eșuat (%s) — rulează: sudo systemctl restart iconta-nou" % (r.stderr.strip() or r.stdout.strip()))


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    productie = "--productie" in rest
    rest = [x for x in rest if x != "--productie"]
    if cmd == "verifica":
        cod, linii = verifica(rest[0])
        for ln in linii:
            print(ln)
        return cod
    if productie:
        _env_productie()
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
