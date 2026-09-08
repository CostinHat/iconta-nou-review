# -*- coding: utf-8 -*-
"""scripts/scan_dependente.py — CE CITEȘTE, de fapt, fiecare aspect al modelului de citire.

**DE CE EXISTĂ.** `firma_rezumat.ASPECTE` declară, pentru fiecare aspect, tabelele-sursă care îl
invalidează. Lista aceea a fost SCRISĂ, nu măsurată — iar auditul lui P2 a arătat că e incompletă
(`salariati`, citită de `_termene_una_firma`, nu era în ea). *O listă de dependențe scrisă din
memorie e o părere despre cod, nu o proprietate a lui.* Modelul de invalidare din Faza B se
construiește pe matricea asta, deci matricea trebuie măsurată, nu crezută.

**DOUĂ INSTRUMENTE INDEPENDENTE, ȘI SE CONFRUNTĂ.** Fiecare are o formă proprie de orbire; folosite
împreună, orbirea unuia intră în domeniul vizibil al celuilalt, iar dezacordul se RAPORTEAZĂ.

  * **PLAN** — pentru fiecare instrucțiune executată, `EXPLAIN (FORMAT JSON)` pe o conexiune
    separată, iar din arborele de plan se culeg `Schema` + `Relation Name`. E o citire din
    **parserul lui PostgreSQL**, nu o potrivire de șiruv pe textul SQL (METODA §23: structură, nu
    text). Atribuie exact: se știe care aspect, care instrucțiune.
    *Orb la:* ce citește o funcție plpgsql pe dinăuntru (planul arată apelul, nu corpul);
    instrucțiunile care nu se pot explica (`SET`, `RESET`, DDL) — numărate și declarate, nu tăcute.

  * **STAT** — delta pe `pg_stat_all_tables` (`seq_scan + idx_scan`) în jurul calculului. E
    contabilitatea lui PostgreSQL despre ce relații au fost efectiv scanate, deci **vede și
    interiorul funcțiilor**.
    *Orb la:* atribuirea per instrucțiune; și poluat de alte sesiuni care ating aceleași tabele în
    aceeași fereastră. De aceea nu e singurul instrument, ci martorul celuilalt.

**DEZACORDUL E REZULTAT, nu eroare.** `doar_stat` = tabele văzute de STAT și nevăzute de PLAN — de
obicei citite din funcții, exact clasa la care PLAN e orb. `doar_plan` = planificat dar nescanat
(ramură moartă, `LIMIT 0`, plan care n-a atins relația). Amândouă se scriu în raport.

**CALIBRAREA — în ambele direcții, plus mutația pe modul propriu de eșec** (interdicția 76,
METODA §22). `calibreaza()` dă instrumentului:
  (a) un bloc care citește o tabelă cunoscută  -> TREBUIE s-o raporteze  (nu ratează);
  (b) un bloc care nu citește nicio tabelă      -> TREBUIE să raporteze gol (nu inventează);
  (c) un bloc care citește o tabelă **prin corpul unei funcții plpgsql** -> PLAN trebuie s-o
      RATEZE, iar STAT trebuie s-o VADĂ. Fără (c), cele două instrumente ar putea fi de fapt unul
      singur, iar „acordul" dintre ele n-ar dovedi nimic.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

#: Instrucțiunile care NU se pot explica — se numără și se declară, nu se ignoră tăcut.
NEEXPLICABILE = ("set ", "reset ", "begin", "commit", "rollback", "savepoint", "release",
                 "create ", "drop ", "alter ", "truncate ", "declare ", "close ", "fetch ",
                 "vacuum", "analyze", "show ", "listen", "notify")


def _e_explicabila(sql):
    s = (sql or "").strip().lstrip("(").lower()
    return not s.startswith(NEEXPLICABILE)


# ============================================================================
#  INSTRUMENTUL 1 — PLAN: relațiile din arborele de plan al lui PostgreSQL
# ============================================================================
def _relatii_din_plan(nod, out):
    """Culege `(schema, relatie)` din arborele de plan. RECURSIV — un plan e un arbore, iar
    relația căutată poate sta oricât de adânc (subplanuri, CTE-uri, `InitPlan`)."""
    if isinstance(nod, list):
        for x in nod:
            _relatii_din_plan(x, out)
        return
    if not isinstance(nod, dict):
        return
    rel = nod.get("Relation Name")
    if rel:
        out.add(((nod.get("Schema") or "?"), rel))
    for cheie in ("Plan", "Plans", "Subplans", "CTE", "Init Plan", "Sub Plan"):
        if cheie in nod:
            _relatii_din_plan(nod[cheie], out)
    # orice altă listă/dict imbricat (formele variază între versiuni de PG)
    for v in nod.values():
        if isinstance(v, (list, dict)):
            _relatii_din_plan(v, out)


class ColectorPlan:
    """Ține evidența instrucțiunilor și, pentru fiecare formă distinctă, relațiile din planul ei.

    Cheia de cache e SQL-ul **neinterpolat** (forma instrucțiunii): aceeași formă are același plan
    la nivel de relații atinse, iar `control_fiscal` execută mii de instrucțiuni de câteva zeci de
    forme. Fără cache, inventarul ar dura de zeci de ori mai mult fără să afle nimic în plus."""

    def __init__(self):
        self.relatii = set()
        self.instructiuni = 0
        self.explicate = 0
        self.neexplicabile = 0
        self.esecuri = []          # (sql scurtat, eroare) — declarate, nu înghițite
        self._cache = {}

    def vede(self, conn_explica, schema, sql_brut, sql_mogrificat):
        self.instructiuni += 1
        if not _e_explicabila(sql_mogrificat):
            self.neexplicabile += 1
            return
        cheie = (schema, sql_brut if isinstance(sql_brut, str) else str(sql_brut))
        if cheie in self._cache:
            self.relatii |= self._cache[cheie]
            self.explicate += 1
            return
        gasite = set()
        try:
            with conn_explica.cursor() as cur:
                if schema:
                    cur.execute('SET search_path TO "%s", public' % schema)
                # VERBOSE e obligatoriu: fără el planul NU poartă cheia `Schema`, iar o relație
                # s-ar identifica doar după numele scurt — adică `tenant_004.facturi` și
                # `public.facturi` ar deveni aceeași dependență. Calibrarea (a) a prins exact asta.
                cur.execute("EXPLAIN (FORMAT JSON, VERBOSE) " + sql_mogrificat)
                plan = cur.fetchone()[0]
            _relatii_din_plan(plan, gasite)
            self.explicate += 1
        except Exception as e:      # noqa: BLE001 — eșecul de explicare e REZULTAT, se raportează
            conn_explica.rollback()
            self.esecuri.append((sql_mogrificat[:160], "%s: %s" % (type(e).__name__, e)))
        self._cache[cheie] = gasite
        self.relatii |= gasite


# ============================================================================
#  ÎNVELIȘURILE — se pun peste `db.get_conn` la rulare, ca la `masoara_interogari`
# ============================================================================
class _Cursor:
    def __init__(self, real, colector, conn_explica, schema):
        self._real, self._c = real, colector
        self._ce, self._schema = conn_explica, schema

    def execute(self, sql, params=None):
        try:
            m = self._real.mogrify(sql, params)
            m = m.decode("utf-8", "replace") if isinstance(m, bytes) else m
        except Exception:
            m = sql if isinstance(sql, str) else str(sql)
        r = self._real.execute(sql, params) if params is not None else self._real.execute(sql)
        # EXPLAIN **după** execuție: dacă instrucțiunea reală ridică, nu vrem ca instrumentul
        # să fie cel care schimbă purtarea codului măsurat.
        self._c.vede(self._ce, self._schema, sql, m)
        return r

    def executemany(self, sql, seq):
        r = self._real.executemany(sql, seq)
        self._c.instructiuni += 1
        return r

    def __getattr__(self, n):
        return getattr(self._real, n)

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *a):
        return self._real.__exit__(*a)

    def __iter__(self):
        return iter(self._real)


class _Conn:
    def __init__(self, real, colector, conn_explica, schema):
        self._real, self._c = real, colector
        self._ce, self._schema = conn_explica, schema

    def cursor(self, *a, **k):
        return _Cursor(self._real.cursor(*a, **k), self._c, self._ce, self._schema)

    def __getattr__(self, n):
        return getattr(self._real, n)


# ============================================================================
#  INSTRUMENTUL 2 — STAT: delta pe contoarele de scanare ale lui PostgreSQL
# ============================================================================
#: **DE CE SE AȘTEAPTĂ, și de ce așteptarea e ADAPTIVĂ.** PostgreSQL nu scrie statisticile la
#: fiecare instrucțiune: backendul le ține în memorie și le varsă când devine inactiv, nu mai
#: devreme de `PGSTAT_MIN_INTERVAL` (1 s în PG 16). `pg_stat_force_next_flush()` golește **doar
#: backendul care îl cheamă** — iar munca măsurată s-a făcut pe alte conexiuni, din pool.
#:
#: O așteptare FIXĂ de 2,5 s a fost încercată întâi și a picat calibrarea în amândouă direcțiile
#: deodată, ceea ce a și arătat de ce e greșită: (a) raporta ZERO pentru o citire care chiar
#: avusese loc, iar (b) — blocul care nu citește nimic — raporta chiar tabela lui (a), fiindcă
#: vărsarea întârziată a nimerit în fereastra lui. *Un instrument care mută efectul de la un bloc
#: la următorul nu e doar imprecis, e o sursă de dependențe INVENTATE.*
#:
#: Deci: se așteaptă până când contoarele **stau pe loc** două citiri la rând, și asta se face pe
#: AMÂNDOUĂ marginile blocului — altfel restul lumii curge în măsurătoare.
STAT_PAS_SEC = 1.2
STAT_RABDARE_SEC = 15.0


def _goleste_backendurile_din_pool():
    """Face fiecare conexiune din pool să-și verse contoarele ACUM.

    **Asta e miezul problemei, și n-a fost evident.** Un backend PostgreSQL varsă statisticile la
    capătul unei comenzi, nu la capătul tranzacției tale — iar o conexiune întoarsă în pool nu mai
    primește nicio comandă, deci **stă cu contoarele nevărsate** până la temporizatorul de inactivitate
    (~10 s în PG 16). Așteptarea „până se liniștesc" a picat exact aici: contoarele stăteau pe loc nu
    fiindcă se vărsaseră, ci fiindcă nu se vărsaseră deloc — iar apoi apăreau în fereastra blocului
    URMĂTOR, dându-i acestuia dependențe pe care nu le avea.

    Deci nu se așteaptă: se scot pe rând conexiunile din pool și li se dă o comandă. E o operație
    ieftină și deterministă, iar `putconn` le pune la loc.
    """
    from core import db as _db
    p = _db.pool()
    luate = []
    try:
        for _ in range(int(getattr(p, "maxconn", 10) or 10)):
            try:
                c = p.getconn()
            except Exception:
                break
            luate.append(c)
            try:
                with c.cursor() as cur:
                    cur.execute("SELECT pg_stat_force_next_flush()")
                c.commit()
            except Exception:
                try:
                    c.rollback()
                except Exception:
                    pass
    finally:
        for c in luate:
            try:
                p.putconn(c)
            except Exception:
                pass


def _citeste_stat(conn, scheme):
    with conn.cursor() as cur:
        cur.execute("SELECT pg_stat_force_next_flush()")
        cur.execute(
            "SELECT schemaname, relname, COALESCE(seq_scan,0) + COALESCE(idx_scan,0) "
            "  FROM pg_stat_all_tables WHERE schemaname = ANY(%s)", (list(scheme),))
        return {(s, r): n for s, r, n in cur.fetchall()}


def _instantaneu_stat(conn, scheme, asteapta=False):
    """Contoarele, așteptate până se liniștesc. `(instantaneu, s_a_linistit)`."""
    if not asteapta:
        return _citeste_stat(conn, scheme), True
    limita = time.time() + STAT_RABDARE_SEC
    _goleste_backendurile_din_pool()
    inst = _citeste_stat(conn, scheme)
    while time.time() < limita:
        time.sleep(STAT_PAS_SEC)
        _goleste_backendurile_din_pool()
        nou = _citeste_stat(conn, scheme)
        if nou == inst:
            return nou, True
        inst = nou
    # Nu s-a liniștit în răbdarea dată — se SPUNE, nu se raportează o cifră ca și cum ar fi stabilă.
    return inst, False


def _delta_stat(inainte, dupa):
    out = set()
    for k, n in dupa.items():
        if n > inainte.get(k, 0):
            out.add(k)
    return out


# ============================================================================
#  MĂSURAREA UNUI BLOC
# ============================================================================
@contextlib.contextmanager
def masoara(scheme_urmarite, cu_stat=True):
    """`with masoara([schema, 'public']) as m:` — apoi `m.raport()`.

    Pune ambele instrumente în jurul blocului și le păstrează separate până la raport.
    `cu_stat=False` lasă doar PLAN — pentru sweep-urile largi, unde golirea backendurilor pe fiecare
    margine ar domina timpul. Raportul spune atunci `stat_rulat=False`, ca o listă STAT goală să nu
    se citească drept „n-a atins nimic"."""
    from core import db as _db
    col = ColectorPlan()
    rezultat = {}
    original = _db.get_conn

    conn_explica = _db.pool().getconn()
    conn_stat = _db.pool().getconn()
    conn_stat.autocommit = True

    @contextlib.contextmanager
    def get_conn_urmarit(schema=None):
        with original(schema) as c:
            yield _Conn(c, col, conn_explica, schema)

    class M:
        def raport(self):
            return rezultat

    m = M()
    if cu_stat:
        inainte, linistit_inainte = _instantaneu_stat(conn_stat, scheme_urmarite, asteapta=True)
    else:
        inainte, linistit_inainte = {}, True
    _db.get_conn = get_conn_urmarit
    t0 = time.time()
    try:
        yield m
    finally:
        secunde = time.time() - t0
        _db.get_conn = original
        try:
            conn_explica.rollback()
        except Exception:
            pass
        if cu_stat:
            dupa, linistit_dupa = _instantaneu_stat(conn_stat, scheme_urmarite, asteapta=True)
            stat = _delta_stat(inainte, dupa)
        else:
            linistit_dupa, stat = True, set()
        plan = set(col.relatii)
        rezultat.update({
            "secunde": round(secunde, 3),
            "stat_rulat": bool(cu_stat),
            # Dacă o margine n-a apucat să se liniștească, cifra STAT e SUSPECTĂ și o spune —
            # altfel ar arăta identic cu una măsurată curat.
            "stat_stabil": bool(linistit_inainte and linistit_dupa),
            "instructiuni": col.instructiuni,
            "explicate": col.explicate,
            "neexplicabile": col.neexplicabile,
            "esecuri_explicare": col.esecuri,
            "plan": sorted(plan),
            "stat": sorted(stat),
            "acord": sorted(plan & stat),
            "doar_plan": sorted(plan - stat),
            "doar_stat": sorted(stat - plan),
        })
        _db.pool().putconn(conn_explica)
        _db.pool().putconn(conn_stat)


# ============================================================================
#  CALIBRARE — ambele direcții + mutația pe modul propriu de eșec
# ============================================================================
_FUNCTIE_PROBA = """
CREATE SCHEMA IF NOT EXISTS proba_dependente;
CREATE TABLE IF NOT EXISTS proba_dependente.tabela_vazuta (x integer);
CREATE TABLE IF NOT EXISTS proba_dependente.tabela_din_functie (x integer);
CREATE OR REPLACE FUNCTION proba_dependente.citeste_ascuns() RETURNS bigint AS $$
    SELECT count(*) FROM proba_dependente.tabela_din_functie;
$$ LANGUAGE sql STABLE;
"""


def calibreaza(verbose=True):
    """`(ok, detalii)`. Trei probe; a treia e cea care contează cel mai mult."""
    from core import db as _db
    _db.init_pool()
    S = "proba_dependente"
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(_FUNCTIE_PROBA)
        c.commit()

    det = {}

    # (a) POZITIVĂ — o citire reală trebuie văzută de amândouă
    with masoara([S]) as m:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT count(*) FROM proba_dependente.tabela_vazuta")
                cur.fetchone()
    a = m.raport()
    det["a_pozitiva"] = a
    vede_plan = (S, "tabela_vazuta") in set(map(tuple, a["plan"]))
    vede_stat = (S, "tabela_vazuta") in set(map(tuple, a["stat"]))

    # (b) NEGATIVĂ — un bloc care nu atinge nicio tabelă nu are voie să inventeze una
    with masoara([S]) as m:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    b = m.raport()
    det["b_negativa"] = b
    nu_inventeaza = not [x for x in b["plan"] if x[0] == S] and not [x for x in b["stat"] if x[0] == S]

    # (c) MUTAȚIA pe modul propriu de eșec: citire ascunsă în corpul unei funcții.
    #     PLAN trebuie s-o RATEZE (asta E orbirea lui, declarată în antet), STAT trebuie s-o vadă.
    #     Dacă amândouă ar vedea-o, sau niciunul, „confruntarea" n-ar mai fi o confruntare.
    with masoara([S]) as m:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT proba_dependente.citeste_ascuns()")
                cur.fetchone()
    cc = m.raport()
    det["c_mutatie_functie"] = cc
    ascunsa = (S, "tabela_din_functie")
    plan_rateaza = ascunsa not in set(map(tuple, cc["plan"]))
    stat_prinde = ascunsa in set(map(tuple, cc["stat"]))

    ok = vede_plan and vede_stat and nu_inventeaza and plan_rateaza and stat_prinde
    if verbose:
        print("CALIBRARE scan_dependente — ambele direcții + mutație:")
        print("  (a) citire reală      : PLAN o vede = %s ; STAT o vede = %s" % (vede_plan, vede_stat))
        print("  (b) fără citire       : niciunul nu inventează = %s" % nu_inventeaza)
        print("  (c) citire în funcție : PLAN o RATEAZĂ = %s ; STAT o PRINDE = %s"
              % (plan_rateaza, stat_prinde))
        print("      (c) e proba că cele două instrumente sunt cu adevărat independente")
        print("  VERDICT:", "OK" if ok else "PICAT — nicio matrice de mai jos n-ar valora nimic")
    return ok, det


# ============================================================================
#  INVENTARUL — per aspect, pe o firmă reală
# ============================================================================
#: CONTABILITATEA PROPRIE a modelului — scrisă de recalculare, nu citită ca sursă. Dacă ar rămâne
#: în matrice, modelul s-ar declara dependent de el însuși, iar orice recalculare ar produce o nouă
#: invalidare: o buclă. Se EXCLUDE explicit, ca să fie o alegere, nu o omisiune.
CONTABILITATE_PROPRIE = ("firma_rezumat", "supervizor_sursa", "supervizor_rezultat",
                         "firma_rezumat_lucru")


def _masoara_aspect(aspect, tenant_id, schema, azi, scheme, cu_stat):
    """Un aspect, o firmă. Cheamă EXACT funcțiile pe care le cheamă lucrătorul."""
    from core import db as _db, firma_rezumat as _fr
    with masoara(scheme, cu_stat=cu_stat) as m:
        try:
            # `ASPECTE_USOARE`, nu `ASPECTE`: de la remediere, aspectele grele stau în ACELAȘI
            # registru (ca să-și declare sursele și timpul), dar cu `calcul = None` — se produc
            # împreună, prin `recalculeaza_greu`. Prima formă a scanerului le trata ca ușoare și
            # chema `None(...)`; măsurătoarea ieșea GOALĂ, nu eronată, iar o matrice goală trece
            # orice comparație „registrul cuprinde ce s-a măsurat".
            if aspect in _fr.ASPECTE_USOARE:
                with _db.get_conn(schema) as cs:
                    _fr.ASPECTE[aspect]["calcul"](cs, schema)
            elif aspect == "termene":
                import main as _main
                with _db.get_conn() as c:
                    with c.cursor() as cur:
                        cur.execute("SELECT nume, cui FROM public.tenants WHERE id=%s", (tenant_id,))
                        r = cur.fetchone()
                nume, cui = (r[0], r[1]) if r else (None, None)
                _main._termene_una_firma({"id": tenant_id, "nume": nume, "cui": cui},
                                         _ctx_admin(tenant_id), azi)
            elif aspect == "control_fiscal":
                import main as _main
                from core import control_fiscal_api as _cf
                ctx = _ctx_admin(tenant_id)
                with _db.get_conn(schema) as cs, _db.get_conn() as cp:
                    rr = _cf.evalueaza_firma(cs, cp, tenant_id, schema, azi)
                _main._construieste_contabil(schema, tenant_id, ctx, azi.year, azi.month,
                                             rr.get("regim_tva_anaf"))
        except Exception as e:      # noqa: BLE001 — o firmă care ridică NU oprește inventarul;
            m._eroare = "%s: %s" % (type(e).__name__, e)   # se notează și se merge mai departe
    rap = m.raport()
    rap["eroare"] = getattr(m, "_eroare", None)
    return rap


def _ctx_admin(tenant_id):
    """Același context ca `recalculeaza_greu`: administratorul cabinetului FIRMEI.

    Fără el, două sub-verificări cad pe 404 și **nu ating tabelele lor** — iar matricea ar ieși mai
    scurtă decât realitatea, exact în direcția periculoasă (dependențe ratate = invalidare ratată)."""
    from core import db as _db
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT u.id FROM public.users u "
                        "  JOIN public.tenants t ON t.accounting_firm_id = u.accounting_firm_id "
                        " WHERE t.id = %s AND u.rol = 'admin_firma' AND u.activ "
                        " ORDER BY u.id LIMIT 1", (tenant_id,))
            r = cur.fetchone()
    return {"uid": r[0]} if r else {"uid": None}


def inventar(azi=None, firme_cu_stat=3, limita_firme=None):
    """Matricea aspect -> surse, măsurată pe TOT portofoliul.

    **DE CE PE TOATE FIRMELE, nu pe una.** Un scan vede doar stările pe care le produc datele firmei
    pe care rulează. Prima rulare, pe `tenant_001`, n-a atins `miscari_stoc` — nu fiindcă modelul nu
    depinde de ea, ci fiindcă firma aceea n-a intrat pe ramura de stocuri. *Punctul orb e firma, nu
    ecranul.* Matricea publicată e REUNIUNEA peste firme, iar numărul de firme e scris lângă ea.

    **CONFRUNTAREA COSTĂ, deci se face pe un eșantion.** PLAN e ieftin (nu așteaptă nimic) și rulează
    pe toate firmele. STAT cere golirea backendurilor pe amândouă marginile, ~5 s per măsurătoare,
    deci rulează pe primele `firme_cu_stat`. Dacă pe eșantion cele două NU se contrazic, PLAN singur
    e crezut pe rest — iar dacă se contrazic, se spune și matricea nu se publică drept completă."""
    from core import db as _db, firma_rezumat as _fr
    from core.common import azi_ro as _azi_ro
    _db.init_pool()
    azi = azi or _azi_ro()

    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE activ ORDER BY id")
            firme = cur.fetchall()
    if limita_firme:
        firme = firme[:limita_firme]

    aspecte = list(_fr.ASPECTE) + list(_fr.ASPECTE_GRELE)
    out = {"azi": str(azi), "firme_masurate": len(firme),
           "firme_cu_confruntare": min(firme_cu_stat, len(firme)),
           "aspecte": {a: {"plan": set(), "stat": set(), "doar_stat": set(), "doar_plan": set(),
                           "instructiuni": 0, "secunde": 0.0, "neexplicabile": 0,
                           "esecuri_explicare": [], "erori_firma": [], "stat_instabil": 0}
                       for a in aspecte}}

    for i, (tid, schema) in enumerate(firme):
        cu_stat = i < firme_cu_stat
        scheme = [schema, "public"]
        for a in aspecte:
            r = _masoara_aspect(a, tid, schema, azi, scheme, cu_stat)
            acc = out["aspecte"][a]
            acc["plan"] |= {tuple(x) for x in r["plan"]}
            acc["instructiuni"] += r["instructiuni"]
            acc["secunde"] += r["secunde"]
            acc["neexplicabile"] += r["neexplicabile"]
            acc["esecuri_explicare"] += r["esecuri_explicare"][:3]
            if r["eroare"]:
                acc["erori_firma"].append((tid, r["eroare"][:120]))
            if cu_stat:
                acc["stat"] |= {tuple(x) for x in r["stat"]}
                acc["doar_stat"] |= {tuple(x) for x in r["doar_stat"]}
                acc["doar_plan"] |= {tuple(x) for x in r["doar_plan"]}
                if not r["stat_stabil"]:
                    acc["stat_instabil"] += 1
        print("   ... firma %s (%s) %s" % (tid, schema, "[+confruntare STAT]" if cu_stat else ""),
              flush=True)

    for a, acc in out["aspecte"].items():
        for cheie in ("plan", "stat", "doar_stat", "doar_plan"):
            acc[cheie] = sorted(x for x in acc[cheie] if x[1] not in CONTABILITATE_PROPRIE)
        acc["secunde"] = round(acc["secunde"], 3)
        acc["declarat_in_cod"] = sorted(_fr.ASPECTE[a]["tabele"]) if a in _fr.ASPECTE else []
    return out


def _tipar(inv):
    print("\nINVENTAR DEPENDENȚE — %d firme (confruntare STAT pe %d), azi=%s"
          % (inv["firme_masurate"], inv["firme_cu_confruntare"], inv["azi"]))
    for a, r in inv["aspecte"].items():
        print("\n── %s ── %.1fs · %d instrucțiuni (%d neexplicabile, %d eșecuri de explicare)"
              % (a, r["secunde"], r["instructiuni"], r["neexplicabile"],
                 len(r["esecuri_explicare"])))
        print("   DECLARAT în cod : %s" % (r.get("declarat_in_cod") or "—"))
        print("   MĂSURAT (%d)    : %s" % (len(r["plan"]), ["%s.%s" % t for t in r["plan"]]))
        if r["doar_stat"]:
            print("   ! DOAR STAT     : %s   (citit din funcție — PLAN e orb aici)"
                  % ["%s.%s" % t for t in r["doar_stat"]])
        if r["doar_plan"]:
            print("   ! DOAR PLAN     : %s   (planificat, nescanat pe eșantion)"
                  % ["%s.%s" % t for t in r["doar_plan"]])
        if r["erori_firma"]:
            print("   firme care au ridicat: %s" % r["erori_firma"][:3])
        if r["stat_instabil"]:
            print("   ! STAT instabil pe %d măsurători" % r["stat_instabil"])


# ============================================================================
#  BLOCUL GENERAT — matricea, scrisă din registru, nu de mână
# ============================================================================
#: `DEPENDENTE_P2.md` conține matricea între marcajele astea. E GENERATĂ din `firma_rezumat.ASPECTE`,
#: iar `core/test_dependente_masurate.py` o regenerează și o compară **caracter cu caracter**. Fără
#: asta, documentul ar fi o a doua copie a registrului — și prima care rămâne în urmă.
MARCAJ_START = "<!-- MATRICE:GENERAT — se scrie cu `python3 -m scripts.scan_dependente --doc` -->"
MARCAJ_STOP = "<!-- MATRICE:SFARSIT -->"

DOC = "DEPENDENTE_P2.md"


def bloc_matrice():
    """Matricea aspect -> surse -> dependență de timp -> regulă de invalidare. Pură (fără bază)."""
    from core import firma_rezumat as FR
    r = [MARCAJ_START, ""]
    r.append("| aspect | surse în schema firmei | surse în `public` | dependență de timp "
             "| regula de invalidare |")
    r.append("|---|---|---|---|---|")
    for a in FR.TOATE:
        d = FR.ASPECTE[a]
        ten = ", ".join("`%s`" % t for t in sorted(d["tabele"])) or "—"
        pub = ", ".join("`%s`" % t for t in sorted(d["tabele_public"])) or "—"
        timp = {None: "nu depinde de ceas", "zi": "**ziua** (`YYYY-MM-DD`)",
                "luna": "**luna** (`YYYY-MM`)"}[d["timp"]]
        regula = ("`versiune_sursa` = suma contoarelor celor %d tabele; invalidat când suma se "
                  "schimbă" % (len(d["tabele"]) + len(d["tabele_public"])))
        if d["timp"]:
            regula += " **sau** când se schimbă epoca"
        r.append("| `%s` | %s | %s | %s | %s |" % (a, ten, pub, timp, regula))
    r.append("")
    r.append("**Inversa** — ce invalidează o scriere într-un tabel:")
    r.append("")
    r.append("| tabel-sursă | invalidează |")
    r.append("|---|---|")
    for t in FR.tabele_urmarite():
        r.append("| `%s` | %s |" % (t, ", ".join("`%s`" % a for a in FR.aspecte_ale_tabelei(t))))
    for t in FR.tabele_publice_urmarite():
        r.append("| `public.%s` | %s |"
                 % (t, ", ".join("`%s`" % a for a in FR.aspecte_ale_tabelei(t))))
    r.append("")
    r.append("**Citite, dar DELIBERAT neurmărite:** %s — poartă denumirea și cabinetul, nu faptele "
             "din care iese verdictul. O redenumire de firmă n-are voie să invalideze 1000 de "
             "rezumate."
             % ", ".join("`public.%s`" % t for t in FR.NEURMARITE_PUBLIC))
    r.append("")
    r.append("**Trigger, dar nu sursă a niciunui aspect:** %s — sursă a supervizorului (P1), care "
             "are contorul lui agregat. Un singur trigger servește amândoi consumatorii."
             % ", ".join("`%s`" % t for t in sorted(set(FR.tabele_cu_trigger())
                                                    - set(FR.tabele_urmarite()))))
    r.append("")
    r.append(MARCAJ_STOP)
    return "\n".join(r)


def scrie_doc(cale=None):
    """Injectează blocul între marcaje. Documentul din jur rămâne scris de om."""
    cale = cale or os.path.join(RAD, DOC)
    with open(cale, "r", encoding="utf-8", newline="") as f:
        s = f.read()
    i, j = s.find(MARCAJ_START), s.find(MARCAJ_STOP)
    if i < 0 or j < 0:
        raise RuntimeError("marcajele lipsesc din %s" % cale)
    nou = s[:i] + bloc_matrice() + s[j + len(MARCAJ_STOP):]
    with open(cale, "w", encoding="utf-8", newline="") as f:
        f.write(nou)
    return cale


if __name__ == "__main__":
    if "--doc" in sys.argv:
        print("scris blocul generat în:", scrie_doc())
        sys.exit(0)
    if "--bloc" in sys.argv:
        print(bloc_matrice())
        sys.exit(0)
    ok, _ = calibreaza()
    if not ok:
        sys.exit(2)
    print()
    inv = inventar()
    _tipar(inv)
    cale = os.path.join(RAD, "masuratori", "p2", "dependente_masurate.json")
    os.makedirs(os.path.dirname(cale), exist_ok=True)
    with open(cale, "w", encoding="utf-8", newline="") as f:
        json.dump(inv, f, ensure_ascii=False, indent=2, default=str)
    print("\nscris: %s" % cale)
