# -*- coding: utf-8 -*-
"""core/scan_afirmatii.py — cate AFIRMATII despre datele firmei sunt inca netipate? (P8, 21.08.2026)

UNITATEA. Un dictionar cu o cheie de REVENDICARE (`mesaj`, `motiv`, `cauza`, `avertisment`,
`constatare`, `semnal`, `explicatie`) care ajunge la utilizator. Daca poarta si `fel`, e o afirmatie
TIPATA (`core/afirmatii.py`); daca nu, e proza intr-un dictionar.

PRIMA FORMA A ACESTUI SCAN cauta LISTE numite `constatari`/`probleme`/`verdicte`. A gasit 24 de
locuri pe toata aplicatia si era ORB pe `control_fiscal_api` - producatorul de referinta, singurul
care chiar produce afirmatii tipate. Cauta forma pe care mi-o imaginam, nu forma pe care o are codul.
Vocabularul de mai jos e MASURAT (numarul de aparitii al fiecarei chei: mesaj 126, motiv 98, cauza 26,
explicatie 14, avertisment 5, semnal 4), nu ales.

CELE PATRU CLASE, iesite din calibrare pe doua esantioane de 30 si de 20 (masurat 21.08):
  A. VERDICT despre datele firmei - 74. „D390 nu se depune", „solduri creditoare la trezorerie".
  C. VALIDARE DE RAND la import   - 46. „randul 7: CNP invalid".
  D. VALIDARE DE FORMULAR         - 41. „campul asta e gresit". NU spune nimic despre firma.
  B. REZULTAT DE OPERATIE         - 25. „salvat", „nu se poate sterge". Poarta `ok`.

GRANITA (Costin, 21.08): A si C intra in decizie; B si D nu. C a intrat prin decizie explicita -
„aceeasi decizie, acelasi tip" - desi afirma despre FISIERUL incarcat, nu despre datele deja
inregistrate. Granita e a lui; scanul o aplica, nu o judeca.

CE NU POATE SPUNE. Clasificarea e pe NUME (chei + numele functiei), deci e un proxy. O lista numita
`mesaje` poate purta verdicte, iar `verifica_randuri` poate face altceva. De-aia clasele se
raporteaza SEPARAT si oricine poate contesta o incadrare uitandu-se la ea - nu se ascunde nimic
intr-un total.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REVENDICARE = {"mesaj", "motiv", "cauza", "cauză", "avertisment", "constatare", "semnal",
               "explicatie", "explicație", "atentie", "atenție", "nereguli", "blocaj"}

TIPATE = {"fel"}

# Un REMEDIU nu e o afirmatie - e ce se poate FACE in privinta ei. Poarta si el `fel`, dar dintr-un
# alt nomenclator ("investigatie", nu "necunoastere"), si o cheie `cauza` care nimereste in
# vocabularul de revendicare. Prima forma a scanului le numara ca afirmatii TIPATE: 23 din cele 27
# „tipate" erau remedii, deci gardul anti-vacuu trecea numarand altceva decat credea. Afirmatii
# tipate reale, la instalare: 4. Discriminatorul e `actiune` - un remediu spune ce sa faci.
REMEDIU = {"actiune"}

# Chei care spun ca dictionarul e o validare de FORMULAR (care camp e gresit), nu o afirmatie despre
# datele firmei. Iesite din calibrarea clasei A: 41 din 186 erau asta.
FORMULAR = {"camp", "erori_campuri", "campuri"}

# Numele de functie care indica IMPORT (clasa C) si OPERATIE (clasa B).
IMPORT_FN = ("verifica_randuri", "extrage", "importa", "potriveste", "extrage_operatiuni",
             "incarca", "preview", "parseaza", "citeste_", "valideaza_rand")
OPERATIE_FN = ("salveaza", "creeaza", "sterge", "marcheaza", "seteaza", "adauga", "modifica",
               "actualizeaza", "trimite", "genereaza_", "aproba", "respinge", "anuleaza")

# Functii care vorbesc despre UTILIZATORI sau despre disponibilitatea unei unelte, nu despre datele
# firmei. Lista e DECLARATA, ca oricine sa poata contesta o intrare.
FARA_FIRMA_FN = ("jurnal", "calitate", "analiza_ai", "_eroare_campuri")

# `registru_` scos 22.08.2026: registrul de EXCEPTII se numara pe SINE, fiindca intrarile lui poarta
# cheia `motiv` (motivul exceptarii). Circular - registrul care declara ce nu e afirmatie ar aparea ca
# datorie de sapte afirmatii. Un registru nu PRODUCE afirmatii, le DESCRIE.
IGNORA_FISIER = ("test_", "scan_", "verificator_conformitate", "migrare_", "conftest", "registru_")

# Module de infrastructura: nu vorbesc despre datele unei firme, oricat de sugestive le-ar fi cheile.
FARA_FIRMA = ("core/auth_api.py", "core/email_util.py", "core/notificari.py", "core/cron.py",
              "core/alerta_acces.py", "core/audit_retentie.py", "core/tenant_provisioning.py",
              "core/db.py", "core/pdf_fonturi.py", "core/backup_api.py")


def clasa(fisier, functie, chei):
    """A_verdict | C_import | B_operatie | D_formular — vezi docstringul."""
    ch = set(chei.split(",")) if isinstance(chei, str) else set(chei)
    if (ch & FORMULAR) or functie in FARA_FIRMA_FN:
        return "D_formular"
    if "rand" in ch or any(k in functie for k in IMPORT_FN) or "_import_" in fisier:
        return "C_import"
    if "ok" in ch or any(functie.startswith(k) for k in OPERATIE_FN):
        return "B_operatie"
    return "A_verdict"


def _fisiere():
    for rad, dirs, fis in os.walk(RAD):
        dirs[:] = [d for d in dirs if d not in ("venv", ".git", "_arhiva", "node_modules",
                                                "frontend_test", "__pycache__")]
        for f in fis:
            if f.endswith(".py") and not f.startswith(IGNORA_FISIER):
                p = os.path.join(rad, f)
                rel = os.path.relpath(p, RAD).replace(os.sep, "/")
                if rel not in FARA_FIRMA:
                    yield p, rel


def _nomenclatoare(arb):
    """Liniile dictionarelor atribuite unei CONSTANTE de modul (NUME_MARE = {...}).

    Alea sunt harti de nomenclator, nu afirmatii: `intrastat.NIVEL_STATUS` e
    `{"depasit": AVERTISMENT, "atentie": AVERTISMENT}` - o mapare status->nivel, prinsa DOAR fiindca
    o CHEIE se cheama `atentie`. Cheia nu face afirmatia; textul o face.

    Excluderea e TINTITA si masurata: la instalare scoate EXACT UN sit din tot inventarul. O prima
    incercare, mai larga („valoarea cheii de revendicare trebuie sa produca text"), scotea SAISPREZECE
    din treizeci si doua - jumatate din datorie, printre care o constatare adevarata din
    `audit_preluare`. Aia nu ascutea instrumentul, il orbea. `test_afirmatii_tipate` numara ce scoate
    excluderea asta si pica daca numarul creste."""
    return {n.value.lineno for n in arb.body
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict)
            and any(isinstance(t, ast.Name) and t.id.isupper() for t in n.targets)}


def inventar():
    """[(fisier, functie, linie, stare, clasa, chei)] — stare in `tipata` | `netipata`."""
    out = []
    for p, rel in sorted(_fisiere(), key=lambda x: x[1]):
        try:
            arb = ast.parse(io.open(p, encoding="utf-8").read())
        except SyntaxError:
            continue
        fn_de_linie = {}
        for fn in ast.walk(arb):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for ln in range(fn.lineno, (fn.end_lineno or fn.lineno) + 1):
                    fn_de_linie.setdefault(ln, fn.name)
        harti = _nomenclatoare(arb)
        for n in ast.walk(arb):
            if not isinstance(n, ast.Dict):
                continue
            ch = {k.value for k in n.keys
                  if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            if not (ch & REVENDICARE) or (ch & REMEDIU) or n.lineno in harti:
                continue
            fn = fn_de_linie.get(n.lineno, "<modul>")
            out.append((rel, fn, n.lineno, "tipata" if (ch & TIPATE) else "netipata",
                        clasa(rel, fn, ch), ",".join(sorted(ch))[:70]))
    return out


def netipate_in_scop():
    """Doar clasele A si C — cele intrate in decizie. Astea sunt numarate de clichet."""
    return [x for x in inventar() if x[3] == "netipata" and x[4] in ("A_verdict", "C_import")]


if __name__ == "__main__":
    from collections import Counter
    inv = inventar()
    print("afirmatii gasite: %d | tipate: %d" % (len(inv), sum(1 for x in inv if x[3] == "tipata")))
    print("netipate, pe clasa: %s" % dict(Counter(x[4] for x in inv if x[3] == "netipata")))
    scop = netipate_in_scop()
    print("\nIN SCOP (A+C): %d, in %d fisiere" % (scop.__len__(), len({x[0] for x in scop})))
    for f, n in Counter(x[0] for x in scop).most_common():
        print("  %-44s %d" % (f, n))
