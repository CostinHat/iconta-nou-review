# -*- coding: utf-8 -*-
"""GARD R193 — întrebarea către modelul AI se pune cu pool-ul liber (comanda Costin 10.10.2026 pct.2).

Costin, verbatim: „R193: da, cele 10 căi care cer un răspuns AI ținând o conexiune la bază se mută înaintea conexiunii.”

Clichetul C5 (`test_val3_contracte.CLICHET_C5 = 0`) păzește forma codului, static. Proba de aici e cealaltă jumătate: rutele
reale, pe o schemă efemeră din `tenant_template.sql`, cu `db.get_conn` numărat — în clipa în care modelul e întrebat se citește
câte conexiuni sunt împrumutate. Trebuie să fie zero. Și simetric: răspunsul ajunge totuși pe factură (cota, contul de venit),
iar o linie fără răspuns pregătit se refuză ca nedeterminată — nu se întreabă modelul de sub conexiune.

Temei: N/A — regula e de capacitate (pool-ul are 10 conexiuni, R178), nu fiscală. Cota și contul vin din răspunsul modelului ca
până acum; regula lor (CF art.291, OMFP 1802/2014) nu se schimbă aici.
"""
import contextlib

import pytest

from core import db as _db, tenant_provisioning as _tp

_SCHEMA = "test_r193_model"
_RASPUNS = '{"cota": 21, "categorie": "standard", "tip": "servicii", "justificare": "regula standard", "incredere": "mare"}'


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def mediu(monkeypatch):
    """Schema efemeră (plătitor TVA, serie de facturi), o singură conexiune reală anulată la final, `get_conn` numărat, modelul
    simulat care notează câte conexiuni erau împrumutate când a fost întrebat."""
    from core import ai_client, uc_comun, facturi_api
    _db.init_pool()
    stare = {"imprumutate": 0, "la_model": []}
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
            cur.execute("SET search_path TO %s, public" % _SCHEMA)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,tip_decont,"
                        "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris) VALUES (1,'R193 SRL',"
                        "'14399840','Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001','micro',true,'L','Pop','Ion',"
                        "'administrator','SRL',200)")
        facturi_api.seteaza_numerotare(c, serie="RM", numar_start=1)

        @contextlib.contextmanager
        def _gc(*a, **k):
            stare["imprumutate"] += 1
            try:
                yield _FaraCommit(c)
            finally:
                stare["imprumutate"] -= 1

        def _model(prompt, **k):
            stare["la_model"].append(stare["imprumutate"])
            return _RASPUNS
        monkeypatch.setattr(_db, "get_conn", _gc)
        monkeypatch.setattr(ai_client, "disponibil", lambda: True)
        monkeypatch.setattr(ai_client, "genereaza_text", _model)
        monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: _SCHEMA)
        monkeypatch.setattr(uc_comun, "_platitor_tva_tert", lambda *a, **k: None)   # ANAF, în afara probei
        stare["conn"] = c
        try:
            yield stare
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _emitere(**k):
    import main
    linie = dict({"descriere": "Mentenanta platforma web", "cantitate": 1, "pret_unitar": 100, "um": "buc"}, **k)
    return main.EmitereIn(linii=[linie], tert_nume="Client R193 SRL", tert_cui="14399840", data_emitere="2026-10-10")


def test_emiterea_intreaba_modelul_inaintea_conexiunii_si_foloseste_raspunsul(mediu):
    """Linie fără cotă și fără cont de venit, produs nou, denumire fără cuvânt-cheie: emiterea are nevoie de model de două ori
    (cota, contul). Întrebat O dată, cu zero conexiuni împrumutate; factura poartă 21% și 704 (servicii).
    MUTAȚIE: `_potriveste_linii` întreabă iar modelul (`cote_tva.potriveste_cota`) -> modelul vede o conexiune -> pică."""
    from core import uc_tenants
    r = uc_tenants.facturi_emite(1, _emitere(), {"uid": 1})
    assert mediu["la_model"] == [0], "modelul a fost întrebat cu conexiuni împrumutate: %s" % mediu["la_model"]
    with mediu["conn"].cursor() as cur:
        cur.execute("SELECT cota_tva::int, cont_venit FROM %s.factura_linii WHERE factura_id = %%s" % _SCHEMA, (r["factura_id"],))
        assert cur.fetchall() == [(21, "704")]


def test_fara_raspuns_pregatit_linia_e_nedeterminata_nu_se_intreaba_sub_conexiune(mediu):
    """Emiterea direct, fără răspunsuri (ca un apelant care le-ar uita): modelul NU e întrebat, iar linia se refuză cu cota
    nedeterminată — ca la un model indisponibil. MUTAȚIE: `cote_tva.raspuns` întreabă modelul la răspuns lipsă -> pică."""
    from core import facturi_api
    with _db.get_conn(_SCHEMA) as conn:
        with pytest.raises(ValueError, match="cota TVA nedeterminată"):
            facturi_api.emite_factura(conn, [{"descriere": "Mentenanta platforma web", "cantitate": 1, "pret_unitar": 100}],
                                      tert_nume="Client R193 SRL", tert_cui="14399840", data_emitere="2026-10-10")
    assert mediu["la_model"] == []


def test_produsul_nou_si_propunerea_intreaba_modelul_cu_pool_ul_liber(mediu):
    """`POST /produse` și `POST /produse/potriveste`: modelul întrebat cu zero conexiuni; produsul din nomenclator nu-l mai
    întreabă deloc. MUTAȚIE: `produse_api.creeaza` cheamă iar `cote_tva.potriveste_cota` -> pică."""
    import main
    from core import uc_tenants
    r = uc_tenants.produse_creeaza(1, main.ProdusCreeazaIn(denumire="Mentenanta platforma web"), {"uid": 1})
    assert r["ok"] and r["cota_tva"] == 21 and mediu["la_model"] == [0], (r, mediu["la_model"])
    p = uc_tenants.produse_potriveste(1, "Abonament suport tehnic", {"uid": 1})
    assert p["cota"] == 21 and mediu["la_model"] == [0, 0], (p, mediu["la_model"])
    p = uc_tenants.produse_potriveste(1, "Mentenanta platforma web", {"uid": 1})
    assert p["sursa"] == "nomenclator" and mediu["la_model"] == [0, 0], "produsul din nomenclator a întrebat modelul"


def test_proforma_transformata_intreaba_modelul_inaintea_conexiunii(mediu):
    """`POST /facturi/{id}/transforma`: liniile proformei se citesc scurt, modelul (contul de venit al liniei fără cont) se întreabă
    cu pool-ul liber. Cota e mereu pe linie (`factura_linii.cota_tva NOT NULL`), deci întrebarea e pentru cont."""
    from core import uc_tenants
    pf = uc_tenants.facturi_emite(1, _emitere(tip="factura", cota_tva=21, cont_venit="704"), {"uid": 1})
    with mediu["conn"].cursor() as cur:
        cur.execute("UPDATE %s.facturi SET tip = 'proforma' WHERE id = %%s" % _SCHEMA, (pf["factura_id"],))
        cur.execute("UPDATE %s.factura_linii SET cont_venit = NULL WHERE factura_id = %%s" % _SCHEMA,
                    (pf["factura_id"],))
    r = uc_tenants.proforma_transforma(1, pf["factura_id"], {"uid": 1})
    assert r["ok"] and mediu["la_model"] == [0], (r, mediu["la_model"])


def test_povestea_si_tiparele_intreaba_modelul_dupa_ce_conexiunile_s_au_inchis(mediu, monkeypatch):
    """`POST /pachete/{id}/genereaza` și `GET /tipare/ai`: citirea întâi, modelul cu conexiunile închise."""
    from core import uc_pachete, uc_tipare, pachete_api, tipare_api, uc_comun
    monkeypatch.setattr(uc_comun, "_pachet_schema", lambda *a, **k: _SCHEMA)
    monkeypatch.setattr(pachete_api, "date_poveste", lambda *a, **k: {"rezumat": {"venituri": 0, "cheltuieli": 0, "rezultat": 0,
                                                                               "tip": "neutru", "declaratii_depuse": []},
                                                                    "restante": None})
    monkeypatch.setattr(pachete_api, "_prompt_poveste", lambda *a, **k: "p")
    monkeypatch.setattr(pachete_api, "abateri_termeni", lambda *a, **k: [])
    monkeypatch.setattr(pachete_api, "scoate_afirmatii_fara_sursa", lambda t, rz: (t, []))
    uc_pachete.pachet_genereaza(1, 2026, 9, {"uid": 1})
    monkeypatch.setattr(tipare_api, "tipare", lambda *a, **k: {"are_date": True, "motive": [{"motiv": "CIF", "n": 2}],
                                                                "tipuri": [], "firme": []})
    uc_tipare.tipare_ai_panou({"firm": 1})
    assert mediu["la_model"] == [0, 0], mediu["la_model"]


def test_magazinul_intreaba_modelul_cu_pool_ul_liber_si_citeste_platitorul_din_profil(mediu, monkeypatch):
    """`POST /woocommerce/sincronizeaza`: modelul întrebat cu zero conexiuni. Și: emiterea primește acum statutul de plătitor din
    profil — până azi lua implicitul `True`, deci o firmă neplătitoare ar fi facturat cu TVA (CF art.310 alin.(10) lit.b): cel care
    aplică regimul de scutire „nu are voie să menționeze taxa pe factură”). MUTAȚIE: `platitor_tva=platitor` scos din `_importa`
    -> factura neplătitorului iese cu 21% -> pică."""
    from core import woocommerce
    comanda = {"number": 501, "date_created": "2026-10-09T10:00:00", "currency": "RON", "total": "100",
               "billing": {"first_name": "Ana", "last_name": "Pop"},
               "line_items": [{"name": "Mentenanta platforma web", "quantity": 1, "total": "100"}]}
    monkeypatch.setattr(woocommerce, "comenzi", lambda *a, **k: [comanda])
    with mediu["conn"].cursor() as cur:
        cur.execute("UPDATE %s.firma_profil SET wc_url='https://magazin.invalid', wc_ck='ck', wc_cs='cs'" % _SCHEMA)
    r = woocommerce.sincronizeaza(_SCHEMA)
    assert len(r["importate"]) == 1 and mediu["la_model"] == [0], (r, mediu["la_model"])
    with mediu["conn"].cursor() as cur:
        cur.execute("UPDATE %s.firma_profil SET platitor_tva = false, wc_ultima_sinc = NULL" % _SCHEMA)
    comanda["number"] = 502
    r = woocommerce.sincronizeaza(_SCHEMA)
    with mediu["conn"].cursor() as cur:
        cur.execute("SELECT cota_tva::int FROM %s.factura_linii WHERE factura_id = %%s" % _SCHEMA, (r["importate"][0]["factura_id"],))
        assert cur.fetchall() == [(0,)], "neplătitorul a facturat cu TVA din magazin"


def test_facturile_recurente_intreaba_modelul_inaintea_emiterii(mediu, monkeypatch):
    """Cronul facturilor recurente: abonamentele, plătitorul și întrebările se citesc scurt, modelul cu pool-ul liber, emiterea
    recitește abonamentele. Al doilea abonament e emis de „altă rulare” exact între faze (cât se întreabă modelul): faza de emitere
    trebuie să-l vadă emis și să-l sară. MUTAȚIE: revalidarea scoasă (se emit abonamentele citite în faza 1) -> se emite de două
    ori -> pică."""
    import datetime
    import json
    from core import cote_tva, facturi_recurente as fr
    linii = json.dumps([{"descriere": "Mentenanta platforma web", "cantitate": 1, "pret_unitar": 100}])
    azi = datetime.date(2026, 10, 10)
    with mediu["conn"].cursor() as cur:
        for i in (1, 2):
            cur.execute("INSERT INTO %s.facturi_recurente (id, tert_nume, tert_cui, linii, zi_emitere) VALUES (%%s, 'Client R193 SRL', "
                        "'14399840', %%s, 1)" % _SCHEMA, (i, linii))
    intreaba = cote_tva.intreaba

    def _intre_faze(*a, **k):
        with mediu["conn"].cursor() as cur:
            cur.execute("UPDATE %s.facturi_recurente SET ultima_emitere = %%s WHERE id = 2" % _SCHEMA, (azi,))
        return intreaba(*a, **k)
    monkeypatch.setattr(cote_tva, "intreaba", _intre_faze)
    e = fr.emite_scadente(_SCHEMA, azi)
    assert [(x["sablon"], x.get("eroare")) for x in e] == [(1, None)], e
    assert mediu["la_model"] == [0], mediu["la_model"]
