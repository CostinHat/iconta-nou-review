"""
core/audit_schema.py — F165: auditor de conformitate a schemelor tenant vs tenant_template.sql.

PROBLEMA (verificat la sursa 22.07): tenant_provisioning aplica template-ul INTEGRAL la
tenantii NOI (consistenti prin constructie), dar cand template-ul se schimba DUPA ce exista
tenanti, cei EXISTENTI raman in urma daca nimeni nu ruleaza un migrare_* pe ei. Convenția
migrare_* REPARA driftul, dar se bazeaza pe DISCIPLINA (cineva sa-si aminteasca) - nimic nu-l
PRINDE mecanic (cazul link_plata/sursa_externa). Acest modul e detectorul.

CUM (filosofia DUK: lasa lucrul real sa fie judecatorul, nu parsa SQL de mana):
construieste o schema de REFERINTA din tenant_template.sql intr-o tranzactie ROLLBACK,
introspecteaza information_schema, face diff coloana-cu-coloana, arunca referinta.

DOUA DIRECTII, tratate diferit (DECIZII 22.07 F165):
  - template -> tenant (tabela/coloana LIPSA in tenant, tip/nullable diferit): POARTA HARD.
    E clasa link_plata: template a castigat ceva, tenantul vechi n-a primit -> codul crapa.
  - tenant -> template (tabela/coloana EXTRA in tenant): DOAR RAPORT informativ, NU pica.
    Ar cere un whitelist ever-growing (cuplare la lista extensibila = rosu fals; aceeasi
    lectie ca vocabularul de Stari, 22.07). (23.07: d301_operatiuni mutat in template - nu mai e
    extra; d205_beneficiari = legacy mort pe tenant_002, fara consumatori - ramane extra informativ.)

ZGOMOT NORMALIZAT: column_default contine numele schemei in nextval('schema.seq') -> ar da
6 tip-diferit fals pe orice tenant. Se normalizeaza inainte de comparatie (lectia primului
diagnostic 22.07 - 6 fals-pozitive integral din nume de secventa).

SUGGEST, NU APPLY (DA Costin 22.07): CLI-ul EMITE corpul migrare_* (ALTER ADD COLUMN IF NOT
EXISTS) pentru coloanele lipsa, dar NU-l aplica. Repararea ramane un migrare_* numit, cu
mirror in template, revizuit de om - altfel fixul aplicat lasa gaura in procesul de migrari
(nedocumentat, nimic in git). Zero mutatie tacuta de schema.

Expus ca:
  - test in suita (test_audit_schema.py): pica la drift template->tenant (poarta la dev);
  - CLI on-demand: `python3 -m core.audit_schema` (tiparul migrare_*._main), inspectie pe prod.
"""
from core import db, tenant_provisioning as tp

MODUL = "audit_schema"

# schema temporara in care se materializeaza template-ul pentru comparatie (mereu in ROLLBACK)
SCHEMA_REF = "zaudit_schema_ref"

# tabele EXTRA cunoscute (informativ, NU cauza de pica) - documentate, nu whitelist de pica.
# 23.07: golit - d301_operatiuni mutat in template (nu mai e extra); d205_beneficiari sters din cod (legacy mort,
# zero consumatori) -> ramane pe tenant_002 ca extra informativ neanotat, nu se mai whitelist-eaza. Vezi DECIZII 23.07.
_EXTRA_CUNOSCUTE = {}


# ============================================================
#  INTROSPECTIE + NORMALIZARE (PURA pe cursor)
# ============================================================
def _norm_default(dflt, schema):
    """Sterge numele schemei din nextval('schema.seq') -> comparabil intre scheme.
    Fara asta, orice coloana seriala ar aparea ca 'tip diferit' (fals-pozitiv)."""
    if dflt is None:
        return None
    return dflt.replace("%s." % schema, "<schema>.")


def _introspect(cur, schema):
    """{tabela: {coloana: (data_type, is_nullable, char_max, default_normalizat)}}.
    Comparam data_type + is_nullable (tip + nullable, ce a cerut Costin); char_max si
    default sunt pastrate pentru SUGGEST, nu pentru poarta (evitam fals-pozitiv pe precizie)."""
    cur.execute(
        "SELECT table_name, column_name, data_type, is_nullable, "
        "       character_maximum_length, column_default "
        "FROM information_schema.columns WHERE table_schema=%s "
        "ORDER BY table_name, column_name", (schema,))
    d = {}
    for t, col, dt, nul, cmax, dflt in cur.fetchall():
        d.setdefault(t, {})[col] = (dt, nul, cmax, _norm_default(dflt, schema))
    return d


# ============================================================
#  DIFF (PURA pe dict-uri de introspectie)
# ============================================================
def _cheie_poarta(meta):
    """(data_type, is_nullable) - ce compara POARTA. char_max/default excluse (zgomot)."""
    return (meta[0], meta[1])


def compara(ref, tenant):
    """Diff intre introspectia REF (template) si a unui tenant. PURA.
    Intoarce dict cu directia HARD (template->tenant) separata de INFORMATIV (tenant->template)."""
    tab_ref, tab_t = set(ref), set(tenant)
    r = {
        "tabele_lipsa": sorted(tab_ref - tab_t),        # HARD
        "coloane_lipsa": {},                            # HARD  {tabela: [coloane]}
        "tip_dif": [],                                  # HARD  [(tabela, col, ref_meta, tenant_meta)]
        "nullable_dif": [],                             # HARD  [(tabela, col, ref_nul, tenant_nul)]
        "tabele_extra": sorted(tab_t - tab_ref),        # INFORMATIV
        "coloane_extra": {},                            # INFORMATIV
    }
    for t in sorted(tab_ref & tab_t):
        rc, tc = ref[t], tenant[t]
        lipsa = sorted(set(rc) - set(tc))
        extra = sorted(set(tc) - set(rc))
        if lipsa:
            r["coloane_lipsa"][t] = lipsa
        if extra:
            r["coloane_extra"][t] = extra
        for c in sorted(set(rc) & set(tc)):
            rdt, rnul = rc[c][0], rc[c][1]
            tdt, tnul = tc[c][0], tc[c][1]
            if rdt != tdt:
                r["tip_dif"].append((t, c, rdt, tdt))
            elif rnul != tnul:   # elif: un tip diferit acopera deja semnalul
                r["nullable_dif"].append((t, c, rnul, tnul))
    return r


def are_drift_hard(drift):
    """True daca exista drift pe directia HARD (template->tenant) = poarta pica."""
    return bool(drift["tabele_lipsa"] or drift["coloane_lipsa"]
                or drift["tip_dif"] or drift["nullable_dif"])


# ============================================================
#  SUGGEST SQL (corp migrare_*, NU se aplica)
# ============================================================
def _tip_ddl(meta):
    """Reconstruieste tipul pentru ALTER din introspectie. Best-effort (suggest, revizuit de om)."""
    dt, nul, cmax, dflt = meta
    tip = "varchar(%d)" % cmax if dt == "character varying" and cmax else dt
    return tip, nul, dflt


def sugereaza_alter(schema, drift, ref):
    """Emite ALTER TABLE ADD COLUMN IF NOT EXISTS pt coloanele LIPSA (corpul unui migrare_*).
    NU se aplica. Coloanele NOT NULL fara default primesc avertisment (esueaza pe tabela cu date)."""
    linii = []
    for t in sorted(drift["coloane_lipsa"]):
        for col in drift["coloane_lipsa"][t]:
            tip, nul, dflt = _tip_ddl(ref[t][col])
            bucata = 'ALTER TABLE "{s}".{t} ADD COLUMN IF NOT EXISTS {c} {tip}'.format(
                s=schema, t=t, c=col, tip=tip)
            if dflt is not None and "<schema>." not in dflt:  # nu propunem nextval (serial)
                bucata += " DEFAULT %s" % dflt
            if nul == "NO":
                if dflt is None:
                    linii.append("-- ATENTIE %s.%s: NOT NULL fara default -> esueaza pe tabela cu "
                                 "date; adauga DEFAULT sau backfill inainte." % (t, col))
                bucata += " NOT NULL"
            linii.append(bucata + ";")
    return linii


# ============================================================
#  ORCHESTRARE — construieste REF, compara, arunca (apelantul controleaza tranzactia)
# ============================================================
def auditeaza(conn, schemas, template_sql):
    """Construieste schema de referinta din template in conexiunea data, compara fiecare
    schema din `schemas`, arunca referinta. Intoarce (rapoarte: {schema: drift}, ref_introspect).
    APELANTUL controleaza commit/rollback - se cheama sub ROLLBACK (ref e temporara)."""
    if not db.schema_valida(SCHEMA_REF):
        raise ValueError("schema ref invalida")
    sql = tp.parametrizeaza_template(template_sql, SCHEMA_REF)
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_REF)
        cur.execute(sql)
        ref = _introspect(cur, SCHEMA_REF)
        rapoarte = {}
        for s in schemas:
            if not db.schema_valida(s):
                raise ValueError("schema invalida: %r" % s)
            rapoarte[s] = compara(ref, _introspect(cur, s))
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_REF)
    return rapoarte, ref


def _schemele_tenant(cur):
    cur.execute("SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
    return [r[0] for r in cur.fetchall()]


def _raporteaza(schema, drift, ref):
    """Text lizibil pentru CLI: drift HARD + suggest SQL + extra informativ."""
    out = ["########## %s ##########" % schema]
    hard = are_drift_hard(drift)
    if drift["tabele_lipsa"]:
        out.append("  TABELE lipsa (in template, nu in tenant):")
        for t in drift["tabele_lipsa"]:
            out.append("     - %s" % t)
    for t, cols in sorted(drift["coloane_lipsa"].items()):
        out.append("  COLOANE lipsa in %s: %s" % (t, ", ".join(cols)))
    for t, c, r_, t_ in drift["tip_dif"]:
        out.append("  TIP diferit %s.%s: template=%s tenant=%s" % (t, c, r_, t_))
    for t, c, r_, t_ in drift["nullable_dif"]:
        out.append("  NULLABLE diferit %s.%s: template is_nullable=%s tenant=%s" % (t, c, r_, t_))
    if hard:
        sug = sugereaza_alter(schema, drift, ref)
        out.append("  --- SQL SUGERAT (corp migrare_*, REVIZUIESTE + ruleaza manual, NU aplicat automat) ---")
        out.extend("     " + l for l in sug)
    # informativ (nu pica)
    for t in drift["tabele_extra"]:
        nota = _EXTRA_CUNOSCUTE.get(t, "extra in tenant, absent in template - de verificat")
        out.append("  (info) tabela extra %s: %s" % (t, nota))
    for t, cols in sorted(drift["coloane_extra"].items()):
        out.append("  (info) coloane extra in %s: %s" % (t, ", ".join(cols)))
    if not hard and not drift["tabele_extra"] and not drift["coloane_extra"]:
        out.append("  OK: conform cu template-ul.")
    return "\n".join(out)


def _main():
    db.init_pool()
    template_sql = open("tenant_template.sql", encoding="utf-8").read()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            schemas = _schemele_tenant(cur)
        rapoarte, ref = auditeaza(conn, schemas, template_sql)
        conn.rollback()  # ref temporara + zero mutatie pe tenanti
    hard = []
    for s in schemas:
        print(_raporteaza(s, rapoarte[s], ref))
        print()
        if are_drift_hard(rapoarte[s]):
            hard.append(s)
    print("REZULTAT: %d/%d scheme cu drift HARD (template->tenant)%s"
          % (len(hard), len(schemas), (": " + ", ".join(hard)) if hard else " - toate conforme"))
    return not hard


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
