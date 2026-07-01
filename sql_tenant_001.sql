--
-- PostgreSQL database dump
--

\restrict AwF3J7YCqFPH3YVjU37NOp1qsyyHVpXYdIC2KWJuc0H3hTRFwm147znnRfsKwsc

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
-- Name: tenant_001; Type: SCHEMA; Schema: -; Owner: iconta_user
--

CREATE SCHEMA tenant_001;


ALTER SCHEMA tenant_001 OWNER TO iconta_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: articole; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.articole (
    id integer NOT NULL,
    cod text,
    denumire text NOT NULL,
    um text DEFAULT 'buc'::text,
    cont_stoc text DEFAULT '371'::text,
    cota_tva numeric DEFAULT 19,
    gestiune_id integer,
    pret_ref numeric DEFAULT 0,
    activ boolean DEFAULT true,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.articole OWNER TO iconta_user;

--
-- Name: articole_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.articole_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.articole_id_seq OWNER TO iconta_user;

--
-- Name: articole_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.articole_id_seq OWNED BY tenant_001.articole.id;


--
-- Name: asociati; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.asociati (
    id integer NOT NULL,
    nume text,
    cnp text,
    cota numeric DEFAULT 0,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.asociati OWNER TO iconta_user;

--
-- Name: asociati_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.asociati_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.asociati_id_seq OWNER TO iconta_user;

--
-- Name: asociati_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.asociati_id_seq OWNED BY tenant_001.asociati.id;


--
-- Name: avans_deconturi; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.avans_deconturi (
    id integer NOT NULL,
    avans_id integer NOT NULL,
    cont_cheltuiala text,
    descriere text,
    suma_neta numeric DEFAULT 0,
    cota_tva numeric DEFAULT 0,
    tva numeric DEFAULT 0,
    data date,
    document text,
    inregistrare_id integer,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.avans_deconturi OWNER TO iconta_user;

--
-- Name: avans_deconturi_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.avans_deconturi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.avans_deconturi_id_seq OWNER TO iconta_user;

--
-- Name: avans_deconturi_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.avans_deconturi_id_seq OWNED BY tenant_001.avans_deconturi.id;


--
-- Name: avansuri; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.avansuri (
    id integer NOT NULL,
    salariat_id integer,
    beneficiar text NOT NULL,
    suma_acordata numeric DEFAULT 0 NOT NULL,
    data_acordare date,
    sursa text DEFAULT '5311'::text,
    status text DEFAULT 'deschis'::text,
    inregistrare_id integer,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.avansuri OWNER TO iconta_user;

--
-- Name: avansuri_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.avansuri_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.avansuri_id_seq OWNER TO iconta_user;

--
-- Name: avansuri_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.avansuri_id_seq OWNED BY tenant_001.avansuri.id;


--
-- Name: casa_operatiuni; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.casa_operatiuni (
    id integer NOT NULL,
    data date,
    tip text NOT NULL,
    suma numeric DEFAULT 0 NOT NULL,
    descriere text,
    cont_corespondent text,
    document text,
    inregistrare_id integer,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.casa_operatiuni OWNER TO iconta_user;

--
-- Name: casa_operatiuni_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.casa_operatiuni_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.casa_operatiuni_id_seq OWNER TO iconta_user;

--
-- Name: casa_operatiuni_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.casa_operatiuni_id_seq OWNED BY tenant_001.casa_operatiuni.id;


--
-- Name: clienti; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.clienti (
    id integer NOT NULL,
    nume character varying(255) NOT NULL,
    cui character varying(20),
    adresa text,
    email character varying(255),
    telefon character varying(50),
    status character varying(20) DEFAULT 'activ'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    oras character varying(100),
    judet character varying(10),
    cod_postal character varying(20)
);


ALTER TABLE tenant_001.clienti OWNER TO iconta_user;

--
-- Name: clienti_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.clienti_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.clienti_id_seq OWNER TO iconta_user;

--
-- Name: clienti_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.clienti_id_seq OWNED BY tenant_001.clienti.id;


--
-- Name: concedii_medicale; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.concedii_medicale (
    id integer NOT NULL,
    salariat_id integer,
    an integer,
    luna integer,
    cod text,
    zile integer DEFAULT 0,
    indemnizatie numeric DEFAULT 0,
    creat timestamp without time zone DEFAULT now(),
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
    diagnostic text
);


ALTER TABLE tenant_001.concedii_medicale OWNER TO iconta_user;

--
-- Name: concedii_medicale_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.concedii_medicale_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.concedii_medicale_id_seq OWNER TO iconta_user;

--
-- Name: concedii_medicale_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.concedii_medicale_id_seq OWNED BY tenant_001.concedii_medicale.id;


--
-- Name: factura_linii; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.factura_linii (
    id integer NOT NULL,
    factura_id integer NOT NULL,
    descriere text NOT NULL,
    um character varying(10) DEFAULT 'buc'::character varying NOT NULL,
    cantitate numeric(12,3) DEFAULT 1 NOT NULL,
    pret_unitar numeric(12,2) DEFAULT 0 NOT NULL,
    cota_tva numeric(5,2) DEFAULT 21 NOT NULL
);


ALTER TABLE tenant_001.factura_linii OWNER TO iconta_user;

--
-- Name: factura_linii_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.factura_linii_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.factura_linii_id_seq OWNER TO iconta_user;

--
-- Name: factura_linii_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.factura_linii_id_seq OWNED BY tenant_001.factura_linii.id;


--
-- Name: facturi; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.facturi (
    id integer NOT NULL,
    client_id integer,
    numar character varying(50) NOT NULL,
    data_emitere date NOT NULL,
    data_scadenta date,
    total numeric(12,2) DEFAULT 0 NOT NULL,
    tva numeric(12,2) DEFAULT 0 NOT NULL,
    status character varying(20) DEFAULT 'emisa'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    moneda character varying(3) DEFAULT 'RON'::character varying NOT NULL,
    directie character varying(10) DEFAULT 'emisa'::character varying NOT NULL,
    xml text,
    tert_nume character varying(255),
    tert_cui character varying(30)
);


ALTER TABLE tenant_001.facturi OWNER TO iconta_user;

--
-- Name: facturi_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.facturi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.facturi_id_seq OWNER TO iconta_user;

--
-- Name: facturi_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.facturi_id_seq OWNED BY tenant_001.facturi.id;


--
-- Name: firma_profil; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.firma_profil (
    id integer DEFAULT 1 NOT NULL,
    nume character varying(255) NOT NULL,
    cui character varying(20) NOT NULL,
    reg_com character varying(50),
    adresa text,
    oras character varying(100),
    judet character varying(10),
    cod_postal character varying(20),
    iban character varying(34),
    email text,
    declarant_nume text,
    declarant_prenume text,
    declarant_functie text,
    banca text,
    caen text,
    tip_decont text,
    pro_rata numeric,
    patron_nume text,
    patron_email text,
    regim_fiscal text,
    platitor_tva boolean,
    operatiuni_ic boolean,
    logo text,
    telefon text,
    CONSTRAINT firma_profil_single CHECK ((id = 1))
);


ALTER TABLE tenant_001.firma_profil OWNER TO iconta_user;

--
-- Name: gestiuni; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.gestiuni (
    id integer NOT NULL,
    nume text NOT NULL,
    tip text DEFAULT 'depozit'::text,
    activ boolean DEFAULT true,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.gestiuni OWNER TO iconta_user;

--
-- Name: gestiuni_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.gestiuni_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.gestiuni_id_seq OWNER TO iconta_user;

--
-- Name: gestiuni_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.gestiuni_id_seq OWNED BY tenant_001.gestiuni.id;


--
-- Name: imobcurs_costuri; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.imobcurs_costuri (
    id integer NOT NULL,
    imobcurs_id integer NOT NULL,
    descriere text,
    cont_furnizor text DEFAULT '401'::text,
    suma_neta numeric DEFAULT 0,
    cota_tva numeric DEFAULT 0,
    tva numeric DEFAULT 0,
    data date,
    document text,
    inregistrare_id integer,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.imobcurs_costuri OWNER TO iconta_user;

--
-- Name: imobcurs_costuri_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.imobcurs_costuri_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.imobcurs_costuri_id_seq OWNER TO iconta_user;

--
-- Name: imobcurs_costuri_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.imobcurs_costuri_id_seq OWNED BY tenant_001.imobcurs_costuri.id;


--
-- Name: imobilizari_curs; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.imobilizari_curs (
    id integer NOT NULL,
    denumire text NOT NULL,
    cont text DEFAULT '231'::text,
    status text DEFAULT 'in_curs'::text,
    mijloc_fix_id integer,
    data_start date,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.imobilizari_curs OWNER TO iconta_user;

--
-- Name: imobilizari_curs_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.imobilizari_curs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.imobilizari_curs_id_seq OWNER TO iconta_user;

--
-- Name: imobilizari_curs_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.imobilizari_curs_id_seq OWNED BY tenant_001.imobilizari_curs.id;


--
-- Name: inregistrari; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.inregistrari (
    id integer NOT NULL,
    data date NOT NULL,
    numar character varying(50),
    factura_id integer,
    document_ref character varying(255),
    descriere text,
    sursa text,
    status character varying(20) DEFAULT 'ciorna'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.inregistrari OWNER TO iconta_user;

--
-- Name: inregistrari_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.inregistrari_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.inregistrari_id_seq OWNER TO iconta_user;

--
-- Name: inregistrari_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.inregistrari_id_seq OWNED BY tenant_001.inregistrari.id;


--
-- Name: inregistrari_linii; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.inregistrari_linii (
    id integer NOT NULL,
    inregistrare_id integer NOT NULL,
    cont_debit character varying(10) NOT NULL,
    cont_credit character varying(10) NOT NULL,
    suma numeric(14,2) NOT NULL
);


ALTER TABLE tenant_001.inregistrari_linii OWNER TO iconta_user;

--
-- Name: inregistrari_linii_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.inregistrari_linii_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.inregistrari_linii_id_seq OWNER TO iconta_user;

--
-- Name: inregistrari_linii_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.inregistrari_linii_id_seq OWNED BY tenant_001.inregistrari_linii.id;


--
-- Name: leasing_contracte; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.leasing_contracte (
    id integer NOT NULL,
    denumire text NOT NULL,
    tip text DEFAULT 'financiar'::text,
    furnizor text DEFAULT '404'::text,
    valoare numeric DEFAULT 0,
    avans numeric DEFAULT 0,
    dobanda_anuala numeric DEFAULT 0,
    nr_rate integer DEFAULT 0,
    reziduala numeric DEFAULT 0,
    cont_bun text DEFAULT '2133'::text,
    cont_amortizare text DEFAULT '2813'::text,
    cota_tva numeric DEFAULT 19,
    data_start date,
    status text DEFAULT 'activ'::text,
    mijloc_fix_id integer,
    initiat boolean DEFAULT false,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.leasing_contracte OWNER TO iconta_user;

--
-- Name: leasing_contracte_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.leasing_contracte_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.leasing_contracte_id_seq OWNER TO iconta_user;

--
-- Name: leasing_contracte_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.leasing_contracte_id_seq OWNED BY tenant_001.leasing_contracte.id;


--
-- Name: leasing_rate; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.leasing_rate (
    id integer NOT NULL,
    contract_id integer NOT NULL,
    idx integer,
    scadenta date,
    rata numeric DEFAULT 0,
    principal numeric DEFAULT 0,
    dobanda numeric DEFAULT 0,
    sold numeric DEFAULT 0,
    tva numeric DEFAULT 0,
    platita boolean DEFAULT false,
    inregistrare_id integer,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.leasing_rate OWNER TO iconta_user;

--
-- Name: leasing_rate_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.leasing_rate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.leasing_rate_id_seq OWNER TO iconta_user;

--
-- Name: leasing_rate_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.leasing_rate_id_seq OWNED BY tenant_001.leasing_rate.id;


--
-- Name: mf_amortizari; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.mf_amortizari (
    id integer NOT NULL,
    mijloc_id integer NOT NULL,
    luna_idx integer,
    perioada text,
    amortizare numeric,
    cumulat numeric,
    ramas numeric,
    inregistrare_id integer,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.mf_amortizari OWNER TO iconta_user;

--
-- Name: mf_amortizari_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.mf_amortizari_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.mf_amortizari_id_seq OWNER TO iconta_user;

--
-- Name: mf_amortizari_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.mf_amortizari_id_seq OWNED BY tenant_001.mf_amortizari.id;


--
-- Name: mijloace_fixe; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.mijloace_fixe (
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
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.mijloace_fixe OWNER TO iconta_user;

--
-- Name: mijloace_fixe_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.mijloace_fixe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.mijloace_fixe_id_seq OWNER TO iconta_user;

--
-- Name: mijloace_fixe_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.mijloace_fixe_id_seq OWNED BY tenant_001.mijloace_fixe.id;


--
-- Name: salariati; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.salariati (
    id integer NOT NULL,
    cnp text,
    nume text,
    prenume text,
    data_angajare date,
    tip_norma text DEFAULT 'intreaga'::text,
    ore_zi numeric DEFAULT 8,
    salariu_brut numeric DEFAULT 0,
    persoane_intretinere integer DEFAULT 0,
    judet_casa text,
    activ boolean DEFAULT true,
    creat timestamp without time zone DEFAULT now(),
    scutit_contrib_minim boolean DEFAULT false,
    motiv_exceptare smallint,
    cor text
);


ALTER TABLE tenant_001.salariati OWNER TO iconta_user;

--
-- Name: salariati_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.salariati_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.salariati_id_seq OWNER TO iconta_user;

--
-- Name: salariati_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.salariati_id_seq OWNED BY tenant_001.salariati.id;


--
-- Name: stoc_miscari; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.stoc_miscari (
    id integer NOT NULL,
    articol_id integer NOT NULL,
    gestiune_id integer,
    tip text NOT NULL,
    cantitate numeric DEFAULT 0 NOT NULL,
    pret_unitar numeric DEFAULT 0 NOT NULL,
    valoare numeric DEFAULT 0 NOT NULL,
    data date,
    document text,
    inregistrare_id integer,
    creat timestamp without time zone DEFAULT now()
);


ALTER TABLE tenant_001.stoc_miscari OWNER TO iconta_user;

--
-- Name: stoc_miscari_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

CREATE SEQUENCE tenant_001.stoc_miscari_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_001.stoc_miscari_id_seq OWNER TO iconta_user;

--
-- Name: stoc_miscari_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_001; Owner: iconta_user
--

ALTER SEQUENCE tenant_001.stoc_miscari_id_seq OWNED BY tenant_001.stoc_miscari.id;


--
-- Name: articole id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.articole ALTER COLUMN id SET DEFAULT nextval('tenant_001.articole_id_seq'::regclass);


--
-- Name: asociati id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.asociati ALTER COLUMN id SET DEFAULT nextval('tenant_001.asociati_id_seq'::regclass);


--
-- Name: avans_deconturi id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.avans_deconturi ALTER COLUMN id SET DEFAULT nextval('tenant_001.avans_deconturi_id_seq'::regclass);


--
-- Name: avansuri id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.avansuri ALTER COLUMN id SET DEFAULT nextval('tenant_001.avansuri_id_seq'::regclass);


--
-- Name: casa_operatiuni id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.casa_operatiuni ALTER COLUMN id SET DEFAULT nextval('tenant_001.casa_operatiuni_id_seq'::regclass);


--
-- Name: clienti id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.clienti ALTER COLUMN id SET DEFAULT nextval('tenant_001.clienti_id_seq'::regclass);


--
-- Name: concedii_medicale id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.concedii_medicale ALTER COLUMN id SET DEFAULT nextval('tenant_001.concedii_medicale_id_seq'::regclass);


--
-- Name: factura_linii id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.factura_linii ALTER COLUMN id SET DEFAULT nextval('tenant_001.factura_linii_id_seq'::regclass);


--
-- Name: facturi id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.facturi ALTER COLUMN id SET DEFAULT nextval('tenant_001.facturi_id_seq'::regclass);


--
-- Name: gestiuni id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.gestiuni ALTER COLUMN id SET DEFAULT nextval('tenant_001.gestiuni_id_seq'::regclass);


--
-- Name: imobcurs_costuri id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.imobcurs_costuri ALTER COLUMN id SET DEFAULT nextval('tenant_001.imobcurs_costuri_id_seq'::regclass);


--
-- Name: imobilizari_curs id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.imobilizari_curs ALTER COLUMN id SET DEFAULT nextval('tenant_001.imobilizari_curs_id_seq'::regclass);


--
-- Name: inregistrari id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.inregistrari ALTER COLUMN id SET DEFAULT nextval('tenant_001.inregistrari_id_seq'::regclass);


--
-- Name: inregistrari_linii id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.inregistrari_linii ALTER COLUMN id SET DEFAULT nextval('tenant_001.inregistrari_linii_id_seq'::regclass);


--
-- Name: leasing_contracte id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.leasing_contracte ALTER COLUMN id SET DEFAULT nextval('tenant_001.leasing_contracte_id_seq'::regclass);


--
-- Name: leasing_rate id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.leasing_rate ALTER COLUMN id SET DEFAULT nextval('tenant_001.leasing_rate_id_seq'::regclass);


--
-- Name: mf_amortizari id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.mf_amortizari ALTER COLUMN id SET DEFAULT nextval('tenant_001.mf_amortizari_id_seq'::regclass);


--
-- Name: mijloace_fixe id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.mijloace_fixe ALTER COLUMN id SET DEFAULT nextval('tenant_001.mijloace_fixe_id_seq'::regclass);


--
-- Name: salariati id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.salariati ALTER COLUMN id SET DEFAULT nextval('tenant_001.salariati_id_seq'::regclass);


--
-- Name: stoc_miscari id; Type: DEFAULT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.stoc_miscari ALTER COLUMN id SET DEFAULT nextval('tenant_001.stoc_miscari_id_seq'::regclass);


--
-- Name: articole articole_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.articole
    ADD CONSTRAINT articole_pkey PRIMARY KEY (id);


--
-- Name: asociati asociati_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.asociati
    ADD CONSTRAINT asociati_pkey PRIMARY KEY (id);


--
-- Name: avans_deconturi avans_deconturi_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.avans_deconturi
    ADD CONSTRAINT avans_deconturi_pkey PRIMARY KEY (id);


--
-- Name: avansuri avansuri_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.avansuri
    ADD CONSTRAINT avansuri_pkey PRIMARY KEY (id);


--
-- Name: casa_operatiuni casa_operatiuni_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.casa_operatiuni
    ADD CONSTRAINT casa_operatiuni_pkey PRIMARY KEY (id);


--
-- Name: clienti clienti_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.clienti
    ADD CONSTRAINT clienti_pkey PRIMARY KEY (id);


--
-- Name: concedii_medicale concedii_medicale_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.concedii_medicale
    ADD CONSTRAINT concedii_medicale_pkey PRIMARY KEY (id);


--
-- Name: factura_linii factura_linii_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.factura_linii
    ADD CONSTRAINT factura_linii_pkey PRIMARY KEY (id);


--
-- Name: facturi facturi_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.facturi
    ADD CONSTRAINT facturi_pkey PRIMARY KEY (id);


--
-- Name: firma_profil firma_profil_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.firma_profil
    ADD CONSTRAINT firma_profil_pkey PRIMARY KEY (id);


--
-- Name: gestiuni gestiuni_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.gestiuni
    ADD CONSTRAINT gestiuni_pkey PRIMARY KEY (id);


--
-- Name: imobcurs_costuri imobcurs_costuri_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.imobcurs_costuri
    ADD CONSTRAINT imobcurs_costuri_pkey PRIMARY KEY (id);


--
-- Name: imobilizari_curs imobilizari_curs_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.imobilizari_curs
    ADD CONSTRAINT imobilizari_curs_pkey PRIMARY KEY (id);


--
-- Name: inregistrari_linii inregistrari_linii_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.inregistrari_linii
    ADD CONSTRAINT inregistrari_linii_pkey PRIMARY KEY (id);


--
-- Name: inregistrari inregistrari_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.inregistrari
    ADD CONSTRAINT inregistrari_pkey PRIMARY KEY (id);


--
-- Name: leasing_contracte leasing_contracte_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.leasing_contracte
    ADD CONSTRAINT leasing_contracte_pkey PRIMARY KEY (id);


--
-- Name: leasing_rate leasing_rate_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.leasing_rate
    ADD CONSTRAINT leasing_rate_pkey PRIMARY KEY (id);


--
-- Name: mf_amortizari mf_amortizari_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.mf_amortizari
    ADD CONSTRAINT mf_amortizari_pkey PRIMARY KEY (id);


--
-- Name: mijloace_fixe mijloace_fixe_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.mijloace_fixe
    ADD CONSTRAINT mijloace_fixe_pkey PRIMARY KEY (id);


--
-- Name: salariati salariati_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.salariati
    ADD CONSTRAINT salariati_pkey PRIMARY KEY (id);


--
-- Name: stoc_miscari stoc_miscari_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.stoc_miscari
    ADD CONSTRAINT stoc_miscari_pkey PRIMARY KEY (id);


--
-- Name: factura_linii factura_linii_factura_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.factura_linii
    ADD CONSTRAINT factura_linii_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES tenant_001.facturi(id) ON DELETE CASCADE;


--
-- Name: facturi facturi_client_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.facturi
    ADD CONSTRAINT facturi_client_id_fkey FOREIGN KEY (client_id) REFERENCES tenant_001.clienti(id);


--
-- Name: inregistrari inregistrari_factura_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.inregistrari
    ADD CONSTRAINT inregistrari_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES tenant_001.facturi(id) ON DELETE SET NULL;


--
-- Name: inregistrari_linii inregistrari_linii_inregistrare_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.inregistrari_linii
    ADD CONSTRAINT inregistrari_linii_inregistrare_id_fkey FOREIGN KEY (inregistrare_id) REFERENCES tenant_001.inregistrari(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict AwF3J7YCqFPH3YVjU37NOp1qsyyHVpXYdIC2KWJuc0H3hTRFwm147znnRfsKwsc

