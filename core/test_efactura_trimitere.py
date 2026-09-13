# -*- coding: utf-8 -*-
"""PROBA FUNCTIONALA a use-case-ului de trimitere — cele patru porti, pe DB reala, cu retea MOCK.

DE CE EXISTA (13.09.2026, valul D2 al lui P7). Mutarea celor 8 instructiuni SQL din motorul fiscal
in repository a fost probata structural: AST, confruntarea textului SQL cu versiunea de la `HEAD`,
si suita ramasa verde. Structura nu acopera insa modul de esec pe care chiar mutarea il introduce:
**o functie de repository chemata cu argumentele in alta ordine**. `trimitere_vie(cur, schema,
factura_id, mediu)` cu ultimele doua inversate se compileaza, trece `ruff`, trece toate gardurile de
strat — si intoarce mereu „nicio trimitere vie", adica strica exact idempotenta pe care poarta 3 o
apara. *O proba pe forma codului nu poate vedea o eroare de APEL.*

Deci proba de aici cheama `trimite` cap-coada, pe o schema efemera comisa, si se uita la ce a ramas
in baza. Reteaua e mock (regula casei: niciodata ANAF real), iar validatorul de structura la fel —
amandoua sunt in afara a ce a mutat valul D2.

ACOPERIRE, numarata: 7 din cele 8 instructiuni mutate trec pe aici — `factura_pentru_ubl`,
`linii_pentru_ubl`, `emitent_pentru_ubl`, `cui_emitent`, `trimitere_vie`,
`insereaza_trimitere_pregatita`, `rezultatul_trimiterii`. A opta, `repo_tenants.dupa_numele_schemei`,
are proba ei mai jos, prin `spv_conector.principal_pentru_schema`.
"""
import os

from cryptography.fernet import Fernet

os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-efactura-trimitere")
os.environ.setdefault("ANAF_CLIENT_ID", "TEST")
os.environ.setdefault("ANAF_REDIRECT_URI", "https://iconta.eu/anaf/oauth/callback")

import pytest  # noqa: E402

from core import db as _db  # noqa: E402
from core import efactura_send as ef  # noqa: E402
from core import efactura_trimitere as et  # noqa: E402
from core import spv_conector as sc  # noqa: E402
from core import tenant_provisioning as tp  # noqa: E402

SCHEMA_T = "ztest_efactura_trimitere"

UPLOAD_OK = ('<header xmlns="mfp:anaf:dgti:spv:respUploadFisier:v1" '
             'dateResponse="202609131200" ExecutionStatus="0" index_incarcare="7700"/>')
UPLOAD_NOK = ('<header xmlns="mfp:anaf:dgti:spv:respUploadFisier:v1" ExecutionStatus="1">'
              '<Errors errorMessage="CIF invalid"/></header>')


class _Resp:
    def __init__(self, text="", status=200):
        self.text = text
        self.status_code = status
        self.content = text.encode("utf-8")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def schema():
    """Schema efemera COMISA din tenant_template + DROP la teardown.

    `trimite` deschide TREI conexiuni proprii si comite pe ele — deci schema trebuie sa fie vizibila
    din afara tranzactiei probei, ca la `test_spv_poll`. *Tocmai faptul ca proba e obligata sa fie
    asa e o afirmatie despre codul probat: hotarele n-au fost mutate.*
    """
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
            cur.execute(tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
    yield SCHEMA_T
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)


@pytest.fixture
def factura(schema):
    """Emitent + o factura cu doua linii — minimul din care generatorul UBL poate produce un XML."""
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.firma_profil
                (id, nume, cui, reg_com, adresa, oras, judet, cod_postal, iban, platitor_tva)
                VALUES (1, 'FIRMA MEA SRL', '40372003', 'J12/1/2020', 'Bd. Test 10, Sector 2',
                        'Bucuresti', 'Bucuresti', '010101', 'RO49AAAA1B31007593840000', true)""")
            cur.execute(f"""INSERT INTO {schema}.facturi
                (numar, serie, data_emitere, data_scadenta, moneda, tert_nume, tert_cui,
                 tert_adresa, taxare_inversa, tip, total, tva)
                VALUES ('0007', 'FCT', DATE '2026-07-18', DATE '2026-08-17', 'RON', 'CLIENT SRL',
                        'RO12345678', 'Str. Exemplu 1, Cluj', false, 'factura', 288.00, 38.00)
                RETURNING id""")
            fid = cur.fetchone()[0]
            cur.execute(f"""INSERT INTO {schema}.factura_linii
                (factura_id, descriere, um, cantitate, pret_unitar, cota_tva)
                VALUES (%s, 'Serviciu A', 'buc', 2, 100.00, 19),
                       (%s, 'Serviciu B', 'buc', 1, 50.00, 0)""", (fid, fid))
    return fid


@pytest.fixture
def fara_retea(monkeypatch):
    """Tokenul, validatorul si upload-ul — toate in afara a ce a mutat valul D2."""
    monkeypatch.setattr(sc, "ia_token_activ", lambda conn, principal: {"id": 1})
    monkeypatch.setattr(ef, "valideaza", lambda xml, standard="FACT1": (True, []))
    monkeypatch.setattr(ef, "upload_ubl", lambda p, cif, xml, mediu: _Resp(UPLOAD_OK))


def _randuri(schema, factura_id):
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"""SELECT id, stare, index_incarcare, execution_status, xml_sha256,
                                   xml_trimis IS NOT NULL, mediu
                              FROM {schema}.efactura_trimiteri
                             WHERE factura_id=%s ORDER BY id""", (factura_id,))
            return cur.fetchall()


def test_trimiterea_reusita_scrie_randul_pe_care_il_promite(schema, factura, fara_retea):
    """Cap-coada: cele patru porti trec, iar randul din baza poarta ce spune raspunsul."""
    rez = et.trimite(schema, factura, sc.principal_tenant(1), mediu="test")
    assert rez["stare"] == "incarcat", rez
    assert rez["index_incarcare"] == "7700"
    assert rez["cif"] == "40372003", "CIF-ul emitentului n-a venit din `cui_emitent`: %r" % rez

    randuri = _randuri(schema, factura)
    assert len(randuri) == 1, "poarta 3 a scris %d randuri, nu unul" % len(randuri)
    _id, stare, index, ex, sha, are_xml, mediu = randuri[0]
    assert (stare, index, ex, mediu) == ("incarcat", "7700", 0, "test")
    assert are_xml, "XML-ul trimis nu s-a pastrat"
    assert sha == rez["xml_sha256"] and len(sha) == 64


def test_a_doua_trimitere_e_refuzata_de_idempotenta(schema, factura, fara_retea):
    """Poarta 3, pe drumul ei adevarat: `trimitere_vie` chemata cu argumentele in ordinea buna.

    Modul de esec pe care il apara: cu `factura_id` si `mediu` inversate, interogarea n-ar gasi
    nimic, iar a doua apasare ar incarca factura A DOUA OARA la ANAF. Upload-ul nu e idempotent.
    """
    prima = et.trimite(schema, factura, sc.principal_tenant(1), mediu="test")
    assert prima["stare"] == "incarcat"
    a_doua = et.trimite(schema, factura, sc.principal_tenant(1), mediu="test")
    assert a_doua["stare"] == "deja_trimisa", a_doua
    assert a_doua["trimitere_id"] == prima["trimitere_id"]
    assert a_doua["stare_existenta"] == "incarcat"
    assert len(_randuri(schema, factura)) == 1, "idempotenta a lasat un al doilea rand"


def test_alt_MEDIU_nu_e_acoperit_de_trimiterea_veche(schema, factura, fara_retea):
    """Calibrarea negativa a probei de mai sus: daca `trimitere_vie` ar ignora `mediu`, ar refuza
    si o trimitere catre celalalt mediu — iar proba de idempotenta ar trece la fel de bine."""
    et.trimite(schema, factura, sc.principal_tenant(1), mediu="test")
    alt = et.trimite(schema, factura, sc.principal_tenant(1), mediu="prod")
    assert alt["stare"] == "incarcat", alt
    assert len(_randuri(schema, factura)) == 2


def test_upload_refuzat_lasa_randul_cu_motivul_LA_VEDERE(schema, factura, monkeypatch):
    """Poarta 4 scrie randul INDIFERENT de rezultat — `rezultatul_trimiterii`, pe calea de esec."""
    monkeypatch.setattr(sc, "ia_token_activ", lambda conn, principal: {"id": 1})
    monkeypatch.setattr(ef, "valideaza", lambda xml, standard="FACT1": (True, []))
    monkeypatch.setattr(ef, "upload_ubl", lambda p, cif, xml, mediu: _Resp(UPLOAD_NOK))

    rez = et.trimite(schema, factura, sc.principal_tenant(1), mediu="test")
    assert rez["stare"] == "nok", rez
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"""SELECT stare, error_message, finalizat_la IS NOT NULL
                              FROM {schema}.efactura_trimiteri WHERE factura_id=%s""", (factura,))
            stare, mesaj, finalizat = cur.fetchone()
    assert stare == "nok"
    assert mesaj.count("CIF invalid") == 1, "motivul refuzului nu s-a pastrat: %r" % mesaj
    assert finalizat, "o stare terminala trebuie sa poarte `finalizat_la`"


def test_fara_token_se_opreste_INAINTE_sa_scrie_ceva(schema, factura, monkeypatch):
    """Poarta 1: fara token nu se genereaza XML si nu se atinge `efactura_trimiteri`."""
    monkeypatch.setattr(sc, "ia_token_activ", lambda conn, principal: None)
    rez = et.trimite(schema, factura, sc.principal_tenant(1), mediu="test")
    assert rez["stare"] == "fara_token"
    assert _randuri(schema, factura) == []


def test_structura_NEVALIDATA_nu_ajunge_la_upload(schema, factura, monkeypatch):
    """Poarta 2: validatorul refuza, deci nu se incarca nimic si nu se scrie niciun rand."""
    monkeypatch.setattr(sc, "ia_token_activ", lambda conn, principal: {"id": 1})
    monkeypatch.setattr(ef, "valideaza", lambda xml, standard="FACT1": (False, ["BR-RO-010"]))

    def _nu_ajunge(*a, **k):
        raise AssertionError("upload chemat desi structura e nevalidata")

    monkeypatch.setattr(ef, "upload_ubl", _nu_ajunge)
    rez = et.trimite(schema, factura, sc.principal_tenant(1), mediu="test")
    assert rez["stare"] == "nevalidat"
    assert rez["validare_mesaje"] == ["BR-RO-010"]
    assert _randuri(schema, factura) == []


def test_o_factura_FARA_LINII_e_refuzata_de_loader(schema, fara_retea):
    """`incarca_factura` pe drumul lui de refuz — al doilea consumator al celor trei citiri."""
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.firma_profil (id, nume, cui)
                            VALUES (1, 'FIRMA MEA SRL', '40372003')""")
            cur.execute(f"""INSERT INTO {schema}.facturi (numar, data_emitere, moneda, tip)
                            VALUES ('0008', DATE '2026-07-18', 'RON', 'factura') RETURNING id""")
            fid = cur.fetchone()[0]
    with pytest.raises(ValueError) as e:
        et.trimite(schema, fid, sc.principal_tenant(1), mediu="test")
    assert str(e.value).count("nu are linii") == 1


def test_principalul_unei_scheme_INEXISTENTE_e_refuzat_nu_ghicit():
    """A opta instructiune mutata: `repo_tenants.dupa_numele_schemei`, prin `spv_conector`.

    Interogarea chiar rulează pe `public.tenants`; ce se probeaza e ca un raspuns GOL devine refuz,
    nu un principal fabricat. *Un `None` pe care apelantul nu-l deosebeste de un principal valid ar
    trimite factura pe tokenul altcuiva.*
    """
    with _db.get_conn() as conn:
        with pytest.raises(ValueError) as e:
            sc.principal_pentru_schema(conn, "ztest_schema_care_nu_exista")
    assert str(e.value).count("fara tenant public") == 1
