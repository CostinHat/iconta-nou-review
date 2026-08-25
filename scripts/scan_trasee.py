# -*- coding: utf-8 -*-
"""scripts/scan_trasee.py — INVENTARUL TRASEELOR, calculat, nu ținut minte.

De ce există. `TRASEE.md` scria traseele ca proză. O proză nu se poate recalcula:
cifra „câte trasee sunt", „câte se pot scrie din cod" și „care firmă poate parcurge
care traseu" erau amintiri. METODA §22 + regula „o cifră care nu se poate recalcula
nu e o măsurătoare" cer un instrument. Ăsta e.

CE FACE
  1. Ține inventarul declarat al traseelor (TRASEE, mai jos) — numele, rutele, tabelele.
  2. Verifică ACOPERIREA: fiecare rută din `main.py` aparține **exact unui** traseu sau
     unei suprafețe declarate ca ne-documentară. O rută nouă care nu intră nicăieri
     IESE LA RAPORT — traseul nu poate îmbătrâni tăcut.
  3. Extrage din cod, per traseu: rutele (metodă, cale, gardă, rol cerut, permisiune
     fină), modulele din `core/`, tabelele în care se scrie, stările puse, refuzurile.
  4. Clasifică traseul **mecanic**, din trei fapte măsurate — nu din impresie:
        exterior?  scrie?   ->  clasă
        da         *            MANUAL   (traseul intern se oprește undeva; unde = decizie)
        nu         nu           PARȚIAL  (se produce ceva ce nu se păstrează nicăieri)
        nu         da           MECANIC  (pașii, stările și refuzurile se citesc din cod)
  5. Cu `--db`: pentru fiecare traseu, **care firmă îl poate exercita azi** — numărate
     pe schemele reale, nu pe firme inventate.

CE NU VEDE, scris ca să nu se creadă altceva:
  - nu vede ce TREBUIE să fie adevărat după un pas (e decizie, nu cod — Partea VII.5);
  - nu vede traseele negative care ar trebui să existe, doar pe cele tratate;
  - clasa MECANIC spune că traseul se poate SCRIE din cod, nu că e corect;
  - „firma poate exercita" = are rânduri în tabelele traseului. Nu probează parcurgerea.

Rulare:
    ./venv/bin/python scripts/scan_trasee.py            # fără DB
    ./venv/bin/python scripts/scan_trasee.py --db       # + firmele
    ./venv/bin/python scripts/scan_trasee.py --json
"""
import ast
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
#  INVENTARUL — declarat, verificat contra codului mai jos
# ============================================================
# Fiecare traseu: (id, nume, [tipare de cale], [tabele proprii])
# Tiparele se potrivesc pe calea NORMALIZATĂ (parametrii -> {}).
TRASEE = [
    # --- deja scrise în TRASEE.md, părțile I-V ---
    ("T01", "Declarația — generare, validare, coadă, aprobare, depunere",
     [r"^/declaratii", r"^/coada", r"^/firme/\{\}/verificari",
      r"^/control-fiscal(/\{\}(?!/audit-preluare))?$",
      r"^/termene$", r"^/tenants/\{\}/istoric-declaratii-import"],
     ["declaratii_coada", "declaratii_depuse"]),
    ("T02", "Factura emisă — creare, contabilizare, ieșiri",
     [r"^/tenants/\{\}/facturi$", r"^/tenants/\{\}/facturi/emite",
      r"^/tenants/\{\}/facturi/numerotare", r"^/tenants/\{\}/facturi/\{\}$",
      r"^/tenants/\{\}/facturi/\{\}/(pdf|email|storno|transforma|contabilizeaza|notificare)",
      r"^/tenants/\{\}/facturi-recurente", r"^/api/v1/firme/\{\}/facturi"],
     ["facturi", "factura_linii", "facturi_recurente"]),
    ("T03", "Statul de plată și fluturașul",
     [r"^/tenants/\{\}/stat-plata", r"^/tenants/\{\}/fluturas"],
     ["state_plata", "beneficii_lunare"]),
    ("T04", "Concediul medical",
     [r"^/tenants/\{\}/salariati/\{\}/concedii", r"^/tenants/\{\}/concedii/coduri",
      r"^/tenants/\{\}/calcul-cm"],
     ["concedii_medicale"]),
    ("T05", "Nota contabilă — de la document la registrul-jurnal",
     [r"^/tenants/\{\}/jurnal(/|$)", r"^/tenants/\{\}/nota-", r"^/tenants/\{\}/plan-conturi",
      r"^/tenants/\{\}/documente/balanta", r"^/api/v1/firme/\{\}/balanta"],
     ["inregistrari", "inregistrari_linii", "plan_conturi"]),
    # --- deja scrise în TRASEE.md, partea X ---
    ("T06", "Importul de e-Factura și transmiterea prin SPV",
     [r"^/tenants/\{\}/import-efactura", r"^/tenants/\{\}/facturi-primite",
      r"^/tenants/\{\}/facturi/\{\}/trimite-spv", r"^/tenants/\{\}/trimiteri-spv"],
     ["efactura_primite", "efactura_trimiteri"]),
    ("T07", "Extrasul bancar și potrivirea",
     [r"^/tenants/\{\}/banca"], ["extras_linii"]),
    ("T08", "NIR și recepția",
     [r"^/tenants/\{\}/stocuri/nir"], ["nir", "nir_linii"]),
    ("T09", "Casa și registrul de casă",
     [r"^/tenants/\{\}/casa"], ["casa_operatiuni"]),
    ("T10", "Inventarierea",
     [r"^/tenants/\{\}/stocuri/inventar", r"^/tenants/\{\}/rip/inventar",
      r"^/tenants/\{\}/verificare-stocuri", r"^/tenants/\{\}/d406-(active|stocuri)"],
     []),
    ("T11", "Închiderea lunii",
     [r"^/tenants/\{\}/facturi/perioada", r"^/tenants/\{\}/perioade-blocate"],
     ["perioade_blocate", "perioada_confirmata"]),
    ("T12", "Închiderea anului și situațiile financiare",
     [r"^/tenants/\{\}/s100[35]"], []),
    ("T13", "Trecerea de regim fiscal",
     [r"^/tenants/\{\}/firma-profil", r"^/tenants/\{\}/vector$", r"^/migrare/vector"],
     ["firma_profil"]),
    ("T14", "Preluarea unei firme",
     [r"^/migrare/(?!vector)", r"^/tenants/\{\}/solduri",
      r"^/tenants/\{\}/(salariati|asociati|retete|articole|mijloace-fixe)-import",
      r"^/tenants/\{\}/rip-import", r"^/tenants/\{\}/parteneri",
      r"^/control-fiscal/\{\}/audit-preluare"],
     ["solduri_initiale", "solduri_parteneri", "asociati"]),
    # --- adăugate 25.08.2026, din inventarul complet ---
    ("T15", "Salariatul — angajare, contract, adeverință, REGES",
     [r"^/tenants/\{\}/salariati$", r"^/tenants/\{\}/salariati/\{\}$",
      r"^/tenants/\{\}/salariati/\{\}/(adeverinta|beneficiu-lunar)",
      r"^/tenants/\{\}/contracte", r"^/contracte/marcaje", r"^/tenants/\{\}/reges-",
      r"^/cor$"],
     ["salariati", "salariu_istoric", "contracte_sabloane"]),
    ("T16", "Pontajul",
     [r"^/tenants/\{\}/salariati/\{\}/pontaj", r"^/tenants/\{\}/pontaj",
      r"^/util/zile-lucratoare"],
     ["pontaj"]),
    ("T17", "Plata salariilor — fișierul către bancă",
     [r"^/tenants/\{\}/plata-salarii"], []),
    ("T18", "Chitanța și încasarea",
     [r"^/tenants/\{\}/chitante", r"^/tenants/\{\}/facturi/\{\}/link-plata",
      r"^/public/plata"],
     ["chitante"]),
    ("T19", "Scadențarul și notificările de scadență",
     [r"^/tenants/\{\}/scadentar"], ["notificari_scadenta"]),
    ("T20", "Mișcarea de stoc — intrare, ieșire, transfer, reclasificare",
     [r"^/tenants/\{\}/stocuri/(?!nir|inventar)"], ["articole", "miscari_stoc"]),
    ("T21", "Rețeta și producția",
     [r"^/tenants/\{\}/retete(/|$)", r"^/tenants/\{\}/produse"],
     ["retete", "retete_linii", "produse"]),
    ("T22", "Mijlocul fix și amortizarea",
     [r"^/tenants/\{\}/mijloace-fixe$", r"^/tenants/\{\}/amortizare",
      r"^/tenants/\{\}/reevaluare-imobilizare"],
     ["mijloace_fixe"]),
    ("T23", "Bonul de la client — portalul și decontul",
     [r"^/portal/bon", r"^/tenants/\{\}/bonuri"], ["bonuri"]),
    ("T24", "Bonul fiscal și raportul Z (AMEF, horeca)",
     [r"^/tenants/\{\}/horeca"], []),
    ("T25", "Comanda din magazinul online (WooCommerce)",
     [r"^/tenants/\{\}/woocommerce"], []),
    ("T26", "Registratura",
     [r"^/tenants/\{\}/registratura"], ["registratura"]),
    ("T27", "e-Transport",
     [r"^/tenants/\{\}/etransport"], ["etransport_trimiteri"]),
    ("T28", "Operațiunile intracomunitare, VIES și Intrastat",
     [r"^/tenants/\{\}/(achizitie-ic|vanzare-ic|verifica-vies|intrastat-praguri)",
      r"^/tenants/\{\}/d390-clasificare", r"^/tenants/\{\}/verifica-cui",
      r"^/public/verifica-cui"],
     ["d390_manual", "d390_reclasificare"]),
    ("T29", "Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă",
     [r"^/tenants/\{\}/(vanzare-marja|vanzare-marja-turism|vanzare-aur-investitii)",
      r"^/tenants/\{\}/(achizitie-agricultor|vanzare-agricultor|achizitie-taxare-inversa)",
      r"^/tenants/\{\}/(achizitie-neinregistrat|achizitie-necorporala)",
      r"^/tenants/\{\}/(import-extracomunitar|export-extracomunitar)",
      r"^/tenants/\{\}/jurnal-marja"],
     []),
    ("T30", "Operațiunile în valută",
     [r"^/tenants/\{\}/(decontare-valuta|reevaluare-valuta)"], []),
    ("T31", "Completările manuale la o declarație (D300, D301)",
     [r"^/tenants/\{\}/d300-manual", r"^/tenants/\{\}/d301-operatiuni"],
     ["d300_manual", "d301_operatiuni"]),
    ("T32", "Registrul de încasări și plăți (partida simplă)",
     [r"^/tenants/\{\}/rip/(?!inventar)"], ["rip_operatiuni"]),
    ("T33", "Exportul contabil (SAGA, WinMentor)",
     [r"^/tenants/\{\}/facturi/export-", r"^/tenants/\{\}/facturi/\{\}/export-"],
     []),
    ("T34", "Rapoartele comerciale, centrele de cost și rapoartele salvate",
     [r"^/tenants/\{\}/rapoarte-comerciale", r"^/tenants/\{\}/rapoarte-salvate",
      r"^/tenants/\{\}/centre-cost",
      r"^/api/v1/firme/\{\}/kpi", r"^/cabinet/consolidare", r"^/ansamblu$"],
     ["rapoarte_salvate", "centre_cost", "bugete"]),
    ("T35", "Pachetul lunar către client și solicitările lui",
     [r"^/pachete", r"^/portal/(?!bon)", r"^/tenants/\{\}/solicitari",
      r"^/tenants/\{\}/(client-acces|acces-portal)", r"^/tenants/\{\}/clienti"],
     ["clienti"]),
]

# Suprafețe care NU poartă un document — declarate, ca să nu fie confundate cu o lipsă.
NEDOCUMENTARE = [
    (r"^/$|^/favicon\.ico$|^/sitemap\.xml$|^/robots\.txt$|^/ghid", "pagini publice"),
    (r"^/auth/|^/public/(termeni|config|activare|magic-|reset-parola)", "cont și acces"),
    (r"^/cont/|^/eu/", "contul actorului"),
    (r"^/asistenti|^/cabinet/api-chei|^/capacitate$|^/tipare", "cabinetul și echipa"),
    (r"^/admin/", "administrarea furnizorului"),
    (r"^/gdpr/", "GDPR"),
    (r"^/raportari|^/recomanda|^/api/eveniment-public|^/ajutor/", "suport și telemetrie"),
    (r"^/notificari", "notificări"),
    (r"^/tenants$|^/tenants/\{\}$", "firma ca obiect de administrare"),
    (r"^/api/v1/firme$", "cheia de integrare"),
]

METODE = {"get", "post", "put", "patch", "delete"}
GARZI = {"cere_cabinet", "cere_context", "cere_rol", "cere_client", "cere_api_key"}
ROLURI = ("superadmin", "admin_firma", "angajat", "client")

RETEA = ("requests.", "urlopen")
LOCAL = ("subprocess.",)

# MARGINEA unui traseu = pasul la care artefactul ajunge la un TERȚ CARE ACȚIONEAZĂ pe
# baza lui. Nu e același lucru cu „modulul cheamă rețeaua": `requests` nu deosebește o
# trimitere de o citire, iar dacă se ia închiderea tranzitivă peste toate modulele de
# rețea, `observare` (email) trage după el jumătate din aplicație și clasificarea devine
# fără sens. Deci lista de mai jos e ENUMERATĂ, cu motivul lângă fiecare — iar
# `nemargini` spune de ce celelalte module de rețea NU sunt margini.
MARGINI = {
    "efactura_send": "transmite factura firmei la ANAF (SPV)",
    "spv_conector": "poarta OAuth către ANAF — upload, stare mesaj, descărcare",
    "spv_receive": "primește mesajele SPV ale firmei",
    "spv_refresh": "rotește tokenul SPV",
    "spv_poll": "interoghează periodic SPV",
    "etransport_send": "transmite declarația UIT la ANAF",
    "reges_client": "transmite salariatul la registrul de evidență a muncii",
    "woocommerce": "sincronizează comenzile cu magazinul online",
    "plati": "linkul de plată — procesatorul (azi MOCK, vezi /public/plata)",
}
# Module de infrastructură: apar în aproape orice rută și nu spun nimic despre traseu.
# Se scot din setul traseului, altfel `db`/`auth_api` aduc `users` și `accounting_firms`
# ca „tabele scrise" în toate cele 35.
INFRA = {"db", "auth_api", "common", "mesaje", "nucleu"}

NEMARGINI = {
    "observare": "email și telemetrie: pleacă o COPIE, nu artefactul, iar traseul nu "
                 "depinde de răspuns",
    "anaf_api": "CITIRE (verificare CUI) — răspunsul nu schimbă starea artefactului",
    "curs_bnr": "CITIRE cu istoric local în `curs_bnr_zilnic`",
    "intracomunitar": "CITIRE (VIES) — intră ca dovadă, nu ca stare",
    "monitor_fiscal": "CITIRE de supraveghere, în afara traseului documentului",
    "duk": "rulează LOCAL prin subprocess, fără rețea — corectura din 24.08.2026",
}


CALE_TABELE = os.path.join(RAD, "scripts", "trasee_tabele.json")


def tabele_cunoscute():
    """Lista tabelelor reale, regenerată din bază cu `--tabele`. Există ca fișier, nu ca
    listă în cod, tocmai ca să fie RECALCULABILĂ. Fără ea, regexul de SQL culege și
    fragmente de f-string (`factur`, `pe`) și le raportează ca tabele."""
    try:
        return set(json.load(open(CALE_TABELE, encoding="utf-8"))["tabele"])
    except OSError:
        return None


def normalizeaza(cale):
    return re.sub(r"\{[^}]+\}", "{}", cale)


# ============================================================
#  CITIREA CODULUI
# ============================================================
def _garzi_si_rol(fn, dec):
    garzi, roluri, fine = set(), set(), set()
    surse = [dec]
    a = fn.args
    surse += list(a.defaults) + [d for d in a.kw_defaults if d is not None]
    surse += [x.annotation for x in (list(a.args) + list(a.kwonlyargs)) if x.annotation]
    for kw in getattr(dec, "keywords", []) or []:
        if kw.arg == "dependencies":
            surse.append(kw.value)
    for s in surse:
        for n in ast.walk(s):
            nume = None
            if isinstance(n, ast.Name):
                nume = n.id
            elif isinstance(n, ast.Attribute):
                nume = n.attr
            if nume in GARZI:
                garzi.add(nume)
            if isinstance(n, ast.Call):
                f = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                if f == "cere_rol":
                    garzi.add("cere_rol")
                    for arg in n.args:
                        if isinstance(arg, ast.Constant):
                            roluri.add(str(arg.value))
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if f in ("_are_permisiune", "are_permisiune"):
                for arg in n.args:
                    if isinstance(arg, ast.Constant):
                        fine.add(str(arg.value))
            if f == "_cer_admin_cabinet":
                roluri.add("admin_firma(ajutor)")
        if isinstance(n, (ast.Compare, ast.Call)):
            try:
                t = ast.unparse(n)
            except Exception:
                continue
            if '"rol"' in t.replace("'", '"') and any(r in t for r in ROLURI):
                roluri.add("verificat-în-corp")
    return sorted(garzi), sorted(roluri), sorted(fine)


def citeste_rute():
    """Rutele din main.py. Aliasurile de import se REZOLVĂ la numele real al modulului
    (`from core import efactura_send as _efs` -> `_efs` = `efactura_send`); fără asta,
    modulul-margine nu se recunoaște și traseul e clasificat greșit MECANIC."""
    src = open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    alias = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("core"):
            for al in n.names:
                alias[al.asname or al.name] = al.name
        if isinstance(n, ast.Import):
            for al in n.names:
                if al.name.startswith("core."):
                    alias[al.asname or al.name.split(".")[-1]] = al.name.split(".")[-1]
    module_core = set(alias)
    rute = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in fn.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            metoda = getattr(dec.func, "attr", None)
            if metoda not in METODE or not dec.args:
                continue
            if not isinstance(dec.args[0], ast.Constant):
                continue
            garzi, roluri, fine = _garzi_si_rol(fn, dec)
            # Aliasurile LOCALE bat pe cele de modul. Multe rute fac
            # `from core import stocuri_api as _s` ÎN CORP, iar `_s` e refolosit de zeci
            # de ori pentru module diferite: fără harta locală, ruta de NIR primea
            # `salarizare` drept modul. E mai rău decât o absență — e o atribuire falsă,
            # și de-aia se citește harta locală întâi.
            local = dict(alias)
            for n in ast.walk(fn):
                if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("core"):
                    for al in n.names:
                        local[al.asname or al.name] = al.name
                elif isinstance(n, ast.Import):
                    for al in n.names:
                        if al.name.startswith("core."):
                            local[al.asname or al.name.split(".")[-1]] = al.name.split(".")[-1]
            chemate = {local[n.value.id] for n in ast.walk(fn)
                       if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                       and n.value.id in local}
            chemate -= INFRA
            # SQL scris INLINE în rută, nu doar prin module. Fără asta, un traseu al
            # cărui UPDATE stă în corpul rutei (pontaj, vector) apare ca „nu scrie
            # nimic" — aceeași absență falsă ca la `firma_profil_api`.
            propriu = {}
            for m in RE_W.finditer("\n".join(_siruri(ast.unparse(fn)))):
                tab = m.group(2)
                if tab.lower() in ("set", "from", "into", "where"):
                    continue
                propriu.setdefault(tab, set()).add(m.group(1).upper().split()[0])
            rute.append({"metoda": metoda.upper(), "cale": dec.args[0].value,
                         "norm": normalizeaza(dec.args[0].value), "fn": fn.name,
                         "linie": fn.lineno, "garzi": garzi, "roluri": roluri,
                         "fine": fine, "module": sorted(chemate),
                         "scrie_inline": {k: sorted(v) for k, v in sorted(propriu.items())},
                         "refuzuri": ast.unparse(fn).count("HTTPException(")})
    return rute


RE_W = re.compile(r'\b(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+'
                  r'(?:"?\{[^}]*\}"?\.|"?%\(?\w*\)?s"?\.|"?[a-z_]+"?\.)?'
                  r'"?([a-zA-Z_][a-zA-Z0-9_]*)"?', re.I)
RE_STARE = re.compile(r"\b(status|stare)\s*=\s*['\"]([a-z_]+)['\"]", re.I)


def _siruri(src):
    """Toate literalele de șir, inclusiv părțile constante ale f-string-urilor.
    Fără asta, un `UPDATE {schema}.facturi` scris ca f-string nu se vede — și tocmai
    forma asta a produs absența falsă de pe `firma_profil_api` (24.08)."""
    out = []
    try:
        t = ast.parse(src)
    except SyntaxError:
        return [src]
    for n in ast.walk(t):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
        elif isinstance(n, ast.JoinedStr):
            out.append("".join(str(v.value) if isinstance(v, ast.Constant) else "{}"
                               for v in n.values))
    return out


def citeste_module():
    """Per modul din core/: tabele scrise, stări puse, refuzuri, atingerea exteriorului."""
    rez = {}
    cdir = os.path.join(RAD, "core")
    for f in sorted(os.listdir(cdir)):
        if not f.endswith(".py") or f.startswith("test_"):
            continue
        src = open(os.path.join(cdir, f), encoding="utf-8").read()
        tot = "\n".join(_siruri(src))
        scrie = {}
        for m in RE_W.finditer(tot):
            tab = m.group(2)
            if tab.lower() in ("set", "from", "into", "where"):
                continue
            scrie.setdefault(tab, set()).add(m.group(1).upper().split()[0])
        rez[f[:-3]] = {
            "scrie": {k: sorted(v) for k, v in sorted(scrie.items())},
            "stari": sorted({m.group(2) for m in RE_STARE.finditer(tot)}),
            "refuzuri": src.count("HTTPException(") + src.count("raise ValueError"),
            "retea": any(x in src for x in RETEA),
            "local": any(x in src for x in LOCAL),
        }
    return rez


def module_margine(mod):
    """Modulele-margine + cele care cheamă DIRECT o margine.

    Închiderea e de UN SINGUR PAS, deliberat: `etransport_send` nu importă `requests`,
    cheamă `spv_conector`, deci trebuie prins — dar o închidere completă face din orice
    modul care trimite un email o margine, și atunci clasa nu mai deosebește nimic.

    Calibrare anti-vacuu: dacă un modul din `MARGINI` nu mai există în `core/`, funcția
    ridică — altfel lista ar îmbătrâni tăcut și ar raporta verde despre o margine ștearsă.
    """
    lipsa = sorted(set(MARGINI) - set(mod))
    if lipsa:
        raise SystemExit("MARGINI numește module inexistente în core/: %s" % ", ".join(lipsa))
    gasite = set(MARGINI)
    cdir = os.path.join(RAD, "core")
    for k in mod:
        if k in gasite:
            continue
        try:
            src = open(os.path.join(cdir, k + ".py"), encoding="utf-8").read()
        except OSError:
            continue
        if any(re.search(r"\bfrom core import [^\n]*\b%s\b|\bcore\.%s\b" % (re.escape(m), re.escape(m)), src)
               for m in MARGINI):
            gasite.add(k)
    return gasite


# ============================================================
#  ACOPERIREA — nicio rută în afara inventarului
# ============================================================
def potriveste(norm, tipare):
    return any(re.search(t, norm) for t in tipare)


def acoperire(rute):
    per_traseu, orfane, dublate = {t[0]: [] for t in TRASEE}, [], []
    nedoc = []
    for r in rute:
        gasit = [t[0] for t in TRASEE if potriveste(r["norm"], t[2])]
        if len(gasit) > 1:
            dublate.append((r["metoda"], r["cale"], gasit))
        if gasit:
            per_traseu[gasit[0]].append(r)
            continue
        et = next((e for p, e in NEDOCUMENTARE if re.search(p, r["norm"])), None)
        if et:
            nedoc.append((r["metoda"], r["cale"], et))
        else:
            orfane.append((r["metoda"], r["cale"]))
    return per_traseu, orfane, dublate, nedoc


def clasifica(exterior, scrie):
    if exterior:
        return "MANUAL"
    if not scrie:
        return "PARTIAL"
    return "MECANIC"


def construieste(cu_db=False):
    rute = citeste_rute()
    mod = citeste_module()
    cunoscute = tabele_cunoscute()
    if cunoscute:
        for r in rute:
            r["scrie_inline"] = {k: v for k, v in r["scrie_inline"].items() if k in cunoscute}
        for info in mod.values():
            info["scrie"] = {k: v for k, v in info["scrie"].items() if k in cunoscute}
    ext = module_margine(mod)
    per_traseu, orfane, dublate, nedoc = acoperire(rute)
    firme = masoara_firme() if cu_db else None

    out = {"total_rute": len(rute), "orfane": orfane, "dublate": dublate,
           "nedocumentare": len(nedoc), "trasee": []}
    for tid, nume, tipare, tabele in TRASEE:
        rr = per_traseu[tid]
        mods = sorted({m for r in rr for m in r["module"]})
        scrise, stari, exterioare = {}, set(), []
        refuz = sum(r["refuzuri"] for r in rr)
        for r in rr:
            for tab, verbe in r["scrie_inline"].items():
                scrise.setdefault(tab, set()).update(verbe)
        for m in mods:
            info = mod.get(m)
            if not info:
                continue
            for tab, verbe in info["scrie"].items():
                scrise.setdefault(tab, set()).update(verbe)
            stari.update(info["stari"])
            refuz += info["refuzuri"]
            if m in ext:
                exterioare.append(m)
        t = {
            "id": tid, "nume": nume, "rute": len(rr),
            "mutante": sum(1 for r in rr if r["metoda"] in ("POST", "PUT", "PATCH", "DELETE")),
            "fara_rol": sum(1 for r in rr
                            if r["metoda"] in ("POST", "PUT", "PATCH", "DELETE")
                            and not r["roluri"] and not r["fine"] and r["garzi"]),
            "roluri": sorted({x for r in rr for x in r["roluri"]}),
            "fine": sorted({x for r in rr for x in r["fine"]}),
            "module": mods,
            "scrie": {k: sorted(v) for k, v in sorted(scrise.items())},
            "stari": sorted(stari), "refuzuri": refuz,
            "exterior": sorted(exterioare),
            "tabele_declarate": tabele,
        }
        t["clasa"] = clasifica(bool(exterioare), bool(scrise))
        if firme is not None:
            if not tabele:
                # NU e „zero firme". E „nu se poate ști din tabele" — traseul n-are tabelă
                # proprie (produce fără să persiste). Un necunoscut nu se rotunjește la
                # „știu că nu": vezi interdicția 32.
                t["firme"] = None
                t["firme_nr"] = None
            else:
                t["firme"] = sorted(sc for sc, n in firme.items()
                                    if any(n.get(tab) for tab in tabele))
                t["firme_nr"] = len(t["firme"])
        out["trasee"].append(t)
    return out


def masoara_firme():
    """Rândurile din fiecare tabelă, pe fiecare firmă. Cere DB.

    Numără DOUĂ feluri de tabele, fiindcă altfel jumătate din trasee ies fals la zero:
      - tabelele din schema firmei (`tenant_0NN.facturi`);
      - tabelele PARTAJATE din `public` care poartă `tenant_id` — acolo trăiesc
        `declaratii_coada` și `declaratii_depuse`, deci traseul declarației arăta
        „nicio firmă" pe o instalare cu 55 de declarații depuse.
    """
    sys.path.insert(0, RAD)
    from core import db
    db.init_pool()
    rez = {}
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, schema_name FROM public.tenants ORDER BY id")
            firme = cur.fetchall()
            cur.execute("""SELECT table_schema, table_name FROM information_schema.tables
                           WHERE table_type='BASE TABLE'""")
            prez = {}
            for sc, t in cur.fetchall():
                prez.setdefault(sc, set()).add(t)
            # tabelele partajate din public care poartă tenant_id
            cur.execute("""SELECT table_name FROM information_schema.columns
                           WHERE table_schema='public' AND column_name='tenant_id'""")
            partajate = sorted({r[0] for r in cur.fetchall()})
            pe_tenant = {}
            for t in partajate:
                cur.execute('SELECT tenant_id, count(*) FROM public."%s" GROUP BY 1' % t)
                pe_tenant[t] = dict(cur.fetchall())
            for tid, sc in firme:
                rez[sc] = {}
                for t in sorted(prez.get(sc, ())):
                    cur.execute('SELECT count(*) FROM "%s"."%s"' % (sc, t))
                    rez[sc][t] = cur.fetchone()[0]
                for t in partajate:
                    rez[sc][t] = rez[sc].get(t, 0) + pe_tenant[t].get(tid, 0)
    return rez


def scrie_tabele():
    """Regenerează `scripts/trasee_tabele.json` din bază: numele reale ale tabelelor,
    din `public` și din prima schemă de tenant. Se rulează când apare o tabelă nouă."""
    sys.path.insert(0, RAD)
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants ORDER BY id LIMIT 1")
            r = cur.fetchone()
            scheme = ["public"] + ([r[0]] if r else [])
            cur.execute("""SELECT DISTINCT table_name FROM information_schema.tables
                           WHERE table_type='BASE TABLE' AND table_schema = ANY(%s)
                           ORDER BY 1""", (scheme,))
            tab = [x[0] for x in cur.fetchall()]
    json.dump({"scheme": scheme, "tabele": tab},
              open(CALE_TABELE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("scris %s: %d tabele din %s" % (CALE_TABELE, len(tab), ", ".join(scheme)))


def main():
    if "--tabele" in sys.argv:
        scrie_tabele()
        return 0
    cu_db = "--db" in sys.argv
    d = construieste(cu_db)
    if "--json" in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0
    print("RUTE: %d · trasee: %d · rute ne-documentare: %d"
          % (d["total_rute"], len(d["trasee"]), d["nedocumentare"]))
    if d["orfane"]:
        print("\nRUTE ÎN AFARA INVENTARULUI (%d) — traseul nu le acoperă:" % len(d["orfane"]))
        for m, c in d["orfane"]:
            print("   %-6s %s" % (m, c))
    if d["dublate"]:
        print("\nRUTE ÎN DOUĂ TRASEE (%d):" % len(d["dublate"]))
        for m, c, g in d["dublate"]:
            print("   %-6s %-55s %s" % (m, c, ",".join(g)))
    print()
    cap = "%-4s %-8s %-4s %-4s %-4s %-5s %s" % ("id", "clasă", "rut", "mut", "f/r", "firme", "nume")
    print(cap)
    print("-" * len(cap))
    for t in d["trasee"]:
        print("%-4s %-8s %-4d %-4d %-4d %-5s %s"
              % (t["id"], t["clasa"], t["rute"], t["mutante"], t["fara_rol"],
                 "?" if t.get("firme_nr") is None else t.get("firme_nr", "-"), t["nume"]))
    from collections import Counter
    c = Counter(t["clasa"] for t in d["trasee"])
    print("\nCLASE: MECANIC %d · PARTIAL %d · MANUAL %d"
          % (c["MECANIC"], c["PARTIAL"], c["MANUAL"]))
    if cu_db:
        z = [t["id"] for t in d["trasee"] if t.get("firme_nr") == 0]
        n = [t["id"] for t in d["trasee"] if t.get("firme_nr") is None]
        print("TRASEE PE CARE NICIO FIRMĂ NU LE POATE EXERCITA AZI: %d — %s"
              % (len(z), " ".join(z)))
        print("TRASEE FĂRĂ TABELĂ PROPRIE (nu se poate ști din date): %d — %s"
              % (len(n), " ".join(n)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
