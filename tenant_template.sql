--
-- PostgreSQL database dump
--

\restrict dvt9E34bCyIEaT2f9va5jVBG5hp2AkVW6nOGSNUkpebHouWJAGAeyugWhRlFNqt

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
-- Name: tenant_001; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tenant_001;


ALTER SCHEMA tenant_001 OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: articole; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.articole (
    id integer NOT NULL,
    denumire character varying(255) NOT NULL,
    um character varying(20) DEFAULT 'buc'::character varying NOT NULL,
    cont_stoc character varying(10) DEFAULT '371'::character varying NOT NULL,
    cont_cheltuiala character varying(10) DEFAULT '607'::character varying NOT NULL,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.articole OWNER TO postgres;

--
-- Name: articole_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.articole ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.articole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: asociati; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.asociati (
    id integer NOT NULL,
    nume text,
    cnp text,
    cota numeric DEFAULT 0,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.asociati OWNER TO postgres;

--
-- Name: asociati_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.asociati ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.asociati_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: bonuri; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.bonuri (
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
    articole jsonb DEFAULT '[]'::jsonb
);


ALTER TABLE tenant_001.bonuri OWNER TO iconta_user;

--
-- Name: bonuri_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE tenant_001.bonuri ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.bonuri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: casa_operatiuni; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.casa_operatiuni (
    id integer NOT NULL,
    data date NOT NULL,
    tip character varying(10) NOT NULL,
    categorie character varying(30) NOT NULL,
    document character varying(50),
    partener character varying(255),
    cui character varying(30),
    suma numeric(12,2) NOT NULL,
    inregistrare_id integer,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.casa_operatiuni OWNER TO postgres;

--
-- Name: casa_operatiuni_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.casa_operatiuni ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.casa_operatiuni_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: clienti; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.clienti (
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


ALTER TABLE tenant_001.clienti OWNER TO postgres;

--
-- Name: clienti_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.clienti ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.clienti_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: concedii_medicale; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.concedii_medicale (
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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.concedii_medicale OWNER TO postgres;

--
-- Name: concedii_medicale_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.concedii_medicale ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.concedii_medicale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: extras_linii; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.extras_linii (
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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.extras_linii OWNER TO postgres;

--
-- Name: extras_linii_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.extras_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.extras_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: factura_linii; Type: TABLE; Schema: tenant_001; Owner: postgres
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


ALTER TABLE tenant_001.factura_linii OWNER TO postgres;

--
-- Name: factura_linii_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.factura_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.factura_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: facturi; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.facturi (
    id integer NOT NULL,
    client_id integer,
    numar character varying(50) NOT NULL,
    data_emitere date NOT NULL,
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
    curs_bnr numeric(12,4),
    tva_lei numeric(12,2),
    total_lei numeric(12,2),
    data_curs date,
    curs_sursa character varying(10),
    tert_adresa text
);


ALTER TABLE tenant_001.facturi OWNER TO postgres;

--
-- Name: facturi_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.facturi ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.facturi_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: firma_profil; Type: TABLE; Schema: tenant_001; Owner: postgres
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
    banca text,
    email text,
    telefon text,
    caen text,
    declarant_nume text,
    declarant_prenume text,
    declarant_functie text,
    patron_nume text,
    patron_email text,
    logo text,
    tip_decont text,
    pro_rata numeric,
    regim_fiscal text,
    platitor_tva boolean,
    operatiuni_ic boolean,
    serie_factura character varying(10),
    urmator_numar_factura integer DEFAULT 1 NOT NULL,
    font_factura character varying(30) DEFAULT 'sans'::character varying,
    culoare_factura character varying(10) DEFAULT '#1d4ed8'::character varying,
    CONSTRAINT firma_profil_singleton CHECK ((id = 1))
);


ALTER TABLE tenant_001.firma_profil OWNER TO postgres;

--
-- Name: furnizori; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.furnizori (
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


ALTER TABLE tenant_001.furnizori OWNER TO postgres;

--
-- Name: furnizori_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.furnizori ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.furnizori_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: inregistrari; Type: TABLE; Schema: tenant_001; Owner: postgres
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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.inregistrari OWNER TO postgres;

--
-- Name: inregistrari_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.inregistrari ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.inregistrari_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: inregistrari_linii; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.inregistrari_linii (
    id integer NOT NULL,
    inregistrare_id integer NOT NULL,
    cont_debit character varying(10) NOT NULL,
    cont_credit character varying(10) NOT NULL,
    suma numeric(14,2) NOT NULL
);


ALTER TABLE tenant_001.inregistrari_linii OWNER TO postgres;

--
-- Name: inregistrari_linii_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.inregistrari_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.inregistrari_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: mijloace_fixe; Type: TABLE; Schema: tenant_001; Owner: postgres
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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.mijloace_fixe OWNER TO postgres;

--
-- Name: mijloace_fixe_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.mijloace_fixe ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.mijloace_fixe_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: miscari_stoc; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.miscari_stoc (
    id integer NOT NULL,
    articol_id integer NOT NULL,
    data date NOT NULL,
    tip character varying(10) NOT NULL,
    cantitate numeric(12,3) NOT NULL,
    pret_unitar numeric(12,4),
    valoare numeric(12,2) NOT NULL,
    document character varying(100),
    inregistrare_id integer,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.miscari_stoc OWNER TO postgres;

--
-- Name: miscari_stoc_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.miscari_stoc ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.miscari_stoc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: nir; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.nir (
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
    inregistrari_ids jsonb,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.nir OWNER TO postgres;

--
-- Name: nir_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.nir ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.nir_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: nir_linii; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.nir_linii (
    id integer NOT NULL,
    nir_id integer NOT NULL,
    denumire character varying(255) NOT NULL,
    cantitate numeric(12,3) NOT NULL,
    pret_achizitie numeric(12,4) NOT NULL,
    pret_vanzare numeric(12,4) NOT NULL,
    cota_tva numeric(5,2) DEFAULT 21 NOT NULL
);


ALTER TABLE tenant_001.nir_linii OWNER TO postgres;

--
-- Name: nir_linii_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.nir_linii ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.nir_linii_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: plan_conturi; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.plan_conturi (
    simbol character varying(10) NOT NULL,
    denumire text NOT NULL,
    tip character varying(20) DEFAULT 'Bifunctional'::character varying,
    sold_debitor numeric(15,2) DEFAULT 0,
    sold_creditor numeric(15,2) DEFAULT 0
);


ALTER TABLE tenant_001.plan_conturi OWNER TO postgres;

--
-- Name: produse; Type: TABLE; Schema: tenant_001; Owner: iconta_user
--

CREATE TABLE tenant_001.produse (
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


ALTER TABLE tenant_001.produse OWNER TO iconta_user;

--
-- Name: produse_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE tenant_001.produse ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.produse_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: salariati; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.salariati (
    id integer NOT NULL,
    cnp text,
    nif text,
    nume text,
    prenume text,
    data_angajare date,
    data_asigurat date,
    part_time boolean DEFAULT false,
    ore_zi numeric DEFAULT 8,
    salariu_brut numeric DEFAULT 0,
    persoane_intretinere integer DEFAULT 0,
    judet_casa text,
    cor text,
    tip_asigurat text,
    scutit_contrib_minim boolean DEFAULT false,
    motiv_exceptare smallint,
    activ boolean DEFAULT true,
    creat_la timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE tenant_001.salariati OWNER TO postgres;

--
-- Name: salariati_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.salariati ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.salariati_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: solduri_initiale; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.solduri_initiale (
    id integer NOT NULL,
    cont text NOT NULL,
    denumire text DEFAULT ''::text NOT NULL,
    sold_debitor numeric(15,2) DEFAULT 0 NOT NULL,
    sold_creditor numeric(15,2) DEFAULT 0 NOT NULL,
    data_referinta date
);


ALTER TABLE tenant_001.solduri_initiale OWNER TO postgres;

--
-- Name: solduri_initiale_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.solduri_initiale ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.solduri_initiale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: solduri_parteneri; Type: TABLE; Schema: tenant_001; Owner: postgres
--

CREATE TABLE tenant_001.solduri_parteneri (
    id integer NOT NULL,
    cont text NOT NULL,
    cui text DEFAULT ''::text NOT NULL,
    denumire text DEFAULT ''::text NOT NULL,
    sold_debitor numeric(15,2) DEFAULT 0 NOT NULL,
    sold_creditor numeric(15,2) DEFAULT 0 NOT NULL,
    data_referinta date
);


ALTER TABLE tenant_001.solduri_parteneri OWNER TO postgres;

--
-- Name: solduri_parteneri_id_seq; Type: SEQUENCE; Schema: tenant_001; Owner: postgres
--

ALTER TABLE tenant_001.solduri_parteneri ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME tenant_001.solduri_parteneri_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: articole articole_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.articole
    ADD CONSTRAINT articole_pkey PRIMARY KEY (id);


--
-- Name: asociati asociati_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.asociati
    ADD CONSTRAINT asociati_pkey PRIMARY KEY (id);


--
-- Name: bonuri bonuri_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.bonuri
    ADD CONSTRAINT bonuri_pkey PRIMARY KEY (id);


--
-- Name: casa_operatiuni casa_operatiuni_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.casa_operatiuni
    ADD CONSTRAINT casa_operatiuni_pkey PRIMARY KEY (id);


--
-- Name: clienti clienti_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.clienti
    ADD CONSTRAINT clienti_pkey PRIMARY KEY (id);


--
-- Name: concedii_medicale concedii_medicale_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.concedii_medicale
    ADD CONSTRAINT concedii_medicale_pkey PRIMARY KEY (id);


--
-- Name: extras_linii extras_linii_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.extras_linii
    ADD CONSTRAINT extras_linii_pkey PRIMARY KEY (id);


--
-- Name: factura_linii factura_linii_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.factura_linii
    ADD CONSTRAINT factura_linii_pkey PRIMARY KEY (id);


--
-- Name: facturi facturi_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.facturi
    ADD CONSTRAINT facturi_pkey PRIMARY KEY (id);


--
-- Name: firma_profil firma_profil_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.firma_profil
    ADD CONSTRAINT firma_profil_pkey PRIMARY KEY (id);


--
-- Name: furnizori furnizori_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.furnizori
    ADD CONSTRAINT furnizori_pkey PRIMARY KEY (id);


--
-- Name: inregistrari_linii inregistrari_linii_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.inregistrari_linii
    ADD CONSTRAINT inregistrari_linii_pkey PRIMARY KEY (id);


--
-- Name: inregistrari inregistrari_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.inregistrari
    ADD CONSTRAINT inregistrari_pkey PRIMARY KEY (id);


--
-- Name: mijloace_fixe mijloace_fixe_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.mijloace_fixe
    ADD CONSTRAINT mijloace_fixe_pkey PRIMARY KEY (id);


--
-- Name: miscari_stoc miscari_stoc_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.miscari_stoc
    ADD CONSTRAINT miscari_stoc_pkey PRIMARY KEY (id);


--
-- Name: nir_linii nir_linii_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.nir_linii
    ADD CONSTRAINT nir_linii_pkey PRIMARY KEY (id);


--
-- Name: nir nir_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.nir
    ADD CONSTRAINT nir_pkey PRIMARY KEY (id);


--
-- Name: plan_conturi plan_conturi_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.plan_conturi
    ADD CONSTRAINT plan_conturi_pkey PRIMARY KEY (simbol);


--
-- Name: produse produse_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: iconta_user
--

ALTER TABLE ONLY tenant_001.produse
    ADD CONSTRAINT produse_pkey PRIMARY KEY (id);


--
-- Name: salariati salariati_cnp_uniq; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.salariati
    ADD CONSTRAINT salariati_cnp_uniq UNIQUE (cnp);


--
-- Name: salariati salariati_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.salariati
    ADD CONSTRAINT salariati_pkey PRIMARY KEY (id);


--
-- Name: solduri_initiale solduri_initiale_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.solduri_initiale
    ADD CONSTRAINT solduri_initiale_pkey PRIMARY KEY (id);


--
-- Name: solduri_parteneri solduri_parteneri_pkey; Type: CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.solduri_parteneri
    ADD CONSTRAINT solduri_parteneri_pkey PRIMARY KEY (id);


--
-- Name: produse_denumire_idx; Type: INDEX; Schema: tenant_001; Owner: iconta_user
--

CREATE INDEX produse_denumire_idx ON tenant_001.produse USING btree (lower(denumire));


--
-- Name: concedii_medicale concedii_medicale_salariat_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.concedii_medicale
    ADD CONSTRAINT concedii_medicale_salariat_id_fkey FOREIGN KEY (salariat_id) REFERENCES tenant_001.salariati(id) ON DELETE CASCADE;


--
-- Name: factura_linii factura_linii_factura_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.factura_linii
    ADD CONSTRAINT factura_linii_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES tenant_001.facturi(id) ON DELETE CASCADE;


--
-- Name: facturi facturi_client_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.facturi
    ADD CONSTRAINT facturi_client_id_fkey FOREIGN KEY (client_id) REFERENCES tenant_001.clienti(id);


--
-- Name: inregistrari inregistrari_factura_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.inregistrari
    ADD CONSTRAINT inregistrari_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES tenant_001.facturi(id);


--
-- Name: inregistrari_linii inregistrari_linii_inregistrare_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.inregistrari_linii
    ADD CONSTRAINT inregistrari_linii_inregistrare_id_fkey FOREIGN KEY (inregistrare_id) REFERENCES tenant_001.inregistrari(id) ON DELETE CASCADE;


--
-- Name: miscari_stoc miscari_stoc_articol_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.miscari_stoc
    ADD CONSTRAINT miscari_stoc_articol_id_fkey FOREIGN KEY (articol_id) REFERENCES tenant_001.articole(id);


--
-- Name: nir_linii nir_linii_nir_id_fkey; Type: FK CONSTRAINT; Schema: tenant_001; Owner: postgres
--

ALTER TABLE ONLY tenant_001.nir_linii
    ADD CONSTRAINT nir_linii_nir_id_fkey FOREIGN KEY (nir_id) REFERENCES tenant_001.nir(id) ON DELETE CASCADE;


--
-- Name: SCHEMA tenant_001; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA tenant_001 TO iconta_user;


--
-- Name: TABLE articole; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.articole TO iconta_user;


--
-- Name: TABLE asociati; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.asociati TO iconta_user;


--
-- Name: SEQUENCE asociati_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.asociati_id_seq TO iconta_user;


--
-- Name: TABLE casa_operatiuni; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.casa_operatiuni TO iconta_user;


--
-- Name: TABLE clienti; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.clienti TO iconta_user;


--
-- Name: SEQUENCE clienti_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.clienti_id_seq TO iconta_user;


--
-- Name: TABLE concedii_medicale; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.concedii_medicale TO iconta_user;


--
-- Name: SEQUENCE concedii_medicale_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.concedii_medicale_id_seq TO iconta_user;


--
-- Name: TABLE extras_linii; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.extras_linii TO iconta_user;


--
-- Name: TABLE factura_linii; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.factura_linii TO iconta_user;


--
-- Name: SEQUENCE factura_linii_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.factura_linii_id_seq TO iconta_user;


--
-- Name: TABLE facturi; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.facturi TO iconta_user;


--
-- Name: SEQUENCE facturi_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.facturi_id_seq TO iconta_user;


--
-- Name: TABLE firma_profil; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.firma_profil TO iconta_user;


--
-- Name: TABLE furnizori; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.furnizori TO iconta_user;


--
-- Name: SEQUENCE furnizori_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.furnizori_id_seq TO iconta_user;


--
-- Name: TABLE inregistrari; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.inregistrari TO iconta_user;


--
-- Name: SEQUENCE inregistrari_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.inregistrari_id_seq TO iconta_user;


--
-- Name: TABLE inregistrari_linii; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.inregistrari_linii TO iconta_user;


--
-- Name: SEQUENCE inregistrari_linii_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.inregistrari_linii_id_seq TO iconta_user;


--
-- Name: TABLE mijloace_fixe; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.mijloace_fixe TO iconta_user;


--
-- Name: SEQUENCE mijloace_fixe_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.mijloace_fixe_id_seq TO iconta_user;


--
-- Name: TABLE miscari_stoc; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.miscari_stoc TO iconta_user;


--
-- Name: TABLE nir; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.nir TO iconta_user;


--
-- Name: TABLE nir_linii; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.nir_linii TO iconta_user;


--
-- Name: TABLE plan_conturi; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.plan_conturi TO iconta_user;


--
-- Name: TABLE salariati; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.salariati TO iconta_user;


--
-- Name: SEQUENCE salariati_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.salariati_id_seq TO iconta_user;


--
-- Name: TABLE solduri_initiale; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.solduri_initiale TO iconta_user;


--
-- Name: SEQUENCE solduri_initiale_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.solduri_initiale_id_seq TO iconta_user;


--
-- Name: TABLE solduri_parteneri; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON TABLE tenant_001.solduri_parteneri TO iconta_user;


--
-- Name: SEQUENCE solduri_parteneri_id_seq; Type: ACL; Schema: tenant_001; Owner: postgres
--

GRANT ALL ON SEQUENCE tenant_001.solduri_parteneri_id_seq TO iconta_user;


--
-- PostgreSQL database dump complete
--

\unrestrict dvt9E34bCyIEaT2f9va5jVBG5hp2AkVW6nOGSNUkpebHouWJAGAeyugWhRlFNqt

