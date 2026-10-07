# -*- coding: utf-8 -*-
"""core/migrare_decizii_0710.py — schema lotului „Deciziile 07.10” + retesturile din 07.10 (comenzile Costin, verbatim în DECIZII).

  · D5  `firma_profil.serie_chitanta` fără „CH” din oficiu: implicitul cade; valoarea „CH” pe care n-a folosit-o nicio chitanță e
        implicitul vechi, nu o alegere -> NULL (seria se cere la prima chitanță). Seria cu chitanțe emise rămâne.
  · D2  `nir.factura_id` (NIR-ul legat de factura primită; cheie fără `ON DELETE` + index unic: o factură, un NIR).
  · R1  `miscari_stoc.nir_id` (intrarea NIR-ului; completată pentru NIR-urile existente din eticheta documentului, numai unde
        potrivirea e unică), `miscari_stoc.anuleaza_id` (stornarea la respingere; index unic: o mișcare se stornează o dată),
        `nir.refacut_din_id` (NIR-ul care reface unul respins; index unic).
  · D3  `miscari_stoc.z_inregistrare_id` (ieșirea pe articol care descarcă un raport Z), `rapoarte_z_amef.fara_marfa`
        (declarația explicită „fără marfă din stoc”; NULL = nedeclarat).
  · S1  `elemente_salariale` (prime, sporuri, ore suplimentare pe salariat și pe lună — `core/elemente_salariale.py`).
  · R2  elementele „notă” din coadă primesc `partener` în payload (titlul scurt: document · partener · N note), cu `hash`-ul
        refăcut — ca `migrare_grup_coada`; nicio stare nu se schimbă.
Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). Idempotentă. `python3 -m core.migrare_decizii_0710` (DDL + date).
"""
from core import db

DDL = [
    # D5
    'ALTER TABLE "{s}".firma_profil ALTER COLUMN serie_chitanta DROP DEFAULT;',
    # D2
    'ALTER TABLE "{s}".nir ADD COLUMN IF NOT EXISTS factura_id integer;',
    """DO $m$ BEGIN
         IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='nir_factura_fk' AND connamespace='"{s}"'::regnamespace) THEN
           ALTER TABLE "{s}".nir ADD CONSTRAINT nir_factura_fk FOREIGN KEY (factura_id) REFERENCES "{s}".facturi(id);
         END IF; END $m$;""",
    'CREATE UNIQUE INDEX IF NOT EXISTS nir_factura_id_uq ON "{s}".nir (factura_id) WHERE factura_id IS NOT NULL;',
    # R1
    'ALTER TABLE "{s}".miscari_stoc ADD COLUMN IF NOT EXISTS nir_id integer;',
    'ALTER TABLE "{s}".miscari_stoc ADD COLUMN IF NOT EXISTS anuleaza_id integer;',
    """DO $m$ BEGIN
         IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='miscari_stoc_nir_fk' AND connamespace='"{s}"'::regnamespace) THEN
           ALTER TABLE "{s}".miscari_stoc ADD CONSTRAINT miscari_stoc_nir_fk FOREIGN KEY (nir_id) REFERENCES "{s}".nir(id);
         END IF;
         IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='miscari_stoc_anuleaza_fk' AND connamespace='"{s}"'::regnamespace) THEN
           ALTER TABLE "{s}".miscari_stoc ADD CONSTRAINT miscari_stoc_anuleaza_fk FOREIGN KEY (anuleaza_id) REFERENCES "{s}".miscari_stoc(id);
         END IF; END $m$;""",
    'CREATE UNIQUE INDEX IF NOT EXISTS miscari_stoc_anuleaza_uq ON "{s}".miscari_stoc (anuleaza_id) WHERE anuleaza_id IS NOT NULL;',
    'ALTER TABLE "{s}".nir ADD COLUMN IF NOT EXISTS refacut_din_id integer;',
    'CREATE UNIQUE INDEX IF NOT EXISTS nir_refacut_din_uq ON "{s}".nir (refacut_din_id) WHERE refacut_din_id IS NOT NULL;',
    # D3
    'ALTER TABLE "{s}".miscari_stoc ADD COLUMN IF NOT EXISTS z_inregistrare_id integer;',
    """DO $m$ BEGIN
         IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='miscari_stoc_z_fk' AND connamespace='"{s}"'::regnamespace) THEN
           ALTER TABLE "{s}".miscari_stoc ADD CONSTRAINT miscari_stoc_z_fk FOREIGN KEY (z_inregistrare_id)
             REFERENCES "{s}".inregistrari(id) ON DELETE SET NULL;
         END IF; END $m$;""",
    'ALTER TABLE "{s}".rapoarte_z_amef ADD COLUMN IF NOT EXISTS fara_marfa boolean;',
    # S1
    """CREATE TABLE IF NOT EXISTS "{s}".elemente_salariale (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    salariat_id integer NOT NULL REFERENCES "{s}".salariati(id) ON DELETE CASCADE,
    an integer NOT NULL,
    luna integer NOT NULL CHECK (luna BETWEEN 1 AND 12),
    tip text NOT NULL CHECK (tip IN ('prima', 'spor', 'ore_suplimentare')),
    denumire text NOT NULL CHECK (length(btrim(denumire)) > 0),
    ore numeric(7,2) CHECK (ore IS NULL OR ore > 0),
    suma numeric(12,2) NOT NULL CHECK (suma > 0),
    creat_la timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT elemente_salariale_ore_ck CHECK ((tip = 'ore_suplimentare') = (ore IS NOT NULL))
);""",
    'CREATE INDEX IF NOT EXISTS elemente_salariale_luna_ix ON "{s}".elemente_salariale (an, luna, salariat_id);',
]

#: D5 — „CH” fără nicio chitanță emisă cu ea = implicitul vechi al schemei, nu o alegere
DATE_SERIE = """UPDATE "{s}".firma_profil fp SET serie_chitanta = NULL
                WHERE fp.serie_chitanta = 'CH' AND NOT EXISTS (SELECT 1 FROM "{s}".chitante c WHERE c.serie = 'CH')"""

#: R1 — intrarea NIR-ului (scrisă cu eticheta „NIR nr <n> din <zz.ll.aaaa>”, `jurnal_api.eticheta_document`) primește `nir_id`;
#: numai unde exact un NIR are acea etichetă și acea dată
DATE_NIR_ID = """UPDATE "{s}".miscari_stoc m SET nir_id = n.id
                 FROM "{s}".nir n
                 WHERE m.nir_id IS NULL AND m.anuleaza_id IS NULL AND m.tip = 'intrare' AND m.factura_id IS NULL
                   AND m.data = n.data AND m.document = 'NIR nr ' || n.numar || ' din ' || to_char(n.data, 'DD.MM.YYYY')
                   AND (SELECT count(*) FROM "{s}".nir n2 WHERE n2.numar = n.numar AND n2.data = n.data) = 1"""


#: S4 — `public.notificari.rezolvata` + triggerul de pe coadă (mirror în infra/bootstrap_public.sql)
SQL_PUBLIC = """ALTER TABLE public.notificari ADD COLUMN IF NOT EXISTS rezolvata text;
ALTER TABLE public.notificari ADD COLUMN IF NOT EXISTS rezolvata_la timestamp with time zone;
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='notificari_rezolvata_ck' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.notificari ADD CONSTRAINT notificari_rezolvata_ck
      CHECK (rezolvata IS NULL OR rezolvata IN ('validat', 'respins', 'inlocuit'));
  END IF;
END $$;
CREATE OR REPLACE FUNCTION public.notificari_rezolva_din_coada() RETURNS trigger LANGUAGE plpgsql AS $f$
BEGIN
  -- elementul din coadă își schimbă starea (sau dispare): notificarea „de validat” care duce la el devine REZOLVATĂ
  IF TG_OP = 'DELETE' THEN
    UPDATE public.notificari SET rezolvata = 'inlocuit', rezolvata_la = now()
     WHERE tip = 'de_validat' AND rezolvata IS NULL AND link = 'validat:' || OLD.id;
    RETURN OLD;
  END IF;
  IF OLD.stare = 'la_senior' AND NEW.stare IS DISTINCT FROM OLD.stare THEN
    UPDATE public.notificari SET rezolvata = CASE WHEN NEW.stare = 'respinsa' THEN 'respins' ELSE 'validat' END,
           rezolvata_la = now()
     WHERE tip = 'de_validat' AND rezolvata IS NULL AND link = 'validat:' || NEW.id;
  END IF;
  RETURN NEW;
END $f$;
DROP TRIGGER IF EXISTS declaratii_coada_rezolva_notificari ON public.declaratii_coada;
CREATE TRIGGER declaratii_coada_rezolva_notificari AFTER UPDATE OF stare OR DELETE ON public.declaratii_coada
  FOR EACH ROW EXECUTE FUNCTION public.notificari_rezolva_din_coada();"""

#: S4 — notificările existente: cele „de validat” ale căror elemente nu mai sunt la validare (sau nu mai există) se rezolvă
DATE_NOTIFICARI = """UPDATE public.notificari n SET rezolvata = CASE WHEN c.id IS NULL THEN 'inlocuit'
                                                                  WHEN c.stare = 'respinsa' THEN 'respins' ELSE 'validat' END,
                            rezolvata_la = now()
                     FROM (SELECT n2.id AS nid, split_part(n2.link, ':', 2)::int AS cid FROM public.notificari n2
                           WHERE n2.tip = 'de_validat' AND n2.rezolvata IS NULL AND n2.link ~ '^validat:[0-9]+$') x
                     LEFT JOIN public.declaratii_coada c ON c.id = x.cid
                     WHERE n.id = x.nid AND (c.id IS NULL OR c.stare <> 'la_senior')"""


def public_ddl(conn):
    """S4 — o singură dată pe bază (public). Întoarce câte notificări existente s-au rezolvat."""
    with conn.cursor() as cur:
        cur.execute(SQL_PUBLIC)
        cur.execute(DATE_NOTIFICARI)
        return cur.rowcount


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='nir'", (schema,))
        if not cur.fetchone():
            return False
        for d in DDL:
            cur.execute(d.format(s=schema))
        cur.execute(DATE_SERIE.format(s=schema))
        cur.execute(DATE_NIR_ID.format(s=schema))
    return True


def storneaza_respinse(conn, schema, tenant_id):
    """R1 — documentele DEJA respinse în coadă (ultimul element al notei e `respinsa`) își primesc stornarea, ca la o respingere de
    azi. Întoarce [(grup, stornate | eroare)]."""
    from core import stocuri_anulare as _sa
    with conn.cursor() as cur:
        cur.execute("""SELECT payload->>'grup', array_agg((payload->>'inregistrare_id')::int ORDER BY id), max(motiv_respingere)
                       FROM (SELECT DISTINCT ON (perioada) id, perioada, stare, payload, motiv_respingere FROM public.declaratii_coada
                             WHERE tenant_id = %s AND fel = 'nota' ORDER BY perioada, id DESC) u
                       WHERE stare = 'respinsa' AND payload->>'inregistrare_id' IS NOT NULL GROUP BY 1 ORDER BY 1""", (tenant_id,))
        grupuri = cur.fetchall()
    out = []
    for grup, note, motiv in grupuri:
        r = _sa.storneaza(conn, schema, grup, note, motiv)
        out.append((grup, r.get("eroare") or r.get("stornate")))
    return out


def partener_in_coada(conn, tenant_id=None):
    """R2 — `partener` în payload-ul elementelor „notă” care nu-l au (aceeași definiție: `coada_api._PARTENER`).
    Întoarce [(coada_id, partener)]."""
    import psycopg2.extras as _E
    from core import coada_api as _c
    schimbate = []
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cond, val = "c.fel = 'nota' AND NOT (c.payload ? 'partener')", []
        if tenant_id is not None:
            cond += " AND c.tenant_id = %s"
            val.append(tenant_id)
        cur.execute("SELECT c.id, c.payload, c.perioada, t.schema_name FROM public.declaratii_coada c "
                    "JOIN public.tenants t ON t.id = c.tenant_id WHERE " + cond + " ORDER BY c.id", val)
        for r in cur.fetchall():
            if not db.schema_valida(r["schema_name"]):
                continue
            nota_id = int(str(r["perioada"]).split("-", 1)[1])
            cur.execute('SET LOCAL search_path TO "%s", public' % r["schema_name"])
            cur.execute("SELECT " + _c._PARTENER + " AS partener FROM inregistrari i LEFT JOIN facturi f ON f.id = i.factura_id "
                        "WHERE i.id = %s", (nota_id,))
            x = cur.fetchone()
            p = dict(r["payload"] or {})
            p["partener"] = x["partener"] if x else None
            cur.execute("UPDATE public.declaratii_coada SET payload = %s, hash = %s WHERE id = %s",
                        (_E.Json(p), _c.calcul_hash(p), r["id"]))
            schimbate.append((r["id"], p["partener"]))
        cur.execute("RESET search_path")
    return schimbate


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("""SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND (
                         (table_name='nir' AND column_name IN ('factura_id','refacut_din_id'))
                      OR (table_name='miscari_stoc' AND column_name IN ('nir_id','anuleaza_id','z_inregistrare_id'))
                      OR (table_name='rapoarte_z_amef' AND column_name = 'fara_marfa')
                      OR (table_name='elemente_salariale' AND column_name = 'suma'))""", (schema,))
        n = cur.fetchone()[0]
        cur.execute("""SELECT column_default FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil'
                       AND column_name='serie_chitanta'""", (schema,))
        r = cur.fetchone()
    return n == 7 and (r is None or r[0] is None)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT t.schema_name, t.id FROM public.tenants t JOIN information_schema.tables x "
                        "ON x.table_schema = t.schema_name AND x.table_name = 'nir' ORDER BY t.id")
            scheme = cur.fetchall()
        ok, esec = 0, []
        try:
            print("notificări rezolvate (S4): %d" % public_ddl(conn))
            conn.commit()
        except Exception as e:  # noqa: BLE001
            conn.rollback()
            esec.append(("public", "S4: %s" % e))
        for s, tid in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare decizii_0710 (DDL): %d/%d ok" % (ok, len(scheme)))
        for s, tid in scheme:
            try:
                rez = storneaza_respinse(conn, s, tid)
                conn.commit()
                for g, r in rez:
                    print("  storno respinse %s %s: %s" % (s, g, r))
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, "storno: %s" % e))
        try:
            pc = partener_in_coada(conn)
            conn.commit()
            print("partener în coadă: %d elemente" % len(pc))
        except Exception as e:  # noqa: BLE001
            conn.rollback()
            esec.append(("coada", "partener: %s" % e))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
