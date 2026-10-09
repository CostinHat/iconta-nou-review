# -*- coding: utf-8 -*-
"""core/migrare_validare_note.py — coada de validare extinsă la note (comanda Costin 06.10.2026, pct.1, varianta (a)).

Sursa UNICĂ a DDL-ului (oglindit în `infra/bootstrap_public.sql` și `tenant_template.sql`). Idempotent.
Aplică pe existenți: `python3 -m core.migrare_validare_note`.

  public.declaratii_coada.fel  — 'declaratie' | 'nota'. Coada era a declarațiilor; elementele noi sunt notele pregătite de un
                                 asistent. Consumatorii care vorbesc DOAR despre declarații (tiparele respingerilor, depunerea)
                                 filtrează pe `fel`; cei care vorbesc despre „ce a pregătit asistentul” (contorul, Activitate
                                 cabinet, sinteza zilnică) le văd pe amândouă.
  <tenant>.inregistrari.creat_de_id — autorul notei, luat din cerere (`core/autor_cerere.py`): valoarea implicită citește
                                 `current_setting('iconta.utilizator', true)`, pe care `db.get_conn` îl scrie pe tranzacție.
                                 Toate drumurile de INSERT îl primesc fără să fie atinse; notele vechi rămân NULL (nu intră
                                 în coadă — nu se atinge trecutul).
  <tenant>.coada_nota_sincron  — trigger: nota VALIDATĂ din jurnal închide elementul ei din coadă ('aprobata', cu cine și
                                 când); nota ȘTEARSĂ cât e încă la validare îi scoate elementul. Coada și jurnalul nu pot
                                 spune lucruri diferite despre aceeași notă, oricare ar fi drumul pe care s-a validat."""
from core import db

DDL_PUBLIC = """
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS fel text NOT NULL DEFAULT 'declaratie';
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_coada_fel' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.declaratii_coada ADD CONSTRAINT declaratii_coada_fel CHECK (fel IN ('declaratie', 'nota'));
  END IF;
END $$;
"""

DDL_TENANT = """
ALTER TABLE "{s}".inregistrari ADD COLUMN IF NOT EXISTS creat_de_id integer
  DEFAULT NULLIF(current_setting('iconta.utilizator', true), '')::integer;
CREATE OR REPLACE FUNCTION "{s}".coada_nota_sincron() RETURNS trigger AS $$
DECLARE t_id integer;
BEGIN
  SELECT id INTO t_id FROM public.tenants WHERE schema_name = TG_TABLE_SCHEMA;
  IF t_id IS NULL THEN
    RETURN NULL;
  END IF;
  IF TG_OP = 'DELETE' THEN
    DELETE FROM public.declaratii_coada
     WHERE tenant_id = t_id AND fel = 'nota' AND perioada = 'nota-' || OLD.id AND stare = 'la_senior';
    RETURN OLD;
  END IF;
  IF NEW.status = 'validata' AND OLD.status IS DISTINCT FROM 'validata' THEN
    UPDATE public.declaratii_coada
       SET stare = 'aprobata', aprobat_la = now(),
           aprobat_de_id = NULLIF(current_setting('iconta.utilizator', true), '')::integer,
           aprobat_de = NULLIF(current_setting('iconta.utilizator', true), '')
     WHERE tenant_id = t_id AND fel = 'nota' AND perioada = 'nota-' || NEW.id AND stare = 'la_senior';
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_coada_nota_sincron ON "{s}".inregistrari;
CREATE TRIGGER trg_coada_nota_sincron AFTER UPDATE OF status OR DELETE ON "{s}".inregistrari
  FOR EACH ROW EXECUTE FUNCTION "{s}".coada_nota_sincron();
"""


def aplica_public(conn):
    with conn.cursor() as cur:
        cur.execute(DDL_PUBLIC)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL_TENANT.replace("{s}", schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='inregistrari' "
                    "AND column_name='creat_de_id'", (schema,))
        col = cur.fetchone() is not None
        cur.execute("SELECT 1 FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = %s AND c.relname = 'inregistrari' AND t.tgname = 'trg_coada_nota_sincron'", (schema,))
        return col and cur.fetchone() is not None


def scheme_cu_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_name='inregistrari' "
                    "AND table_schema ~ '^tenant_' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica_public(conn)
        conn.commit()
        print("migrare validare_note (public.declaratii_coada.fel): ok")
        scheme = scheme_cu_tabela(conn)
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare validare_note (tenanti): %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
