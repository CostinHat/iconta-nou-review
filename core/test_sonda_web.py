# -*- coding: utf-8 -*-
"""GARD [R75 (b), 27.08.2026]: procesul care servește ecranele e supravegheat, și se știe cum.

Costin: *„(b) e în aceeași formă cu ce merge deja: `cron.RITMURI` supraveghează 11 joburi; al
12-lea e procesul care le servește pe toate."* Iar cerința, textual: **„procesul e viu ȘI
răspunde"** — nu doar `active` la systemd.

CE FACE IMPOSIBIL:
  1. sonda scoasă din `cron.RITMURI` — atunci lipsa ei n-ar fi lipsă pentru nimeni;
  2. sonda care nu mai trece prin `cron.ruleaza` — n-ar alerta la eșec și n-ar bate la reușită;
  3. sonda care se mulțumește să întrebe systemd dacă unitatea e `active`: trebuie să **ceară
     pagina** și să compare **ora de pornire**. Amândouă, structural;
  4. constanta legată ca argument implicit — forma care a făcut calea de eșec neprobabilă la
     prima scriere (prinsă de propria calibrare, în aceeași tură).

CE NU FACE, declarat, și e afirmația mai slabă pe care Costin a cerut-o scrisă ca atare:
**sonda prinde REPORNIREA, nu durata căderii.** Între două rulări la 15 minute, o cădere de trei
secunde și una de paisprezece minute arată identic. Ce se poate spune e *„a repornit între X și
Y"*, nu *„a fost jos N secunde"*. Iar dacă mașina cade cu totul, nu rulează nici sonda — limita
declarată deja în `cron.verifica_batai`, pe care doar un deadman EXTERN ar acoperi-o.
"""
import ast
import io
import os

from core import cron, sonda_web

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _arbore():
    return ast.parse(io.open(os.path.join(_RAD, "core", "sonda_web.py"), encoding="utf-8").read())


def test_sonda_e_in_deadman():
    assert set(cron.RITMURI) >= {"sonda_web"}, (
        "`sonda_web` nu e în `cron.RITMURI` — lipsa ei n-ar fi lipsă pentru nimeni")
    assert cron.RITMURI["sonda_web"] >= 1, "prag prea strâns pentru un job la 15 minute"


def test_sonda_trece_prin_ambalajul_care_alerteaza_si_bate():
    """Structural: apelul, nu un comentariu."""
    arb = _arbore()
    gasit = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "ruleaza"
        and isinstance(n.func.value, ast.Name) and n.func.value.id == "cron"
        and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id == "NUME"
        for n in ast.walk(arb))
    assert gasit, "`sonda_web` nu trece prin `cron.ruleaza(NUME, …)`"


def test_sonda_CERE_pagina_si_compara_ora_de_pornire():
    """Cele două lucruri pe care le-a cerut Costin: viu **și** răspunde, plus repornirea vizibilă."""
    fn = next(n for n in ast.walk(_arbore())
              if isinstance(n, ast.FunctionDef) and n.name == "verifica")
    chemate = {n.func.id for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert chemate >= {"raspunde", "ora_pornirii"}, (
        "`verifica` nu mai cere pagina sau nu mai citește ora de pornire: %s" % sorted(chemate))


def test_constantele_NU_sunt_argumente_implicite():
    """Forma care a făcut calea de eșec neprobabilă: `def f(baza=BAZA)` fixează valoarea la
    definirea funcției. Prinsă de propria calibrare, 27.08.2026."""
    rele = []
    for n in ast.walk(_arbore()):
        if not isinstance(n, ast.FunctionDef):
            continue
        for d in n.args.defaults:
            if isinstance(d, ast.Name) and d.id.isupper():
                rele.append("%s(...=%s)" % (n.name, d.id))
    assert not rele, (
        "constante legate ca argument implicit: %s — se citesc în corpul funcției, altfel calea "
        "de eșec nu se poate proba" % rele)


def test_pe_viu_procesul_raspunde():
    """Nu o simulare: se cere chiar pagina publică de la procesul care rulează acum."""
    cod, octeti = sonda_web.raspunde()
    assert cod == 200, "pagina publică răspunde %s" % cod
    assert octeti > 200, "pagina publică are doar %d octeți — e goală sau ruptă" % octeti


def test_ora_pornirii_se_poate_citi():
    """Fără ea, sonda ar putea spune doar «răspunde acum», nu «a repornit între timp»."""
    v = sonda_web.ora_pornirii()
    assert v and len(v) > 10, (
        "ora de pornire a unității nu se poate citi (%r) — jumătatea de detectare a repornirii "
        "e oarbă, iar sonda ar trebui s-o spună, nu s-o presupună" % v)


def test_deploy_ul_NU_alerteaza_iar_caderea_DA():
    """`post-commit` repornește serviciul la FIECARE commit. Fără distincția asta, sonda ar fi
    alertat de zece ori pe zi despre reporniri pe care le-am cerut noi — iar *„un semnal care se
    aprinde mereu nu mai e semnal"* e chiar doctrina din `core/cron.py`.

    Cele patru direcții, pe funcția PURĂ:"""
    f = sonda_web.fel_repornirii
    assert f("A", "A", "c1", "c1") is None, "n-a repornit, dar se raportează ceva"
    assert f("A", "B", "c1", "c2") == "deploy", "repornire cu ALT commit = deploy, nu cădere"
    assert f("A", "B", "c1", "c1") == "cadere", "repornire cu ACELAȘI commit = cădere"
    assert f("A", "B", None, "c1") == "necunoscut", (
        "fără unul din commituri, sonda trebuie să SPUNĂ că nu poate deosebi, nu să tacă")
    assert f(None, "B", None, "c1") is None, "prima rulare n-are cu ce compara"
    # [18.10.2026, comanda Costin 8.1 pct.6] același commit, dar mașina a pornit după proces: repornirea serverului, nu o cădere
    assert f("A", "B", "c1", "c1", server_repornit=True) == "server"
    assert f("A", "B", "c1", "c2", server_repornit=True) == "deploy", "un deploy rămâne deploy"


def test_sonda_citeste_commitul_procesului_din_registrul_instantelor():
    """[271] Sursa commitului e registrul instanțelor (`instante.vii`), scris de procesul web la pornire — nu `HEAD` de pe disc (publicarea
    îl mută înaintea repornirii) și nu `versiune.stare()` (memoria procesului web: sonda, alt proces, ar citi mereu None)."""
    arb = _arbore()
    fn = next(n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef) and n.name == "commitul_procesului")
    chemate = {n.func.attr for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "vii" in chemate and chemate.isdisjoint({"git_head", "stare"}), sorted(chemate)


def test_def_271_publicarea_nu_mai_e_citita_ca_cadere(monkeypatch):
    """[271] Reluarea publicării lotului 4 (15.10.2026): discul mutat pe commitul nou la 17:59:35, sonda de la 18:00:02 rulează ÎNAINTEA
    repornirii (procesul vechi, commitul vechi), repornirea la 18:01:26, sonda de la 18:15:01. Înainte: sonda de la 18:00 nota ora veche
    lângă commitul NOU (de pe disc), iar cea de la 18:15 vedea „a repornit cu același commit” -> alerta „fără să fi fost un deploy”.
    Acum: deploy, fără alertă. Și cealaltă direcție rămâne: o repornire cu ACELAȘI commit al procesului alertează.
    MUTAȚIE: `commitul_procesului` întors la `HEAD` de pe disc -> alerta de cădere -> pică."""
    from core import db, instante, observare, versiune
    gazda = instante.eu()[0]
    stare = {"pornit": "Thu 2026-10-15 16:47:02 EEST", "proces": "OLD", "ultima": (None, None)}
    alerte = []
    monkeypatch.setattr(versiune, "git_head", lambda *a, **k: "NEW")       # discul e deja pe commitul nou
    monkeypatch.setattr(sonda_web, "raspunde", lambda *a, **k: (200, 5000))
    monkeypatch.setattr(sonda_web, "ora_pornirii", lambda *a, **k: stare["pornit"])
    import datetime as _dtm   # mașina pornită înaintea scenariului (altfel ceasul real al serverului ar decide)
    monkeypatch.setattr(sonda_web, "ora_bootarii", lambda *a, **k: _dtm.datetime(2026, 9, 10, 13, 13))
    monkeypatch.setattr(instante, "vii", lambda conn, *a, **k: [(gazda, 11, stare["proces"], None), (gazda, 12, stare["proces"], None)])
    monkeypatch.setattr(sonda_web, "_citeste_ultima", lambda conn: stare["ultima"])
    monkeypatch.setattr(sonda_web, "_scrie_ultima", lambda conn, p, c: stare.update(ultima=(p, c)))
    monkeypatch.setattr(observare, "alerteaza", lambda cheie, subiect, mesaj, acum=None: alerte.append(subiect))
    monkeypatch.setattr(db, "init_pool", lambda *a, **k: None)

    class _Conn:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    monkeypatch.setattr(db, "get_conn", lambda *a, **k: _Conn())

    assert sonda_web.verifica()["fel"] is None                                # 17:45, înainte de publicare
    assert sonda_web.verifica()["commit"] == "OLD"                            # 18:00:02 — disc mutat, procesul încă vechi
    stare.update(pornit="Thu 2026-10-15 18:01:26 EEST", proces="NEW")        # repornirea publicării
    assert sonda_web.verifica()["fel"] == "deploy" and alerte == []           # 18:15:01
    stare.update(pornit="Thu 2026-10-15 19:02:00 EEST")                       # a repornit singur, cu același commit
    assert sonda_web.verifica()["fel"] == "cadere"
    assert alerte == ["Procesul iConta a repornit fără să fi fost un deploy"]


def test_commitul_procesului_nu_se_ghiceste(monkeypatch):
    """Două commituri printre procesele vii (repornire în curs) sau niciun proces -> None („nu se poate deosebi”), nu unul la nimereală;
    procesele altei gazde nu se numără."""
    from core import instante
    gazda = instante.eu()[0]
    for vii, asteptat in (([(gazda, 1, "A", None), (gazda, 2, "A", None), ("alta", 3, "B", None)], "A"),
                          ([(gazda, 1, "A", None), (gazda, 2, "B", None)], None), ([], None), ([(gazda, 1, None, None)], None)):
        monkeypatch.setattr(instante, "vii", lambda conn, *a, _v=vii, **k: _v)
        assert sonda_web.commitul_procesului(None) == asteptat, vii


def test_CALIBRARE_o_unitate_inexistenta_NU_inventeaza_o_ora():
    """Direcția «pretinde că știe»: sonda are voie să nu știe, nu are voie să fabrice."""
    assert sonda_web.ora_pornirii("unitate-care-nu-exista-r75.service") in (None, ""), (
        "a întors o valoare pentru o unitate inexistentă")


def test_repornirea_serverului_de_la_0902_e_numita_server(tmp_path, monkeypatch):
    """[18.10.2026, comanda Costin 8.1 pct.6: alerta „Procesul iConta a repornit fără deploy” la repornirea de la 09:02] Mașina a fost
    repornită (`sudo reboot`, 09:02:13; boot 09:02:24) și procesul a pornit la 09:02:51 pe același commit `7ebbf79b`. Sonda spunea
    „procesul a căzut și s-a ridicat singur”; acum spune „Serverul iConta a repornit (mașina, nu numai procesul)”.
    MUTAȚIE: `server_repornit` neluat în seamă în `fel_repornirii` -> „cadere” -> pică."""
    import datetime as dt
    st = tmp_path / "stat"
    st.write_text("cpu 1 2 3\nbtime %d\n" % int(dt.datetime(2026, 10, 18, 9, 2, 24).timestamp()), encoding="ascii")
    assert sonda_web.ora_bootarii(str(st)) == dt.datetime(2026, 10, 18, 9, 2, 24)
    inainte = sonda_web._ca_data("Sun 2026-10-18 07:19:39 EEST")
    assert inainte == dt.datetime(2026, 10, 18, 7, 19, 39)
    boot = sonda_web.ora_bootarii(str(st))
    assert sonda_web.fel_repornirii("Sun 2026-10-18 07:19:39 EEST", "Sun 2026-10-18 09:02:51 EEST", "7ebbf79b", "7ebbf79b",
                                    server_repornit=boot > inainte) == "server"
