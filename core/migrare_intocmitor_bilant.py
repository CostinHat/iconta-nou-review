"""
core/migrare_intocmitor_bilant.py — întocmitorul bilanțului și interesul public (lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII
„Comanda 10.3”: „Întocmitorul bilanțului: calitatea întocmitorului în profilul cabinetului, interesul public în Date firmă; ambele
blochează dacă lipsesc.”).

Structura ANAF a bilanțului (anaf_surse/structura_SC_1225_270126.txt, S1002 / S1003 / S1005, la fel S1004):
  „15. interes_public Entitati de interes public N(1) DA interes_public=(0,1)”
  „20. nume_intocmit Nume si prenume Intocmit C(75 DA”
  „21. calit_intocmit Calitate intocmit N(2) DA Nomenclator calitate - Intocmit”
  „22. nri_intocmit Numar de inreg.in org.profesional C(15)”
  „22a cif_intocmit CIF intocmit C(13) NU … daca calit_intocmit=(21,22) atunci cif_intocmit#null altfel cif_intocmit=null”
  Nomenclatorul: 11 DIRECTOR ECONOMIC, 12 CONTABIL SEF, 13 ALTA PERSOANA IMPUTERNICITA, POTRIVIT LEGII, 21 PERSOANE FIZICE AUTORIZATE,
  MEMBRE CECCAR, 22 PERSOANE JURIDICE AUTORIZATE, MEMBRE CECCAR.
Generatorul scria `interes_public=0` și `calit_intocmit=12` oricărei firme, iar întocmitorul era administratorul.

Coloane noi, goale (NULL = nedeclarat -> bilanțul se oprește cu refuz numit): `firma_profil.interes_public` (fiecare firmă) și, pe
cabinet, `public.accounting_firms.calit_intocmit` / `nume_intocmit` / `cif_intocmit` / `nri_intocmit`. Datele existente nu se ating.
Sursa UNICĂ a structurii: mirror în tenant_template.sql (firma) și infra/bootstrap_public.sql (cabinetul). Idempotent (IF NOT EXISTS).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_intocmitor_bilant.py`.
"""
from core import db

#: codurile nomenclatorului „calitate - Intocmit” (structura SC 1225, citat mai sus) — sursa unică pentru validare și ecran
CALITATI_INTOCMIT = {11: "Director economic", 12: "Contabil șef", 13: "Altă persoană împuternicită, potrivit legii",
                     21: "Persoană fizică autorizată, membră CECCAR", 22: "Persoană juridică autorizată, membră CECCAR"}

_DDL_PUBLIC = [
    "ALTER TABLE public.accounting_firms ADD COLUMN IF NOT EXISTS calit_intocmit smallint;",
    "ALTER TABLE public.accounting_firms ADD COLUMN IF NOT EXISTS nume_intocmit varchar(75);",
    "ALTER TABLE public.accounting_firms ADD COLUMN IF NOT EXISTS cif_intocmit varchar(13);",
    "ALTER TABLE public.accounting_firms ADD COLUMN IF NOT EXISTS nri_intocmit varchar(15);",
    "ALTER TABLE public.accounting_firms DROP CONSTRAINT IF EXISTS accounting_firms_calit_intocmit_chk;",
    "ALTER TABLE public.accounting_firms ADD CONSTRAINT accounting_firms_calit_intocmit_chk "
    "CHECK (calit_intocmit IS NULL OR calit_intocmit IN (%s));" % ", ".join(str(k) for k in sorted(CALITATI_INTOCMIT)),
]
_DDL_FIRMA = ["ALTER TABLE \"{s}\".firma_profil ADD COLUMN IF NOT EXISTS interes_public boolean;"]


def aplica_public(conn):
    with conn.cursor() as cur:
        for ddl in _DDL_PUBLIC:
            cur.execute(ddl)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL_FIRMA:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil' "
                    "AND column_name = 'interes_public'", (schema,))
        firma = cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='accounting_firms' "
                    "AND column_name IN ('calit_intocmit', 'nume_intocmit', 'cif_intocmit', 'nri_intocmit')")
        return firma and cur.fetchone()[0] == 4


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica_public(conn)
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                aplica(conn, s)
                conn.commit()
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_intocmitor_bilant: cabinetul (public) ok; firme %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
