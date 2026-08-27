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
    · **o repornire petrecută între două sonde** — inclusiv una de trei secunde, fiindcă ora de
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


def _citeste_ultima(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT detalii FROM public.cron_batai WHERE nume=%s", (NUME,))
        r = cur.fetchone()
    if not r or not r[0]:
        return None
    d = r[0] if isinstance(r[0], dict) else json.loads(r[0])
    return d.get("pornit_la")


def _scrie_ultima(conn, pornit_la):
    import psycopg2.extras as _E
    with conn.cursor() as cur:
        # upsert-ok: sonda are un singur rand, pe nume — se suprascrie deliberat la fiecare rulare
        cur.execute("INSERT INTO public.cron_batai (nume, ultima_reusita, rulari, detalii) "
                    "VALUES (%s, now(), 0, %s) "
                    "ON CONFLICT (nume) DO UPDATE SET detalii = EXCLUDED.detalii",
                    (NUME, _E.Json({"pornit_la": pornit_la})))
    conn.commit()


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
        inainte = _citeste_ultima(conn)
    repornit = bool(inainte and pornit and inainte != pornit)
    if repornit:
        from core import observare
        observare.alerteaza(
            "sonda_web_repornire",
            "Procesul iConta a repornit între două sonde",
            "Ora de pornire a %s s-a schimbat.\n\n  înainte: %s\n  acum:    %s\n\n"
            "Sonda spune CĂ a repornit, nu cât a fost jos: între două rulări la 15 minute, o "
            "cădere de trei secunde și una de paisprezece minute arată la fel.\n"
            "Dacă repornirea e a ta (deploy, restart manual), ignor-o." % (UNITATE, inainte, pornit))
    if pornit:
        db.init_pool()
        with db.get_conn() as conn:
            _scrie_ultima(conn, pornit)
    return {"cod": cod, "octeti": octeti, "pornit_la": pornit, "repornit": repornit}


def _main():
    r = verifica()
    print("sonda_web: cod=%s octeti=%s pornit_la=%s repornit=%s"
          % (r["cod"], r["octeti"], r["pornit_la"], r["repornit"]), flush=True)
    return r


if __name__ == "__main__":
    from core import cron
    cron.ruleaza(NUME, _main)
    sys.exit(0)
