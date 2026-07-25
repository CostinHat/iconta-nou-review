-- GDPR art.17: jurnal de stergere cabinet. Supravietuieste stergerii; FARA date personale.
CREATE TABLE IF NOT EXISTS public.gdpr_stergeri (
  id serial PRIMARY KEY,
  cabinet_id integer NOT NULL,
  nr_tenanti integer NOT NULL DEFAULT 0,
  nr_useri integer NOT NULL DEFAULT 0,
  scheme_sterse text[] NOT NULL DEFAULT '{}',
  sters_de_user_id integer,
  sters_la timestamptz NOT NULL DEFAULT now(),
  detalii jsonb
);
