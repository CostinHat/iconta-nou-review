# -*- coding: utf-8 -*-
"""CE CONTINE PACHETUL DE AUDIT INAINTE DE A FI PUBLICAT — scanul de secrete.

De ce exista. Pachetul pleaca pe o oglinda PUBLICA. O cheie, o parola, un sir de conexiune sau o
linie de date reale ajunse acolo nu se mai pot retrage: GitHub le indexeaza, iar stergerea ulterioara
nu sterge istoria clonata de altii. Deci intrebarea nu e "cred ca e curat", ci "ce anume am cautat,
si ce am gasit".

Cum se citeste rezultatul. Scanul nu spune "curat". Spune, pentru FIECARE tipar cautat, cate
potriviri are si unde. Un tipar cu zero potriviri e o afirmatie verificabila; un tipar cu potriviri
e o decizie de luat, nu un esec automat — de-aia se tipareste fragmentul, redactat.

Orbirea LUI, declarata (METODA §22 — un instrument care nu-si spune modul de esec nu se poate crede):
  · cauta TIPARE, deci un secret care nu seamana cu niciunul dintre ele trece;
  · citeste TEXT, deci un secret dintr-un fisier binar (imagine, arhiva, pdf) nu se vede;
  · nu poate decide daca un CUI/CNP e al unei firme reale sau al uneia de test — le NUMARA si le
    arata, iar decizia ramane a omului;
  · calibrarea lui e in --autotest: isi pune singur, intr-un fisier temporar, cate o instanta din
    fiecare clasa si cere sa le gaseasca pe toate. Fara asta, "0 gasite" ar insemna deopotriva
    "n-are ce gasi" si "s-a stricat";
  · PROPRIA lui sursa se sare, si se spune ca s-a sarit. Mostrele de calibrare de mai jos SUNT
    secrete sintetice, scrise cu mana: numarate ca gasiri, ar pune un "AWS_ACCESS_KEY 1" intr-un
    raport publicat, unde se citeste gresit. Sarirea nu ascunde nimic — fisierul e in pachet,
    lizibil, iar randul "sarit" spune de ce.

A doua intrebare, la fel de importanta ca prima: CE E NOU. Un fisier al carui continut e deja in
depozitul public nu poate scurge nimic prin publicarea pachetului — e deja acolo. Deci fiecare fisier
se intreaba, prin AMPRENTA lui de obiect git, daca exista deja in arborele referintei publice.
Raspunsul imparte pachetul in "deja public" si "nou", iar atentia se duce unde trebuie.

Rulare:
    python audit/scan_secrete.py <director>                      # scaneaza
    python audit/scan_secrete.py <director> --fata-de public/main # + ce e nou fata de oglinda
    python audit/scan_secrete.py --autotest                      # se calibreaza pe sine, apoi iese
"""
import os
import re
import subprocess
import sys
import tempfile

# (nume, tipar, de ce conteaza)
TIPARE = [
    ("CHEIE_PRIVATA", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
     "cheie privata SSH/TLS in clar"),
    ("CHEIE_PUTTY", r"PuTTY-User-Key-File",
     "cheie privata in format PuTTY"),
    ("AWS_ACCESS_KEY", r"\bAKIA[0-9A-Z]{16}\b",
     "identificator de cheie AWS"),
    ("TOKEN_GITHUB", r"\bgh[pousr]_[A-Za-z0-9]{20,}",
     "token GitHub (acces la depozit)"),
    ("TOKEN_OPENAI", r"\bsk-[A-Za-z0-9]{20,}",
     "cheie de API in forma sk-"),
    ("TOKEN_SLACK", r"\bxox[baprs]-[A-Za-z0-9-]{10,}",
     "token Slack"),
    ("CHEIE_BREVO", r"\bxkeysib-[A-Za-z0-9]{10,}",
     "cheie API Brevo (trimiterea de email)"),
    ("JWT", r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
     "jeton JWT (sesiune sau acces SPV)"),
    ("SIR_CONEXIUNE_CU_PAROLA", r"\b(?:postgres(?:ql)?|mysql|mongodb|amqp|redis)://[^\s:/@]+:[^\s@]+@",
     "sir de conexiune cu parola in el"),
    ("SIR_CONEXIUNE", r"\b(?:postgres(?:ql)?|mysql|mongodb|amqp|redis)://",
     "sir de conexiune (chiar fara parola, spune unde e baza)"),
    ("PAROLA_ATRIBUITA", r"(?i)\b(?:password|passwd|parola|pwd|secret|api_?key|token)\b\s*[=:]\s*"
                         r"[\"'][^\"'\s]{6,}[\"']",
     "parola sau cheie scrisa langa numele ei"),
    ("PGPASSWORD", r"\bPGPASSWORD\s*=\s*\S+",
     "parola de PostgreSQL in mediu"),
    ("AUTORIZARE_HTTP", r"(?i)authorization\s*:\s*(?:bearer|basic)\s+\S{8,}",
     "antet de autorizare cu jeton in el"),
    ("IBAN", r"\bRO\d{2}[A-Z]{4}[A-Z0-9]{16}\b",
     "cont bancar"),
    ("CNP", r"(?<![\d.])[1-8]\d{12}(?![\d.])",
     "cod numeric personal (13 cifre) — al unei persoane reale sau de test"),
    ("EMAIL", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
     "adresa de email"),
    ("DESCARCARE_BAZA", r"(?im)^\s*(?:INSERT\s+INTO|COPY\s+\w+\s.*FROM\s+stdin)",
     "linie de descarcare de baza (continut de date)"),
]

BINARE = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".jar", ".ico", ".woff",
          ".woff2", ".ttf", ".xlsx", ".docx", ".p12", ".pfx")


def _redacteaza(s):
    """Arata cat sa se poata recunoaste, nu cat sa se poata folosi."""
    s = s.strip()
    if len(s) <= 12:
        return s
    return "%s…%s  (%d car.)" % (s[:8], s[-4:], len(s))


def scaneaza(radacina):
    gasite = {n: [] for n, _t, _d in TIPARE}
    sarite = []
    fisiere = 0
    for rad, dirs, nume in os.walk(radacina):
        dirs[:] = [d for d in dirs if d != ".git"]
        for n in sorted(nume):
            cale = os.path.join(rad, n)
            rel = os.path.relpath(cale, radacina).replace(os.sep, "/")
            if n.lower().endswith(BINARE):
                sarite.append((rel, "extensie binara"))
                continue
            if n == "SCAN_SECRETE.txt":
                sarite.append((rel, "e chiar IESIREA acestui scan — fragmentele redactate din ea "
                                    "s-ar renumara, si scanul s-ar masura pe sine"))
                continue
            if n == os.path.basename(__file__):
                sarite.append((rel, "e CHIAR instrumentul — mostrele lui de calibrare sunt "
                                    "secrete sintetice, prin constructie"))
                continue
            try:
                with open(cale, "r", encoding="utf-8", errors="strict") as f:
                    text = f.read()
            except (UnicodeDecodeError, OSError) as e:
                sarite.append((rel, "necitibil ca text: %s" % type(e).__name__))
                continue
            fisiere += 1
            for i, linie in enumerate(text.splitlines(), 1):
                for nume_t, tipar, _d in TIPARE:
                    for m in re.finditer(tipar, linie):
                        gasite[nume_t].append((rel, i, _redacteaza(m.group(0))))
    return gasite, sarite, fisiere


def amprente_din_ref(ref, depozit):
    """Amprentele de OBIECT ale tuturor fisierelor din arborele `ref`. Fara mapare de cai:
    un continut identic are aceeasi amprenta oriunde ar sta."""
    r = subprocess.run(["git", "-C", depozit, "ls-tree", "-r", ref],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    a = set()
    for linie in r.stdout.splitlines():
        parti = linie.split()
        if len(parti) >= 3:
            a.add(parti[2])
    return a


def fata_de(radacina, ref, depozit):
    """Imparte fisierele pachetului in DEJA PUBLIC / NOU, dupa amprenta de obiect git."""
    deja = amprente_din_ref(ref, depozit)
    if deja is None:
        return None
    noi, vechi = [], []
    for rad, dirs, nume in os.walk(radacina):
        dirs[:] = [d for d in dirs if d != ".git"]
        for n in sorted(nume):
            cale = os.path.join(rad, n)
            rel = os.path.relpath(cale, radacina).replace(os.sep, "/")
            h = subprocess.run(["git", "hash-object", cale], capture_output=True, text=True)
            amp = h.stdout.strip()
            (vechi if amp in deja else noi).append(rel)
    return vechi, noi


def autotest():
    """Calibrarea: fiecare clasa primeste o instanta sintetica; toate trebuie gasite."""
    mostre = {
        "CHEIE_PRIVATA": "-----BEGIN RSA PRIVATE KEY-----",
        "CHEIE_PUTTY": "PuTTY-User-Key-File-3: ssh-rsa",
        "AWS_ACCESS_KEY": "AKIAIOSFODNN7EXAMPLE",
        "TOKEN_GITHUB": "ghp_" + "A" * 36,
        "TOKEN_OPENAI": "sk-" + "B" * 32,
        "TOKEN_SLACK": "xoxb-1234567890-abcdefghij",
        "CHEIE_BREVO": "xkeysib-" + "c" * 20,
        "JWT": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dBjftJeZ4CVPmB92K27u",
        "SIR_CONEXIUNE_CU_PAROLA": "postgresql://utilizator:parolasecreta@gazda/baza",
        "SIR_CONEXIUNE": "redis://gazda:6379/0",
        "PAROLA_ATRIBUITA": "password = \"nuOparolaBuna\"",
        "PGPASSWORD": "PGPASSWORD=ceva-secret",
        "AUTORIZARE_HTTP": "Authorization: Bearer abcdefghijklmnop",
        "IBAN": "RO49AAAA1B31007593840000",
        "CNP": "1960101410011",
        "EMAIL": "cineva@exemplu.ro",
        "DESCARCARE_BAZA": "INSERT INTO facturi VALUES (1, 'x');",
    }
    lipsa = [n for n, _t, _d in TIPARE if n not in mostre]
    if lipsa:
        print("AUTOTEST ESUAT: tipare fara mostra de calibrare: %s" % ", ".join(lipsa))
        return 1
    d = tempfile.mkdtemp(prefix="calibrare_scan_")
    cale = os.path.join(d, "mostre.txt")
    with open(cale, "w", encoding="utf-8") as f:
        for n in mostre:
            f.write("%s\n" % mostre[n])
    gasite, _sarite, _f = scaneaza(d)
    ratate = [n for n, _t, _d in TIPARE if not gasite[n]]
    os.remove(cale)
    os.rmdir(d)
    if ratate:
        print("AUTOTEST ESUAT — tipare care nu si-au gasit propria mostra: %s" % ", ".join(ratate))
        return 1
    print("AUTOTEST TRECUT: toate cele %d de tipare isi gasesc propria mostra." % len(TIPARE))
    print("  (deci un «0 gasite» de mai jos inseamna «n-are ce gasi», nu «s-a stricat»)")
    return 0


def main():
    if "--autotest" in sys.argv:
        return autotest()
    if len(sys.argv) < 2:
        print("folosire: scan_secrete.py <director> | --autotest")
        return 2
    radacina = sys.argv[1]
    print("=" * 100)
    print("SCAN DE SECRETE — %s" % os.path.abspath(radacina))
    print("=" * 100)
    print()
    if autotest():
        return 1
    print()
    gasite, sarite, fisiere = scaneaza(radacina)
    print("Fisiere de text citite: %d · sarite (binare/necitibile): %d" % (fisiere, len(sarite)))
    if sarite:
        for rel, motiv in sarite:
            print("    sarit: %-60s %s" % (rel, motiv))
    print()
    print("-" * 100)
    print("CE S-A CAUTAT, SI CE S-A GASIT")
    print("-" * 100)
    total = 0
    for nume_t, _tipar, descriere in TIPARE:
        lovituri = gasite[nume_t]
        total += len(lovituri)
        print("  %-24s %4d   %s" % (nume_t, len(lovituri), descriere))
        locuri = {}
        for rel, linie, frag in lovituri:
            locuri.setdefault(rel, []).append((linie, frag))
        for rel in sorted(locuri):
            v = locuri[rel]
            print("        %s  (%d)" % (rel, len(v)))
            for linie, frag in v[:5]:
                print("            :%-6d %s" % (linie, frag))
            if len(v) > 5:
                print("            … si inca %d in acelasi fisier" % (len(v) - 5))
    print()
    print("TOTAL potriviri: %d" % total)

    if "--fata-de" in sys.argv:
        ref = sys.argv[sys.argv.index("--fata-de") + 1]
        depozit = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        r = fata_de(radacina, ref, depozit)
        print()
        print("-" * 100)
        print("CE E NOU FATA DE `%s` — dupa amprenta de obiect git, nu dupa nume" % ref)
        print("-" * 100)
        if r is None:
            print("  NU S-A PUTUT CITI referinta `%s` — clasificarea NU s-a facut." % ref)
            print("  (se scrie asa, nu se tace: o verificare nefacuta nu e o verificare trecuta)")
            return 1
        vechi, noi = r
        print("  DEJA IN DEPOZITUL PUBLIC, cu acelasi continut: %d fisiere" % len(vechi))
        for f in vechi:
            print("      %s" % f)
        print()
        print("  CONTINUT NOU, care se publica prin pachet: %d fisiere" % len(noi))
        for f in noi:
            print("      %s" % f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
