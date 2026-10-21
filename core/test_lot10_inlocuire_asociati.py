# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 426 — clasa; ultimul membru: importul asociaților] Comanda Costin 10.1 (verbatim în DECIZII „Comanda 10.1”): „al
doilea import de balanță pentru aceeași firmă o înlocuiește pe prima fără avertisment. Înainte de înlocuire: spune că există deja o
balanță, arată totalurile vechi și noi, cere confirmare; dacă există note pe lunile de după preluare, spune că soldurile lor se
recalculează.” Clasa = orice import de migrare care înlocuiește ce exista; importul asociaților fără dată de cesiune („corectură”)
ștergea structura existentă în tăcere (`DELETE FROM asociati`), deși notele de dividende și D205 se împart după ea.

Temeiul dependenței numite: Legea 31/1990 art.67 alin.(2) — „Dividendele se distribuie asociaților proporțional cu cota de participare la
capitalul social vărsat” (nota de dividende și D205 împart după structura de la data distribuirii, `dividende_curs.structura_la`), alin.(6)
— „Dividendele care se cuvin după data transmiterii acțiunilor aparțin cesionarului” (cu dată de cesiune structura veche rămâne în istoric,
deci nu e înlocuire). CNP-uri sintetice cu cifra de control verificată (algoritmul din CLAUDE.md)."""
import io
import os
import uuid

import pytest

from core import asociati_import_api as I
from core import db as _db
from core import erori as _erori
from core import migrare_api
from core import tenant_provisioning as _tprov

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNP_A, CNP_B, CNP_C = "1800101400016", "2850202400023", "1900101410011"   # cifra de control verificată


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def schema():
    """Firmă cu structura POPESCU ION 60% / IONESCU MARIA 40% și o notă de dividende validată la 20.05.2026 (10.000 lei)."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    sch = "efemer_l10_asoc_%s" % uuid.uuid4().hex[:8]
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), sch))
        cur.execute("SET LOCAL search_path TO %s, public" % sch)
        cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU ION', %s, 60), ('IONESCU MARIA', %s, 40)", (CNP_A, CNP_B))
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES ('2026-05-20', 'dividende', "
                    "'operatiuni', 'ciorna', 'Hotărârea AGA nr 3') RETURNING id")
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '117', '457', 10000)",
                    (nid,))
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
        c.commit()
    yield sch
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
        c.commit()


NOI = [{"nume": "POPESCU ION", "cnp": CNP_A, "cota": 50}, {"nume": "VASILE DAN", "cnp": CNP_C, "cota": 50}]


def _structura(sch):
    with _db.get_conn(sch) as c, c.cursor() as cur:
        cur.execute("SELECT nume, cota FROM asociati ORDER BY cota DESC, nume")
        return [(n, float(q)) for n, q in cur.fetchall()]


def test_def_426_corectura_peste_asociati_existenti_cere_confirmare(schema):
    with _db.get_conn(schema) as c:
        with pytest.raises(migrare_api.InlocuireNeconfirmata) as e:
            I.importa(c, NOI)
    m = str(e.value)
    # comanda 10.1: „spune că există deja […], arată [ce e] vechi și nou […], cere confirmare”; dependența numită (Legea 31/1990 art.67
    # alin.(2): dividendele se împart după cota de participare)
    assert m.startswith("Firma are deja 2 asociați: POPESCU ION 60%, IONESCU MARIA 40%. Fișierul nou: POPESCU ION 50%, VASILE DAN 50%. "
                        "Fără dată de cesiune, salvarea e o corectură: structura de acum se înlocuiește și nu rămâne în istoric. "
                        "Nota de dividende se împarte după structura de acum: nota nr. crt. 1 din 20.05.2026 (10.000,00 lei)"), m
    assert m.endswith(migrare_api.CERE_CONFIRMAREA), m
    assert (e.value.vechi["randuri"], [n["suma"] for n in e.value.dependente]) == (2, [10000.0])
    # refuzul nu scrie nimic: structura veche e neatinsă
    assert _structura(schema) == [("POPESCU ION", 60.0), ("IONESCU MARIA", 40.0)]


def test_def_426_corectura_confirmata_inlocuieste(schema):
    with _db.get_conn(schema) as c:
        r = I.importa(c, NOI, inlocuieste=True)
    assert r == {"importati": 2, "arhivati": 0, "inlocuit": {"randuri": 2}}
    assert _structura(schema) == [("POPESCU ION", 50.0), ("VASILE DAN", 50.0)]


def test_cesiunea_nu_cere_confirmare_structura_veche_ramane_in_istoric(schema):
    """Legea 31/1990 art.67 alin.(6): cu data cesiunii structura de acum intră în istoric — nu se pierde, deci nu e înlocuire."""
    with _db.get_conn(schema) as c:
        r = I.importa(c, NOI, data_cesiune="2026-06-01")
    assert r == {"importati": 2, "arhivati": 2, "inlocuit": None}


def test_firma_fara_asociati_nu_cere_confirmare():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    sch = "efemer_l10_asoc_%s" % uuid.uuid4().hex[:8]
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), sch))
            c.commit()
        with _db.get_conn(sch) as c:
            assert I.importa(c, NOI)["inlocuit"] is None
    finally:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
            c.commit()


def test_def_426_use_case_raspunde_409_si_previzualizarea_spune_ce_exista(schema, monkeypatch):
    from types import SimpleNamespace
    from core import uc_comun, uc_tenants
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: schema)
    date = SimpleNamespace(randuri=[SimpleNamespace(model_dump=lambda r=r: dict(r)) for r in NOI], data_cesiune=None, inlocuieste=False)
    with _db.get_conn(schema) as c:              # refuzul motorului pe aceleași rânduri, în aceeași stare (textul: testul de mai sus)
        with pytest.raises(migrare_api.InlocuireNeconfirmata) as refuz:
            I.importa(c, NOI)
    with pytest.raises(_erori.Conflict) as e:   # 409: ecranul deschide confirmarea (`_inlocuire409`)
        uc_tenants.asociati_import_salveaza(1, date, {"uid": 1})
    assert e.value.detaliu == str(refuz.value), e.value.detaliu   # 409 cu textul refuzului, întreg
    monkeypatch.setattr(I, "extrage", lambda *a, **k: [dict(r, rand_fisier=i) for i, r in enumerate(NOI, start=2)])
    rez = uc_tenants.asociati_import_incarca(1, b"x", "x.csv", {"uid": 1})
    rez = getattr(rez, "body", None) and __import__("json").loads(rez.body) or rez
    assert rez["existenta"]["randuri"] == 2, rez
    # previzualizarea: același text ca refuzul, fără fraza de final (`asociati_import_api.text_inlocuire`, „textul comun”)
    assert "%s %s" % (rez["avertisment_inlocuire"], migrare_api.CERE_CONFIRMAREA) == str(refuz.value), rez
    # avertismentul nu poartă fraza de final a refuzului (confirmarea o cere ecranul)
    assert not rez["avertisment_inlocuire"].endswith(migrare_api.CERE_CONFIRMAREA)
    date.inlocuieste = True
    assert uc_tenants.asociati_import_salveaza(1, date, {"uid": 1})["inlocuit"] == {"randuri": 2}


def test_date_firma_corectura_explicita_nu_cere_confirmare(schema, monkeypatch):
    """Date firmă → Asociați corectează structura arătată pe același ecran, cu jurnal vechi -> nou: salvarea e confirmarea."""
    from core import uc_asociati, uc_comun
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: schema)
    r = uc_asociati.asociati_salveaza(1, {"randuri": NOI}, {"uid": 1})
    assert r["ok"] and r["inlocuit"] == {"randuri": 2}
    assert _structura(schema) == [("POPESCU ION", 50.0), ("VASILE DAN", 50.0)]
