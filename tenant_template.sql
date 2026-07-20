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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
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
-- Name: factura_linii; Type: TABLE; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

CREATE TABLE TENANT_PLACEHOLDER.factura_linii (
    id integer NOT NULL,
    factura_id integer NOT NULL,
    descriere text NOT NULL,
    um character varying(10) DEFAULT 'buc'::character varying NOT NULL,
    cantitate numeric(12,3) DEFAULT 1 NOT NULL,
    pret_unitar numeric(12,2) DEFAULT 0 NOT NULL,
    cota_tva numeric(5,2) DEFAULT 21 NOT NULL
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
    tert_adresa text,
    taxare_inversa boolean DEFAULT false NOT NULL,
    categorie_331 character varying(30),
    tip character varying(10) DEFAULT 'factura'::character varying NOT NULL,
    transformat_in_id integer,
    sursa_externa character varying(50),
    link_plata text,
    plata_provider character varying(20),
    plata_ref character varying(100),
    platita_la timestamp with time zone
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
    patron_email text,
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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
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
('1012', 'Capital subscris varsat', 'Bifunctional'),
('105', 'Rezerve din reevaluare', 'Bifunctional'),
('106', 'Rezerve', 'Bifunctional'),
('1061', 'Rezerve legale', 'Bifunctional'),
('1068', 'Alte rezerve', 'Bifunctional'),
('117', 'Rezultatul reportat', 'Bifunctional'),
('1171', 'Rezultatul reportat - profit nerepartizat / pierdere neacoperita', 'Bifunctional'),
('121', 'Profit sau pierdere', 'Bifunctional'),
('129', 'Repartizarea profitului', 'Bifunctional'),
('151', 'Provizioane', 'Bifunctional'),
('161', 'Imprumuturi din emisiuni de obligatiuni', 'Bifunctional'),
('162', 'Credite bancare pe termen lung', 'Bifunctional'),
('1621', 'Credite bancare pe termen lung', 'Bifunctional'),
('166', 'Datorii care privesc imobilizarile financiare', 'Bifunctional'),
('167', 'Alte imprumuturi si datorii asimilate', 'Bifunctional'),
('168', 'Dobanzi aferente imprumuturilor', 'Bifunctional'),
('201', 'Cheltuieli de constituire', 'Bifunctional'),
('203', 'Cheltuieli de dezvoltare', 'Bifunctional'),
('205', 'Concesiuni, brevete, licente, marci comerciale', 'Bifunctional'),
('208', 'Alte imobilizari necorporale', 'Bifunctional'),
('211', 'Terenuri si amenajari de terenuri', 'Bifunctional'),
('212', 'Constructii', 'Bifunctional'),
('213', 'Instalatii tehnice si mijloace de transport', 'Bifunctional'),
('2131', 'Echipamente tehnologice', 'Bifunctional'),
('2132', 'Aparate si instalatii de masurare', 'Bifunctional'),
('2133', 'Mijloace de transport', 'Bifunctional'),
('214', 'Mobilier, aparatura birotica', 'Bifunctional'),
('231', 'Imobilizari corporale in curs de executie', 'Bifunctional'),
('261', 'Actiuni detinute la entitatile afiliate', 'Bifunctional'),
('267', 'Creante imobilizate', 'Bifunctional'),
('280', 'Amortizari privind imobilizarile necorporale', 'Bifunctional'),
('2805', 'Amortizarea concesiunilor, brevetelor, licentelor', 'Bifunctional'),
('2808', 'Amortizarea altor imobilizari necorporale', 'Bifunctional'),
('281', 'Amortizari privind imobilizarile corporale', 'Bifunctional'),
('2811', 'Amortizarea amenajarilor de terenuri', 'Bifunctional'),
('2812', 'Amortizarea constructiilor', 'Bifunctional'),
('2813', 'Amortizarea instalatiilor si mijloacelor de transport', 'Bifunctional'),
('2814', 'Amortizarea altor imobilizari corporale', 'Bifunctional'),
('301', 'Materii prime', 'Bifunctional'),
('302', 'Materiale consumabile', 'Bifunctional'),
('3021', 'Materiale auxiliare', 'Bifunctional'),
('3022', 'Combustibili', 'Bifunctional'),
('3024', 'Piese de schimb', 'Bifunctional'),
('3028', 'Alte materiale consumabile', 'Bifunctional'),
('303', 'Materiale de natura obiectelor de inventar', 'Bifunctional'),
('331', 'Produse in curs de executie', 'Bifunctional'),
('345', 'Produse finite', 'Bifunctional'),
('371', 'Marfuri', 'Bifunctional'),
('378', 'Diferente de pret la marfuri', 'Bifunctional'),
('381', 'Ambalaje', 'Bifunctional'),
('391', 'Ajustari pentru deprecierea materiilor prime', 'Bifunctional'),
('397', 'Ajustari pentru deprecierea marfurilor', 'Bifunctional'),
('401', 'Furnizori', 'Bifunctional'),
('403', 'Efecte de platit', 'Bifunctional'),
('404', 'Furnizori de imobilizari', 'Bifunctional'),
('408', 'Furnizori - facturi nesosite', 'Bifunctional'),
('409', 'Furnizori - debitori', 'Bifunctional'),
('4091', 'Furnizori - debitori pentru cumparari de bunuri', 'Bifunctional'),
('411', 'Clienti', 'Bifunctional'),
('4111', 'Clienti', 'Bifunctional'),
('4118', 'Clienti incerti sau in litigiu', 'Bifunctional'),
('413', 'Efecte de primit de la clienti', 'Bifunctional'),
('418', 'Clienti - facturi de intocmit', 'Bifunctional'),
('419', 'Clienti - creditori', 'Bifunctional'),
('421', 'Personal - salarii datorate', 'Bifunctional'),
('423', 'Personal - ajutoare materiale datorate', 'Bifunctional'),
('425', 'Avansuri acordate personalului', 'Bifunctional'),
('426', 'Drepturi de personal neridicate', 'Bifunctional'),
('427', 'Retineri din salarii datorate tertilor', 'Bifunctional'),
('428', 'Alte datorii si creante in legatura cu personalul', 'Bifunctional'),
('431', 'Asigurari sociale', 'Bifunctional'),
('4315', 'Contributia de asigurari sociale', 'Bifunctional'),
('4316', 'Contributia de asigurari sociale de sanatate', 'Bifunctional'),
('436', 'Contributia asiguratorie pentru munca', 'Bifunctional'),
('437', 'Ajutor de somaj', 'Bifunctional'),
('438', 'Alte datorii si creante sociale', 'Bifunctional'),
('441', 'Impozitul pe profit si alte impozite', 'Bifunctional'),
('4411', 'Impozitul pe profit', 'Bifunctional'),
('4418', 'Impozitul pe venit', 'Bifunctional'),
('442', 'Taxa pe valoarea adaugata', 'Bifunctional'),
('4423', 'TVA de plata', 'Bifunctional'),
('4424', 'TVA de recuperat', 'Bifunctional'),
('4426', 'TVA deductibila', 'Bifunctional'),
('4427', 'TVA colectata', 'Bifunctional'),
('4428', 'TVA neexigibila', 'Bifunctional'),
('444', 'Impozitul pe venituri de natura salariilor', 'Bifunctional'),
('445', 'Subventii', 'Bifunctional'),
('446', 'Alte impozite, taxe si varsaminte asimilate', 'Bifunctional'),
('447', 'Fonduri speciale - taxe si varsaminte asimilate', 'Bifunctional'),
('448', 'Alte datorii si creante cu bugetul statului', 'Bifunctional'),
('455', 'Sume datorate actionarilor/asociatilor', 'Bifunctional'),
('4551', 'Actionari/asociati - conturi curente', 'Bifunctional'),
('456', 'Decontari cu actionarii/asociatii privind capitalul', 'Bifunctional'),
('457', 'Dividende de plata', 'Bifunctional'),
('458', 'Decontari din operatiuni in participatie', 'Bifunctional'),
('461', 'Debitori diversi', 'Bifunctional'),
('462', 'Creditori diversi', 'Bifunctional'),
('471', 'Cheltuieli inregistrate in avans', 'Bifunctional'),
('472', 'Venituri inregistrate in avans', 'Bifunctional'),
('473', 'Decontari din operatiuni in curs de clarificare', 'Bifunctional'),
('491', 'Ajustari pentru deprecierea creantelor - clienti', 'Bifunctional'),
('5121', 'Conturi la banci in lei', 'Bifunctional'),
('5124', 'Conturi la banci in valuta', 'Bifunctional'),
('5125', 'Sume in curs de decontare', 'Bifunctional'),
('512', 'Conturi curente la banci', 'Bifunctional'),
('518', 'Dobanzi', 'Bifunctional'),
('519', 'Credite bancare pe termen scurt', 'Bifunctional'),
('531', 'Casa', 'Bifunctional'),
('5311', 'Casa in lei', 'Bifunctional'),
('5314', 'Casa in valuta', 'Bifunctional'),
('532', 'Alte valori', 'Bifunctional'),
('5328', 'Alte valori', 'Bifunctional'),
('541', 'Acreditive', 'Bifunctional'),
('542', 'Avansuri de trezorerie', 'Bifunctional'),
('581', 'Viramente interne', 'Bifunctional'),
('601', 'Cheltuieli cu materiile prime', 'Bifunctional'),
('602', 'Cheltuieli cu materialele consumabile', 'Bifunctional'),
('6021', 'Cheltuieli cu materialele auxiliare', 'Bifunctional'),
('6022', 'Cheltuieli privind combustibilii', 'Bifunctional'),
('6024', 'Cheltuieli privind piesele de schimb', 'Bifunctional'),
('6028', 'Cheltuieli privind alte materiale consumabile', 'Bifunctional'),
('603', 'Cheltuieli privind materialele de natura obiectelor de inventar', 'Bifunctional'),
('604', 'Cheltuieli privind materialele nestocate', 'Bifunctional'),
('605', 'Cheltuieli privind utilitatile', 'Bifunctional'),
('607', 'Cheltuieli privind marfurile', 'Bifunctional'),
('608', 'Cheltuieli privind ambalajele', 'Bifunctional'),
('611', 'Cheltuieli cu intretinerea si reparatiile', 'Bifunctional'),
('612', 'Cheltuieli cu redeventele, locatiile de gestiune si chiriile', 'Bifunctional'),
('613', 'Cheltuieli cu primele de asigurare', 'Bifunctional'),
('614', 'Cheltuieli cu studiile si cercetarile', 'Bifunctional'),
('621', 'Cheltuieli cu colaboratorii', 'Bifunctional'),
('622', 'Cheltuieli privind comisioanele si onorariile', 'Bifunctional'),
('623', 'Cheltuieli de protocol, reclama si publicitate', 'Bifunctional'),
('624', 'Cheltuieli cu transportul de bunuri si personal', 'Bifunctional'),
('625', 'Cheltuieli cu deplasari, detasari si transferari', 'Bifunctional'),
('626', 'Cheltuieli postale si taxe de telecomunicatii', 'Bifunctional'),
('627', 'Cheltuieli cu serviciile bancare si asimilate', 'Bifunctional'),
('628', 'Alte cheltuieli cu serviciile executate de terti', 'Bifunctional'),
('635', 'Cheltuieli cu alte impozite, taxe si varsaminte asimilate', 'Bifunctional'),
('641', 'Cheltuieli cu salariile personalului', 'Bifunctional'),
('642', 'Cheltuieli cu avantajele in natura si tichetele acordate salariatilor', 'Bifunctional'),
('645', 'Cheltuieli privind asigurarile si protectia sociala', 'Bifunctional'),
('646', 'Cheltuieli privind contributia asiguratorie pentru munca', 'Bifunctional'),
('652', 'Cheltuieli cu protectia mediului inconjurator', 'Bifunctional'),
('654', 'Pierderi din creante si debitori diversi', 'Bifunctional'),
('655', 'Cheltuieli din reevaluarea imobilizarilor corporale', 'Bifunctional'),
('658', 'Alte cheltuieli de exploatare', 'Bifunctional'),
('6581', 'Despagubiri, amenzi si penalitati', 'Bifunctional'),
('6588', 'Alte cheltuieli de exploatare', 'Bifunctional'),
('665', 'Cheltuieli din diferente de curs valutar', 'Bifunctional'),
('666', 'Cheltuieli privind dobanzile', 'Bifunctional'),
('667', 'Cheltuieli privind sconturile acordate', 'Bifunctional'),
('681', 'Cheltuieli de exploatare privind amortizarile, provizioanele', 'Bifunctional'),
('6811', 'Cheltuieli de exploatare privind amortizarea imobilizarilor', 'Bifunctional'),
('6812', 'Cheltuieli de exploatare privind provizioanele', 'Bifunctional'),
('6814', 'Cheltuieli de exploatare privind ajustarile pentru deprecierea activelor circulante', 'Bifunctional'),
('691', 'Cheltuieli cu impozitul pe profit', 'Bifunctional'),
('698', 'Cheltuieli cu impozitul pe venit', 'Bifunctional'),
('701', 'Venituri din vanzarea produselor finite', 'Bifunctional'),
('704', 'Venituri din servicii prestate', 'Bifunctional'),
('705', 'Venituri din studii si cercetari', 'Bifunctional'),
('706', 'Venituri din redevente, locatii de gestiune si chirii', 'Bifunctional'),
('707', 'Venituri din vanzarea marfurilor', 'Bifunctional'),
('708', 'Venituri din activitati diverse', 'Bifunctional'),
('711', 'Venituri aferente costurilor stocurilor de produse', 'Bifunctional'),
('721', 'Venituri din productia de imobilizari necorporale', 'Bifunctional'),
('722', 'Venituri din productia de imobilizari corporale', 'Bifunctional'),
('741', 'Venituri din subventii de exploatare', 'Bifunctional'),
('754', 'Venituri din creante reactivate si debitori diversi', 'Bifunctional'),
('758', 'Alte venituri din exploatare', 'Bifunctional'),
('7581', 'Venituri din despagubiri, amenzi si penalitati', 'Bifunctional'),
('7588', 'Alte venituri din exploatare', 'Bifunctional'),
('765', 'Venituri din diferente de curs valutar', 'Bifunctional'),
('766', 'Venituri din dobanzi', 'Bifunctional'),
('767', 'Venituri din sconturi obtinute', 'Bifunctional'),
('781', 'Venituri din provizioane si ajustari pentru depreciere', 'Bifunctional'),
('7814', 'Venituri din ajustari pentru deprecierea activelor circulante', 'Bifunctional'),
('8051', 'Dobanzi de platit', 'Bifunctional'),
('731', 'Venituri din cotizatiile membrilor, contributiile banesti sau in natura ale membrilor si simpatizantilor, din cote-parti primite potrivit statutului', 'Bifunctional'),
('732', 'Venituri din taxele de inregistrare stabilite potrivit legislatiei in vigoare', 'Bifunctional'),
('733', 'Venituri din donatii, sume sau bunuri primite prin sponsorizare si ajutoare', 'Bifunctional'),
('734', 'Venituri financiare rezultate din activitatile fara scop patrimonial', 'Bifunctional'),
('736', 'Venituri din subventii de exploatare', 'Bifunctional'),
('738', 'Alte venituri din activitatile fara scop patrimonial', 'Bifunctional');


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
    curs_valutar numeric(10,4),
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
    creat_la timestamp with time zone DEFAULT now() NOT NULL
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
-- Name: state_plata state_plata_salariat_id_luna_key; Type: CONSTRAINT; Schema: TENANT_PLACEHOLDER; Owner: postgres
--

ALTER TABLE ONLY TENANT_PLACEHOLDER.state_plata
    ADD CONSTRAINT state_plata_salariat_id_luna_key UNIQUE (salariat_id, luna);


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

-- perioada_blocata_trigger_v1 (#66): blocheaza INSERT/UPDATE/DELETE pe luna inchisa

CREATE OR REPLACE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata() RETURNS trigger AS $$
DECLARE
  d date;
BEGIN
  IF TG_OP = 'DELETE' THEN d := OLD.data; ELSE d := NEW.data; END IF;
  IF EXISTS (SELECT 1 FROM TENANT_PLACEHOLDER.perioade_blocate
             WHERE an = EXTRACT(YEAR FROM d)::int AND luna = EXTRACT(MONTH FROM d)::int) THEN
    RAISE EXCEPTION 'PERIOADA_BLOCATA: luna %/% este inchisa',
      LPAD(EXTRACT(MONTH FROM d)::text, 2, '0'), EXTRACT(YEAR FROM d)::text;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_verifica_perioada_blocata ON TENANT_PLACEHOLDER.inregistrari;
CREATE TRIGGER trg_verifica_perioada_blocata
BEFORE INSERT OR UPDATE OR DELETE ON TENANT_PLACEHOLDER.inregistrari
FOR EACH ROW EXECUTE FUNCTION TENANT_PLACEHOLDER.verifica_perioada_blocata();

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
    CONSTRAINT beneficii_lunare_tip_ck CHECK (tip IN ('vacanta', 'cadou')),
    CONSTRAINT beneficii_lunare_eveniment_ck CHECK (eveniment IN ('', 'paste', 'craciun', '8martie', '1iunie', 'altul')),
    CONSTRAINT beneficii_lunare_luna_ck CHECK (luna BETWEEN 1 AND 12),
    CONSTRAINT beneficii_lunare_val_ck CHECK (valoare >= 0),
    CONSTRAINT beneficii_lunare_unic_v2 UNIQUE (salariat_id, an, luna, tip, eveniment)
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
