# -*- coding: utf-8 -*-
"""CE PRODUCE APLICAȚIA PE FIECARE REGIM REAL — pasul 1b, 29.08.2026.

DE CE EXISTĂ. `PLAN_INVESTIGATII.md`, faza 1, pasul 1b: *„Pentru fiecare artefact: **se produce
azi?** Măsurat pe o firmă cu date reale. «Există ruta» nu e «produce artefactul». **Se validează?**
Cu instrumentul oficial, unde există."* Iar criteriul de terminare al lui E1 cere clasificarea
**pe regimurile REALE** — cele 12 măsurate la 1a (`scripts/scan_regimuri.py`, 29.08.2026).
Măsurătoarea 1b de pe 22.08 a acoperit **trei firme**, adică **două** din cele 12 semnături; restul
regimurilor n-au fost niciodată exercitate ca artefact.

CE MĂSOARĂ, pe fiecare firmă activă:

  FAMILIA C (declarațiile) — pentru fiecare din tipurile pe care le expune aplicația:
    (1) **ce BLOCHEAZĂ selectorul** — lista `neaplicabile` de la `/declaratii/tipuri`. ATENȚIE la
        vocabular, fiindcă prima formă a scanului l-a greșit: „neblocat" **nu** înseamnă „aplicația
        spune că se datorează". `control_fiscal_api.neaplicabile_selector` acoperă **forma**
        (partidă simplă) și **vectorul TVA** (d300/d394/d390/d301) — atât. Regimul fiscal
        (micro↔profit, deci D100↔D101) **nu intră** în el; obligația pe regim o știe alt mecanism,
        `obligatii_datorate` (semaforul). Deci coloana asta măsoară ce lasă selectorul să treacă,
        nu ce datorează firma;
    (2) **ce iese efectiv** — `POST /declaratii/{tip}/valideaza`, care GENEREAZĂ și trece XML-ul
        prin **DUKIntegrator** (arbitrul oficial). Stările: valid · atenționare · erori · gri ·
        REFUZ (422, generatorul refuză înainte de XML) · EROARE.
    Divergența dintre (1) și (2) e obiectul propriu al lui 1b: un „nu se datorează" pe ecran peste
    un generator care produce oricum, sau invers.

  FAMILIA A (registrele) — balanța (rânduri **și dacă se închide**), registrul-jurnal (rânduri +
    câte note n-au document justificativ derivabil), Cartea mare, Registrul-inventar.

  FAMILIA B (situațiile financiare) — bilanțul: octeți de XML produși pe date reale.

  FAMILIA D (evidențele speciale) — registrul de casă, RIP, jurnalul de regim marjă.

CE NU VEDE, declarat:
  - **o singură perioadă** (lunar 08/2026 · trimestrial T3/2026 · anual 2026). Un artefact care ar
    ieși pe altă lună și nu pe asta apare aici ca „nu iese";
  - **corectitudinea cifrelor**: „valid la DUKIntegrator" e o afirmație despre FORMĂ. Nici măcar
    închiderea balanței nu spune că soldurile sunt corecte — o balanță greșită se închide perfect;
  - **un producător sub alt nume** decât cele căutate (termenii se scriu în raport, ca să poată fi
    contraziși);
  - artefactele fără cale HTTP se măsoară pe **producătorul** lor, iar asta se spune în rând:
    „producător DA / la om NU" nu e același lucru cu „iese".

SCRIE? Da, și se declară: generarea unei declarații lasă urmă în `public.audit_log` (excepția
scrisă în Partea II — o citire de date personale lasă urmă). Scanul face **snapshot înainte/după**
pe tabelele care ar putea fi atinse și tipărește deltele; dacă se atinge altceva decât `audit_log`,
se vede.

    set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a
    ./venv/bin/python scripts/scan_1b_regimuri.py [--firme tenant_013,tenant_003] [--md]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import db  # noqa: E402
import scan_regimuri as R  # noqa: E402

BAZA = "http://127.0.0.1:8010"

# Perioada de măsurare — una singură, aceeași pe toate firmele, ca rândurile să fie comparabile.
AN, LUNA, TRIM = 2026, 8, 3

# Tabelele care ar putea fi atinse de o generare. `audit_log` e cea așteptată; celelalte sunt
# martorii: dacă vreuna se mișcă, sonda a scris ceva ce nu trebuia (METODA — „sonda de audit nu e
# read-only până n-o dovedești").
MARTORI_PUBLIC = ("audit_log", "declaratii_coada")
MARTORI_TENANT = ("inregistrari", "inregistrari_linii", "facturi", "declaratii_depuse")


def _call(path, payload=None, tok=None, method=None, timeout=180):
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BAZA + path, data, h, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=timeout)), None
    except urllib.error.HTTPError as e:
        try:
            body = json.load(e)
        except Exception:
            body = {"detail": e.read().decode(errors="replace")[:300]}
        return None, {"cod": e.code, "detail": body.get("detail") if isinstance(body, dict) else body}
    except Exception as e:  # timeout, conexiune
        return None, {"cod": 0, "detail": str(e)[:200]}


def _token(email):
    from core import auth_api
    import psycopg2.extras as E
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT * FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
    assert u, "user %r inexistent" % email
    return auth_api.emite_token(dict(u))


def _firme(conn):
    """(tenant_id, schema, nume, cabinet_id, email_admin) pentru fiecare firmă activă."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.id, t.schema_name, t.nume, t.accounting_firm_id,
                   (SELECT u.email FROM public.users u
                     WHERE u.accounting_firm_id = t.accounting_firm_id
                       AND u.rol IN ('admin_firma','angajat')
                     ORDER BY CASE u.rol WHEN 'admin_firma' THEN 0 ELSE 1 END, u.id LIMIT 1)
            FROM public.tenants t WHERE t.activ ORDER BY t.schema_name""")
        return cur.fetchall()


def _numar(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]


def _snapshot(conn, scheme):
    s = {}
    with conn.cursor() as cur:
        for t in MARTORI_PUBLIC:
            try:
                s["public." + t] = _numar(cur, "SELECT COUNT(*) FROM public.%s" % t)
            except Exception:
                conn.rollback()
        for sch in scheme:
            for t in MARTORI_TENANT:
                try:
                    s["%s.%s" % (sch, t)] = _numar(cur, "SELECT COUNT(*) FROM %s.%s" % (sch, t))
                except Exception:
                    conn.rollback()
    return s


def _corp_perioada(tip, per):
    b = {"an": AN}
    if per == "lunar":
        b["luna"] = LUNA
    elif per == "trimestrial":
        b["trim"] = TRIM
        b["luna"] = LUNA          # d406 (SAF-T) cere an+luna chiar și la trimestrial
    return b


def familia_c(tok, tid):
    """Ce spune aplicația că se datorează × ce iese efectiv, pe fiecare tip."""
    tipuri, e = _call("/declaratii/tipuri?tenant_id=%d" % tid, tok=tok)
    if e:
        return None, {"eroare": "nu pot citi /declaratii/tipuri: %s" % e}
    neap = tipuri.get("neaplicabile") or {}
    per_map = tipuri.get("periodicitate") or {}
    out = {}
    for tip in tipuri.get("tipuri") or []:
        corp = {"tenant_id": tid}
        corp.update(_corp_perioada(tip, per_map.get(tip, "lunar")))
        t0 = time.time()
        rez, err = _call("/declaratii/%s/valideaza" % tip, corp, tok=tok, method="POST")
        dt = round(time.time() - t0, 1)
        r = {"neblocat_de_selector": tip not in neap,
             "motiv_neaplicabil": (neap.get(tip) or "")[:200],
             "periodicitate": per_map.get(tip), "secunde": dt}
        if err and err.get("cod") == 422:
            r["rezultat"] = "REFUZ"
            r["mesaj"] = str(err.get("detail"))[:220]
        elif err:
            r["rezultat"] = "EROARE %s" % err.get("cod")
            r["mesaj"] = str(err.get("detail"))[:220]
        else:
            st, sev = rez.get("stare"), rez.get("severitate")
            r["rezultat"] = ("valid" if st == "valid" else
                             "atentionare" if (st == "erori" and sev == "atentionare") else
                             "erori" if st == "erori" else "gri")
            r["operatiuni"] = rez.get("operatiuni")
            r["mesaj"] = (rez.get("erori") or "")[:220]
            r["note_rezultat"] = (rez.get("note_rezultat") or [])[:3]
        out[tip] = r
    return out, None


def familia_a_b_d(conn, tok, tid, schema):
    """Registrele, situațiile financiare, evidențele speciale — pe date reale."""
    from core import documente_api
    art = {}

    # --- A: balanța. Producătorul e cel al rutei de PDF; ruta de cabinet întoarce PDF, nu date.
    try:
        randuri = documente_api.balanta(conn, schema, AN, LUNA)
        si_d = round(sum(r["si_d"] for r in randuri), 2)
        si_c = round(sum(r["si_c"] for r in randuri), 2)
        ru_d = round(sum(r.get("ruj_d", r.get("deb", 0)) for r in randuri), 2)
        ru_c = round(sum(r.get("ruj_c", r.get("cred", 0)) for r in randuri), 2)
        sf_d = round(sum(r.get("sf_d", 0) for r in randuri), 2)
        sf_c = round(sum(r.get("sf_c", 0) for r in randuri), 2)
        art["balanta"] = {"randuri": len(randuri), "se_inchide":
                          (si_d == si_c and ru_d == ru_c and sf_d == sf_c) if randuri else None,
                          "si": [si_d, si_c], "rulaje": [ru_d, ru_c], "sf": [sf_d, sf_c]}
    except Exception as e:
        conn.rollback()
        art["balanta"] = {"eroare": str(e)[:160]}

    # --- A: registrul-jurnal, prin ruta lui (derivă cele trei coloane 14-1-1 la citire)
    j, e = _call("/tenants/%d/jurnal?an=%d&luna=%d" % (tid, AN, LUNA), tok=tok)
    if e:
        art["registru_jurnal"] = {"eroare": str(e)[:160]}
    else:
        randuri = j.get("randuri") or j.get("note") or j.get("linii") or []
        art["registru_jurnal"] = {
            "randuri": len(randuri),
            "note_fara_document": j.get("note_fara_document"),
            # Totalizarea lunară cerută de pct. 45 iese ca `total_debit`/`total_credit`. Prima formă
            # a scanului căuta `total_lunar`/`totaluri` — chei care nu există — și raporta „nu are"
            # despre un artefact care o are. Cheile se citesc din răspuns, nu din memorie.
            "total_lunar": [j.get("total_debit"), j.get("total_credit")],
            "are_total_lunar": ("total_debit" in j and "total_credit" in j),
            "chei": sorted(j.keys())[:12]}

    # --- D: registrul de casă
    c, e = _call("/tenants/%d/casa/registru?an=%d&luna=%d" % (tid, AN, LUNA), tok=tok)
    art["registru_casa"] = ({"eroare": str(e)[:160]} if e else
                            {"randuri": len(c.get("operatiuni") or c.get("randuri") or []),
                             "chei": sorted(c.keys())[:12]})

    # --- D: RIP (partidă simplă) și jurnalul de regim marjă
    r, e = _call("/tenants/%d/rip/registru?an=%d&luna=%d" % (tid, AN, LUNA), tok=tok)
    art["rip"] = ({"eroare": str(e)[:120]} if e else
                  {"randuri": len(r.get("operatiuni") or r.get("randuri") or r.get("linii") or [])})
    for fel in ("secondhand", "turism"):
        m, e = _call("/tenants/%d/jurnal-marja?tip=%s&luna=%04d-%02d" % (tid, fel, AN, LUNA), tok=tok)
        art["jurnal_marja_" + fel] = ({"eroare": str(e)[:120]} if e else
                                      {"randuri": len(m.get("randuri") or m.get("note") or [])})

    # --- POPULAȚIA lunii, pe status. Cele trei registre NU citesc aceeași mulțime: `fisa_cont`
    #     filtrează `status='validata'`, iar `documente_api.balanta` și ruta `/jurnal` nu filtrează
    #     deloc (verificat în cod, 29.08.2026). Fără numărătoarea asta, un „0 rânduri" la fișă nu se
    #     poate deosebi de „nu se produce".
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status, COUNT(*) FROM %s.inregistrari "
                        "WHERE date_trunc('month', data) = %%s GROUP BY status" % schema,
                        ("%d-%02d-01" % (AN, LUNA),))
            art["note_pe_status"] = {s: n for s, n in cur.fetchall()}
    except Exception as e:
        conn.rollback()
        art["note_pe_status"] = {"eroare": str(e)[:120]}

    # --- A: Cartea mare, prin înlocuitorul ei legal. `core/fisa_cont.py` citează norma verbatim:
    #     „Registrul Cartea mare poate fi înlocuit cu Fișa de cont pentru operațiuni diverse"
    #     (OMFP 2634/2015 Anexa 2, poz. 165–166). Nu are rută și n-are ecran — deci se cheamă
    #     PRODUCĂTORUL, iar rândul spune asta. Contul ales e cel cu cele mai multe linii în lună.
    try:
        from core import fisa_cont as _fc
        with conn.cursor() as cur:
            cur.execute("""SELECT c, COUNT(*) FROM (
                             SELECT l.cont_debit AS c FROM {s}.inregistrari_linii l
                               JOIN {s}.inregistrari i ON i.id=l.inregistrare_id
                              WHERE EXTRACT(YEAR FROM i.data)=%s AND EXTRACT(MONTH FROM i.data)=%s
                             UNION ALL
                             SELECT l.cont_credit FROM {s}.inregistrari_linii l
                               JOIN {s}.inregistrari i ON i.id=l.inregistrare_id
                              WHERE EXTRACT(YEAR FROM i.data)=%s AND EXTRACT(MONTH FROM i.data)=%s
                           ) t GROUP BY c ORDER BY 2 DESC LIMIT 1""".format(s=schema),
                        (AN, LUNA, AN, LUNA))
            r0 = cur.fetchone()
        if not r0:
            art["fisa_cont"] = {"randuri": 0, "cont": None, "ruta": False,
                                "motiv": "nicio linie în lună"}
        else:
            f = _fc.fisa_cont(conn, schema, r0[0], AN, luna=LUNA)
            art["fisa_cont"] = {"randuri": len(f.get("randuri") or []), "cont": r0[0],
                                "ruta": False,
                                # `fisa_cont` citește DOAR notele `validata`; balanța și
                                # registrul-jurnal nu filtrează pe status. De-asta se numără mai jos
                                # notele pe status: fără ele, un „0 rânduri" nu se poate citi.
                                "citeste_doar_validate": True}
    except Exception as e:
        conn.rollback()
        art["fisa_cont"] = {"eroare": str(e)[:160], "ruta": False}

    # --- B: bilanțul. Nu are rută (măsurat 22.08); se cheamă producătorul, și se spune.
    try:
        from core import bilant_api
        rez = bilant_api.genereaza(conn, schema, AN)
        xml = rez[0] if isinstance(rez, tuple) else (rez.get("xml") if isinstance(rez, dict) else rez)
        art["bilant"] = {"octeti": len(xml or ""), "ruta": False}
    except Exception as e:
        conn.rollback()
        art["bilant"] = {"eroare": str(e)[:160], "ruta": False}

    return art


def ruleaza(doar=None):
    db.init_pool()
    with db.get_conn() as conn:
        lot = R.aduna(conn)                     # profilurile, cu ACEEAȘI definiție ca la 1a
        firme = _firme(conn)
    assert lot, "domeniul e gol — nicio firmă activă"
    assert firme, "domeniul e gol — nicio firmă activă în public.tenants"

    prof = {sc: p for sc, _n, p, _s in lot}
    tinta = [f for f in firme if (not doar or f[1] in doar)]
    assert tinta, "niciun rând de măsurat — filtrul --firme a golit domeniul"
    scheme = [f[1] for f in tinta]

    with db.get_conn() as conn:
        inainte = _snapshot(conn, scheme)

    tok_cache, rez = {}, {}
    for tid, schema, nume, cab, email in tinta:
        if not email:
            rez[schema] = {"eroare": "cabinetul %s n-are user cu acces" % cab}
            continue
        if email not in tok_cache:
            tok_cache[email] = _token(email)
        tok = tok_cache[email]
        c, err = familia_c(tok, tid)
        with db.get_conn(schema) as conn:
            abd = familia_a_b_d(conn, tok, tid, schema)
        p = prof.get(schema)
        rez[schema] = {"tenant_id": tid, "nume": nume, "cabinet": cab,
                       "semnatura": (R.semnatura(p) if isinstance(p, dict) else None),
                       "familia_c": c, "familia_c_eroare": err, "artefacte": abd}
        print("  măsurat %-12s %-32s %s" % (schema, (nume or "")[:32],
                                            "C:%d tipuri" % len(c or {})))

    with db.get_conn() as conn:      # conexiune NOUĂ: `SET search_path` e tranzacțional
        dupa = _snapshot(conn, scheme)

    # ——— calibrare, în amândouă direcțiile (METODA §22) ———
    valide = sum(1 for r in rez.values()
                 for v in ((r.get("familia_c") or {}).values() if r.get("familia_c") else [])
                 if v.get("rezultat") == "valid")
    assert valide > 0, ("CALIBRARE POZITIVĂ PICATĂ: nicio declarație validă pe tot portofoliul — "
                        "instrumentul măsoară altceva decât crede (app oprit? token greșit?)")
    goale = [s for s, r in rez.items()
             if (r.get("artefacte") or {}).get("balanta", {}).get("randuri") == 0]
    print("\n(calibrare: %d rezultate `valid` pe portofoliu · %d firme cu balanță de 0 rânduri)"
          % (valide, len(goale)))

    return rez, inainte, dupa


# ————————————————————————— tipărire —————————————————————————

def _et_c(v):
    r = v.get("rezultat", "?")
    op = v.get("operatiuni")
    if r == "valid":
        return "valid" + ("(%s op)" % op if op is not None else "")
    if r == "REFUZ":
        return "REFUZ"
    return r


def tipar(rez, inainte, dupa):
    grupe = {}
    for schema, r in sorted(rez.items()):
        grupe.setdefault(r.get("semnatura"), []).append((schema, r))

    print("\n" + "=" * 100)
    print("1b — CE PRODUCE APLICAȚIA PE FIECARE REGIM REAL   (lunar %02d/%d · trim T%d/%d · anual %d)"
          % (LUNA, AN, TRIM, AN, AN))
    print("=" * 100)
    print("REGIMURI ACOPERITE: %d din 12 măsurate la 1a · FIRME: %d" % (len(grupe), len(rez)))

    print("LIMITĂ DE VOCABULAR: «neblocat» = selectorul nu-l declară neaplicabil. Selectorul acoperă")
    print("  FORMA (partidă simplă) + vectorul TVA (d300/d394/d390/d301). Obligația pe REGIM FISCAL")
    print("  (micro→D100 / profit→D101) o știe alt mecanism — `obligatii_datorate` — care NU intră aici.")

    tipuri = sorted({t for r in rez.values() for t in (r.get("familia_c") or {})})
    for sem, firme in sorted(grupe.items(), key=lambda x: (-len(x[1]), str(x[0]))):
        print("\n─── REGIM: %s   (%d firme)" % (" · ".join(sem) if sem else "PROFIL INCOMPLET",
                                                len(firme)))
        for schema, r in firme:
            if r.get("eroare"):
                print("  %-12s  %s" % (schema, r["eroare"]))
                continue
            print("  %-12s %s" % (schema, (r.get("nume") or "")[:40]))
            c = r.get("familia_c") or {}
            for tip in tipuri:
                v = c.get(tip)
                if not v:
                    continue
                marca = "neblocat" if v["neblocat_de_selector"] else "BLOCAT  "
                linie = "      %-6s %-8s → %-14s" % (tip, marca, _et_c(v))
                if not v["neblocat_de_selector"] and v["rezultat"] in ("valid", "atentionare"):
                    linie += "  ⚠ DIVERGENȚĂ: selectorul o declară NEAPLICABILĂ, generatorul o produce"
                elif v.get("mesaj"):
                    linie += "  %s" % v["mesaj"][:90].replace("\n", " ")
                print(linie)
            a = r.get("artefacte") or {}
            b = a.get("balanta", {})
            print("      balanță: %s rânduri, se închide=%s · jurnal: %s rânduri (fără document: %s,"
                  " total lunar: %s) · fișă de cont %s: %s rânduri · casă: %s · RIP: %s"
                  % (b.get("randuri"), b.get("se_inchide"),
                     a.get("registru_jurnal", {}).get("randuri"),
                     a.get("registru_jurnal", {}).get("note_fara_document"),
                     a.get("registru_jurnal", {}).get("are_total_lunar"),
                     a.get("fisa_cont", {}).get("cont"), a.get("fisa_cont", {}).get("randuri"),
                     a.get("registru_casa", {}).get("randuri"), a.get("rip", {}).get("randuri")))
            print("      note în lună, pe status: %s" % (a.get("note_pe_status") or {}))
            print("      bilanț (producător, FĂRĂ rută): %s"
                  % a.get("bilant", {}).get("octeti", a.get("bilant", {}).get("eroare")))

    # ——— divergențele, adunate ———
    div = [(s, t) for s, r in sorted(rez.items())
           for t, v in (r.get("familia_c") or {}).items()
           if not v["neblocat_de_selector"] and v["rezultat"] in ("valid", "atentionare")]
    print("\n═══ DIVERGENȚE «selectorul o declară neaplicabilă, generatorul o produce»: %d" % len(div))
    for s, t in div:
        print("  %-12s %s" % (s, t))

    print("\n═══ CELE TREI REGISTRE NU CITESC ACEEAȘI MULȚIME (luna %02d/%d)" % (LUNA, AN))
    print("    `fisa_cont` (Cartea mare) cere `status='validata'`; balanța și `/jurnal` nu filtrează.")
    for s, r in sorted(rez.items()):
        st = (r.get("artefacte") or {}).get("note_pe_status") or {}
        if not st:
            continue
        val = st.get("validata", 0)
        alt = sum(n for k, n in st.items() if k != "validata")
        if alt:
            print("  %-12s %d note în lună, din care VALIDATE %d · restul %s → intră în balanță și în"
                  " registrul-jurnal, NU în fișa de cont" % (s, val + alt, val,
                                                             {k: n for k, n in st.items()
                                                              if k != "validata"}))

    rele = [(s, t, v["rezultat"]) for s, r in sorted(rez.items())
            for t, v in (r.get("familia_c") or {}).items() if v["rezultat"] in ("erori", "gri")]
    print("\n═══ IES, DAR NU TREC ARBITRUL (lista 4 a verdictului 1d): %d" % len(rele))
    for s, t, st in rele:
        print("  %-12s %-6s %s" % (s, t, st))

    print("\n═══ CE A SCRIS SONDA (snapshot înainte/după)")
    miscat = {k: (inainte.get(k), dupa.get(k)) for k in sorted(set(inainte) | set(dupa))
              if inainte.get(k) != dupa.get(k)}
    if not miscat:
        print("  nimic — niciun martor s-a mișcat")
    for k, (a, b) in miscat.items():
        print("  %-40s %s → %s  (%+d)" % (k, a, b, (b or 0) - (a or 0)))


if __name__ == "__main__":
    _doar = None
    if "--firme" in sys.argv:
        _doar = set(sys.argv[sys.argv.index("--firme") + 1].split(","))
    _r, _i, _d = ruleaza(_doar)
    tipar(_r, _i, _d)
    if "--json" in sys.argv:
        # În AFARA repo-ului: e ieșirea unei măsurători, nu un artefact de versionat. Cifra se
        # reface rulând instrumentul; un JSON comis ar îmbătrâni tăcut lângă el.
        cale = "/tmp/1b_rezultat.json"
        open(cale, "w", encoding="utf-8").write(json.dumps(_r, ensure_ascii=False, indent=1))
        print("\nJSON: %s" % cale)
