# -*- coding: utf-8 -*-
"""GARD — niciun secret în fișierele urmărite de git (comanda Costin 05.10.2026).

Comanda: *„Parola contului de cabinet contabil.b@sesiuneab.test e încă în git (frontend_test/f1_helper.py:12), iar oglinda e
publică […] Caută alte parole în clar în tot arborele […]; același tratament.”* Căutând s-a găsit și **parola bazei de
producție**, scrisă de un instrument de măsurare într-un artefact comis (`masuratori/p3/concurenta.json`). Amândouă erau pe
oglinda publică. Istoria nu se rescrie; secretele s-au rotit. Gardul face ca un secret să nu mai poată intra: rulează în
poartă, iar poarta rulează înainte de commit.

DOUĂ TREPTE, fiindcă prind lucruri diferite:
1. **Valorile reale** din `~/.iconta/*.env` (parole, chei, jetoane, partea de parolă a unui DSN) nu apar în niciun fișier
   urmărit. Prinde orice formă — și un artefact care serializează configurația, cum a fost `str(cfg)`.
2. **Tiparele** lui `audit/scan_secrete.py` (o singură implementare, aceeași cu scanul pachetului de audit) dau, pe fiecare
   fișier, exact numărul declarat mai jos — lista e ÎNCHISĂ, cu motivul fiecărei intrări. Prinde un secret care nu e (încă)
   în `~/.iconta`: o parolă de probă nouă, un DSN cu parolă, o cheie lipită.

LIMITA, declarată: treapta 1 vede doar valorile pe care le are serverul care rulează poarta (acolo trăiesc); treapta 2 vede
doar ce seamănă cu un tipar. Un secret fără nume lângă el și care nu e în `~/.iconta` trece amândouă.
"""
import glob
import os
import re
import subprocess
import sys
from collections import Counter

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "audit"))
import scan_secrete as ss  # noqa: E402

DIR_SECRETE = os.path.expanduser("~/.iconta")
# cheile ale căror valori sunt secrete (DB_NAME, DB_USER, URL-urile publice nu sunt)
_CHEIE_SECRETA = re.compile(r"PASS|PAROLA|SECRET|KEY|TOKEN|_CK$|_CS$|CLIENT_ID")
_TIPARE = ("CHEIE_PRIVATA", "CHEIE_PUTTY", "AWS_ACCESS_KEY", "TOKEN_GITHUB", "TOKEN_OPENAI", "TOKEN_SLACK", "CHEIE_BREVO",
           "JWT", "SIR_CONEXIUNE_CU_PAROLA", "PAROLA_ATRIBUITA", "PGPASSWORD", "AUTORIZARE_HTTP")

# Lista ÎNCHISĂ: (fișier, tipar) -> (câte potriviri, de ce nu e un secret). Numărul e EXACT: o potrivire în plus = un secret
# nou de judecat; una în minus = intrarea se scoate (lista nu poate deveni o listă de ignorat).
_PERMISE = {
    ("audit/scan_secrete.py", "AUTORIZARE_HTTP"): (1, "mostra de calibrare a scannerului (secret sintetic, prin construcție)"),
    ("audit/scan_secrete.py", "AWS_ACCESS_KEY"): (1, "mostra de calibrare (cheia-exemplu publică din documentația AWS)"),
    ("audit/scan_secrete.py", "CHEIE_PRIVATA"): (1, "mostra de calibrare: doar antetul, fără cheie"),
    ("audit/scan_secrete.py", "CHEIE_PUTTY"): (2, "tiparul și mostra de calibrare: doar antetul formatului"),
    ("audit/scan_secrete.py", "JWT"): (1, "mostra de calibrare: jeton-exemplu, nesemnat de cheia noastră"),
    ("audit/scan_secrete.py", "PAROLA_ATRIBUITA"): (2, "mostrele de calibrare (`TOKEN_SLACK`, `SIR_CONEXIUNE_CU_PAROLA`)"),
    ("audit/scan_secrete.py", "PGPASSWORD"): (1, "mostra de calibrare a parolei Postgres din mediu (sintetică)"),
    ("audit/scan_secrete.py", "SIR_CONEXIUNE_CU_PAROLA"): (1, "mostra de calibrare `utilizator:parolasecreta@gazda`"),
    ("audit/scan_secrete.py", "TOKEN_SLACK"): (1, "mostra de calibrare a scannerului (jeton Slack sintetic)"),
    ("audit/CUM_RULEZI_POARTA.md", "SIR_CONEXIUNE_CU_PAROLA"): (1, "substituent `<rol_test>:<parola>` într-o instrucțiune"),
    ("core/mediu_test.py", "SIR_CONEXIUNE_CU_PAROLA"): (1, "docstring: forma `user:parola@host`, fără valori"),
    ("core/test_izolare_productie.py", "SIR_CONEXIUNE_CU_PAROLA"): (4, "DSN-uri sintetice (parola `x` / `a@b/c`) și un format `%s:%s`"),
    ("core/test_wave3_instante.py", "SIR_CONEXIUNE_CU_PAROLA"): (1, "DSN sintetic `cineva:x@…/alta_baza`"),
    ("masuratori/p3/concurenta.json", "SIR_CONEXIUNE_CU_PAROLA"): (1, "redactat `***` (05.10.2026; parola veche rotită)"),
    ("masuratori/r68/R68_LIVE_BEFORE.txt", "SIR_CONEXIUNE_CU_PAROLA"): (1, "deja redactat `***` la scriere"),
    ("core/test_p4_fault_injection.py", "PAROLA_ATRIBUITA"): (5, "parola unei înregistrări făcute să EȘUEZE (cont șters de "
                                                                 "test) + jetoane OAuth false dintr-un răspuns simulat"),
    ("core/test_post_token_fara_conexiune.py", "PAROLA_ATRIBUITA"): (3, "jetoane OAuth false (`acc-…`, `ref-…`) ale serverului simulat"),
    ("core/lexicon_diacritice.json", "PAROLA_ATRIBUITA"): (1, "perechea de lexicon `\"parola\": \"parolă\"` (forma fără diacritice "
                                                            "a unui cuvânt, nu o parolă) — Retest 2, lexiconul derivat din corpus"),
    ("core/test_spv_conector.py", "PAROLA_ATRIBUITA"): (3, "jetoane de reîmprospătare false ale serverului simulat"),
    ("core/test_wave1_stare_partajata.py", "PAROLA_ATRIBUITA"): (1, "parolă GREȘITĂ intenționat (se numără logările eșuate)"),
    ("static/js/sesiune.js", "PAROLA_ATRIBUITA"): (2, "NUMELE cheilor din sessionStorage (`iconta_token`), nu valori"),
    ("core/test_fara_secrete_in_git.py", "PAROLA_ATRIBUITA"): (5, "mostrele de calibrare ale ACESTUI gard (`nuOparola…`, sintetice)"),
    ("core/test_fara_secrete_in_git.py", "SIR_CONEXIUNE_CU_PAROLA"): (1, "mostra de calibrare a redactării (`u:nuOparola9@h`)"),
}


def _urmarite():
    out = subprocess.run(["git", "ls-files"], cwd=RAD, capture_output=True, text=True, check=True).stdout.split("\n")
    return [f for f in out if f and not f.startswith("venv/") and not f.lower().endswith(ss.BINARE)]


def _text(f):
    try:
        return open(os.path.join(RAD, f), encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return None


def _valori_secrete():
    """{valoare: [fișier:cheie]} din `~/.iconta/*.env` — doar cheile secrete, plus partea de parolă a unui DSN."""
    out = {}
    for f in sorted(glob.glob(os.path.join(DIR_SECRETE, "*.env"))):
        for ln in open(f, encoding="utf-8", errors="replace"):
            m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*)$", ln.rstrip("\n"))
            if not m:
                continue
            k, v = m.group(1), m.group(2).strip().strip("'\"")
            d = re.match(r"\w+://[^:/@]+:([^@]+)@", v)
            if d and len(d.group(1)) >= 6:
                out.setdefault(d.group(1), []).append("%s:%s(parola din DSN)" % (os.path.basename(f), k))
            # un URL fără acreditare (ex. `ANAF_TOKEN_URL`) e o adresă publică, nu un secret; cel cu acreditare e prins mai sus
            if _CHEIE_SECRETA.search(k) and len(v) >= 6 and not re.match(r"https?://[^@]*$", v):
                out.setdefault(v, []).append("%s:%s" % (os.path.basename(f), k))
    return out


@pytest.mark.skipif(not os.path.isdir(DIR_SECRETE), reason="~/.iconta absent: aici nu sunt secrete de comparat (limita declarată)")
def test_nicio_valoare_din_iconta_in_fisierele_urmarite():
    """Treapta 1. Pe codul de dinainte de 05.10.2026: parola lui contabil.b (fe_test.env) în `f1_helper.py` și parola bazei
    de producție (db.env) în `masuratori/p3/concurenta.json`. Mesajul NU tipărește valoarea, doar cheia și fișierul."""
    valori = _valori_secrete()
    assert len(valori) >= 5, "ANTI-VACUU: doar %d valori secrete citite din %s" % (len(valori), DIR_SECRETE)
    gasite = []
    for f in _urmarite():
        t = _text(f)
        if t is None:
            continue
        for v, chei in valori.items():
            if t.count(v):
                gasite.append("%s  <-  %s" % (f, ", ".join(chei)))
    assert not gasite, ("secrete REALE din ~/.iconta în fișiere urmărite de git (oglinda e publică) — scoate-le, citește-le "
                        "din mediu și ROTEȘTE-le:\n  " + "\n  ".join(gasite))


def test_tiparele_de_secrete_dau_exact_lista_inchisa():
    """Treapta 2. Pe codul de dinainte: `f1_helper.py` și `proba_f1_etape12.py` (`PAROLA = "…"`) și cele trei seed-uri
    (`CAB_PAROLA = "…"`) ar fi apărut aici ca intrări nedeclarate."""
    tipare = {n: re.compile(t) for n, t, _d in ss.TIPARE if n in _TIPARE}
    assert set(tipare) == set(_TIPARE), "scannerul nu mai are tiparele: %s" % (set(_TIPARE) - set(tipare))
    gasit = Counter()
    for f in _urmarite():
        t = _text(f)
        if t is None:
            continue
        for n, rx in tipare.items():
            k = len(rx.findall(t))
            if k:
                gasit[(f, n)] = k
    declarat = {k: v[0] for k, v in _PERMISE.items()}
    noi = sorted("%s [%s] x%d" % (f, n, k) for (f, n), k in gasit.items() if declarat.get((f, n)) != k)
    disparute = sorted("%s [%s] (declarat %d, găsit %d)" % (f, n, v, gasit.get((f, n), 0))
                       for (f, n), v in declarat.items() if gasit.get((f, n), 0) != v)
    assert not noi and not disparute, (
        "secrete posibile în fișiere urmărite, nedeclarate:\n  %s\nintrări din lista închisă care nu mai corespund:\n  %s\n"
        "O parolă de probă se citește din ~/.iconta (vezi frontend_test/cont_test.py), nu se scrie în cod."
        % ("\n  ".join(noi) or "—", "\n  ".join(disparute) or "—"))


def _coloane_parola_cu_valori(text):
    """[(linie, valoare)] din tabelele Markdown cu o coloană „parolă”/„password” care are o valoare (nu `—`/gol)."""
    out, col = [], None
    for i, ln in enumerate(text.split("\n"), 1):
        if not ln.lstrip().startswith("|"):
            col = None
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        antet = [i_ for i_, x in enumerate(c) if re.fullmatch(r"(?i)\**`?(parol[ăa]|password|pass)`?\**", x)]
        if antet:
            col = antet[0]
            continue
        if col is None or col >= len(c) or re.fullmatch(r"[-:\s]*", c[col]):
            continue
        if not re.match(r"[—–-]", c[col]):
            out.append((i, c[col][:3] + "…"))
    return out


def test_niciun_tabel_cu_coloana_parola_nu_are_valori():
    """Treapta 3. `date_test/C3_cabinete.md` avea 6 conturi cu parola în tabel (05.10.2026) — formă pe care nici tiparele,
    nici valorile din ~/.iconta nu o vedeau (conturile nu mai existau). Rețeta de recreare e tot o parolă publicată."""
    gasite = []
    for f in _urmarite():
        if not f.endswith((".md", ".csv", ".txt")):
            continue
        t = _text(f)
        if t is not None:
            gasite += ["%s:%d (%s)" % (f, i, v) for i, v in _coloane_parola_cu_valori(t)]
    assert not gasite, "tabele cu parole în fișiere urmărite: %s" % gasite


def test_CALIBRARE_tabelul_cu_parole():
    t = ("| email | parolă | rol |\n|---|---|---|\n| a@b.test | Cab!rol2026 | x |\n| c@d.test | — *(nu stă în depozit)* | y |\n"
         "\n| cod | descriere |\n|---|---|\n| P1 | parolă |\n")
    assert [v for _i, v in _coloane_parola_cu_valori(t)] == ["Cab…"]


def test_fiecare_intrare_permisa_are_motiv():
    scurte = sorted("%s [%s]" % k for k, (_n, motiv) in _PERMISE.items() if len(motiv) < 20)
    assert not scurte, "intrări fără motiv scris: %s" % scurte


def test_CALIBRARE_tiparul_de_parola_vede_formele_gasite_in_depozit():
    """Formele care au stat în git și pe care tiparul vechi (`\\bparola\\b\\s*[=:]`) NU le vedea, plus cele care nu trebuie
    numărate (fără ghilimele, URL)."""
    rx = re.compile([t for n, t, _d in ss.TIPARE if n == "PAROLA_ATRIBUITA"][0])
    vede = ['CAB_PAROLA = "nuOparolaBuna1"', 'PAROLA = "nuOparolaBuna1"', '{"parola": "nuOparolaBuna1"}',
            "password='nuOparolaBuna1'"]
    nu_vede = ["parola_schimbata = true", '"token_url": "https://logincert.anaf.ro/x"', 'parola = os.environ["X"]']
    assert [bool(rx.search(s)) for s in vede] == [True] * len(vede), [s for s in vede if not rx.search(s)]
    assert [bool(rx.search(s)) for s in nu_vede] == [False] * len(nu_vede), [s for s in nu_vede if rx.search(s)]


def test_configuratia_bazei_se_arata_fara_parola():
    """Producătorul artefactului scăpat scrie acum prin `db.config_fara_parola`. Pe forma veche (`str(cfg)`) parola ieșea."""
    from core import db
    for cfg in ({"url": "postgresql://u:nuOparola9@h:5432/d"}, {"host": "h", "user": "u", "password": "nuOparola9"},
                {"url": "host=h user=u password=nuOparola9 dbname=d"}):
        assert not re.search("nuOparola9", str(db.config_fara_parola(cfg))), cfg
    src = open(os.path.join(RAD, "scripts", "masoara_concurenta.py"), encoding="utf-8").read()
    assert re.search(r'"cfg":\s*str\(_db\.config_fara_parola\(cfg\)\)', src), "masoara_concurenta scrie din nou cfg brut"
