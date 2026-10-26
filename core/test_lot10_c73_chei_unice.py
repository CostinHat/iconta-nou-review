# -*- coding: utf-8 -*-
"""[lotul 10, deficiența C73] Cheia naturală dublată ajunge la contabil ca refuz numit, nu ca 500.

Instanța (găsită de e2e la 428): `POST /tenants/{id}/clienti` cu un CUI deja existent cădea cu **500** —
*„psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "clienti_cui_uniq" DETAIL: Key
(cui)=(RO24736200) already exists.”* Contabilul trebuie să primească „Există deja clientul <nume> cu CUI …”, cu drumul spre el.

CLASA (închisă de U2): TOATE cheile unice ale schemei unei firme — catalogul se CITEȘTE din `tenant_template.sql` (`CONSTRAINT …
UNIQUE`, `UNIQUE (…)` în `CREATE TABLE`, `ALTER TABLE … ADD CONSTRAINT … UNIQUE`, `CREATE UNIQUE INDEX`, cu predicatul indexului
parțial), nu din lista `migrare_intrare_date_garduri.UNIQUE` (care rămâne o submulțime, verificată). Două feluri de dublură:
  - valoarea scrisă de OM (CUI, cod de bare, nume de șablon, număr de factură/borderou) -> refuz numit (`chei_unice.refuza_dublura`);
  - numărul dat de APLICAȚIE (`MAX + 1`: registratura, registrele art.321, registrul-inventar, exemplarul artefactului) -> cursa se
    REIA cu numărul următor (`chei_unice.reincearca_la_dublura`), fiindcă nu e a omului.

GARD (structural): fiecare `INSERT INTO <tabel>` care scrie o coloană a unei chei (și pe care predicatul indexului parțial nu-l
exclude prin valoarea scrisă literal) și fiecare `UPDATE <tabel> SET` care atinge o coloană a cheii SAU a predicatului (sau are SET
dinamic), din `core/*.py` și `main.py` (fără teste și migrări), stă într-o funcție (cea mai din afară) care tratează dublura
(`refuza_dublura` / `reincearca_la_dublura` / ON CONFLICT / `UniqueViolation`), ori e:
  - în `LA_APELANT` — funcția de repository e tratată la apelant: FIECARE apel al ei din cod stă într-o funcție care tratează;
  - în `EXCEPTII` — cheie de sistem care nu poate dubla, cu motivul.
Plus: catalogul citit = indexurile unice reale ale unei scheme efemere (anti-vacuu al cititorului), și probe funcționale pe Postgres.

MUTAȚII: `refuza_dublura` scos din `clienti_api.creeaza_client` -> `test_gardul_cheilor_unice` și `test_client_dublat_refuz_numit`
pică; verificarea `conturi_dublate` scoasă din `solduri_api.importa` -> `test_solduri_cont_dublat_in_randuri_trimise` pică. (U2) helperul
scos din `stocuri_cv_api.set_barcode` -> gardul și `test_cod_de_bare_dublat_refuz_numit` pică; reluarea scoasă din
`registratura_api.inregistreaza` -> gardul și `test_doua_inregistrari_simultane_in_registratura` pică.
"""
import ast
import glob
import io
import os
import re
import threading
import time

import pytest

from core import db as _db
from core import migrare_intrare_date_garduri as _mig
from core import tenant_provisioning as _tp

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot10_c73"
TID = 991073

#: scrieri pe o cheie unică care NU pot dubla, fiecare cu motivul. (fișier, funcție, tabel) -> motiv
EXCEPTII = {
    # [lotul 13, 519 / 522] legăturile activului (`mf_note`: nota -> activ; `mf_linii`: rândul -> activ): le scrie numai operațiunea care
    # tocmai a creat nota / rândul, în aceeași tranzacție, o singură dată — id-ul notei / al rândului e nou (secvență), deci nu poate exista
    ("core/mf_note.py", "leaga", "mf_note"):
        "nota e creată chiar înainte, în aceeași tranzacție (`nota_operatiune_ciorna` … RETURNING id), și se leagă o singură dată de "
        "activul ei: cheia `mf_note_pkey` (inregistrare_id) nu poate dubla",
    ("core/mf_note.py", "adauga_linie", "mf_linii"):
        "rândul e inserat chiar înainte, în aceeași funcție (`INSERT INTO inregistrari_linii … RETURNING id`), și primește activul o "
        "singură dată: cheia `mf_linii_pkey` (linie_id) nu poate dubla",
    # [lotul 13, 548] vânzarea din stoc (marjă / aur), legată de ieșirea ei: rândul îl scrie numai use-case-ul care tocmai a creat nota
    ("core/repo_operatiuni.py", "vanzare_din_stoc_scrie", "vanzari_din_stoc"):
        "nota vânzării e creată chiar înainte, în aceeași tranzacție (`nota_operatiune_ciorna` … RETURNING id), și se scrie o singură "
        "dată: cheia `vanzari_din_stoc_pkey` (inregistrare_id) nu poate dubla",
    # [lotul 12, 252] facturile deschise preluate (`tip = 'preluata'`) nu cad sub nicio cheie unică a `facturi`: numerotarea emise
    # (`facturi_numar_emisa_uniq`) le scoate (`migrare_unic_numar_factura.CONDITIE`), iar cheile borderoului sunt parțiale pe `tip = 'borderou'`
    ("core/solduri_parteneri_api.py", "_scrie_documente", "facturi"):
        "factura deschisă preluată (`tip = 'preluata'`): nicio cheie unică a `facturi` nu o cuprinde (indexurile parțiale `WHERE … tip`)",
    # [lotul 12, C139] ștergerea raportului Z nevalidat desface întâi legătura stornărilor de ieșirile lui, apoi le șterge pe amândouă
    ("core/z_descarcare.py", "sterge_z", "miscari_stoc"):
        "scrie numai `anuleaza_id = NULL`: indexul `miscari_stoc_anuleaza_uq` e parțial pe `anuleaza_id IS NOT NULL`, deci rândul iese "
        "din cheie — NULL nu poate dubla",
    ("core/scan_cai_factura.py", "<modul>", "facturi"):
        "nu e scriere: exemplele de SQL ale scanerului căilor de creare a facturii (`scan_cai_factura`), text analizat, neexecutat",
    # [lotul 11, 443] `emite_factura` nu mai scrie seria după `creeaza_factura` (seria intră la INSERT, înaintea contării), deci intrarea ei a
    # ieșit din listă; `storneaza` scrie numai `storno_din_id` (cheia `facturi_borderou_storno_uniq`, parțială pe `tip = 'borderou'`)
    ("core/facturi_api.py", "storneaza", "facturi"):
        "scrierea lui `storno_din_id` pe factura de stornare abia scrisă de `creeaza_factura` (tratată): rândul e o factură (`tip = "
        "'factura'`), în afara predicatului indexului `facturi_borderou_storno_uniq` (`tip = 'borderou'`), deci nu poate dubla cheia",
    ("core/repo_contabilitate.py", "nota_cu_sursa_si_status", "inregistrari"):
        "`sursa` vine de la apelant; indexul `inregistrari_raport_z_unic` cuprinde numai sursele raportului Z (`raport_z.SURSE`), iar "
        "toți apelanții trec o sursă LITERALĂ din afara lor — verificat mecanic de `test_apelantii_notei_cu_sursa_nu_scriu_un_raport_z`",
    ("core/inchidere_an.py", "propune", "inregistrari"):
        "`sursa` = `inchidere_an.SURSA` („inchidere_an”), în afara surselor raportului Z din predicatul indexului parțial "
        "(verificat de `test_apelantii_notei_cu_sursa_nu_scriu_un_raport_z`)",
    ("core/repo_contabilitate.py", "adauga_z_cota", "rapoarte_z_cote"):
        "(nota, cotă): nota e cea abia scrisă în aceeași tranzacție (`horeca_raport_z`), iar cotele sunt cele două cote DISTINCTE ale "
        "datei (redusă, standard), câte un rând fiecare",
    ("core/repo_contabilitate.py", "adauga_z_amef", "rapoarte_z_amef"):
        "cheia primară e nota raportului Z abia scrisă în aceeași tranzacție (`horeca_import_amef`, `horeca_raport_z`): un rând pe ea",
    ("core/repo_reevaluari.py", "consemneaza", "reevaluari"):
        "`inregistrare_id` = nota CIORNĂ abia creată în aceeași tranzacție (`nota_operatiune_ciorna` / `nota_cu_sursa_si_status`): "
        "id nou din secvență, deci o singură reevaluare pe ea",
    ("core/nir_legare.py", "leaga", "nir"):
        "`nir.factura_id` se pune numai din `contare_facturi.contabilizeaza`, care blochează rândul facturii (`FOR NO KEY UPDATE`) "
        "înaintea verificării „deja contată” — două contări ale aceleiași facturi nu mai pot lega două NIR-uri (verificat de "
        "`test_contarea_blocheaza_factura`); NIR-ul ales e nelegat (`candidati`: `factura_id IS NULL`), iar re-contarea păstrează NIR-ul legat",
    ("core/nir_legare.py", "leaga_forma_noua", "nir"):
        "același lacăt pe factură ca `leaga`; în plus `WHERE factura_id IS NULL` — un NIR deja legat nu se mai atinge",
    ("core/repo_facturi.py", "actualizeaza_clasificarea", "facturi"):
        "(U3) SET dinamic din bucățile APELANTULUI: clasificarea de la validarea facturii primite (tipul furnizorului, taxarea inversă, "
        "categoria art.331, TVA la încasare, țara) — nicio coloană a cheilor facturii; verificat mecanic pe fiecare apelant de "
        "`test_clasificarea_facturii_nu_atinge_cheile`",
}

#: funcții de repository a căror dublură o tratează APELANTUL (savepoint-ul cuprinde și scrierea dinaintea lor). Gardul verifică
#: FIECARE apel al lor din cod: stă într-o funcție care tratează dublura. (fișier, funcție, tabel) -> motiv
LA_APELANT = {
    ("core/repo_contabilitate.py", "nota_amef_ciorna", "inregistrari"):
        "raportul Z importat: `uc_tenants.horeca_import_amef` (savepoint + `UniqueViolation` -> același 409 ca `_cere_z_unic`)",
    ("core/repo_contabilitate.py", "nota_horeca_z_ciorna", "inregistrari"):
        "raportul Z tastat: `uc_tenants.horeca_raport_z` (`refuza_dublura` -> același 409 ca `_cere_z_unic`)",
    ("core/repo_registru_evidenta_fiscala.py", "insert_s", "registru_fiscal_pf"):
        "`registru_evidenta_fiscala.adauga_pf` alocă `nr_crt` (MAX + 1) și scrie sub `reincearca_la_dublura` pe `registru_fiscal_pf_ordine_unica`",
    ("core/repo_registru_inventar.py", "insert_s", "registru_inventar"):
        "`registru_inventar.adauga` alocă `nr_curent` (MAX + 1) și scrie sub `reincearca_la_dublura`",
    ("core/repo_contabilitate.py", "adauga_cont_in_plan", "plan_conturi"):
        "contul adăugat de om: `uc_tenants.tenant_plan_conturi_adauga` (`refuza_dublura` pe `plan_conturi_pkey` -> același 409)",
    ("core/repo_main.py", "insert_facturi", "facturi"):
        "factura din XML: `uc_comun._factura_din_parsat` (`refuza_dublura` pe numărul emis)",
}

def _trateaza(fn):
    """Funcția tratează dublura — citit din COD, nu din text (un comentariu „foloseste ON CONFLICT” nu tratează nimic): un apel
    `refuza_dublura` / `reincearca_la_dublura`, un `except … UniqueViolation`, sau un literal SQL (nu docstring) cu `ON CONFLICT`."""
    if fn is None:
        return False
    doc = {id(x.body[0].value) for x in ast.walk(fn) if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.body
           and isinstance(x.body[0], ast.Expr) and isinstance(x.body[0].value, ast.Constant)}
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if (f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)) in ("refuza_dublura", "reincearca_la_dublura"):
                return True
        if isinstance(n, ast.ExceptHandler) and n.type is not None and _numeste(n.type, "UniqueViolation"):
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc and _are_on_conflict(n.value):
            return True
    return False


def _numeste(expr, nume):
    """Expresia (tipul unui `except`, eventual un tuplu de tipuri) numește clasa `nume` — ca nume (`UniqueViolation`) sau ca atribut
    (`psycopg2.errors.UniqueViolation`) —, citit din nodurile AST, nu din textul lor."""
    return any((isinstance(x, ast.Name) and x.id == nume) or (isinstance(x, ast.Attribute) and x.attr == nume) for x in ast.walk(expr))


def _are_on_conflict(sql):
    """Literalul SQL conține clauza `ON CONFLICT` — două cuvinte SQL consecutive, nu un sub-șir (`ON CONFLICTUL` nu e clauza)."""
    cuv = sql.upper().split()
    return ("ON", "CONFLICT") in set(zip(cuv, cuv[1:]))
_CUVINTE_SQL = {"coalesce", "upper", "lower", "btrim", "extract", "year", "from", "is", "not", "null", "and", "or", "in", "using",
                "btree", "where", "true", "false"}


def _surse():
    for f in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))) + [os.path.join(_RAD, "main.py")]:
        b = os.path.basename(f)
        if b.startswith("test_") or b.startswith("migrare_") or b == "conftest.py":
            continue
        yield os.path.relpath(f, _RAD), io.open(f, encoding="utf-8").read()


# ============================================================
#  CATALOGUL — citit din tenant_template.sql
# ============================================================
def _inchisa(s, i):
    """`s[i] == "("` -> indexul parantezei pereche."""
    n = 0
    for j in range(i, len(s)):
        n += {"(": 1, ")": -1}.get(s[j], 0)
        if n == 0:
            return j
    raise ValueError(s[i:i + 80])


def _coloane(expr):
    """Coloanele dintr-o listă / expresie de index („COALESCE(serie, ''), numar” -> serie, numar)."""
    expr = re.sub(r"'[^']*'", " ", expr)
    return tuple(w for w in re.findall(r"\b([a-z_][a-z0-9_]*)\b(?!\s*\()", expr) if w not in _CUVINTE_SQL)


def _literale(predicat):
    """Coloanele predicatului fixate pe valori literale: „stare IN ('a','b') AND mediu='prod'” -> {stare: {a, b}, mediu: {prod}}."""
    out = {}
    for c, v in re.findall(r"\b(\w+)\s+IN\s*\(([^)]*)\)", predicat, re.I):
        out[c] = set(re.findall(r"'([^']*)'", v))
    for c, v in re.findall(r"\b(\w+)\s*=\s*'([^']*)'", predicat):
        out[c] = {v}
    return out


def catalog_unice(sql=None):
    """[(tabel, constrângere, coloane, coloanele predicatului, literalele predicatului)] — toate cheile unice ale schemei firmei."""
    if sql is None:
        sql = io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    sql = re.sub(r"--[^\n]*", "", sql)
    out = {}
    for m in re.finditer(r"CREATE\s+UNIQUE\s+INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+ON\s+TENANT_PLACEHOLDER\.(\w+)\s*"
                         r"(?:USING\s+\w+\s*)?\(", sql, re.I):
        j = _inchisa(sql, m.end() - 1)
        w = re.search(r"\bWHERE\b(.*)", sql[j + 1:sql.index(";", j)], re.I | re.S)
        pred = w.group(1) if w else ""
        out[m.group(1)] = (m.group(2), m.group(1), _coloane(sql[m.end():j]), _coloane(pred), _literale(pred))
    for m in re.finditer(r"ALTER\s+TABLE\s+(?:ONLY\s+)?TENANT_PLACEHOLDER\.(\w+)\s+ADD\s+CONSTRAINT\s+(\w+)\s+UNIQUE\s*\(([^)]*)\)",
                         sql, re.I):
        out[m.group(2)] = (m.group(1), m.group(2), _coloane(m.group(3)), (), {})
    for m in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?TENANT_PLACEHOLDER\.(\w+)\s*\(", sql, re.I):
        corp = sql[m.end():_inchisa(sql, m.end() - 1)]
        for u in re.finditer(r"(?:CONSTRAINT\s+(\w+)\s+)?UNIQUE\s*\(([^)]*)\)", corp, re.I):
            cols = _coloane(u.group(2))
            nume = u.group(1) or "%s_%s_key" % (m.group(1), "_".join(cols))   # numele implicit dat de PostgreSQL
            out[nume] = (m.group(1), nume, cols, (), {})
        for u in re.finditer(r"^\s*(\w+)\s+[^,\n]*?\bUNIQUE\b(?!\s*\()", corp, re.I | re.M):   # `col tip UNIQUE`
            nume = "%s_%s_key" % (m.group(1), u.group(1))
            out[nume] = (m.group(1), nume, (u.group(1),), (), {})
        # cheia primară NATURALĂ e tot o cheie unică (`plan_conturi.simbol`, `pontaj (salariat_id, zi)`): în tabel sau pe coloană
        for u in re.finditer(r"(?:CONSTRAINT\s+(\w+)\s+)?PRIMARY\s+KEY\s*\(([^)]*)\)", corp, re.I):
            out[u.group(1) or "%s_pkey" % m.group(1)] = (m.group(1), u.group(1) or "%s_pkey" % m.group(1), _coloane(u.group(2)), (), {})
        for u in re.finditer(r"^\s*(\w+)\s+[^,\n]*?\bPRIMARY\s+KEY\b(?!\s*\()", corp, re.I | re.M):
            out["%s_pkey" % m.group(1)] = (m.group(1), "%s_pkey" % m.group(1), (u.group(1),), (), {})
    for m in re.finditer(r"ALTER\s+TABLE\s+(?:ONLY\s+)?TENANT_PLACEHOLDER\.(\w+)\s+ADD\s+CONSTRAINT\s+(\w+)\s+PRIMARY\s+KEY\s*\(([^)]*)\)",
                         sql, re.I):
        out[m.group(2)] = (m.group(1), m.group(2), _coloane(m.group(3)), (), {})
    # cheia primară SURogat (`id` din secvență) nu se dublează din cod: nicio scriere nu-și alege `id`-ul (firma_profil `id = 1` e rândul
    # unic al firmei, scris la creare)
    return sorted((v for v in out.values() if v[2] != ("id",)), key=lambda x: (x[0], x[1]))


def _intrare(u):
    """Forma comună: (tabel, constrângere, coloane, coloanele predicatului, literalele predicatului). Primește și forma veche
    `(tabel, constrângere, "col1, col2")` a listei `migrare_intrare_date_garduri.UNIQUE`."""
    if len(u) == 3:
        return u[0], u[1], tuple(x.strip() for x in u[2].split(",")), (), {}
    return u


# ============================================================
#  SCANERUL — scrierile din cod pe tabelele cu chei unice
# ============================================================
def _valori_insert(txt, start):
    """Lista valorilor din `VALUES (…)` care urmează după `start` (despărțite la virgulele de pe primul nivel), sau None."""
    m = re.compile(r"\s*VALUES\s*\(", re.I).match(txt, start)
    if not m:
        return None
    j = _inchisa(txt, m.end() - 1)
    val, nivel, cur = [], 0, ""
    for ch in txt[m.end():j]:
        if ch == "," and nivel == 0:
            val.append(cur.strip())
            cur = ""
            continue
        nivel += {"(": 1, ")": -1}.get(ch, 0)
        cur += ch
    return val + [cur.strip()]


def _exclusa_de_predicat(cols_insert, valori, literale):
    """INSERT-ul scrie LITERAL, pe o coloană a predicatului, o valoare din afara lui -> rândul nu intră în indexul parțial."""
    if not literale or valori is None or len(valori) != len(cols_insert):
        return False
    for c, v in zip(cols_insert, valori):
        if c in literale and re.fullmatch(r"'[^']*'", v) and v.strip("'") not in literale[c]:
            return True
    return False


def bucati_set(fn):
    """(U3) Coloanele bucăților LITERALE de SET din funcție („nume = %s”, `"tert_tara=%s"`): un SET dinamic se compune din ele."""
    if fn is None:
        return set()
    return {m.group(1) for x in ast.walk(fn) if isinstance(x, ast.Constant) and isinstance(x.value, str)
            for m in [re.fullmatch(r"\s*(\w+)\s*=\s*%s\s*", x.value)] if m}


def _set_inchis_fara_cheie(fn, coloane):
    b = bucati_set(fn)
    return bool(b) and not (b & set(coloane))


def scrieri_pe_chei(sursa, cale, unice):
    """[(cale, functie, tabel, fel, tratata)] — fiecare INSERT/UPDATE pe un tabel cu cheie unică care poate dubla cheia.
    INSERT fără nicio coloană a cheii (cheia rămâne NULL, deci distinctă), INSERT pe care predicatul indexului parțial îl exclude și
    UPDATE care nu atinge nici cheia, nici predicatul nu pot dubla nimic și nu se cer. Funcția raportată (și cea în care se caută
    tratarea) e cea mai din afară: o închidere `_scrie` chemată de `reincearca_la_dublura` e a funcției care o cheamă."""
    if "INSERT" not in sursa and "UPDATE" not in sursa:
        return []
    unice = [_intrare(u) for u in unice]
    arbore = ast.parse(sursa)
    functii = [n for n in ast.walk(arbore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

    def functia(lin):
        c = [n for n in functii if n.lineno <= lin <= n.end_lineno]
        return max(c, key=lambda n: n.end_lineno - n.lineno) if c else None

    # docstringurile (modul, clasă, funcție) descriu, nu scriu: un exemplu de `INSERT` într-un docstring nu e o scriere
    doc = {id(x.body[0].value) for x in ast.walk(arbore)
           if isinstance(x, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and x.body
           and isinstance(x.body[0], ast.Expr) and isinstance(x.body[0].value, ast.Constant)}
    out, vazute = [], set()
    for n in ast.walk(arbore):
        if id(n) in doc or (isinstance(n, ast.Constant) and not isinstance(n.value, str)):
            continue
        if not isinstance(n, (ast.JoinedStr, ast.Constant, ast.BinOp)):
            continue
        txt = re.sub(r"\s+", " ", " ".join(x.value for x in ast.walk(n) if isinstance(x, ast.Constant) and isinstance(x.value, str)))
        for tabel, _c, chei, pred, literale in unice:
            fel, on_conflict = None, False
            # (U3) calificativul de schemă se termină în „.” (`public.`, `{s}.`, `%s.`) sau e prefixul `%s` („schema.” dat de apelant):
            # altfel `user_tenants` ar fi citit ca `tenants`
            m = re.search(r"INSERT\s+INTO\s+(?:[\"\w{}%]*\.|%s)?\"?" + tabel + r"\b\"?\s*(\(([^)]*)\))?", txt, re.I)
            # lista de coloane: cu o coloană a cheii, dinamică („(%s)”) sau absentă -> poate scrie cheia
            if m and (m.group(2) is None or "%s" in m.group(2) or any(re.search(r"\b%s\b" % k, m.group(2)) for k in chei)):
                cols_insert = [x.strip() for x in m.group(2).split(",")] if m.group(2) else []
                if not _exclusa_de_predicat(cols_insert, _valori_insert(txt, m.end()), literale):
                    fel = "INSERT"
                    # (U3) instrucțiunea însăși are `ON CONFLICT` (corpul unei funcții de trigger dintr-o constantă de modul)
                    on_conflict = bool(re.search(r"\bON\s+CONFLICT\b", txt[m.end():].split(";")[0], re.I))
            fn = functia(n.lineno)
            u = re.search(r"UPDATE\s+(?:[\"\w{}%]*\.|%s)?\"?" + tabel + r"\"?\s+SET\s+(.*?)(\bWHERE\b|$)", txt, re.I)
            # SET dinamic: „SET %s” sau lista lipită din afara literalului („SET " + ", ".join(sets)`, `f"… SET {seturi} WHERE"`) — corpul
            # lui SET rămâne gol în textul literalelor (U3: `auth_api.actualizeaza_cabinet` scria `cui` așa, nevăzut). Nu se cere numai
            # când funcția își compune lista din bucăți LITERALE („nume = %s”) și niciuna nu e o coloană a cheii sau a predicatului.
            dinamic = u is not None and (u.group(1).lstrip().startswith("%s") or not u.group(1).strip())
            if u and (any(re.search(r"\b%s\s*=" % k, u.group(1)) for k in chei + pred)
                      or (dinamic and not _set_inchis_fara_cheie(fn, chei + pred))):
                fel = "UPDATE"
            if not fel:
                continue
            cheie = (tabel, fn.name if fn else "<modul>", fel, n.lineno)
            if cheie in vazute:
                continue
            vazute.add(cheie)
            out.append((cale, fn.name if fn else "<modul>", tabel, fel, on_conflict or _trateaza(fn)))
    return out


def apeluri(sursa, modul, functie):
    """[(funcția apelantă cea mai din afară, tratată?)] pentru fiecare apel `<alias>.functie(…)` al funcției din `core/<modul>.py`
    (aliasul citit din importurile fișierului: `from core import modul as alias`, `import core.modul as alias`)."""
    arbore = ast.parse(sursa)
    aliasuri = set()
    for n in ast.walk(arbore):
        if isinstance(n, ast.ImportFrom) and n.module == "core":
            aliasuri |= {a.asname or a.name for a in n.names if a.name == modul}
        elif isinstance(n, ast.Import):
            aliasuri |= {a.asname for a in n.names if a.name == "core." + modul and a.asname}
    if not aliasuri:
        return []
    functii = [n for n in ast.walk(arbore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    out = []
    for n in ast.walk(arbore):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == functie
                and isinstance(n.func.value, ast.Name) and n.func.value.id in aliasuri):
            c = [f for f in functii if f.lineno <= n.lineno <= f.end_lineno]
            fn = max(c, key=lambda f: f.end_lineno - f.lineno) if c else None
            out.append((fn.name if fn else "<modul>", _trateaza(fn)))
    return out


def test_scannerul_vede_o_scriere_netratata():
    """Anti-vacuu al instrumentului: o funcție sintetică cu INSERT netratat e găsită și marcată netratată; una cu `refuza_dublura`,
    tratată; un INSERT fără coloana cheii nu se cere."""
    sursa = ('def rau(cur):\n    cur.execute("INSERT INTO clienti (nume, cui) VALUES (%s,%s)", ("A", "1"))\n'
             'def bun(cur):\n    with _chei.refuza_dublura(cur, ("clienti_cui_uniq",), None):\n'
             '        cur.execute("INSERT INTO clienti (nume, cui) VALUES (%s,%s)", ("A", "1"))\n'
             'def fara_cheie(cur):\n    cur.execute(f"INSERT INTO {s}.articole (denumire, um) VALUES (%s,%s)", ("A", "buc"))\n'
             'def editare(cur, seturi):\n    cur.execute("UPDATE clienti SET %s WHERE id = %%s" % seturi, [])\n'
             'def dinamic(cur, cols):\n    cur.execute("INSERT INTO clienti (%s) VALUES (%s)" % cols, [])\n')
    r = {(f, t, fel): ok for _c, f, t, fel, ok in scrieri_pe_chei(sursa, "x.py", _mig.UNIQUE)}
    assert r == {("rau", "clienti", "INSERT"): False, ("bun", "clienti", "INSERT"): True, ("editare", "clienti", "UPDATE"): False,
                 ("dinamic", "clienti", "INSERT"): False}, r


def test_scannerul_vede_indexul_partial_si_inchiderea():
    """(U2) Anti-vacuu pe formele noi: predicatul indexului parțial exclude INSERT-ul cu o valoare literală din afara lui (sursa
    „casa” nu e raport Z), dar nu și pe cel cu valoarea parametru; un UPDATE pe coloana predicatului (`stare`) se cere; o închidere
    `_scrie` sub `reincearca_la_dublura` e tratată și raportată pe funcția care o cheamă."""
    sursa = ('def casa(cur):\n    cur.execute("INSERT INTO inregistrari (data, numar, sursa) VALUES (%s, %s, \'casa\')", [])\n'
             'def z(cur, sursa):\n    cur.execute("INSERT INTO inregistrari (data, numar, sursa) VALUES (%s, %s, %s)", [])\n'
             'def z_lit(cur):\n    cur.execute("INSERT INTO inregistrari (data, numar, sursa) VALUES (%s, %s, \'amef\')", [])\n'
             'def stare(cur):\n    cur.execute("UPDATE efactura_trimiteri SET stare=%s WHERE id=%s", [])\n'
             'def mesaj(cur):\n    cur.execute("UPDATE efactura_trimiteri SET error_message=%s WHERE id=%s", [])\n'
             'def numar(cur):\n    def _scrie():\n        cur.execute("INSERT INTO registratura (an, numar) VALUES (%s,%s)", [])\n'
             '    return _chei.reincearca_la_dublura(cur, ("registratura_an_numar_unic",), _scrie, None)\n')
    r = {(f, t, fel): ok for _c, f, t, fel, ok in scrieri_pe_chei(sursa, "x.py", catalog_unice())}
    assert r == {("z", "inregistrari", "INSERT"): False, ("z_lit", "inregistrari", "INSERT"): False,
                 ("stare", "efactura_trimiteri", "UPDATE"): False, ("numar", "registratura", "INSERT"): True}, r
    # apelurile unei funcții de repository, prin aliasul importului
    s2 = ('from core import repo_x as _r\ndef bun(cur):\n    with _chei.refuza_dublura(cur, (), None):\n        _r.scrie(cur)\n'
          'def rau(cur):\n    _r.scrie(cur)\n')
    assert sorted(apeluri(s2, "repo_x", "scrie")) == [("bun", True), ("rau", False)]


def test_scannerul_formele_u3():
    """(U3) Anti-vacuu pe formele găsite pe schema `public`: `user_tenants` nu e citit ca `tenants`; SET-ul lipit din bucăți
    (`"… SET " + ", ".join(sets)`) se cere când o bucată atinge cheia (`cui = %s`), nu și când toate sunt în afara ei; prefixul `%s`
    al schemei; `ON CONFLICT` în instrucțiunea dintr-o constantă de modul (corpul unui trigger) tratează."""
    cat = [("tenants", "tenants_schema_name_key", ("schema_name",), (), {}), ("accounting_firms", "accounting_firms_cui_key", ("cui",), (), {}),
           ("users", "users_email_key", ("email",), (), {}), ("firma_tip", "firma_tip_pkey", ("tenant_id",), (), {})]
    sursa = ('def leaga(cur):\n    cur.execute("INSERT INTO user_tenants VALUES (%s, %s)", (1, 2))\n'
             'def cabinet(cur, nume, cui):\n    sets = []\n    sets.append("nume = %s")\n    sets.append("cui = %s")\n'
             '    cur.execute("UPDATE public.accounting_firms SET " + ", ".join(sets) + " WHERE id = %s", [])\n'
             'def profil(cur):\n    sets = ["nume = %s", "prenume = %s"]\n'
             '    cur.execute("UPDATE public.users SET " + ", ".join(sets) + " WHERE id = %s", [])\n'
             'def prefix(cur, s):\n    cur.execute("UPDATE %susers SET email=%%s WHERE id=%%s" % s, [])\n'
             'DDL = """CREATE FUNCTION f() AS $$ BEGIN INSERT INTO public.firma_tip (tenant_id) VALUES (1) ON CONFLICT (tenant_id) DO NOTHING; '
             'END $$"""\n')
    r = {(f, t, fel): ok for _c, f, t, fel, ok in scrieri_pe_chei(sursa, "x.py", cat)}
    assert r == {("cabinet", "accounting_firms", "UPDATE"): False, ("prefix", "users", "UPDATE"): False,
                 ("<modul>", "firma_tip", "INSERT"): True}, r


def test_catalogul_e_indexurile_reale_ale_schemei():
    """Cititorul catalogului nu pierde nicio cheie: pe o schemă efemeră din `tenant_template.sql`, indexurile unice (cu cheile primare
    naturale, fără cea surogat `id`) sunt EXACT cele citite din text. Și lista veche `migrare_intrare_date_garduri.UNIQUE` e cuprinsă în catalog."""
    cat = catalog_unice()
    nume = {c[1] for c in cat}
    assert {u[1] for u in _mig.UNIQUE} <= nume, sorted({u[1] for u in _mig.UNIQUE} - nume)
    assert len(cat) >= 47, len(cat)   # 39 chei unice + 8 chei primare naturale la 21.10.2026 (U2): un cititor stricat ar da mai puțin
    if not _db_ok():
        pytest.skip("DB indisponibil")
    sablon = io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    sch = SCH + "_cat"
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
            cur.execute(_tp.parametrizeaza_template(sablon, sch))
            cur.execute("SELECT ci.relname, ct.relname, i.indisprimary, pg_get_indexdef(i.indexrelid) FROM pg_index i "
                        "JOIN pg_class ci ON ci.oid = i.indexrelid JOIN pg_class ct ON ct.oid = i.indrelid "
                        "JOIN pg_namespace n ON n.oid = ct.relnamespace WHERE n.nspname = %s AND i.indisunique", (sch,))
            # cheile primare: numai cele naturale (cea surogat, `(id)`, nu e în catalog — vezi `catalog_unice`)
            reale = {(t, ix) for ix, t, pk, d in cur.fetchall() if not (pk and d.endswith("(id)"))}
        c.rollback()
    citite = {(c[0], c[1]) for c in cat}
    print("C73 catalog:", len(citite), "citite /", len(reale), "în bază")
    assert citite == reale, ("citite, nu în bază: %s; în bază, necitite: %s" % (sorted(citite - reale), sorted(reale - citite)))


def test_gardul_cheilor_unice():
    """Fiecare scriere a unei chei unice din catalog tratează dublura, ori e tratată la apelant, ori e excepție cu motiv."""
    gasite = []
    for cale, sursa in _surse():
        gasite += scrieri_pe_chei(sursa, cale, catalog_unice())
    print("C73 scrieri pe chei:", len(gasite))
    for g in gasite:
        print("  ", g)
    netratate = [g for g in gasite if not g[4] and (g[0], g[1], g[2]) not in EXCEPTII and (g[0], g[1], g[2]) not in LA_APELANT]
    assert not netratate, ("scriere pe o cheie unică fără tratarea dublurii (refuza_dublura / reincearca_la_dublura / ON CONFLICT), "
                           "deci 500 la dublură: %s" % netratate)
    # anti-vacuu: drumurile cunoscute sunt văzute (instanța C73 și câte una din fiecare familie reparată)
    vazute = {(g[0], g[1], g[2]) for g in gasite}
    for asteptat in [("core/clienti_api.py", "creeaza_client", "clienti"), ("core/clienti_api.py", "actualizeaza_client", "clienti"),
                     ("core/solduri_api.py", "importa", "solduri_initiale"),
                     ("core/solduri_parteneri_api.py", "importa", "solduri_parteneri"),
                     ("core/asociati_import_api.py", "importa", "asociati"), ("core/repo_mijloace_fixe.py", "adauga", "mijloace_fixe"),
                     ("core/repo_mijloace_fixe.py", "adauga_cu_reevaluare", "mijloace_fixe"),
                     ("core/mijloace_fixe_import_api.py", "importa", "mijloace_fixe"),
                     ("core/stat_plata_emis.py", "_insereaza", "state_plata"), ("core/spv_receive.py", "importa_mesaj", "efactura_primite"),
                     ("core/salariati_api.py", "creeaza_salariat", "salariati"), ("core/salariati_api.py", "actualizeaza_salariat", "salariati"),
                     ("core/asociati_import_api.py", "arhiveaza_pentru_cesiune", "asociati_istoric"),
                     # U2
                     ("core/stocuri_cv_api.py", "set_barcode", "articole"), ("core/contracte_api.py", "salveaza_sablon", "contracte_sabloane"),
                     ("core/rapoarte_comerciale_api.py", "salveaza_varianta", "rapoarte_salvate"),
                     ("core/registratura_api.py", "inregistreaza", "registratura"), ("core/registre_art321.py", "adauga", "registre_art321"),
                     ("core/casa_api.py", "storneaza", "casa_operatiuni"), ("core/repo_efactura.py", "rezultatul_trimiterii", "efactura_trimiteri"),
                     ("core/etransport_send.py", "trimite", "etransport_trimiteri"), ("core/spv_poll.py", "_seteaza", "efactura_trimiteri"),
                     ("core/stocuri_api.py", "adauga_nir", "nir"), ("core/stocuri_anulare.py", "storneaza", "miscari_stoc"),
                     ("core/stocuri_cv_api.py", "retur_la_stornare", "miscari_stoc"), ("core/facturi_api.py", "creeaza_factura", "facturi"),
                     ("core/artefacte.py", "pastreaza", "artefacte_produse"),
                     ("core/repo_salariati.py", "inlocuieste_suspendari", "suspendari_contract")]:
        assert asteptat in vazute, (asteptat, sorted(vazute))
    # excepțiile și cele tratate la apelant nu se învechesc: fiecare încă există
    for e in list(EXCEPTII) + list(LA_APELANT):
        assert e in vazute, ("intrare fără scriere în cod — de scos", e)


def test_tratate_la_apelant():
    """Funcțiile de repository din `LA_APELANT`: FIECARE apel al lor din cod stă într-o funcție care tratează dublura — un apelant
    nou, netratat, ar aduce înapoi 500-ul."""
    for (fis, functie, _t), _motiv in LA_APELANT.items():
        modul = os.path.basename(fis)[:-3]
        gasite = []
        for cale, sursa in _surse():
            gasite += [(cale,) + a for a in apeluri(sursa, modul, functie)]
        print("C73 apelanții lui %s.%s:" % (modul, functie), gasite)
        assert gasite, ("niciun apel al lui %s.%s — de scos din LA_APELANT" % (modul, functie))
        assert all(ok for _c, _f, ok in gasite), ("apelant care nu tratează dublura: %s" % [g for g in gasite if not g[2]])


def test_apelantii_notei_cu_sursa_nu_scriu_un_raport_z():
    """Premisa excepțiilor `nota_cu_sursa_si_status` / `inchidere_an.propune`: sursa notei e un literal din afara surselor raportului Z
    (`raport_z.SURSE`, predicatul indexului `inregistrari_raport_z_unic`)."""
    from core import inchidere_an, raport_z
    assert inchidere_an.SURSA not in raport_z.SURSE
    gasite = []
    for cale, sursa in _surse():
        arbore = ast.parse(sursa)
        for n in ast.walk(arbore):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "nota_cu_sursa_si_status":
                arg = n.args[4] if len(n.args) > 4 else None
                gasite.append((cale, n.lineno, arg.value if isinstance(arg, ast.Constant) else None))
    print("C73 nota_cu_sursa_si_status:", gasite)
    assert gasite and all(s is not None and s not in raport_z.SURSE for _c, _l, s in gasite), gasite


def test_contarea_blocheaza_factura():
    """Premisa excepțiilor `nir_legare.leaga*`: `contare_facturi.contabilizeaza` citește factura cu lacăt (`FOR NO KEY UPDATE`)."""
    from core import contare_facturi
    import inspect
    sursa = inspect.getsource(contare_facturi.contabilizeaza)
    assert re.search(r"SELECT \* FROM %sfacturi WHERE id=%%s FOR NO KEY UPDATE", sursa), "contarea nu mai blochează factura"


# ============================================================
#  PROBE FUNCȚIONALE — schemă efemeră
# ============================================================
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


def _cnp(b):
    """CNP valid din primele 12 cifre (algoritmul din CLAUDE.md, cheia 279146358279)."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    r = sum(int(b[i]) * ch[i] for i in range(12)) % 11
    return b + str(1 if r == 10 else r)


CNP_A, CNP_B = _cnp("180010141001"), _cnp("285020241002")
CUI_ALFA, CUI_BETA = "RO24736200", "14399840"   # cifra de control verificată (algoritmul CUI din CLAUDE.md)


@pytest.fixture()
def firma(monkeypatch):
    sablon = io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(sablon, SCH))
        c.commit()
    from core import auth_api
    monkeypatch.setattr(auth_api, "schema_tenant", lambda c, uid, tid: SCH if tid == TID else None)
    try:
        yield
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


class _Corp:
    def __init__(self, **k):
        self.k = k

    def model_dump(self):
        return dict(self.k)


def _numar(tabel):
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM %s" % tabel)
            return cur.fetchone()[0]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_client_dublat_refuz_numit(firma):
    from core import erori, uc_tenants
    ctx = {"uid": 1}
    r = uc_tenants.client_creeaza(TID, _Corp(nume="ALFA SRL", cui=CUI_ALFA), ctx)
    with pytest.raises(erori.Conflict) as ex:
        uc_tenants.client_creeaza(TID, _Corp(nume="ALFA DUBLURA", cui=CUI_ALFA), ctx)
    d = ex.value.detaliu
    print("C73 client dublat:", d)
    # comanda C73: „Există deja clientul <nume> cu CUI …” — și drumul spre el (fișa existentă)
    # [lotul 11, decizia Costin 10.3] CUI-ul se păstrează fără „RO” (`RO24736200` scris -> `24736200` păstrat), deci refuzul îl numește așa
    assert d["mesaj"].startswith("Există deja clientul ALFA SRL cu CUI-ul 24736200"), d
    assert d["existent"] == {"client_id": r["client_id"], "nume": "ALFA SRL"}, d
    assert "UniqueViolation" not in d["mesaj"] and "clienti_cui_uniq" not in d["mesaj"], d   # fără codul intern al bazei
    assert _numar("clienti") == 1                       # a doua fișă nu s-a scris
    # editarea: CUI-ul altui client -> același refuz, fișa editată rămâne neatinsă
    b = uc_tenants.client_creeaza(TID, _Corp(nume="BETA SRL", cui=CUI_BETA), ctx)
    with pytest.raises(erori.Conflict) as ex:
        uc_tenants.client_actualizeaza(TID, b["client_id"], _Corp(cui=CUI_ALFA), ctx)
    assert ex.value.detaliu["existent"]["client_id"] == r["client_id"], ex.value.detaliu
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            cur.execute("SELECT cui FROM clienti WHERE id = %s", (b["client_id"],))
            assert cur.fetchone()[0] == CUI_BETA


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_solduri_cont_dublat_in_randuri_trimise(firma):
    from core import solduri_api, solduri_parteneri_api
    with pytest.raises(ValueError) as ex:
        with _db.get_conn(SCH) as c:
            solduri_api.importa(c, [{"cont": "5121", "debit": 100, "credit": 0}, {"cont": "5121", "debit": 50, "credit": 0},
                                    {"cont": "1012", "debit": 0, "credit": 150}], "2025-12-31")
    # refuzul numit al contului dublat, cu contul (constanta mesajului, nu o copie a textului)
    assert type(ex.value) is ValueError and str(ex.value) == solduri_api.MESAJ_CONT_DUBLAT % "5121", repr(ex.value)
    dublati = [{"cont": "4111", "cui": "14399840", "denumire": "BETA", "debit": 10, "credit": 0},
               {"cont": "4111", "cui": "14399840", "denumire": "BETA", "debit": 5, "credit": 0}]
    with pytest.raises(ValueError) as ex:
        with _db.get_conn(SCH) as c:
            solduri_parteneri_api.importa(c, dublati, "2025-12-31")
    # [lotul 13, deficiența 582, comanda Costin 13.1, verbatim: „Verificarea dublurilor oprește tot înainte de celelalte verificări; restul
    # greșelilor apar abia la reîncărcare.”] Perechea dublată se respinge acum pe rânduri, în `verifica_randuri`, cu celelalte verificări
    # (regula `partener_dublat`, ambele rânduri numite); fără niciun rând bun, refuzul întreg le spune pe amândouă — tot refuz numit, nu 500
    assert ([(e["rand"], e["regula"]) for e in solduri_parteneri_api.verifica_randuri(dublati)[0]] == [(2, "partener_dublat"), (3, "partener_dublat")]
            and "rândul 3" in str(ex.value) and "rândul 2" in str(ex.value) and "4111" in str(ex.value)), repr(ex.value)
    assert _numar("solduri_initiale") == 0 and _numar("solduri_parteneri") == 0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_doua_salvari_simultane_ale_balantei(firma):
    """Cursa: T1 a scris balanța (necomisă); T2 așteaptă la DELETE; T1 comite; T2 scrie același cont -> refuz numit, nu 500."""
    from core import chei_unice, solduri_api
    rand = [{"cont": "5121", "debit": 100, "credit": 0}, {"cont": "1012", "debit": 0, "credit": 100}]
    cm1 = _db.get_conn(SCH)
    c1 = cm1.__enter__()
    solduri_api.importa(c1, rand, "2025-12-31", inlocuieste=True)
    rez = {}

    def t2():
        try:
            with _db.get_conn(SCH) as c2:
                solduri_api.importa(c2, rand, "2025-12-31", inlocuieste=True)
            rez["r"] = "scris"
        except Exception as e:  # noqa: BLE001
            rez["r"] = e

    t = threading.Thread(target=t2)
    t.start()
    with _db.get_conn() as c:   # T2 a ajuns să aștepte lacătul lui T1
        with c.cursor() as cur:
            for _ in range(100):
                cur.execute("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock' AND query LIKE 'DELETE FROM solduri_initiale%%'")
                if cur.fetchone()[0]:
                    break
                c.rollback()
                time.sleep(0.1)
    cm1.__exit__(None, None, None)
    t.join(20)
    print("C73 cursa:", repr(rez.get("r")))
    assert isinstance(rez.get("r"), chei_unice.CheieDublata), rez
    assert rez["r"].valoare == "5121", rez["r"].detaliu()        # contul dublat, citit din detaliul violării (nu din text)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mijloc_fix_cod_implicit_liber_si_cod_dublat_numit(firma):
    from core import chei_unice, repo_mijloace_fixe as rm
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            # înainte: a doua licență primea același „NEC-LIC” -> 500. Acum primul cod liber.
            assert rm.cod_liber(cur, SCH, "NEC-LIC") == "NEC-LIC"
            rm.adauga(cur, SCH, rm.cod_liber(cur, SCH, "NEC-LIC"), "Licenta 1", "205", "2805", 1000, 12, "2025-01-10")
            assert rm.cod_liber(cur, SCH, "NEC-LIC") == "NEC-LIC-2"
            rm.adauga(cur, SCH, rm.cod_liber(cur, SCH, "NEC-LIC"), "Licenta 2", "205", "2805", 1000, 12, "2025-01-10")
            assert rm.cod_liber(cur, SCH, "NEC-LIC") == "NEC-LIC-3"
            with pytest.raises(chei_unice.CheieDublata) as ex:   # codul scris de om, deja folosit
                rm.adauga_cu_reevaluare(cur, SCH, "NEC-LIC", "Alt activ", "2131", "2813", 500, 0, 24, "2025-01-10", "liniara")
            d = ex.value.detaliu()
            assert (d["cod"], d["valoare"], d["existent"]["denumire"]) == ("CHEIE_DUBLATA", "NEC-LIC", "Licenta 1"), d   # drumul spre cel existent
            assert d["erori_campuri"] == [{"camp": "cod", "mesaj": str(ex.value)}], d
            cur.execute("SELECT count(*) FROM mijloace_fixe")   # tranzacția a rămas utilizabilă (savepoint), nimic în plus
            assert cur.fetchone()[0] == 2


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cnp_salariat_dublat_la_creare_si_la_editare(firma):
    from core import salariati_api as sa
    kw = dict(prenume="I", data_angajare="2026-01-01", salariu_brut=4050, tip_norma="intreaga", functie_baza=True,
              scutit_contrib_minim=False, cor="522101")
    with _db.get_conn(SCH) as c:
        sa.creeaza_salariat(c, nume="POP", cnp=CNP_A, **kw)
        sb = sa.creeaza_salariat(c, nume="ION", cnp=CNP_B, **kw)["salariat_id"]
    for f in (lambda c: sa.creeaza_salariat(c, nume="DUBLU", cnp=CNP_A, **kw), lambda c: sa.actualizeaza_salariat(c, sb, cnp=CNP_A)):
        with pytest.raises(ValueError) as ex:
            with _db.get_conn(SCH) as c:
                f(c)
        assert "Există deja un salariat cu CNP-ul %s" % CNP_A in str(ex.value), repr(ex.value)
        assert [x["camp"] for x in ex.value.erori_campuri] == ["cnp"], ex.value.erori_campuri
    assert _numar("salariati") == 2


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_exemplar_de_stat_emis_de_doua_ori(firma):
    from core import chei_unice, stat_plata_emis as spe
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO salariati (nume, prenume, cnp) VALUES ('POP', 'ANA', %s) RETURNING id", (CNP_B,))
            sid = cur.fetchone()[0]
        r = {"id": sid, "nume": "POP ANA", "brut": 4050}
        spe._insereaza(c, SCH, r, 2099, 1, 1, "1")
        with pytest.raises(chei_unice.CheieDublata) as ex:
            spe._insereaza(c, SCH, r, 2099, 1, 1, "1")
        # cheia dublată, citită din detaliul violării (salariat_id, luna, exemplar) — nu din textul refuzului
        assert ex.value.valoare == "%d, 2099-01-01, 1" % sid, ex.value.detaliu()


def test_alta_constrangere_nu_se_traduce():
    """Helperul traduce NUMAI constrângerile declarate: o altă violare trece neatinsă (nu inventăm un refuz)."""
    import psycopg2
    from core import chei_unice

    class _E(psycopg2.errors.UniqueViolation):
        pass

    class _Cur:
        def __init__(self):
            self.sql = []

        def execute(self, q, *a):
            self.sql.append(q)

    cur = _Cur()
    with pytest.raises(psycopg2.errors.UniqueViolation):
        with chei_unice.refuza_dublura(cur, ("clienti_cui_uniq",), lambda c, e: chei_unice.CheieDublata("nu")):
            raise _E("alta")
    assert cur.sql == ["SAVEPOINT cheie_unica"], cur.sql


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_doua_licente_din_operatiuni_nu_mai_cad(firma, monkeypatch):
    """Drumul omului: Operațiuni → „Achiziție necorporală” n-are câmp de cod; înainte, a doua licență primea același „NEC-LIC” și
    ruta cădea cu 500 pe `mijloace_fixe_cod_uniq`. Acum fiecare primește primul cod liber."""
    from core import anaf_api, uc_tenants
    monkeypatch.setattr(anaf_api, "platitor_tva_freeze", lambda cui, fallback=None: True)
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, tip_decont, regim_fiscal, tip_firma) "
                        "VALUES (1, 'C73 TEST SRL', '14399840', true, 'L', 'profit', 'srl')" % SCH)
        c.commit()
    for nr in ("F1", "F2"):
        uc_tenants.achizitie_necorporala(TID, {"data": "2026-10-05", "denumire": "Licenta " + nr, "valoare": "1000", "tip": "licenta",
                                               "dnf_luni": 12, "furnizor_cui": "24736200", "furnizor_nume": "ALFA SRL",
                                               "numar": nr, "cota": 21}, {"uid": 1})
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            cur.execute("SELECT cod, denumire FROM mijloace_fixe ORDER BY id")
            r = cur.fetchall()
    print("C73 necorporale:", r)
    assert r == [("NEC-LIC", "Licenta F1"), ("NEC-LIC-2", "Licenta F2")], r


# ============================================================
#  U2 — drumurile rămase după U: probe funcționale pe schema efemeră
# ============================================================
def _executa(sql, *arg):
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            cur.execute(sql, arg)
            r = cur.fetchall() if cur.description else None
        c.commit()
    return r


def _asteapta_lacat(fragment):
    """Până când o cerere ajunge să aștepte un lacăt pe o interogare care conține `fragment` (cursa reală, nu simulată)."""
    with _db.get_conn() as c:
        with c.cursor() as cur:
            for _ in range(100):
                cur.execute("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock' AND query LIKE %s",
                            ("%" + fragment + "%",))
                if cur.fetchone()[0]:
                    return True
                c.rollback()
                time.sleep(0.1)
    return False


def _cursa(prima, a_doua, fragment):
    """T1 rulează `prima(c1)` fără să comită; T2 rulează `a_doua(c2)` pe alt fir (și ajunge să aștepte lacătul lui T1); T1 comite.
    Întoarce ce a întors T2, sau excepția lui."""
    cm1 = _db.get_conn(SCH)
    c1 = cm1.__enter__()
    r1 = prima(c1)
    rez = {}

    def t2():
        try:
            with _db.get_conn(SCH) as c2:
                rez["r"] = a_doua(c2)
        except Exception as e:  # noqa: BLE001
            rez["r"] = e

    t = threading.Thread(target=t2)
    t.start()
    assert _asteapta_lacat(fragment), "a doua cerere n-a ajuns să aștepte lacătul primei — cursa nu s-a produs"
    cm1.__exit__(None, None, None)
    t.join(20)
    return r1, rez.get("r")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cod_de_bare_dublat_refuz_numit(firma):
    """Comanda U2 pct.1: „Codul de bare X e deja la articolul …”, pe câmpul `barcode` (422), nu 500 pe `articole_barcode_uniq`."""
    from core import erori, uc_tenants
    a, b = [r[0] for r in _executa("INSERT INTO articole (denumire, um) VALUES ('Marfa A', 'buc'), ('Marfa B', 'buc') RETURNING id")]
    ctx = {"uid": 1}
    assert uc_tenants.cv_barcode_set(TID, a, {"barcode": " 5940000000017 "}, ctx) == {"articol_id": a, "barcode": "5940000000017"}
    with pytest.raises(erori.DateInvalide) as ex:
        uc_tenants.cv_barcode_set(TID, b, {"barcode": "5940000000017"}, ctx)
    d = ex.value.detaliu
    print("C73/U2 cod de bare dublat:", d)
    assert d["mesaj"].startswith("Codul de bare 5940000000017 e deja la articolul Marfa A."), d
    assert d["erori_campuri"] == [{"camp": "barcode", "mesaj": d["mesaj"]}], d          # lângă câmp (G10)
    assert d["existent"] == {"articol_id": a, "denumire": "Marfa A"}, d
    assert "articole_barcode" not in d["mesaj"] and "UniqueViolation" not in d["mesaj"], d   # fără codul intern al bazei
    assert _executa("SELECT barcode FROM articole WHERE id = %s", b) == [(None,)]       # articolul B rămâne neatins
    # același articol, același cod: nu e dublură; ștergerea codului (gol) eliberează valoarea
    assert uc_tenants.cv_barcode_set(TID, a, {"barcode": "5940000000017"}, ctx)["barcode"] == "5940000000017"
    assert uc_tenants.cv_barcode_set(TID, a, {"barcode": ""}, ctx)["barcode"] is None
    assert uc_tenants.cv_barcode_set(TID, b, {"barcode": "5940000000017"}, ctx)["barcode"] == "5940000000017"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_doua_inregistrari_simultane_in_registratura(firma):
    """Comanda U2 pct.4: numărul de înregistrare îl dă aplicația (MAX + 1), deci cursa se REIA cu numărul următor — nu refuz, nu 500.
    T1 a luat nr. 1 (necomis); T2 citește tot MAX + 1 = 1, așteaptă la index, T1 comite, T2 primește violarea și reia: nr. 2."""
    from core import registratura_api as ra
    corp = {"directie": "intrare", "data": "2099-03-02", "descriere": "Adresa ITM"}
    r1, r2 = _cursa(lambda c: ra.inregistreaza(c, SCH, corp, 1), lambda c: ra.inregistreaza(c, SCH, dict(corp, descriere="Somatie"), 1),
                    "INSERT INTO %s.registratura" % SCH)
    print("C73/U2 registratura:", r1, r2)
    assert r1["numar"] == 1 and isinstance(r2, dict) and r2["ok"] and r2["numar"] == 2, (r1, r2)
    assert _executa("SELECT numar, descriere FROM registratura ORDER BY numar") == [(1, "Adresa ITM"), (2, "Somatie")]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_doua_salvari_simultane_ale_sablonului(firma):
    """Comanda U2 pct.2: numele dublat al șablonului — refuzul existent NUME_EXISTA și la cursă (înainte: 500 pe
    `contracte_sabloane_nume_unic`); și la a doua salvare conștientă, același cod."""
    from core import contracte_api as ca
    r1, r2 = _cursa(lambda c: ca.salveaza_sablon(c, SCH, None, "Contract vanzare", "Text 1", 1),
                    lambda c: ca.salveaza_sablon(c, SCH, None, "Contract vanzare", "Text 2", 1),
                    "INSERT INTO %s.contracte_sabloane" % SCH)
    print("C73/U2 sablon:", r1, r2)
    assert r1["ok"] and r2 == {"ok": False, "cod": "NUME_EXISTA"}, (r1, r2)
    with _db.get_conn(SCH) as c:
        assert ca.salveaza_sablon(c, SCH, None, "Contract vanzare", "Text 3", 1) == {"ok": False, "cod": "NUME_EXISTA"}
        alt = ca.salveaza_sablon(c, SCH, None, "Contract prestari", "Text 4", 1)
        assert ca.salveaza_sablon(c, SCH, alt["id"], "Contract vanzare", "Text 4", 1) == {"ok": False, "cod": "NUME_EXISTA"}   # editarea
        assert ca.salveaza_sablon(c, SCH, alt["id"], "Contract prestari", "Text 5", 1) == {"ok": True, "id": alt["id"]}
    assert _executa("SELECT nume, continut FROM contracte_sabloane ORDER BY id") == [("Contract vanzare", "Text 1"),
                                                                                    ("Contract prestari", "Text 5")]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_varianta_de_raport_dublata(firma):
    """Comanda U2 pct.3: varianta de raport cu același nume — NUME_EXISTA (prin constrângere, același drum ca la cursă)."""
    from core import rapoarte_comerciale_api as rc
    with _db.get_conn(SCH) as c:
        assert rc.salveaza_varianta(c, SCH, "comercial", "Lunar", {"a": 1}, 1)["ok"]
        assert rc.salveaza_varianta(c, SCH, "comercial", "Lunar", {"a": 2}, 1) == {"ok": False, "cod": "NUME_EXISTA"}
        with c.cursor() as cur:   # tranzacția a rămas utilizabilă (savepoint)
            cur.execute("SELECT count(*) FROM rapoarte_salvate")
            assert cur.fetchone()[0] == 1


def _factura_si_firma():
    _executa("INSERT INTO firma_profil (id, nume, cui, platitor_tva, tip_decont, regim_fiscal, tip_firma) "
             "VALUES (1, 'C73 TEST SRL', '14399840', true, 'L', 'profit', 'srl')")
    return _executa("INSERT INTO facturi (numar, data_emitere, directie, total, tva) VALUES ('U2-1', '2099-01-10', 'emisa', 121, 21) "
                    "RETURNING id")[0][0]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_a_doua_trimitere_efactura_simultana_se_opreste_inainte_de_anaf(firma, monkeypatch):
    """Comanda U2 pct.7: „o trimitere e deja în curs”. Rândul «pregătit» nu e în indexul `uq_efactura_trimiteri_viu`, deci două
    trimiteri simultane încărcau AMÂNDOUĂ factura la ANAF, iar a doua cădea abia la scrierea rezultatului (500, index pierdut).
    Acum o trimitere «pregătit» de acum câteva secunde oprește a doua cerere ÎNAINTE de încărcare."""
    from core import efactura_trimitere as eft
    fid = _factura_si_firma()
    _executa("INSERT INTO efactura_trimiteri (factura_id, mediu, stare, xml_sha256, trimis_la) VALUES (%s, 'prod', 'pregatit', 'x', "
             "now() - interval '5 seconds')", fid)
    incarcari = []
    monkeypatch.setattr(eft.spv_conector, "ia_token_activ", lambda conn, p: "token")
    monkeypatch.setattr(eft.spv_conector, "stare_firma", lambda conn, p, cif: {})
    monkeypatch.setattr(eft, "incarca_factura", lambda conn, s, f: ({"tert_tara": "RO"}, [], {}, {}))
    monkeypatch.setattr(eft, "completeaza_client_ro", lambda c: c)
    monkeypatch.setattr(eft._ef, "genereaza_xml", lambda *a: "<Invoice/>")
    monkeypatch.setattr(eft._ef, "valideaza", lambda xml: (True, []))
    monkeypatch.setattr(eft._ef, "upload_ubl", lambda *a, **k: incarcari.append(a))
    r = eft.trimite(SCH, fid, {"tip": "cabinet"}, mediu="prod")
    print("C73/U2 trimitere în curs:", r)
    assert r["stare"] == "in_curs" and r["mesaj"].startswith("O trimitere a acestei facturi către SPV e deja în curs (pornită la "), r
    assert incarcari == [], "a doua cerere a ajuns la ANAF"
    assert _executa("SELECT count(*) FROM efactura_trimiteri")[0][0] == 1
    # o încercare «pregătit» veche (peste fereastră) e întreruptă, nu în curs: nu mai oprește trimiterea
    _executa("UPDATE efactura_trimiteri SET trimis_la = now() - %s * interval '1 minute'", eft.FEREASTRA_IN_CURS_MIN + 1)
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            assert eft._repo.trimitere_in_curs(cur, SCH, fid, "prod", eft.FEREASTRA_IN_CURS_MIN) is None


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_rezultatul_peste_o_trimitere_vie_nu_se_pierde(firma):
    """Plasa de sub poartă (U2): dacă rândul ar deveni al doilea viu al facturii, rezultatul ANAF (indexul) nu se pierde într-un 500 —
    rândul trece în «investigatie», cu dublura numită."""
    from core import repo_efactura as re_
    fid = _factura_si_firma()
    viu = _executa("INSERT INTO efactura_trimiteri (factura_id, mediu, stare, xml_sha256, index_incarcare) "
                   "VALUES (%s, 'prod', 'ok', 'a', '111') RETURNING id", fid)[0][0]
    pregatit = _executa("INSERT INTO efactura_trimiteri (factura_id, mediu, stare, xml_sha256, trimis_la) "
                        "VALUES (%s, 'prod', 'pregatit', 'b', now()) RETURNING id", fid)[0][0]
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            m = re_.rezultatul_trimiterii(cur, SCH, "incarcat", "222", 0, None, pregatit)
    print("C73/U2 dublura vie:", m)
    assert m.startswith("ANAF a primit și această încărcare, dar factura avea deja o trimitere vie (trimiterea %d)" % viu), m
    assert _executa("SELECT stare, index_incarcare FROM efactura_trimiteri WHERE id = %s", pregatit) == [("investigatie", "222")]
    # rezultatul obișnuit (fără dublură) se scrie ca până acum
    alta = _executa("INSERT INTO efactura_trimiteri (factura_id, mediu, stare, xml_sha256, trimis_la) "
                    "VALUES (%s, 'prod', 'pregatit', 'c', now()) RETURNING id", fid)[0][0]
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            assert re_.rezultatul_trimiterii(cur, SCH, "nok", None, 1, "eroare", alta) is None
    assert _executa("SELECT stare FROM efactura_trimiteri WHERE id = %s", alta) == [("nok",)]


def test_reluarea_numarului_se_opreste_numit_dupa_incercari(monkeypatch):
    """`reincearca_la_dublura`: o cursă pierdută se reia (scrierea a doua oară reușește); după `incercari` curse pierdute la rând, refuzul
    numit — niciodată excepția bazei; altă constrângere trece neatinsă."""
    import psycopg2
    from core import chei_unice

    class _E(psycopg2.errors.UniqueViolation):
        pass

    class _Cur:
        def __init__(self):
            self.sql = []

        def execute(self, q, *a):
            self.sql.append(q)

    monkeypatch.setattr(chei_unice, "constrangerea", lambda e: str(e))
    cur, pasi = _Cur(), []

    def scrie():
        pasi.append(1)
        if len(pasi) == 1:
            raise _E("registratura_an_numar_unic")
        return "nr %d" % len(pasi)
    assert chei_unice.reincearca_la_dublura(cur, ("registratura_an_numar_unic",), scrie, None) == "nr 2"
    assert cur.sql == ["SAVEPOINT cheie_unica", "ROLLBACK TO SAVEPOINT cheie_unica", "SAVEPOINT cheie_unica",
                       "RELEASE SAVEPOINT cheie_unica"], cur.sql

    def mereu(): raise _E("registratura_an_numar_unic")   # noqa: E704
    with pytest.raises(chei_unice.CheieDublata, match="numărul nu s-a putut aloca"):
        chei_unice.reincearca_la_dublura(_Cur(), ("registratura_an_numar_unic",), mereu,
                                         lambda c, e: chei_unice.CheieDublata("numărul nu s-a putut aloca"), incercari=3)

    def alta(): raise _E("alta_cheie")   # noqa: E704
    with pytest.raises(psycopg2.errors.UniqueViolation):
        chei_unice.reincearca_la_dublura(_Cur(), ("registratura_an_numar_unic",), alta, None)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_emisa_din_fisier_cu_numarul_alteia(firma):
    """(U2) Importul unei facturi EMISE din XML cu numărul altei facturi emise (alt client, altă dată — deci nu dublura recunoscută)
    cădea cu 500 pe `facturi_numar_emisa_uniq` și oprea tot importul; acum refuz numit pe factura aceea, tranzacția rămâne utilizabilă."""
    from core import chei_unice, uc_comun
    _executa("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_nume, tert_cui) "
             "VALUES ('U2-9', '2099-01-05', 'emisa', 121, 21, 'ALFA SRL', '24736200')")
    f = {"numar": "U2-9", "data_emitere": "2099-02-07", "data_scadenta": None, "total": 50, "tva": 0, "moneda": "RON", "directie": "emisa",
         "xml": "<Invoice/>", "tert_nume": "BETA SRL", "tert_cui": "14399840", "linii": []}
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            with pytest.raises(chei_unice.CheieDublata) as ex:
                uc_comun._factura_din_parsat(cur, SCH, f)
            print("C73/U2 import emisă:", ex.value)
            assert str(ex.value).startswith("Factura emisă U2-9 din 07.02.2099 (către BETA SRL) nu s-a importat: numărul U2-9 e deja pe "
                                            "factura emisă din 05.01.2099, către ALFA SRL."), str(ex.value)
            cur.execute("SELECT count(*) FROM facturi")     # tranzacția a rămas utilizabilă, nimic în plus
            assert cur.fetchone()[0] == 1
            assert uc_comun._factura_din_parsat(cur, SCH, dict(f, numar="U2-10"))[1] is True   # alt număr: se importă


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_poarta_etransport_vede_trimiterea_in_curs(firma):
    """Comanda U2 pct.7 (e-Transport): o notificare «pregătit» de acum câteva secunde -> „in_curs”, înainte de încărcare; una vie ->
    „deja_trimisa”; peste fereastră -> liberă."""
    from core import etransport_send as es
    _executa("INSERT INTO etransport_trimiteri (mediu, stare, xml_sha256, trimis_la) VALUES ('prod', 'pregatit', 'sha-u2', now())")
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            r = es._poarta_vie(cur, SCH, "sha-u2")
    print("C73/U2 e-Transport:", r)
    assert r["stare"] == "in_curs" and r["mesaj"].startswith("Notificarea aceasta e deja în curs de trimitere către ANAF"), r
    _executa("UPDATE etransport_trimiteri SET trimis_la = now() - %s * interval '1 minute'", es.FEREASTRA_IN_CURS_MIN + 1)
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            assert es._poarta_vie(cur, SCH, "sha-u2") is None
    _executa("UPDATE etransport_trimiteri SET stare = 'ok', uit = 'UIT-1'")
    with _db.get_conn(SCH) as c:
        with c.cursor() as cur:
            assert es._poarta_vie(cur, SCH, "sha-u2")["stare"] == "deja_trimisa"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_doua_adaugari_simultane_ale_contului(firma):
    """(U2, cheia primară naturală) Contul adăugat de om în plan: T1 a scris simbolul (necomis), T2 îl adaugă și el — înainte 500 pe
    `plan_conturi_pkey`, acum ACELAȘI 409 ca la a doua adăugare conștientă, cu denumirea contului scris între timp."""
    import types
    from core import erori, uc_tenants

    def prima(c):
        with c.cursor() as cur:
            cur.execute("INSERT INTO %s.plan_conturi (simbol, denumire, tip) VALUES ('4111.99', 'Clienti U2', 'A')" % SCH)
    _r1, r2 = _cursa(prima, lambda c: uc_tenants.tenant_plan_conturi_adauga(TID, types.SimpleNamespace(simbol="4111.99", denumire="Alt"),
                                                                             {"uid": 1}), "INSERT INTO plan_conturi")
    print("C73/U2 cont:", repr(r2))
    assert isinstance(r2, erori.Conflict) and str(r2.detaliu).startswith("Contul 4111.99 există deja în plan: „Clienti U2”"), repr(r2)


def test_clasificarea_facturii_nu_atinge_cheile():
    """(U3) Premisa excepției `repo_facturi.actualizeaza_clasificarea`: fiecare apelant își compune SET-ul din bucăți LITERALE, niciuna
    pe o coloană a cheilor facturii (sau a predicatului lor)."""
    chei = {k for t, _c, cols, pred, _l in catalog_unice() if t == "facturi" for k in cols + pred}
    gasite = []
    for cale, sursa in _surse():
        arbore = ast.parse(sursa)
        for fn in [n for n in ast.walk(arbore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == "actualizeaza_clasificarea"
                   for x in ast.walk(fn)):
                gasite.append((cale, fn.name, sorted(bucati_set(fn))))
    gasite = [g for g in gasite if not any(h[0] == g[0] and h[1] != g[1] and g[1] in h[2] for h in gasite)]
    print("C73/U3 clasificarea facturii:", gasite)
    assert gasite and all(b and not (set(b) & chei) for _c, _f, b in gasite), (gasite, sorted(chei))


# ============================================================
#  U3 — SCHEMA `public` (partajată între cabinete)
# ============================================================
#: scrieri pe o cheie unică a schemei `public` care NU pot dubla, fiecare cu motivul (și, unde se poate, premisa verificată mecanic)
EXCEPTII_PUBLIC = {
    # [lotul 13, 645] reactivarea pune `reactivat_la` pe suspendarea deschisă: rândul IESE din indexul unic parțial
    # `suspendari_cabinet_deschisa` (`WHERE reactivat_la IS NULL`), deci nu poate produce o dublură
    ("core/repo_admin.py", "inchide_suspendarea", "suspendari_cabinet"):
        "UPDATE care scoate rândul din indexul unic parțial (`reactivat_la` devine nenul): o dublură n-are drum",
    ("core/api_public.py", "genereaza", "api_chei"):
        "`cheie_hash` = sha256 al unei chei noi `secrets.token_urlsafe(32)` (256 de biți aleatori): o coliziune n-are drum "
        "(`test_tokenurile_publice_sunt_aleatoare`)",
    ("core/inregistrare_libera.py", "creeaza", "inregistrari_in_asteptare"):
        "`token_hash` = hash-ul unui `secrets.token_urlsafe(32)` nou (`test_tokenurile_publice_sunt_aleatoare`)",
    ("core/inregistrare_libera.py", "inlocuieste_tokenul", "inregistrari_in_asteptare"):
        "tokenul nou vine din `uc_auth.retrimite_confirmarea`: `secrets.token_urlsafe(32)` (`test_tokenurile_publice_sunt_aleatoare`)",
    ("core/invitatii.py", "creeaza", "invitatii_cabinet"):
        "`token_hash` = hash-ul unui `secrets.token_urlsafe(32)` nou (`test_tokenurile_publice_sunt_aleatoare`)",
    ("core/repo_main.py", "insert_public_3", "tokene_activare"):
        "tokenul de activare / logare vine de la apelanții lui `_pune_token`, fiecare cu `token_urlsafe(32)` nou "
        "(`test_tokenurile_publice_sunt_aleatoare`)",
    ("core/fisiere_private.py", "salveaza", "fisiere_private"):
        "`cale` = `<cabinet>/<uuid4>.<tip>` (122 de biți aleatori), aleasă de aplicație la fiecare fișier",
    ("core/repo_utilizatori.py", "leaga_contul_de_firma", "user_tenants"):
        "(contul, firma) cu contul ABIA creat în aceeași funcție (`creeaza_cont`, id nou din secvență) — o singură legătură pe el "
        "(`test_contul_nou_se_leaga_o_data`); contul existent trece prin `leaga_contul_de_firma_idempotent` (ON CONFLICT)",
    ("core/coada_api.py", "aproba", "declaratii_coada"):
        "`stare` la_senior -> aprobata: amândouă în indexul `ux_coada_activa`, pe același (firmă, tip, perioadă) — rândul era deja "
        "unicul activ (`test_tranzitiile_cozii_nu_dubleaza_elementul_activ`)",
    ("core/coada_api.py", "respinge", "declaratii_coada"):
        "`stare` -> respinsa: rândul IESE din indexul parțial `ux_coada_activa` (`test_tranzitiile_cozii_nu_dubleaza_elementul_activ`)",
    ("core/coada_api.py", "inlocuieste", "declaratii_coada"):
        "`stare` -> respinsa: rândul IESE din indexul parțial `ux_coada_activa` (`test_tranzitiile_cozii_nu_dubleaza_elementul_activ`)",
    ("core/coada_api.py", "marcheaza_depusa", "declaratii_coada"):
        "`stare` -> depusa: rândul IESE din indexul parțial `ux_coada_activa` (`test_tranzitiile_cozii_nu_dubleaza_elementul_activ`)",
    ("core/repo_declaratii.py", "inchide_asteptarea_deschisa", "declaratii_in_asteptare"):
        "`rezolvata_la = now()`: așteptarea IESE din indexul parțial `declaratii_in_asteptare_deschisa` (`WHERE rezolvata_la IS NULL`)",
    ("core/repo_declaratii.py", "revendica_asteptarea", "declaratii_in_asteptare"):
        "`rezolvata_la = now()`: așteptarea IESE din indexul parțial `declaratii_in_asteptare_deschisa`",
    ("core/spv_conector.py", "dezactiveaza_token", "spv_token"):
        "`activ = false`: tokenul IESE din indexurile parțiale `uq_spv_token_*_viu` (`WHERE activ AND …`), cheia nu se schimbă",
    ("core/repo_notificari_livrare.py", "scrie_jurnalul", "notificari_jurnal"):
        "`mesaj_id` = id-ul dat de WhatsApp mesajului abia trimis (unul per trimitere), NULL pe email — în afara indexului parțial "
        "(`test_jurnalul_notificarilor_primeste_idul_furnizorului`)",
    ("core/firma_rezumat.py", "aplica_ddl", "firma_aspect_sursa"):
        "registrul proiectat din cod la PORNIRE: DELETE + INSERT în aceeași tranzacție, sub `instante.blocaj_pornire` (workerii se "
        "serializează), din perechi distincte (`test_registrul_proiectat_la_pornire`)",
    ("core/firma_rezumat.py", "aplica_ddl", "sursa_supervizor"):
        "la fel ca `firma_aspect_sursa`: proiecția `supervizor_cache.TABELE_TENANT`, distinctă, sub blocajul de pornire",
}

#: funcții de repository pe chei ale schemei `public` a căror dublură o tratează APELANTUL (savepoint-ul și refuzul sunt ale
#: use-case-ului, care știe ce text dă verificarea lui prealabilă). Gardul verifică FIECARE apel.
LA_APELANT_PUBLIC = {
    ("core/repo_utilizatori.py", "creeaza_cont", "users"):
        "clientul invitat (`uc_tenants.client_acces_creeaza`, `uc_portal.portal_adauga_acces`): `refuza_dublura` pe `users_email_key` "
        "cu textul verificării (`uc_comun._refuz_email_la_cursa`)",
    ("core/repo_utilizatori.py", "creeaza_cont_asistent", "users"):
        "asistentul invitat (`uc_asistenti.asistent_creeaza`): același refuz, 422 pe câmpul `email`",
    ("core/repo_utilizatori.py", "schimba_emailul", "users"):
        "confirmarea adresei noi (`uc_public.portal_confirma_email`): același text ca `uc_comun._adresa_e_libera`",
    ("core/repo_declaratii.py", "insereaza_asteptare", "declaratii_in_asteptare"):
        "`uc_coada.asteapta_notele` închide așteptarea deschisă și o scrie pe cea nouă sub `reincearca_la_dublura` (operația e „scrie "
        "sau înlocuiește”: cursa pierdută se reia și o înlocuiește pe cea comisă între timp)",
}


def catalog_public():
    """[(tabel, constrângere, coloane, coloanele predicatului, literalele predicatului)] — cheile unice ale schemei `public`, citite din
    `pg_index` pe baza de TEST (numai citire). Schema publică n-are o sursă unică în text (bootstrap + `core/migrare_*.py` + `*.sql` din
    rădăcină + DDL la pornire); baza de test e cea pe care rulează suita, iar `test_catalogul_public_cuprinde_sursele` o leagă de
    sursele din depozit. Cheia surogat `(id)` nu e în catalog (ca la `catalog_unice`)."""
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT ct.relname, ci.relname, pg_get_indexdef(i.indexrelid) FROM pg_index i "
                        "JOIN pg_class ci ON ci.oid = i.indexrelid JOIN pg_class ct ON ct.oid = i.indrelid "
                        "JOIN pg_namespace n ON n.oid = ct.relnamespace WHERE n.nspname = 'public' AND i.indisunique")
            randuri = cur.fetchall()
        c.rollback()
    out = []
    for t, ix, d in randuri:
        d = re.sub(r"::\w+", "", d)   # conversiile din forma canonică (`'respinsa'::text`)
        k = d.index("(", d.index(" USING "))
        j = _inchisa(d, k)
        cols = tuple(x for x in _coloane(d[k + 1:j]) if x not in ("array", "all", "any"))
        w = re.search(r"\bWHERE\b(.*)", d[j + 1:], re.S)
        pred = tuple(x for x in _coloane(w.group(1)) if x not in ("array", "all", "any")) if w else ()
        if cols != ("id",):
            out.append((t, ix, cols, pred, _literale(w.group(1)) if w else {}))
    return sorted(out, key=lambda x: (x[0], x[1]))


def _unice_publice_declarate():
    """Numele indexurilor unice create pe `public.` în sursele din depozit (migrări, `*.sql`, DDL-ul de la pornire), fără cele șterse."""
    fis = (glob.glob(os.path.join(_RAD, "core", "*.py")) + glob.glob(os.path.join(_RAD, "*.sql")) + glob.glob(os.path.join(_RAD, "*.py"))
           + [os.path.join(_RAD, "infra", "bootstrap_public.sql")])
    create, drop = set(), set()
    for f in fis:
        if os.path.basename(f).startswith("test_"):
            continue
        s = io.open(f, encoding="utf-8").read()
        create |= set(re.findall(r"CREATE\s+UNIQUE\s+INDEX\s+(?:CONCURRENTLY\s+)?(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+ON\s+(?:ONLY\s+)?public\.",
                                 s, re.I))
        drop |= set(re.findall(r"DROP\s+INDEX\s+(?:IF\s+EXISTS\s+)?(?:public\.)?(\w+)", s, re.I))
    return create - drop


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_catalogul_public_cuprinde_sursele():
    """Anti-vacuu al catalogului public: cel puțin cheile măsurate la 21.10.2026 (45: 19 unice + 26 chei primare naturale), cele numite
    în comandă, și fiecare index unic creat pe `public.` în sursele din depozit (baza de test nu e în urma codului)."""
    cat = catalog_public()
    nume = {c[1] for c in cat}
    print("C73/U3 catalog public:", len(cat), sorted(nume))
    assert len(cat) >= 45, len(cat)
    assert {"users_email_key", "ux_coada_activa", "declaratii_in_asteptare_deschisa", "invitatii_cabinet_token_hash_key",
            "inregistrari_in_asteptare_token_hash_key", "api_chei_cheie_hash_key", "ix_tokene_activare_token_hash",
            "fisiere_private_cale_key", "notificari_jurnal_mesaj_uq", "uq_spv_token_tenant_viu", "accounting_firms_cui_key",
            "declaratii_depuse_pkey", "alerte_emise_pkey"} <= nume, sorted(nume)
    declarate = _unice_publice_declarate()
    assert declarate and declarate <= nume, ("index unic creat în sursă, absent din baza de test (migrare nerulată?)",
                                             sorted(declarate - nume))
    # ce predicat are coada: elementul activ = stare în afara lui respinsa / depusa (premisa excepțiilor `coada_api`)
    coada = [c for c in cat if c[1] == "ux_coada_activa"][0]
    assert coada[2] == ("tenant_id", "tip", "perioada") and coada[3] == ("stare",), coada


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_gardul_cheilor_unice_public():
    """Fiecare scriere a unei chei unice din schema `public` tratează dublura, ori e tratată la apelant, ori e excepție cu motiv."""
    cat = catalog_public()
    gasite = []
    for cale, sursa in _surse():
        gasite += scrieri_pe_chei(sursa, cale, cat)
    print("C73/U3 scrieri pe chei publice:", len(gasite))
    for g in gasite:
        print("  ", g)
    netratate = [g for g in gasite if not g[4] and (g[0], g[1], g[2]) not in EXCEPTII_PUBLIC
                 and (g[0], g[1], g[2]) not in LA_APELANT_PUBLIC]
    assert not netratate, ("scriere pe o cheie unică din schema public fără tratarea dublurii, deci 500 la dublură: %s" % netratate)
    vazute = {(g[0], g[1], g[2]) for g in gasite}
    for asteptat in [("core/auth_api.py", "inregistreaza_cabinet", "users"), ("core/auth_api.py", "actualizeaza_cabinet", "accounting_firms"),
                     ("core/coada_api.py", "marcheaza_depusa", "declaratii_depuse"), ("core/coada_api.py", "adauga_in_coada", "declaratii_coada"),
                     ("core/repo_control_fiscal_api.py", "insert_depusa_extern", "declaratii_depuse"),
                     ("core/istoric_declaratii_import_api.py", "importa", "declaratii_depuse"),
                     ("core/repo_declaratii.py", "insereaza_asteptare", "declaratii_in_asteptare"),
                     ("core/repo_monitor_fiscal.py", "revendica_pragul", "alerte_emise"),
                     ("core/spv_conector.py", "salveaza_token", "spv_token"),
                     ("core/firma_rezumat.py", "<modul>", "firma_tip")]:
        assert asteptat in vazute, (asteptat, sorted(vazute))
    for e in list(EXCEPTII_PUBLIC) + list(LA_APELANT_PUBLIC):
        assert e in vazute, ("intrare fără scriere în cod — de scos", e)
    # ce tratează funcțiile `LA_APELANT_PUBLIC` e verificat de `test_tratate_la_apelant`, pe fiecare apel


def test_tratate_la_apelant_public():
    """Ca `test_tratate_la_apelant`, pentru funcțiile de repository ale schemei `public`."""
    for (fis, functie, _t), _motiv in LA_APELANT_PUBLIC.items():
        modul = os.path.basename(fis)[:-3]
        gasite = []
        for cale, sursa in _surse():
            gasite += [(cale,) + a for a in apeluri(sursa, modul, functie)]
        print("C73/U3 apelanții lui %s.%s:" % (modul, functie), gasite)
        assert gasite, ("niciun apel al lui %s.%s — de scos din LA_APELANT_PUBLIC" % (modul, functie))
        assert all(ok for _c, _f, ok in gasite), ("apelant care nu tratează dublura: %s" % [g for g in gasite if not g[2]])


def _functie(cale, nume):
    arbore = ast.parse(io.open(os.path.join(_RAD, cale), encoding="utf-8").read())
    return [n for n in ast.walk(arbore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume][0]


def _token_aleator(fn):
    """Funcția cheamă `secrets.token_urlsafe(32)` (sau `token_urlsafe(32)` importat) — apelul, citit ca nod AST: un comentariu sau un
    șir care pomenește `token_urlsafe(32)` nu e un token."""
    return any(isinstance(x, ast.Call) and (getattr(x.func, "attr", None) or getattr(x.func, "id", None)) == "token_urlsafe"
               and [getattr(a, "value", None) for a in x.args] == [32] for x in ast.walk(fn))


def test_tokenurile_publice_sunt_aleatoare():
    """Premisa excepțiilor pe hash-uri de token (`api_chei`, `invitatii_cabinet`, `inregistrari_in_asteptare`, `tokene_activare`): tokenul
    se naște din `secrets.token_urlsafe(32)` chiar în funcția care îl scrie sau în FIECARE apelant al lui `_pune_token`."""
    for cale, fn in [("core/api_public.py", "genereaza"), ("core/inregistrare_libera.py", "creeaza"), ("core/invitatii.py", "creeaza"),
                     ("core/uc_auth.py", "retrimite_confirmarea")]:
        assert _token_aleator(_functie(cale, fn)), (cale, fn)
    apelanti = []
    for cale, sursa in _surse():
        arbore = ast.parse(sursa)
        for fn in [n for n in ast.walk(arbore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name != "_pune_token"]:
            if any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == "_pune_token" for x in ast.walk(fn)):
                apelanti.append((cale, fn.name, _token_aleator(fn)))
    print("C73/U3 apelanții _pune_token:", apelanti)
    assert len(apelanti) >= 4 and all(ok for _c, _f, ok in apelanti), apelanti
    assert any(isinstance(x, ast.Attribute) and x.attr == "hex" and isinstance(x.value, ast.Call)   # `uuid.uuid4().hex`, ca nod
               and isinstance(x.value.func, ast.Attribute) and x.value.func.attr == "uuid4"
               and isinstance(x.value.func.value, ast.Name) and x.value.func.value.id == "uuid"
               for x in ast.walk(_functie("core/fisiere_private.py", "salveaza")))


def test_contul_nou_se_leaga_o_data():
    """Premisa excepției `leaga_contul_de_firma`: fiecare apel stă după un `creeaza_cont` în aceeași funcție (id nou)."""
    gasite = []
    for cale, sursa in _surse():
        arbore = ast.parse(sursa)
        for fn in [n for n in ast.walk(arbore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            lin = lambda nume: [x.lineno for x in ast.walk(fn) if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)  # noqa: E731
                                and x.func.attr == nume]
            for l_ in lin("leaga_contul_de_firma"):
                gasite.append((cale, fn.name, any(c < l_ for c in lin("creeaza_cont"))))
    gasite = [g for g in gasite if g[1] != "leaga_contul_de_firma"]
    print("C73/U3 leaga_contul_de_firma:", gasite)
    assert gasite and all(ok for _c, _f, ok in gasite), gasite


def test_tranzitiile_cozii_nu_dubleaza_elementul_activ():
    """Premisa excepțiilor `coada_api` pe `ux_coada_activa` (activ = stare ∉ {respinsa, depusa}): stările scrise de UPDATE sunt
    aprobata (din la_senior — rămâne activ, aceeași cheie), respinsa și depusa (ies din index); niciun UPDATE nu schimbă cheia."""
    from core import coada_api
    sursa = io.open(os.path.join(_RAD, "core", "coada_api.py"), encoding="utf-8").read()
    stari = set(re.findall(r"UPDATE public\.declaratii_coada SET stare\s*=\s*'(\w+)'", sursa))
    assert stari == {"aprobata", "respinsa", "depusa"}, stari
    assert coada_api.TRANZITII["aproba"] == ("la_senior", "aprobata"), coada_api.TRANZITII
    assert not re.search(r"UPDATE public\.declaratii_coada SET[^\"]*\b(tenant_id|tip|perioada)\s*=", sursa)
    # „Confirmă depunerea” citește elementul cu lacăt: a doua confirmare simultană vede «depusa», nu scrie a doua depunere
    import inspect
    assert re.search(r"FROM public\.declaratii_coada \"\s*\"WHERE id = %s FOR UPDATE", inspect.getsource(coada_api.marcheaza_depusa))


def test_jurnalul_notificarilor_primeste_idul_furnizorului():
    """Premisa excepției `scrie_jurnalul`: un singur apelant (`notificari._jurnal`), iar `mesaj_id` vine numai din trimiterea WhatsApp."""
    gasite = [(c, f) for c, s in _surse() for f, _ok in apeluri(s, "repo_notificari_livrare", "scrie_jurnalul")]
    s = io.open(os.path.join(_RAD, "core", "notificari.py"), encoding="utf-8").read()
    assert set(re.findall(r"mesaj_id=(\w+)", s)) <= {"mid", "None"}, re.findall(r"mesaj_id=(\w+)", s)
    assert re.search(r"mid = _wa\.trimite_notificare\(", s)
    assert set(gasite) == {("core/notificari.py", "_jurnal")}, gasite


def test_registrul_proiectat_la_pornire():
    """Premisa excepțiilor `firma_rezumat.aplica_ddl`: chemat la pornire DUPĂ `blocaj_pornire` (workeri serializați), din perechi
    distincte."""
    from core import firma_rezumat as fr, supervizor_cache as sc
    m = io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()
    assert 0 <= m.index("_instante.blocaj_pornire(conn)") < m.index("_fr_boot.aplica_ddl(conn)")
    perechi = [(a, t) for a, d in fr.ASPECTE.items() for t in tuple(d["tabele"]) + tuple(d["tabele_public"])]
    assert len(perechi) == len(set(perechi)) and len(sc.TABELE_TENANT) == len(set(sc.TABELE_TENANT))


# ── probe funcționale: baza de TEST, o tranzacție ANULATĂ, valori sintetice (`*@exemplu.test`, firma 9910733, anul 2099) ──────────
TID_PUB = 9910733
CUI_CABINET = "99907310"   # sintetic, cifra de control verificată (algoritmul CUI din CLAUDE.md)


class _CurOrb:
    """Cursorul „orb la prima citire”: cererea a citit ÎNAINTE ca cealaltă să comită (fereastra cursei). Pe schema `public` cursa
    reală nu se poate reproduce în ROLLBACK (rândul câștigătorului ar trebui comis într-un tabel partajat), deci câștigătorul se scrie
    în aceeași tranzacție, iar citirea care l-ar fi văzut întoarce „nimic” (sau o formă veche) — o dată. Scrierea și violarea cheii
    sunt REALE, pe Postgres."""

    def __init__(self, real, orb):
        object.__setattr__(self, "_r", real)
        object.__setattr__(self, "_o", orb)

    def __getattr__(self, n):
        return getattr(self._r, n)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self._r.close()
        return False

    def __iter__(self):
        return iter(self._r)

    def execute(self, q, a=None):
        for k in list(self._o):
            if k in q:
                v = self._o.pop(k)
                q, a = (q.replace(k, v), a) if v is not None else ("SELECT 1 WHERE false", None)
                break
        return self._r.execute(q, a)


class _ConnOrb:
    def __init__(self, real, orb):
        object.__setattr__(self, "_r", real)
        object.__setattr__(self, "orb", orb)

    def __getattr__(self, n):
        return getattr(self._r, n)

    def cursor(self, *a, **k):
        return _CurOrb(self._r.cursor(*a, **k), self.orb)

    def commit(self):
        pass

    def rollback(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture()
def pub(monkeypatch):
    """O conexiune în tranzacție ANULATĂ la final; `db.get_conn` o dă pe ea (commit / rollback ale use-case-urilor: fără efect)."""
    p = _db.pool()
    real = p.getconn()
    c = _ConnOrb(real, {})
    monkeypatch.setattr(_db, "get_conn", lambda schema=None: c)
    from core import observare
    monkeypatch.setattr(observare, "trimite_email_html_sau_semnaleaza", lambda *a, **k: True)
    try:
        yield c
    finally:
        real.rollback()
        p.putconn(real)


def _sql(c, q, *a):
    with c._r.cursor() as cur:
        cur.execute(q, a)
        return cur.fetchall() if cur.description else None


def _cabinet(c, nume, cui=None):
    return _sql(c, "INSERT INTO public.accounting_firms (nume, cui) VALUES (%s, %s) RETURNING id", nume, cui)[0][0]


def _cont(c, email, firma, rol="angajat"):
    return _sql(c, "INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ) VALUES (%s, 'x', 'U3', %s, %s, "
                   "true) RETURNING id", email, rol, firma)[0][0]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_asistent_cu_adresa_luata_la_cursa(pub):
    """Comanda U3 (`users`, `creeaza_cont_asistent`): adresa luată între verificare și scriere — înainte 500 pe `users_email_key`,
    acum ACELAȘI refuz ca verificarea prealabilă (422, lângă câmpul `email`)."""
    import types
    from core import erori, mesaje, uc_asistenti
    f = _cabinet(pub, "U3 CABINET A")
    _cont(pub, "u3.asistent@exemplu.test", f)                       # câștigătorul cursei
    pub.orb["SELECT id, rol, activ, accounting_firm_id FROM public.users"] = None   # verificarea a citit înaintea lui
    d = types.SimpleNamespace(email="u3.asistent@exemplu.test", nume="Ana", poate_pregati=True, poate_valida=False, poate_depune=False,
                              firme=[])
    with pytest.raises(erori.DateInvalide) as ex:
        uc_asistenti.asistent_creeaza(d, {"firm": f, "uid": 1, "rol": "admin_firma"})
    d = ex.value.detaliu
    print("C73/U3 asistent:", d)
    assert d["mesaj"] == mesaje.EMAIL_ASISTENT_EXISTA % "u3.asistent@exemplu.test", d    # același refuz ca verificarea prealabilă
    assert d["erori_campuri"] == [{"camp": "email", "mesaj": d["mesaj"]}], d
    assert "users_email_key" not in str(d) and "U3 CABINET" not in str(d), d    # fără codul bazei, fără cabinetul altcuiva
    assert _sql(pub, "SELECT count(*) FROM public.users WHERE email = 'u3.asistent@exemplu.test'") == [(1,)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_confirmarea_adresei_luate_intre_timp(pub):
    """Comanda U3 (`schimba_emailul`): adresa nouă luată după verificarea `_adresa_e_libera` — același text, nu 500."""
    import types
    from core import erori, mesaje, uc_comun, uc_public
    f = _cabinet(pub, "U3 CABINET B")
    a = _cont(pub, "u3.vechi@exemplu.test", f, "client")
    _cont(pub, "u3.nou@exemplu.test", f, "client")
    _sql(pub, "INSERT INTO public.schimbari_email (user_id, tenant_id, email_vechi, email_nou, token_hash, expira) VALUES (%s, %s, "
              "'u3.vechi@exemplu.test', 'u3.nou@exemplu.test', %s, now() + interval '1 hour')", a, TID_PUB, uc_comun._hash_tok("tok-u3"))
    pub.orb["SELECT id FROM public.users WHERE lower(email)=%s AND id<>%s"] = None
    with pytest.raises(erori.CerereGresita) as ex:
        uc_public.portal_confirma_email(types.SimpleNamespace(token="tok-u3"))
    print("C73/U3 confirmare email:", ex.value.detaliu)
    assert ex.value.detaliu["mesaj"] == mesaje.EMAIL_OCUPAT % "u3.nou@exemplu.test", ex.value.detaliu   # același text ca verificarea
    assert _sql(pub, "SELECT email FROM public.users WHERE id = %s", a) == [("u3.vechi@exemplu.test",)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_inregistrarea_cu_adresa_luata_la_cursa(pub):
    """Comanda U3 (`auth_api.inregistreaza_cabinet`): același „email deja înregistrat” ca verificarea, și niciun cabinet fără proprietar."""
    from core import auth_api
    f = _cabinet(pub, "U3 CABINET C")
    _cont(pub, "u3.cabinet@exemplu.test", f, "admin_firma")
    pub.orb["SELECT id, activ FROM public.users WHERE email=%s"] = None
    r = auth_api.inregistreaza_cabinet(pub, "u3.cabinet@exemplu.test", "Parola-U3-lunga!", "U3 CABINET NOU")
    print("C73/U3 înregistrare:", r)
    assert r == {"ok": False, "cod": "EMAIL_EXISTA", "mesaj": "Există deja un cont cu acest email. Autentifică-te sau folosește alt email."}, r   # [lotul 13, 608]
    assert _sql(pub, "SELECT count(*) FROM public.accounting_firms WHERE nume = 'U3 CABINET NOU'") == [(0,)]
    # fără cursă: înregistrarea merge (savepoint-ul nu strică drumul obișnuit)
    r = auth_api.inregistreaza_cabinet(pub, "u3.altul@exemplu.test", "Parola-U3-lunga!", "U3 CABINET NOU")
    assert r["ok"] and _sql(pub, "SELECT email FROM public.users WHERE id = %s", r["user_id"]) == [("u3.altul@exemplu.test",)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cui_cabinet_dublat_refuz_numit(pub):
    """Comanda U3 (`accounting_firms_cui_key`, Setări cabinet): CUI-ul altui cabinet — înainte 500, acum 422 lângă câmpul `cui`, fără
    să numească cabinetul care îl are (schema `public` e a tuturor cabinetelor)."""
    import types
    from core import auth_api, erori, uc_eu
    _cabinet(pub, "U3 CABINET ALFA", CUI_CABINET)
    f = _cabinet(pub, "U3 CABINET BETA")
    with pytest.raises(erori.DateInvalide) as ex:
        uc_eu.eu_cabinet_set(types.SimpleNamespace(nume=None, cui=CUI_CABINET), {"rol": "admin_firma", "firm": f})
    d = ex.value.detaliu
    print("C73/U3 CUI cabinet:", d)
    assert d["mesaj"] == auth_api.CUI_CABINET_EXISTA % CUI_CABINET, d
    assert d["erori_campuri"] == [{"camp": "cui", "mesaj": d["mesaj"]}] and "existent" not in d, d
    assert "ALFA" not in str(d) and "accounting_firms" not in str(d), d
    assert _sql(pub, "SELECT cui FROM public.accounting_firms WHERE id = %s", f) == [(None,)]
    assert uc_eu.eu_cabinet_set(types.SimpleNamespace(nume="U3 BETA NOU", cui=None), {"rol": "admin_firma", "firm": f})["ok"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_istoricul_peste_o_depunere_prin_iconta(pub):
    """Comanda U3 (`declaratii_depuse_pkey`): rândul istoric pe o perioadă deja depusă prin iConta.eu dădea 500 pentru tot importul;
    acum rândul acela se respinge numit, restul intră (C25)."""
    from core import istoric_declaratii_import_api as idi
    # fixtura-sintetica-ok: tenant sintetic TID_PUB = 9910733 (nicio firmă reală), conexiunea `pub` se anulează la final (ROLLBACK)
    _sql(pub, "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa) "
              "VALUES (%s, 2025, 1, 'd300', '2025-02-20', 'iconta')", TID_PUB)
    r = idi.importa(pub, TID_PUB, [{"tip": "D300", "an": 2025, "luna": 1, "data_depunere": "2025-02-21"},
                                   {"tip": "D112", "an": 2025, "luna": 1, "data_depunere": "2025-02-22"}])
    print("C73/U3 istoric:", r["importati"], r["respinse"])
    assert r["importati"] == 1, r
    assert [(x["rand"], x["mesaj"]) for x in r["respinse"]] == [
        (2, "D300 pe 01/2025 e deja depusă prin iConta.eu la 20.02.2025: rândul din istoric nu se importă peste ea.")], r["respinse"]
    assert _sql(pub, "SELECT tip, sursa FROM public.declaratii_depuse WHERE tenant_id = %s ORDER BY tip", TID_PUB) == [
        ("d112", "migrare"), ("d300", "iconta")]
    # numai rânduri care nu pot intra: refuz întreg (istoricul vechi nu se șterge pentru nimic)
    with pytest.raises(ValueError, match="Niciun rând nu poate intra: rand 2: D300 pe 01/2025 e deja depusă prin iConta.eu"):
        idi.importa(pub, TID_PUB, [{"tip": "D300", "an": 2025, "luna": 1, "data_depunere": "2025-02-21"}], inlocuieste=True)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_numarul_depunerii_se_reia_la_cursa(pub):
    """Comanda U3 (`nr_depunere` = MAX + 1, dat de aplicație): numărul citit înaintea celeilalte depuneri e deja luat — înainte 500 pe
    `declaratii_depuse_pkey`, acum se reia cu numărul următor."""
    from core import repo_control_fiscal_api as rcf
    _sql(pub, "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa) "
              "VALUES (%s, 2099, 2, 'd300', '2099-03-20', 'iconta')", TID_PUB)
    pub.orb["COALESCE(MAX(nr_depunere), 0) + 1"] = "COALESCE(MAX(nr_depunere), 0)"   # MAX-ul vechi: numărul 1, deja luat
    with pub.cursor() as cur:
        rcf.insert_depusa_extern(cur, TID_PUB, 2099, 2, "d300", "2099-03-21", "REC-U3")
    assert not pub.orb, "cursa nu s-a produs"
    assert _sql(pub, "SELECT nr_depunere, sursa FROM public.declaratii_depuse WHERE tenant_id = %s ORDER BY 1", TID_PUB) == [
        (1, "iconta"), (2, "extern")]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_asteptarea_simultana_inlocuieste_nu_cade(pub):
    """Comanda U3 (`declaratii_in_asteptare`, 3 drumuri): două cereri simultane pe aceeași declarație — a doua nu vedea așteptarea
    primei ca s-o închidă, iar indexul o refuza cu 500. Acum se reia: o închide (INLOCUITA) și rămâne una singură deschisă."""
    import types
    from core import uc_coada
    _sql(pub, "INSERT INTO public.declaratii_in_asteptare (cabinet_id, tenant_id, tip, an, luna, cerere, user_id, note_ids) "
              "VALUES (1, %s, 'd300', 2099, 1, '{}', 1, '{1}')", TID_PUB)
    pub.orb["UPDATE public.declaratii_in_asteptare SET rezolvata_la = now(), rezultat"] = None
    d = types.SimpleNamespace(tenant_id=TID_PUB, tip="d300", an=2099, luna=1, trim=None,
                              model_dump=lambda exclude_none=False: {"tip": "d300"})
    aid = uc_coada.asteapta_notele(d, {"firm": 1, "uid": 1, "rol": "admin_firma"}, [2])
    r = _sql(pub, "SELECT id = %s, rezolvata_la IS NULL, rezultat FROM public.declaratii_in_asteptare WHERE tenant_id = %s ORDER BY id",
             aid, TID_PUB)
    print("C73/U3 așteptare:", r)
    assert not pub.orb and r == [(False, False, {"cod": "INLOCUITA"}), (True, True, None)], r


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_anunturile_automate_o_singura_data(pub):
    """Comanda U3 (`alerte_emise`): două rulări suprapuse ale cronului — înainte amândouă trimiteau anunțurile, iar a doua cădea pe
    `alerte_emise_pkey`; acum pragul se revendică ÎNAINTE de anunțuri (ON CONFLICT DO NOTHING), deci a doua nu mai emite nimic."""
    from core import monitor_fiscal, repo_monitor_fiscal as rmf
    _sql(pub, "INSERT INTO public.alerte_fiscale (sursa, titlu, data_vigoare) VALUES ('u3-sintetic', 'Alerta U3 sintetica', CURRENT_DATE + 7)")
    n1 = monitor_fiscal.emite_alerte_programate(pub)
    pub.orb["SELECT 1 FROM public.alerte_emise"] = None   # a doua rulare (forma veche) citise jurnalul ÎNAINTE ca prima să-l scrie
    n2 = monitor_fiscal.emite_alerte_programate(pub)
    n = _sql(pub, "SELECT count(*) FROM public.anunturi_cabinet WHERE mesaj LIKE '%%Alerta U3 sintetica%%'")[0][0]
    print("C73/U3 anunțuri:", n1, n2, n)
    assert n1 >= 1 and n2 == 0 and n == n1, (n1, n2, n)
    with pub.cursor() as cur:
        aid = _sql(pub, "SELECT id FROM public.alerte_fiscale WHERE sursa = 'u3-sintetic'")[0][0]
        assert rmf.revendica_pragul(cur, aid, 3) is True and rmf.revendica_pragul(cur, aid, 3) is False
