# -*- coding: utf-8 -*-
"""GARD — deficiența 221 (comanda Costin 10.10.2026, verbatim în DECIZII): „Bilanț: coloana «An precedent» e copiată din anul curent
(grav, cifre greșite în declarație).” Cauza: `f10p` era soldul de preluare (`solduri_initiale`) oricare ar fi anul, iar pe anul
preluării coloana curentă ieșea tot din el (fără mișcări) — două coloane identice.

TEMEI: OMFP 1802/2014, Reglementări, pct.130 (forma consolidată din corpus, `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`):
„Pentru fiecare element de bilanţ … trebuie prezentată valoarea aferentă exerciţiului financiar la care se referă bilanţul … precum
şi valoarea aferentă elementului corespondent pentru exerciţiul financiar precedent.”

[Decizia Costin 11.10.2026, verbatim în DECIZII — supersedează „gol, cu avertisment”] „coloana «An precedent» din bilanț se completează
din bilanțul anului anterior, dacă firma îl are în aplicație. Dacă nu îl are, se completează manual, cu avertisment vizibil. Bilanțul nu
poate fi generat cu coloana goală.” Sursele, în ordine (`bilant_api.coloana_precedenta`): bilanțul anului precedent validat în aplicație
-> evidența anului precedent (F10 = soldurile la 31.12, cunoscute de la soldurile de preluare încoace; F20 = numai cu tot anul în
aplicație) -> completată manual. Nicio sursă pe o secțiune -> refuz. Schemă efemeră din `tenant_template.sql`, ROLLBACK."""
import datetime
import re
from decimal import Decimal

import pytest
from psycopg2.extras import RealDictCursor

from core import bilant_api as ba, db as _db, tenant_provisioning as _tp

_SCHEMA = "ztest_bilant_an_precedent"


@pytest.fixture
def cur():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                c.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                c.execute("SET search_path TO %s, public" % _SCHEMA)
                c.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'PROBA SRL', '14399840') ON CONFLICT (id) DO NOTHING")
                yield c
        finally:
            conn.rollback()


def _nota(c, zi, debit, credit, suma):
    c.execute("INSERT INTO inregistrari (data, status, sursa, descriere) VALUES (%s, 'validata', 't', 'Probă') RETURNING id", (zi,))
    c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
              (c.fetchone()["id"], debit, credit, suma))


def _manual(c, tip, an, valori, de="Contabil Probă"):
    import json
    from core import artefacte
    artefacte.pastreaza(c.connection, _SCHEMA, ba.FEL_MANUAL, "%s:%d" % (tip, an), json.dumps(valori), produs_de=de)


def _bilant_pastrat(c, fel, cheie, continut, **kw):
    """Un bilanț păstrat DUPĂ rescrierea rândurilor pe formularul 2025 (`bilant_api.S1003_F20_SCHEMA_NOUA_DIN`): produs_la fixat după prag,
    ca testul să nu depindă de ceas (un bilanț produs înainte nu e „An precedent” — C10, C12, C13)."""
    from core import artefacte
    r = artefacte.pastreaza(c.connection, _SCHEMA, fel, cheie, continut, **kw)
    c.execute("UPDATE artefacte_produse SET produs_la = %s WHERE id = %s", (ba.S1003_F20_SCHEMA_NOUA_DIN + datetime.timedelta(days=1), r["id"]))
    return r


def _toate(sectiune, tip="s1005", **valori):
    return {str(r): valori.get("r%d" % r, 0) for r in ba.randuri_formular(tip)[sectiune]}


def test_coloana_precedenta_e_soldul_de_la_31_12_al_anului_precedent(cur):
    """Solduri de preluare la 31.12.2024 (5121 = 10.000), o încasare în 2025 (+2.000) și un venit în 2025 (704 = 2.000): bilanțul 2025
    are F10 „An precedent” 10.000 / „An curent” 12.000 — nu două coloane egale (simptomul 221); F20 al lui 2024 nu e în aplicație (evidența
    începe la 01.01.2025) -> refuz cu motivul, până la completarea manuală. Bilanțul 2026: tot anul 2025 e în aplicație -> F10 = soldurile la
    31.12.2025, F20 = rulajele lui 2025 (venitul 2.000 pe rd.01). MUTAȚIE: coloana precedentă = soldul de preluare pe ambele coloane ->
    pică; F20 luat din evidență și fără tot anul -> pică (nu se mai refuză)."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2024-12-31'), ('1012', 'Capital', 0, 10000, '2024-12-31')")
    _nota(cur, datetime.date(2025, 3, 10), "5121", "704", Decimal("2000"))
    with pytest.raises(ValueError, match=r"coloana „An precedent” goală \(F20\).*tot anul 2024"):
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2025)
    assert cp["sursa"] == {"F10": "evidenta", "F20": None}, cp["sursa"]
    f10c = ba.coloana_curenta_f10(cur, _SCHEMA, 2025)
    assert (cp["F10"].get(8), f10c.get(8)) == (10000, 12000), (cp["F10"].get(8), f10c.get(8))   # rd.08 „Casa și conturi la bănci”
    cp26 = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2026)
    assert cp26["sursa"] == {"F10": "evidenta", "F20": "evidenta"}, cp26["sursa"]
    assert cp26["F10"].get(8) == 12000 and cp26["F20"].get(1) == 2000, (cp26["F10"].get(8), cp26["F20"])


def test_bilantul_anului_precedent_din_aplicatie_are_intaietate(cur):
    """Firma are în aplicație bilanțul S1005 pe 2025 validat (artefactul, „An curent” rd.08 = 7.777, rd.01 F20 = 555), iar evidența ar da
    altceva (12.000): „An precedent” al bilanțului 2026 = coloana „An curent” a bilanțului 2025 din aplicație, pe ambele secțiuni. Un
    exemplar mai nou, cu erori de validare, nu-l înlocuiește. MUTAȚIE: artefactul ignorat (sursa = evidența) -> pică; exemplarul cu erori
    luat -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2024-12-31'), ('1012', 'Capital', 0, 10000, '2024-12-31')")
    _nota(cur, datetime.date(2025, 3, 10), "5121", "704", Decimal("2000"))
    xml_2025 = '<Bilant1005><F10 F10_0081="7000" F10_0082="7777"/><F20 F20_0012="555"/></Bilant1005>'
    _bilant_pastrat(cur, "s1005", "2025", xml_2025, produs_de="Contabil", verdict="valid")
    _bilant_pastrat(cur, "s1005", "2025", xml_2025.replace("7777", "1"), produs_de="Contabil", verdict="erori")
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2026)
    assert cp["sursa"] == {"F10": "bilant", "F20": "bilant"}, cp["sursa"]
    assert cp["F10"] == {8: 7777} and cp["F20"] == {1: 555}, (cp["F10"], cp["F20"])
    assert cp["bilant"]["exemplar"] == 1, cp["bilant"]
    assert ba.coloana_precedenta(cur, _SCHEMA, "s1003", 2026)["sursa"]["F20"] != "bilant"   # alt formular: rândurile F20 diferă


def test_fara_sursa_nu_se_genereaza_iar_manualul_se_spune(cur):
    """Solduri de preluare la 31.08.2026: anul 2025 nu e deloc în aplicație -> bilanțul 2026 se refuză („coloana «An precedent» goală (F10,
    F20)”); completată manual -> se generează, cu avertismentul vizibil (cine, „completată manual”, verifică față de bilanțul depus), iar
    cifrele manuale ajung în XML (F10_0081). Bilanțul 2025 se refuză (31.12.2025 e înainte de preluare). MUTAȚIE: refuzul pe secțiunea
    lipsă scos (coloana goală) -> pică; avertismentul manual scos -> pică; verificarea `zi < ref` scoasă din `sold_la` -> 2025 se
    generează cu soldul de preluare -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    with pytest.raises(ValueError, match=r"coloana „An precedent” goală \(F10, F20\)"):
        ba.coloanele(cur, _SCHEMA, "s1005", 2026, [])
    _manual(cur, "s1005", 2026, {"F10": _toate("F10", r8=4321), "F20": _toate("F20")})
    av = []
    f10p, f10c, f20p = ba.coloanele(cur, _SCHEMA, "s1005", 2026, av)
    assert f10p.get(8) == 4321 and f10c.get(8) == 10000 and f20p == {r: 0 for r in ba.randuri_formular("s1005")["F20"]}, (f10p, f20p)
    assert len(av) == 1, av
    assert re.search(r"completată manual de (.+?), la ", av[0]).group(1) == "Contabil Probă", av          # cine
    assert re.findall(r"bilanțul depus pe (\d{4})", av[0]) == ["2025"], av                              # față de ce se verifică
    cur.execute("UPDATE firma_profil SET reg_com = 'J40/1/2020', declarant_nume = 'Ion Popescu' WHERE id = 1")
    xml, _ = ba.genereaza(cur.connection, _SCHEMA, 2026)
    assert re.findall(r'\bF10_0081="(\d+)"', xml) == ["4321"] and re.findall(r'\bF10_0082="(\d+)"', xml) == ["10000"], xml[:600]
    with pytest.raises(ValueError, match="nu se poate întocmi"):
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])


def test_data_soldurilor_vine_din_luna_preluarii_cand_lipseste(cur):
    """Fără `data_referinta`: soldurile sunt la ziua dinaintea lunii preluării (aceeași regulă ca Date firmă / Control fiscal). Luna
    salvată 09/2026 -> 31.08.2026."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor) VALUES ('5121', 'Banca', 500, 0)")
    cur.execute("UPDATE firma_profil SET luna_preluare = '2026-09-01' WHERE id = 1")
    assert ba.data_soldurilor(cur, _SCHEMA) == datetime.date(2026, 8, 31)


def test_autorul_completarii_manuale_e_numit_nu_numerotat(cur):
    """[găsit la proba 221: „completată manual de 1968”] Avertismentul spune CINE a completat coloana: `artefacte.pastreaza` scrie
    numele utilizatorului (prenume + nume) din `public.users`, nu id-ul pe care apelanții îl treceau în lipsa unui nume în context.
    MUTAȚIE: căutarea numelui scoasă din `pastreaza` -> autorul e „<id>” -> pică."""
    import json
    from core import artefacte
    cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT 221') RETURNING id")
    firm = cur.fetchone()["id"]
    cur.execute("INSERT INTO public.users (email, password_hash, nume, prenume, rol, accounting_firm_id, activ) VALUES "
                "('zt_221@invalid', 'x', 'Popescu', 'Elena', 'admin_firma', %s, true) RETURNING id", (firm,))
    uid = cur.fetchone()["id"]
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    artefacte.pastreaza(cur.connection, _SCHEMA, ba.FEL_MANUAL, "s1005:2026",
                        json.dumps({"F10": _toate("F10"), "F20": _toate("F20")}), produs_de_id=uid, produs_de=str(uid))
    av = []
    ba.coloanele(cur, _SCHEMA, "s1005", 2026, av)
    assert re.search(r"completată manual de (.+?), la ", av[0]).group(1) == "Elena Popescu", av


def test_bilantul_generat_de_defect_nu_e_bilantul_anului_precedent(cur):
    """[prins la proba pe producție, 11.10.2026] F1 avea S1005 2025 „valid” din 10.10 — generat de defectul 221, cu ambele coloane =
    soldurile de preluare de la 31.08.2026. Un bilanț al anului precedent pe care aplicația nu l-ar putea întocmi azi (31.12 a lui e
    înaintea soldurilor de preluare) nu e sursă: coloana se cere manual, iar mesajul spune de ce bilanțul păstrat nu se folosește.
    MUTAȚIE: verificarea scoasă (artefactul luat oricum) -> „An precedent” = soldurile de preluare, fără refuz -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    _bilant_pastrat(cur, "s1005", "2025", '<Bilant1005><F10 F10_0081="10000" F10_0082="10000"/><F20/></Bilant1005>',
                        produs_de="Contabil", verdict="valid")
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2026)
    assert cp["sursa"] == {"F10": None, "F20": None} and cp["bilant_respins"]["exemplar"] == 1, cp
    with pytest.raises(ValueError, match=r"Bilanțul pe 2025 păstrat în aplicație .* nu se folosește: soldurile de preluare sunt de la 31\.08\.2026"):
        ba.coloanele(cur, _SCHEMA, "s1005", 2026, [])


def test_fiecare_an_din_mesaje_e_anul_lui(cur):
    """[decizia Costin 12.10.2026 pct.5, mutația scăpată din lotul 11.10: `an - 1` -> `an` în „din bilanțul depus pe %d” trecea verde]
    Contabilul acționează după anii din mesaj: verifică față de bilanțul depus pe anul PRECEDENT, completează soldurile de la 31.12 a
    anului precedent. Fiecare an din refuzul coloanei goale, din nota bilanțului respins, din avertismentul manual și din refuzul „nu se
    poate întocmi” e fixat pe poziția lui (bilanțul 2026: anul precedent 2025). MUTAȚIE: oricare `an - 1` din cele trei mesaje -> `an`,
    sau anul din refuzul „nu se poate întocmi” -> `an - 1` -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    _bilant_pastrat(cur, "s1005", "2025", '<Bilant1005><F10 F10_0081="10000" F10_0082="10000"/><F20/></Bilant1005>',
                        produs_de="Contabil", verdict="valid")
    with pytest.raises(ValueError) as e:
        ba.coloanele(cur, _SCHEMA, "s1005", 2026, [])
    m = str(e.value)
    assert re.findall(r"Bilanțul pe (\d{4}) nu se poate genera", m) == ["2026"], m
    assert re.findall(r"nu are în aplicație bilanțul pe (\d{4}) validat", m) == ["2025"], m
    assert re.findall(r"soldurile de la (\d\d\.\d\d\.\d{4})", m) == ["31.12.2025"], m
    assert re.findall(r"tot anul (\d{4})", m) == ["2025"], m
    assert re.findall(r"Bilanțul pe (\d{4}) păstrat în aplicație", m) == ["2025"], m
    assert re.findall(r"nu sunt ale exercițiului (\d{4})", m) == ["2025"], m
    assert re.findall(r"bilanțul depus pe (\d{4})", m) == ["2025"], m
    _manual(cur, "s1005", 2026, {"F10": _toate("F10"), "F20": _toate("F20")})
    av = []
    ba.coloanele(cur, _SCHEMA, "s1005", 2026, av)
    assert re.findall(r"nu din bilanțul pe (\d{4})", av[0]) == ["2025"], av
    assert re.findall(r"Bilanțul pe (\d{4}) păstrat în aplicație", av[0]) == ["2025"], av
    assert re.findall(r"nu sunt ale exercițiului (\d{4})", av[0]) == ["2025"], av
    assert re.findall(r"bilanțul depus pe (\d{4})", av[0]) == ["2025"], av
    with pytest.raises(ValueError) as e:
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    m = str(e.value)
    assert re.findall(r"Bilanțul pe (\d{4}) nu se poate întocmi", m) == ["2025"], m
    assert re.findall(r"soldurile de la (\d\d\.\d\d\.\d{4}) nu sunt în aplicație", m) == ["31.12.2025"], m


def _ecranul(cur, monkeypatch):
    """Rutele ecranului Bilanț (`uc_tenants.bilant_an_precedent(_scrie)`) pe schema efemeră, în tranzacția testului."""
    import contextlib
    from core import auth_api, uc_tenants

    @contextlib.contextmanager
    def _conn():
        yield cur.connection
    monkeypatch.setattr(_db, "get_conn", _conn)
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: _SCHEMA)
    return uc_tenants


def test_anii_de_pe_ecranul_bilant_sunt_ai_anului_precedent(cur, monkeypatch):
    """[generalizarea pct.5 din 12.10.2026: aceeași clasă — anul precedent scris ca an curent — pe drumul ecranului] Afirmația coloanei
    poartă anul precedent (`an`), sursele în care s-a căutat sunt pe anul precedent, iar refuzul completării manuale peste o secțiune
    venită din bilanț sau din evidență numește anul precedent. Bilanțul 2026 -> 2025 peste tot. MUTAȚIE: oricare `an - 1` din
    `bilant_an_precedent` / `bilant_an_precedent_scrie` -> `an` -> pică."""
    from core import erori
    uc = _ecranul(cur, monkeypatch)
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    a = uc.bilant_an_precedent(1, 2026, "s1005", {"uid": 1})["afirmatie"]
    assert (a["fel"], a["an"]) == ("absenta_observatie", 2025), a
    assert [re.findall(r"pe (\d{4})", s) for s in a["surse_consultate"]] == [["2025"], ["2025"]], a["surse_consultate"]
    _manual(cur, "s1005", 2026, {"F10": _toate("F10"), "F20": _toate("F20")})
    a = uc.bilant_an_precedent(1, 2026, "s1005", {"uid": 1})["afirmatie"]
    assert (a["fel"], a["an"]) == ("fapt", 2025), a
    cur.execute("UPDATE solduri_initiale SET data_referinta = '2024-12-31'")
    _nota(cur, datetime.date(2025, 3, 10), "5121", "704", Decimal("2000"))
    _bilant_pastrat(cur, "s1005", "2025", '<Bilant1005><F10 F10_0082="7777"/><F20 F20_0012="555"/></Bilant1005>',
                        produs_de="Contabil", verdict="valid")
    with pytest.raises(erori.DateInvalide) as e:
        uc.bilant_an_precedent_scrie(1, 2026, "s1005", {"F10": {}}, {"uid": 1})
    assert re.findall(r"vine din bilanțul pe (\d{4}) din aplicație", str(e.value)) == ["2025"], str(e.value)
    with pytest.raises(erori.DateInvalide) as e:
        uc.bilant_an_precedent_scrie(1, 2026, "s1003", {"F20": {}}, {"uid": 1})
    assert re.findall(r"vine din evidența pe (\d{4}) din aplicație", str(e.value)) == ["2025"], str(e.value)


def test_primul_exercitiu_coloana_an_precedent_ramane_goala(cur, monkeypatch):
    """[deficiența 229, comanda Costin 12.10.2026] „dacă firma s-a înființat în anul bilanțului, coloana «An precedent» rămâne legal goală
    (primul exercițiu) și nu se cere completarea manuală. Ține cont de data înființării.” TEMEI: Legea 82/1991 art.27 alin.(8) „Exercițiul
    financiar al unităților nou-înființate începe la data înființării, potrivit legii.”; OMFP 1802/2014 pct.130 cere valoarea „pentru
    exercițiul financiar precedent”, pe care primul exercițiu nu-l are.
    Firma înființată pe 15.03.2025, o notă în 03/2025: bilanțul 2025 se generează fără coloana 1 (nicio valoare „An precedent” în XML),
    fără avertisment și fără formular de completat; XML-ul e valid pe DUK; ecranul spune de ce, iar completarea manuală se refuză; bilanțul
    2024 (înaintea înființării) se refuză. MUTAȚIE: regula primului exercițiu scoasă din `coloana_precedenta` -> coloana „goală (F10, F20)”,
    refuz -> pică; anul înființării comparat cu `an - 1` -> pică."""
    from core import duk, erori
    cur.execute("UPDATE firma_profil SET data_infiintare = '2025-03-15', reg_com = 'J40/1/2025', caen = '6202', adresa = 'Str 1', "
                "oras = 'Buc', judet = 'B', declarant_nume = 'Popescu', declarant_prenume = 'Ion', declarant_functie = 'ADMINISTRATOR' WHERE id = 1")
    _nota(cur, datetime.date(2025, 3, 20), "5121", "1012", Decimal("1000"))
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2025)
    assert cp["sursa"] == {"F10": "primul_exercitiu", "F20": "primul_exercitiu"} and cp["F10"] == {} and cp["F20"] == {}, cp
    av = []
    f10p, f10c, f20p = ba.coloanele(cur, _SCHEMA, "s1005", 2025, av)
    assert (f10p, f20p, av) == ({}, {}, []) and f10c.get(8) == 1000, (f10p, f20p, av, f10c)
    xml, _ = ba.genereaza(cur.connection, _SCHEMA, 2025)
    assert re.findall(r'\bF[12]0_\d{3}1="', xml) == [] and re.findall(r'\bF10_0082="(\d+)"', xml) == ["1000"], xml[:600]
    v = duk.valideaza(xml, "s1005", an=2025, luna=12)
    assert v["stare"] == "valid", v
    with pytest.raises(ValueError, match=r"Bilanțul pe 2024 nu există: firma s-a înființat pe 15\.03\.2025"):
        ba.coloanele(cur, _SCHEMA, "s1005", 2024, [])
    uc = _ecranul(cur, monkeypatch)
    e = uc.bilant_an_precedent(1, 2025, "s1005", {"uid": 1})
    assert (e["lipsa"], e["de_completat"], e["afirmatie"]["fel"], e["afirmatie"]["an"]) == ([], [], "fapt", 2025), e
    assert re.search(r"Primul exercițiu financiar: firma s-a înființat pe 15\.03\.2025", e["afirmatie"]["motiv"]), e["afirmatie"]
    with pytest.raises(erori.DateInvalide, match="Primul exercițiu financiar"):
        uc.bilant_an_precedent_scrie(1, 2025, "s1005", {"F10": {}}, {"uid": 1})
    with pytest.raises(erori.DateInvalide, match="nu există"):
        uc.bilant_an_precedent(1, 2024, "s1005", {"uid": 1})


def test_firma_infiintata_inainte_cere_coloana_ca_pana_acum(cur):
    """Data înființării într-un an anterior nu schimbă nimic: bilanțul 2026 al unei firme din 2020, cu soldurile de preluare la
    31.08.2026, cere coloana „An precedent” (refuz până la completare) — primul exercițiu e numai anul înființării."""
    cur.execute("UPDATE firma_profil SET data_infiintare = '2020-05-04' WHERE id = 1")
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    with pytest.raises(ValueError, match=r"coloana „An precedent” goală \(F10, F20\)"):
        ba.coloanele(cur, _SCHEMA, "s1005", 2026, [])


def test_firma_adaugata_ia_data_infiintarii_din_anaf(cur):
    """[deficiența 229] La adăugarea firmei, `precompleteaza_din_anaf` scrie data înregistrării ANAF ca dată a înființării — fără să
    suprascrie una deja aleasă de contabil. MUTAȚIE: coloana scoasă din precompletare -> pică."""
    d = {"denumire": "PROBA SRL", "cod_caen": "6202", "adresa": "Str 1", "nr_reg_com": "J40/1/2025", "platitor_tva": False,
         "tva_la_incasare": False, "tva_data_inceput": None, "data_inregistrare": "2025-03-15"}
    _tp.precompleteaza_din_anaf(cur.connection, _SCHEMA, d)
    cur.execute("SELECT data_infiintare FROM firma_profil WHERE id = 1")
    assert cur.fetchone()["data_infiintare"] == datetime.date(2025, 3, 15)
    _tp.precompleteaza_din_anaf(cur.connection, _SCHEMA, dict(d, data_inregistrare="2001-01-01"))
    cur.execute("SELECT data_infiintare FROM firma_profil WHERE id = 1")
    assert cur.fetchone()["data_infiintare"] == datetime.date(2025, 3, 15)


def test_anul_care_nu_se_poate_intocmi_se_spune_pe_ecran(cur, monkeypatch):
    """[deficiența 228] Lângă acțiunile inactive stă motivul: pentru un an al cărui bilanț nu se poate întocmi deloc (31.12 dinaintea
    soldurilor de preluare) motivul e acesta, nu „completează coloana”, care n-ar ajuta. MUTAȚIE: verificarea `coloana_curenta_f10` scoasă
    din `bilant_an_precedent` -> ecranul ar cere completarea coloanei -> pică."""
    from core import erori
    uc = _ecranul(cur, monkeypatch)
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2024-12-31'), ('1012', 'Capital', 0, 10000, '2024-12-31')")
    with pytest.raises(erori.DateInvalide, match=r"Bilanțul pe 2023 nu se poate întocmi .* 31\.12\.2024"):
        uc.bilant_an_precedent(1, 2023, "s1005", {"uid": 1})
    assert uc.bilant_an_precedent(1, 2025, "s1005", {"uid": 1})["lipsa"] == ["F20"]


def test_s1003_pe_numerotarea_veche_nu_e_an_precedent(cur):
    """[C10, 12.10.2026] Un S1003 păstrat înainte de rescrierea F20 pe rândurile formularului are contul de profit și pierdere pe
    numerotarea veche: coloana lui „An curent” ar ajunge pe rânduri greșite. Nu se folosește ca „An precedent” (ca bilanțul respins de
    221), iar mesajul spune de ce. MUTAȚIE: verificarea `S1003_F20_SCHEMA_NOUA_DIN` scoasă -> sursa „bilant” -> pică."""
    from core import artefacte
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2023-12-31'), ('1012', 'Capital', 0, 10000, '2023-12-31')")
    artefacte.pastreaza(cur.connection, _SCHEMA, "s1003", "2025", '<Bilant1003><F10 F10_0082="7"/><F20 F20_0042="800"/></Bilant1003>',
                        produs_de="Contabil", verdict="valid")
    cur.execute("UPDATE artefacte_produse SET produs_la = '2026-10-01' WHERE fel = 's1003'")
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1003", 2026)
    assert cp["sursa"]["F20"] != "bilant" and cp["bilant_respins"]["numerotare_veche"], cp
    assert re.findall(r"profit și pierdere e pe (numerotarea veche)", ba.nota_bilant_respins(2026, cp["bilant_respins"])) == ["numerotarea veche"]


def test_def_233_totalurile_coloanei_manuale_le_calculeaza_serverul(cur):
    """[deficiența 233, comanda Costin 12.10.2026] „Totalurile se calculează automat din componente și se afișează fără câmp.” Coloana
    manuală: un total salvat altfel decât din componentele lui (și o coloană salvată înainte, cu totalurile scrise de mână) se citește cu
    totalurile calculate ca în formular (`bilant.NOMENCLATOR_TOTALURI`). MUTAȚIE: recalcularea scoasă din `coloana_precedenta` -> rd.09 =
    999 -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2025-06-30'), ('1012', 'Capital', 0, 10000, '2025-06-30')")
    _manual(cur, "s1005", 2025, {"F10": _toate("F10", r8=5000, r30=5000, r9=999, r49=1), "F20": _toate("F20", r1=1000, r3=300, r8=5)})
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2025)
    assert (cp["F10"][9], cp["F10"][15], cp["F10"][46], cp["F10"][49]) == (5000, 5000, 5000, 5000), cp["F10"]   # rd.09 = 05+06+07+08
    assert (cp["F20"][8], cp["F20"][9]) == (700, 0), cp["F20"]                          # rd.08 = 01 + 02 − 03 − … (numai dacă e pozitiv)
    assert sorted(ba.componente_formular("s1005")["F20"]) == [1, 2, 3, 4, 5, 6, 7, 302, 303, 304]


def test_def_235_primul_exercitiu_categoria_dupa_regula_entitatilor_nou_infiintate(cur):
    """[deficiența 235, comanda Costin 12.10.2026] „Încadrarea în primul exercițiu se face după regula din OMFP 1802/2014 pentru entitățile
    nou-înființate, fără mesaj roșu. Citează temeiul.” TEMEI: OMFP 1802/2014 pct.22 alin.(1) „În cazul entităților nou-înființate, acestea
    pot întocmi pentru primul exercițiu financiar de raportare situațiile financiare anuale prevăzute fie la pct. 20, fie la pct. 21 sau în
    formatul aplicabil microentităților.” Firma înființată pe 15.03.2026: categoria pe 2026 = `primul_exercitiu`, cu norma citată; pe 2027
    — încadrarea pe criterii (aici „nedeterminata”: 2026 fără rulaje). MUTAȚIE: ramura primului exercițiu scoasă -> „nedeterminata” -> pică."""
    from core import categorie_marime as cm
    cur.execute("UPDATE firma_profil SET data_infiintare = '2026-03-15' WHERE id = 1")
    c = cm.categorie(cur.connection, _SCHEMA, 2026)
    assert (c["categorie"], c["cod_motiv"]) == ("primul_exercitiu", "primul_exercitiu"), c
    assert re.findall(r"OMFP 1802/2014 (pct\.22 alin\.\(1\))", c["motiv"]) == ["pct.22 alin.(1)"], c["motiv"]
    assert re.findall(r"înființat pe (\d\d\.\d\d\.\d{4})", c["motiv"]) == ["15.03.2026"], c["motiv"]
    assert re.findall(r"„(.*?)”", c["motiv"]) == ["În cazul entităților nou-înființate, acestea pot întocmi pentru primul exercițiu "
                                                  "financiar de raportare situațiile financiare anuale prevăzute fie la pct. 20, fie la "
                                                  "pct. 21 sau în formatul aplicabil microentităților."], c["motiv"]
    assert cm.categorie(cur.connection, _SCHEMA, 2027)["categorie"] == "nedeterminata"


def test_s1005_dinaintea_listelor_formularului_nu_e_an_precedent(cur):
    """[C12, C13 — clasa C10] Un S1005 păstrat înainte ca F10 și F20 S1005 să urmeze listele formularului 2025 are rândurile vechi (603–608
    la rd.03, CAM-ul fără rând): nu se folosește ca „An precedent”, iar mesajul spune de ce. MUTAȚIE: verificarea limitată înapoi la S1003
    -> sursa „bilant” -> pică."""
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2023-12-31'), ('1012', 'Capital', 0, 10000, '2023-12-31')")
    _bilant_pastrat(cur, "s1005", "2025", '<Bilant1005><F10 F10_0082="7"/><F20 F20_0032="800"/></Bilant1005>',
                        produs_de="Contabil", verdict="valid")
    cur.execute("UPDATE artefacte_produse SET produs_la = '2026-10-01' WHERE fel = 's1005'")
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2026)
    assert cp["sursa"]["F20"] != "bilant" and cp["bilant_respins"]["numerotare_veche"], cp
    assert re.findall(r"Bilanțul (S100\d) pe (\d{4}) .* rândurile lui sunt (dinaintea rescrierii)", ba.nota_bilant_respins(2026, cp["bilant_respins"])) \
        == [("S1005", "2025", "dinaintea rescrierii")]
