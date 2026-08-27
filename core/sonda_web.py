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
import json
import subprocess
import sys
import urllib.error
import urllib.request

NUME = "sonda_web"
BAZA = "http://127.0.0.1:8010"
UNITATE = "iconta-nou.service"


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


def raspunde(baza=None, cale="/"):
    """(cod, octeti). Ridică urllib.error dacă nu se poate conecta — voit: `cron.ruleaza` o prinde."""
    baza = baza or BAZA          # vezi nota de la `ora_pornirii`
    with urllib.request.urlopen(baza + cale, timeout=20) as r:
        corp = r.read()
        return r.getcode(), len(corp)


def commitul_de_pe_disc():
    """`HEAD` din checkout, ca text scurt. None dacă nu se poate citi.

    NU commitul din memoria procesului web: acela e ștampilat la pornirea LUI, iar sonda e un alt
    proces — l-ar citi mereu `None` și ar raporta veșnic „necunoscut". (Prins la prima rulare
    reală, 27.08.2026, nu la scriere.)

    Ce discriminează: la un **deploy**, `post-commit` mută `HEAD` **și** repornește serviciul —
    deci ambele se schimbă. La o **cădere**, procesul repornește cu `HEAD` neatins.
    Limita, declarată: dacă o cădere se nimerește în aceeași fereastră de 15 minute cu un commit,
    e citită ca deploy. Fereastra e mică și prețul e o cădere ratată, nu o alarmă falsă.
    """
    try:
        from core import versiune
        return versiune.git_head(versiune.RAD)
    except Exception:
        return None


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
    conn.commit()


def fel_repornirii(pornit_inainte, pornit_acum, commit_inainte, commit_acum):
    """PURĂ. -> None (n-a repornit) | "deploy" | "necunoscut" | "cadere".

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
    return "deploy" if commit_inainte != commit_acum else "cadere"


def verifica():
    """-> dict cu ce s-a observat. Ridică dacă procesul nu răspunde."""
    from core import db
    cod, octeti = raspunde()
    if cod != 200 or octeti < 200:
        raise RuntimeError("procesul răspunde %s cu %d octeți — pagina publică e goală sau ruptă"
                           % (cod, octeti))
    pornit = ora_pornirii()
    commit = commitul_de_pe_disc()
    db.init_pool()
    with db.get_conn() as conn:
        pornit_inainte, commit_inainte = _citeste_ultima(conn)
    fel = fel_repornirii(pornit_inainte, pornit, commit_inainte, commit)
    # `deploy` NU alertează: e o repornire pe care am cerut-o noi. Restul, da.
    if fel in ("cadere", "necunoscut"):
        from core import observare
        observare.alerteaza(
            "sonda_web_repornire",
            "Procesul iConta a repornit fără să fi fost un deploy"
            if fel == "cadere" else "Procesul iConta a repornit — nu pot spune dacă a fost deploy",
            "Ora de pornire a %s s-a schimbat.\n\n  înainte: %s  (commit %s)\n  acum:    %s  (commit %s)\n\n"
            "%s\n\n"
            "Sonda spune CĂ a repornit, nu cât a fost jos: între două rulări la 15 minute, o "
            "cădere de trei secunde și una de paisprezece minute arată la fel."
            % (UNITATE, pornit_inainte, commit_inainte, pornit, commit,
               "Commitul e ACELAȘI, deci n-a fost un deploy — procesul a căzut și s-a ridicat singur."
               if fel == "cadere" else
               "Nu s-a putut citi unul din commituri, deci nu pot deosebi un deploy de o cădere."))
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
