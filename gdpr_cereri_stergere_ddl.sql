-- GDPR art.17: cereri de stergere depuse de cabinet (dovada de primire).
-- Cabinetul CERE din aplicatie; superadmin executa manual (core.gdpr_sterge).
-- Aceasta tabela NU sterge nimic — supravietuieste stergerii, FARA date personale.
CREATE TABLE IF NOT EXISTS public.gdpr_cereri_stergere (
  id serial PRIMARY KEY,
  cabinet_id integer NOT NULL,
  cerut_de_user_id integer,
  nume_cabinet text,                       -- denumirea la momentul cererii (typed-back)
  motiv text,                              -- optional, dat de cabinet
  stare text NOT NULL DEFAULT 'primita',    -- primita | in_lucru | executata | respinsa
  cerut_la timestamptz NOT NULL DEFAULT now(),
  procesat_de_user_id integer,
  procesat_la timestamptz,
  detalii jsonb
);
