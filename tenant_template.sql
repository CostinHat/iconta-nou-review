--
-- PostgreSQL database dump
--


-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: TENANT_PLACEHOLDER; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA TENANT_PLACEHOLDER;


ALTER SCHEMA TENANT_PLACEHOLDER OWNER TO iconta_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_corectii; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.ai_corectii (
    id integer NOT NULL,
    context character varying(255) NOT NULL,
    cont_propus character varying(10),
    cont_final character varying(10) NOT NULL,
    corectat boolean NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.ai_corectii OWNER TO iconta_user;

--
-- Name: ai_corectii_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE SEQUENCE TENANT_PLACEHOLDER.ai_corectii_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE TENANT_PLACEHOLDER.ai_corectii_id_seq OWNER TO iconta_user;

--
-- Name: ai_corectii_id_seq; Type: SEQUENCE OWNED BY; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER SEQUENCE TENANT_PLACEHOLDER.ai_corectii_id_seq OWNED BY TENANT_PLACEHOLDER.ai_corectii.id;


--
-- Name: articole; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.articole (
    id integer NOT NULL,
    denumire character varying(255) NOT NULL,
    um character varying(20) DEFAULT 'buc'::character varying NOT NULL,
    cont_stoc character varying(10) DEFAULT '371'::character varying NOT NULL,
    cont_cheltuiala character varying(10) DEFAULT '607'::character varying NOT NULL,
    barcode character varying(50),
    nivel_minim numeric(12,3),
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.articole OWNER TO iconta_user;

--
-- Name: articole_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.articole ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.articole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: asociati; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.asociati (
    id integer NOT NULL,
    nume text,
    cnp text,
    cota numeric DEFAULT 0,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.asociati OWNER TO iconta_user;

--
-- Name: asociati_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.asociati ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.asociati_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: bonuri; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

CREATE TABLE TENANT_PLACEHOLDER.bonuri (
    id integer NOT NULL,
    comerciant text,
    cui text,
    data date,
    total numeric(12,2),
    tva_11 numeric(12,2) DEFAULT 0,
    tva_21 numeric(12,2) DEFAULT 0,
    cont_cheltuiala character varying(10),
    status character varying(20) DEFAULT 'de_verificat'::character varying NOT NULL,
    inregistrare_id integer,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    articole jsonb DEFAULT '[]'::jsonb,
    tva jsonb DEFAULT '[]'::jsonb,
    nr_imagini integer DEFAULT 0 NOT NULL,
    bon_complet boolean DEFAULT true NOT NULL,
    tip character varying(12) DEFAULT 'bon'::character varying NOT NULL,
    numar_document character varying(50),
    mentiuni text,
    factura_id integer,
    casa_operatiune_id integer
);


ALTER TABLE TENANT_PLACEHOLDER.bonuri OWNER TO iconta_user;

--
-- Name: bonuri_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

ALTER TABLE TENANT_PLACEHOLDER.bonuri ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.bonuri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1
);


--
-- Name: casa_operatiuni; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.casa_operatiuni (
    id integer NOT NULL,
    data date NOT NULL,
    tip character varying(10) NOT NULL,
    categorie character varying(30) NOT NULL,
    document character varying(50),
    partener character varying(255),
    cui character varying(30),
    suma numeric(12,2) NOT NULL,
    inregistrare_id integer,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    storno_de integer,  -- [Retest 2 pct.4] operațiunea stornată de aceasta (o operațiune cu notă validată nu se șterge, se stornează)
    avans boolean DEFAULT false NOT NULL   -- [lotul 6 pct.3b, 278] partea care depășește facturile alese: avans (core/migrare_casa_avans.py)
);


ALTER TABLE TENANT_PLACEHOLDER.casa_operatiuni OWNER TO iconta_user;

--
-- Name: casa_operatiuni_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.casa_operatiuni ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.casa_operatiuni_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: clienti; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.clienti (
    id integer NOT NULL,
    nume character varying(255) NOT NULL,
    cui character varying(20),
    adresa text,
    email character varying(255),
    telefon character varying(50),
    oras character varying(100),
    judet character varying(10),
    cod_postal character varying(20),
    status character varying(20) DEFAULT 'activ'::character varying NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.clienti OWNER TO iconta_user;

--
-- Name: clienti_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.clienti ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.clienti_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: concedii_medicale; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.concedii_medicale (
    id integer NOT NULL,
    salariat_id integer,
    an integer,
    luna integer,
    cod text,
    zile integer DEFAULT 0,
    indemnizatie numeric DEFAULT 0,
    baza numeric DEFAULT 0,
    media_zilnica numeric DEFAULT 0,
    procent numeric DEFAULT 0,
    diminuare boolean DEFAULT true,
    zile_platite integer DEFAULT 0,
    zile_ang integer DEFAULT 0,
    zile_fnuass integer DEFAULT 0,
    brut_ang numeric DEFAULT 0,
    brut_fnuass numeric DEFAULT 0,
    cass numeric DEFAULT 0,
    impozit numeric DEFAULT 0,
    cas numeric DEFAULT 0,
    net numeric DEFAULT 0,
    serie text,
    numar text,
    data_acordare date,
    data_inceput date,
    data_sfarsit date,
    loc_prescriere integer DEFAULT 1,
    diagnostic text,
    cod_urgenta integer,
    cnp_ingrijit text,
    serie_initiala text,
    numar_initial text,
    este_continuare boolean DEFAULT false,
    data_certificat_initial date,
    venituri_6_luni numeric,
    zile_6_luni integer,
    program_national boolean DEFAULT false,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale OWNER TO iconta_user;

--
-- Name: concedii_medicale_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.concedii_medicale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: extras_linii; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.extras_linii (
    id integer NOT NULL,
    data date NOT NULL,
    descriere text,
    suma numeric(12,2) NOT NULL,
    valuta boolean DEFAULT false NOT NULL,
    tip character varying(10) NOT NULL,
    cui_detectat character varying(30),
    status character varying(15) DEFAULT 'nou'::character varying NOT NULL,
    alocari jsonb,
    nota_propusa jsonb,
    fisier_sursa character varying(255),
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    cont_extras character varying(34),
    referinta character varying(100)
);


ALTER TABLE TENANT_PLACEHOLDER.extras_linii OWNER TO iconta_user;

--
-- Name: extras_linii_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.extras_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.extras_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: extras_import; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
-- [C5] Registrul importurilor de extras bancar: un rand per FISIER importat (hash de continut). [16.10.2026, lotul 6 pct.1, 277]
-- Nu mai decide duplicatul (il decide miscarea, `reconciliere_api.importa_extras`); ramane registrul fisierelor.
-- Sursa unica a DDL-ului = core/migrare_extras_import.py.
--

CREATE TABLE TENANT_PLACEHOLDER.extras_import (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fisier_hash text NOT NULL,
    fisier_nume character varying(255),
    nr_linii integer NOT NULL DEFAULT 0,
    creat_la timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT extras_import_hash_uniq UNIQUE (fisier_hash)
);


ALTER TABLE TENANT_PLACEHOLDER.extras_import OWNER TO iconta_user;


--
-- Name: factura_linii; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.factura_linii (
    id integer NOT NULL,
    factura_id integer NOT NULL,
    descriere text NOT NULL,
    um character varying(10) DEFAULT 'buc'::character varying NOT NULL,
    cantitate numeric(12,3) DEFAULT 1 NOT NULL,
    pret_unitar numeric(12,2) DEFAULT 0 NOT NULL,
    cota_tva numeric(5,2) DEFAULT 21 NOT NULL,
    destinatie_tva text DEFAULT 'taxabil'::text NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.factura_linii OWNER TO iconta_user;

--
-- Name: factura_linii_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.factura_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.factura_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: facturi; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.facturi (
    id integer NOT NULL,
    client_id integer,
    numar character varying(50) NOT NULL,
    data_emitere date NOT NULL,
    data_faptului_generator date,  -- [A2 art.284 D390] OPTIONAL: exigibilitate IC = MIN(data_emitere, ziua 15 a lunii urmatoare faptului); NULL -> incadrare pe data_emitere (comportament anterior)
    tert_platitor_tva boolean,  -- [B clasifica_partener] statutul TVA al tertului INGHETAT la factura (fapt); True->tip1, False->tip2/N, NULL->euristica de forma (legacy)
    data_scadenta date,
    total numeric(12,2) DEFAULT 0 NOT NULL,
    tva numeric(12,2) DEFAULT 0 NOT NULL,
    moneda character varying(3) DEFAULT 'RON'::character varying NOT NULL,
    directie character varying(10) DEFAULT 'emisa'::character varying NOT NULL,
    status character varying(20) DEFAULT 'emisa'::character varying,
    xml text,
    tert_nume character varying(255),
    tert_cui character varying(30),
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    serie character varying(10),
    storno_din_id integer,
    curs_bnr numeric,
    tva_lei numeric(12,2),
    total_lei numeric(12,2),
    data_curs date,
    curs_sursa character varying(10),
    tert_adresa text,
    taxare_inversa boolean DEFAULT false NOT NULL,
    tert_tara text DEFAULT 'RO'::text NOT NULL,  -- [B1 D300] cod ISO 2 litere partener (IC/export)
    tip_operatiune text DEFAULT 'normal'::text NOT NULL,  -- [B1 D300] {normal,avans,regularizare_avans}: avansul e exigibil la emitere (art.282 al.2 lit.b)
    furnizor_tva_incasare boolean DEFAULT false NOT NULL,  -- [B1 D300] pe PRIMITE: furnizor la incasare -> deducere amanata la plata (art.297 al.2)
    axa_ic text,  -- [R186 16.09.2026] 'bunuri'|'servicii' pe operatiunea IC, INGHETATA la introducere; NULL = nedeclarata (facturi istorice). Vezi core/migrare_axa_ic.py
    CONSTRAINT facturi_axa_ic_chk CHECK (axa_ic IS NULL OR axa_ic IN ('bunuri','servicii')),
    categorie_331 character varying(30),
    tip character varying(10) DEFAULT 'factura'::character varying NOT NULL,
    transformat_in_id integer,
    sursa_externa character varying(50),
    link_plata text,
    plata_provider character varying(20),
    plata_ref character varying(100),
    platita_la timestamp with time zone,
    plata_confirmata_de character varying(20)
);


ALTER TABLE TENANT_PLACEHOLDER.facturi OWNER TO iconta_user;

--
-- Name: facturi_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.facturi ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.facturi_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: facturi_recurente; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.facturi_recurente (
    id integer NOT NULL,
    client_id integer,
    tert_nume character varying(255),
    tert_cui character varying(30),
    linii jsonb NOT NULL,
    zi_emitere integer DEFAULT 1 NOT NULL,
    moneda character varying(3) DEFAULT 'RON'::character varying NOT NULL,
    activ boolean DEFAULT true NOT NULL,
    ultima_emitere date,
    creat_la timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT facturi_recurente_zi_emitere_check CHECK (((zi_emitere >= 1) AND (zi_emitere <= 28)))
);


ALTER TABLE TENANT_PLACEHOLDER.facturi_recurente OWNER TO iconta_user;

--
-- Name: facturi_recurente_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE SEQUENCE TENANT_PLACEHOLDER.facturi_recurente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE TENANT_PLACEHOLDER.facturi_recurente_id_seq OWNER TO iconta_user;

--
-- Name: facturi_recurente_id_seq; Type: SEQUENCE OWNED BY; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER SEQUENCE TENANT_PLACEHOLDER.facturi_recurente_id_seq OWNED BY TENANT_PLACEHOLDER.facturi_recurente.id;


--
-- Name: firma_profil; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.firma_profil (
    id integer DEFAULT 1 NOT NULL,
    nume character varying(255) NOT NULL,
    cui character varying(20) NOT NULL,
    reg_com character varying(50),
    adresa text,
    oras character varying(100),
    judet character varying(10),
    cod_postal character varying(20),
    iban character varying(34),
    banca text,
    email text,
    telefon text,
    caen text,
    declarant_nume text,
    declarant_prenume text,
    declarant_functie text,
    patron_nume text,
    -- [R65, 26.08.2026] `patron_email` scos: avea precedenta la trimiterea
    -- pachetului si nicio cale de scriere. Vezi core/migrare_patron_email.py.
    logo text,
    tip_decont text,
    cont_venit_implicit character varying(10) DEFAULT '707',
    pro_rata numeric,
    regim_fiscal text,
    platitor_tva boolean,
    operatiuni_ic boolean,
    serie_factura character varying(10),
    urmator_numar_factura integer DEFAULT 1 NOT NULL,
    font_factura character varying(30) DEFAULT 'sans'::character varying,
    culoare_factura character varying(10) DEFAULT '#1d4ed8'::character varying,
    tva_la_incasare boolean DEFAULT false NOT NULL,
    urmator_numar_proforma integer DEFAULT 1 NOT NULL,
    urmator_numar_aviz integer DEFAULT 1 NOT NULL,
    wc_url text,
    wc_ck text,
    wc_cs text,
    wc_ultima_sinc date,
    CONSTRAINT firma_profil_singleton CHECK ((id = 1)),
    baza_contabila character varying(12) DEFAULT 'A'::character varying NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.firma_profil OWNER TO iconta_user;

--
-- Name: furnizori; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.furnizori (
    id integer NOT NULL,
    nume character varying(255) NOT NULL,
    cui character varying(20),
    adresa text,
    email character varying(255),
    telefon character varying(50),
    oras character varying(100),
    judet character varying(10),
    cod_postal character varying(20),
    status character varying(20) DEFAULT 'activ'::character varying NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.furnizori OWNER TO iconta_user;

--
-- Name: furnizori_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.furnizori ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.furnizori_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: inregistrari; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.inregistrari (
    id integer NOT NULL,
    data date NOT NULL,
    numar character varying(50),
    factura_id integer,
    document_ref character varying(255),
    descriere text,
    sursa text,
    status character varying(20) DEFAULT 'ciorna'::character varying NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.inregistrari OWNER TO iconta_user;

--
-- [R61 / P5 val 1b, 10.09.2026] UNICITATEA RAPORTULUI Z, in BAZA, nu doar in cod.
-- Poarta traia numai in `main.py::_cere_z_unic`: un SELECT, apoi un INSERT, fara nimic
-- intre ele. Nu s-a vazut pana la P5 fiindca ruta era `async def` fara niciun `await`
-- dupa citirea fisierului, deci bucla o rula pana la capat fara s-o intrerupa — o
-- garantie accidentala, nu una a datelor. Indexul e PARTIAL: alte surse au voie sa
-- repete un numar (o nota manuala si una de banca pot purta acelasi `numar`).
--
CREATE UNIQUE INDEX IF NOT EXISTS inregistrari_raport_z_unic
    ON TENANT_PLACEHOLDER.inregistrari (sursa, numar)
    WHERE sursa IN ('horeca_z', 'amef') AND numar IS NOT NULL;

--
-- Name: inregistrari_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.inregistrari ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.inregistrari_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: inregistrari_linii; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.inregistrari_linii (
    id integer NOT NULL,
    inregistrare_id integer NOT NULL,
    cont_debit character varying(10) NOT NULL,
    cont_credit character varying(10) NOT NULL,
    suma numeric(14,2) NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.inregistrari_linii OWNER TO iconta_user;

--
-- Name: inregistrari_linii_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.inregistrari_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.inregistrari_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: mijloace_fixe; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.mijloace_fixe (
    id integer NOT NULL,
    cod text,
    denumire text NOT NULL,
    cont_imobilizare text DEFAULT '2131'::text,
    cont_amortizare text DEFAULT '2813'::text,
    valoare numeric DEFAULT 0 NOT NULL,
    rezidual numeric DEFAULT 0,
    dnf_luni integer DEFAULT 12 NOT NULL,
    data_pif date,
    metoda text DEFAULT 'liniara'::text,
    activ boolean DEFAULT true,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    destinatie_cd boolean NOT NULL DEFAULT false   -- [lot 19 d11] CF art.20 alin.(1) lit.b): accelerata si pt aparatura C&D
);


ALTER TABLE TENANT_PLACEHOLDER.mijloace_fixe OWNER TO iconta_user;

--
-- Name: mijloace_fixe_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.mijloace_fixe ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.mijloace_fixe_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: reevaluari; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--
-- [R59, 16.09.2026] Reevaluarea unei imobilizari, ca FAPT cu atribute. Sursa unica a DDL-ului e
-- core/migrare_reevaluare.py (idempotent, pentru schemele EXISTENTE); aici e oglinda pentru
-- tenantii NOI. `aplicata_la` NULL = nota inca e ciorna: efectul pe `mijloace_fixe.valoare` se
-- produce la VALIDAREA notei, nu la scrierea ei.
--

CREATE TABLE TENANT_PLACEHOLDER.reevaluari (
    id integer NOT NULL,
    inregistrare_id integer NOT NULL,
    mijloc_fix_id integer NOT NULL,
    data date NOT NULL,
    valoare_bruta_veche numeric NOT NULL,
    amortizare_eliminata numeric NOT NULL,
    valoare_justa numeric NOT NULL,
    aplicata_la timestamp with time zone,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.reevaluari OWNER TO iconta_user;

ALTER TABLE TENANT_PLACEHOLDER.reevaluari ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.reevaluari_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


ALTER TABLE ONLY TENANT_PLACEHOLDER.reevaluari
    ADD CONSTRAINT reevaluari_pkey PRIMARY KEY (id);

-- O nota = cel mult o reevaluare. Poarta e in BAZA: o a doua validare a aceleiasi note ar urca
-- valoarea inca o data, si nimic n-ar spune.
CREATE UNIQUE INDEX IF NOT EXISTS reevaluari_nota_unic
    ON TENANT_PLACEHOLDER.reevaluari (inregistrare_id);

CREATE INDEX IF NOT EXISTS reevaluari_mijloc_idx
    ON TENANT_PLACEHOLDER.reevaluari (mijloc_fix_id, data);


GRANT ALL ON TABLE TENANT_PLACEHOLDER.reevaluari TO iconta_user;
GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.reevaluari_id_seq TO iconta_user;


--
-- Name: miscari_stoc; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.miscari_stoc (
    id integer NOT NULL,
    articol_id integer NOT NULL,
    data date NOT NULL,
    tip character varying(10) NOT NULL,
    cantitate numeric(12,3) NOT NULL,
    pret_unitar numeric(12,4),
    valoare numeric(12,2) NOT NULL,
    document character varying(100),
    inregistrare_id integer,
    locatie character varying(100),
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc OWNER TO iconta_user;

--
-- Name: miscari_stoc_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.miscari_stoc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: nir; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.nir (
    id integer NOT NULL,
    numar character varying(50) NOT NULL,
    data date NOT NULL,
    furnizor character varying(255),
    cui character varying(30),
    factura_ref character varying(100),
    cost_total numeric(12,2) DEFAULT 0 NOT NULL,
    valoare_vanzare numeric(12,2) DEFAULT 0 NOT NULL,
    adaos_total numeric(12,2) DEFAULT 0 NOT NULL,
    tva_neexigibila numeric(12,2) DEFAULT 0 NOT NULL,
    transport numeric(12,2) DEFAULT 0 NOT NULL,
    taxe numeric(12,2) DEFAULT 0 NOT NULL,
    inregistrari_ids jsonb,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.nir OWNER TO iconta_user;

--
-- Name: nir_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.nir ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.nir_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: nir_linii; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.nir_linii (
    id integer NOT NULL,
    nir_id integer NOT NULL,
    denumire character varying(255) NOT NULL,
    cantitate numeric(12,3) NOT NULL,
    pret_achizitie numeric(12,4) NOT NULL,
    pret_vanzare numeric(12,4) NOT NULL,
    cota_tva numeric(5,2) DEFAULT 21 NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.nir_linii OWNER TO iconta_user;

--
-- Name: nir_linii_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.nir_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.nir_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: perioade_blocate; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.perioade_blocate (
    an integer NOT NULL,
    luna integer NOT NULL,
    blocat_de integer,
    blocat_la timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT perioade_blocate_luna_check CHECK (((luna >= 1) AND (luna <= 12)))
);


ALTER TABLE TENANT_PLACEHOLDER.perioade_blocate OWNER TO iconta_user;

--
-- Name: plan_conturi; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.plan_conturi (
    simbol character varying(10) NOT NULL,
    denumire text NOT NULL,
    tip character varying(20) DEFAULT 'Bifunctional'::character varying,
    sold_debitor numeric(15,2) DEFAULT 0,
    sold_creditor numeric(15,2) DEFAULT 0
);


ALTER TABLE TENANT_PLACEHOLDER.plan_conturi OWNER TO iconta_user;
-- [p97_plan_seed] Populare automata plan de conturi OMFP la creare firma (fix radacina 10.07.2026)
INSERT INTO TENANT_PLACEHOLDER.plan_conturi (simbol, denumire, tip) VALUES
('101', 'Capital', 'Bifunctional'),
('1011', 'Capital subscris nevărsat', 'Bifunctional'),
('1012', 'Capital subscris vărsat', 'Bifunctional'),
('1015', 'Patrimoniul regiei', 'Bifunctional'),
('1016', 'Patrimoniul public', 'Bifunctional'),
('1017', 'Patrimoniul privat', 'Bifunctional'),
('1018', 'Patrimoniul institutelor naționale de cercetare-dezvoltare', 'Bifunctional'),
('103', 'Alte elemente de capitaluri proprii', 'Bifunctional'),
('1031', 'Beneficii acordate angajaților sub forma instrumentelor de capitaluri proprii', 'Bifunctional'),
('1033', 'Diferențe de curs valutar în relație cu investiția netă într-o entitate străină', 'Bifunctional'),
('1038', 'Diferențe din modificarea valorii juste a activelor financiare disponibile în vederea vânzării și alte elemente de capitaluri proprii', 'Bifunctional'),
('104', 'Prime de capital', 'Bifunctional'),
('1041', 'Prime de emisiune', 'Bifunctional'),
('1042', 'Prime de fuziune/divizare', 'Bifunctional'),
('1043', 'Prime de aport', 'Bifunctional'),
('1044', 'Prime de conversie a obligațiunilor în acțiuni', 'Bifunctional'),
('105', 'Rezerve din reevaluare', 'Bifunctional'),
('106', 'Rezerve', 'Bifunctional'),
('1061', 'Rezerve legale', 'Bifunctional'),
('1063', 'Rezerve statutare sau contractuale', 'Bifunctional'),
('1068', 'Alte rezerve', 'Bifunctional'),
('107', 'Diferențe de curs valutar din conversie', 'Bifunctional'),
('108', 'Interese care nu controlează', 'Bifunctional'),
('1081', 'Interese care nu controlează - rezultatul exercițiului financiar', 'Bifunctional'),
('1082', 'Interese care nu controlează - alte capitaluri proprii', 'Bifunctional'),
('109', 'Acțiuni proprii', 'Bifunctional'),
('1091', 'Acțiuni proprii deținute pe termen scurt', 'Bifunctional'),
('1092', 'Acțiuni proprii deținute pe termen lung', 'Bifunctional'),
('1095', 'Acțiuni proprii reprezentând titluri deținute de societatea absorbită la societatea absorbantă', 'Bifunctional'),
('117', 'Rezultatul reportat', 'Bifunctional'),
('1171', 'Rezultatul reportat reprezentând profitul nerepartizat sau pierderea neacoperită', 'Bifunctional'),
('1172', 'Rezultatul reportat provenit din adoptarea pentru prima dată a IAS, mai puțin IAS 29', 'Bifunctional'),
('1173', 'Rezultatul reportat provenit din modificările politicilor contabile', 'Bifunctional'),
('1174', 'Rezultatul reportat provenit din corectarea erorilor contabile', 'Bifunctional'),
('1175', 'Rezultatul reportat reprezentând surplusul realizat din rezerve din reevaluare', 'Bifunctional'),
('1176', 'Rezultatul reportat provenit din trecerea la aplicarea reglementărilor contabile conforme cu directivele europene', 'Bifunctional'),
('121', 'Profit sau pierdere', 'Bifunctional'),
('129', 'Repartizarea profitului', 'Bifunctional'),
('141', 'Câștiguri legate de vânzarea sau anularea instrumentelor de capitaluri proprii', 'Bifunctional'),
('1411', 'Câștiguri legate de vânzarea instrumentelor de capitaluri proprii', 'Bifunctional'),
('1412', 'Câștiguri legate de anularea instrumentelor de capitaluri proprii', 'Bifunctional'),
('149', 'Pierderi legate de emiterea, răscumpărarea, vânzarea, cedarea cu titlu gratuit sau anularea instrumentelor de capitaluri proprii', 'Bifunctional'),
('1491', 'Pierderi rezultate din vânzarea instrumentelor de capitaluri proprii', 'Bifunctional'),
('1495', 'Pierderi rezultate din reorganizări, care sunt determinate de anularea titlurilor deținute', 'Bifunctional'),
('1496', 'Pierderi rezultate din reorganizări de societăți, corespunzătoare activului net negativ al societății absorbite', 'Bifunctional'),
('1498', 'Alte pierderi legate de instrumentele de capitaluri proprii', 'Bifunctional'),
('151', 'Provizioane', 'Bifunctional'),
('1511', 'Provizioane pentru litigii', 'Bifunctional'),
('1512', 'Provizioane pentru garanții acordate clienților', 'Bifunctional'),
('1513', 'Provizioane pentru dezafectare imobilizări corporale și alte acțiuni similare legate de acestea', 'Bifunctional'),
('1514', 'Provizioane pentru restructurare', 'Bifunctional'),
('1515', 'Provizioane pentru pensii și obligații similare', 'Bifunctional'),
('1516', 'Provizioane pentru impozite', 'Bifunctional'),
('1517', 'Provizioane pentru terminarea contractului de muncă', 'Bifunctional'),
('1518', 'Alte provizioane', 'Bifunctional'),
('161', 'Împrumuturi din emisiuni de obligațiuni', 'Bifunctional'),
('1614', 'Împrumuturi externe din emisiuni de obligațiuni garantate de stat', 'Bifunctional'),
('1615', 'Împrumuturi externe din emisiuni de obligațiuni garantate de bănci', 'Bifunctional'),
('1617', 'Împrumuturi interne din emisiuni de obligațiuni garantate de stat', 'Bifunctional'),
('1618', 'Alte împrumuturi din emisiuni de obligațiuni', 'Bifunctional'),
('162', 'Credite bancare pe termen lung', 'Bifunctional'),
('1621', 'Credite bancare pe termen lung', 'Bifunctional'),
('1622', 'Credite bancare pe termen lung nerambursate la scadență', 'Bifunctional'),
('1623', 'Credite externe guvernamentale', 'Bifunctional'),
('1624', 'Credite bancare externe garantate de stat', 'Bifunctional'),
('1625', 'Credite bancare externe garantate de bănci', 'Bifunctional'),
('1626', 'Credite de la trezoreria statului', 'Bifunctional'),
('1627', 'Credite bancare interne garantate de stat', 'Bifunctional'),
('166', 'Datorii care privesc imobilizările financiare', 'Bifunctional'),
('1661', 'Datorii față de entitățile afiliate', 'Bifunctional'),
('1663', 'Datorii față de entitățile asociate și entitățile controlate în comun', 'Bifunctional'),
('167', 'Alte împrumuturi și datorii asimilate', 'Bifunctional'),
('168', 'Dobânzi aferente împrumuturilor și datoriilor asimilate', 'Bifunctional'),
('1681', 'Dobânzi aferente împrumuturilor din emisiuni de obligațiuni', 'Bifunctional'),
('1682', 'Dobânzi aferente creditelor bancare pe termen lung', 'Bifunctional'),
('1685', 'Dobânzi aferente datoriilor față de entitățile afiliate', 'Bifunctional'),
('1686', 'Dobânzi aferente datoriilor față de entitățile asociate și entitățile controlate în comun', 'Bifunctional'),
('1687', 'Dobânzi aferente altor împrumuturi și datorii asimilate', 'Bifunctional'),
('169', 'Prime privind rambursarea obligațiunilor și a altor datorii', 'Bifunctional'),
('1691', 'Prime privind rambursarea obligațiunilor', 'Bifunctional'),
('1692', 'Prime privind rambursarea altor datorii', 'Bifunctional'),
('201', 'Cheltuieli de constituire', 'Bifunctional'),
('203', 'Cheltuieli de dezvoltare', 'Bifunctional'),
('205', 'Concesiuni, brevete, licențe, mărci comerciale, drepturi și active similare', 'Bifunctional'),
('206', 'Active necorporale de explorare și evaluare a resurselor minerale', 'Bifunctional'),
('207', 'Fond comercial', 'Bifunctional'),
('2071', 'Fond comercial pozitiv', 'Bifunctional'),
('2075', 'Fond comercial negativ', 'Bifunctional'),
('208', 'Alte imobilizări necorporale', 'Bifunctional'),
('211', 'Terenuri și amenajări de terenuri', 'Bifunctional'),
('2111', 'Terenuri', 'Bifunctional'),
('2112', 'Amenajări de terenuri', 'Bifunctional'),
('212', 'Construcții', 'Bifunctional'),
('213', 'Instalații tehnice și mijloace de transport', 'Bifunctional'),
('2131', 'Echipamente tehnologice (mașini, utilaje și instalații de lucru)', 'Bifunctional'),
('2132', 'Aparate și instalații de măsurare, control și reglare', 'Bifunctional'),
('2133', 'Mijloace de transport', 'Bifunctional'),
('214', 'Mobilier, aparatură birotică, echipamente de protecție a valorilor umane și materiale și alte active corporale', 'Bifunctional'),
('215', 'Investiții imobiliare', 'Bifunctional'),
('216', 'Active corporale de explorare și evaluare a resurselor minerale', 'Bifunctional'),
('217', 'Active biologice productive', 'Bifunctional'),
('223', 'Instalații tehnice și mijloace de transport în curs de aprovizionare', 'Bifunctional'),
('224', 'Mobilier, aparatură birotică, echipamente de protecție a valorilor umane și materiale și alte active corporale în curs de aprovizionare', 'Bifunctional'),
('227', 'Active biologice productive în curs de aprovizionare', 'Bifunctional'),
('231', 'Imobilizări corporale în curs de execuție', 'Bifunctional'),
('235', 'Investiții imobiliare în curs de execuție', 'Bifunctional'),
('261', 'Acțiuni deținute la entitățile afiliate', 'Bifunctional'),
('262', 'Acțiuni deținute la entități asociate', 'Bifunctional'),
('263', 'Acțiuni deținute la entități controlate în comun', 'Bifunctional'),
('264', 'Titluri puse în echivalență', 'Bifunctional'),
('265', 'Alte titluri imobilizate', 'Bifunctional'),
('266', 'Certificate verzi amânate', 'Bifunctional'),
('267', 'Creanțe imobilizate', 'Bifunctional'),
('2671', 'Sume de încasat de la entitățile afiliate', 'Bifunctional'),
('2672', 'Dobânda aferentă sumelor de încasat de la entitățile afiliate', 'Bifunctional'),
('2673', 'Creanțe față de entitățile asociate și entitățile controlate în comun', 'Bifunctional'),
('2674', 'Dobânda aferentă creanțelor față de entitățile asociate și entitățile controlate în comun', 'Bifunctional'),
('2675', 'Împrumuturi acordate pe termen lung', 'Bifunctional'),
('2676', 'Dobânda aferentă împrumuturilor acordate pe termen lung', 'Bifunctional'),
('2677', 'Obligațiuni achiziționate cu ocazia emisiunilor efectuate de terți', 'Bifunctional'),
('2678', 'Alte creanțe imobilizate', 'Bifunctional'),
('2679', 'Dobânzi aferente altor creanțe imobilizate', 'Bifunctional'),
('269', 'Vărsăminte de efectuat pentru imobilizări financiare', 'Bifunctional'),
('2691', 'Vărsăminte de efectuat privind acțiunile deținute la entitățile afiliate', 'Bifunctional'),
('2692', 'Vărsăminte de efectuat privind acțiunile deținute la entități asociate', 'Bifunctional'),
('2693', 'Vărsăminte de efectuat privind acțiunile deținute la entități controlate în comun', 'Bifunctional'),
('2695', 'Vărsăminte de efectuat pentru alte imobilizări financiare', 'Bifunctional'),
('280', 'Amortizări privind imobilizările necorporale', 'Bifunctional'),
('2801', 'Amortizarea cheltuielilor de constituire', 'Bifunctional'),
('2803', 'Amortizarea cheltuielilor de dezvoltare', 'Bifunctional'),
('2805', 'Amortizarea concesiunilor, brevetelor, licențelor, mărcilor comerciale, drepturilor și activelor similare', 'Bifunctional'),
('2806', 'Amortizarea activelor necorporale de explorare și evaluare a resurselor minerale', 'Bifunctional'),
('2807', 'Amortizarea fondului comercial', 'Bifunctional'),
('2808', 'Amortizarea altor imobilizări necorporale', 'Bifunctional'),
('281', 'Amortizări privind imobilizările corporale', 'Bifunctional'),
('2811', 'Amortizarea amenajărilor de terenuri', 'Bifunctional'),
('2812', 'Amortizarea construcțiilor', 'Bifunctional'),
('2813', 'Amortizarea instalațiilor și mijloacelor de transport', 'Bifunctional'),
('2814', 'Amortizarea altor imobilizări corporale', 'Bifunctional'),
('2815', 'Amortizarea investițiilor imobiliare', 'Bifunctional'),
('2816', 'Amortizarea activelor corporale de explorare și evaluare a resurselor minerale', 'Bifunctional'),
('2817', 'Amortizarea activelor biologice productive', 'Bifunctional'),
('290', 'Ajustări pentru deprecierea imobilizărilor necorporale', 'Bifunctional'),
('2903', 'Ajustări pentru deprecierea cheltuielilor de dezvoltare', 'Bifunctional'),
('2905', 'Ajustări pentru deprecierea concesiunilor, brevetelor, licențelor, mărcilor comerciale, drepturilor și activelor similare', 'Bifunctional'),
('2906', 'Ajustări pentru deprecierea activelor necorporale de explorare și evaluare a resurselor minerale', 'Bifunctional'),
('2908', 'Ajustări pentru deprecierea altor imobilizări necorporale', 'Bifunctional'),
('291', 'Ajustări pentru deprecierea imobilizărilor corporale', 'Bifunctional'),
('2911', 'Ajustări pentru deprecierea terenurilor și amenajărilor de terenuri', 'Bifunctional'),
('2912', 'Ajustări pentru deprecierea construcțiilor', 'Bifunctional'),
('2913', 'Ajustări pentru deprecierea instalațiilor și mijloacelor de transport', 'Bifunctional'),
('2914', 'Ajustări pentru deprecierea altor imobilizări corporale', 'Bifunctional'),
('2915', 'Ajustări pentru deprecierea investițiilor imobiliare', 'Bifunctional'),
('2916', 'Ajustări pentru deprecierea activelor corporale de explorare și evaluare a resurselor minerale', 'Bifunctional'),
('2917', 'Ajustări pentru deprecierea activelor biologice productive', 'Bifunctional'),
('293', 'Ajustări pentru deprecierea imobilizărilor în curs de execuție', 'Bifunctional'),
('2931', 'Ajustări pentru deprecierea imobilizărilor corporale în curs de execuție', 'Bifunctional'),
('2935', 'Ajustări pentru deprecierea investițiilor imobiliare în curs de execuție', 'Bifunctional'),
('296', 'Ajustări pentru pierderea de valoare a imobilizărilor financiare', 'Bifunctional'),
('2961', 'Ajustări pentru pierderea de valoare a acțiunilor deținute la entitățile afiliate', 'Bifunctional'),
('2962', 'Ajustări pentru pierderea de valoare a acțiunilor deținute la entități asociate și entități controlate în comun', 'Bifunctional'),
('2963', 'Ajustări pentru pierderea de valoare a altor titluri imobilizate', 'Bifunctional'),
('2964', 'Ajustări pentru pierderea de valoare a sumelor de încasat de la entitățile afiliate', 'Bifunctional'),
('2965', 'Ajustări pentru pierderea de valoare a creanțelor față de entitățile asociate și entitățile controlate în comun', 'Bifunctional'),
('2966', 'Ajustări pentru pierderea de valoare a împrumuturilor acordate pe termen lung', 'Bifunctional'),
('2968', 'Ajustări pentru pierderea de valoare a altor creanțe imobilizate', 'Bifunctional'),
('301', 'Materii prime', 'Bifunctional'),
('302', 'Materiale consumabile', 'Bifunctional'),
('3021', 'Materiale auxiliare', 'Bifunctional'),
('3022', 'Combustibili', 'Bifunctional'),
('3023', 'Materiale pentru ambalat', 'Bifunctional'),
('3024', 'Piese de schimb', 'Bifunctional'),
('3025', 'Semințe și materiale de plantat', 'Bifunctional'),
('3026', 'Furaje', 'Bifunctional'),
('3028', 'Alte materiale consumabile', 'Bifunctional'),
('303', 'Materiale de natura obiectelor de inventar', 'Bifunctional'),
('308', 'Diferențe de preț la materii prime și materiale', 'Bifunctional'),
('321', 'Materii prime în curs de aprovizionare', 'Bifunctional'),
('322', 'Materiale consumabile în curs de aprovizionare', 'Bifunctional'),
('323', 'Materiale de natura obiectelor de inventar în curs de aprovizionare', 'Bifunctional'),
('326', 'Active biologice de natura stocurilor în curs de aprovizionare', 'Bifunctional'),
('327', 'Mărfuri în curs de aprovizionare', 'Bifunctional'),
('328', 'Ambalaje în curs de aprovizionare', 'Bifunctional'),
('331', 'Produse în curs de execuție', 'Bifunctional'),
('332', 'Servicii în curs de execuție', 'Bifunctional'),
('341', 'Semifabricate', 'Bifunctional'),
('345', 'Produse finite', 'Bifunctional'),
('346', 'Produse reziduale', 'Bifunctional'),
('347', 'Produse agricole', 'Bifunctional'),
('348', 'Diferențe de preț la produse', 'Bifunctional'),
('351', 'Materii și materiale aflate la terți', 'Bifunctional'),
('354', 'Produse aflate la terți', 'Bifunctional'),
('356', 'Active biologice de natura stocurilor aflate la terți', 'Bifunctional'),
('357', 'Mărfuri aflate la terți', 'Bifunctional'),
('358', 'Ambalaje aflate la terți', 'Bifunctional'),
('361', 'Active biologice de natura stocurilor', 'Bifunctional'),
('368', 'Diferențe de preț la active biologice de natura stocurilor', 'Bifunctional'),
('371', 'Mărfuri', 'Bifunctional'),
('378', 'Diferențe de preț la mărfuri', 'Bifunctional'),
('381', 'Ambalaje', 'Bifunctional'),
('388', 'Diferențe de preț la ambalaje', 'Bifunctional'),
('391', 'Ajustări pentru deprecierea materiilor prime', 'Bifunctional'),
('392', 'Ajustări pentru deprecierea materialelor', 'Bifunctional'),
('3921', 'Ajustări pentru deprecierea materialelor consumabile', 'Bifunctional'),
('3922', 'Ajustări pentru deprecierea materialelor de natura obiectelor de inventar', 'Bifunctional'),
('393', 'Ajustări pentru deprecierea producției în curs de execuție', 'Bifunctional'),
('394', 'Ajustări pentru deprecierea produselor', 'Bifunctional'),
('3941', 'Ajustări pentru deprecierea semifabricatelor', 'Bifunctional'),
('3945', 'Ajustări pentru deprecierea produselor finite', 'Bifunctional'),
('3946', 'Ajustări pentru deprecierea produselor reziduale', 'Bifunctional'),
('3947', 'Ajustări pentru deprecierea produselor agricole', 'Bifunctional'),
('395', 'Ajustări pentru deprecierea stocurilor aflate la terți', 'Bifunctional'),
('3951', 'Ajustări pentru deprecierea materiilor și materialelor aflate la terți', 'Bifunctional'),
('3952', 'Ajustări pentru deprecierea semifabricatelor aflate la terți', 'Bifunctional'),
('3953', 'Ajustări pentru deprecierea produselor finite aflate la terți', 'Bifunctional'),
('3954', 'Ajustări pentru deprecierea produselor reziduale aflate la terți', 'Bifunctional'),
('3955', 'Ajustări pentru deprecierea produselor agricole aflate la terți', 'Bifunctional'),
('3956', 'Ajustări pentru deprecierea activelor biologice de natura stocurilor aflate la terți', 'Bifunctional'),
('3957', 'Ajustări pentru deprecierea mărfurilor aflate la terți', 'Bifunctional'),
('3958', 'Ajustări pentru deprecierea ambalajelor aflate la terți', 'Bifunctional'),
('396', 'Ajustări pentru deprecierea activelor biologice de natura stocurilor', 'Bifunctional'),
('397', 'Ajustări pentru deprecierea mărfurilor', 'Bifunctional'),
('398', 'Ajustări pentru deprecierea ambalajelor', 'Bifunctional'),
('401', 'Furnizori', 'Bifunctional'),
('403', 'Efecte de plătit', 'Bifunctional'),
('404', 'Furnizori de imobilizări', 'Bifunctional'),
('405', 'Efecte de plătit pentru imobilizări', 'Bifunctional'),
('408', 'Furnizori - facturi nesosite', 'Bifunctional'),
('409', 'Furnizori - debitori', 'Bifunctional'),
('4091', 'Furnizori - debitori pentru cumpărări de bunuri de natura stocurilor', 'Bifunctional'),
('4092', 'Furnizori - debitori pentru prestări de servicii', 'Bifunctional'),
('4093', 'Avansuri acordate pentru imobilizări corporale', 'Bifunctional'),
('4094', 'Avansuri acordate pentru imobilizări necorporale', 'Bifunctional'),
('411', 'Clienți', 'Bifunctional'),
('4111', 'Clienți', 'Bifunctional'),
('4118', 'Clienți incerți sau în litigiu', 'Bifunctional'),
('413', 'Efecte de primit de la clienți', 'Bifunctional'),
('418', 'Clienți - facturi de întocmit', 'Bifunctional'),
('419', 'Clienți - creditori', 'Bifunctional'),
('421', 'Personal - salarii datorate', 'Bifunctional'),
('423', 'Personal - ajutoare materiale datorate', 'Bifunctional'),
('424', 'Prime reprezentând participarea personalului la profit', 'Bifunctional'),
('425', 'Avansuri acordate personalului', 'Bifunctional'),
('426', 'Drepturi de personal neridicate', 'Bifunctional'),
('427', 'Rețineri din salarii datorate terților', 'Bifunctional'),
('428', 'Alte datorii și creanțe în legătură cu personalul', 'Bifunctional'),
('4281', 'Alte datorii în legătură cu personalul', 'Bifunctional'),
('4282', 'Alte creanțe în legătură cu personalul', 'Bifunctional'),
('431', 'Asigurări sociale', 'Bifunctional'),
('4311', 'Contribuția unității la asigurările sociale', 'Bifunctional'),
('4312', 'Contribuția personalului la asigurările sociale', 'Bifunctional'),
('4313', 'Contribuția angajatorului pentru asigurările sociale de sănătate', 'Bifunctional'),
('4314', 'Contribuția angajaților pentru asigurările sociale de sănătate', 'Bifunctional'),
('4315', 'Contribuția de asigurări sociale', 'Bifunctional'),
('4316', 'Contribuția de asigurări sociale de sănătate', 'Bifunctional'),
('4318', 'Alte contribuții pentru asigurările sociale de sănătate', 'Bifunctional'),
('436', 'Contribuția asiguratorie pentru muncă', 'Bifunctional'),
('437', 'Ajutor de șomaj', 'Bifunctional'),
('4371', 'Contribuția unității la fondul de șomaj', 'Bifunctional'),
('4372', 'Contribuția personalului la fondul de șomaj', 'Bifunctional'),
('438', 'Alte datorii și creanțe sociale', 'Bifunctional'),
('4381', 'Alte datorii sociale', 'Bifunctional'),
('4382', 'Alte creanțe sociale', 'Bifunctional'),
('441', 'Impozitul pe profit și alte impozite', 'Bifunctional'),
('4411', 'Impozitul pe profit', 'Bifunctional'),
('4415', 'Impozitul specific unor activități', 'Bifunctional'),
('4417', 'Impozitul pe profit la nivelul impozitului minim pe cifra de afaceri', 'Bifunctional'),
('4418', 'Impozitul pe venit', 'Bifunctional'),
('442', 'Taxa pe valoarea adăugată', 'Bifunctional'),
('4423', 'TVA de plată', 'Bifunctional'),
('4424', 'TVA de recuperat', 'Bifunctional'),
('4426', 'TVA deductibilă', 'Bifunctional'),
('4427', 'TVA colectată', 'Bifunctional'),
('4428', 'TVA neexigibilă', 'Bifunctional'),
('4428.01', 'TVA neexigibilă — achiziții fără factură (NIR)', 'Bifunctional'),
('4428.02', 'TVA neexigibilă aferentă mărfurilor (preț de vânzare)', 'Bifunctional'),
('444', 'Impozitul pe venituri de natura salariilor', 'Bifunctional'),
('445', 'Subvenții', 'Bifunctional'),
('4451', 'Subvenții guvernamentale', 'Bifunctional'),
('4452', 'Împrumuturi nerambursabile cu caracter de subvenții', 'Bifunctional'),
('4458', 'Alte sume primite cu caracter de subvenții', 'Bifunctional'),
('446', 'Alte impozite, taxe și vărsăminte asimilate', 'Bifunctional'),
('447', 'Fonduri speciale - taxe și vărsăminte asimilate', 'Bifunctional'),
('448', 'Alte datorii și creanțe cu bugetul statului', 'Bifunctional'),
('4481', 'Alte datorii față de bugetul statului', 'Bifunctional'),
('4482', 'Alte creanțe privind bugetul statului', 'Bifunctional'),
('451', 'Decontări între entitățile afiliate', 'Bifunctional'),
('4511', 'Decontări între entitățile afiliate', 'Bifunctional'),
('4518', 'Dobânzi aferente decontărilor între entitățile afiliate', 'Bifunctional'),
('453', 'Decontări cu entitățile asociate și entitățile controlate în comun', 'Bifunctional'),
('4531', 'Decontări cu entitățile asociate și entitățile controlate', 'Bifunctional'),
('4538', 'Dobânzi aferente decontărilor cu entitățile asociate și entitățile controlate în comun', 'Bifunctional'),
('455', 'Sume datorate acționarilor/asociaților', 'Bifunctional'),
('4551', 'Acționari/Asociați - conturi curente', 'Bifunctional'),
('4558', 'Acționari/Asociați - dobânzi la conturi curente', 'Bifunctional'),
('456', 'Decontări cu acționarii/asociații privind capitalul', 'Bifunctional'),
('457', 'Dividende de plată', 'Bifunctional'),
('458', 'Decontări din operațiuni în participație', 'Bifunctional'),
('4581', 'Decontări din operațiuni în participație - pasiv', 'Bifunctional'),
('4582', 'Decontări din operațiuni în participație - activ', 'Bifunctional'),
('461', 'Debitori diverși', 'Bifunctional'),
('462', 'Creditori diverși', 'Bifunctional'),
('463', 'Creanțe reprezentând dividende repartizate în cursul exercițiului financiar', 'Bifunctional'),
('466', 'Decontări din operațiuni de fiducie', 'Bifunctional'),
('4661', 'Datorii din operațiuni de fiducie', 'Bifunctional'),
('4662', 'Creanțe din operațiuni de fiducie', 'Bifunctional'),
('467', 'Datorii aferente distribuirilor interimare de dividende', 'Bifunctional'),
('471', 'Cheltuieli înregistrate în avans', 'Bifunctional'),
('472', 'Venituri înregistrate în avans', 'Bifunctional'),
('473', 'Decontări din operațiuni în curs de clarificare', 'Bifunctional'),
('475', 'Subvenții pentru investiții', 'Bifunctional'),
('4751', 'Subvenții guvernamentale pentru investiții', 'Bifunctional'),
('4752', 'Împrumuturi nerambursabile cu caracter de subvenții pentru investiții', 'Bifunctional'),
('4753', 'Donații pentru investiții', 'Bifunctional'),
('4754', 'Plusuri de inventar de natura imobilizărilor', 'Bifunctional'),
('4758', 'Alte sume primite cu caracter de subvenții pentru investiții', 'Bifunctional'),
('478', 'Venituri în avans aferente activelor primite prin transfer de la clienți', 'Bifunctional'),
('481', 'Decontări între unitate și subunități', 'Bifunctional'),
('482', 'Decontări între subunități', 'Bifunctional'),
('490', 'Ajustări pentru deprecierea creanțelor reprezentând avansuri acordate furnizorilor', 'Bifunctional'),
('4901', 'Ajustări pentru deprecierea creanțelor aferente cumpărărilor de bunuri de natura stocurilor', 'Bifunctional'),
('4902', 'Ajustări pentru deprecierea creanțelor aferente prestărilor de servicii', 'Bifunctional'),
('4903', 'Ajustări pentru deprecierea creanțelor aferente imobilizărilor corporale', 'Bifunctional'),
('4904', 'Ajustări pentru deprecierea creanțelor aferente imobilizărilor necorporale', 'Bifunctional'),
('491', 'Ajustări pentru deprecierea creanțelor - clienți', 'Bifunctional'),
('495', 'Ajustări pentru deprecierea creanțelor - decontări în cadrul grupului și cu acționarii/asociații', 'Bifunctional'),
('496', 'Ajustări pentru deprecierea creanțelor - debitori diverși', 'Bifunctional'),
('501', 'Acțiuni deținute la entitățile afiliate', 'Bifunctional'),
('505', 'Obligațiuni emise și răscumpărate', 'Bifunctional'),
('506', 'Obligațiuni', 'Bifunctional'),
('507', 'Certificate verzi primite', 'Bifunctional'),
('508', 'Alte investiții pe termen scurt și creanțe asimilate', 'Bifunctional'),
('5081', 'Alte titluri de plasament', 'Bifunctional'),
('5088', 'Dobânzi la obligațiuni și titluri de plasament', 'Bifunctional'),
('509', 'Vărsăminte de efectuat pentru investițiile pe termen scurt', 'Bifunctional'),
('5091', 'Vărsăminte de efectuat pentru acțiunile deținute la entitățile afiliate', 'Bifunctional'),
('5092', 'Vărsăminte de efectuat pentru alte investiții pe termen scurt', 'Bifunctional'),
('511', 'Valori de încasat', 'Bifunctional'),
('5112', 'Cecuri de încasat', 'Bifunctional'),
('5113', 'Efecte de încasat', 'Bifunctional'),
('5114', 'Efecte remise spre scontare', 'Bifunctional'),
('512', 'Conturi curente la bănci', 'Bifunctional'),
('5121', 'Conturi la bănci în lei', 'Bifunctional'),
('5124', 'Conturi la bănci în valută', 'Bifunctional'),
('5125', 'Sume în curs de decontare', 'Bifunctional'),
('518', 'Dobânzi', 'Bifunctional'),
('5186', 'Dobânzi de plătit', 'Bifunctional'),
('5187', 'Dobânzi de încasat', 'Bifunctional'),
('519', 'Credite bancare pe termen scurt', 'Bifunctional'),
('5191', 'Credite bancare pe termen scurt', 'Bifunctional'),
('5192', 'Credite bancare pe termen scurt nerambursate la scadență', 'Bifunctional'),
('5193', 'Credite externe guvernamentale', 'Bifunctional'),
('5194', 'Credite externe garantate de stat', 'Bifunctional'),
('5195', 'Credite externe garantate de bănci', 'Bifunctional'),
('5196', 'Credite de la Trezoreria Statului', 'Bifunctional'),
('5197', 'Credite interne garantate de stat', 'Bifunctional'),
('5198', 'Dobânzi aferente creditelor bancare pe termen scurt', 'Bifunctional'),
('531', 'Casa', 'Bifunctional'),
('5311', 'Casa în lei', 'Bifunctional'),
('5314', 'Casa în valută', 'Bifunctional'),
('532', 'Alte valori', 'Bifunctional'),
('5321', 'Timbre fiscale și poștale', 'Bifunctional'),
('5322', 'Bilete de tratament și odihnă', 'Bifunctional'),
('5323', 'Tichete și bilete de călătorie', 'Bifunctional'),
('5328', 'Alte valori', 'Bifunctional'),
('541', 'Acreditive', 'Bifunctional'),
('5411', 'Acreditive în lei', 'Bifunctional'),
('5414', 'Acreditive în valută', 'Bifunctional'),
('542', 'Avansuri de trezorerie', 'Bifunctional'),
('581', 'Viramente interne', 'Bifunctional'),
('591', 'Ajustări pentru pierderea de valoare a acțiunilor deținute la entitățile afiliate', 'Bifunctional'),
('595', 'Ajustări pentru pierderea de valoare a obligațiunilor emise și răscumpărate', 'Bifunctional'),
('596', 'Ajustări pentru pierderea de valoare a obligațiunilor', 'Bifunctional'),
('598', 'Ajustări pentru pierderea de valoare a altor investiții pe termen scurt și creanțe asimilate', 'Bifunctional'),
('601', 'Cheltuieli cu materiile prime', 'Bifunctional'),
('602', 'Cheltuieli cu materialele consumabile', 'Bifunctional'),
('6021', 'Cheltuieli cu materialele auxiliare', 'Bifunctional'),
('6022', 'Cheltuieli privind combustibilii', 'Bifunctional'),
('6023', 'Cheltuieli privind materialele pentru ambalat', 'Bifunctional'),
('6024', 'Cheltuieli privind piesele de schimb', 'Bifunctional'),
('6025', 'Cheltuieli privind semințele și materialele de plantat', 'Bifunctional'),
('6026', 'Cheltuieli privind furajele', 'Bifunctional'),
('6028', 'Cheltuieli privind alte materiale consumabile', 'Bifunctional'),
('603', 'Cheltuieli privind materialele de natura obiectelor de inventar', 'Bifunctional'),
('604', 'Cheltuieli privind materialele nestocate', 'Bifunctional'),
('605', 'Cheltuieli privind utilitățile', 'Bifunctional'),
('6051', 'Cheltuieli privind consumul de energie', 'Bifunctional'),
('6052', 'Cheltuieli privind consumul de apă', 'Bifunctional'),
('6053', 'Cheltuieli privind consumul de gaze naturale', 'Bifunctional'),
('6058', 'Cheltuieli cu alte utilități', 'Bifunctional'),
('606', 'Cheltuieli privind activele biologice de natura stocurilor', 'Bifunctional'),
('607', 'Cheltuieli privind mărfurile', 'Bifunctional'),
('608', 'Cheltuieli privind ambalajele', 'Bifunctional'),
('609', 'Reduceri comerciale primite', 'Bifunctional'),
('611', 'Cheltuieli cu întreținerea și reparațiile', 'Bifunctional'),
('612', 'Cheltuieli cu redevențele, locațiile de gestiune și chiriile', 'Bifunctional'),
('6121', 'Cheltuieli cu redevențele', 'Bifunctional'),
('6122', 'Cheltuieli cu locațiile de gestiune', 'Bifunctional'),
('6123', 'Cheltuieli cu chiriile', 'Bifunctional'),
('613', 'Cheltuieli cu primele de asigurare', 'Bifunctional'),
('614', 'Cheltuieli cu studiile și cercetările', 'Bifunctional'),
('615', 'Cheltuieli cu pregătirea personalului', 'Bifunctional'),
('616', 'Cheltuieli aferente drepturilor de proprietate intelectuală', 'Bifunctional'),
('617', 'Cheltuieli de management', 'Bifunctional'),
('618', 'Cheltuieli de consultanță', 'Bifunctional'),
('621', 'Cheltuieli cu colaboratorii', 'Bifunctional'),
('622', 'Cheltuieli privind comisioanele și onorariile', 'Bifunctional'),
('623', 'Cheltuieli de protocol, reclamă și publicitate', 'Bifunctional'),
('6231', 'Cheltuieli de protocol', 'Bifunctional'),
('6232', 'Cheltuieli de reclamă și publicitate', 'Bifunctional'),
('624', 'Cheltuieli cu transportul de bunuri și personal', 'Bifunctional'),
('625', 'Cheltuieli cu deplasări, detașări și transferări', 'Bifunctional'),
('626', 'Cheltuieli poștale și taxe de telecomunicații', 'Bifunctional'),
('627', 'Cheltuieli cu serviciile bancare și asimilate', 'Bifunctional'),
('628', 'Alte cheltuieli cu serviciile executate de terți', 'Bifunctional'),
('635', 'Cheltuieli cu alte impozite, taxe și vărsăminte asimilate', 'Bifunctional'),
('6351', 'Cheltuieli cu impozitul suplimentar pentru sectoarele de activitate specifice', 'Bifunctional'),
('641', 'Cheltuieli cu salariile personalului', 'Bifunctional'),
('642', 'Cheltuieli cu avantajele în natură și tichetele acordate salariaților', 'Bifunctional'),
('6421', 'Cheltuieli cu avantajele în natură acordate salariaților', 'Bifunctional'),
('6422', 'Cheltuieli cu tichetele acordate salariaților', 'Bifunctional'),
('643', 'Cheltuieli cu remunerarea în instrumente de capitaluri proprii', 'Bifunctional'),
('644', 'Cheltuieli cu primele reprezentând participarea personalului la profit', 'Bifunctional'),
('645', 'Cheltuieli privind asigurările și protecția socială', 'Bifunctional'),
('6451', 'Cheltuieli privind contribuția unității la asigurările sociale', 'Bifunctional'),
('6452', 'Cheltuieli privind contribuția unității pentru ajutorul de șomaj', 'Bifunctional'),
('6453', 'Cheltuieli privind contribuția angajatorului pentru asigurările sociale de sănătate', 'Bifunctional'),
('6455', 'Cheltuieli privind contribuția unității la asigurările de viață', 'Bifunctional'),
('6456', 'Cheltuieli privind contribuția unității la fondurile de pensii facultative', 'Bifunctional'),
('6457', 'Cheltuieli privind contribuția unității la primele de asigurare voluntară de sănătate', 'Bifunctional'),
('6458', 'Alte cheltuieli privind asigurările și protecția socială', 'Bifunctional'),
('646', 'Cheltuieli privind contribuția asiguratorie pentru muncă', 'Bifunctional'),
('6461', 'Cheltuieli privind contribuția asiguratorie pentru muncă corespunzătoare salariaților', 'Bifunctional'),
('6462', 'Cheltuieli privind contribuția asiguratorie pentru muncă corespunzătoare altor persoane, decât salariații', 'Bifunctional'),
('651', 'Cheltuieli din operațiuni de fiducie', 'Bifunctional'),
('6511', 'Cheltuieli ocazionate de constituirea fiduciei', 'Bifunctional'),
('6512', 'Cheltuieli din derularea operațiunilor de fiducie', 'Bifunctional'),
('6513', 'Cheltuieli din lichidarea operațiunilor de fiducie', 'Bifunctional'),
('652', 'Cheltuieli cu protecția mediului înconjurător', 'Bifunctional'),
('654', 'Pierderi din creanțe și debitori diverși', 'Bifunctional'),
('655', 'Cheltuieli din reevaluarea imobilizărilor corporale', 'Bifunctional'),
('658', 'Alte cheltuieli de exploatare', 'Bifunctional'),
('6581', 'Despăgubiri, amenzi și penalități', 'Bifunctional'),
('6582', 'Donații acordate', 'Bifunctional'),
('6583', 'Cheltuieli privind activele cedate și alte operațiuni de capital', 'Bifunctional'),
('6584', 'Cheltuieli cu sumele sau bunurile acordate ca sponsorizări', 'Bifunctional'),
('6586', 'Cheltuieli reprezentând transferuri și contribuții datorate în baza unor acte normative speciale', 'Bifunctional'),
('6587', 'Cheltuieli privind calamitățile și alte evenimente similare', 'Bifunctional'),
('6588', 'Alte cheltuieli de exploatare', 'Bifunctional'),
('663', 'Pierderi din creanțe legate de participații', 'Bifunctional'),
('664', 'Cheltuieli privind investițiile financiare cedate', 'Bifunctional'),
('6641', 'Cheltuieli privind imobilizările financiare cedate', 'Bifunctional'),
('6642', 'Pierderi din investițiile pe termen scurt cedate', 'Bifunctional'),
('665', 'Cheltuieli din diferențe de curs valutar', 'Bifunctional'),
('6651', 'Diferențe nefavorabile de curs valutar legate de elementele monetare exprimate în valută', 'Bifunctional'),
('6652', 'Diferențe nefavorabile de curs valutar din evaluarea elementelor monetare care fac parte din investiția netă într-o entitate străină', 'Bifunctional'),
('666', 'Cheltuieli privind dobânzile', 'Bifunctional'),
('667', 'Cheltuieli privind sconturile acordate', 'Bifunctional'),
('668', 'Alte cheltuieli financiare', 'Bifunctional'),
('681', 'Cheltuieli de exploatare privind amortizările, provizioanele și ajustările pentru depreciere', 'Bifunctional'),
('6811', 'Cheltuieli de exploatare privind amortizarea imobilizărilor', 'Bifunctional'),
('6812', 'Cheltuieli de exploatare privind provizioanele', 'Bifunctional'),
('6813', 'Cheltuieli de exploatare privind ajustările pentru deprecierea imobilizărilor', 'Bifunctional'),
('6814', 'Cheltuieli de exploatare privind ajustările pentru deprecierea activelor circulante', 'Bifunctional'),
('6817', 'Cheltuieli de exploatare privind ajustările pentru deprecierea fondului comercial', 'Bifunctional'),
('6818', 'Cheltuieli de exploatare privind ajustările pentru deprecierea creanțelor reprezentând avansuri acordate furnizorilor', 'Bifunctional'),
('686', 'Cheltuieli financiare privind amortizările, provizioanele și ajustările pentru pierdere de valoare', 'Bifunctional'),
('6861', 'Cheltuieli privind actualizarea provizioanelor', 'Bifunctional'),
('6863', 'Cheltuieli financiare privind ajustările pentru pierderea de valoare a imobilizărilor financiare', 'Bifunctional'),
('6864', 'Cheltuieli financiare privind ajustările pentru pierderea de valoare a activelor circulante', 'Bifunctional'),
('6865', 'Cheltuieli financiare privind amortizarea diferențelor aferente titlurilor de stat', 'Bifunctional'),
('6868', 'Cheltuieli financiare privind amortizarea primelor de rambursare a obligațiunilor și a altor datorii', 'Bifunctional'),
('691', 'Cheltuieli cu impozitul pe profit', 'Bifunctional'),
('694', 'Cheltuieli cu impozitul pe profit, respectiv impozitul pe profit la nivelul impozitului minim pe cifra de afaceri, rezultat din decontările în cadrul grupului fiscal în domeniul impozitului pe profit', 'Bifunctional'),
('695', 'Cheltuieli cu impozitul specific unor activități', 'Bifunctional'),
('697', 'Cheltuieli cu impozitul pe profit la nivelul impozitului minim pe cifra de afaceri', 'Bifunctional'),
('698', 'Cheltuieli cu impozitul pe venit și cu alte impozite care nu apar în elementele de mai sus', 'Bifunctional'),
('701', 'Venituri din vânzarea produselor finite, produselor agricole și a activelor biologice de natura stocurilor', 'Bifunctional'),
('7015', 'Venituri din vânzarea produselor finite', 'Bifunctional'),
('7017', 'Venituri din vânzarea produselor agricole', 'Bifunctional'),
('7018', 'Venituri din vânzarea activelor biologice de natura stocurilor', 'Bifunctional'),
('702', 'Venituri din vânzarea semifabricatelor', 'Bifunctional'),
('703', 'Venituri din vânzarea produselor reziduale', 'Bifunctional'),
('704', 'Venituri din servicii prestate', 'Bifunctional'),
('705', 'Venituri din studii și cercetări', 'Bifunctional'),
('706', 'Venituri din redevențe, locații de gestiune și chirii', 'Bifunctional'),
('707', 'Venituri din vânzarea mărfurilor', 'Bifunctional'),
('708', 'Venituri din activități diverse', 'Bifunctional'),
('709', 'Reduceri comerciale acordate', 'Bifunctional'),
('711', 'Venituri aferente costurilor stocurilor de produse', 'Bifunctional'),
('712', 'Venituri aferente costurilor serviciilor în curs de execuție', 'Bifunctional'),
('721', 'Venituri din producția de imobilizări necorporale', 'Bifunctional'),
('722', 'Venituri din producția de imobilizări corporale', 'Bifunctional'),
('725', 'Venituri din producția de investiții imobiliare', 'Bifunctional'),
('741', 'Venituri din subvenții de exploatare', 'Bifunctional'),
('7411', 'Venituri din subvenții de exploatare aferente cifrei de afaceri', 'Bifunctional'),
('7412', 'Venituri din subvenții de exploatare pentru materii prime și materiale', 'Bifunctional'),
('7413', 'Venituri din subvenții de exploatare pentru alte cheltuieli externe', 'Bifunctional'),
('7414', 'Venituri din subvenții de exploatare pentru plata personalului', 'Bifunctional'),
('7415', 'Venituri din subvenții de exploatare pentru asigurări și protecție socială', 'Bifunctional'),
('7416', 'Venituri din subvenții de exploatare pentru alte cheltuieli de exploatare', 'Bifunctional'),
('7417', 'Venituri din subvenții de exploatare în caz de calamități și alte evenimente similare', 'Bifunctional'),
('7418', 'Venituri din subvenții de exploatare pentru dobânda datorată', 'Bifunctional'),
('7419', 'Venituri din subvenții de exploatare aferente altor venituri', 'Bifunctional'),
('751', 'Venituri din operațiuni de fiducie', 'Bifunctional'),
('7511', 'Venituri ocazionate de constituirea fiduciei', 'Bifunctional'),
('7512', 'Venituri din derularea operațiunilor de fiducie', 'Bifunctional'),
('7513', 'Venituri din lichidarea operațiunilor de fiducie', 'Bifunctional'),
('754', 'Venituri din creanțe reactivate și debitori diverși', 'Bifunctional'),
('755', 'Venituri din reevaluarea imobilizărilor corporale', 'Bifunctional'),
('758', 'Alte venituri din exploatare', 'Bifunctional'),
('7581', 'Venituri din despăgubiri, amenzi și penalități', 'Bifunctional'),
('7582', 'Venituri din donații primite', 'Bifunctional'),
('7583', 'Venituri din vânzarea activelor și alte operațiuni de capital', 'Bifunctional'),
('7584', 'Venituri din subvenții pentru investiții', 'Bifunctional'),
('7586', 'Venituri reprezentând transferuri cuvenite în baza unor acte normative speciale', 'Bifunctional'),
('7588', 'Alte venituri din exploatare', 'Bifunctional'),
('761', 'Venituri din imobilizări financiare', 'Bifunctional'),
('7611', 'Venituri din acțiuni deținute la entitățile afiliate', 'Bifunctional'),
('7612', 'Venituri din acțiuni deținute la entități asociate', 'Bifunctional'),
('7613', 'Venituri din acțiuni deținute la entități controlate în comun', 'Bifunctional'),
('7615', 'Venituri din alte imobilizări financiare', 'Bifunctional'),
('762', 'Venituri din investiții financiare pe termen scurt', 'Bifunctional'),
('764', 'Venituri din investiții financiare cedate', 'Bifunctional'),
('7641', 'Venituri din imobilizări financiare cedate', 'Bifunctional'),
('7642', 'Câștiguri din investiții pe termen scurt cedate', 'Bifunctional'),
('765', 'Venituri din diferențe de curs valutar', 'Bifunctional'),
('7651', 'Diferențe favorabile de curs valutar legate de elementele monetare exprimate în valută', 'Bifunctional'),
('7652', 'Diferențe favorabile de curs valutar din evaluarea elementelor monetare care fac parte din investiția netă într-o entitate străină', 'Bifunctional'),
('766', 'Venituri din dobânzi', 'Bifunctional'),
('767', 'Venituri din sconturi obținute', 'Bifunctional'),
('768', 'Alte venituri financiare', 'Bifunctional'),
('781', 'Venituri din provizioane și ajustări pentru depreciere privind activitatea de exploatare', 'Bifunctional'),
('7812', 'Venituri din provizioane', 'Bifunctional'),
('7813', 'Venituri din ajustări pentru deprecierea imobilizărilor', 'Bifunctional'),
('7814', 'Venituri din ajustări pentru deprecierea activelor circulante', 'Bifunctional'),
('7815', 'Venituri din fondul comercial negativ', 'Bifunctional'),
('7818', 'Venituri din ajustări pentru deprecierea creanțelor reprezentând avansuri acordate furnizorilor', 'Bifunctional'),
('786', 'Venituri financiare din amortizări și ajustări pentru pierdere de valoare', 'Bifunctional'),
('7863', 'Venituri financiare din ajustări pentru pierderea de valoare a imobilizărilor financiare', 'Bifunctional'),
('7864', 'Venituri financiare din ajustări pentru pierderea de valoare a activelor circulante', 'Bifunctional'),
('7865', 'Venituri financiare din amortizarea diferențelor aferente titlurilor de stat', 'Bifunctional'),
('794', 'Venituri din impozitul pe profit, respectiv impozitul pe profit la nivelul impozitului minim pe cifra de afaceri, rezultat din decontările în cadrul grupului fiscal în domeniul impozitului pe profit', 'Bifunctional'),
('801', 'Angajamente acordate', 'Bifunctional'),
('8011', 'Giruri și garanții acordate', 'Bifunctional'),
('8018', 'Alte angajamente acordate', 'Bifunctional'),
('802', 'Angajamente primite', 'Bifunctional'),
('8021', 'Giruri și garanții primite', 'Bifunctional'),
('8028', 'Alte angajamente primite', 'Bifunctional'),
('803', 'Alte conturi în afara bilanțului', 'Bifunctional'),
('8031', 'Imobilizări corporale primite cu chirie sau în baza altor contracte similare', 'Bifunctional'),
('8032', 'Valori materiale primite spre prelucrare sau reparare', 'Bifunctional'),
('8033', 'Valori materiale primite în păstrare sau custodie', 'Bifunctional'),
('8034', 'Debitori scoși din activ, urmăriți în continuare', 'Bifunctional'),
('8035', 'Stocuri de natura obiectelor de inventar date în folosință', 'Bifunctional'),
('8036', 'Redevențe, locații de gestiune, chirii și alte datorii asimilate', 'Bifunctional'),
('8037', 'Efecte scontate neajunse la scadență', 'Bifunctional'),
('8038', 'Bunuri primite în administrare, concesiune, cu chirie și alte bunuri similare', 'Bifunctional'),
('8039', 'Alte valori în afara bilanțului', 'Bifunctional'),
('804', 'Certificate verzi', 'Bifunctional'),
('805', 'Dobânzi aferente contractelor de leasing și altor contracte asimilate, neajunse la scadență', 'Bifunctional'),
('8051', 'Dobânzi de plătit', 'Bifunctional'),
('8052', 'Dobânzi de încasat', 'Bifunctional'),
('806', 'Certificate de emisii de gaze cu efect de seră', 'Bifunctional'),
('807', 'Active contingente', 'Bifunctional'),
('808', 'Datorii contingente', 'Bifunctional'),
('809', 'Creanțe preluate prin cesionare', 'Bifunctional'),
('891', 'Bilanț de deschidere', 'Bifunctional'),
('892', 'Bilanț de închidere', 'Bifunctional'),
('901', 'Decontări interne privind cheltuielile', 'Bifunctional'),
('902', 'Decontări interne privind producția obținută', 'Bifunctional'),
('903', 'Decontări interne privind diferențele de preț', 'Bifunctional'),
('921', 'Cheltuielile activității de bază', 'Bifunctional'),
('922', 'Cheltuielile activităților auxiliare', 'Bifunctional'),
('923', 'Cheltuieli indirecte de producție', 'Bifunctional'),
('924', 'Cheltuieli generale de administrație', 'Bifunctional'),
('925', 'Cheltuieli de desfacere', 'Bifunctional'),
('931', 'Costul producției obținute', 'Bifunctional'),
('933', 'Costul producției în curs de execuție', 'Bifunctional');
-- [retest 08.10 pct.17] fără 731–738 (OMFP 3103/2017, entități fără scop patrimonial): nu sunt în planul unei societăți
-- comerciale (OMFP 1802/2014), iar D406 le respinge. Firmele existente: core/migrare_retest_0810.py (numai unde nu sunt folosite).


--
-- Name: produse; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

CREATE TABLE TENANT_PLACEHOLDER.produse (
    id integer NOT NULL,
    denumire text NOT NULL,
    um character varying(10) DEFAULT 'buc'::character varying NOT NULL,
    pret_unitar numeric(12,2) DEFAULT 0 NOT NULL,
    cota_tva numeric(5,2) DEFAULT 21 NOT NULL,
    categorie character varying(40),
    justificare text,
    sursa character varying(10) DEFAULT 'manual'::character varying NOT NULL,
    confirmat boolean DEFAULT false NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.produse OWNER TO iconta_user;

--
-- Name: produse_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

ALTER TABLE TENANT_PLACEHOLDER.produse ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.produse_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: retete; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.retete (
    id integer NOT NULL,
    denumire text NOT NULL,
    pret_fara_tva numeric(12,2) DEFAULT 0 NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.retete OWNER TO iconta_user;

--
-- Name: retete_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.retete ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.retete_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1
);


--
-- Name: retete_linii; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.retete_linii (
    id integer NOT NULL,
    reteta_id integer,
    articol_id integer,
    cantitate numeric(12,3) NOT NULL
);


ALTER TABLE TENANT_PLACEHOLDER.retete_linii OWNER TO iconta_user;

--
-- Name: retete_linii_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.retete_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.retete_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: rip_operatiuni; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.rip_operatiuni (
    id integer NOT NULL,
    data_operatiune date NOT NULL,
    tip character varying(10) NOT NULL,
    document_tip character varying(50),
    document_numar character varying(50),
    document_data date,
    explicatie text NOT NULL,
    suma numeric(14,2) NOT NULL,
    valuta character varying(3) DEFAULT 'RON'::character varying NOT NULL,
    suma_valuta numeric(14,2),
    curs_valutar numeric,
    metoda character varying(10) NOT NULL,
    banca_linie_id integer,
    casa_operatiune_id integer,
    categorie character varying(50) NOT NULL,
    deductibilitate character varying(15),
    status character varying(10) DEFAULT 'ciorna'::character varying NOT NULL,
    creat_de integer,
    validat_de integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT rip_operatiuni_metoda_check CHECK (((metoda)::text = ANY ((ARRAY['numerar'::character varying, 'banca'::character varying])::text[]))),
    CONSTRAINT rip_operatiuni_status_check CHECK (((status)::text = ANY ((ARRAY['ciorna'::character varying, 'validata'::character varying])::text[]))),
    CONSTRAINT rip_operatiuni_suma_check CHECK ((suma > (0)::numeric)),
    CONSTRAINT rip_operatiuni_tip_check CHECK (((tip)::text = ANY ((ARRAY['incasare'::character varying, 'plata'::character varying])::text[])))
);


ALTER TABLE TENANT_PLACEHOLDER.rip_operatiuni OWNER TO iconta_user;

--
-- Name: rip_operatiuni_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE SEQUENCE TENANT_PLACEHOLDER.rip_operatiuni_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE TENANT_PLACEHOLDER.rip_operatiuni_id_seq OWNER TO iconta_user;

--
-- Name: rip_operatiuni_id_seq; Type: SEQUENCE OWNED BY; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER SEQUENCE TENANT_PLACEHOLDER.rip_operatiuni_id_seq OWNED BY TENANT_PLACEHOLDER.rip_operatiuni.id;


--
-- Name: salariati; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.salariati (
    id integer NOT NULL,
    cnp text,
    nif text,
    nume text,
    prenume text,
    data_angajare date,
    data_asigurat date,
    part_time boolean DEFAULT false,
    ore_zi numeric DEFAULT 8,
    -- [punctul 4, 04.10.2026] salariu_brut retras: salariul contractual traieste numai in salariu_istoric
    persoane_intretinere integer DEFAULT 0,
    functie_baza boolean NOT NULL DEFAULT true,        -- [3c] CF art.77(1): deducerea personala se acorda NUMAI la locul unde e functia de baza
    data_nastere date,                                 -- [deducere suplimentara] tineri <26 (CF art.77 alin.10a)
    copii_scolarizati integer NOT NULL DEFAULT 0,      -- [deducere suplimentara] copii <=18 in invatamant (100 lei/copil)
    declaratie_copii boolean NOT NULL DEFAULT false,   -- [deducere suplimentara] declaratia parintelui (art.77 alin.12-13)
    judet_casa text,
    cor text,
    tip_asigurat text,
    scutit_contrib_minim boolean DEFAULT false,
    motiv_exceptare smallint,
    data_incetare date,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    de_verificat text[] DEFAULT '{}'::text[] NOT NULL,  -- [14.10.2026] câmpuri importate fără valoare, de confirmat (core/migrare_salariati_de_verificat.py)
    CONSTRAINT salariati_incetare_dupa_angajare CHECK (data_incetare IS NULL OR data_incetare >= data_angajare)
);


ALTER TABLE TENANT_PLACEHOLDER.salariati OWNER TO iconta_user;

--
-- Name: salariati_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.salariati ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.salariati_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: solduri_initiale; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.salariu_istoric (
    id integer NOT NULL,
    salariat_id integer NOT NULL,
    valabil_din date NOT NULL,
    salariu_brut numeric NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT salariu_istoric_pozitiv CHECK (salariu_brut >= 0)
);
ALTER TABLE TENANT_PLACEHOLDER.salariu_istoric OWNER TO iconta_user;
ALTER TABLE TENANT_PLACEHOLDER.salariu_istoric ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.salariu_istoric_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_salariu_istoric_sal_data
  ON TENANT_PLACEHOLDER.salariu_istoric (salariat_id, valabil_din);

CREATE TABLE TENANT_PLACEHOLDER.solduri_initiale (
    id integer NOT NULL,
    cont text NOT NULL,
    denumire text DEFAULT ''::text NOT NULL,
    sold_debitor numeric(15,2) DEFAULT 0 NOT NULL,
    sold_creditor numeric(15,2) DEFAULT 0 NOT NULL,
    data_referinta date
);


ALTER TABLE TENANT_PLACEHOLDER.solduri_initiale OWNER TO iconta_user;

--
-- Name: solduri_initiale_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.solduri_initiale ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.solduri_initiale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: solduri_parteneri; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.solduri_parteneri (
    id integer NOT NULL,
    cont text NOT NULL,
    cui text DEFAULT ''::text NOT NULL,
    denumire text DEFAULT ''::text NOT NULL,
    sold_debitor numeric(15,2) DEFAULT 0 NOT NULL,
    sold_creditor numeric(15,2) DEFAULT 0 NOT NULL,
    data_referinta date
);


ALTER TABLE TENANT_PLACEHOLDER.solduri_parteneri OWNER TO iconta_user;

--
-- Name: solduri_parteneri_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.solduri_parteneri ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.solduri_parteneri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: state_plata; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.state_plata (
    id integer NOT NULL,
    salariat_id integer NOT NULL,
    luna date NOT NULL,
    venit_brut numeric DEFAULT 0 NOT NULL,
    zile_lucrate integer DEFAULT 0 NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    exemplar integer DEFAULT 1 NOT NULL,
    amprenta text,
    date jsonb,
    emis_de text,
    emis_la timestamp with time zone DEFAULT now() NOT NULL,
    corectie_la integer,
    motiv text,
    motiv_de text,
    motiv_la timestamp with time zone
);


ALTER TABLE TENANT_PLACEHOLDER.state_plata OWNER TO iconta_user;

--
-- Name: state_plata_id_seq; Type: SEQUENCE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE TENANT_PLACEHOLDER.state_plata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME TENANT_PLACEHOLDER.state_plata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ai_corectii id; Type: DEFAULT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.ai_corectii ALTER COLUMN id SET DEFAULT nextval('TENANT_PLACEHOLDER.ai_corectii_id_seq'::regclass);


--
-- Name: facturi_recurente id; Type: DEFAULT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.facturi_recurente ALTER COLUMN id SET DEFAULT nextval('TENANT_PLACEHOLDER.facturi_recurente_id_seq'::regclass);


--
-- Name: rip_operatiuni id; Type: DEFAULT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.rip_operatiuni ALTER COLUMN id SET DEFAULT nextval('TENANT_PLACEHOLDER.rip_operatiuni_id_seq'::regclass);


--
-- Name: ai_corectii ai_corectii_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.ai_corectii
    ADD CONSTRAINT ai_corectii_pkey PRIMARY KEY (id);


--
-- Name: articole articole_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.articole
    ADD CONSTRAINT articole_pkey PRIMARY KEY (id);


--
-- Name: asociati asociati_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.asociati
    ADD CONSTRAINT asociati_pkey PRIMARY KEY (id);


--
-- Name: bonuri bonuri_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.bonuri
    ADD CONSTRAINT bonuri_pkey PRIMARY KEY (id);


--
-- Name: casa_operatiuni casa_operatiuni_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.casa_operatiuni
    ADD CONSTRAINT casa_operatiuni_pkey PRIMARY KEY (id);


--
-- Name: clienti clienti_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.clienti
    ADD CONSTRAINT clienti_pkey PRIMARY KEY (id);


--
-- Name: concedii_medicale concedii_medicale_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.concedii_medicale
    ADD CONSTRAINT concedii_medicale_pkey PRIMARY KEY (id);


--
-- Name: extras_linii extras_linii_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.extras_linii
    ADD CONSTRAINT extras_linii_pkey PRIMARY KEY (id);


--
-- Name: factura_linii factura_linii_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.factura_linii
    ADD CONSTRAINT factura_linii_pkey PRIMARY KEY (id);


--
-- Name: facturi facturi_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.facturi
    ADD CONSTRAINT facturi_pkey PRIMARY KEY (id);

--
-- [C1, 17.09.2026] numerotare secventiala UNICA pe emise (art. 319 CF): plasa a doua
-- peste rezervarea atomica din facturi_api._rezerva_numar. Partial pe emise; primite pot
-- repeta numarul furnizorului. Oglinda in core/migrare_unic_numar_factura.py.
--
CREATE UNIQUE INDEX IF NOT EXISTS facturi_numar_emisa_uniq ON TENANT_PLACEHOLDER.facturi (COALESCE(serie, ''), numar) WHERE directie = 'emisa';


--
-- Name: facturi_recurente facturi_recurente_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.facturi_recurente
    ADD CONSTRAINT facturi_recurente_pkey PRIMARY KEY (id);


--
-- Name: firma_profil firma_profil_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.firma_profil
    ADD CONSTRAINT firma_profil_pkey PRIMARY KEY (id);


--
-- Name: furnizori furnizori_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.furnizori
    ADD CONSTRAINT furnizori_pkey PRIMARY KEY (id);


--
-- Name: inregistrari_linii inregistrari_linii_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.inregistrari_linii
    ADD CONSTRAINT inregistrari_linii_pkey PRIMARY KEY (id);


--
-- Name: inregistrari inregistrari_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.inregistrari
    ADD CONSTRAINT inregistrari_pkey PRIMARY KEY (id);


--
-- Name: mijloace_fixe mijloace_fixe_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.mijloace_fixe
    ADD CONSTRAINT mijloace_fixe_pkey PRIMARY KEY (id);


--
-- Name: miscari_stoc miscari_stoc_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.miscari_stoc
    ADD CONSTRAINT miscari_stoc_pkey PRIMARY KEY (id);


--
-- Name: nir_linii nir_linii_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.nir_linii
    ADD CONSTRAINT nir_linii_pkey PRIMARY KEY (id);


--
-- Name: nir nir_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.nir
    ADD CONSTRAINT nir_pkey PRIMARY KEY (id);


--
-- Name: perioade_blocate perioade_blocate_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.perioade_blocate
    ADD CONSTRAINT perioade_blocate_pkey PRIMARY KEY (an, luna);


--
-- Name: plan_conturi plan_conturi_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.plan_conturi
    ADD CONSTRAINT plan_conturi_pkey PRIMARY KEY (simbol);


--
-- Name: produse produse_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.produse
    ADD CONSTRAINT produse_pkey PRIMARY KEY (id);


--
-- Name: retete_linii retete_linii_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.retete_linii
    ADD CONSTRAINT retete_linii_pkey PRIMARY KEY (id);


--
-- Name: retete retete_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.retete
    ADD CONSTRAINT retete_pkey PRIMARY KEY (id);


--
-- Name: rip_operatiuni rip_operatiuni_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.rip_operatiuni
    ADD CONSTRAINT rip_operatiuni_pkey PRIMARY KEY (id);


--
-- Name: salariati salariati_cnp_uniq; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.salariati
    ADD CONSTRAINT salariati_cnp_uniq UNIQUE (cnp);


--
-- Name: salariati salariati_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.salariati
    ADD CONSTRAINT salariati_pkey PRIMARY KEY (id);


--
-- Name: solduri_initiale solduri_initiale_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.solduri_initiale
    ADD CONSTRAINT solduri_initiale_pkey PRIMARY KEY (id);


--
-- Name: solduri_parteneri solduri_parteneri_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.solduri_parteneri
    ADD CONSTRAINT solduri_parteneri_pkey PRIMARY KEY (id);


--
-- Name: state_plata state_plata_pkey; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.state_plata
    ADD CONSTRAINT state_plata_pkey PRIMARY KEY (id);


--
-- Name: state_plata uq_state_plata_sal_luna_ex; Type: INDEX; Schema: TENANT_PLACEHOLDER; Owner: postgres
-- [stat_emis 21.08.2026] Vechea UNIQUE (salariat_id, luna) interzicea STRUCTURAL al doilea exemplar:
-- schema codifica statul ca VEDERE (un rand per om per luna), nu ca DOCUMENT. Corectia unui fluturas
-- dat unui om e un act nou care il refera pe primul, deci cheia cuprinde si numarul exemplarului.
--

CREATE UNIQUE INDEX IF NOT EXISTS uq_state_plata_sal_luna_ex
    ON TENANT_PLACEHOLDER.state_plata (salariat_id, luna, exemplar);


--
-- Name: ai_corectii_ctx; Type: INDEX; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE INDEX ai_corectii_ctx ON TENANT_PLACEHOLDER.ai_corectii USING btree (context);


--
-- Name: idx_rip_data; Type: INDEX; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE INDEX idx_rip_data ON TENANT_PLACEHOLDER.rip_operatiuni USING btree (data_operatiune);


--
-- Name: idx_rip_status; Type: INDEX; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE INDEX idx_rip_status ON TENANT_PLACEHOLDER.rip_operatiuni USING btree (status);


--
-- Name: produse_denumire_idx; Type: INDEX; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

CREATE INDEX produse_denumire_idx ON TENANT_PLACEHOLDER.produse USING btree (lower(denumire));


--
-- Name: articole_barcode_uq; Type: INDEX; Schema: TENANT_PLACEHOLDER; Owner: iconta_user
--

CREATE UNIQUE INDEX articole_barcode_uq ON TENANT_PLACEHOLDER.articole USING btree (barcode) WHERE (barcode IS NOT NULL);


--
-- Name: concedii_medicale concedii_medicale_salariat_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.concedii_medicale
    ADD CONSTRAINT concedii_medicale_salariat_id_fkey FOREIGN KEY (salariat_id) REFERENCES TENANT_PLACEHOLDER.salariati(id) ON DELETE CASCADE;


--
-- Name: factura_linii factura_linii_factura_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.factura_linii
    ADD CONSTRAINT factura_linii_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES TENANT_PLACEHOLDER.facturi(id) ON DELETE CASCADE;


--
-- Name: facturi facturi_client_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.facturi
    ADD CONSTRAINT facturi_client_id_fkey FOREIGN KEY (client_id) REFERENCES TENANT_PLACEHOLDER.clienti(id);


--
-- Name: inregistrari inregistrari_factura_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.inregistrari
    ADD CONSTRAINT inregistrari_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES TENANT_PLACEHOLDER.facturi(id);


--
-- Name: inregistrari_linii inregistrari_linii_inregistrare_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.inregistrari_linii
    ADD CONSTRAINT inregistrari_linii_inregistrare_id_fkey FOREIGN KEY (inregistrare_id) REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE CASCADE;


--
-- Name: miscari_stoc miscari_stoc_articol_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.miscari_stoc
    ADD CONSTRAINT miscari_stoc_articol_id_fkey FOREIGN KEY (articol_id) REFERENCES TENANT_PLACEHOLDER.articole(id);


--
-- Name: nir_linii nir_linii_nir_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.nir_linii
    ADD CONSTRAINT nir_linii_nir_id_fkey FOREIGN KEY (nir_id) REFERENCES TENANT_PLACEHOLDER.nir(id) ON DELETE CASCADE;


--
-- Name: retete_linii retete_linii_articol_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.retete_linii
    ADD CONSTRAINT retete_linii_articol_id_fkey FOREIGN KEY (articol_id) REFERENCES TENANT_PLACEHOLDER.articole(id);


--
-- Name: retete_linii retete_linii_reteta_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.retete_linii
    ADD CONSTRAINT retete_linii_reteta_id_fkey FOREIGN KEY (reteta_id) REFERENCES TENANT_PLACEHOLDER.retete(id) ON DELETE CASCADE;


--
-- Name: rip_operatiuni rip_operatiuni_banca_linie_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.rip_operatiuni
    ADD CONSTRAINT rip_operatiuni_banca_linie_id_fkey FOREIGN KEY (banca_linie_id) REFERENCES TENANT_PLACEHOLDER.extras_linii(id);


--
-- Name: rip_operatiuni rip_operatiuni_casa_operatiune_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.rip_operatiuni
    ADD CONSTRAINT rip_operatiuni_casa_operatiune_id_fkey FOREIGN KEY (casa_operatiune_id) REFERENCES TENANT_PLACEHOLDER.casa_operatiuni(id);


--
-- Name: state_plata state_plata_salariat_id_fkey; Type: FK CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.state_plata
    ADD CONSTRAINT state_plata_salariat_id_fkey FOREIGN KEY (salariat_id) REFERENCES TENANT_PLACEHOLDER.salariati(id) ON DELETE CASCADE;


--
-- Name: SCHEMA TENANT_PLACEHOLDER; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA TENANT_PLACEHOLDER TO iconta_user;


--
-- Name: TABLE ai_corectii; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.ai_corectii TO iconta_user;


--
-- Name: SEQUENCE ai_corectii_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE TENANT_PLACEHOLDER.ai_corectii_id_seq TO iconta_user;


--
-- Name: TABLE articole; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.articole TO iconta_user;


--
-- Name: SEQUENCE articole_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.articole_id_seq TO iconta_user;


--
-- Name: TABLE asociati; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.asociati TO iconta_user;


--
-- Name: SEQUENCE asociati_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.asociati_id_seq TO iconta_user;


--
-- Name: TABLE casa_operatiuni; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.casa_operatiuni TO iconta_user;


--
-- Name: SEQUENCE casa_operatiuni_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.casa_operatiuni_id_seq TO iconta_user;


--
-- Name: TABLE clienti; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.clienti TO iconta_user;


--
-- Name: SEQUENCE clienti_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.clienti_id_seq TO iconta_user;


--
-- Name: TABLE concedii_medicale; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.concedii_medicale TO iconta_user;


--
-- Name: SEQUENCE concedii_medicale_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.concedii_medicale_id_seq TO iconta_user;


--
-- Name: TABLE extras_linii; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.extras_linii TO iconta_user;


--
-- Name: SEQUENCE extras_linii_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.extras_linii_id_seq TO iconta_user;


--
-- Name: TABLE factura_linii; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.factura_linii TO iconta_user;


--
-- Name: SEQUENCE factura_linii_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.factura_linii_id_seq TO iconta_user;


--
-- Name: TABLE facturi; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.facturi TO iconta_user;


--
-- Name: SEQUENCE facturi_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.facturi_id_seq TO iconta_user;


--
-- Name: TABLE facturi_recurente; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.facturi_recurente TO iconta_user;


--
-- Name: SEQUENCE facturi_recurente_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE TENANT_PLACEHOLDER.facturi_recurente_id_seq TO iconta_user;


--
-- Name: TABLE firma_profil; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.firma_profil TO iconta_user;


--
-- Name: TABLE furnizori; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.furnizori TO iconta_user;


--
-- Name: SEQUENCE furnizori_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.furnizori_id_seq TO iconta_user;


--
-- Name: TABLE inregistrari; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.inregistrari TO iconta_user;


--
-- Name: SEQUENCE inregistrari_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.inregistrari_id_seq TO iconta_user;


--
-- Name: TABLE inregistrari_linii; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.inregistrari_linii TO iconta_user;


--
-- Name: SEQUENCE inregistrari_linii_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.inregistrari_linii_id_seq TO iconta_user;


--
-- Name: TABLE mijloace_fixe; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.mijloace_fixe TO iconta_user;


--
-- Name: SEQUENCE mijloace_fixe_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.mijloace_fixe_id_seq TO iconta_user;


--
-- Name: TABLE miscari_stoc; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.miscari_stoc TO iconta_user;


--
-- Name: SEQUENCE miscari_stoc_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.miscari_stoc_id_seq TO iconta_user;


--
-- Name: TABLE nir; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.nir TO iconta_user;


--
-- Name: SEQUENCE nir_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.nir_id_seq TO iconta_user;


--
-- Name: TABLE nir_linii; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.nir_linii TO iconta_user;


--
-- Name: SEQUENCE nir_linii_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.nir_linii_id_seq TO iconta_user;


--
-- Name: TABLE perioade_blocate; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.perioade_blocate TO iconta_user;


--
-- Name: TABLE plan_conturi; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.plan_conturi TO iconta_user;


--
-- Name: TABLE retete; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.retete TO iconta_user;


--
-- Name: SEQUENCE retete_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.retete_id_seq TO iconta_user;


--
-- Name: TABLE retete_linii; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.retete_linii TO iconta_user;


--
-- Name: SEQUENCE retete_linii_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.retete_linii_id_seq TO iconta_user;


--
-- Name: TABLE rip_operatiuni; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.rip_operatiuni TO iconta_user;


--
-- Name: SEQUENCE rip_operatiuni_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE TENANT_PLACEHOLDER.rip_operatiuni_id_seq TO iconta_user;


--
-- Name: TABLE salariati; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.salariati TO iconta_user;


--
-- Name: SEQUENCE salariati_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.salariati_id_seq TO iconta_user;


--
-- Name: TABLE solduri_initiale; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.solduri_initiale TO iconta_user;


--
-- Name: SEQUENCE solduri_initiale_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.solduri_initiale_id_seq TO iconta_user;


--
-- Name: TABLE solduri_parteneri; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON TABLE TENANT_PLACEHOLDER.solduri_parteneri TO iconta_user;


--
-- Name: SEQUENCE solduri_parteneri_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT ALL ON SEQUENCE TENANT_PLACEHOLDER.solduri_parteneri_id_seq TO iconta_user;


--
-- Name: TABLE state_plata; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE TENANT_PLACEHOLDER.state_plata TO iconta_user;


--
-- Name: SEQUENCE state_plata_id_seq; Type: ACL; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

GRANT USAGE ON SEQUENCE TENANT_PLACEHOLDER.state_plata_id_seq TO iconta_user;


--
-- PostgreSQL database dump complete
--



-- generalizare_zi_v1

-- chitante_emise_v1
CREATE TABLE TENANT_PLACEHOLDER.chitante (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    serie character varying(10) NOT NULL,
    numar integer NOT NULL,
    data date NOT NULL,
    factura_id integer,
    client_nume text,
    client_cui character varying(30),
    suma numeric(12,2) NOT NULL,
    reprezentand text,
    casa_operatiune_id integer,
    inregistrare_id integer,
    anulata boolean DEFAULT false NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE TENANT_PLACEHOLDER.chitante OWNER TO iconta_user;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS serie_chitanta character varying(10) DEFAULT 'CH';
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS numerotare_configurata boolean NOT NULL DEFAULT false;

-- bon_flux_e9_v1
ALTER TABLE TENANT_PLACEHOLDER.bonuri ADD COLUMN IF NOT EXISTS orientare smallint NOT NULL DEFAULT 0;

-- perioada_blocata_trigger_v1 (#66): blocheaza INSERT/UPDATE/DELETE pe luna inchisa — funcția și triggerul pe `inregistrari`
-- se definesc acum în blocul reguli_fond_v1 (sfârșitul fișierului), cu golul UPDATE închis (data veche). O singură definiție.

-- perioada_blocata_rip_trigger_v1 (#67): blocheaza INSERT/UPDATE/DELETE pe rip_operatiuni pt luna inchisa

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_rip() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  IF TG_OP = 'DELETE' THEN d := OLD.data_operatiune; ELSE d := NEW.data_operatiune; END IF;
  IF EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
             WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
    RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
      LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_verifica_perioada_blocata_rip ON TENANT_PLACEHOLDER.rip_operatiuni;
CREATE TRIGGER trg_verifica_perioada_blocata_rip
BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.rip_operatiuni
FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_rip();

-- [validare_note 06.10.2026] autorul notei din cerere + sincronizarea cu coada de validare — sursa unica: core/migrare_validare_note.py
ALTER TABLE TENANT_PLACEHOLDER.inregistrari ADD COLUMN IF NOT EXISTS creat_de_id integer
  DEFAULT NULLIF(current_setting('iconta.utilizator', true), '')::integer;
CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.coada_nota_sincron() RETURNS trigger AS $$
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
DROP TRIGGER IF EXISTS trg_coada_nota_sincron ON TENANT_PLACEHOLDER.inregistrari;
CREATE TRIGGER trg_coada_nota_sincron AFTER UPDATE OF status OR DELETE ON TENANT_PLACEHOLDER.inregistrari
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.coada_nota_sincron();

--
-- F131 comp.5 (notificari scadenta) — mirror al core/migrare_notificari_scadenta.py (DDL idempotent)
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.notificari_scadenta (
    factura_id integer NOT NULL,
    prag integer NOT NULL,
    trimis_la timestamptz NOT NULL DEFAULT now(),
    stare text NOT NULL DEFAULT 'trimis',
    CONSTRAINT notificari_scadenta_pkey PRIMARY KEY (factura_id, prag)
);
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS notificari_scadenta_activ boolean NOT NULL DEFAULT false;
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS notificare_stop boolean NOT NULL DEFAULT false;
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS notificare_amanata_pana date;

-- [tip_firma_v1] mirror al 01_ddl_tip_firma.sql: firmele NOI trebuie sa aiba coloana,
-- altfel INSERT-ul din provision_tenant (tip_firma) crapa. srl=partida dubla / pfa=partida simpla.
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS tip_firma character varying(4) NOT NULL DEFAULT 'srl';
ALTER TABLE TENANT_PLACEHOLDER.firma_profil DROP CONSTRAINT IF EXISTS tip_firma_valid;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD CONSTRAINT tip_firma_valid CHECK (tip_firma IN ('srl', 'pfa'));

-- [lot 19 d12] mirror al core/migrare_capital_social.py: Legea 31/1990 art.74 alin.(3) — capitalul social pe factura
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS forma_juridica character varying(4);
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS capital_subscris numeric(18,2);
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS capital_varsat numeric(18,2);
ALTER TABLE TENANT_PLACEHOLDER.firma_profil DROP CONSTRAINT IF EXISTS forma_juridica_valida;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD CONSTRAINT forma_juridica_valida CHECK (forma_juridica IS NULL OR forma_juridica IN ('SRL', 'SA', 'SCA', 'SNC', 'SCS', 'ALTA'));

-- [D394 Î2] mirror al core/migrare_d394_i2.py: activitatea exceptată de la AMEF (OUG 28/1999 art.2) + cota pe chitanță
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS activitate_exceptata_amef boolean NOT NULL DEFAULT false;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS activitate_amef character varying(2);
ALTER TABLE TENANT_PLACEHOLDER.chitante ADD COLUMN IF NOT EXISTS cota_tva numeric(5,2);

-- [F143 centre_cost, Faza 1] mirror al 02_ddl_centre_cost.sql: firmele NOI trebuie sa aiba
-- tabelul + coloana. Dimensiune management accounting intern (centru de cost pe linia de nota).
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.centre_cost (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nume varchar(100) NOT NULL,
    activ boolean NOT NULL DEFAULT true,
    creat_la timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE TENANT_PLACEHOLDER.inregistrari_linii ADD COLUMN IF NOT EXISTS centru_cost_id integer;
ALTER TABLE TENANT_PLACEHOLDER.inregistrari_linii DROP CONSTRAINT IF EXISTS inregistrari_linii_centru_cost_fk;
ALTER TABLE TENANT_PLACEHOLDER.inregistrari_linii ADD CONSTRAINT inregistrari_linii_centru_cost_fk
    FOREIGN KEY (centru_cost_id) REFERENCES TENANT_PLACEHOLDER.centre_cost(id);

-- [F143 bugete, Faza 2] mirror al 03_ddl_bugete.sql: buget anual per centru, per clasa
-- (cheltuieli + venituri). UNIQUE(centru, an) = un rand de buget per centru pe an.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.bugete (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    centru_cost_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.centre_cost(id),
    an integer NOT NULL,
    buget_cheltuieli numeric(14,2) NOT NULL DEFAULT 0,
    buget_venituri numeric(14,2) NOT NULL DEFAULT 0,
    CONSTRAINT bugete_centru_an_unic UNIQUE (centru_cost_id, an)
);

-- [F133 tichete masa, Faza 1] mirror al 04_ddl_tichet_masa.sql: valoarea nominala a unui
-- tichet de masa per salariat (0 = nu primeste). Plafonul legal traieste in common.COTE.
ALTER TABLE TENANT_PLACEHOLDER.salariati ADD COLUMN IF NOT EXISTS tichet_masa_valoare numeric NOT NULL DEFAULT 0;

-- [F134 plata pe card] mirror al 07_ddl_iban_salariat.sql: IBAN-ul salariatului (cont beneficiar)
-- pentru fisierul de plata SEPA pain.001. Optional (doar cei platiti pe card). Validat in salariati_api.
ALTER TABLE TENANT_PLACEHOLDER.salariati ADD COLUMN IF NOT EXISTS iban varchar(34);

-- [deficiența 412, 19.10.2026] mirror al core/migrare_cim_salariat.py: contractul individual de muncă pe fișa salariatului —
-- durata (Legea 53/2003 art.12: nedeterminată / determinată), numărul și data CIM (art.16 alin.(1)); adeverința le precompletează.
ALTER TABLE TENANT_PLACEHOLDER.salariati ADD COLUMN IF NOT EXISTS tip_contract text CONSTRAINT salariati_tip_contract_valid CHECK (tip_contract IS NULL OR tip_contract IN ('nedeterminata', 'determinata'));
ALTER TABLE TENANT_PLACEHOLDER.salariati ADD COLUMN IF NOT EXISTS nr_cim text;
ALTER TABLE TENANT_PLACEHOLDER.salariati ADD COLUMN IF NOT EXISTS data_cim date;

-- [F133 beneficii one-off, Faza 2a] mirror al 05_ddl_beneficii_lunare.sql: tichete de vacanta
-- (si cadou la 2b) = sume one-off per salariat/an/luna/tip (nu config permanent ca masa).
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.beneficii_lunare (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    salariat_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.salariati(id),
    an integer NOT NULL,
    luna integer NOT NULL,
    tip varchar(20) NOT NULL,
    valoare numeric(14,2) NOT NULL DEFAULT 0,
    eveniment varchar(20) NOT NULL DEFAULT '',  -- [F133 Faza 2b1] cadou: paste/craciun/8martie/1iunie/altul
    CONSTRAINT beneficii_lunare_tip_ck CHECK (tip IN ('vacanta', 'cadou', 'cultural', 'cresa')),
    CONSTRAINT beneficii_lunare_eveniment_ck CHECK (eveniment IN ('', 'paste', 'craciun', '8martie', '1iunie', 'altul', 'ocazional')),
    CONSTRAINT beneficii_lunare_luna_ck CHECK (luna BETWEEN 1 AND 12),
    CONSTRAINT beneficii_lunare_val_ck CHECK (valoare >= 0),
    CONSTRAINT beneficii_lunare_unic_v2 UNIQUE (salariat_id, an, luna, tip, eveniment)
);

-- [F125] mirror al 09_ddl_d390_clasificare.sql: clasificarea manuala D390 (reclasificare + adaugare).
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.d390_reclasificare (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    an integer NOT NULL, luna integer NOT NULL,
    directie text NOT NULL, tara varchar(2) NOT NULL, cod varchar(20) NOT NULL,
    tip char(1) NOT NULL,
    UNIQUE (an, luna, directie, tara, cod)
);
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.d390_manual (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    an integer NOT NULL, luna integer NOT NULL,
    tip char(1) NOT NULL, tara varchar(2) NOT NULL,
    cod varchar(20) NOT NULL DEFAULT '', den text NOT NULL DEFAULT '', baza numeric NOT NULL DEFAULT 0
);

--
-- [d301_canonic 23.07] Decont special TVA neplatitori (D301) — mutat din CREATE lazy (d301.py:ensure_tabel,
-- ELIMINAT) in template = o singura sursa de adevar (aliniat cu decizia 22.07 anti-lazy). id SERIAL (nu IDENTITY)
-- ca sa coincida cu tabelele deja create lazy pe tenantii existenti (tenant_001/002) -> zero drift F165.
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.d301_operatiuni (
    id SERIAL PRIMARY KEY, an integer, luna integer, tip integer DEFAULT 1,
    nr_doc text, data_doc text, val_valuta numeric DEFAULT 0,
    tip_valuta text DEFAULT 'EUR', curs numeric, tva numeric DEFAULT 0,
    partener_tara varchar(2) DEFAULT '', partener_cod varchar(20) DEFAULT '', partener_den text DEFAULT '',
    temei_307 text,   -- art. 307 alin. (3)/(5)/(6) per operatiune tip 4; NULL=neconfirmat (mirror core/migrare_d301_temei_307.py)
    creat timestamp DEFAULT now()
);

--
-- [B2/B3 D300] Randuri manuale D300 (Decont TVA) - mirror al core/migrare_d300_manual.py.
-- Randurile pe care generatorul (core/d300.py) NU le deriva din facturi (scutiri R14/R15,
-- regularizari R16/R30, ajustari R29/R43/R44, cote istorice) se introduc de contabil si PERSISTA
-- aici; d300.genereaza le re-citeste pe calea de depunere (paritate preview<->depunere).
-- UNITATE: LEI intregi (bigint), aliniat cu d300.py. baza=col.1, tva=col.2 (0 la randurile
-- fara col.2). id SERIAL (ca d301_operatiuni) - zero drift.
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.d300_manual (
    id SERIAL PRIMARY KEY, an integer NOT NULL, luna integer NOT NULL,
    rand text NOT NULL, baza bigint NOT NULL DEFAULT 0, tva bigint NOT NULL DEFAULT 0,
    descriere text, creat timestamp DEFAULT now(),
    UNIQUE (an, luna, rand)
);

--
-- F145 (rapoarte configurabile salvabile) — mirror al core/migrare_rapoarte_salvate.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.rapoarte_salvate (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tip_raport text NOT NULL CHECK (tip_raport IN ('comercial')),
    nume text NOT NULL,
    filtru jsonb NOT NULL DEFAULT '{}'::jsonb,
    creat_de integer,
    creat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT rapoarte_salvate_tip_nume_unic UNIQUE (tip_raport, nume)
);

--
-- R45 (un artefact produs se pastreaza) — mirror al core/migrare_artefacte.py
-- Cele cinci campuri decise 25.08.2026: continut, moment, autor, amprenta, exemplar;
-- plus verdictul, la felurile care se valideaza. UNIQUE include `exemplar`: al doilea
-- exemplar TREBUIE sa poata exista (P4), doar numarul lui nu se poate repeta.
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.artefacte_produse (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fel text NOT NULL,
    cheie text NOT NULL,
    exemplar integer NOT NULL,
    continut text,
    amprenta text NOT NULL,
    produs_la timestamptz NOT NULL DEFAULT now(),
    produs_de_id integer,
    produs_de text,
    verdict text,
    verdict_la timestamptz,
    verdict_versiune text,
    verdict_amprenta text,
    CONSTRAINT artefacte_exemplar_unic UNIQUE (fel, cheie, exemplar)
);
CREATE INDEX IF NOT EXISTS artefacte_fel_cheie ON TENANT_PLACEHOLDER.artefacte_produse (fel, cheie);

-- [R58, 26.08.2026] Urma inchiderii/redeschiderii unei perioade. Sursa DDL: core/migrare_inchideri.py
-- (idempotent, aplicat pe tenantii existenti cu `python3 -m core.migrare_inchideri`).
-- P15 + interdictia 36: redeschiderea e ACT CONSEMNAT, CU MOTIV. Constrangerea de motiv sta in
-- BAZA, nu doar in ruta -- o urma care se poate scrie fara motiv de pe alta cale n-ar fi o urma.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.perioade_inchideri (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    an integer NOT NULL,
    luna integer NOT NULL,
    actiune text NOT NULL,
    motiv text,
    cine_id integer,
    cand timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT perioade_inchideri_actiune CHECK (actiune IN ('inchisa', 'redeschisa')),
    CONSTRAINT perioade_inchideri_motiv_la_redeschidere
        CHECK (actiune <> 'redeschisa' OR btrim(coalesce(motiv, '')) <> '')
);
CREATE INDEX IF NOT EXISTS perioade_inchideri_perioada
    ON TENANT_PLACEHOLDER.perioade_inchideri (an, luna, cand);

--
-- F146 (registratura documente) — mirror al core/migrare_registratura.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.registratura (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    directie text NOT NULL CHECK (directie IN ('intrare','iesire')),
    numar integer NOT NULL,
    an integer NOT NULL,
    data date NOT NULL,
    descriere text NOT NULL,
    partener text,
    document_ref text,
    creat_de integer,
    creat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registratura_an_numar_unic UNIQUE (an, numar)
);

--
-- F147 (generare contracte din sabloane) — mirror al core/migrare_contracte_sabloane.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.contracte_sabloane (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nume text NOT NULL,
    continut text NOT NULL,
    creat_de integer,
    creat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT contracte_sabloane_nume_unic UNIQUE (nume)
);

--
-- F172 (punte factura->stoc) — mirror al core/migrare_punte_stoc.py
--
ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD COLUMN IF NOT EXISTS articol_id integer;
ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc  ADD COLUMN IF NOT EXISTS factura_id integer;
DO $mig$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='factura_linii_articol_fk'
                   AND connamespace='TENANT_PLACEHOLDER'::regnamespace) THEN
        ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD CONSTRAINT factura_linii_articol_fk
            FOREIGN KEY (articol_id) REFERENCES TENANT_PLACEHOLDER.articole(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='miscari_stoc_factura_fk'
                   AND connamespace='TENANT_PLACEHOLDER'::regnamespace) THEN
        ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ADD CONSTRAINT miscari_stoc_factura_fk
            FOREIGN KEY (factura_id) REFERENCES TENANT_PLACEHOLDER.facturi(id) ON DELETE SET NULL;
    END IF;
END $mig$;

--
-- F135 (pontaj informativ) — mirror al core/migrare_pontaj.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.pontaj (
    salariat_id integer NOT NULL,
    zi date NOT NULL,
    stare text NOT NULL,
    nota text,
    CONSTRAINT pontaj_pkey PRIMARY KEY (salariat_id, zi)
);

-- [cap.23 DS] Perioada confirmata: starea CONFIRMAT/NECONFIRMAT per (an,luna,domeniu) conditioneaza calculele din aval
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.perioada_confirmata (
    an integer NOT NULL,
    luna integer NOT NULL,
    domeniu varchar(20) NOT NULL,
    confirmat_de integer,
    confirmat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT perioada_confirmata_pkey PRIMARY KEY (an, luna, domeniu),
    CONSTRAINT perioada_confirmata_luna_ck CHECK (luna BETWEEN 1 AND 12)
);

--
-- e-Factura trimiteri (F126/F160, pasul 2) — mirror al core/migrare_efactura_trimiteri.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.efactura_trimiteri (
  id                BIGSERIAL PRIMARY KEY,
  factura_id        BIGINT NOT NULL REFERENCES TENANT_PLACEHOLDER.facturi(id),
  mediu             TEXT NOT NULL CHECK (mediu IN ('test','prod')),
  stare             TEXT NOT NULL DEFAULT 'pregatit'
                    CHECK (stare IN ('pregatit','eroare_upload','incarcat','in_prelucrare','ok','nok','investigatie')),
  index_incarcare   TEXT,
  execution_status  INTEGER,
  id_descarcare     TEXT,
  error_message     TEXT,
  xml_trimis        TEXT,
  xml_sha256        TEXT NOT NULL,
  zip_raspuns_path  TEXT,
  xml_semnat_sha256 TEXT,
  trimis_la         TIMESTAMPTZ,
  finalizat_la      TIMESTAMPTZ,
  creat_la          TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizat_la     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_efactura_trimiteri_viu
  ON TENANT_PLACEHOLDER.efactura_trimiteri (factura_id)
  WHERE mediu='prod' AND stare IN ('incarcat','in_prelucrare','ok');

--
-- e-Factura: adresa structurata cumparator (BT-52/BT-54) — mirror al core/migrare_efactura_adresa.py
--
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS tert_oras  text;
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS tert_judet text;

--
-- e-Factura PRIMITE de la furnizori din SPV (F126 receive, F179) — mirror al core/migrare_efactura_primite.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.efactura_primite (
  id                BIGSERIAL PRIMARY KEY,
  id_mesaj_anaf     TEXT NOT NULL,
  id_solicitare     TEXT,
  cif_emitent       TEXT NOT NULL,
  cif_beneficiar    TEXT NOT NULL,
  data_creare       TIMESTAMPTZ,
  tip               TEXT,
  xml_brut          TEXT,
  xml_sha256        TEXT NOT NULL,
  status            TEXT NOT NULL DEFAULT 'descarcata'
                    CHECK (status IN ('descarcata','ciorna','validata','respinsa')),
  factura_id        BIGINT REFERENCES TENANT_PLACEHOLDER.facturi(id),
  importat_la       TIMESTAMPTZ NOT NULL DEFAULT now(),
  validat_la        TIMESTAMPTZ,
  motiv_respins     TEXT,
  cont_cheltuiala   TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_efactura_primite_mesaj
  ON TENANT_PLACEHOLDER.efactura_primite (id_mesaj_anaf);
-- [factura_tva_cote_v1, lotul 11, C79] TVA-ul de pe factură, pe cote (BG-23) — SURSA: core/migrare_factura_tva_cote.py
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.factura_tva_cote (
  factura_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.facturi(id) ON DELETE CASCADE,
  nr smallint NOT NULL,
  categorie text,
  cota numeric(5,2) NOT NULL,
  baza numeric(15,2) NOT NULL,
  tva numeric(15,2) NOT NULL,
  sursa text NOT NULL CHECK (sursa IN ('BG-23', 'BT-110')),
  PRIMARY KEY (factura_id, nr)
);
-- [factura_tva_cote_v1] sfârșit
-- [valoare_neta_linie_v1, lotul 11, C82 / C80] BT-131 al liniei, exact; linia de document — SURSA: core/migrare_valoare_neta_linie.py
ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD COLUMN IF NOT EXISTS valoare_neta numeric(15,2);
ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD COLUMN IF NOT EXISTS nivel_document boolean NOT NULL DEFAULT false;
-- [valoare_neta_linie_v1] sfârșit

--
-- e-Transport: urmarirea trimiterilor UIT (F121) — mirror al core/migrare_etransport_trimiteri.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.etransport_trimiteri (
  id                BIGSERIAL PRIMARY KEY,
  mediu             TEXT NOT NULL CHECK (mediu IN ('test','prod')),
  stare             TEXT NOT NULL DEFAULT 'pregatit'
                    CHECK (stare IN ('pregatit','eroare_upload','incarcat','ok','nok')),
  index_incarcare   TEXT,
  uit               TEXT,
  data_transport    DATE,
  intracom          BOOLEAN NOT NULL DEFAULT false,
  uit_valabil_pana  DATE,
  execution_status  INTEGER,
  error_message     TEXT,
  ref_declarant     TEXT,
  xml_trimis        TEXT,
  xml_sha256        TEXT NOT NULL,
  trimis_la         TIMESTAMPTZ,
  creat_la          TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizat_la     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_etransport_trimiteri_viu
  ON TENANT_PLACEHOLDER.etransport_trimiteri (xml_sha256)
  WHERE mediu='prod' AND stare IN ('incarcat','ok');

-- F180: snapshot ANAF pentru platitor_tva (mirror in core/migrare_platitor_tva_anaf.py).
-- platitor_tva_anaf = scpTVA de la ANAF v9, SEPARAT de platitor_tva (editabil manual).
-- NULL = fara snapshot -> Control fiscal arata GRI. Data = cand a fost interogat ANAF.
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS platitor_tva_anaf boolean;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS platitor_tva_anaf_data date;
-- [B1] data inceperii inregistrarii in scopuri de TVA (fapt ANAF v9: perioade_TVA.data_inceput_ScpTVA activa)
-- -> declaratii_datorate margineste fereastra D300/D394 la perioadele DE DUPA inregistrare (nu restante inainte).
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS platitor_tva_anaf_inceput date;
-- [art.317 14.08.2026] inregistrare speciala in scopuri de TVA (art. 317 CF, fost 153^1): decide pers_inreg
-- in D301 (1 vs 2) si face verdictul D390 la neplatitorul cu IC satisfiabil (mirror in core/migrare_art317.py).
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS inreg_art317 boolean DEFAULT false NOT NULL;
-- [cont_venit_linie #11] contul de venit stabilit PE LINIE (marfa->707/produse->701/serviciu->704,
-- OMFP 1802/2014), editabil de contabil; contabilizarea grupeaza nota pe (cont_venit, cota).
-- Nullable: linie fara cont -> contabilizarea decide (cont_venit_implicit / legacy 707). Mirror in core/migrare_cont_venit_linie.py.
ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD COLUMN IF NOT EXISTS cont_venit text;
-- [274b, 16.10.2026] categoria de TVA a liniei cu cota 0% (core/categorii_tva.VALORI: codul UBL, motivul, rândul D300); NULL = linie
-- taxabilă sau factură de dinainte. Mirror în core/migrare_categorie_tva_linie.py.
ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD COLUMN IF NOT EXISTS categorie_tva text;
ALTER TABLE TENANT_PLACEHOLDER.factura_linii DROP CONSTRAINT IF EXISTS factura_linii_categorie_tva_check;
ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD CONSTRAINT factura_linii_categorie_tva_check CHECK (categorie_tva IS NULL OR categorie_tva IN ('taxare_inversa', 'scutit_cu_drept', 'scutit_fara_drept', 'livrare_ic', 'serviciu_extern', 'export', 'in_afara_sferei', 'neplatitor'));

-- [R130, 04.09.2026] cine si cand a introdus cursul de mana; v. core/migrare_curs_manual_urma.py
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS curs_manual_de text;
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS curs_manual_la timestamptz;
-- [decizia Costin A, 02.10.2026] factura emisă pe baza bonului fiscal (HG 1/2016 pct.97 alin.(1): „conform bon fiscal
-- nr./data”) — nu se mai numără a doua oară (D300, D394 op2, contare). Mirror core/migrare_factura_bon_fiscal.py.
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS bon_fiscal_nr text;
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS bon_fiscal_data date;
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD CONSTRAINT facturi_bon_fiscal_complet CHECK ((bon_fiscal_nr IS NULL) = (bon_fiscal_data IS NULL) AND (bon_fiscal_nr IS NULL OR btrim(bon_fiscal_nr) <> ''));

-- [14-1-2] Registrul-inventar, al doilea registru obligatoriu (Legea 82/1991 art. 20).
-- Continutul: OMFP 2634/2015 Anexa 2 — sase coloane. `valoare_inventar` e NOT NULL si nu are
-- default: completata implicit din `valoare_contabila`, ar produce un registru fara nicio
-- diferenta, adica o inventariere perfecta care nu s-a facut. `cauza` e nullable fiindca norma o
-- cere CONDITIONAT (numai cand exista diferenta) — regula sta in core/registru_inventar.py.
-- Mirror in core/migrare_registru_inventar.py, care e sursa de adevar.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.registru_inventar (
    id                 BIGSERIAL PRIMARY KEY,
    exercitiu          integer     NOT NULL,
    momentul           text        NOT NULL
                       CHECK (momentul IN ('inceput_activitate', 'sfarsit_exercitiu',
                                           'incetare_activitate')),
    nr_curent          integer     NOT NULL,
    cont               text        NOT NULL,
    element            text        NOT NULL,
    gestiune           text,
    valoare_contabila  numeric(18,2) NOT NULL,
    valoare_inventar   numeric(18,2) NOT NULL,
    cauza              text,
    data_inventariere  date,
    document           text,
    creat_la           timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registru_inventar_ordine_unica UNIQUE (exercitiu, momentul, nr_curent)
);

-- [art.321] Cele DOUA registre cerute de art. 321 alin. (4) CF prin normele lui
-- (HG 1/2016, lit. e) registrul nontransferurilor si lit. f) registrul bunurilor primite).
-- Un singur tabel cu discriminator: cele doua liste de campuri din norma sunt OGLINZI.
-- Mirror in core/migrare_registre_art321.py, care e sursa de adevar.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.registre_art321 (
    id                     BIGSERIAL PRIMARY KEY,
    fel                    text        NOT NULL
                           CHECK (fel IN ('nontransfer', 'bunuri_primite')),
    nr_ordine              integer     NOT NULL,
    partener_denumire      text        NOT NULL,
    partener_adresa        text        NOT NULL,
    data_transport         date        NOT NULL,
    descriere              text        NOT NULL,
    cantitate              numeric(18,3) NOT NULL,
    valoare                numeric(18,2),
    data_retur             date,
    descriere_returnate    text,
    cantitate_returnate    numeric(18,3),
    descriere_nereturnate  text,
    cantitate_nereturnate  numeric(18,3),
    documente              text,
    data_documente         date,
    creat_la               timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registre_art321_ordine_unica UNIQUE (fel, nr_ordine)
);


--
-- [GARZI cat.1, 20.09.2026] Intrare date, sub-lotul 1: NOT NULL pe coloanele de bani (categoriile A+B)
-- + chei naturale UNIQUE pe tabelele de import CURATE. Sursa unica a DDL-ului = core/migrare_intrare_date_garduri.py
-- (aceleasi coloane/constrangeri, aplicate pe tenantii existenti). In PostgreSQL UNIQUE trateaza NULL ca
-- distinct => unic pe non-NULL, NULL-uri nelimitate (PF fara CUI, articol fara barcode). EXCLUSE (whitelist,
-- vezi core/test_intrare_date_garduri.py): produse (fara camp de cod), mijloace_fixe (sub-lotul 2), si
-- coloanele legitim nullable (curs valutar pe RON, venituri_6_luni).
--
ALTER TABLE TENANT_PLACEHOLDER.bonuri ALTER COLUMN total SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.bonuri ALTER COLUMN tva_11 SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.bonuri ALTER COLUMN tva_21 SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN baza SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN brut_ang SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN brut_fnuass SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN cas SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN cass SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN impozit SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.concedii_medicale ALTER COLUMN net SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.d301_operatiuni ALTER COLUMN tva SET NOT NULL;
-- [DECIZII 66] factura_id: operatiunea D301 scrisa de achizitie_ic poarta id-ul facturii;
-- D390-din-op filtreaza factura_id IS NULL (achizitia legata intra in D390 din factura).
-- Mirror core/migrare_d301_op_factura.py.
ALTER TABLE TENANT_PLACEHOLDER.d301_operatiuni ADD COLUMN IF NOT EXISTS factura_id integer;
ALTER TABLE TENANT_PLACEHOLDER.plan_conturi ALTER COLUMN sold_creditor SET NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.plan_conturi ALTER COLUMN sold_debitor SET NOT NULL;

ALTER TABLE TENANT_PLACEHOLDER.efactura_primite ADD CONSTRAINT efactura_primite_msg_uniq UNIQUE (id_mesaj_anaf);
ALTER TABLE TENANT_PLACEHOLDER.solduri_initiale ADD CONSTRAINT solduri_initiale_cont_uniq UNIQUE (cont);
ALTER TABLE TENANT_PLACEHOLDER.solduri_parteneri ADD CONSTRAINT solduri_parteneri_cont_cui_uniq UNIQUE (cont, cui);
ALTER TABLE TENANT_PLACEHOLDER.asociati ADD CONSTRAINT asociati_cnp_uniq UNIQUE (cnp);
ALTER TABLE TENANT_PLACEHOLDER.clienti ADD CONSTRAINT clienti_cui_uniq UNIQUE (cui);
ALTER TABLE TENANT_PLACEHOLDER.furnizori ADD CONSTRAINT furnizori_cui_uniq UNIQUE (cui);
ALTER TABLE TENANT_PLACEHOLDER.state_plata ADD CONSTRAINT state_plata_sal_luna_ex_uniq UNIQUE (salariat_id, luna, exemplar);
ALTER TABLE TENANT_PLACEHOLDER.articole ADD CONSTRAINT articole_barcode_uniq UNIQUE (barcode);
ALTER TABLE TENANT_PLACEHOLDER.mijloace_fixe ADD CONSTRAINT mijloace_fixe_cod_uniq UNIQUE (cod);
-- [08.10.2026, decizia Costin W2] codul de clasificare din Catalogul HG 2139/2004 (mirror core/migrare_decizii_0810.py)
ALTER TABLE TENANT_PLACEHOLDER.mijloace_fixe ADD COLUMN IF NOT EXISTS cod_catalog text;

-- [lot 19 pct.4b, 02.10.2026] Defalcarea raportului Z pe cote (baza + TVA pe fiecare cota), scrisa de
-- ambele cai de import (AMEF `coteZ` / ruta tastata) in aceeasi tranzactie cu nota; D300 rd.9/10 o citeste.
-- Nota contabila (707/4427) poarta un singur TVA, fara cota. Mirror core/raport_z.py (_SQL_TABEL_COTE).
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.rapoarte_z_cote (
    id serial PRIMARY KEY,
    inregistrare_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE CASCADE,
    cota numeric(5,2) NOT NULL,
    baza numeric(15,2) NOT NULL,
    tva numeric(15,2) NOT NULL,
    CONSTRAINT rapoarte_z_cote_nota_cota_uniq UNIQUE (inregistrare_id, cota)
);

-- [D394 op2 I1, decizia Costin 02.10.2026, varianta B] Casa (NUI) si numarul de bonuri ale raportului Z, un rand pe
-- raport, scris de AMBELE rute (import AMEF + ruta tastata). D394 lit.G: nr. de AMEF (case distincte pe luna) +
-- nr. bonuri fiscale. Mirror core/raport_z.py (_SQL_TABEL_AMEF).
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.rapoarte_z_amef (
    inregistrare_id integer PRIMARY KEY REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE CASCADE,
    nui text NOT NULL CHECK (btrim(nui) <> ''),
    nr_bonuri integer NOT NULL CHECK (nr_bonuri > 0)
);

-- [lot 19 pct.4c, 02.10.2026] Perioadele de suspendare FARA drepturi salariale (CFP / suspendare, Codul muncii
-- art.49 alin.(2), art.54, art.153). Statul de plata si D112 proratau brutul doar la CM. Mirror
-- core/migrare_suspendari_contract.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.suspendari_contract (
    id serial PRIMARY KEY,
    salariat_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.salariati(id) ON DELETE CASCADE,
    data_inceput date NOT NULL,
    data_sfarsit date NOT NULL,
    tip text NOT NULL CONSTRAINT suspendari_contract_tip CHECK (tip IN ('cfp', 'suspendare')),
    temei text,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT suspendari_contract_interval CHECK (data_sfarsit >= data_inceput),
    CONSTRAINT suspendari_contract_uniq UNIQUE (salariat_id, data_inceput)
);

-- [lot 19 pct.4e, 02.10.2026] Structurile ANTERIOARE ale asociatilor (cote), valabile pana la o data - D205 imparte
-- fiecare dividend dupa structura de la data distribuirii (Legea 31/1990 art.67 alin.(2) si (6)).
-- Mirror core/migrare_asociati_istoric.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.asociati_istoric (
    id serial PRIMARY KEY,
    cnp text NOT NULL,
    nume text,
    cota numeric NOT NULL,
    valabil_pana_la date NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT asociati_istoric_uniq UNIQUE (valabil_pana_la, cnp)
);

-- [decizia Costin 05.10.2026] jurnalul cotei TVA alese pe linia facturii (propus -> ales, cine, când).
-- Mirror core/migrare_factura_cota_jurnal.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.factura_cota_jurnal (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    factura_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.facturi(id) ON DELETE CASCADE,
    linie_nr integer NOT NULL,
    descriere text,
    cota_propusa numeric(5,2) NOT NULL,
    cota_aleasa numeric(5,2) NOT NULL,
    user_id integer NOT NULL,
    la timestamp with time zone NOT NULL DEFAULT now()
);

-- [decizia Costin 04.10.2026] jurnalul schimbărilor regimului de TVA (platitor_tva, tip_decont, inreg_art317: utilizator,
-- dată, veche -> nouă). Mirror core/migrare_firma_profil_jurnal.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.firma_profil_jurnal (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    camp character varying(40) NOT NULL,
    valoare_veche text,
    valoare_noua text,
    user_id integer NOT NULL,
    la timestamp with time zone NOT NULL DEFAULT now()
);

-- [decizia Costin 04.10.2026] jurnalul schimbărilor de pe fișa mijlocului fix (bifa C&D: utilizator, dată, veche -> nouă).
-- Mirror core/migrare_mf_jurnal.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.mijloace_fixe_jurnal (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mijloc_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.mijloace_fixe(id),
    camp character varying(40) NOT NULL,
    valoare_veche text,
    valoare_noua text,
    user_id integer,
    la timestamp with time zone NOT NULL DEFAULT now()
);

--
-- Contorul documentelor interne pe tip și an (comanda Costin 06.10.2026 §6.2) — mirror al core/migrare_documente_interne.py
--
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.documente_interne_contor (
    tip text NOT NULL,
    an integer NOT NULL,
    ultim integer NOT NULL,
    PRIMARY KEY (tip, an)
);

--
-- Metoda de stoc, setare explicită pe firmă (comanda Costin 06.10.2026 §6.3) — mirror al core/migrare_metoda_stoc.py
--
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS metoda_stoc text
    CHECK (metoda_stoc IN ('global_valoric', 'cantitativ_valoric'));

--
-- Faptele DA/NU din Date firmă fără implicit în schemă (lotul 07.10 B, comanda Costin A.3) — mirror al core/migrare_fapte_date_firma.py.
-- NULL = neales; se cer o singură dată, la prima folosire (chitanța fără factură / D394 pentru AMEF, D301 pentru art.317).
--
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ALTER COLUMN activitate_exceptata_amef DROP NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ALTER COLUMN activitate_exceptata_amef DROP DEFAULT;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ALTER COLUMN inreg_art317 DROP NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ALTER COLUMN inreg_art317 DROP DEFAULT;

--
-- NIR-ul la firma cu stocul la cost (lotul 07.10 B, comanda Costin C10/C11) — mirror al core/migrare_nir_cost.py
--
ALTER TABLE TENANT_PLACEHOLDER.nir_linii ALTER COLUMN pret_vanzare DROP NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.nir_linii ALTER COLUMN cota_tva DROP DEFAULT;
ALTER TABLE TENANT_PLACEHOLDER.nir_linii ADD COLUMN IF NOT EXISTS articol_id integer;
ALTER TABLE TENANT_PLACEHOLDER.nir ADD COLUMN IF NOT EXISTS metoda_stoc text;

--
-- Lotul „Deciziile 07.10” + retesturile 07.10 (comenzile Costin) — mirror al core/migrare_decizii_0710.py
--   D5 seria chitanței fără implicit; D2 NIR-ul legat de factura primită; R1 stornarea la respingere, NIR-ul refăcut.
--
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ALTER COLUMN serie_chitanta DROP DEFAULT;
ALTER TABLE TENANT_PLACEHOLDER.nir ADD COLUMN IF NOT EXISTS factura_id integer;
ALTER TABLE TENANT_PLACEHOLDER.nir ADD CONSTRAINT nir_factura_fk FOREIGN KEY (factura_id) REFERENCES TENANT_PLACEHOLDER.facturi(id);
CREATE UNIQUE INDEX IF NOT EXISTS nir_factura_id_uq ON TENANT_PLACEHOLDER.nir (factura_id) WHERE factura_id IS NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ADD COLUMN IF NOT EXISTS nir_id integer;
ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ADD COLUMN IF NOT EXISTS anuleaza_id integer;
ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ADD CONSTRAINT miscari_stoc_nir_fk FOREIGN KEY (nir_id) REFERENCES TENANT_PLACEHOLDER.nir(id);
ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ADD CONSTRAINT miscari_stoc_anuleaza_fk FOREIGN KEY (anuleaza_id) REFERENCES TENANT_PLACEHOLDER.miscari_stoc(id);
CREATE UNIQUE INDEX IF NOT EXISTS miscari_stoc_anuleaza_uq ON TENANT_PLACEHOLDER.miscari_stoc (anuleaza_id) WHERE anuleaza_id IS NOT NULL;
ALTER TABLE TENANT_PLACEHOLDER.nir ADD COLUMN IF NOT EXISTS refacut_din_id integer;
CREATE UNIQUE INDEX IF NOT EXISTS nir_refacut_din_uq ON TENANT_PLACEHOLDER.nir (refacut_din_id) WHERE refacut_din_id IS NOT NULL;
-- D3 raportul Z la cantitativ-valoric: ieșirile legate de Z și declarația „fără marfă”
ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ADD COLUMN IF NOT EXISTS z_inregistrare_id integer;
ALTER TABLE TENANT_PLACEHOLDER.miscari_stoc ADD CONSTRAINT miscari_stoc_z_fk FOREIGN KEY (z_inregistrare_id) REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE SET NULL;
ALTER TABLE TENANT_PLACEHOLDER.rapoarte_z_amef ADD COLUMN IF NOT EXISTS fara_marfa boolean;
-- S1 elementele variabile ale salariului (prime, sporuri, ore suplimentare), pe salariat și pe lună
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.elemente_salariale (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    salariat_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.salariati(id) ON DELETE CASCADE,
    an integer NOT NULL,
    luna integer NOT NULL CHECK (luna BETWEEN 1 AND 12),
    tip text NOT NULL CHECK (tip IN ('prima', 'spor', 'ore_suplimentare')),
    denumire text NOT NULL CHECK (length(btrim(denumire)) > 0),
    ore numeric(7,2) CHECK (ore IS NULL OR ore > 0),
    suma numeric(12,2) NOT NULL CHECK (suma > 0),
    creat_la timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT elemente_salariale_ore_ck CHECK ((tip = 'ore_suplimentare') = (ore IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS elemente_salariale_luna_ix ON TENANT_PLACEHOLDER.elemente_salariale (an, luna, salariat_id);

-- [08.10.2026, decizia Costin §6 pct.4] luna preluării, editabilă în Date firmă (mirror core/migrare_decizii_0810_s6.py)
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS luna_preluare date;

-- [12.10.2026, deficiența 229] data înființării (ANAF data_inregistrare / Date firmă): primul exercițiu (mirror core/migrare_data_infiintare.py)
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS data_infiintare date;

-- [Retest 2 pct.4] stornarea operațiunii de casă: legătura spre operațiunea stornată (mirror: core/migrare_retest2.py)
ALTER TABLE ONLY TENANT_PLACEHOLDER.casa_operatiuni
    ADD CONSTRAINT casa_operatiuni_storno_de_fkey FOREIGN KEY (storno_de) REFERENCES TENANT_PLACEHOLDER.casa_operatiuni(id);
CREATE UNIQUE INDEX casa_operatiuni_storno_de_uq ON TENANT_PLACEHOLDER.casa_operatiuni (storno_de) WHERE storno_de IS NOT NULL;

-- [reguli_fond_v1, 09.10.2026] regulile de fond în bază (comanda Costin pct.11) — SURSA: core/migrare_reguli_fond.py
CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.nota_din_tranzactia_curenta(nid integer) RETURNS boolean AS $$
  -- rândul vizibil al cărui `xmin` e încă „in progress” poate fi numai al tranzacției curente (și al sub-tranzacțiilor ei, care au
  -- identificatori MAI MARI decât ea); `xmin` e pe 32 de biți: se pune epoca curentă, iar numai un `xmin` cu peste 2^31 înaintea
  -- tranzacției curente e din epoca anterioară; un rezultat negativ sau NULL (prea vechi) = nu e al tranzacției
  SELECT COALESCE((
    SELECT pg_xact_status(y::text::xid8) = 'in progress'
      FROM (SELECT CASE WHEN x - c > 2147483648 THEN x - 4294967296 ELSE x END AS y
              FROM (SELECT ((k.c >> 32) << 32) | i.xmin::text::bigint AS x, k.c
                      FROM TENANT_PLACEHOLDER.inregistrari i, (SELECT pg_current_xact_id()::text::bigint AS c) k WHERE i.id = nid) t) u
     WHERE y >= 0), false)
$$ LANGUAGE sql VOLATILE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_nota() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status = 'validata' AND NOT TENANT_PLACEHOLDER.nota_din_tranzactia_curenta(OLD.id) THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Nota % e validată, deci nu se mai șterge. Corectura se face prin stornare (OMFP 1802/2014 pct.69).', TENANT_PLACEHOLDER.eticheta_nota(OLD.id);
    END IF;
    RETURN OLD;
  END IF;
  IF TG_OP = 'UPDATE' AND OLD.status = 'validata' AND NOT TENANT_PLACEHOLDER.nota_din_tranzactia_curenta(OLD.id)
     AND (NEW.data, NEW.numar, NEW.factura_id, NEW.document_ref, NEW.descriere, NEW.sursa, NEW.status)
         IS DISTINCT FROM (OLD.data, OLD.numar, OLD.factura_id, OLD.document_ref, OLD.descriere, OLD.sursa, OLD.status) THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Nota % e validată, deci nu se mai modifică. Corectura se face prin stornare (OMFP 1802/2014 pct.69).', TENANT_PLACEHOLDER.eticheta_nota(OLD.id);
  END IF;
  IF NEW.status = 'validata' AND OLD.status IS DISTINCT FROM 'validata' AND COALESCE(btrim(NEW.document_ref), '') = ''
     AND NOT EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.facturi f WHERE f.id = NEW.factura_id) THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Nota % n-are documentul justificativ: o notă nu se validează fără documentul din care provine.', TENANT_PLACEHOLDER.eticheta_nota(NEW.id);
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_nota ON TENANT_PLACEHOLDER.inregistrari;
CREATE TRIGGER trg_regula_nota BEFORE UPDATE OR DELETE ON TENANT_PLACEHOLDER.inregistrari
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_nota();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  FOREACH d IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.data END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.data END] LOOP
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_verifica_perioada_blocata ON TENANT_PLACEHOLDER.inregistrari;
CREATE TRIGGER trg_verifica_perioada_blocata BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.inregistrari
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_linii_nota() RETURNS trigger AS $$
DECLARE
  nid integer; st text; d date;
BEGIN
  IF TG_OP <> 'DELETE' AND (COALESCE(btrim(NEW.cont_debit), '') = '' OR COALESCE(btrim(NEW.cont_credit), '') = '') THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Un rând de notă are nevoie de ambele conturi, debitor și creditor: debitul e egal cu creditul numai așa.';
  END IF;
  FOREACH nid IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.inregistrare_id END,
                            CASE WHEN TG_OP <> 'DELETE' THEN NEW.inregistrare_id END] LOOP
    CONTINUE WHEN nid IS NULL;
    SELECT status, data INTO st, d FROM TENANT_PLACEHOLDER.inregistrari WHERE id = nid;
    IF st = 'validata' AND NOT TENANT_PLACEHOLDER.nota_din_tranzactia_curenta(nid) THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Nota % e validată, deci rândurile ei nu se mai schimbă. Corectura se face prin stornare (OMFP 1802/2014 pct.69).', TENANT_PLACEHOLDER.eticheta_nota(nid);
    END IF;
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_linii_nota ON TENANT_PLACEHOLDER.inregistrari_linii;
CREATE TRIGGER trg_regula_linii_nota BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.inregistrari_linii
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_linii_nota();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.miscare_in_evidenta(mid integer) RETURNS boolean AS $$
  SELECT EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.miscari_stoc m WHERE m.id = mid AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.inregistrari i WHERE i.status = 'validata' AND (i.id = m.inregistrare_id OR (m.inregistrare_id IS NULL AND m.nir_id IS NOT NULL AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.nir n WHERE n.id = m.nir_id AND n.inregistrari_ids @> to_jsonb(i.id))) OR (m.inregistrare_id IS NULL AND m.factura_id IS NOT NULL AND i.factura_id = m.factura_id))))
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_stoc() RETURNS trigger AS $$
DECLARE
  nota_tinta integer; st text;
BEGIN
  IF TG_OP <> 'INSERT' AND TENANT_PLACEHOLDER.miscare_in_evidenta(OLD.id) THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Mișcarea de stoc „%” e a unui document contat: nu se modifică și nu se șterge. Se corectează printr-un document de corecție.', OLD.document;
  END IF;
  IF TG_OP <> 'DELETE' AND NEW.anuleaza_id IS NOT NULL AND TENANT_PLACEHOLDER.miscare_in_evidenta(NEW.anuleaza_id) THEN
    SELECT inregistrare_id INTO nota_tinta FROM TENANT_PLACEHOLDER.miscari_stoc WHERE id = NEW.anuleaza_id;
    SELECT status INTO st FROM TENANT_PLACEHOLDER.inregistrari WHERE id = NEW.inregistrare_id;
    IF NEW.inregistrare_id IS NULL OR NEW.inregistrare_id IS NOT DISTINCT FROM nota_tinta OR st IS DISTINCT FROM 'ciorna' THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Mișcarea de stoc „%” e a unui document contat: se stornează numai cu un document de corecție (o notă nouă, în ciornă).', (SELECT m.document FROM TENANT_PLACEHOLDER.miscari_stoc m WHERE m.id = NEW.anuleaza_id);
    END IF;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_stoc ON TENANT_PLACEHOLDER.miscari_stoc;
CREATE TRIGGER trg_regula_stoc BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.miscari_stoc
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_stoc();
-- [reguli_fond_v1] sfârșit
-- [reguli_fond_v2, 09.10.2026] regulile de fond a, c, d, e, f (comanda Costin „Retestul plasei” pct.6) — SURSA: core/migrare_reguli_fond_2.py
CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_factura_emisa() RETURNS trigger AS $$
BEGIN
  IF OLD.directie = 'emisa' AND COALESCE(OLD.tip, 'factura') = 'factura' AND COALESCE(OLD.status, 'emisa') NOT IN ('ciorna') THEN
    RAISE EXCEPTION 'REGULA_CONTABILA: Factura % e emisă, deci nu se șterge: se corectează prin factură de stornare (CF art.330 alin.(1)).',
      COALESCE(OLD.serie, '') || OLD.numar;
  END IF;
  RETURN OLD;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_factura_emisa ON TENANT_PLACEHOLDER.facturi;
CREATE TRIGGER trg_regula_factura_emisa BEFORE DELETE ON TENANT_PLACEHOLDER.facturi
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_factura_emisa();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.efect_stoc(tip text, cantitate numeric) RETURNS numeric AS $$
  SELECT CASE WHEN tip = 'intrare' THEN cantitate WHEN tip = 'iesire' THEN -cantitate ELSE 0 END
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_stoc_nenegativ() RETURNS trigger AS $$
DECLARE
  delta numeric := 0; art integer; q numeric;
BEGIN
  IF TG_OP <> 'INSERT' THEN delta := delta - TENANT_PLACEHOLDER.efect_stoc(OLD.tip, OLD.cantitate); art := OLD.articol_id; END IF;
  IF TG_OP <> 'DELETE' THEN delta := delta + TENANT_PLACEHOLDER.efect_stoc(NEW.tip, NEW.cantitate); art := NEW.articol_id; END IF;
  IF TG_OP = 'UPDATE' AND OLD.articol_id IS DISTINCT FROM NEW.articol_id THEN
    delta := -TENANT_PLACEHOLDER.efect_stoc(OLD.tip, OLD.cantitate); art := OLD.articol_id;   -- articolul vechi pierde mișcarea întreagă
  END IF;
  IF delta < 0 THEN
    SELECT COALESCE(SUM(TENANT_PLACEHOLDER.efect_stoc(m.tip, m.cantitate)), 0) INTO q FROM TENANT_PLACEHOLDER.miscari_stoc m WHERE m.articol_id = art;
    IF q + delta < 0 THEN
      RAISE EXCEPTION 'REGULA_CONTABILA: Stocul articolului „%” ar deveni negativ (% după mișcarea „%”): o ieșire nu poate scoate mai mult decât e în stoc.',
        (SELECT a.denumire FROM TENANT_PLACEHOLDER.articole a WHERE a.id = art), q + delta, COALESCE(CASE WHEN TG_OP = 'DELETE' THEN OLD.document ELSE NEW.document END, 'fără document');
    END IF;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_stoc_nenegativ ON TENANT_PLACEHOLDER.miscari_stoc;
CREATE TRIGGER trg_regula_stoc_nenegativ BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.miscari_stoc
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_stoc_nenegativ();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_chitanta() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'REGULA_CONTABILA: Chitanța % nr. % e emisă, deci nu se șterge: se anulează și se păstrează (OMFP 2634/2015, Anexa 1 pct.15).',
    OLD.serie, OLD.numar;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_chitanta ON TENANT_PLACEHOLDER.chitante;
CREATE TRIGGER trg_regula_chitanta BEFORE DELETE ON TENANT_PLACEHOLDER.chitante
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_chitanta();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_facturi() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  FOREACH d IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.data_emitere END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.data_emitere END] LOOP
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_perioada_blocata_facturi ON TENANT_PLACEHOLDER.facturi;
CREATE TRIGGER trg_perioada_blocata_facturi BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.facturi
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_facturi();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_miscari_stoc() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  FOREACH d IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.data END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.data END] LOOP
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_perioada_blocata_miscari_stoc ON TENANT_PLACEHOLDER.miscari_stoc;
CREATE TRIGGER trg_perioada_blocata_miscari_stoc BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.miscari_stoc
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_miscari_stoc();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_casa_operatiuni() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  FOREACH d IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.data END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.data END] LOOP
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_perioada_blocata_casa_operatiuni ON TENANT_PLACEHOLDER.casa_operatiuni;
CREATE TRIGGER trg_perioada_blocata_casa_operatiuni BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.casa_operatiuni
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_casa_operatiuni();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_chitante() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  FOREACH d IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.data END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.data END] LOOP
    IF d IS NOT NULL AND EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
               WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
      RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
        LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_perioada_blocata_chitante ON TENANT_PLACEHOLDER.chitante;
CREATE TRIGGER trg_perioada_blocata_chitante BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.chitante
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata_chitante();
-- [reguli_fond_v2] sfârșit
-- [nr_curent_v1, 17.10.2026] numărul notei dat la validare (deficiența 302) — SURSA: core/migrare_nr_curent_note.py
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.registru_jurnal_numere (
    inregistrare_id integer PRIMARY KEY REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE CASCADE,
    an integer NOT NULL,
    nr_curent integer NOT NULL,
    dat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registru_jurnal_numere_unic UNIQUE (an, nr_curent)
);
INSERT INTO TENANT_PLACEHOLDER.registru_jurnal_numere (inregistrare_id, an, nr_curent)
SELECT x.id, x.an, x.rn
  FROM (SELECT id, status, EXTRACT(YEAR FROM data)::int AS an,
               ROW_NUMBER() OVER (PARTITION BY date_trunc('year', data) ORDER BY data, id) AS rn FROM TENANT_PLACEHOLDER.inregistrari) x
 WHERE x.status = 'validata' AND NOT EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.registru_jurnal_numere);

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.nr_curent_la_validare() RETURNS trigger AS $$
DECLARE
  an_nota integer := EXTRACT(YEAR FROM NEW.data)::int;
BEGIN
  IF NEW.status = 'validata' AND NOT EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.registru_jurnal_numere WHERE inregistrare_id = NEW.id) THEN
    PERFORM pg_advisory_xact_lock(hashtext('nr_curent:' || TG_TABLE_SCHEMA || ':' || an_nota::text));
    INSERT INTO TENANT_PLACEHOLDER.registru_jurnal_numere (inregistrare_id, an, nr_curent)
    SELECT NEW.id, an_nota, COALESCE(MAX(nr_curent), 0) + 1 FROM TENANT_PLACEHOLDER.registru_jurnal_numere WHERE an = an_nota;
  END IF;
  RETURN NULL;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_nr_curent_la_validare ON TENANT_PLACEHOLDER.inregistrari;
CREATE TRIGGER trg_nr_curent_la_validare AFTER INSERT OR UPDATE OF status ON TENANT_PLACEHOLDER.inregistrari
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.nr_curent_la_validare();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.nr_curent_neschimbat() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'REGULA_CONTABILA: Nota nr. crt. % din % e în Registrul-jurnal: numărul ei nu se mai schimbă.', OLD.nr_curent, OLD.an;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_nr_curent_neschimbat ON TENANT_PLACEHOLDER.registru_jurnal_numere;
CREATE TRIGGER trg_nr_curent_neschimbat BEFORE UPDATE ON TENANT_PLACEHOLDER.registru_jurnal_numere
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.nr_curent_neschimbat();
-- [nr_curent_v1] sfârșit

-- [ciorne_proprii_v1, 15.10.2026] ciorna altui utilizator (deficiența 246) — SURSA: core/migrare_ciorne_proprii.py
CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.eticheta_nota(nid integer) RETURNS text AS $$
  -- [deficiența 258] numele notei cum îl vede contabilul în Registrul jurnal: „nr. crt. N din ZZ.LL.AAAA”. [deficiența 302, 17.10.2026]
  -- N = `registru_jurnal_numere.nr_curent`, dat la validare și neschimbat după (core/migrare_nr_curent_note.py); nota nevalidată n-are număr: „din ZZ.LL.AAAA”
  -- („Nota din 07.10.2026 e ciorna lui …”; starea o spune fraza în care stă eticheta). NULL dacă nota nu există. Python o cheamă prin `core/eticheta_nota.py`, ca textul din
  -- bază și cel din aplicație să fie unul (paritatea cu Registrul jurnal: core/test_eticheta_nota.py).
  SELECT CASE WHEN r.nr_curent IS NOT NULL THEN 'nr. crt. ' || r.nr_curent || ' din ' || to_char(n.data, 'DD.MM.YYYY')
              ELSE 'din ' || to_char(n.data, 'DD.MM.YYYY') END
    FROM TENANT_PLACEHOLDER.inregistrari n LEFT JOIN TENANT_PLACEHOLDER.registru_jurnal_numere r ON r.inregistrare_id = n.id WHERE n.id = nid
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.eticheta_rip(oid integer) RETURNS text AS $$
  -- [deficiența 258] operațiunea din registrul de încasări și plăți cum o arată rândul ei: „plata din ZZ.LL.AAAA de 1.234,50 RON”
  SELECT CASE WHEN r.tip = 'plata' THEN 'plata' ELSE 'încasarea' END || ' din ' || to_char(r.data_operatiune, 'DD.MM.YYYY') || ' de '
         || translate(to_char(r.suma, 'FM999,999,999,990.00'), ',.', '.,') || ' ' || r.valuta
    FROM TENANT_PLACEHOLDER.rip_operatiuni r WHERE r.id = oid
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.ciorna_altui(autor integer, utilizator integer) RETURNS text AS $$
  -- numele autorului dacă `utilizator` e asistent (`angajat`) și ciorna e a ALTUI utilizator; NULL altfel (fără autor, fără utilizator,
  -- autorul însuși, administratorul / superadminul)
  SELECT COALESCE(NULLIF(btrim(concat_ws(' ', a.prenume, a.nume)), ''), a.email)
    FROM public.users u JOIN public.users a ON a.id = autor
   WHERE u.id = utilizator AND u.rol = 'angajat' AND autor <> utilizator
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.utilizatorul_cererii() RETURNS integer AS $$
  SELECT NULLIF(current_setting('iconta.utilizator', true), '')::integer
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.decizia_validatorului() RETURNS boolean AS $$
  SELECT COALESCE((SELECT poate_valida FROM public.users WHERE id = TENANT_PLACEHOLDER.utilizatorul_cererii()), false)
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_ciorna_proprie() RETURNS trigger AS $$
DECLARE
  autor text;
BEGIN
  IF OLD.status = 'validata' THEN
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
  END IF;
  autor := TENANT_PLACEHOLDER.ciorna_altui(OLD.creat_de_id, TENANT_PLACEHOLDER.utilizatorul_cererii());
  IF autor IS NOT NULL AND NOT (TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status AND TENANT_PLACEHOLDER.decizia_validatorului())
     AND (TG_OP = 'DELETE' OR (NEW.data, NEW.numar, NEW.factura_id, NEW.document_ref, NEW.descriere, NEW.sursa, NEW.status)
                              IS DISTINCT FROM (OLD.data, OLD.numar, OLD.factura_id, OLD.document_ref, OLD.descriere, OLD.sursa, OLD.status)) THEN
    RAISE EXCEPTION 'DREPT_CIORNA: Nota % e ciorna lui %: o poți vedea, dar n-o modifici, n-o ștergi și n-o trimiți la validare. Dacă trebuie schimbată, spune-i lui % sau administratorului cabinetului.', TENANT_PLACEHOLDER.eticheta_nota(OLD.id), autor, autor;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_ciorna_proprie ON TENANT_PLACEHOLDER.inregistrari;
CREATE TRIGGER trg_regula_ciorna_proprie BEFORE UPDATE OR DELETE ON TENANT_PLACEHOLDER.inregistrari
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_ciorna_proprie();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_linii_ciorna_proprie() RETURNS trigger AS $$
DECLARE
  nid integer; st text; aut integer; autor text;
BEGIN
  FOREACH nid IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.inregistrare_id END,
                            CASE WHEN TG_OP <> 'DELETE' THEN NEW.inregistrare_id END] LOOP
    CONTINUE WHEN nid IS NULL;
    SELECT status, creat_de_id INTO st, aut FROM TENANT_PLACEHOLDER.inregistrari WHERE id = nid;
    CONTINUE WHEN st IS NULL OR st = 'validata';
    autor := TENANT_PLACEHOLDER.ciorna_altui(aut, TENANT_PLACEHOLDER.utilizatorul_cererii());
    IF autor IS NOT NULL THEN
      RAISE EXCEPTION 'DREPT_CIORNA: Nota % e ciorna lui %: o poți vedea, dar n-o modifici, n-o ștergi și n-o trimiți la validare. Dacă trebuie schimbată, spune-i lui % sau administratorului cabinetului.', TENANT_PLACEHOLDER.eticheta_nota(nid), autor, autor;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_linii_ciorna_proprie ON TENANT_PLACEHOLDER.inregistrari_linii;
CREATE TRIGGER trg_regula_linii_ciorna_proprie BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.inregistrari_linii
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_linii_ciorna_proprie();

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.regula_rip_ciorna_proprie() RETURNS trigger AS $$
DECLARE
  autor text;
BEGIN
  IF OLD.status = 'validata' THEN
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
  END IF;
  autor := TENANT_PLACEHOLDER.ciorna_altui(OLD.creat_de, TENANT_PLACEHOLDER.utilizatorul_cererii());
  IF autor IS NOT NULL AND NOT (TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status AND TENANT_PLACEHOLDER.decizia_validatorului()) THEN
    RAISE EXCEPTION 'DREPT_CIORNA: În registrul de încasări și plăți, % e ciorna lui %: o poți vedea, dar n-o modifici și n-o ștergi. Dacă trebuie schimbată, spune-i lui % sau administratorului cabinetului.', TENANT_PLACEHOLDER.eticheta_rip(OLD.id), autor, autor;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_rip_ciorna_proprie ON TENANT_PLACEHOLDER.rip_operatiuni;
CREATE TRIGGER trg_regula_rip_ciorna_proprie BEFORE UPDATE OR DELETE ON TENANT_PLACEHOLDER.rip_operatiuni
  FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.regula_rip_ciorna_proprie();
-- [ciorne_proprii_v1] sfârșit

-- [deficiența 378, comanda Costin 8.2, 18.10.2026] ajustările fiscale ale rezultatului (Registrul de evidență fiscală, varianta pe profit),
-- pe rândul oficial D101 (OPANAF 206/2025): sursa unică pentru D100 trimestrial (cumulat) și D101. `trim` NULL = cifră a anului (rd.39,
-- pierderea de recuperat). Firmele existente: core/migrare_ajustari_fiscale.py. Modulul: core/ajustari_fiscale.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.ajustari_fiscale (
    id serial PRIMARY KEY,
    an integer NOT NULL,
    trim smallint CHECK (trim BETWEEN 1 AND 4),
    rand text NOT NULL,
    suma numeric(15,2) NOT NULL CHECK (suma > 0),
    descriere text,
    document text,
    creat_de integer,
    creat_la timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ajustari_fiscale_an ON TENANT_PLACEHOLDER.ajustari_fiscale (an);

-- [deficiența 381, comanda Costin 8.2, 18.10.2026] partenerul pe linia notei: nota pe 401 / 4111 îl cere la introducere (Registrul jurnal),
-- iar D406 îl pune pe CustomerID / SupplierID (până azi venea numai din factura legată). Firmele existente:
-- core/migrare_partener_linie.py.
ALTER TABLE TENANT_PLACEHOLDER.inregistrari_linii ADD COLUMN IF NOT EXISTS partener_cui text;
ALTER TABLE TENANT_PLACEHOLDER.inregistrari_linii ADD COLUMN IF NOT EXISTS partener_nume text;

-- [deficiența 359, comanda Costin 8.2, 18.10.2026] amortizarea cumulată preluată din registrul vechi, la data preluării: se compară cu cea
-- calculată din PIF + durată + metodă și se reconciliază cu balanța de deschidere (auditul de preluare). Firmele existente:
-- core/migrare_mf_amortizare_preluata.py.
ALTER TABLE TENANT_PLACEHOLDER.mijloace_fixe ADD COLUMN IF NOT EXISTS amortizare_preluata numeric;
ALTER TABLE TENANT_PLACEHOLDER.mijloace_fixe ADD COLUMN IF NOT EXISTS data_preluare date;

-- [deficiența 418b, comanda Costin 9.3, 19.10.2026] contul liniei unei facturi PRIMITE (marfă pe 371, cartea de birou pe cheltuială);
-- gol = contul facturii. Firmele existente: core/migrare_cont_linie_primita.py.
ALTER TABLE TENANT_PLACEHOLDER.factura_linii ADD COLUMN IF NOT EXISTS cont_cheltuiala text;

-- [deficiențele 401–402, 19.10.2026] actul de identitate al persoanei fizice de pe borderoul de achiziție (`facturi.tip = 'borderou'`).
-- Firmele existente: core/migrare_borderou_achizitie.py.
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS tert_act_identitate text;

-- [deficiențele 404–405, lotul 9, 19.10.2026] plata în numerar a unui NIR fără factură (avans 4091 = 5311, legat de NIR) și ajustarea fiscală
-- scrisă automat din nota inventarului (în calcul numai cu nota validată; ștearsă cu ea). Firmele existente:
-- core/migrare_avans_nir_ajustare_nota.py.
ALTER TABLE TENANT_PLACEHOLDER.casa_operatiuni ADD COLUMN IF NOT EXISTS nir_id integer REFERENCES TENANT_PLACEHOLDER.nir(id);
ALTER TABLE TENANT_PLACEHOLDER.ajustari_fiscale ADD COLUMN IF NOT EXISTS inregistrare_id integer REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE CASCADE;

-- [deficiența 425, lotul 10, 20.10.2026] balanța de deschidere cu soldurile inițiale ale anului și rulajele lui (NULL = numai solduri
-- finale). Firmele existente: core/migrare_balanta_rulaje_an.py.
ALTER TABLE TENANT_PLACEHOLDER.solduri_initiale ADD COLUMN IF NOT EXISTS si_an_debit numeric(15,2);
ALTER TABLE TENANT_PLACEHOLDER.solduri_initiale ADD COLUMN IF NOT EXISTS si_an_credit numeric(15,2);
ALTER TABLE TENANT_PLACEHOLDER.solduri_initiale ADD COLUMN IF NOT EXISTS rulaj_an_debit numeric(15,2);
ALTER TABLE TENANT_PLACEHOLDER.solduri_initiale ADD COLUMN IF NOT EXISTS rulaj_an_credit numeric(15,2);

-- [deficiența 428, lotul 10, 20.10.2026] perioadele sistemului TVA la încasare (CF art.282 alin.(3), (3^1), (5), (7)).
-- Firmele existente: core/migrare_tva_incasare_perioade.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.tva_incasare_perioade (id serial PRIMARY KEY, de_la date NOT NULL, pana_la date, sursa text NOT NULL DEFAULT 'manual' CHECK (sursa IN ('manual', 'anaf')), verificat_anaf_la timestamptz, stare_anaf text, creat_la timestamptz NOT NULL DEFAULT now(), CHECK (pana_la IS NULL OR pana_la >= de_la));

-- [deficiența 429, lotul 10, 20.10.2026] reevaluarea lunară a soldurilor în valută (OMFP 1802/2014 pct.325), un rând pe element.
-- Firmele existente: core/migrare_reevaluari_valuta.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.reevaluari_valuta (id serial PRIMARY KEY, data date NOT NULL, inregistrare_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE CASCADE, factura_id integer REFERENCES TENANT_PLACEHOLDER.facturi(id) ON DELETE CASCADE, cont text NOT NULL, moneda text NOT NULL, sold_valuta numeric(15,2) NOT NULL, curs_vechi numeric NOT NULL, curs_nou numeric NOT NULL, diferenta numeric(15,2) NOT NULL, creat_la timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS reevaluari_valuta_factura ON TENANT_PLACEHOLDER.reevaluari_valuta (factura_id, data);
ALTER TABLE TENANT_PLACEHOLDER.reevaluari_valuta ADD COLUMN IF NOT EXISTS sursa text NOT NULL DEFAULT 'propunere' CHECK (sursa IN ('propunere', 'manual'));
-- [deficiența 429, lotul 11, decizia Costin 10.3] reevaluarea pe PARTENER (cheia lui: CUI fără RO / „~NUME”), contul ajustat manual în
-- același formular și clauza valutară în lei (768 / 668, OMFP 1802/2014 pct.325 alin.(3)). Firmele existente:
-- core/migrare_reevaluare_partener.py.
ALTER TABLE TENANT_PLACEHOLDER.reevaluari_valuta ADD COLUMN IF NOT EXISTS partener text;
ALTER TABLE TENANT_PLACEHOLDER.reevaluari_valuta ADD COLUMN IF NOT EXISTS manual boolean NOT NULL DEFAULT false;
ALTER TABLE TENANT_PLACEHOLDER.reevaluari_valuta ADD COLUMN IF NOT EXISTS clauza boolean NOT NULL DEFAULT false;
CREATE INDEX IF NOT EXISTS reevaluari_valuta_partener ON TENANT_PLACEHOLDER.reevaluari_valuta (partener, cont, moneda, data);

-- [deficiența 428, lotul 10, deciziile Costin 20.10.2026] compensările de creanțe și datorii (o factură emisă stinsă cu o factură primită,
-- același partener; mută TVA-ul la încasare prin același punct ca banca și casa) și beneficiarul afiliat (CF art.282 alin.(6) lit.d).
-- Firmele existente: core/migrare_compensari_afiliat.py.
CREATE TABLE IF NOT EXISTS TENANT_PLACEHOLDER.compensari (id serial PRIMARY KEY, data date NOT NULL, factura_emisa_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.facturi(id), factura_primita_id integer NOT NULL REFERENCES TENANT_PLACEHOLDER.facturi(id), suma numeric(15,2) NOT NULL CHECK (suma > 0), inregistrare_id integer REFERENCES TENANT_PLACEHOLDER.inregistrari(id) ON DELETE CASCADE, document_ref text, creat_la timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS compensari_emisa ON TENANT_PLACEHOLDER.compensari (factura_emisa_id);
CREATE INDEX IF NOT EXISTS compensari_primita ON TENANT_PLACEHOLDER.compensari (factura_primita_id);
ALTER TABLE TENANT_PLACEHOLDER.clienti ADD COLUMN IF NOT EXISTS afiliat boolean NOT NULL DEFAULT false;
ALTER TABLE TENANT_PLACEHOLDER.facturi ADD COLUMN IF NOT EXISTS beneficiar_afiliat boolean NOT NULL DEFAULT false;

-- [C69, lotul 10, deciziile Costin 20.10.2026] câmpurile firmei cerute de bilanț (mare contribuabil, forma de proprietate) și de D406
-- (fără cont bancar), până acum inventate. Firmele existente: core/migrare_profil_c69.py.
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS mare_contribuabil boolean;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS forma_proprietate text;
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS fara_cont_bancar boolean NOT NULL DEFAULT false;

-- [deficiența 434, lotul 10, comanda Costin 10.2 pct.4] „Numerotarea borderourilor e unică și continuă”: numărul borderoului de achiziție e
-- unic în anul lui (aceeași formă ca verificarea din aplicație). Firmele existente: core/migrare_borderou_numar_unic.py.
CREATE UNIQUE INDEX IF NOT EXISTS facturi_borderou_numar_an_uniq ON TENANT_PLACEHOLDER.facturi (upper(btrim(numar)), (EXTRACT(YEAR FROM data_emitere))) WHERE tip = 'borderou';

-- [lotul 11, deficiența 449] categoria cotei 0% a produsului (taxare inversă / scutit cu sau fără drept / neimpozabil) și bunul cu taxare
-- inversă (codul D394). Firmele existente: core/migrare_produse_categorie_tva.py (sursa valorilor admise).
ALTER TABLE TENANT_PLACEHOLDER.produse ADD COLUMN IF NOT EXISTS categorie_tva text;
ALTER TABLE TENANT_PLACEHOLDER.produse ADD COLUMN IF NOT EXISTS categorie_331 text;
ALTER TABLE TENANT_PLACEHOLDER.produse DROP CONSTRAINT IF EXISTS produse_categorie_tva_check;
ALTER TABLE TENANT_PLACEHOLDER.produse ADD CONSTRAINT produse_categorie_tva_check CHECK ((categorie_tva IS NULL OR (cota_tva = 0 AND categorie_tva IN ('taxare_inversa', 'scutit_cu_drept', 'scutit_fara_drept', 'in_afara_sferei'))) AND (categorie_331 IS NULL OR (categorie_tva = 'taxare_inversa' AND categorie_331 IN ('1001', '1002', '1003', '1004', '1005', '10086000', '1201', '120400', '1205', '120600', '121291', 'deseuri', 'masa_lemnoasa', 'certificate_emisii', 'energie_electrica', 'certificate_verzi', 'cladiri_terenuri', 'aur_investitii', 'telefoane', 'circuite_integrate', 'console_tablete', 'gaze_naturale'))));

-- [lotul 11, decizia Costin 10.3 pct.4] „Borderoul se corectează prin stornare, ca factura.”: un borderou se stornează o singură dată.
-- Firmele existente: core/migrare_borderou_storno_unic.py.
CREATE UNIQUE INDEX IF NOT EXISTS facturi_borderou_storno_uniq ON TENANT_PLACEHOLDER.facturi (storno_din_id) WHERE tip = 'borderou' AND storno_din_id IS NOT NULL;

-- [lotul 11, decizia Costin 10.3 pct.4] „interesul public în Date firmă” — bilanțul: „15. interes_public … DA interes_public=(0,1)”
-- (structura SC 1225); NULL = nedeclarat -> bilanțul se oprește. Firmele existente: core/migrare_intocmitor_bilant.py.
ALTER TABLE TENANT_PLACEHOLDER.firma_profil ADD COLUMN IF NOT EXISTS interes_public boolean;

-- [cui_fara_ro_v1, lotul 11, decizia Costin 10.3] CUI-ul fără „RO” și fără spații — SURSA: core/migrare_cui_fara_ro.py
CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.cui_stocare(v text) RETURNS text AS $$
  SELECT CASE WHEN v IS NULL OR btrim(v) = '' THEN v ELSE regexp_replace(regexp_replace(upper(v), '[\s\u0085\u00a0\u2007\u202f\u001c-\u001f]', '', 'g'), '^RO([0-9]+)$', '\1') END
$$ LANGUAGE sql IMMUTABLE;
CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza() RETURNS trigger AS $$
DECLARE c text; v text; n text; j jsonb := '{}'::jsonb;
BEGIN
  FOREACH c IN ARRAY TG_ARGV LOOP
    v := to_jsonb(NEW) ->> c;
    n := TENANT_PLACEHOLDER.cui_stocare(v);
    IF n IS DISTINCT FROM v THEN j := j || jsonb_build_object(c, n); END IF;
  END LOOP;
  IF j <> '{}'::jsonb THEN NEW := jsonb_populate_record(NEW, j); END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza_factura() RETURNS trigger AS $$
BEGIN
  IF NEW.tert_platitor_tva IS NULL AND regexp_replace(upper(COALESCE(NEW.tert_cui, '')), '[\s\u0085\u00a0\u2007\u202f\u001c-\u001f]', '', 'g') ~ '^RO[0-9]+$' THEN
    NEW.tert_platitor_tva := true;
  END IF;
  NEW.tert_cui := TENANT_PLACEHOLDER.cui_stocare(NEW.tert_cui);
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.clienti;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui ON TENANT_PLACEHOLDER.clienti FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.furnizori;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui ON TENANT_PLACEHOLDER.furnizori FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.firma_profil;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui ON TENANT_PLACEHOLDER.firma_profil FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.solduri_parteneri;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui ON TENANT_PLACEHOLDER.solduri_parteneri FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.facturi;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF tert_cui ON TENANT_PLACEHOLDER.facturi FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza_factura();
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.facturi_recurente;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF tert_cui ON TENANT_PLACEHOLDER.facturi_recurente FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('tert_cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.casa_operatiuni;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui ON TENANT_PLACEHOLDER.casa_operatiuni FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.bonuri;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui ON TENANT_PLACEHOLDER.bonuri FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.chitante;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF client_cui ON TENANT_PLACEHOLDER.chitante FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('client_cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.nir;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui ON TENANT_PLACEHOLDER.nir FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.inregistrari_linii;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF partener_cui ON TENANT_PLACEHOLDER.inregistrari_linii FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('partener_cui');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.efactura_primite;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cif_emitent, cif_beneficiar ON TENANT_PLACEHOLDER.efactura_primite FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cif_emitent', 'cif_beneficiar');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.extras_linii;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cui_detectat ON TENANT_PLACEHOLDER.extras_linii FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cui_detectat');
DROP TRIGGER IF EXISTS trg_cui_fara_ro ON TENANT_PLACEHOLDER.asociati;
CREATE TRIGGER trg_cui_fara_ro BEFORE INSERT OR UPDATE OF cnp ON TENANT_PLACEHOLDER.asociati FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.cui_normalizeaza('cnp');
-- [cui_fara_ro_v1] sfârșit
