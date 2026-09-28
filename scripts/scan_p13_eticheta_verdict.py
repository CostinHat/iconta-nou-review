# -*- coding: utf-8 -*-
"""Perimetru P13 (interdictiile 27 verdict-ca-fraza si 31 eticheta-nederivata-din-stare), derivat MECANIC.

31: o eticheta ALEASA de cine randeaza (JS), nu derivata din stare. Semnale mecanice:
  (a) fallback pe token brut: `X[ent.status] || ent.status` / `... .stare] || ...` -> daca lipseste eticheta,
      contabilului i se arata TOKEN-ul de stare (ex. "de_recunoscut"), sau, mai rau, o stare fara eticheta
      trece tacut;
  (b) harta de stare (indexata prin `.status`/`.stare`) confruntata cu nomenclatorul Python al starilor:
      stari FARA eticheta + etichete FANTOMA (stare inexistenta in nomenclator).
  NU sunt 31: hartile care eticheteaza NUME DE CAMP fixe (coloane), nu stari de entitate.

27: verdict stocat/afisat ca fraza. Backendul Python e acoperit de verificator VERDICT_COLAPSAT (poarta verde).
  Aici raportam reziduul: fallback-uri de stare in JS care afiseaza token brut (acelasi semnal ca 31a) tin si de 27
  cand ce se afiseaza e un VERDICT (stare SPV: trimisa/respinsa/blocata), nu doar o eticheta de status.

P13b (28.09.2026 — perimetru LARGIT dupa reclasificarea arhitectului): sectiunea `scaneaza_verdict_pozitiv`
deriva mecanic TOATE locurile din `static/js` unde un text-verdict POZITIV (la zi / complet / fara probleme /
in regula) e ales pe baza unor CONTOARE sau a unui FALLBACK, nu dintr-o stare pozitiva EXPLICITA. Instanta
declansatoare: `semaforCard` (semafor.js) arata "Toate firmele la zi" verde cand rosu=galben=0 SAU cand
sumarul lipseste — ignorand `sumar.gri` (produs de uc_control_fiscal) si tratand absenta ca verde.
"""
import os, re, subprocess
RAD = "/home/costin/iconta_nou"
JS = os.path.join(RAD, "static/js")

# ─────────────────────────────────────────────────────────────────────────────
# P13b — verdict POZITIV ales din contoare/fallback (nu dintr-o stare verde explicita)
# ─────────────────────────────────────────────────────────────────────────────
# Fraze de verdict POZITIV — clasa fiscala „totul e bine" unde exista o a treia stare (gri) ascunsa.
# TIGHT intentionat: NU includem „complet" (dominat de imperativul „Completeaza" / „incomplet" /
# label-uri ca „istoric complet") — verdictul de profil-complet e alt subsistem (derivat din date
# LOCALE complete, fara a treia stare backend); daca ar aparea pe o garda de golire, sub-scanul (2)
# il prinde oricum prin fraza „la zi"/„fara probleme". Vezi calibrarea din test_verde_derivat.py.
POZ_LEXIC = re.compile(r'(la zi|fără probleme|fara probleme|în regulă|in regula)', re.I)
# Gardul CORECT: o stare pozitiva EXPLICITA — egalitate cu un token verde, sau un camp/cheie `verde`.
POZ_STARE = re.compile(r'===?\s*["\'](verde|ok|conform|valid|la_zi)["\']', re.I)
POZ_CAMP = re.compile(r'(?<![-\w])verde(?![-\w])')
# Garda de GOLIRE/ZERO/FALLBACK: exact tiparul „pozitivul apare din absenta/zero", nu dintr-o stare.
GOL_ZERO = re.compile(r'(!\s*[\w.]+|===?\s*0|<\s*1|\|\|)')
# Negatia frazei (ca sa nu numaram „NU e la zi" drept verdict pozitiv).
NEG_APROAPE = re.compile(r'(nu\s+e|not|!==|!=|\bfără\b|\bfara\b)', re.I)


def _statement_start(src, pos):
    """Offsetul de inceput al instructiunii care contine `pos`: ultima granita
    (`;`/`{`/`}`/`=>`/`return`) dinainte. Captureaza ternare/apeluri multi-linie
    (conditia `X ? ...` poate sta cu cateva randuri mai sus decat fraza)."""
    return max(src.rfind(";", 0, pos), src.rfind("{", 0, pos), src.rfind("}", 0, pos),
               src.rfind("=>", 0, pos), src.rfind("return", 0, pos)) + 1


def _apel_balansat(src, start):
    """Textul apelului `f(...)` de la prima paranteza dupa `start` pana la inchiderea ei (balansat)."""
    i = src.find("(", start)
    if i < 0:
        return ""
    d, j = 0, i
    while j < len(src):
        if src[j] == "(":
            d += 1
        elif src[j] == ")":
            d -= 1
            if d == 0:
                return src[i:j + 1]
        j += 1
    return src[i:]


def scaneaza_verdict_pozitiv(js_root=JS):
    """Deriva (bad, good): locurile din static/js unde un TEXT-VERDICT pozitiv e ales din contoare/fallback.
    Doua sub-scanuri, ambele cu clasificare GOOD daca exista o stare verde EXPLICITA in context:
      (1) apeluri `semaforCard(...)` care primesc o fraza pozitiva in `mesajOk` — BAD daca apelul NU
          trece si un semnal `verde` explicit (post-fix apelul trece `s.verde` -> GOOD).
      (2) fraza-verdict pozitiva intr-un literal, guvernata de o garda de GOLIRE/ZERO/FALLBACK
          (`!x.length`, `=== 0`, `|| "..."`) fara stare verde explicita -> BAD.
    Fiecare element: (cale_relativa, nr_linie, fragment)."""
    bad, good = [], []
    for root, _, fs in os.walk(js_root):
        for f in sorted(fs):
            if not f.endswith(".js"):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, RAD)
            src = open(p, encoding="utf-8", errors="replace").read()

            # ── sub-scan (1): apelurile semaforCard / _semaforCard (alias) ──
            for m in re.finditer(r'\b_?semaforCard\s*\(', src):
                apel = _apel_balansat(src, m.start())
                pm = POZ_LEXIC.search(apel)
                if not pm:
                    continue  # mesajOk gol sau ne-pozitiv (ex. cabinet.js:458 cu "") -> nu e verdict pozitiv
                lineno = src.count("\n", 0, src.find("(", m.start()) + pm.start()) + 1
                are_verde = bool(POZ_CAMP.search(apel))
                frag = "semaforCard(...) mesajOk pozitiv" + (" + verde" if are_verde else " FARA verde")
                (good if are_verde else bad).append((rel, lineno, frag))

            # ── sub-scan (2): fraze-verdict in ternare/fallback ──
            for mm in POZ_LEXIC.finditer(src):
                ls = src.rfind("\n", 0, mm.start()) + 1
                le = src.find("\n", mm.start())
                le = le if le != -1 else len(src)
                linie = src[ls:le]
                strip = linie.strip()
                if strip.startswith(("//", "*", "/*")):
                    continue
                if '"' not in linie and "'" not in linie and "`" not in linie:
                    continue
                inainte = src[max(0, mm.start() - 10):mm.start()]
                if NEG_APROAPE.search(inainte):
                    continue  # „NU e la zi" etc. — nu e verdict pozitiv
                # GARDA GUVERNANTA: textul instructiunii DINAINTEA frazei (conditia care alege pozitivul).
                b = _statement_start(src, mm.start())
                coada = src[b:mm.start()][-140:]
                lineno = src.count("\n", 0, mm.start()) + 1
                rec = (rel, lineno, strip[:90])
                # POZITIV explicit (verde / ok / valid / conform, ca stare sau flag ternar) -> GOOD
                pozitiv = POZ_STARE.search(coada) or re.search(r'(?<![-\w])(ok|verde|valid|conform)(?![-\w])', coada)
                if pozitiv:
                    if rec not in good:
                        good.append(rec)
                    continue
                # BAD doar cand garda e de GOLIRE/ZERO/FALLBACK (pozitivul iese din absenta), fara stare verde
                if GOL_ZERO.search(coada) and rec not in bad:
                    bad.append(rec)
    return bad, good


def _print_verdict_pozitiv():
    print("=== P13b — verdict POZITIV ales din contoare/fallback (nu din stare verde explicita) ===")
    bad, good = scaneaza_verdict_pozitiv()
    print("  BAD (verdict pozitiv fara gardă pe verde explicit) — trebuie 0:")
    for f, i, s in bad:
        print("    %s:%d  %s" % (f, i, s))
    print("  TOTAL BAD:", len(bad))
    print("  GOOD (verdict pozitiv derivat corect din stare verde explicita) — calibrare pozitiva:")
    for f, i, s in good:
        print("    %s:%d  %s" % (f, i, s))
    print("  TOTAL GOOD:", len(good))


# --- 31a: fallback pe token brut de stare in JS ---
def _print_31a():
    print("\n=== 31a — fallback pe TOKEN BRUT de stare (renderer arata tokenul daca lipseste eticheta) ===")
    rx = re.compile(r'\[\s*[A-Za-z_][\w.]*\.(status|stare)\s*\]\s*\|\|')
    hits = []
    for root, _, fs in os.walk(JS):
        for f in fs:
            if not f.endswith(".js"):
                continue
            p = os.path.join(root, f)
            for i, l in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                if rx.search(l):
                    hits.append((os.path.relpath(p, RAD), i, l.strip()[:90]))
    for f, i, s in hits:
        print("  %s:%d  %s" % (f, i, s))
    print("  TOTAL fallback-uri token-brut:", len(hits))


def _print_31b():
    print("\n=== 31b — STATUS_ETICHETA (facturi_ecran.js) vs nomenclator_status_factura.STARI ===")
    import sys
    sys.path.insert(0, RAD)
    from core import nomenclator_status_factura as nsf
    stari = set(nsf.STARI)
    fe = open(os.path.join(JS, "ecrane/facturi_ecran.js"), encoding="utf-8").read()
    m = re.search(r'STATUS_ETICHETA\s*=\s*\{([^}]*)\}', fe)
    etich = set(re.findall(r'(\w+)\s*:', m.group(1))) if m else set()
    print("  nomenclator STARI (%d): %s" % (len(stari), sorted(stari)))
    print("  STATUS_ETICHETA (%d): %s" % (len(etich), sorted(etich)))
    print("  STARI FARA eticheta (contabilul vede tokenul):", sorted(stari - etich))
    print("  ETICHETE FANTOMA (eticheta pt stare inexistenta):", sorted(etich - stari))
    print("  (nota: storno/contabilizata sunt derivate in cod, nu stari de nomenclator)")


def _print_27():
    print("\n=== 27 — backend Python: VERDICT_COLAPSAT (verificator) ===")
    r = subprocess.run(["./venv/bin/python", "verificator_conformitate.py"], cwd=RAD, capture_output=True, text=True)
    vc = [l for l in r.stdout.split("\n") if "verdict" in l.lower() or "TOTAL" in l]
    print("  verificator ruleaza; VERDICT_COLAPSAT e activ. TOTAL:", [l.strip() for l in vc if "TOTAL:" in l][:1])


if __name__ == "__main__":
    _print_verdict_pozitiv()
    _print_31a()
    _print_31b()
    _print_27()
