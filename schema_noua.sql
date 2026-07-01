-- ============================================================
--  iConta — SCHEMA NOUĂ (reconstrucție din inventar de cod)
--  Iunie 2026. Construită de la zero, doar coloane vii.
--
--  Convenții:
--   - id GENERATED ALWAYS AS IDENTITY (nu serial/nextval)
--   - timestamps în română: creat_la / actualizat_la etc. (timestamptz)
--   - doar coloane folosite efectiv în codul iconta_nou
--
--  Structură:
--   PARTEA 1 — schema public (identitate + global)
--   PARTEA 2 — funcție de creare șablon tenant (tabelele contabile per firmă)
-- ============================================================

-- ============================================================
--  PARTEA 1 — PUBLIC
-- ============================================================

-- ---- Cabinetul de contabilitate (rădăcina) ----
CREATE TABLE public.accounting_firms (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nume      varchar(255) NOT NULL,
    cui       varchar(20) UNIQUE,
    activ     boolean NOT NULL DEFAULT true,
    creat_la  timestamptz NOT NULL DEFAULT now()
);

-- ---- Utilizatori (identitate + RBAC + permisiuni flux) ----
CREATE TABLE public.users (
    id                 integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email              varchar(255) NOT NULL UNIQUE,
    password_hash      varchar(255) NOT NULL,
    nume               varchar(255),
    prenume            text,
    functie            text,
    rol                varchar(20) NOT NULL DEFAULT 'angajat'
                       CHECK (rol IN ('superadmin','admin_firma','angajat','client')),
    accounting_firm_id integer REFERENCES public.accounting_firms(id),
    activ              boolean NOT NULL DEFAULT true,
    parola_schimbata   boolean NOT NULL DEFAULT false,
    poate_pregati      boolean NOT NULL DEFAULT false,
    poate_valida       boolean NOT NULL DEFAULT false,
    poate_depune       boolean NOT NULL DEFAULT false,
    creat_la           timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT chk_firm_required
        CHECK (rol = 'superadmin' OR accounting_firm_id IS NOT NULL)
);

-- ---- Firme-client (tenant) — fiecare cu schema ei contabilă ----
CREATE TABLE public.tenants (
    id                     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schema_name            varchar(63) NOT NULL UNIQUE,
    nume                   varchar(255) NOT NULL,
    cui                    varchar(20),
    accounting_firm_id     integer REFERENCES public.accounting_firms(id),
    activ                  boolean NOT NULL DEFAULT true,
    plan_importat_la       timestamptz,
    balanta_importata_la   timestamptz,
    salariati_importati_la timestamptz,
    creat_la               timestamptz NOT NULL DEFAULT now()
);

-- ---- Legătură user <-> tenant (vizibilitate pentru angajat/client) ----
CREATE TABLE public.user_tenants (
    user_id   integer NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    tenant_id integer NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    creat_la  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, tenant_id)
);

-- ---- Coada de validare declarații (flux asistent -> senior -> depus) ----
CREATE TABLE public.declaratii_coada (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cabinet_id       integer NOT NULL,
    tenant_id        integer NOT NULL,
    tip              text NOT NULL,
    perioada         text NOT NULL,
    stare            text NOT NULL DEFAULT 'la_senior',
    coerenta         text,
    payload          jsonb,
    hash             text,
    creat_de         text,
    creat_la         timestamptz NOT NULL DEFAULT now(),
    aprobat_de       text,
    aprobat_la       timestamptz,
    respins_de       text,
    respins_la       timestamptz,
    motiv_respingere text,
    depus_de         text,
    depus_la         timestamptz,
    spv_index        text
);
CREATE INDEX ix_coada_firma ON public.declaratii_coada (tenant_id, tip, perioada);
CREATE INDEX ix_coada_stare ON public.declaratii_coada (cabinet_id, stare);
CREATE UNIQUE INDEX ux_coada_activa ON public.declaratii_coada (tenant_id, tip, perioada)
    WHERE stare NOT IN ('respinsa', 'depusa');

-- ---- Registrul declarațiilor depuse (istoric + migrare) ----
CREATE TABLE public.declaratii_depuse (
    tenant_id     integer NOT NULL,
    an            integer NOT NULL,
    luna          integer NOT NULL,
    tip           text NOT NULL,
    data_depunere timestamptz NOT NULL DEFAULT now(),
    sursa         text NOT NULL DEFAULT 'iconta',
    PRIMARY KEY (tenant_id, an, luna, tip)
);

-- ---- Status migrare (7 straturi per cabinet) ----
CREATE TABLE public.migrare_status (
    id                 integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    accounting_firm_id integer NOT NULL REFERENCES public.accounting_firms(id),
    strat              text NOT NULL,
    stare              text NOT NULL DEFAULT 'in_lucru',
    nota               text NOT NULL DEFAULT '',
    actualizat_la      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (accounting_firm_id, strat)
);

-- ---- Invitații de activare cont (Adaugă actor) ----
CREATE TABLE public.invitatii_cont (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cabinet_id  integer NOT NULL REFERENCES public.accounting_firms(id) ON DELETE CASCADE,
    user_id     integer NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    email       text NOT NULL,
    token       text NOT NULL UNIQUE,
    expira_la   timestamptz NOT NULL,
    folosit     boolean NOT NULL DEFAULT false,
    folosit_la  timestamptz,
    creat_de    text,
    creat_la    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_invcont_cabinet ON public.invitatii_cont (cabinet_id);


-- ============================================================
--  PARTEA 2 — ȘABLON TENANT
--  Funcție care creează toate tabelele contabile într-o schemă nouă.
--  Apelată la provisioning-ul fiecărei firme: SELECT public.creeaza_schema_tenant('tenant_003');
-- ============================================================

CREATE OR REPLACE FUNCTION public.creeaza_schema_tenant(p_schema text)
RETURNS void AS $func$
BEGIN
    -- validare nume schemă (litere mici, cifre, underscore)
    IF p_schema !~ '^[a-z_][a-z0-9_]*$' THEN
        RAISE EXCEPTION 'nume schemă invalid: %', p_schema;
    END IF;

    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', p_schema);
    EXECUTE format('SET LOCAL search_path TO %I', p_schema);

    -- ---- Profil firmă (vector fiscal — esențial pt Control fiscal) ----
    EXECUTE format($t$
        CREATE TABLE %I.firma_profil (
            id                integer PRIMARY KEY DEFAULT 1,
            nume              varchar(255) NOT NULL,
            cui               varchar(20) NOT NULL,
            reg_com           varchar(50),
            adresa            text,
            oras              varchar(100),
            judet             varchar(10),
            cod_postal        varchar(20),
            iban              varchar(34),
            banca             text,
            email             text,
            telefon           text,
            caen              text,
            declarant_nume    text,
            declarant_prenume text,
            declarant_functie text,
            patron_nume       text,
            patron_email      text,
            logo              text,
            tip_decont        text,
            pro_rata          numeric,
            regim_fiscal      text,
            platitor_tva      boolean,
            operatiuni_ic     boolean,
            CONSTRAINT firma_profil_singleton CHECK (id = 1)
        )$t$, p_schema);

    -- ---- Plan de conturi ----
    EXECUTE format($t$
        CREATE TABLE %I.plan_conturi (
            simbol        varchar(10) PRIMARY KEY,
            denumire      text NOT NULL,
            tip           varchar(20) DEFAULT 'Bifunctional',
            sold_debitor  numeric(15,2) DEFAULT 0,
            sold_creditor numeric(15,2) DEFAULT 0
        )$t$, p_schema);

    -- ---- Clienți ----
    EXECUTE format($t$
        CREATE TABLE %I.clienti (
            id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nume       varchar(255) NOT NULL,
            cui        varchar(20),
            adresa     text,
            email      varchar(255),
            telefon    varchar(50),
            oras       varchar(100),
            judet      varchar(10),
            cod_postal varchar(20),
            status     varchar(20) NOT NULL DEFAULT 'activ',
            creat_la   timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema);

    -- ---- Furnizori (simetric cu clienți) ----
    EXECUTE format($t$
        CREATE TABLE %I.furnizori (
            id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nume       varchar(255) NOT NULL,
            cui        varchar(20),
            adresa     text,
            email      varchar(255),
            telefon    varchar(50),
            oras       varchar(100),
            judet      varchar(10),
            cod_postal varchar(20),
            status     varchar(20) NOT NULL DEFAULT 'activ',
            creat_la   timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema);

    -- ---- Facturi ----
    EXECUTE format($t$
        CREATE TABLE %I.facturi (
            id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            client_id     integer REFERENCES %I.clienti(id),
            numar         varchar(50) NOT NULL,
            data_emitere  date NOT NULL,
            data_scadenta date,
            total         numeric(12,2) NOT NULL DEFAULT 0,
            tva           numeric(12,2) NOT NULL DEFAULT 0,
            moneda        varchar(3) NOT NULL DEFAULT 'RON',
            directie      varchar(10) NOT NULL DEFAULT 'emisa',
            status        varchar(20) DEFAULT 'emisa',
            xml           text,
            tert_nume     varchar(255),
            tert_cui      varchar(30),
            creat_la      timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema, p_schema);

    -- ---- Linii factură ----
    EXECUTE format($t$
        CREATE TABLE %I.factura_linii (
            id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            factura_id  integer NOT NULL REFERENCES %I.facturi(id) ON DELETE CASCADE,
            descriere   text NOT NULL,
            um          varchar(10) NOT NULL DEFAULT 'buc',
            cantitate   numeric(12,3) NOT NULL DEFAULT 1,
            pret_unitar numeric(12,2) NOT NULL DEFAULT 0,
            cota_tva    numeric(5,2) NOT NULL DEFAULT 21
        )$t$, p_schema, p_schema);

    -- ---- Note contabile (înregistrări) ----
    EXECUTE format($t$
        CREATE TABLE %I.inregistrari (
            id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            data         date NOT NULL,
            numar        varchar(50),
            factura_id   integer REFERENCES %I.facturi(id),
            document_ref varchar(255),
            descriere    text,
            sursa        text,
            status       varchar(20) NOT NULL DEFAULT 'ciorna',
            creat_la     timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema, p_schema);

    -- ---- Linii notă (debit/credit) ----
    EXECUTE format($t$
        CREATE TABLE %I.inregistrari_linii (
            id              integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            inregistrare_id integer NOT NULL REFERENCES %I.inregistrari(id) ON DELETE CASCADE,
            cont_debit      varchar(10) NOT NULL,
            cont_credit     varchar(10) NOT NULL,
            suma            numeric(14,2) NOT NULL
        )$t$, p_schema, p_schema);

    -- ---- Solduri inițiale (balanță de pornire) ----
    EXECUTE format($t$
        CREATE TABLE %I.solduri_initiale (
            id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            cont           text NOT NULL,
            denumire       text NOT NULL DEFAULT '',
            sold_debitor   numeric(15,2) NOT NULL DEFAULT 0,
            sold_creditor  numeric(15,2) NOT NULL DEFAULT 0,
            data_referinta date
        )$t$, p_schema);

    -- ---- Solduri parteneri (4111/401 detaliat) ----
    EXECUTE format($t$
        CREATE TABLE %I.solduri_parteneri (
            id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            cont           text NOT NULL,
            cui            text NOT NULL DEFAULT '',
            denumire       text NOT NULL DEFAULT '',
            sold_debitor   numeric(15,2) NOT NULL DEFAULT 0,
            sold_creditor  numeric(15,2) NOT NULL DEFAULT 0,
            data_referinta date
        )$t$, p_schema);

    -- ---- Salariați ----
    -- Verificat la sursă (D112, OUG/Cod fiscal). Schimbări vs schema veche:
    --  - scos tip_norma (redundant cu part_time)
    --  - part_time boolean: codul d112.py îl citea, lipsea în schema veche (bug latent)
    --  - nif: alternativă la CNP pentru asigurați străini (D112)
    --  - data_asigurat: data intrării în categoria de asigurat (D112, poate ≠ data_angajare)
    --  - tip_asigurat: cod tip asigurat D112 (25 construcții, 54 IT...; pregătit pt codurile
    --    noi 1.11.2/1.11.3 din D112-iulie 2026). Logica de populare = funcție de perioadă.
    EXECUTE format($t$
        CREATE TABLE %I.salariati (
            id                   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            cnp                  text,
            nif                  text,
            nume                 text,
            prenume              text,
            data_angajare        date,
            data_asigurat        date,
            part_time            boolean DEFAULT false,
            ore_zi               numeric DEFAULT 8,
            salariu_brut         numeric DEFAULT 0,
            persoane_intretinere integer DEFAULT 0,
            judet_casa           text,
            cor                  text,
            tip_asigurat         text,
            scutit_contrib_minim boolean DEFAULT false,
            motiv_exceptare      smallint,
            activ                boolean DEFAULT true,
            creat_la             timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema);

    -- ---- Asociați (pt D205, dividende) ----
    EXECUTE format($t$
        CREATE TABLE %I.asociati (
            id       integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nume     text,
            cnp      text,
            cota     numeric DEFAULT 0,
            creat_la timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema);

    -- ---- Concedii medicale (CM — calcul complet) ----
    EXECUTE format($t$
        CREATE TABLE %I.concedii_medicale (
            id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            salariat_id    integer REFERENCES %I.salariati(id) ON DELETE CASCADE,
            an             integer,
            luna           integer,
            cod            text,
            zile           integer DEFAULT 0,
            indemnizatie   numeric DEFAULT 0,
            baza           numeric DEFAULT 0,
            media_zilnica  numeric DEFAULT 0,
            procent        numeric DEFAULT 0,
            diminuare      boolean DEFAULT true,
            zile_platite   integer DEFAULT 0,
            zile_ang       integer DEFAULT 0,
            zile_fnuass    integer DEFAULT 0,
            brut_ang       numeric DEFAULT 0,
            brut_fnuass    numeric DEFAULT 0,
            cass           numeric DEFAULT 0,
            impozit        numeric DEFAULT 0,
            cas            numeric DEFAULT 0,
            net            numeric DEFAULT 0,
            serie          text,
            numar          text,
            data_acordare  date,
            data_inceput   date,
            data_sfarsit   date,
            loc_prescriere integer DEFAULT 1,
            diagnostic     text,
            creat_la       timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema, p_schema);

    -- ---- Mijloace fixe (amortizare) ----
    EXECUTE format($t$
        CREATE TABLE %I.mijloace_fixe (
            id               integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            cod              text,
            denumire         text NOT NULL,
            cont_imobilizare text DEFAULT '2131',
            cont_amortizare  text DEFAULT '2813',
            valoare          numeric NOT NULL DEFAULT 0,
            rezidual         numeric DEFAULT 0,
            dnf_luni         integer NOT NULL DEFAULT 12,
            data_pif         date,
            metoda           text DEFAULT 'liniara',
            activ            boolean DEFAULT true,
            creat_la         timestamptz NOT NULL DEFAULT now()
        )$t$, p_schema);

END;
$func$ LANGUAGE plpgsql;

-- ============================================================
--  Verificare
-- ============================================================
SELECT 'schema public creată' AS status;
