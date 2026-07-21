-- 09_ddl_d390_clasificare.sql
-- F125: clasificare manuala D390. Auto-maparea (d390.calcul_d390) transforma orice factura
-- intracomunitara in BUNURI (emisa->L, primita->A). Contabilul poate:
--   (a) RECLASIFICA o operatiune auto-derivata (partener + directie) la alt tip D390
--       - emisa: L(bunuri) / T(triangulatie) / P(serviciu prestat) / R(agricol special)
--       - primita: A(bunuri) / S(serviciu primit)
--       -> d390_reclasificare (override tipul, NU adauga -> fara dubla numarare)
--   (b) ADAUGA linii pur manuale (operatiuni fara factura in sistem) -> d390_manual
-- Ambele per tenant/an/luna. Idempotent. Ruleaza:
--   sudo -u postgres psql -d iconta_v2 -f 09_ddl_d390_clasificare.sql

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%'
    LOOP
        EXECUTE format($f$
            CREATE TABLE IF NOT EXISTS %I.d390_reclasificare (
                id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                an       integer NOT NULL,
                luna     integer NOT NULL,
                directie text    NOT NULL,             -- 'emisa' / 'primita'
                tara     varchar(2)  NOT NULL,
                cod      varchar(20) NOT NULL,
                tip      char(1) NOT NULL,             -- tipul nou (L/T/P/R emisa; A/S primita)
                UNIQUE (an, luna, directie, tara, cod)
            )$f$, r.schema_name);
        EXECUTE format($f$
            CREATE TABLE IF NOT EXISTS %I.d390_manual (
                id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                an      integer NOT NULL,
                luna    integer NOT NULL,
                tip     char(1) NOT NULL,              -- P/S/T/R (linie pur manuala)
                tara    varchar(2)  NOT NULL,
                cod     varchar(20) NOT NULL DEFAULT '',
                den     text NOT NULL DEFAULT '',
                baza    numeric NOT NULL DEFAULT 0
            )$f$, r.schema_name);
        -- owner = rolul aplicatiei (ca restul tabelelor tenant); altfel app-ul n-are drept
        EXECUTE format('ALTER TABLE %I.d390_reclasificare OWNER TO iconta_user', r.schema_name);
        EXECUTE format('ALTER TABLE %I.d390_manual OWNER TO iconta_user', r.schema_name);
    END LOOP;
END $$;

SELECT nspname AS tenant,
       EXISTS(SELECT 1 FROM information_schema.tables t
              WHERE t.table_schema = nspname AND t.table_name = 'd390_reclasificare') AS are_reclas,
       EXISTS(SELECT 1 FROM information_schema.tables t
              WHERE t.table_schema = nspname AND t.table_name = 'd390_manual') AS are_manual
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
