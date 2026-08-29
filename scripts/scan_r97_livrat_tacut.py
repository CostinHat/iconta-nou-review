# -*- coding: utf-8 -*-
"""CÂT DE MARE E CLASA „RUTA LIVREAZĂ, ECRANUL TACE" — măsurarea lui R97, 29.08.2026.

DE CE EXISTĂ. `scripts/scan_1c_verificabil.py` își declară limita în cap: *măsoară ce TRIMITE ruta,
nu ce RANDEAZĂ ecranul*. Sub limita aia s-au găsit **două** defecte reale — registrul-jurnal
(`nr_curent`, `document`, `total_debit`/`total_credit` derivate și neafișate) și netul de pe fluturaș
(toate cele 7 componente trimise, niciuna afișată). Decizia lui Costin, 29.08: **nu sunt două
poziții, sunt o clasă**, iar *„nu e caz izolat până nu demonstrezi că e"*. Condiția de deblocare a lui
R97 cere, în ordinea asta: **întâi instrumentul care confruntă trimis↔randat, pe fiecare pereche**,
abia apoi reparațiile. Ăsta e instrumentul.

PERECHEA e declarată de ECRAN, nu ghicită: fiecare `api.get(...)` din `static/js/` numește ruta pe
care o consumă. Se ia URL-ul **așa cum e scris acolo**, i se înlocuiesc interpolările cu valori reale,
se cheamă **VIU**, și se citesc cheile răspunsului — la toate adâncimile, fiindcă amândouă instanțele
cunoscute sunt chei **imbricate** (`note[].nr_curent`, `stat[].deducere`).

DIRECȚIA DE EROARE, ALEASĂ DELIBERAT. „Randat" se caută pe NUME, iar un nume se poate potrivi din
întâmplare — deci **randat e supra-numărat**, și prin urmare **clasa e plafon INFERIOR**. Asta e
direcția care contează: o cifră care spune *„cel puțin atâtea"* poate dovedi că nu e caz izolat; una
care supra-numără n-ar putea dovedi nimic. Se raportează **două** praguri:

  - **TĂCUT SIGUR** — numele nu apare **nicăieri** în tot `static/js/`. Câmpul nu e folosit de nimeni,
    în niciun fel. Astea sunt instanțele **certe** ale clasei;
  - **TĂCUT ÎN ECRANUL CARE-L CERE** — numele nu apare, ca acces de proprietate sau ca literal, în
    **fișierul care face apelul**, dar apare altundeva în `static/js/`. Astea sunt **candidați**: ori
    randarea e într-un ajutor comun, ori câmpul chiar e ignorat exact acolo unde e cerut.

CE NU VEDE, declarat:
  - **apelurile cu interpolări pe care nu le pot substitui** (`${vreoVariabila}`) — se numără separat,
    ca domeniu neatins, NU ca fiind în regulă;
  - **un câmp folosit doar în LOGICĂ, nu afișat** (`if (n.status === ...)`) trece drept „randat".
    Încă o dată: supra-numără randatul, deci subestimează clasa;
  - **doar GET.** Clasa e despre ce livrează o citire. Că un GET nu scrie e măsurat separat
    (interdicția 6: 0 rute GET care scriu);
  - **răspunsurile care nu sunt JSON** (PDF-uri) — se numără separat: acolo nu există câmp de tăcut,
    iar asta e în sine o observație despre artefact.

    set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a
    ./venv/bin/python scripts/scan_r97_livrat_tacut.py [--json]
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db  # noqa: E402

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js")
BAZA = "http://127.0.0.1:8010"
AN, LUNA, TRIM = 2026, 8, 3

# Firma pe care se cheamă rutele: cea mai bogată din portofoliu (19 note, salariați, facturi, casă).
# O firmă goală ar întoarce liste vide, iar un câmp care apare doar când sunt date n-ar fi văzut —
# adică instrumentul ar rata exact clasa pe care o caută.
SCHEMA_TINTA = "tenant_013"

RE_GET = re.compile(r"api\.get\(\s*[`\"']([^`\"']+)[`\"']")

# Interpolările pe care le pot înlocui cu o valoare reală. Restul opresc apelul, declarat.
SUBST = {
    "an": str(AN), "luna": str(LUNA), "trim": str(TRIM),
    "t.id": None, "tenantId": None, "tenant_id": None, "tid": None, "S.tenant_id": None,
    "f.id": None, "firma.id": None, "t.tenant_id": None,
}

# Nume prea generice ca să spună ceva la o căutare pe nume: apar oriunde. Se numără separat.
PREA_GENERICE = {"id", "nume", "data", "tip", "stare", "total", "an", "luna", "cod", "text",
                 "valoare", "suma", "cont", "linii", "ok", "url", "fel", "motiv", "titlu"}


# Martorii: un GET nu are voie să scrie (interdicția 6, măsurată: 0 rute GET care scriu din 172).
# Dar „nu are voie" nu e „nu scrie" — sonda o dovedește la fiecare rulare. Printre rutele chemate e
# și `/tenants/{id}/scoatere`, previzualizarea celui mai distructiv act al aplicației.
MARTORI = ("public.tenants", "public.users", "public.audit_log", "public.declaratii_coada",
           "{s}.inregistrari", "{s}.inregistrari_linii", "{s}.facturi", "{s}.salariati",
           "{s}.declaratii_depuse")


def _snapshot(schema):
    s = {}
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            for t in MARTORI:
                nume = t.format(s=schema)
                try:
                    cur.execute("SELECT COUNT(*) FROM %s" % nume)
                    s[nume] = cur.fetchone()[0]
                except Exception:
                    conn.rollback()
    return s


def _token(email):
    from core import auth_api
    import psycopg2.extras as E
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT * FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
    assert u, "user %r inexistent" % email
    return auth_api.emite_token(dict(u))


def _get(cale, tok, timeout=90):
    cerere = urllib.request.Request(BAZA + cale, None, {"Authorization": "Bearer " + tok})
    try:
        r = urllib.request.urlopen(cerere, timeout=timeout)
        brut = r.read()
        ct = r.headers.get("Content-Type", "")
        if "json" not in ct:
            return None, {"fel": "ne-JSON", "detaliu": ct.split(";")[0] or "?"}
        return json.loads(brut.decode("utf-8", "replace")), None
    except urllib.error.HTTPError as e:
        return None, {"fel": "HTTP %d" % e.code,
                      "detaliu": e.read().decode(errors="replace")[:90]}
    except Exception as e:
        return None, {"fel": "eroare", "detaliu": str(e)[:90]}


def chei_recursiv(x, adancime=0, prefix=""):
    """{cale_cheie: nume} pentru TOATE cheile, la orice adâncime. Instanțele cunoscute sunt imbricate."""
    out = {}
    if adancime > 5:
        return out
    if isinstance(x, dict):
        for k, v in x.items():
            cale = (prefix + "." + k) if prefix else k
            out[cale] = k
            out.update(chei_recursiv(v, adancime + 1, cale))
    elif isinstance(x, list):
        for e in x[:8]:
            out.update(chei_recursiv(e, adancime + 1, prefix + "[]"))
    return out


def apeluri_get():
    """[(fisier_rel, linia, url_scris)] pentru fiecare `api.get` din static/js."""
    out = []
    for rad, _, fis in os.walk(JS):
        for f in sorted(fis):
            if not f.endswith(".js"):
                continue
            cale = os.path.join(rad, f)
            src = open(cale, encoding="utf-8").read()
            rel = os.path.relpath(cale, RAD).replace(os.sep, "/")
            for m in RE_GET.finditer(src):
                out.append((rel, src[:m.start()].count("\n") + 1, m.group(1)))
    return out


def substituie(url, tid):
    """(url_concret, None) sau (None, motiv) dacă rămâne o interpolare nesubstituibilă."""
    def _rep(m):
        expr = m.group(1).strip()
        if expr in SUBST:
            return SUBST[expr] if SUBST[expr] is not None else str(tid)
        return "\x00" + expr + "\x00"
    u = re.sub(r"\$\{([^}]*)\}", _rep, url)
    if "\x00" in u:
        return None, "interpolare nesubstituibilă: ${%s}" % u.split("\x00")[1]
    return u, None


def incarca_js():
    """(text_pe_fisier, text_tot) — sursa JS, o singură dată."""
    pe_fisier, tot = {}, []
    for rad, _, fis in os.walk(JS):
        for f in fis:
            if not f.endswith(".js"):
                continue
            cale = os.path.join(rad, f)
            src = open(cale, encoding="utf-8").read()
            pe_fisier[os.path.relpath(cale, RAD).replace(os.sep, "/")] = src
            tot.append(src)
    return pe_fisier, "\n".join(tot)


def apare_undeva(nume, tot):
    return re.search(r"\b%s\b" % re.escape(nume), tot) is not None


RE_GENERIC = r"Object\.(?:keys|entries|values)\(\s*%s\b"
RE_FORIN = r"for\s*\(\s*(?:const|let|var)?\s*\w+\s+in\s+(?:\w+\.)*%s\b"


def randat_generic(parinte, src):
    """Containerul `parinte` e parcurs GENERIC în `src`? Atunci copiii lui ajung pe ecran fără să
    fie numiți, iar o căutare pe NUME nu-i vede.

    DE CE EXISTĂ, și e o reparație a instrumentului, nu o rafinare: prima formă a raportat 66 de
    câmpuri tăcute, printre care `randuri_de_sters.audit_log` (ecranul de scoatere) și cele 9
    `marcaje.*` (ecranul de contracte). **Citite la sursă, amândouă SE AFIȘEAZĂ** — prin
    `Object.keys(rd)` și `Object.entries(marcaje)`. Deci greșeala nu era o nuanță: instrumentul
    supra-număra clasa, adică **exact invers decât direcția pe care o declarasem** („randat e
    supra-numărat, deci clasa e plafon inferior").

    Se rezolvă și un nivel de alias — `const rd = p.randuri_de_sters` urmat de `Object.keys(rd)` —
    fiindcă ăla e chiar cazul real. **Ce nu rezolvă:** alias pe două niveluri, parcurgere printr-o
    funcție ajutătoare, sau parcurgere într-un ALT fișier. Acolo rămâne supra-numărare, declarată.
    """
    import re as _re
    p = _re.escape(parinte)
    if _re.search(RE_GENERIC % p, src) or _re.search(RE_FORIN % p, src):
        return True
    for m in _re.finditer(r"(?:const|let|var)\s+(\w+)\s*=\s*[^;\n]*\b%s\b" % p, src):
        alias = _re.escape(m.group(1))
        if _re.search(RE_GENERIC % alias, src) or _re.search(RE_FORIN % alias, src):
            return True
    return False


def apare_in_ecran(nume, src):
    """Acces de proprietate sau literal de cheie, în fișierul care face apelul."""
    n = re.escape(nume)
    return (re.search(r"\.%s\b" % n, src) is not None
            or re.search(r"[\"'`]%s[\"'`]" % n, src) is not None
            or re.search(r"\{[^{}]*\b%s\b[^{}]*\}" % n, src) is not None)


def ruleaza():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT t.id, (SELECT u.email FROM public.users u "
                        " WHERE u.accounting_firm_id=t.accounting_firm_id AND u.rol='admin_firma' "
                        " ORDER BY u.id LIMIT 1) FROM public.tenants t WHERE t.schema_name=%s",
                        (SCHEMA_TINTA,))
            r = cur.fetchone()
    assert r and r[1], "firma țintă %s n-are user de cabinet" % SCHEMA_TINTA
    tid, email = r
    tok = _token(email)

    pe_fisier, tot_js = incarca_js()
    apeluri = apeluri_get()
    assert len(apeluri) > 100, "ANTI-VACUU: doar %d apeluri `api.get` găsite" % len(apeluri)
    assert len(pe_fisier) > 20, "ANTI-VACUU: doar %d fișiere JS citite" % len(pe_fisier)

    inainte = _snapshot(SCHEMA_TINTA)
    rez, nemasurate, ne_json, esuate = [], [], [], []
    vazute = set()
    for fisier, linia, url in apeluri:
        concret, motiv = substituie(url, tid)
        if concret is None:
            nemasurate.append((fisier, linia, url, motiv))
            continue
        cheie = (fisier, concret)
        if cheie in vazute:
            continue
        vazute.add(cheie)
        corp, err = _get(concret, tok)
        if err:
            (ne_json if err["fel"] == "ne-JSON" else esuate).append(
                (fisier, concret, "%s %s" % (err["fel"], err["detaliu"])))
            continue
        chei = chei_recursiv(corp)
        src = pe_fisier.get(fisier, "")
        sigur, candidat, generice, prin_container = [], [], [], []
        for cale, nume in sorted(chei.items()):
            if nume in PREA_GENERICE:
                generice.append(cale)
                continue
            # Containerul e parcurs generic? Atunci copilul ajunge pe ecran fără să fie numit.
            parinti = [p.replace("[]", "") for p in cale.split(".")[:-1] if p.replace("[]", "")]
            if any(randat_generic(p, src) for p in parinti):
                prin_container.append(cale)
                continue
            if not apare_undeva(nume, tot_js):
                sigur.append(cale)
            elif not apare_in_ecran(nume, src):
                candidat.append(cale)
        rez.append({"fisier": fisier, "url": concret, "chei": len(chei),
                    "tacut_sigur": sigur, "tacut_in_ecran": candidat,
                    "randat_prin_container": prin_container, "generice": len(generice)})
    dupa = _snapshot(SCHEMA_TINTA)
    miscat = {k: (inainte.get(k), dupa.get(k)) for k in sorted(set(inainte) | set(dupa))
              if inainte.get(k) != dupa.get(k)}
    return {"rezultate": rez, "nemasurate": nemasurate, "ne_json": ne_json,
            "esuate": esuate, "apeluri": len(apeluri), "perechi": len(vazute),
            "martori_miscati": {k: list(v) for k, v in miscat.items()}}


def calibrare(d):
    """Cazurile cunoscute TREBUIE găsite; cele randate NU au voie să apară. Fără asta, cifra nu e rezultat."""
    tacut = {c for r in d["rezultate"] for c in r["tacut_sigur"] + r["tacut_in_ecran"]}
    nume_tacute = {c.split(".")[-1].replace("[]", "") for c in tacut}
    pozitive, negative = [], []
    for asteptat in ("nr_curent", "total_debit", "total_credit"):
        pozitive.append((asteptat, asteptat in nume_tacute))
    for asteptat in ("deducere_tineri", "deducere_copii", "cas_suprataxa"):
        pozitive.append((asteptat, asteptat in nume_tacute))
    for nerandat in ("descriere", "sold_final", "operatiuni"):
        negative.append((nerandat, nerandat not in nume_tacute))
    return pozitive, negative


def tipar(d):
    print("=" * 100)
    print("R97 — CAT DE MARE E CLASA: ruta livreaza, ecranul tace")
    print("=" * 100)
    print("apeluri `api.get` în static/js: %d · perechi chemate viu: %d" % (d["apeluri"], d["perechi"]))
    print("nemăsurate (interpolare nesubstituibilă): %d · ne-JSON (PDF etc.): %d · eșuate: %d"
          % (len(d["nemasurate"]), len(d["ne_json"]), len(d["esuate"])))

    cu_sigur = [r for r in d["rezultate"] if r["tacut_sigur"]]
    n_sigur = sum(len(r["tacut_sigur"]) for r in d["rezultate"])
    n_cand = sum(len(r["tacut_in_ecran"]) for r in d["rezultate"])
    print("\n═══ MĂRIMEA CLASEI")
    print("  TĂCUT SIGUR (numele nu apare NICĂIERI în static/js): **%d câmpuri**, pe **%d rute**"
          % (n_sigur, len(cu_sigur)))
    print("  TĂCUT ÎN ECRANUL CARE-L CERE (apare altundeva):      %d câmpuri, pe %d rute"
          % (n_cand, len([r for r in d["rezultate"] if r["tacut_in_ecran"]])))
    n_cont = sum(len(r.get("randat_prin_container") or []) for r in d["rezultate"])
    print("  RANDAT PRIN CONTAINER (Object.keys/entries pe părinte): %d câmpuri — SCOASE din clasă"
          % n_cont)
    print("  *Primul e PLAFON INFERIOR: randatul e supra-numarat prin constructie.*")

    print("\n═══ RUTELE CU CÂMPURI TĂCUTE SIGUR")
    for r in sorted(cu_sigur, key=lambda x: -len(x["tacut_sigur"])):
        print("  %-58s %s" % (r["url"][:58], r["fisier"]))
        print("      %d din %d chei: %s" % (len(r["tacut_sigur"]), r["chei"],
                                            ", ".join(r["tacut_sigur"][:14])))

    poz, neg = calibrare(d)
    print("\n═══ CALIBRARE")
    for nume, ok in poz:
        print("  POZITIV  %-18s %s" % (nume, "GĂSIT" if ok else "*** RATAT ***"))
    for nume, ok in neg:
        print("  NEGATIV  %-18s %s" % (nume, "corect absent" if ok else "*** FALS POZITIV ***"))
    assert all(ok for _n, ok in poz), "calibrare pozitivă picată — instrumentul nu vede clasa"
    assert all(ok for _n, ok in neg), "calibrare negativă picată — instrumentul inventează instanțe"

    print("\n═══ CE A SCRIS SONDA (martori, înainte/după)")
    m = d.get("martori_miscati") or {}
    if not m:
        print("  nimic — niciun martor s-a mișcat. *Un GET nu are voie să scrie; aici se DOVEDEȘTE,")
        print("   inclusiv pentru `/tenants/{id}/scoatere`, previzualizarea ștergerii unei firme.*")
    for k, (a, b) in sorted(m.items()):
        print("  %-40s %s → %s  (%+d)" % (k, a, b, (b or 0) - (a or 0)))

    if d["nemasurate"]:
        print("\n═══ DOMENIU NEATINS (se numără, nu se înghite): %d" % len(d["nemasurate"]))
        for f, li, u, m in d["nemasurate"][:12]:
            print("  %s:%d  %s   (%s)" % (f, li, u[:52], m))


if __name__ == "__main__":
    _d = ruleaza()
    tipar(_d)
    if "--json" in sys.argv:
        open("/tmp/r97_rezultat.json", "w", encoding="utf-8").write(
            json.dumps(_d, ensure_ascii=False, indent=1))
        print("\nJSON: /tmp/r97_rezultat.json")
