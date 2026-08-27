-- ============================================================================
-- infra/bootstrap_public.sql — schema PUBLIC nereproductibila din migrare_*
-- ============================================================================
-- CUM se ruleaza (ca SUPERUSER, o singura data):
--     sudo -u postgres psql -d iconta_v2 -f infra/bootstrap_public.sql
-- CAND: O DATA, la provisionarea unui SERVER NOU, INAINTE de a porni app-ul si
--     INAINTE de a rula migrare_*. Pe prod EXISTENT e deja aplicat (no-op, idempotent).
-- PRERECHIZIT: rolul `iconta_user` si baza `iconta_v2` EXISTA deja (create de pasul de
--     provisioning care ruleaza inaintea acestui script); bootstrap-ul foloseste SET SESSION
--     AUTHORIZATION iconta_user ca obiectele sa fie owned de el, deci rolul trebuie sa existe.
-- ORDINE la server nou: createdb + createrole -> ACEST bootstrap -> deploy app -> migrare_*.
-- DOVEDIT idempotent pe baza temporara locala (rulat de 2 ori, zero erori; NU pe prod).
--
-- CE contine (si DE CE doar atat): GRANT-ul de care depinde tot restul + DDL-ul
-- tabelelor publice care NU au CREATE nicaieri in git (nu vin din migrare_* / *.sql).
-- Tabelele care AU un CREATE in git sunt EXCLUSE intentionat (o singura sursa de
-- adevar): alerte_control_emise (migrare_alerte_control_emise), migrare_status
-- (migrare_api), cor_ocupatii (08_ddl_cor_ocupatii.sql), spv_token + spv_cui_acoperit
-- (spv_conector_ddl_v1.sql). declaratii_depuse intra AICI la starea GENESIS (coloane
-- de baza); coloanele sursa/xml/randuri/nr_depunere + PK-ul nou + vederea le adauga
-- migrare_declaratii_depuse_randuri / _versiune (nu se dubleaza).
--
-- REGULA PERMANENTA: orice obiect public NOU de-acum intra printr-un core/migrare_*.py
-- (ruleaza ca iconta_user datorita GRANT-ului de mai jos), NU aici. Bootstrap-ul e doar
-- genesis-ul care nu se putea reproduce altfel. Vezi DECIZII 22.07 [INFRA] + DE_FACUT.
--
-- Idempotent (IF NOT EXISTS + guard pe constrangeri): rulabil de doua ori fara efect.
-- Ownership: obiectele se creeaza ca iconta_user (SET SESSION AUTHORIZATION) ca sa nu
-- fie nevoie de ALTER OWNER ulterior. Fara date, fara secrete (doar schema).
-- ============================================================================

-- 1) GRANT-ul de care depinde tot restul (ca postgres). PG15+ revoca CREATE de la PUBLIC.
GRANT CREATE ON SCHEMA public TO iconta_user;

-- 2) restul se creeaza CA iconta_user -> owned de iconta_user (uniform, migrarile viitoare merg)
SET SESSION AUTHORIZATION iconta_user;

-- 3) declaratii_depuse — GENESIS (migrarile adauga sursa/xml/randuri/nr_depunere + PK + vedere)
CREATE TABLE IF NOT EXISTS public.declaratii_depuse (
    tenant_id     integer                  NOT NULL,
    an            integer                  NOT NULL,
    luna          integer                  NOT NULL,
    tip           text                     NOT NULL,
    data_depunere timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT declaratii_depuse_pkey PRIMARY KEY (tenant_id, an, luna, tip)
);

-- 4) restul tabelelor publice fara CREATE in git (din pg_dump, filtrat + idempotent)

\restrict ymCNwZrYKP9Vqly9eGlHCWL3hEfIjDxsfZjicplacq42tStt2lebxG7IQsboTA4

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;

CREATE TABLE IF NOT EXISTS public.accounting_firms (
    id integer NOT NULL,
    nume character varying(255) NOT NULL,
    cui character varying(20),
    activ boolean DEFAULT true NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    educatie_4ochi_la_nr integer DEFAULT 0 NOT NULL,
    patru_ochi_activ boolean DEFAULT false NOT NULL
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='accounting_firms' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.accounting_firms ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.accounting_firms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.alerte_emise (
    alerta_id integer NOT NULL,
    prag integer NOT NULL,
    emis_la timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.alerte_fiscale (
    id integer NOT NULL,
    sursa text NOT NULL,
    titlu text NOT NULL,
    rezumat text,
    url text,
    relevanta character varying(10),
    vazut boolean DEFAULT false NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    data_vigoare date
);

CREATE SEQUENCE IF NOT EXISTS public.alerte_fiscale_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.alerte_fiscale_id_seq OWNED BY public.alerte_fiscale.id;

CREATE TABLE IF NOT EXISTS public.anunturi_cabinet (
    id integer NOT NULL,
    cabinet_id integer,
    mesaj text NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    confirmat_la timestamp with time zone,
    data_afisare date,
    tenant_id integer
);

CREATE SEQUENCE IF NOT EXISTS public.anunturi_cabinet_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.anunturi_cabinet_id_seq OWNED BY public.anunturi_cabinet.id;

CREATE TABLE IF NOT EXISTS public.api_chei (
    id integer NOT NULL,
    accounting_firm_id integer NOT NULL,
    cheie_hash character varying(64) NOT NULL,
    prefix character varying(12) NOT NULL,
    nume character varying(100),
    activ boolean DEFAULT true NOT NULL,
    ultima_folosire timestamp with time zone,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.api_chei_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.api_chei_id_seq OWNED BY public.api_chei.id;

CREATE TABLE IF NOT EXISTS public.audit_log (
    id integer NOT NULL,
    user_id integer,
    tenant_id integer,
    actiune character varying(80) NOT NULL,
    entitate character varying(40),
    entitate_id integer,
    detalii jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;

CREATE TABLE IF NOT EXISTS public.curs_bnr_zilnic (
    data date NOT NULL,
    moneda character varying(3) NOT NULL,
    curs numeric(12,4) NOT NULL,
    luat_la timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.declaratii_coada (
    id bigint NOT NULL,
    cabinet_id integer NOT NULL,
    tenant_id integer NOT NULL,
    tip text NOT NULL,
    perioada text NOT NULL,
    stare text DEFAULT 'la_senior'::text NOT NULL,
    coerenta text,
    payload jsonb,
    hash text,
    creat_de text,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    aprobat_de text,
    aprobat_la timestamp with time zone,
    respins_de text,
    respins_la timestamp with time zone,
    motiv_respingere text,
    depus_de text,
    depus_la timestamp with time zone,
    spv_index text,
    creat_de_id integer,
    aprobat_de_id integer,
    respins_de_id integer,
    depus_de_id integer,
    inceput_la timestamp with time zone
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='declaratii_coada' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.declaratii_coada ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.declaratii_coada_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.invitatii_cont (
    id bigint NOT NULL,
    cabinet_id integer NOT NULL,
    user_id integer NOT NULL,
    email text NOT NULL,
    token text NOT NULL,
    expira_la timestamp with time zone NOT NULL,
    folosit boolean DEFAULT false NOT NULL,
    folosit_la timestamp with time zone,
    creat_de text,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='invitatii_cont' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.invitatii_cont ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.invitatii_cont_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.metrici_sanatate (
    id integer NOT NULL,
    ram_procent numeric,
    disc_procent numeric,
    load1 numeric,
    conexiuni_db integer,
    erori_noi integer,
    creat_la timestamp without time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.metrici_sanatate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.metrici_sanatate_id_seq OWNED BY public.metrici_sanatate.id;

CREATE TABLE IF NOT EXISTS public.notificari (
    id integer NOT NULL,
    user_id integer NOT NULL,
    tip character varying(40) NOT NULL,
    text text NOT NULL,
    link character varying(80),
    citit boolean DEFAULT false NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='notificari' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.notificari ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.notificari_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.pachet_povestea (
    tenant_id integer NOT NULL,
    an integer NOT NULL,
    luna integer NOT NULL,
    text text NOT NULL,
    status text DEFAULT 'ciorna'::text NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.raportari (
    id bigint NOT NULL,
    autor_id integer NOT NULL,
    cabinet_id integer,
    subiect text,
    stare text DEFAULT 'noua'::text NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    ultim_mesaj_la timestamp with time zone DEFAULT now() NOT NULL,
    pentru_admin boolean DEFAULT false NOT NULL
);

CREATE TABLE IF NOT EXISTS public.raportari_atasamente (
    id bigint NOT NULL,
    mesaj_id bigint NOT NULL,
    cale text NOT NULL,
    nume_orig text,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='raportari_atasamente' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.raportari_atasamente ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.raportari_atasamente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='raportari' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.raportari ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.raportari_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.raportari_mesaje (
    id bigint NOT NULL,
    raportare_id bigint NOT NULL,
    autor_id integer,
    rol_autor text NOT NULL,
    text text NOT NULL,
    citit boolean DEFAULT false NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='raportari_mesaje' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.raportari_mesaje ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.raportari_mesaje_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.reges_chei (
    tenant_id integer NOT NULL,
    username text NOT NULL,
    parola text NOT NULL,
    mediu text DEFAULT 'test'::text NOT NULL,
    author_id uuid DEFAULT gen_random_uuid() NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.reges_mesaje (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    salariat_id integer,
    operatie text NOT NULL,
    message_id uuid NOT NULL,
    response_id text,
    referinta_salariat uuid,
    referinta_contract uuid,
    status text DEFAULT 'trimis'::text NOT NULL,
    raspuns text,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='reges_mesaje' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.reges_mesaje ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.reges_mesaje_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.solicitari_client (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    mesaj text NOT NULL,
    autor_rol character varying(20) NOT NULL,
    autor_id integer NOT NULL,
    creat_la timestamp without time zone DEFAULT now() NOT NULL,
    citit boolean DEFAULT false NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.solicitari_client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.solicitari_client_id_seq OWNED BY public.solicitari_client.id;

CREATE TABLE IF NOT EXISTS public.tenants (
    id integer NOT NULL,
    schema_name character varying(63) NOT NULL,
    nume character varying(255) NOT NULL,
    cui character varying(20),
    accounting_firm_id integer,
    activ boolean DEFAULT true NOT NULL,
    plan_importat_la timestamp with time zone,
    balanta_importata_la timestamp with time zone,
    salariati_importati_la timestamp with time zone,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='tenants' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.tenants ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tenants_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.tokene_activare (
    token text NOT NULL,
    user_id integer NOT NULL,
    expira timestamp with time zone NOT NULL,
    folosit boolean DEFAULT false NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.user_tenants (
    user_id integer NOT NULL,
    tenant_id integer NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    nume character varying(255),
    prenume text,
    functie text,
    rol character varying(20) DEFAULT 'angajat'::character varying NOT NULL,
    accounting_firm_id integer,
    activ boolean DEFAULT true NOT NULL,
    parola_schimbata boolean DEFAULT false NOT NULL,
    poate_pregati boolean DEFAULT false NOT NULL,
    poate_valida boolean DEFAULT false NOT NULL,
    poate_depune boolean DEFAULT false NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    nivel text DEFAULT 'asistent'::text NOT NULL,
    CONSTRAINT chk_firm_required CHECK ((((rol)::text = 'superadmin'::text) OR ((rol)::text = 'client'::text) OR (accounting_firm_id IS NOT NULL))),
    CONSTRAINT users_rol_check CHECK (((rol)::text = ANY ((ARRAY['superadmin'::character varying, 'admin_firma'::character varying, 'angajat'::character varying, 'client'::character varying])::text[])))
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='users' AND column_name='id' AND is_identity='YES') THEN
    ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
  END IF;
END $$;

ALTER TABLE ONLY public.alerte_fiscale ALTER COLUMN id SET DEFAULT nextval('public.alerte_fiscale_id_seq'::regclass);

ALTER TABLE ONLY public.anunturi_cabinet ALTER COLUMN id SET DEFAULT nextval('public.anunturi_cabinet_id_seq'::regclass);

ALTER TABLE ONLY public.api_chei ALTER COLUMN id SET DEFAULT nextval('public.api_chei_id_seq'::regclass);

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);

ALTER TABLE ONLY public.metrici_sanatate ALTER COLUMN id SET DEFAULT nextval('public.metrici_sanatate_id_seq'::regclass);

ALTER TABLE ONLY public.solicitari_client ALTER COLUMN id SET DEFAULT nextval('public.solicitari_client_id_seq'::regclass);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='accounting_firms_cui_key' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.accounting_firms ADD CONSTRAINT accounting_firms_cui_key UNIQUE (cui);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='accounting_firms_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.accounting_firms ADD CONSTRAINT accounting_firms_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='alerte_emise_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.alerte_emise ADD CONSTRAINT alerte_emise_pkey PRIMARY KEY (alerta_id, prag);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='alerte_fiscale_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.alerte_fiscale ADD CONSTRAINT alerte_fiscale_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='alerte_fiscale_sursa_titlu_key' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.alerte_fiscale ADD CONSTRAINT alerte_fiscale_sursa_titlu_key UNIQUE (sursa, titlu);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='anunturi_cabinet_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.anunturi_cabinet ADD CONSTRAINT anunturi_cabinet_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='api_chei_cheie_hash_key' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.api_chei ADD CONSTRAINT api_chei_cheie_hash_key UNIQUE (cheie_hash);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='api_chei_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.api_chei ADD CONSTRAINT api_chei_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='audit_log_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.audit_log ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='curs_bnr_zilnic_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.curs_bnr_zilnic ADD CONSTRAINT curs_bnr_zilnic_pkey PRIMARY KEY (data, moneda);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_coada_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.declaratii_coada ADD CONSTRAINT declaratii_coada_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='invitatii_cont_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.invitatii_cont ADD CONSTRAINT invitatii_cont_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='invitatii_cont_token_key' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.invitatii_cont ADD CONSTRAINT invitatii_cont_token_key UNIQUE (token);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='metrici_sanatate_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.metrici_sanatate ADD CONSTRAINT metrici_sanatate_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='notificari_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.notificari ADD CONSTRAINT notificari_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='pachet_povestea_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.pachet_povestea ADD CONSTRAINT pachet_povestea_pkey PRIMARY KEY (tenant_id, an, luna);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_atasamente_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari_atasamente ADD CONSTRAINT raportari_atasamente_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_mesaje_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari_mesaje ADD CONSTRAINT raportari_mesaje_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari ADD CONSTRAINT raportari_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='reges_chei_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.reges_chei ADD CONSTRAINT reges_chei_pkey PRIMARY KEY (tenant_id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='reges_mesaje_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.reges_mesaje ADD CONSTRAINT reges_mesaje_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='solicitari_client_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.solicitari_client ADD CONSTRAINT solicitari_client_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='tenants_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.tenants ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='tenants_schema_name_key' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.tenants ADD CONSTRAINT tenants_schema_name_key UNIQUE (schema_name);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='tokene_activare_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.tokene_activare ADD CONSTRAINT tokene_activare_pkey PRIMARY KEY (token);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='user_tenants_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.user_tenants ADD CONSTRAINT user_tenants_pkey PRIMARY KEY (user_id, tenant_id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='users_email_key' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.users ADD CONSTRAINT users_email_key UNIQUE (email);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='users_pkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_audit_log_tenant ON public.audit_log USING btree (tenant_id, created_at);

CREATE INDEX IF NOT EXISTS idx_audit_log_user ON public.audit_log USING btree (user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_metrici_sanatate_timp ON public.metrici_sanatate USING btree (creat_la);

CREATE INDEX IF NOT EXISTS idx_solicitari_client_tenant ON public.solicitari_client USING btree (tenant_id);

CREATE INDEX IF NOT EXISTS ix_coada_creat_de_id ON public.declaratii_coada USING btree (creat_de_id);

CREATE INDEX IF NOT EXISTS ix_coada_firma ON public.declaratii_coada USING btree (tenant_id, tip, perioada);

CREATE INDEX IF NOT EXISTS ix_coada_stare ON public.declaratii_coada USING btree (cabinet_id, stare);

CREATE INDEX IF NOT EXISTS ix_invcont_cabinet ON public.invitatii_cont USING btree (cabinet_id);

CREATE INDEX IF NOT EXISTS ix_notif_user ON public.notificari USING btree (user_id, citit);

CREATE INDEX IF NOT EXISTS ix_rap_mesaje_rap ON public.raportari_mesaje USING btree (raportare_id);

CREATE INDEX IF NOT EXISTS ix_raportari_autor ON public.raportari USING btree (autor_id);

CREATE UNIQUE INDEX IF NOT EXISTS ux_coada_activa ON public.declaratii_coada USING btree (tenant_id, tip, perioada) WHERE (stare <> ALL (ARRAY['respinsa'::text, 'depusa'::text]));

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='anunturi_cabinet_cabinet_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.anunturi_cabinet ADD CONSTRAINT anunturi_cabinet_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.accounting_firms(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='anunturi_cabinet_tenant_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.anunturi_cabinet ADD CONSTRAINT anunturi_cabinet_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='api_chei_accounting_firm_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.api_chei ADD CONSTRAINT api_chei_accounting_firm_id_fkey FOREIGN KEY (accounting_firm_id) REFERENCES public.accounting_firms(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_coada_aprobat_de_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.declaratii_coada ADD CONSTRAINT declaratii_coada_aprobat_de_id_fkey FOREIGN KEY (aprobat_de_id) REFERENCES public.users(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_coada_creat_de_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.declaratii_coada ADD CONSTRAINT declaratii_coada_creat_de_id_fkey FOREIGN KEY (creat_de_id) REFERENCES public.users(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_coada_depus_de_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.declaratii_coada ADD CONSTRAINT declaratii_coada_depus_de_id_fkey FOREIGN KEY (depus_de_id) REFERENCES public.users(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_coada_respins_de_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.declaratii_coada ADD CONSTRAINT declaratii_coada_respins_de_id_fkey FOREIGN KEY (respins_de_id) REFERENCES public.users(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='invitatii_cont_cabinet_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.invitatii_cont ADD CONSTRAINT invitatii_cont_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.accounting_firms(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='invitatii_cont_user_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.invitatii_cont ADD CONSTRAINT invitatii_cont_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_atasamente_mesaj_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari_atasamente ADD CONSTRAINT raportari_atasamente_mesaj_id_fkey FOREIGN KEY (mesaj_id) REFERENCES public.raportari_mesaje(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_autor_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari ADD CONSTRAINT raportari_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES public.users(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_cabinet_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari ADD CONSTRAINT raportari_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.accounting_firms(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_mesaje_autor_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari_mesaje ADD CONSTRAINT raportari_mesaje_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES public.users(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='raportari_mesaje_raportare_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.raportari_mesaje ADD CONSTRAINT raportari_mesaje_raportare_id_fkey FOREIGN KEY (raportare_id) REFERENCES public.raportari(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='solicitari_client_tenant_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.solicitari_client ADD CONSTRAINT solicitari_client_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='tenants_accounting_firm_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.tenants ADD CONSTRAINT tenants_accounting_firm_id_fkey FOREIGN KEY (accounting_firm_id) REFERENCES public.accounting_firms(id);
  END IF;
END $$;

-- [R62 (b), 26.08.2026] `tenants.principal_client_id` si cheia ei straina au fost SCOASE:
-- coloana avea drum de citire si zero drum de scriere. Vezi core/migrare_portal.py.

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='user_tenants_tenant_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.user_tenants ADD CONSTRAINT user_tenants_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='user_tenants_user_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.user_tenants ADD CONSTRAINT user_tenants_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='users_accounting_firm_id_fkey' AND connamespace='public'::regnamespace) THEN
    ALTER TABLE public.users ADD CONSTRAINT users_accounting_firm_id_fkey FOREIGN KEY (accounting_firm_id) REFERENCES public.accounting_firms(id);
  END IF;
END $$;

RESET SESSION AUTHORIZATION;

-- [R62, 26.08.2026] Oglinda DDL-ului din core/migrare_portal.py (sursa UNICA e acolo).
-- Confirmarea schimbarii de adresa + urma pe care o vede cabinetul.
CREATE TABLE IF NOT EXISTS public.schimbari_email (
    id             serial PRIMARY KEY,
    user_id        integer NOT NULL,
    tenant_id      integer NOT NULL,
    email_vechi    text NOT NULL,
    email_nou      text NOT NULL,
    token_hash     text NOT NULL,
    expira         timestamp with time zone NOT NULL,
    cerut_la       timestamp with time zone DEFAULT now() NOT NULL,
    confirmat_la   timestamp with time zone,
    CONSTRAINT schimbari_email_alta_adresa
        CHECK (lower(btrim(email_nou)) <> lower(btrim(email_vechi)))
);

CREATE INDEX IF NOT EXISTS schimbari_email_token_idx
    ON public.schimbari_email (token_hash);

CREATE TABLE IF NOT EXISTS public.urme_portal (
    id          serial PRIMARY KEY,
    tenant_id   integer NOT NULL,
    actiune     text NOT NULL,
    detaliu     text NOT NULL,
    autor_id    integer,
    creat_la    timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT urme_portal_actiune_cunoscuta
        CHECK (actiune IN ('email_cerut', 'email_confirmat', 'acces_dat', 'acces_retras')),
    CONSTRAINT urme_portal_detaliu_nevid
        CHECK (btrim(detaliu) <> '')
);

CREATE INDEX IF NOT EXISTS urme_portal_tenant_idx
    ON public.urme_portal (tenant_id, creat_la DESC);


-- [R72, 27.08.2026] Oglinda DDL-ului din core/migrare_firme_scoase.py (sursa UNICA e acolo).
-- Urma unei firme scoase din portofoliu. NU are chei straine: tinta (tenant, user) nu mai
-- exista in momentul in care randul devine util. Poarta `tenant_id`, dar NU se sterge odata cu
-- firma - e declarata in tenant_stergere.NU_SE_STERG, iar garda verifica declaratia.
CREATE TABLE IF NOT EXISTS public.firme_scoase (
    id              bigserial PRIMARY KEY,
    tenant_id       integer     NOT NULL,
    nume            text        NOT NULL,
    cui             text,
    schema_name     text        NOT NULL,
    cabinet_id      integer,
    motiv           text        NOT NULL,
    randuri_sterse  jsonb,
    scos_de_user_id integer,
    scos_la         timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT firme_scoase_motiv_ck
        CHECK (motiv IN ('scoatere_firma', 'gdpr_cabinet')),
    CONSTRAINT firme_scoase_nume_nevid_ck
        CHECK (btrim(nume) <> '')
);

CREATE INDEX IF NOT EXISTS idx_firme_scoase_cabinet ON public.firme_scoase (cabinet_id, scos_la DESC);
CREATE INDEX IF NOT EXISTS idx_firme_scoase_tenant  ON public.firme_scoase (tenant_id);

-- [nume_anaf_v1, 27.08.2026] Denumirea asa cum a intors-o ANAF, langa cea editabila, cu data
-- masuratorii. Aceeasi forma ca firma_profil.platitor_tva_anaf + _data: valoarea omului langa
-- instantaneul autoritatii, nu in locul lui. `nume` ramane editabil - varianta (a), needitabil,
-- ar fi blocat firmele pe care ANAF nu le intoarce (nou-infiintate, sau ANAF jos).
ALTER TABLE public.tenants ADD COLUMN IF NOT EXISTS nume_anaf text;
ALTER TABLE public.tenants ADD COLUMN IF NOT EXISTS nume_anaf_la timestamptz;

-- Urmele portalului, copiate la scoatere. NUMAI pe motiv='scoatere_firma' - la GDPR nu se
-- copiaza nimic, fiindca acolo scopul actului e chiar disparitia datelor.
ALTER TABLE public.firme_scoase ADD COLUMN IF NOT EXISTS urme_pastrate jsonb;
