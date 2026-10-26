# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), zona admin — tiparele de erori (574, 576), calitatea echipei fără regenerări (458.1), „Declarații lucrate”
(C87.1).

Anexa comenzii 13.1, verbatim:
  574: „«Înlocuită de declarația generată din nou» (automat) e numărată ca respingere: D300 67% umflat; notele respinse de om (ex. Asist
       Test azi) lipsesc.”
  576: „Construiește pe cifrele umflate și inventează […]; «---» afișat ca atare. Doar respingeri făcute de om; «prea puține cazuri» sub prag.”
  458.1: „Administratorul are încă «Depășită, lipsește F1A5» numărată ca respingere, deși e regenerare automată; regenerările automate nu
       intră în calitatea echipei.”
  C87.1: „«Declarații lucrate» există, dar rândurile spun «nota · nota-143» (numărul intern), «stare: la_senior», «Acoperire: nota»”.

Pe baza de TEST, într-o tranzacție anulată, cu rânduri de coadă sintetice pe perioade 2099 (nu se ciocnesc cu datele reale).
458.1 cere peticul `l13_petice/admin_7.json` (`coada_api.sql_inlocuita`) aplicat.
"""
import json
import types

import pytest

from core import asistenti_api, db, tipare_api


@pytest.fixture()
def cur():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute("INSERT INTO public.accounting_firms (nume) VALUES ('Cabinet probă 574 (sintetic)') RETURNING id")
            cab = c.fetchone()[0]
            c.execute("INSERT INTO public.users (email, password_hash, rol, activ, accounting_firm_id, prenume, nume) VALUES "
                      "('sef.574@exemplu.ro', 'x', 'admin_firma', true, %s, 'Șef', 'Probă'), "
                      "('asist.574@exemplu.ro', 'x', 'angajat', true, %s, 'Asist', 'Probă') RETURNING id", (cab, cab))
            sef, asist = [r[0] for r in c.fetchall()]
            c.execute("SELECT id FROM public.tenants ORDER BY id LIMIT 1")
            tid = c.fetchone()[0]
            yield types.SimpleNamespace(c=c, cab=cab, sef=sef, asist=asist, tid=tid)
        conn.rollback()


def _rand(b, fel, tip, perioada, creat_de, creat_la, stare="la_senior", respins_de=None, respins_la=None, motiv=None, payload=None):
    b.c.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, fel, tip, perioada, stare, payload, creat_de, creat_de_id, "
                "creat_la, respins_de, respins_de_id, respins_la, motiv_respingere) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (b.cab, b.tid, fel, tip, perioada, stare, json.dumps(payload or {}), str(creat_de), creat_de, creat_la,
                 str(respins_de) if respins_de else None, respins_de, respins_la, motiv))
    return b.c.fetchone()[0]


def _scenariu(b):
    """D300 99/2099: (1) generat de șef, „Generează din nou” (urmașul în aceeași tranzacție); (2) retras de șef însuși cu motiv
    („Depășită, lipsește F1A5”), apoi generat din nou de el; (3) urmașul final. Nota asistentei: respinsă de șef, cu motiv."""
    _rand(b, "declaratie", "d300", "25.01.2099", b.sef, "2099-01-10 10:00", "respinsa", b.sef, "2099-01-10 11:00",
          "Înlocuită de declarația generată din nou (Șef Probă).")
    _rand(b, "declaratie", "d300", "25.01.2099", b.sef, "2099-01-10 11:00", "respinsa", b.sef, "2099-01-11 09:00",
          "Depășită, lipsește F1A5 (servicii UE, rd.3/3.1)")
    _rand(b, "declaratie", "d300", "25.01.2099", b.sef, "2099-01-11 09:02")
    _rand(b, "nota", "nota", "nota-990001", b.asist, "2099-01-12 10:00", "respinsa", b.sef, "2099-01-12 12:00",
          "Lipsește documentul justificativ", {"descriere": "Ridicare numerar 574", "document_ref": "CEC 574", "grup": "nota-990001"})


def test_tiparele_numara_numai_respingerile_omului_si_notele(cur):
    """574: D300 nu mai apare cu respingeri (înlocuirea și retragerea proprie regenerată nu sunt respingeri — 458.1), iar nota respinsă
    de om apare („Note contabile”, motivul ei). MUTAȚII: filtrul `fel IN ('declaratie','nota')` -> numai declarații => nota lipsește ->
    pică; peticul 458.1 scos => „Depășită, lipsește F1A5” revine -> pică."""
    _scenariu(cur)
    t = tipare_api.tipare(cur.c.connection, cur.cab)
    assert [m["motiv"] for m in t["motive"]] == ["Lipsește documentul justificativ"], t["motive"]
    tip = {x["tip"]: (x["respinse"], x["total"]) for x in t["tipuri"]}
    assert tip == {"d300": (0, 1), "nota": (1, 1)}, tip
    assert t["respinse"] == 1
    assert tipare_api.eticheta_tip("nota") == "Note contabile" and tipare_api.eticheta_tip("d300") == "D300"


def test_calitatea_echipei_nu_numara_retragerea_proprie_regenerata(cur):
    """458.1: calitatea administratorului (șeful) — 0 respinse (retragerea proprie + regenerarea nu e eroare); a asistentei — 1."""
    _scenariu(cur)
    sef = asistenti_api.calitate(cur.c.connection, cur.cab, cur.sef)
    asist = asistenti_api.calitate(cur.c.connection, cur.cab, cur.asist)
    assert (sef["respinse"], [x["motiv"] for x in sef["tipare"]]) == (0, []), sef["tipare"]
    assert (asist["respinse"], [x["motiv"] for x in asist["tipare"]]) == (1, ["Lipsește documentul justificativ"])
    assert asist["tipuri"] == ["note contabile"], asist["tipuri"]                    # C87.1: „Acoperire: note contabile”, nu „nota”


def test_activitatea_numeste_elementele_si_starile_in_cuvinte(cur):
    """C87.1: rândul notei spune „Notă · <descriere> · <document>” și „respinsă”; declarația „D300 · <perioada>” și „la validare” /
    „înlocuită de una generată din nou”. MUTAȚIE: `eticheta` = perioada -> „nota-990001” -> pică."""
    _scenariu(cur)
    a = asistenti_api.activitate(cur.c.connection, cur.cab, cur.asist)["activitate"]
    nota = [x for x in a if x["fel"] == "nota"][0]
    assert nota["eticheta"] == "Notă · Ridicare numerar 574 · CEC 574" and nota["stare_text"] == "respinsă", nota
    assert "payload" not in nota
    s = {x["id"]: (x["eticheta"], x["stare_text"]) for x in asistenti_api.activitate(cur.c.connection, cur.cab, cur.sef)["activitate"]
         if x["fel"] == "declaratie"}
    assert sorted(set(e for e, _ in s.values())) == ["D300 · 25.01.2099"], s
    assert sorted(st for _, st in s.values()) == ["la validare", "înlocuită de una generată din nou", "înlocuită de una generată din nou"], s


def test_analiza_ai_sub_prag_nu_intreaba_modelul(monkeypatch):
    """576: sub `PRAG_ANALIZA` respingeri (ale omului) — „Prea puține respingeri…”, iar modelul nu e întrebat. MUTAȚIE:
    `PRAG_ANALIZA = 0` -> modelul e întrebat -> pică."""
    from core import ai_client
    chemat = []
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    monkeypatch.setattr(ai_client, "genereaza_text", lambda *a, **k: chemat.append(1) or "x")
    assert tipare_api.PRAG_ANALIZA == 5                                              # pragul ales (576), nu derivat în test
    date = {"are_date": True, "respinse": 4, "motive": [{"motiv": "m", "n": 4}], "tipuri": [], "firme": []}
    r = tipare_api.analiza_ai(date)
    assert r["disponibil"] is False and r["motiv"].startswith("Prea puține respingeri pentru o analiză") and chemat == [], r


def test_analiza_ai_peste_prag_cu_reguli_si_fara_separatoare(monkeypatch):
    """576: peste prag, promptul cere numai datele primite, „sistematic” de la `PRAG_SISTEMATIC` cazuri, diacritice; linia „---” din
    răspuns nu ajunge pe ecran."""
    from core import ai_client
    primit = {}
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    monkeypatch.setattr(ai_client, "genereaza_text", lambda p, sistem=None, **k: primit.update(p=p, s=sistem) or "Observ un tipar.\n---\n- Verifică documentul.")
    date = {"are_date": True, "respinse": 6, "motive": [{"motiv": "Lipsește documentul", "n": 6}],
            "tipuri": [{"tip": "nota", "respinse": 6, "total": 9, "pct": 67}], "firme": [{"nume": "F1", "respinse": 6, "total": 9}]}
    r = tipare_api.analiza_ai(date)
    assert r == {"disponibil": True, "analiza": "Observ un tipar.\n- Verifică documentul."}, r
    assert "Note contabile: 6 din 9" in primit["p"] and "nu numești firme, persoane, sesiuni" in primit["s"]
    assert ("cel puțin %d cazuri" % tipare_api.PRAG_SISTEMATIC) in primit["s"]   # PRAG_SISTEMATIC = 3 -> „3 cazuri” (`cate`)
