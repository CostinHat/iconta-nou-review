# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `emit` — deficiența 495: „Factură: Ciorna facturii e salvată doar în browser; pe alt calculator nu se regăsește.”
Clasa: ciornele formularelor lungi ale unei firme (salariatul nou, concediul medical — `static/js/ciorna_formular.js`).

Ce se probează aici (proba de pe ecran, două browsere ale aceluiași om, e în `frontend_test/e2e/e2e_lot12_emit.py::test_def_495_*`):
  * `public.ciorne_formular` (`core/migrare_ciorne_formular.py`): o ciornă pe UTILIZATOR + FIRMĂ + FORMULAR; a doua scriere o înlocuiește,
    ștergerea o scoate, iar ciorna unui utilizator nu se vede la altul, la altă firmă sau la alt formular (deficiența 65 rămâne închisă
    și pe server);
  * rutele (`core/ciorne_formular.py`): citește / scrie / șterge pe firma la care omul are acces; forma greșită, numele de formular
    necunoscut și ciorna uriașă se refuză;
  * ecranele: transportul comun (`ciorna_formular.js` `ciornaPeServer`) citește serverul la deschidere și urcă pe server copia rămasă în
    browser (ciorna veche, de dinainte de 495); după ce serverul a primit-o, copia din browser se șterge; factura (`emitere_ecran.js`)
    și formularele lungi ale firmei îl folosesc pe el, nu o a doua implementare.

Tabela se creează în tranzacția testului (DDL-ul migrării) și totul se anulează la capăt: nimic nu rămâne în baza de test.
Temei: N/A — păstrarea lucrului început e regulă de produs (CLAUDE.md §9), nu fiscală.
"""
import contextlib
import io
import os
import re

import pytest

from core import db as _db

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def rollback(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def mediu(monkeypatch):
    """O conexiune reală, cu tabela ciornelor creată în tranzacția ei (DDL-ul migrării), doi utilizatori și două firme existente în baza
    de test; `db.get_conn` dă aceeași conexiune (fără commit), iar la capăt totul se anulează."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import migrare_ciorne_formular as m, uc_comun
    with _db.get_conn() as c:
        m.aplica(c)
        with c.cursor() as cur:
            cur.execute("SELECT id FROM public.users ORDER BY id LIMIT 2")
            useri = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT id FROM public.tenants ORDER BY id LIMIT 2")
            firme = [r[0] for r in cur.fetchall()]
        if len(useri) < 2 or len(firme) < 2:
            c.rollback()
            pytest.skip("baza de test n-are doi utilizatori și două firme")

        @contextlib.contextmanager
        def _gc(*a, **k):
            yield _FaraCommit(c)
        monkeypatch.setattr(_db, "get_conn", _gc)
        acces = {"refuzat": set()}

        def _schema(ctx, tid):
            from core import erori
            if (ctx["uid"], int(tid)) in acces["refuzat"]:
                raise erori.Inexistent("Firma nu există sau nu ai acces la ea.")
            return "tenant_x"
        monkeypatch.setattr(uc_comun, "_schema_sau_404", _schema)
        try:
            yield {"conn": c, "useri": useri, "firme": firme, "acces": acces}
        finally:
            c.rollback()


def test_ciorna_e_pe_utilizator_si_firma_si_se_regaseste_de_oriunde(mediu):
    """495: ciorna facturii scrisă de utilizatorul A la firma X se citește înapoi la fel (oricare ar fi calculatorul — serverul nu știe de
    browser); la A pe firma Y, la B pe firma X și la A pe alt formular nu e nimic (65). A doua scriere o înlocuiește; ștergerea o scoate,
    a doua ștergere nu e eroare. MUTAȚIE: `WHERE user_id = %s AND tenant_id = %s AND formular = %s` din `citeste` -> fără utilizator ->
    B vede ciorna lui A -> pică."""
    from core import ciorne_formular as cf
    (a, b), (x, y) = mediu["useri"], mediu["firme"]
    continut = {"v": 1, "salvat_la": "2099-01-02T10:11:00.000Z", "campuri": {"em-nume": "Client Ciorna 495 SRL"},
                "linii": [{"descriere": "Consultanta", "cantitate": 2, "pret_unitar": 150}]}
    r = cf.ciorna_scrie(x, "factura", {"continut": continut}, {"uid": a})
    assert r["ok"] is True and r["salvat_la"]
    assert cf.ciorna_citeste(x, "factura", {"uid": a}) == {"ciorna": continut}
    assert cf.ciorna_citeste(y, "factura", {"uid": a}) == {"ciorna": None}          # altă firmă
    assert cf.ciorna_citeste(x, "factura", {"uid": b}) == {"ciorna": None}          # alt utilizator
    assert cf.ciorna_citeste(x, "salariat_nou", {"uid": a}) == {"ciorna": None}     # alt formular
    nou = dict(continut, campuri={"em-nume": "Client Schimbat SRL"})
    cf.ciorna_scrie(x, "factura", {"continut": nou}, {"uid": a})
    assert cf.ciorna_citeste(x, "factura", {"uid": a})["ciorna"]["campuri"]["em-nume"] == "Client Schimbat SRL"
    with mediu["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM public.ciorne_formular WHERE user_id = %s AND tenant_id = %s AND formular = 'factura'", (a, x))
        assert cur.fetchone()[0] == 1                                    # o singură ciornă pe utilizator + firmă + formular
    cm = {"v": 1, "salvat_la": 4070908800000, "campuri": {"cm-serie": "CCMAM", "cm-numar": "1234567"}}
    cf.ciorna_scrie(x, "concediu_medical:15", {"continut": cm}, {"uid": a})          # clasa: formularul lung al firmei
    assert cf.ciorna_citeste(x, "concediu_medical:15", {"uid": a}) == {"ciorna": cm}
    assert cf.ciorna_sterge(x, "factura", {"uid": a}) == {"ok": True, "stearsa": True}
    assert cf.ciorna_citeste(x, "factura", {"uid": a}) == {"ciorna": None}
    assert cf.ciorna_citeste(x, "concediu_medical:15", {"uid": a}) == {"ciorna": cm}  # ștergerea facturii nu atinge altă ciornă
    assert cf.ciorna_sterge(x, "factura", {"uid": a}) == {"ok": True, "stearsa": False}


def test_firma_fara_acces_forma_gresita_si_ciorna_uriasa_se_refuza(mediu):
    """Ruta citește / scrie numai la o firmă la care omul are acces (404, ca orice rută a firmei); un corp fără `continut` obiect, un
    nume de formular care nu e al aplicației și o ciornă peste 256 KB se refuză cu mesajul lor, fără să scrie.
    MUTAȚIE: verificarea mărimii scoasă -> se scrie -> pică."""
    from core import ciorne_formular as cf, erori
    (a, _b), (x, _y) = mediu["useri"], mediu["firme"]
    mediu["acces"]["refuzat"].add((a, x))
    with pytest.raises(erori.Inexistent):
        cf.ciorna_citeste(x, "factura", {"uid": a})
    mediu["acces"]["refuzat"].clear()
    with pytest.raises(erori.DateInvalide) as e:
        cf.ciorna_scrie(x, "factura", {"continut": "text"}, {"uid": a})
    assert e.value.detaliu == cf.MESAJ_FORMA
    with pytest.raises(erori.DateInvalide) as e:
        cf.ciorna_citeste(x, "../users", {"uid": a})
    assert e.value.detaliu == cf.MESAJ_FORMULAR % ("../users",)
    with pytest.raises(erori.DateInvalide) as e:
        cf.ciorna_scrie(x, "factura", {"continut": {"linii": [{"descriere": "x" * (cf.LIMITA_OCTETI + 10)}]}}, {"uid": a})
    assert e.value.detaliu == cf.MESAJ_PREA_MARE
    assert cf.ciorna_citeste(x, "factura", {"uid": a}) == {"ciorna": None}


def _js(cale):
    return io.open(os.path.join(RAD, "static", "js", cale), encoding="utf-8").read()


def _corp(src, antet):
    i = src.index(antet)
    j = src.index("\n}\n", i)
    return src[i:j]


def test_transportul_comun_citeste_serverul_si_urca_ciorna_veche_din_browser():
    """`ciornaPeServer`: la deschidere cere ciorna serverului și, dacă în browser a rămas o copie mai nouă sau serverul n-are nimic, o
    urcă (PUT); după PUT, copia din browser se șterge numai dacă nu s-a schimbat între timp; ștergerea cere DELETE. Factura îl folosește
    (`emitere_ecran.js`: `incarcaCiorna` înainte de formular, pe `/ciorne-formular/factura`), la fel ciorna formularelor firmei (`ciornaFormular`
    cu `server`). MUTAȚIE: `await incarcaCiorna(tenantId)` scos din `randeazaEmitere` -> pică."""
    from core.arbore_js import apeluri, arbore_js, functia, noduri
    cf = _js("ciorna_formular.js")
    tr = _corp(cf, "export function ciornaPeServer(cheie, url)")
    arb, cod = arbore_js(os.path.join(RAD, "static", "js", "ciorna_formular.js"))
    nod = functia(arb, "ciornaPeServer")
    # pe ARBORE: transportul cere, urcă și șterge pe același `url` (PUT așteptat), cu ciorna ca `continut`
    assert [apeluri(nod, cod, x) for x in ("api.get", "api.put", "api.del")] == [[("url",)], [("url", "{ continut: c }")], [("url",)]]
    assert {"await api.put(url, { continut: c })", "await api.get(url)"} <= {cod(a) for a in noduri(nod, "AwaitExpression")}
    assert re.search(r"acum\.salvat_la === c\.salvat_la\) _stergeLocal\(cheie\)", tr)
    assert re.search(r"if \(local && \(!server \|\| .*\) \{ await trimite\(\); return local; \}", tr)
    assert [cod(a) for a in noduri(functia(arb, "ciornaFormular"), "AssignmentExpression") if cod(a["right"]).startswith("ciornaPeServer(")] \
        == ["t = ciornaPeServer(cheie, `/tenants/${server.tenantId}/ciorne-formular/${encodeURIComponent(server.formular)}`)"]
    em = _js("ecrane/emitere_ecran.js")
    r = _corp(em, "export async function randeazaEmitere(")
    assert r.index("await incarcaCiorna(tenantId)") < r.index("formularEmitere(corp, nav, tenantId, num, opt)")
    arb_em, cod_em = arbore_js("emitere_ecran.js")
    assert apeluri(arb_em, cod_em, "ciornaPeServer") == [("cheieCiorna(tenantId)", "`/tenants/${tenantId}/ciorne-formular/factura`")]
    assert "localStorage" not in em.split("// ---------- CIORNA FACTURII ----------")[1].split("// ---------- FORMULAR EMITERE")[0], \
        "factura și-a făcut iar o a doua stocare a ciornei"


def test_ciornele_formularelor_firmei_sunt_pe_server():
    """Clasa lui 495: formularele lungi ale unei FIRME (concediul medical, salariatul nou) cer ciorna pe server (`server` = {tenantId,
    formular}); înregistrarea cabinetului rămâne în browser (înaintea contului nu există utilizator). MUTAȚIE: argumentul `server` scos
    din concediul medical -> pică."""
    import re as _re
    apeluri = {}
    for cale in ("ecrane/flux_concediu.js", "ecrane/firme.js", "ecrane/login.js"):
        for m in _re.finditer(r"ciornaFormular\(\s*\w+\s*,\s*([^,]+?)\s*,\s*\[[^\]]*\]\s*(,\s*\{[^}]*formular:[^}]*\})?\)", _js(cale), _re.S):
            apeluri[(cale, m.group(1))] = bool(m.group(2))
    assert apeluri[("ecrane/flux_concediu.js", '"iconta_ciorna_cm:" + t.id + ":" + sal.id')] is True, apeluri
    assert apeluri[("ecrane/firme.js", '"iconta_ciorna_salariat:" + t.id')] is True, apeluri
    assert not any(v for (c, _k), v in apeluri.items() if c == "ecrane/login.js"), apeluri
