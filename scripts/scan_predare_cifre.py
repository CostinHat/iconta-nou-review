# -*- coding: utf-8 -*-
"""Cifrele despre DATE din `PREDARE_LANT.md`, interogate din bază — blocul generat.

DE CE EXISTĂ, cu instanța ei. Pe 28.08.2026 am scris în predare *„**0 din 18** firme au
`nume_anaf`"*. Recitit pe date, douăzeci de minute mai târziu: **1 din 18**. Cifra fusese **deja
invalidată o dată**, iar corectura era scrisă în tabelul „cifre invalidate" **din aceeași predare**.
Am purtat-o mai departe din memorie — la douăzeci de minute după ce scrisesem `METODA §10.16`, regula
care interzice exact asta.

Concluzia, și e a metodei, nu a atenției: *o regulă scrisă nu ține fără control mecanic* (§14,
aplicată unei reguli din §10). Recitirea nu e „mai multă grijă" — e **o comandă rulată**.

CE ACOPERĂ: cifrele despre **date** — portofoliu, cabinete, divergențe, instantanee ANAF, urme de
scoatere, scheme, contor, orfani, duplicate. Fiecare a fost, cel puțin o dată, scrisă greșit.

CE NU ACOPERĂ, declarat, și nu din lene:
  - **cifrele despre COD** (rute, gărzi, teste) — au deja instrumentele lor, fiecare cu garda ei;
  - **cifrele despre PROCES** („a câta tură", „câte commituri în urmă") — nu se pot interoga de
    nicăieri; rămân afirmații datate, cu ora citirii (`METODA §10.16b`, Y2);
  - **judecățile** — „ce nu e adevărat despre starea asta" e proză, și rămâne proză.

**BLOCUL NU POARTĂ ORA MĂSURĂTORII.** Ar fi fost firesc s-o poarte, și e greșit: garda compară
documentul cu interogarea de la rulare, iar o oră scrisă în bloc ar face comparația să pice
întotdeauna. Ora trăiește în raport și în antetul predării, unde e o afirmație despre **când**, nu o
cifră despre **ce**. (Aceeași lecție ca la inventarul din `GARZI.md`, unde datele au ieșit din bloc
din același motiv, cu două ore înainte.)

  ./venv/bin/python scripts/scan_predare_cifre.py --md
"""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

MARCA_START = "<!-- CIFRE-DATE:START (generat de scripts/scan_predare_cifre.py --md) -->"
MARCA_STOP = "<!-- CIFRE-DATE:STOP -->"

# Aceeași regulă ca la clichetul de divergențe (X1, `core/test_nume_firma_unic.py`): un cabinet al
# cărui nume conține cuvântul TEST sau PROBA e mediu de test. **Nu se duplică regula, se importă** —
# două tipare pe același lucru se despart în tăcere (lecția R62).
_RE_TENANT_NR = re.compile(r"^tenant_(\d+)$")


def _nrm(s):
    return " ".join(str(s or "").split()).lower()


def culege(conn):
    """{cheie: valoare} — o singură trecere prin bază, fără nimic ținut minte."""
    from core.test_nume_firma_unic import _RE_CABINET_DE_TEST
    from core import tenant_stergere as ts
    from core.migrare_schema_seq import maxim_istoric

    d = {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, nume FROM public.accounting_firms ORDER BY id")
        cabinete = cur.fetchall()
        de_test = {i for i, n in cabinete if _RE_CABINET_DE_TEST.search(n or "")}
        d["cabinete"] = len(cabinete)
        d["cabinete_de_test"] = len(de_test)

        cur.execute("SELECT id, nume, schema_name, accounting_firm_id, activ, nume_anaf, nume_ales "
                    "FROM public.tenants ORDER BY id")
        firme = cur.fetchall()
        d["firme"] = len(firme)
        d["firme_active"] = sum(1 for f in firme if f[4])
        d["firme_reale"] = sum(1 for f in firme if f[3] not in de_test)
        d["firme_de_test"] = sum(1 for f in firme if f[3] in de_test)

        # divergențe de denumire, pe amândouă populațiile
        div_tot, div_reale = 0, 0
        for tid, nume, schema, cab, _a, _na, _nl in firme:
            try:
                cur.execute('SELECT nume FROM "%s".firma_profil WHERE id = 1' % schema)
                r = cur.fetchone()
            except Exception:
                conn.rollback()
                continue
            fiscal = r[0] if r else None
            if fiscal and _nrm(nume) != _nrm(fiscal):
                div_tot += 1
                if cab not in de_test:
                    div_reale += 1
        d["divergente_toate"] = div_tot
        d["divergente_reale"] = div_reale

        # instantaneul ANAF: câte îl au, la câte diferă, la câte s-a ales deja
        cu_anaf = [f for f in firme if (f[5] or "").strip()]
        d["cu_nume_anaf"] = len(cu_anaf)
        d["cu_nume_anaf_divergent"] = sum(1 for f in cu_anaf if _nrm(f[5]) != _nrm(f[1]))
        d["cu_alegere_consemnata"] = sum(1 for f in cu_anaf if f[6])

        cur.execute("SELECT count(*), count(DISTINCT schema_name) FROM public.firme_scoase")
        n_fs, n_sch = cur.fetchone()
        d["firme_scoase"] = n_fs
        d["firme_scoase_scheme_distincte"] = n_sch

        cur.execute("SELECT count(*) FROM information_schema.schemata "
                    "WHERE schema_name ~ '^tenant_[0-9]+$'")
        d["scheme_tenant"] = cur.fetchone()[0]

        cur.execute("SELECT last_value, is_called FROM public.tenant_schema_seq")
        last, chemat = cur.fetchone()
        d["contor_schema"] = last if chemat else last - 1
        d["maxim_istoric_schema"] = maxim_istoric(conn)

        orfani = 0
        for tabel in ts.TABELE_TENANT:
            cur.execute('SELECT count(*) FROM public."%s" x WHERE x.tenant_id IS NOT NULL '
                        'AND NOT EXISTS (SELECT 1 FROM public.tenants p WHERE p.id=x.tenant_id)'
                        % tabel)
            orfani += cur.fetchone()[0]
        d["orfani"] = orfani
        d["tabele_cu_tenant_id"] = len(ts.TABELE_TENANT)

        cur.execute("""SELECT count(*) FROM (
                         SELECT accounting_firm_id,
                                lower(btrim(regexp_replace(nume, '\\s+', ' ', 'g'))) AS n
                         FROM public.tenants WHERE accounting_firm_id IS NOT NULL
                         GROUP BY 1, 2 HAVING count(*) > 1) x""")
        d["duplicate_nume_in_cabinet"] = cur.fetchone()[0]
    return d


RANDURI = [
    ("Portofoliu", [
        ("firme", "firme în portofoliu"),
        ("firme_active", "din care active"),
        ("firme_reale", "la cabinete reale"),
        ("firme_de_test", "la cabinete de test"),
        ("duplicate_nume_in_cabinet", "perechi de firme cu același nume în același cabinet"),
    ]),
    ("Cabinete", [
        ("cabinete", "cabinete"),
        ("cabinete_de_test", "din care declarate de test (tipar pe nume: TEST / PROBA)"),
    ]),
    ("Denumirea firmei (R81)", [
        ("divergente_reale", "divergențe portofoliu ↔ fiscal, pe populația declarată"),
        ("divergente_toate", "divergențe pe TOATĂ populația, fără nicio excludere"),
        ("cu_nume_anaf", "firme cu instantaneu ANAF (`nume_anaf`)"),
        ("cu_nume_anaf_divergent", "din care cu denumirea DIFERITĂ de cea de la ANAF"),
        ("cu_alegere_consemnata", "din care cu alegerea deja consemnată (deci caseta nu apare)"),
    ]),
    ("Scoatere și scheme (R79)", [
        ("firme_scoase", "rânduri în `public.firme_scoase`"),
        ("firme_scoase_scheme_distincte", "nume de schemă distincte în ele"),
        ("scheme_tenant", "scheme `tenant_NNN` în bază"),
        ("contor_schema", "contorul `tenant_schema_seq`"),
        ("maxim_istoric_schema", "maximul istoric de nume de schemă"),
    ]),
    ("Referințe moarte", [
        ("orfani", "rânduri care trimit la o firmă inexistentă"),
        ("tabele_cu_tenant_id", "tabele din `public` cu `tenant_id`, numărate"),
    ]),
]


def redare_md(d):
    linii = [MARCA_START, ""]
    linii.append("*Generat din bază. **Nu se scrie cu mâna** — `core/test_predare_cifre.py` compară "
                 "blocul cu interogarea curentă și pică dacă diferă. Regenerare: "
                 "`./venv/bin/python scripts/scan_predare_cifre.py --md`.*")
    linii.append("")
    for titlu, campuri in RANDURI:
        linii.append("**%s**" % titlu)
        linii.append("")
        linii.append("| cifra | ce e |")
        linii.append("|---|---|")
        for cheie, eticheta in campuri:
            linii.append("| **%s** | %s |" % (d[cheie], eticheta))
        linii.append("")
    linii.append(MARCA_STOP)
    return "\n".join(linii)


def main():
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        d = culege(conn)
    if "--md" in sys.argv:
        print(redare_md(d))
        return 0
    for k in sorted(d):
        print("  %-32s %s" % (k, d[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
