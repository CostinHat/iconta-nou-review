# -*- coding: utf-8 -*-
"""core/migrare_decizii_0810.py — partea de bază a lotului „Deciziile 08.10” (comanda Costin, verbatim în DECIZII 08.10.2026).

  · pct.4  „Notificările fără element (44, 45, 46, 48) nu rămân active în clopoțel: se marchează rezolvate, cu motivul «elementul
           nu mai există».”
           CLASA (nu cele patru rânduri): o notificare DE ACȚIUNE (`de_validat`, `respinsa`) a cărei legătură nu numește elementul
           (`link = 'validat'`, rezerva veche din `uc_comun` când lipsea id-ul din coadă) nu se poate rezolva niciodată — nici
           triggerul S4, nici `rezolva_nota_inlocuita` n-au după ce s-o găsească. Măsurat pe producție 08.10: 44, 46, 48
           (`de_validat`) și 45 (`respinsa`).
             1. `rezolvata` primește valoarea `inexistent` („elementul nu mai există”);
             2. notificările de acțiune fără element existente -> `inexistent`;
             3. GARD în bază: `notificari_element_ck` — o notificare de acțiune nerezolvată POARTĂ elementul
                (`validat:<id>` sau `jurnal:<firmă>:<notă>…`). Reapariția clasei e imposibilă, nu improbabilă;
             4. declarația respinsă (`respinsa`, `validat:<id>`) se rezolvă `inlocuit` când aceeași declarație (firmă, tip,
                perioadă) intră din nou în coadă, și `inexistent` când elementul dispare.
  · U2     declarația marcată „depusă în afara iConta” poartă recipisa (opțională): coloana `declaratii_depuse.recipisa`.
  · retest 08.10 pct.3  elementele „notă” dinaintea lui S3 primesc `payload.doc` (`doc_in_coada`), ca refacerea documentului să
           le găsească respingerea.
Sursa UNICĂ (mirror în infra/bootstrap_public.sql). Idempotentă. `python3 -m core.migrare_decizii_0810`.
"""
from core import db

#: tipurile de notificare care cer o acțiune și se rezolvă prin elementul lor
TIPURI_DE_ACTIUNE = ("de_validat", "respinsa")
#: legătura care numește elementul (coada sau nota din Registrul jurnal)
LINK_CU_ELEMENT = "^(validat|jurnal):[0-9]+"

SQL_PUBLIC = """DO $$ BEGIN
  ALTER TABLE public.notificari DROP CONSTRAINT IF EXISTS notificari_rezolvata_ck;
  ALTER TABLE public.notificari ADD CONSTRAINT notificari_rezolvata_ck
    CHECK (rezolvata IS NULL OR rezolvata IN ('validat', 'respins', 'inlocuit', 'inexistent'));
END $$;
UPDATE public.notificari SET rezolvata = 'inexistent', rezolvata_la = now()
 WHERE tip IN ('de_validat', 'respinsa') AND rezolvata IS NULL AND (link IS NULL OR link !~ '^(validat|jurnal):[0-9]+');
-- COALESCE: un CHECK cu `link` NULL ar da NULL, iar Postgres trece un CHECK NULL (prins de garda la prima rulare)
ALTER TABLE public.notificari DROP CONSTRAINT IF EXISTS notificari_element_ck;
ALTER TABLE public.notificari ADD CONSTRAINT notificari_element_ck
  CHECK (tip NOT IN ('de_validat', 'respinsa') OR rezolvata IS NOT NULL OR COALESCE(link, '') ~ '^(validat|jurnal):[0-9]+');
CREATE OR REPLACE FUNCTION public.notificari_rezolva_din_coada() RETURNS trigger LANGUAGE plpgsql AS $f$
BEGIN
  -- [08.10] aceeași declarație (firmă, tip, perioadă) intră din nou în coadă: „a fost respinsă” a celei vechi e înlocuită
  IF TG_OP = 'INSERT' THEN
    UPDATE public.notificari SET rezolvata = 'inlocuit', rezolvata_la = now()
     WHERE tip = 'respinsa' AND rezolvata IS NULL AND link IN (
           SELECT 'validat:' || c.id FROM public.declaratii_coada c
            WHERE c.tenant_id = NEW.tenant_id AND c.tip = NEW.tip AND c.perioada = NEW.perioada AND c.stare = 'respinsa'
              AND c.id <> NEW.id);
    RETURN NEW;
  END IF;
  -- elementul din coadă își schimbă starea (sau dispare): notificarea „de validat” care duce la el devine REZOLVATĂ
  IF TG_OP = 'DELETE' THEN
    UPDATE public.notificari SET rezolvata = 'inlocuit', rezolvata_la = now()
     WHERE tip = 'de_validat' AND rezolvata IS NULL AND link = 'validat:' || OLD.id;
    UPDATE public.notificari SET rezolvata = 'inexistent', rezolvata_la = now()
     WHERE tip = 'respinsa' AND rezolvata IS NULL AND link = 'validat:' || OLD.id;
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
CREATE TRIGGER declaratii_coada_rezolva_notificari AFTER INSERT OR UPDATE OF stare OR DELETE ON public.declaratii_coada
  FOR EACH ROW EXECUTE FUNCTION public.notificari_rezolva_din_coada();
-- [08.10, decizia Costin U2] „O declarație anterioară se poate marca «depusă în afara iConta», cu recipisă opțională.” (sursa = 'extern')
ALTER TABLE public.declaratii_depuse ADD COLUMN IF NOT EXISTS recipisa text;"""


def public_ddl(conn):
    """O singură dată pe bază (public). Întoarce [(id, tip, link)] — notificările marcate acum „elementul nu mai există”."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, tip, link FROM public.notificari WHERE tip IN ('de_validat', 'respinsa') AND rezolvata IS NULL "
                    "AND (link IS NULL OR link !~ %s) ORDER BY id", (LINK_CU_ELEMENT,))
        marcate = [tuple(r) for r in cur.fetchall()]
        cur.execute(SQL_PUBLIC)
    return marcate


#: [W2] codul de clasificare din Catalogul HG 2139/2004, pe mijlocul fix (mirror în tenant_template.sql)
DDL_SCHEMA = ['ALTER TABLE "{s}".mijloace_fixe ADD COLUMN IF NOT EXISTS cod_catalog text;']


def aplica(conn, schema):
    """DDL-ul pe schema unei firme. False dacă schema n-are `mijloace_fixe`."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='mijloace_fixe'", (schema,))
        if not cur.fetchone():
            return False
        for d in DDL_SCHEMA:
            cur.execute(d.format(s=schema))
    return True


def doc_in_coada(conn):
    """[retest 08.10 pct.3] Elementele „notă” din coadă scrise ÎNAINTEA lui S3 (07.10) n-au `payload.doc` — documentul notei —, deci
    `coada_api.retrimisa` (care caută respingerea anterioară după `doc`) nu le găsea: NIR-ul refăcut din NIR 1 (F1) nu arăta
    „retrimis după respingere”. Se completează cu definiția unică (`coada_api.cheie_document`), hash refăcut; nicio stare nu se
    schimbă. Întoarce [(coada_id, doc)]."""
    import psycopg2.extras as _E
    from core import coada_api as _c
    out = []
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id, payload FROM public.declaratii_coada WHERE fel = 'nota' AND NOT (payload ? 'doc') ORDER BY id")
        for r in cur.fetchall():
            p = dict(r["payload"] or {})
            p["doc"] = _c.cheie_document(p)
            p.setdefault("doc_anterior", p["doc"])
            cur.execute("UPDATE public.declaratii_coada SET payload = %s, hash = %s WHERE id = %s", (_E.Json(p), _c.calcul_hash(p), r["id"]))
            out.append((r["id"], p["doc"]))
    return out


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        marcate = public_ddl(conn)
        conn.commit()
    print("notificări fără element, marcate «elementul nu mai există»: %d %s" % (len(marcate), marcate))
    with db.get_conn() as conn:
        doc = doc_in_coada(conn)
        conn.commit()
    print("elemente din coadă cu documentul completat (retest 08.10 pct.3): %d %s" % (len(doc), doc))
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
            scheme = [x[0] for x in cur.fetchall()]
        ok = 0
        for s in scheme:
            try:
                ok += 1 if aplica(conn, s) else 0
                conn.commit()
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                print("  ESEC", s, e)
    print("cod_catalog pe mijloace_fixe: %d/%d scheme" % (ok, len(scheme)))


if __name__ == "__main__":
    _main()
