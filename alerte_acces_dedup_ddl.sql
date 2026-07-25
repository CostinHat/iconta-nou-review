-- GDPR art.33: dedup persistent pentru alertele de acces anormal (cron, nu in-memory).
CREATE TABLE IF NOT EXISTS public.alerte_acces_dedup (
  cheie text PRIMARY KEY,
  trimis_la timestamptz NOT NULL DEFAULT now()
);
