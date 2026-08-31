# -*- coding: utf-8 -*-
"""GARDĂ DE AȘTEPTARE: poziția 116 e o absență DECLARATĂ, și se află când încetează să fie posibilă.

*Costin, 31.08.2026: «Poziția 116 — absență declarată, nu construcție. Zero din 19 firme o datorează;
cod fără nicio instanță pe care să se probeze e clasa cu valori implicite fabricate. Ce nu se acceptă
e tăcerea de azi: D100 nu poate declara obligația și nici nu spune că nu poate. Dacă apare o firmă
purtătoare, se află atunci, nu la depunere.»*

**CE PĂZEȘTE, în trei părți:**

1. **Că D100 nu mai tace.** O firmă care ar putea fi purtătoare primește un avertisment care spune
   ce nu se poate și de ce — cu temeiul, nu ca propoziție.
2. **Că absența rămâne DECLARATĂ, nu se transformă în implementare tăcută.** Dacă cineva adaugă
   poziția 116 în `d100.COD_BUGETAR` fără să existe o firmă pe care s-o probeze, garda cade: e chiar
   clasa cu valori implicite fabricate.
3. **Că se află CÂND apare purtătorul.** A doua parte e inversul unei gărzi obișnuite, ca la notele
   explicative: cât timp nicio firmă nu e purtătoare, trece; **în ziua în care apare una, PICĂ**.

**CE NU PĂZEȘTE, declarat:** că firma chiar datorează. Criteriul legii e *titular de acord
petrolier* (OUG 24/2026 art. 2 alin. (1)) — un atribut pe care aplicația nu-l are deloc. Proxy-ul e
CAEN-ul, și **poate RATA** un purtător al cărui CAEN nu reflectă activitatea. Direcția erorii se
scrie: lista de purtători găsiți e un **plafon inferior**.
"""
import pytest

from core import d100_pozitia_116 as p116


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


# ── PARTEA PURĂ ─────────────────────────────────────────────────────────────────────────────

def test_absenta_isi_scrie_CE_LIPSESTE_ca_date():
    """O absență al cărei motiv e proză se repovestește greșit. Aici e o listă care se poate citi."""
    assert len(p116.CE_LIPSESTE) >= 3
    assert all(isinstance(x, str) and len(x) > 20 for x in p116.CE_LIPSESTE)


def test_codul_XML_al_pozitiei_e_NECUNOSCUT_nu_ghicit():
    """OPANAF 602/2026 numește POZIȚIA, nu codul de obligație XML — iar în D100 cele două sunt
    lucruri diferite (vezi `d100.COD_BUGETAR`: poz.5 din tabel are cod_oblig 121).

    `None` aici e răspunsul corect. Un număr pus «ca să fie» ar fi trecut de orice gardă de formă și
    ar fi picat abia la validatorul ANAF — adică la depunere."""
    assert p116.POZITIA == 116
    assert p116.COD_OBLIG_XML is None, (
        "codul XML al poziției 116 a primit o valoare. Dacă a fost citit la sursă, scrie sursa; "
        "dacă a fost dedus din poziție, e greșit prin construcție.")


def test_cele_trei_temeiuri_sunt_SEPARATE():
    """Trei întrebări diferite, trei acte: ce introduce obligația (OPANAF 602/2026), cine o
    datorează (OUG 24/2026 art. 2 alin. (1)) și CÂND (alin. (2), prețul Brent). Un singur temei ar
    fi ascuns că a treia condiție nici măcar nu ține de firmă."""
    assert p116.TEMEI_NOMENCLATOR.tip == "OPANAF" and p116.TEMEI_NOMENCLATOR.nr == 602
    assert p116.TEMEI_CINE_DATOREAZA.nr == 24 and p116.TEMEI_CINE_DATOREAZA.alin == "1"
    assert p116.TEMEI_CAND_SE_DATOREAZA.nr == 24 and p116.TEMEI_CAND_SE_DATOREAZA.alin == "2"
    assert p116.PRAG_BRENT_USD == 70, (
        "pragul de care atârnă obligația nu mai e 70 USD/baril. E o DATĂ, nu un număr dintr-o "
        "propoziție — dacă norma s-a schimbat, se schimbă și citarea de lângă el")


def test_proxy_ul_nu_inventeaza_un_purtator():
    """Direcția erorii, probată: proxy-ul poate RATA, nu poate inventa."""
    for caen in ("1071", "9602", "6201", "0111"):
        posibil, cod, _ = p116.poate_datora({"caen": caen})
        assert posibil is False and cod == "caen_in_afara", "CAEN %s a nimerit în proxy" % caen
    posibil, cod, _ = p116.poate_datora({"caen": "0610"})
    assert posibil is True and cod == "caen_in_zona", "proxy-ul nu vede nici extracția de țiței"


def test_o_firma_fara_CAEN_nu_e_declarata_curata():
    """Absența CAEN-ului nu e o dovadă că firma nu e purtătoare — e absența probei. Motivul o spune."""
    posibil, cod, _motiv = p116.poate_datora({})
    assert posibil is False
    assert cod == "fara_caen", (
        "motivul nu deosebește «nu indică» de «nu se poate aplica» — se asertează pe COD, nu pe "
        "cuvinte din propoziție")
    assert set(p116.MOTIVE) == {"caen_in_zona", "caen_in_afara", "fara_caen"}


def test_constatarea_e_OBIECT_cu_campuri_nu_propozitie():
    """Pe STRUCTURA (clichet 50): ce nu poate D100 e un obiect, iar propoziția pentru om se COMPUNE
    din el. Prima formă a acestei probe căuta cuvintele «Brent» și «nu o poate declara» în mesaj —
    a treia oară în trei zile când o gardă întreabă un sir. Reparația e mereu aceeași."""
    c = p116.constatare({"caen": "0610"})
    assert set(c) >= {"ce", "pozitia", "cod_oblig_xml", "motiv_cod", "motiv_proxy", "ce_lipseste",
                      "prag_brent_usd", "temei_nomenclator", "temei_cine", "temei_cand"}
    assert c["fel"] == "verificare_rupta", (
        "constatarea nu mai e o afirmație tipată. `verificare_rupta` există tocmai ca o derivare "
        "oprită să NU arate ca un verdict gri permanent — «nu se poate declara», nu «nu se datorează»")
    assert c["eroare"], "`verificare_rupta` fără `eroare` — nimeni n-ar ști de unde s-o repare"
    assert c["ce"] == "obligatie_nedeclarabila"
    assert c["pozitia"] == p116.POZITIA and c["cod_oblig_xml"] is None
    assert c["prag_brent_usd"] == p116.PRAG_BRENT_USD
    assert len(c["ce_lipseste"]) >= 3
    assert p116.constatare({"caen": "1071"}) is None, "constatare pe o firmă care n-are treabă"


def test_propozitia_pentru_om_se_COMPUNE_din_constatare():
    """Anti-vacuu pe compunere: un obiect perfect din care nu iese nicio propoziție n-ajunge la om."""
    av = p116.avertisment({"caen": "0610"})
    c = p116.constatare({"caen": "0610"})
    assert av and str(c["pozitia"]) in av and c["temei_nomenclator"] in av
    assert str(c["prag_brent_usd"]) in av, "propoziția nu poartă pragul din constatare"
    assert p116.avertisment({"caen": "1071"}) is None


# ── CĂ NU DEVINE IMPLEMENTARE TĂCUTĂ ────────────────────────────────────────────────────────

def test_pozitia_116_nu_a_intrat_TACUT_in_nomenclatorul_D100():
    """Dacă apare în `COD_BUGETAR`, obligația a fost implementată — și atunci absența declarată de
    aici e o minciună rămasă în urmă. Se cere ștergerea ei odată cu construcția."""
    from core import d100
    assert "116" not in d100.COD_BUGETAR, (
        "poziția 116 a intrat în `d100.COD_BUGETAR`, dar `d100_pozitia_116` o declară încă "
        "neconstruibilă. Ori s-a construit (și atunci absența asta se șterge, cu gardă proprie), "
        "ori a intrat un cod ghicit.")


def test_d100_CHEAMA_declararea_absentei():
    """Anti-vacuu pe legătură: modulul poate fi perfect scris și niciodată chemat — chiar clasa R70.
    Se citește din AST-ul lui `d100`, nu ca șir în fișier."""
    import ast
    import io
    import os
    cale = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "core", "d100.py")
    arb = ast.parse(io.open(cale, encoding="utf-8").read())
    chemat = any(isinstance(n, ast.Attribute) and n.attr == "avertisment"
                 for n in ast.walk(arb))
    importat = any(isinstance(n, ast.ImportFrom) and n.module == "core"
                   and any(a.name == "d100_pozitia_116" for a in n.names)
                   for n in ast.walk(arb))
    assert importat and chemat, (
        "`d100` nu mai cheamă declararea absenței — D100 a redevenit tăcut despre poziția 116")


# ── CÂND APARE PURTĂTORUL ───────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nicio_firma_nu_e_inca_purtatoare():
    """Inversul unei gărzi obișnuite: apără o absență motivată. **În ziua în care apare o firmă
    purtătoare, PICĂ** — și atunci absența declarată încetează să fie acceptabilă.

    Fără `skipif` pe variabile inventate: lecția gărzii de așteptare a notelor explicative, care a
    fost o zi verde pe zero fiindcă sărea pe `PGHOST`, o variabilă care nici nu există aici.
    """
    from core import db
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    assert scheme, "ANTI-VACUU: zero firme active — garda ar trece pe o mulțime goală"

    purtatoare = []
    for s in scheme:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT caen, nume FROM {}.firma_profil WHERE id = 1".format(s))
            r = cur.fetchone()
        if r and p116.poate_datora({"caen": r[0]})[0]:
            purtatoare.append((s, r[0], r[1]))

    assert not purtatoare, (
        "A APĂRUT o firmă care ar putea datora contribuția de solidaritate: %s.\n\n"
        "Absența declarată a poziției 116 nu mai e acceptabilă: acum există o instanță pe care "
        "calculul se poate proba. Ce lipsește, ca listă: %s.\n"
        "Atenție: obligația se datorează DOAR în lunile cu Brent peste 70 USD/baril (%s), iar "
        "cotația nu e în aplicație — deci construcția cere și o sursă pentru ea."
        % (purtatoare, "; ".join(p116.CE_LIPSESTE), p116.TEMEI_CAND_SE_DATOREAZA))
