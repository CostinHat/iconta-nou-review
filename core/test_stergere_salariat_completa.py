# -*- coding: utf-8 -*-
"""GARD (D5, 20.08.2026): stergerea unui salariat nu lasa jumatate din inregistrare in urma.

`salariu_istoric.salariat_id` e `integer NOT NULL` FARA `REFERENCES` (tenant_template.sql l.1176-1183),
la fel si celelalte tabele-copil: nimic nu cascadeaza in baza. `sterge_salariat` facea DOAR
`DELETE FROM salariati` -> istoricul salarial supravietuia ca orfan. Masurat la auditul t001 (20.08):
24 din 30 de randuri orfane pe tenant_001 (celelalte 18 scheme, curate).

Nu otravea cifrele - `salariu_istoric.salariu_la()` citeste mereu cu `salariat_id`, deci orfanii sunt
inerti. Riscul e altul: o inregistrare pe jumatate stearsa, care creste tacut, si care ar deveni
GRESITA in ziua in care cineva agrega pe perioada in loc de pe salariat.

REGULA GARDATA, auto-intretinuta din SCHEMA (nu dintr-o lista scrisa de mana):
  pentru fiecare tabel din `tenant_template.sql` care are coloana `salariat_id`, `sterge_salariat`
  trebuie ori sa STEARGA din el, ori sa REFUZE stergerea cand are randuri (poarta de mai sus).
Un tabel-copil NOU adaugat in template intra automat sub gard si forteaza decizia o data.

Mutatie probata: scoaterea lui `DELETE FROM salariu_istoric` -> rosu, numind tabelul.
"""
import ast
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SQL = [os.path.join(_RAD, f) for f in os.listdir(_RAD) if f.endswith(".sql")]
_API = os.path.join(_RAD, "core", "salariati_api.py")


def _schema():
    """Schema tenantului traieste in tenant_template.sql SI in fisierele NN_ddl_*.sql - le citesc pe toate
    (gardul a picat prima data exact pe asta: 3 tabele gasite in template vs 5 reale in baza)."""
    return "\n".join(open(f, encoding="utf-8", errors="replace").read() for f in sorted(_SQL))


def _tabele_cu_salariat_id():
    """{tabel: protejat_de_fk} - tabelele cu coloana salariat_id si daca schema le da un FK."""
    sql = _schema()
    out = {}
    for m in re.finditer(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(?:TENANT_PLACEHOLDER\.)?(\w+)\s*\((.*?)\n\s*\);",
                         sql, re.S):
        corp = m.group(2)
        if re.search(r"salariat_id\b", corp):
            out[m.group(1)] = bool(re.search(r"salariat_id[^,]*REFERENCES", corp, re.I))
    # tabele definite prin format() in DDL-uri numerotate (sirurile SQL sunt pe linii separate)
    for m in re.finditer(r"'\s*salariat_id\s+integer[^']*'", sql):
        pass
    # FK adaugate separat prin ALTER TABLE
    for m in re.finditer(r"ALTER TABLE[^;]*?\.(\w+)\s+ADD CONSTRAINT[^;]*?FOREIGN KEY \(salariat_id\)", sql, re.S):
        if m.group(1) in out:
            out[m.group(1)] = True
    return out


def _corp_sterge_salariat():
    arb = ast.parse(open(_API, encoding="utf-8").read())
    fn = next((n for n in ast.walk(arb)
               if isinstance(n, ast.FunctionDef) and n.name == "sterge_salariat"), None)
    assert fn is not None, "sterge_salariat nu mai exista in core/salariati_api.py"
    src = open(_API, encoding="utf-8").read()
    return ast.get_source_segment(src, fn) or ""


def test_toate_tabelele_copil_sunt_tratate():
    """Trei tratamente valide, oricare: STERGE din el / REFUZA daca are randuri / PROTEJAT de FK."""
    tabele = _tabele_cu_salariat_id()
    assert len(tabele) >= 4, \
        "doar %d tabele cu salariat_id gasite in schema - regexul s-a rupt, gardul ar trece pe gol" % len(tabele)
    corp = _corp_sterge_salariat()
    netratate = []
    for t, are_fk in sorted(tabele.items()):
        if are_fk:
            continue
        sterge = re.search(r"DELETE\s+FROM\s+%s\s+WHERE\s+salariat_id" % re.escape(t), corp, re.I)
        refuza = re.search(r"count\(\*\)\s+FROM\s+%s\s+WHERE\s+salariat_id" % re.escape(t), corp, re.I)
        if not (sterge or refuza):
            netratate.append(t)
    assert not netratate, (
        "sterge_salariat nu trateaza tabelele-copil (nici stergere, nici refuz) -> raman randuri "
        "orfane dupa stergere: " + ", ".join(netratate))


def test_copiii_se_sterg_inaintea_parintelui():
    """Ordinea conteaza: parintele sters primul ar face ca un viitor FK sa pice, iar azi ar lasa
    copiii in urma daca stergerea parintelui esueaza la jumatate."""
    corp = _corp_sterge_salariat()
    parinte = corp.find("DELETE FROM salariati WHERE id")
    assert parinte > 0, "DELETE FROM salariati negasit in sterge_salariat"
    for m in re.finditer(r"DELETE\s+FROM\s+(\w+)\s+WHERE\s+salariat_id", corp, re.I):
        assert m.start() < parinte, \
            "DELETE din %s vine DUPA stergerea parintelui - copiii trebuie stersi inainte" % m.group(1)
