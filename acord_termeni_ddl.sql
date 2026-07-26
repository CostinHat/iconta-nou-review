-- Acordul cu Termenii si conditiile la crearea contului (cine, cand, ce versiune).
-- Versiunea = linia 3 din TERMENI_SI_CONDITII.md la momentul acceptarii. Dovada de consimtamant.
CREATE TABLE IF NOT EXISTS public.acord_termeni (
  id serial PRIMARY KEY,
  user_id integer,
  cabinet_id integer,
  email text,
  versiune text NOT NULL,
  acceptat_la timestamptz NOT NULL DEFAULT now()
);
