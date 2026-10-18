# -*- coding: utf-8 -*-
"""
core/sonda_web.py — R75, varianta (b): procesul care servește ecranele intră în deadman.

DECIZIA lui Costin (27.08.2026): *„(b) e în aceeași formă cu ce merge deja: `cron.RITMURI`
supraveghează 11 joburi; al 12-lea e procesul care le servește pe toate."* Iar cerința lui, în
cuvintele lui: **„procesul e viu ȘI răspunde"** — nu doar că unitatea e `active`.

De ce nu (a), sonda externă: *„cere un serviciu extern care devine el însuși ceva de întreținut."*
De ce nu (c): *„declară acceptată o cădere pe care n-am putut-o explica."*

CE FACE, în ordinea în care contează:
  1. **cere pagina**, nu întreabă systemd: `GET /` local, cod 200 și corp nevid. Un proces `active`
     care nu mai răspunde e exact felul de cădere pe care „viu" n-o vede.
  2. **compară ora de pornire a unității** cu cea de la sonda precedentă. Dacă s-a schimbat,
     procesul **a repornit între cele două sonde** — și o spune, cu amândouă orele.
  3. bate în `cron_batai` prin `cron.ruleaza`, deci lipsa sondei însăși devine vizibilă.

CE PRINDE ȘI CE NU — și distincția e cerută explicit de Costin: *„dacă o cădere de trei secunde
nu se prinde cu ritmul supravegherii, spune — atunci ce se prinde e repornirea, nu căderea, și
aia e o afirmație mai slabă care se scrie ca atare."*

  PRINDE:
    · procesul căzut ȘI nerepornit — sonda ia eroare de conexiune, `cron.ruleaza` alertează;
    · procesul viu care **nu mai răspunde** (200 care nu mai vine, corp gol);
    · **o repornire petrecută între două sonde**, iar de la 27.08 le și **deosebește**: o
      repornire cu **alt commit** e un **deploy** (`post-commit` repornește serviciul la fiecare
      commit) și **nu alertează**; una cu **același** commit n-a cerut-o nimeni, și alertează.
      Commitul e al PROCESULUI care rulează (registrul instanțelor), nu cel de pe disc (271).
      Dacă vreun commit nu se poate citi, se alertează spunând că **nu se poate deosebi** — inclusiv una de trei secunde, fiindcă ora de
      pornire se schimbă și rămâne schimbată. **Dar o prinde ca REPORNIRE, nu ca durată**: nu se
      poate spune cât a fost jos, doar că a fost.
  NU PRINDE:
    · **cât a durat căderea.** Între două sonde la 15 minute, o cădere de 3 secunde și una de 14
      minute arată identic;
    · **două reporniri între aceleași două sonde** — se vede una;
    · **serverul jos cu totul.** Atunci nu rulează nici sonda. E aceeași limită declarată în
      `cron.verifica_batai`, și pe ea o acoperă doar un deadman EXTERN.

Rulare: `python3 -m core.sonda_web` (crontab, la 15 minute).

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

NUME = "sonda_web"
BAZA = "http://127.0.0.1:8010"
UNITATE = "iconta-nou.service"

#: [11.09.2026] Gazda PUBLICA a aplicatiei, declarata intr-un singur loc. Nu e folosita de
#: sonda deadman — aia cere procesul LOCAL, si asa trebuie sa ramana (un 200 prin nginx poate
#: veni dintr-un cache sau de la alt upstream, deci ar putea fi verde peste un proces mort).
#: Sta aici ca sa existe UN loc adevarat: in aceeasi zi am verificat de patru ori la rand un
#: alt domeniu de-al nostru, care raspundea 200 in timp ce aplicatia era cazuta cu 502.
#: Pazita de `core/test_gazda_productie.py`.
GAZDA_PRODUCTIE = "https://iconta.eu"


def ora_pornirii(unitate=None):
    # globala se citeste AICI, nu ca argument implicit: altfel valoarea se fixeaza la definirea
    # functiei, iar calea de esec nu se poate proba. (Prins de propria calibrare, 27.08.2026.)
    unitate = unitate or UNITATE
    """`ActiveEnterTimestamp` al unității, ca text. None dacă nu se poate citi (nu e o eroare:
    sonda are voie să nu știe, dar nu are voie să pretindă că știe)."""
    try:
        r = subprocess.run(["systemctl", "show", unitate, "-p", "ActiveEnterTimestamp",
                            "--value"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    v = (r.stdout or "").strip()
    return v or None


def ora_bootarii(cale="/proc/stat"):
    """[18.10.2026, comanda Costin 8.1 pct.6] Ora la care a pornit MAȘINA (`btime` din /proc/stat), ca dată locală fără fus; None dacă nu
    se poate citi. Repornirea serverului de la 09:02 (`sudo reboot`, kernelul nou) a fost numită „procesul a căzut și s-a ridicat singur”."""
    import datetime as _dtm
    try:
        for ln in open(cale, encoding="ascii"):
            if ln.startswith("btime "):
                return _dtm.datetime.fromtimestamp(int(ln.split()[1]))
    except (OSError, ValueError):
        return None
    return None


def _ca_data(pornit):
    """`ActiveEnterTimestamp` („Sun 2026-10-18 09:02:51 EEST”) -> datetime local, fără fus; None dacă nu se recunoaște."""
    import datetime as _dtm
    m = re.search(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", pornit or "")
    return _dtm.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S") if m else None


def raspunde(baza=None, cale="/"):
    """(cod, octeti). Ridică urllib.error dacă nu se poate conecta — voit: `cron.ruleaza` o prinde."""
    baza = baza or BAZA          # vezi nota de la `ora_pornirii`
    with urllib.request.urlopen(baza + cale, timeout=20) as r:
        corp = r.read()
        return r.getcode(), len(corp)


def commitul_procesului(conn):
    """Commitul pe care RULEAZĂ procesele vii ale aplicației de pe această gazdă, ca text. None dacă nu se poate spune unul singur.

    [deficiența 271, comanda 4 a lotului 5: „sonda citește commitul procesului care rulează”] Sursa e registrul instanțelor
    (`public.instante`): fiecare proces web se trece acolo LA PORNIRE cu commitul ștampilat în memoria lui (`versiune.RUNNING_COMMIT`,
    `instante.inregistreaza`) și bate din fundal. Sonda e alt proces (cron), deci nu poate citi memoria procesului web — `versiune.stare()`
    i-ar da mereu None — dar citește registrul.
    Înainte se citea `HEAD` de pe DISC, iar publicarea mută discul ÎNAINTEA repornirii (fast-forward, apoi migrările, apoi restartul):
    o sondă nimerită între ele nota ora veche de pornire lângă commitul NOU, iar sonda următoare vedea „a repornit cu același commit” =
    cădere (alerta din 15.10.2026 18:15, după publicarea lotului 4; la fel pe 14.10).
    Două commituri diferite printre procesele vii (o repornire în curs) sau niciun proces viu -> None: sonda spune că nu poate deosebi.
    """
    from core import instante
    gazda = instante.eu()[0]
    sha = {c for g, _pid, c, _pornit in instante.vii(conn) if g == gazda}
    return next(iter(sha)) if len(sha) == 1 else None


def _citeste_ultima(conn):
    """(pornit_la, commit) de la sonda precedentă. (None, None) la prima rulare."""
    with conn.cursor() as cur:
        cur.execute("SELECT detalii FROM public.cron_batai WHERE nume=%s", (NUME,))
        r = cur.fetchone()
    if not r or not r[0]:
        return None, None
    d = r[0] if isinstance(r[0], dict) else json.loads(r[0])
    return d.get("pornit_la"), d.get("commit")


def _scrie_ultima(conn, pornit_la, commit):
    import psycopg2.extras as _E
    with conn.cursor() as cur:
        # upsert-ok: sonda are un singur rand, pe nume — se suprascrie deliberat la fiecare rulare
        cur.execute("INSERT INTO public.cron_batai (nume, ultima_reusita, rulari, detalii) "
                    "VALUES (%s, now(), 0, %s) "
                    "ON CONFLICT (nume) DO UPDATE SET detalii = EXCLUDED.detalii",
                    (NUME, _E.Json({"pornit_la": pornit_la, "commit": commit})))


def fel_repornirii(pornit_inainte, pornit_acum, commit_inainte, commit_acum, server_repornit=False):
    """PURĂ. -> None (n-a repornit) | "deploy" | "necunoscut" | "server" | "cadere".

    DE CE EXISTĂ, și e o reparație de dinaintea primei alerte: `post-commit` repornește serviciul
    la **fiecare** commit. Fără distincția asta, sonda ar fi alertat de zece ori pe zi despre
    reporniri pe care chiar noi le-am produs — iar *„o alarmă care se aprinde mereu nu mai e
    semnal"* e chiar doctrina scrisă în `core/cron.py`.

    Criteriul: dacă s-a schimbat **și** commitul, procesul a fost repornit **deliberat** (deploy).
    Dacă a repornit cu **același** commit, nimeni n-a cerut-o — aia e căderea care ne interesează.
    Dacă vreun commit nu se poate citi, se întoarce `"necunoscut"`: se raportează, dar se **spune**
    că nu se poate deosebi. Sonda are voie să nu știe; n-are voie să pretindă.
    """
    if not (pornit_inainte and pornit_acum) or pornit_inainte == pornit_acum:
        return None
    if not (commit_inainte and commit_acum):
        return "necunoscut"
    if commit_inainte != commit_acum:
        return "deploy"
    # [18.10.2026] același commit, dar MAȘINA a pornit după procesul de dinainte: repornirea serverului (cerută sau a furnizorului), nu o
    # cădere a aplicației — se spune ce a fost
    return "server" if server_repornit else "cadere"


def verifica():
    """-> dict cu ce s-a observat. Ridică dacă procesul nu răspunde."""
    from core import db
    cod, octeti = raspunde()
    if cod != 200 or octeti < 200:
        raise RuntimeError("procesul răspunde %s cu %d octeți — pagina publică e goală sau ruptă"
                           % (cod, octeti))
    pornit = ora_pornirii()
    db.init_pool()
    with db.get_conn() as conn:
        commit = commitul_procesului(conn)
        pornit_inainte, commit_inainte = _citeste_ultima(conn)
    boot, inainte = ora_bootarii(), _ca_data(pornit_inainte)
    fel = fel_repornirii(pornit_inainte, pornit, commit_inainte, commit, server_repornit=bool(boot and inainte and boot > inainte))
    # `deploy` NU alertează: e o repornire pe care am cerut-o noi. Restul, da.
    if fel == "server":
        from core import observare
        from core import pdf_util as _pu
        observare.alerteaza(
            "sonda_web_repornire", "Serverul iConta a repornit (mașina, nu numai procesul)",
            "Mașina a pornit la %s; procesul %s a pornit odată cu ea, pe același commit (%s).\n\n  înainte: %s\n  acum:    %s\n\n"
            "Nu e o cădere a aplicației și nici un deploy: serverul a fost repornit — cerut de cineva cu acces (de exemplu ca să "
            "activeze un kernel nou) sau de furnizor. Cine a cerut-o se vede în jurnalul sistemului (`journalctl -b -1`)."
            % ("%s %s" % (_pu.data_ro(boot), boot.strftime("%H:%M:%S")), UNITATE, commit, pornit_inainte, pornit))
    elif fel in ("cadere", "necunoscut"):
        from core import observare
        observare.alerteaza(
            "sonda_web_repornire",
            "Procesul iConta a repornit fără să fi fost un deploy"
            if fel == "cadere" else "Procesul iConta a repornit — nu se poate spune dacă a fost deploy",
            "Ora de pornire a %s s-a schimbat.\n\n  înainte: %s  (commit %s)\n  acum:    %s  (commit %s)\n\n"
            "%s\n\n"
            "Sonda spune CĂ a repornit, nu cât a fost jos: între două rulări la 15 minute, o "
            "cădere de trei secunde și una de paisprezece minute arată la fel."
            % (UNITATE, pornit_inainte, commit_inainte, pornit, commit,
               "Commitul e ACELAȘI, deci n-a fost un deploy — procesul a căzut și s-a ridicat singur."
               if fel == "cadere" else
               "Nu s-a putut citi unul din commituri, deci nu se poate deosebi un deploy de o cădere."))
    if pornit:
        db.init_pool()
        with db.get_conn() as conn:
            _scrie_ultima(conn, pornit, commit)
    return {"cod": cod, "octeti": octeti, "pornit_la": pornit, "commit": commit,
            "repornit": fel is not None, "fel": fel}


def _main():
    r = verifica()
    print("sonda_web: cod=%s octeti=%s pornit_la=%s commit=%s repornit=%s (%s)"
          % (r["cod"], r["octeti"], r["pornit_la"], r["commit"], r["repornit"], r["fel"]),
          flush=True)
    return r


if __name__ == "__main__":
    from core import cron
    cron.ruleaza(NUME, _main)
    sys.exit(0)
