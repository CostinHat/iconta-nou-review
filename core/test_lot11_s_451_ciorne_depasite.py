# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 451, PRIORITAR — comanda Costin 11.1 pct.6, verbatim] „ciornele generate înainte de o reparație rămân validabile
cu regula veche. Cazuri: ieșirea Marfa A din Z 0042 cu «Bon de consum nr 1», F1; ciorna salariilor 10/2026 cu alte sume decât statul
curent, F5 (448). Toate trebuie refăcute din sursă sau marcate depășite și oprite de la validare, pe toate firmele.”

Mecanismul (`core/ciorne_depasite.py`): la validare, ciorna derivată se regenerează pe uscat din sursa ei și se compară pe data,
documentul, conturile și sumele; diferă -> refuz `NOTA_DEPASITA`, cu refacerea din sursă. Fiecare regenerator e probat în ambele
direcții: ciorna scrisă cu regula de ACUM trece (fără fals pozitiv), ciorna scrisă cu regula VECHE (reprodusă prin monkeypatch pe funcția
regulii, nu prin INSERT-uri care ar ocoli drumul) e oprită. Temei: OMFP 2634/2015 pct.58 lit.c — „fiecare dată înregistrată în
contabilitate trebuie să se regăsească în conținutul unui document”.

Schemă efemeră din `tenant_template.sql`, în tranzacție anulată; date în 2099 (sintetic). CUI 14399840 (DANTE INTERNATIONAL SA, cifra de
control verificată cu algoritmul din CLAUDE.md)."""
import io
import os
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot11_s_451"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_Z = "Raport Z nr 0042 din 20.10.2099 (casa 8000000001)"


def _azi():
    """Ziua în care testul a scris nota („generată pe …” din mesaj), în formatul românesc ZZ.LL.AAAA."""
    import datetime as _dt
    a = _dt.date.today()
    return "%02d.%02d.%d" % (a.day, a.month, a.year)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'S451 SRL', '14399840', 'cantitativ_valoric') "
                            "ON CONFLICT (id) DO UPDATE SET metoda_stoc = 'cantitativ_valoric'")
            yield c
        finally:
            c.rollback()


def _articol(conn, den="Marfa A", cant=100, pret="50"):
    from core import stocuri_cv_api as cva
    r = cva.intrare(conn, SCH, {"denumire": den, "um": "buc", "data": "2099-10-01", "cantitate": cant, "pret_unitar": pret,
                                "document": "NIR nr 1 din 01.10.2099"})
    assert "eroare" not in r, r
    return r["articol_id"]


def _z(cur):
    """Raportul Z ciornă, cum îl scrie ruta tastată (nota + casa)."""
    from core import repo_contabilitate as rc
    iid = rc.nota_horeca_z_ciorna(cur, SCH, "2099-10-20", "Z-8000000001-0042", "Raport Z 2099-10-20 casa 8000000001 nr 0042", DOC_Z)[0]
    rc.adauga_linie_3(cur, SCH, iid, "5311", "707", 121)
    rc.adauga_linie_3(cur, SCH, iid, "707", "4427", 21)
    rc.adauga_z_amef(cur, SCH, iid, "8000000001", 3)
    return iid


def _iesire_z(conn, regula_veche, monkeypatch):
    """Descărcarea Z-ului pe articol, pe drumul aplicației (`stocuri_cv_api.iesire` cu `z_id`); cu `regula_veche`, documentul se ia cu regula
    de dinainte de 438 (fără documentul Z-ului: bonul de consum) — exact cum a scris-o F1 pe 20.10.2026 (nota 163)."""
    from core import stocuri_cv_api as cva
    aid = _articol(conn)
    with conn.cursor() as cur:
        zid = _z(cur)
    if regula_veche:
        monkeypatch.setattr(cva, "document_iesire", lambda cur, schema, document_scris, z_id: str(document_scris or "").strip() or None)
    r = cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-20", "cantitate": 2, "z_id": zid})
    monkeypatch.undo()
    assert r and "eroare" not in r, r
    return r["inregistrare_id"], zid


def _doc(conn, nid):
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (nid,))
        return cur.fetchone()[0]


def test_def_451_iesirea_din_z_cu_bon_de_consum_e_depasita_si_se_reface(conn, monkeypatch):
    """Cazul F1 (Z 0042, «Bon de consum nr 1»): roșu înainte — validarea trecea; acum refuz numit, refacere, validare."""
    from core import ciorne_depasite as cd, jurnal_api as _j, stocuri_cv_api as cva
    nid, _zid = _iesire_z(conn, True, monkeypatch)
    assert _doc(conn, nid).startswith("Bon de consum nr ")
    rez = _j.valideaza(conn, SCH, nid)
    # OMFP 2634/2015 pct.58 lit.c: nota trebuie să se regăsească în documentul ei — vânzarea de pe Z are documentul Z-ului (438)
    assert rez.get("cod") == cd.COD, rez
    d = rez["depasita"]
    assert d["sursa_fel"] == "stoc_iesire" and d["sursa"] == "raportul Z" and d["refacere"]["actiune"] == "POST /tenants/{tenant_id}/jurnal/{nota_id}/reface"
    assert [x["ce"] for x in d["diferente"]] == ["documentul justificativ"] and DOC_Z in d["diferente"][0]["acum"], d
    # mesajul întreg, pe câmpul `eroare` (core/test_garzi_pe_text.py): spune de ce e depășită și de unde se reface
    assert rez["eroare"] == (
        "Nota din 20.10.2099 a fost generată pe %s după o regulă care s-a schimbat de atunci: acum raportul Z ar scrie documentul "
        "justificativ «%s» (pe ciornă: «Bon de consum nr 1 din 20.10.2099»). Nota e depășită și nu se validează — refă-o din "
        "raportul Z („Refă nota din mișcarea de stoc”), apoi valideaz-o." % (_azi(), DOC_Z)), rez["eroare"]
    nou = cva.reface_nota_miscare(conn, SCH, nid)["nota_id"]
    assert _doc(conn, nou) == DOC_Z
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM inregistrari WHERE id = %s", (nid,))
        assert cur.fetchone()[0] == 0   # ciorna veche a fost înlocuită
        cur.execute("SELECT inregistrare_id, document FROM miscari_stoc WHERE inregistrare_id = %s", (nou,))
        assert cur.fetchone()[1] == DOC_Z   # mișcarea poartă nota nouă și documentul ei (fișa de magazie)
    assert _j.valideaza(conn, SCH, nou) == {"ok": True}


def test_451_iesirea_scrisa_cu_regula_de_acum_trece(conn, monkeypatch):
    """Fără fals pozitiv: Z, factură, manuală fără document (bon de consum), manuală cu documentul omului."""
    from core import ciorne_depasite as cd, jurnal_api as _j, stocuri_cv_api as cva
    nid, _zid = _iesire_z(conn, False, monkeypatch)
    aid = _articol(conn, "Marfa M")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, status, total, tva) VALUES ('12', 'FCT', '2099-10-21', "
                    "'emisa', 'emisa', 100, 0) RETURNING id")
        fid = cur.fetchone()[0]
    fact = cva.descarca_factura(conn, SCH, fid, "2099-10-21")   # fără linii cu articol: nimic de descărcat
    assert fact["descarcate"] == []
    ies_f = cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-21", "cantitate": 1,
                                   "document": _j.eticheta_factura("factura", "FCT", "12", "2099-10-21")}, factura_id=fid)
    ies_b = cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-22", "cantitate": 1})
    ies_o = cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-23", "cantitate": 1, "document": "Proces-verbal de casare nr 3"})
    with conn.cursor() as cur:
        for x in (nid, ies_f["inregistrare_id"], ies_b["inregistrare_id"], ies_o["inregistrare_id"]):
            assert cd.felul(cur, SCH, x) == "stoc_iesire"
            assert cd.verifica(conn, cur, SCH, x) is None, (x, cd.verifica(conn, cur, SCH, x))
    for x in (nid, ies_f["inregistrare_id"], ies_b["inregistrare_id"], ies_o["inregistrare_id"]):
        assert _j.valideaza(conn, SCH, x) == {"ok": True}


def test_451_returul_cu_alt_document_decat_regula_e_depasit(conn):
    """Returul la stornare (F1, nota 170, scris de reparația pe date cu «Stornare factura F1A nr. 8 …»): regula aplicației dă
    «Retur la <factura de stornare>» — depășit; refăcut, trece."""
    from core import ciorne_depasite as cd, jurnal_api as _j, stocuri_cv_api as cva
    aid = _articol(conn, "Marfa B", 20, "27.50")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, status, total, tva) VALUES ('8', 'F1A', '2099-10-19', "
                    "'emisa', 'emisa', 27.5, 0) RETURNING id")
        f8 = cur.fetchone()[0]
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, status, total, tva, storno_din_id) VALUES ('9', 'F1A', "
                    "'2099-10-19', 'emisa', 'emisa', -27.5, 0, %s) RETURNING id", (f8,))
        f9 = cur.fetchone()[0]
    cva.iesire(conn, SCH, {"articol_id": aid, "data": "2099-10-19", "cantitate": 1,
                           "document": _j.eticheta_factura("factura", "F1A", "8", "2099-10-19")}, factura_id=f8)
    vechi = cva.retur_la_stornare(conn, SCH, f8, f9, "2099-10-19", "Stornare factura F1A nr. 8 din 19.10.2099")[0]["inregistrare_id"]
    with conn.cursor() as cur:
        d = cd.verifica(conn, cur, SCH, vechi)
    assert d and d["sursa_fel"] == "stoc_retur" and d["diferente"] == [
        {"ce": "documentul justificativ", "acum": "«Retur la Factură F1A nr. 9 din 19.10.2099»",
         "pe_ciorna": "«Stornare factura F1A nr. 8 din 19.10.2099»"}], d
    nou = cva.reface_nota_miscare(conn, SCH, vechi)["nota_id"]
    assert _doc(conn, nou) == "Retur la Factură F1A nr. 9 din 19.10.2099"
    assert _j.valideaza(conn, SCH, nou) == {"ok": True}


def _stat(an=2099, luna=10, sume=(("641", "421", Decimal("12045.45")), ("421", "4315", Decimal("3011.00")))):
    return {"note": [{"debit": d, "credit": c, "suma": float(s)} for d, c, s in sume], "document_ref": "SAL %02d/%d" % (luna, an)}


def _nota_stat(cur, sume, an=2099, luna=10):
    """Nota statului, scrisă cum o scrie `uc_tenants.salarii_contare_scrie` (antetul `salarii_contare.antet_nota`, rândurile propunerii)."""
    from core import repo_contabilitate as rc, salarii_contare as sc
    data, nr, descr, doc = sc.antet_nota(an, luna)
    nid = rc.nota_cu_sursa_si_status(cur, data, nr, descr, "salarii", "ciorna", doc)[0]
    for d, c, s in sume:
        rc.adauga_linie_fara_schema(cur, nid, d, c, s)
    return nid


def test_def_451_ciorna_salariilor_cu_alte_sume_decat_statul_e_depasita(conn, monkeypatch):
    """Cazul F5 (448): ciorna 10 cu 641 = 421 12.045,45, statul de acum 11.860,79 (concediul medical) -> refuz cu ambele cifre."""
    from core import ciorne_depasite as cd, jurnal_api as _j, salarii_contare as sc
    vechi = (("641", "421", Decimal("12045.45")), ("421", "4315", Decimal("3011.00")))
    acum = (("641", "421", Decimal("11860.79")), ("421", "4315", Decimal("2965.00")), ("6458", "423", Decimal("262.00")))
    with conn.cursor() as cur:
        nid = _nota_stat(cur, vechi)
    monkeypatch.setattr(sc, "propunere", lambda conn, schema, an, luna: _stat(an, luna, acum))
    rez = _j.valideaza(conn, SCH, nid)
    assert rez.get("cod") == cd.COD and rez["depasita"]["sursa_fel"] == "salarii", rez
    rand = rez["depasita"]["diferente"][0]
    assert rand == {"ce": "rândurile", "acum": "421 = 4315 2.965,00; 641 = 421 11.860,79; 6458 = 423 262,00",
                    "pe_ciorna": "421 = 4315 3.011,00; 641 = 421 12.045,45"}, rand
    assert rez["eroare"] == (
        "Nota din 31.10.2099 a fost generată pe %s după o regulă care s-a schimbat de atunci: acum statul de plată 10/2099 ar scrie "
        "rândurile 421 = 4315 2.965,00; 641 = 421 11.860,79; 6458 = 423 262,00 (pe ciornă: 421 = 4315 3.011,00; 641 = 421 12.045,45). "
        "Nota e depășită și nu se validează — refă-o din statul de plată 10/2099 („Refă nota din statul de plată”), apoi valideaz-o."
        % _azi()), rez["eroare"]


def test_451_ciorna_salariilor_la_zi_trece_si_data_veche_e_prinsa(conn, monkeypatch):
    """La zi -> trece. Ziua 28 (regula de dinainte de lotul 07.10 pct.7) în loc de ultima zi -> depășită pe dată."""
    from core import ciorne_depasite as cd, salarii_contare as sc
    sume = (("641", "421", Decimal("11860.79")), ("421", "4315", Decimal("2965.00")))
    monkeypatch.setattr(sc, "propunere", lambda conn, schema, an, luna: _stat(an, luna, sume))
    with conn.cursor() as cur:
        nid = _nota_stat(cur, sume)
        assert cd.verifica(conn, cur, SCH, nid) is None
        cur.execute("UPDATE inregistrari SET data = '2099-10-28' WHERE id = %s", (nid,))
        d = cd.verifica(conn, cur, SCH, nid)
    assert d and [x["ce"] for x in d["diferente"]] == ["data"] and d["diferente"][0]["acum"] == "31.10.2099", d


def test_451_sursa_care_nu_mai_poate_scrie_nota_o_marcheaza_depasita(conn, monkeypatch):
    """Statul nu se mai poate contabiliza (D112 negenerabil): ciorna e depășită, cu motivul, și nu se validează."""
    from core import ciorne_depasite as cd, jurnal_api as _j, salarii_contare as sc
    with conn.cursor() as cur:
        nid = _nota_stat(cur, (("641", "421", Decimal("100.00")),))

    def _nu(conn, schema, an, luna):
        raise ValueError("profilul firmei nu are codul CAEN")
    monkeypatch.setattr(sc, "propunere", _nu)
    rez = _j.valideaza(conn, SCH, nid)
    assert rez.get("cod") == cd.COD and rez["depasita"]["neregenerabila"] is True, rez
    assert rez["eroare"] == (
        "Nota din 31.10.2099 a fost generată pe %s, după regula de atunci, iar sursa ei nu o mai poate scrie acum: statul de plată "
        "10/2099 nu se mai poate contabiliza acum: profilul firmei nu are codul CAEN. Nota e depășită și nu se validează — corectează "
        "sursa, apoi generează nota din nou." % _azi()), rez["eroare"]


def test_451_amortizarea_cu_alt_registru_e_depasita(conn):
    from core import amortizare_lunii as al, ciorne_depasite as cd, repo_contabilitate as rc, uc_comun as uc
    with conn.cursor() as cur:
        cur.execute("INSERT INTO mijloace_fixe (cod, denumire, valoare, dnf_luni, data_pif, metoda) VALUES ('MF1', 'Laptop', 6000, 60, "
                    "'2099-01-15', 'liniara') RETURNING id")
        mf = cur.fetchone()[0]
        linii = al.linii(cur, SCH, 2099, 10)
        assert linii and linii[0][0] == "2813"
        nid = rc.nota_amortizare_ciorna(cur, SCH, uc.ultima_zi_a_lunii(2099, 10), al.numar(2099, 10), "Amortizare 10/2099")[0]
        for c, r, _d in linii:
            rc.adauga_linie_cheltuiala_amortizare(cur, SCH, nid, c, r)
        assert cd.felul(cur, SCH, nid) == "amortizare" and cd.verifica(conn, cur, SCH, nid) is None
        cur.execute("UPDATE mijloace_fixe SET valoare = 12000 WHERE id = %s", (mf,))   # registrul s-a schimbat după generare
        d = cd.verifica(conn, cur, SCH, nid)
    assert d and d["sursa_fel"] == "amortizare" and d["diferente"][0]["ce"] == "rândurile", d


def test_451_validarea_interna_si_in_masa_trec_prin_aceeasi_poarta(conn, monkeypatch):
    """Validarea internă (PFA) și cea din coadă cheamă `jurnal_api.valideaza`: refuzul ajunge cu codul lui."""
    from core import ciorne_depasite as cd, jurnal_api as _j
    nid, _ = _iesire_z(conn, True, monkeypatch)
    validate, refuzate = _j.valideaza_interne(conn, SCH, [nid], cu_cod=True)
    assert validate == [] and refuzate[0][0] == nid and refuzate[0][2] == cd.COD, refuzate


def test_451_ruta_refacerii_refuza_firma_fara_acces():
    """Ruta `POST /tenants/{tenant_id}/jurnal/{nota_id}/reface` (`main.jurnal_reface` -> `uc_tenants.jurnal_reface`): firma fără acces ->
    Inexistent, nimic scris. (Refacerea însăși e probată mai sus, pe funcția ei, și în browser: `e2e_lot11_s.py`.)"""
    from core import erori, uc_tenants
    with pytest.raises(erori.Inexistent):
        uc_tenants.jurnal_reface(-1, 1, {"uid": -1, "rol": "patron", "firm": -1})
    with pytest.raises(erori.Inexistent):
        uc_tenants.jurnal_depasita(-1, 1, {"uid": -1, "rol": "patron", "firm": -1})


# ── GARDA INVENTARULUI: o sursă nouă de notă nu poate apărea fără rând în `SURSE` ─────────────────────────────────────────────────────────
def test_garda_fiecare_fel_de_sursa_are_starea_lui():
    """MUTAȚIE: rândul „nir” scos din `SURSE` -> pică. Felurile = documentele din `note_derivate.UNDE` (cu „stoc” despărțit în felurile
    lui) + închiderea anului + variantele fără număr ale statului / amortizării."""
    from core import ciorne_depasite as cd, note_derivate as nd
    feluri = (set(nd.UNDE) - {"stoc", "salarii", "amortizare"}) | {"stoc_iesire", "stoc_retur", "inventar", "stoc_alt", "salarii",
                                                                     "salarii_alt", "amortizare", "amortizare_alt", "inchidere_an"}
    assert feluri - set(cd.SURSE) == set(), feluri - set(cd.SURSE)
    assert set(cd.REGENERATOARE) == {f for f, (st, _m) in cd.SURSE.items() if st == cd.REGENERAT}
    assert all(m.strip() for _st, m in cd.SURSE.values())


def test_garda_fiecare_sursa_scrisa_de_cod_e_clasificata():
    """O sursă nouă de notă scrisă în cod (`INSERT INTO … inregistrari (… sursa …)`, scanarea lui 245) fără rând în `SURSA_NOTEI` pică:
    trebuie spus din ce feluri de documente poate deriva — sau că e nederivată."""
    from core import ciorne_depasite as cd
    from core.test_jurnal_sursa_eticheta import surse_scrise
    fara = sorted(set(surse_scrise()) - set(cd.SURSA_NOTEI))
    assert fara == [], fara
    assert all(f in cd.SURSE for v in cd.SURSA_NOTEI.values() for f in v), cd.SURSA_NOTEI
