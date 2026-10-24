# -*- coding: utf-8 -*-
"""Lotul 12, pachetul firme2 — salariile: C133 (motivul scutirii de contribuția minimă), C134 (D112 `B_brutSalarii`), C127 (notele de
salarii / amortizare scrise înainte de încheierea lunii).

SURSE (citite la sursă, `anaf_surse/opanaf_605_2026_d112.pdf`, text extras cu `pdftotext -layout`):
- OPANAF 605/2026 anexa 2, secțiunea „Date de identificare ale asiguratului”, pct.12: „Motivul exceptării - se completează în cazul în
  care caseta de la pct.11 a fost completată cu valoarea "1", astfel : "1" - pentru persoana fizică prevăzută la art.146 alin. (5^7)
  lit.a) din Codul fiscal, respectiv, pentru elevi şi studenţi, cu vârsta până la 26 de ani […]; "2" - […] ucenicii, cu vârstă de până la
  18 ani […]; "3" - […] persoana cu dizabilităţi sau alte categorii de persoane cărora prin lege li se recunoaşte posibilitatea de a lucra
  mai puţin de 8 ore pe zi; "4" - […] salariaţii care au calitatea de pensionari pentru limită de vârstă […]; "5" - […] două sau mai multe
  contracte individuale de muncă, a căror baza lunară cumulate […] este cel puţin egală cu salariul de bază minim brut pe ţară”.
- Structura D112 (`anaf_surse/structura_D112_0726_070926.txt`, 9cc `motivExc`): „daca asigExc=1 atunci motivExc = (1-5,null)”.
- OPANAF 605/2026 anexa 2, secțiunea B: „Rândul 4 "Total fond de salarii brute" - se completează cu suma câştigurilor brute realizate de
  asiguraţii înscrişi la "Rândul 2" (venituri de natură salarială, venituri asimilate salariilor, precum şi sumele suportate de angajator,
  primele 5 zile de incapacitate temporară de muncă, pentru concedii medicale conform prevederilor O.U.G. nr. 158/2005 […]), pentru care
  angajatorul datorează contribuţia asiguratorie pentru muncă.”
C127: N/A fiscal — regula 216 (o notă care închide luna se scrie după ce luna s-a încheiat) și regula „nota validată nu se modifică”.
CNP-urile de probă au cifra de control verificată (algoritmul din CLAUDE.md). Scheme efemere din template, șterse la ieșire.
"""
import io
import os
import re

import pytest

from core import db as _db, salariati_api as sa, salariati_import_api as si, tenant_provisioning as _tprov

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_l12_firme2_sal"
CNP1 = "1900101410011"      # cifra de control verificată (test_412_cim_salariat)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


db_necesar = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _campuri(erori):
    return {c for c, _m in erori}


# ── C133: regula pe server (ecran, API) ──────────────────────────────────────────────────────────────────────────────────────────
_BAZA = {"nume": "POP", "cnp": CNP1, "salariu_brut": 3000, "cor": "251401", "tip_norma": "intreaga", "functie_baza": True}


def test_c133_scutit_fara_motiv_se_refuza_la_creare():
    """Scutit = Da fără motiv: refuz pe câmpul `motiv_exceptare` (D112 `asigExc` = 1 numai cu `motivExc` 1–5, OPANAF 605/2026 anexa 2,
    pct.12). ROȘU înainte: niciun refuz — salariatul intra scutit fără motiv, iar D112 îl declara neexceptat."""
    er = sa.valideaza_salariat({**_BAZA, "scutit_contrib_minim": True}, la_creare=True)
    assert "motiv_exceptare" in _campuri(er), er
    assert [m for c, m in er if c == "motiv_exceptare"] == ["Alege motivul scutirii de contribuția minimă — D112 îl declară (CF art.146 alin.(5^7))."]


@pytest.mark.parametrize("motiv", [1, 2, 3, 4, 5])
def test_c133_cele_cinci_motive_se_primesc(motiv):
    # OPANAF 605/2026 anexa 2, pct.12: motivele „1”–„5” (CF art.146 alin.(5^7) lit.a–e)
    assert "motiv_exceptare" not in _campuri(sa.valideaza_salariat({**_BAZA, "scutit_contrib_minim": True, "motiv_exceptare": motiv},
                                                                   la_creare=True))


def test_c133_motiv_in_afara_listei_sau_fara_scutire_se_refuza():
    er = sa.valideaza_salariat({**_BAZA, "scutit_contrib_minim": True, "motiv_exceptare": 6}, la_creare=True)
    assert [m for c, m in er if c == "motiv_exceptare"] == ["Motivul scutirii e unul din cele cinci din listă (OPANAF 605/2026, D112 pct.12)."]
    er = sa.valideaza_salariat({**_BAZA, "scutit_contrib_minim": False, "motiv_exceptare": 4}, la_creare=True)
    assert [m for c, m in er if c == "motiv_exceptare"] == ["Motivul scutirii se alege numai când salariatul e scutit de contribuția minimă."]
    assert "motiv_exceptare" not in _campuri(sa.valideaza_salariat({**_BAZA, "scutit_contrib_minim": False}, la_creare=True))


# ── C133: importul și datele existente ───────────────────────────────────────────────────────────────────────────────────────────
def test_c133_importul_scutit_fara_motiv_intra_marcat_de_verificat():
    """Fișierul spune „scutit: da”, dar n-are motivul: salariatul intră scutit și marcat „de verificat” (motiv_exceptare), cu semnalul pe
    rând. Nescutitul nu se marchează. ROȘU înainte: intra scutit, fără motiv și fără niciun semn."""
    f = ("nume;prenume;cnp;data angajare;brut;judet;persoane in intretinere;scutit contributie minima;norma;functie de baza\n"
         "POPESCU;ANA;%s;2024-01-15;2000;B;0;da;intreaga;da\n" % CNP1).encode("utf-8")
    r = si.extrage(f, "s.csv")
    assert r[0]["scutit_contrib_minim"] is True and "motiv_exceptare" in r[0]["de_verificat"], r[0]
    sem = [x["mesaj"] for x in si.semnale_randuri(r) if x.get("regula") == "motiv_scutire_lipsa"]
    assert sem == ["POPESCU ANA: e scutit de contribuția minimă, dar fișierul nu spune motivul scutirii (D112 îl declară) — salariatul e "
                   "marcat de verificat; motivul îl alegi în Stat de plată, la „De verificat”"], si.semnale_randuri(r)
    nescutit = si.extrage(f.replace(b";da;intreaga", b";nu;intreaga"), "s.csv")[0]
    assert "motiv_exceptare" not in nescutit["de_verificat"]


@pytest.fixture()
def conn_sal():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
        c.rollback()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _salariat(cur, scutit, motiv=None, de_verificat="{}"):
    cur.execute("INSERT INTO salariati (cnp, nume, prenume, data_angajare, scutit_contrib_minim, motiv_exceptare, de_verificat) "
                "VALUES (%s, 'POP', 'ANA', '2024-01-01', %s, %s, %s::text[]) RETURNING id", (CNP1, scutit, motiv, de_verificat))
    return cur.fetchone()[0]


@db_necesar
def test_c133_migrarea_marcheaza_scutitii_fara_motiv_iar_salvarea_motivului_ii_scoate(conn_sal):
    """Datele existente: salariatul scutit fără motiv (scris înainte de reparație) e marcat „de verificat” de
    `core/migrare_motiv_scutire.py`; „De verificat” -> motivul 4 -> `actualizeaza_salariat` îl salvează și scoate marcajul. A doua
    rulare a migrării: nimic. Nescutitul și scutitul cu motiv nu se ating."""
    from core import migrare_motiv_scutire as mig
    with conn_sal.cursor() as cur:
        sid = _salariat(cur, True)
        cur.execute("INSERT INTO salariati (cnp, nume, prenume, data_angajare, scutit_contrib_minim, motiv_exceptare) VALUES "
                    "('1960101078916', 'ION', 'RADU', '2024-01-01', true, 1), ('2900101410012', 'ANA', 'MARIA', '2024-01-01', false, NULL)")
    assert mig.verifica(conn_sal, SCH) is False
    assert mig.aplica(conn_sal, SCH) == [sid]
    assert mig.aplica(conn_sal, SCH) == [] and mig.verifica(conn_sal, SCH) is True
    with conn_sal.cursor() as cur:
        cur.execute("SELECT cnp, de_verificat FROM salariati ORDER BY id")
        assert cur.fetchall() == [(CNP1, ["motiv_exceptare"]), ("1960101078916", []), ("2900101410012", [])]
    assert sa.actualizeaza_salariat(conn_sal, sid, motiv_exceptare=4) == {"ok": True}
    with conn_sal.cursor() as cur:
        cur.execute("SELECT motiv_exceptare, de_verificat FROM salariati WHERE id = %s", (sid,))
        assert cur.fetchone() == (4, [])


@db_necesar
def test_c133_scutirea_pusa_pe_da_cere_motivul_iar_pe_nu_il_goleste(conn_sal):
    with conn_sal.cursor() as cur:
        sid = _salariat(cur, False)
    with pytest.raises(ValueError) as ei:
        sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True)
    # refuzul stă pe câmpul motivului (contractul {detail, erori_campuri}), singurul câmp refuzat
    assert [e["camp"] for e in getattr(ei.value, "erori_campuri", [])] == ["motiv_exceptare"], ei.value
    sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=True, motiv_exceptare=2)
    sa.actualizeaza_salariat(conn_sal, sid, scutit_contrib_minim=False)
    with conn_sal.cursor() as cur:
        cur.execute("SELECT scutit_contrib_minim, motiv_exceptare FROM salariati WHERE id = %s", (sid,))
        assert cur.fetchone() == (False, None)


# ── C133 + C134: D112 ────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def d112_mod(monkeypatch):
    """Fixtura D112 a pachetului ctrl (`test_lot12_ctrl_d112_cm_pensionar`), pe o schemă proprie (nu se calcă cu acel fișier)."""
    from core import test_lot12_ctrl_d112_cm_pensionar as m
    monkeypatch.setattr(m, "_SCHEMA", "test_lot12_firme2_d112")
    return m


@pytest.fixture
def conn_d112(d112_mod):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % d112_mod._SCHEMA)
            c.commit()


@db_necesar
def test_c133_d112_refuza_salariatul_scutit_fara_motiv(d112_mod, conn_d112):
    """Fișa veche (scutit, fără motiv) oprește D112 și numește salariatul. ROȘU înainte: D112 ieșea cu `asigExc` 0 pentru el."""
    with pytest.raises(ValueError) as ei:
        d112_mod._genereaza(conn_d112, [{**d112_mod._ION}, {**d112_mod._PENS, "motiv": None}])
    assert str(ei.value) == ("D112 nu se poate genera: un salariat e scutit de contribuția minimă fără motivul scutirii (D112 îl declară, "
                             "OPANAF 605/2026 anexa 2, pct.12). Alege-l în Stat de plată, la „De verificat”: PENSIONAR (CNP 1500303410017).")


@db_necesar
def test_c134_fondul_de_salarii_brute_cuprinde_indemnizatia_angajatorului(d112_mod, conn_d112):
    """POPESCU, 6.000 lei, certificat cod 01 de 5 zile (4 plătite de angajator, 1.000 lei): salariul realizat 6.000 × 17 / 22 = 4.636,36
    -> 4.636; rândul 4 al secțiunii B = 4.636 + 1.000 = 5.636 = C4_baza. ROȘU înainte: 4.636 (fără indemnizația angajatorului). DUK
    valid."""
    xml, _res = d112_mod._genereaza(conn_d112, [d112_mod._POP], [d112_mod._CM])
    st = d112_mod.structura(xml)
    b, c4 = d112_mod.unic(st["_angajator"], "angajatorB"), d112_mod.unic(st["_angajator"], "angajatorC4")
    # OPANAF 605/2026 anexa 2, secțiunea B, rândul 4: „… precum şi sumele suportate de angajator, primele 5 zile de incapacitate …”
    assert int(b["B_brutSalarii"]) == 5636 == int(c4["C4_baza"]), (b, c4)
    d112_mod._duk_valid(xml)


@db_necesar
def test_c134_partea_fnuass_nu_intra_in_fondul_de_salarii(d112_mod, conn_d112):
    """Aceeași lună, indemnizația integral din FNUASS: rândul 4 = salariul realizat 4.636 (angajatorul n-a suportat nimic). DUK valid."""
    cm_fnuass = d112_mod._CM.replace("'01',5,4,0,1000,0,", "'01',5,0,4,0,1000,")
    xml, _res = d112_mod._genereaza(conn_d112, [d112_mod._POP], [cm_fnuass])
    b = d112_mod.unic(d112_mod.structura(xml)["_angajator"], "angajatorB")
    assert int(b["B_brutSalarii"]) == 4636, b
    d112_mod._duk_valid(xml)


# ── C127: notele scrise înainte de încheierea lunii ─────────────────────────────────────────────────────────────────────────────
def _nota(cur, data, status, sursa, creat_la, desc):
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref, creat_la) VALUES (%s, %s, %s, 'ciorna', %s, %s) "
                "RETURNING id", (data, desc, sursa, "Stat de plată " + desc, creat_la))
    iid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '641', '421', 5000)", (iid,))
    if status == "validata":
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (iid,))
    return iid


@db_necesar
def test_c127_ciorna_scrisa_inainte_de_incheierea_lunii_se_scoate_validata_se_semnaleaza(conn_sal):
    """F5 înainte de reparație: ciorna „Salariile lunii 10/2026” scrisă pe 08.10.2026 și nota VALIDATĂ „Stat de plata 11/2026” scrisă pe
    06.10.2026 (perioade sintetice: 2099). Migrarea scoate ciorna (urma în `public.audit_log`), nu atinge nota validată; semnalul de pe
    rând o numește. Nota scrisă după încheierea lunii (salariile 09/2099, scrise pe 02.10.2099) nu se atinge și nu se semnalează."""
    from core import inchidere_luna as il, migrare_note_luna_neincheiata as mig
    with conn_sal.cursor() as cur:
        c10 = _nota(cur, "2099-10-31", "ciorna", "salarii", "2099-10-08 14:34:55+03", "SAL 10/2099")
        v11 = _nota(cur, "2099-11-28", "validata", "salarii", "2099-10-06 12:14:43+03", "11/2099")
        ok9 = _nota(cur, "2099-09-30", "validata", "salarii", "2099-10-02 10:00:00+03", "SAL 09/2099")
        am = _nota(cur, "2099-10-31", "ciorna", "amortizare", "2099-10-31 23:59:00+02", "AMORT 10/2099")
        sem = il.note_contate_inainte(cur, SCH)
    assert set(sem) == {c10, v11, am}, sem
    assert sem[v11]["motiv"] == ("Nota a fost scrisă pe 06.10.2099, înainte ca luna 11/2099 să se încheie: cifrele ei pot să nu cuprindă tot "
                                 "ce s-a întâmplat în lună. Verific-o față de documentul lunii (statul de plată, registrul mijloacelor fixe); "
                                 "o diferență se corectează printr-o notă de corecție — nota validată nu se modifică.")
    r = mig.aplica(conn_sal, SCH)
    assert r == {"scoase": [c10, am], "validate": [(v11, "11/2099")], "ramase": []}, r
    with conn_sal.cursor() as cur:
        cur.execute("SELECT id, status FROM inregistrari ORDER BY id")
        assert cur.fetchall() == [(v11, "validata"), (ok9, "validata")]
        cur.execute("SELECT detalii->>'descriere', detalii->'linii' FROM public.audit_log WHERE actiune = 'stergere_ciorna_luna_neincheiata' "
                    "AND detalii->>'schema' = %s ORDER BY entitate_id", (SCH,))
        assert cur.fetchall() == [("SAL 10/2099", [["641", "421", "5000.00"]]), ("AMORT 10/2099", [["641", "421", "5000.00"]])]
        assert set(il.note_contate_inainte(cur, SCH)) == {v11}
    assert mig.verifica(conn_sal, SCH) is True
    assert mig.aplica(conn_sal, SCH) == {"scoase": [], "validate": [(v11, "11/2099")], "ramase": []}


@db_necesar
def test_c127_ciorna_din_luna_blocata_ramane_si_se_numeste(conn_sal):
    from core import migrare_note_luna_neincheiata as mig
    with conn_sal.cursor() as cur:
        c = _nota(cur, "2099-08-31", "ciorna", "salarii", "2099-08-20 10:00:00+03", "SAL 08/2099")
        cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2099, 8)")
    r = mig.aplica(conn_sal, SCH)
    assert r["scoase"] == [] and [i for i, _m in r["ramase"]] == [c], r
    assert re.match(r"^PERIOADA_BLOCATA", r["ramase"][0][1]), r
