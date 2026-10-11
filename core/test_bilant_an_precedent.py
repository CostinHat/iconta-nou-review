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
    from core import artefacte
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2024-12-31'), ('1012', 'Capital', 0, 10000, '2024-12-31')")
    _nota(cur, datetime.date(2025, 3, 10), "5121", "704", Decimal("2000"))
    xml_2025 = '<Bilant1005><F10 F10_0081="7000" F10_0082="7777"/><F20 F20_0012="555"/></Bilant1005>'
    artefacte.pastreaza(cur.connection, _SCHEMA, "s1005", "2025", xml_2025, produs_de="Contabil", verdict="valid")
    artefacte.pastreaza(cur.connection, _SCHEMA, "s1005", "2025", xml_2025.replace("7777", "1"), produs_de="Contabil", verdict="erori")
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
    from core import artefacte
    cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES "
                "('5121', 'Banca', 10000, 0, '2026-08-31'), ('1012', 'Capital', 0, 10000, '2026-08-31')")
    artefacte.pastreaza(cur.connection, _SCHEMA, "s1005", "2025", '<Bilant1005><F10 F10_0081="10000" F10_0082="10000"/><F20/></Bilant1005>',
                        produs_de="Contabil", verdict="valid")
    cp = ba.coloana_precedenta(cur, _SCHEMA, "s1005", 2026)
    assert cp["sursa"] == {"F10": None, "F20": None} and cp["bilant_respins"]["exemplar"] == 1, cp
    with pytest.raises(ValueError, match=r"Bilanțul pe 2025 păstrat în aplicație .* nu se folosește: soldurile de preluare sunt de la 31\.08\.2026"):
        ba.coloanele(cur, _SCHEMA, "s1005", 2026, [])
