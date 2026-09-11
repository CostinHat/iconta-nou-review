# -*- coding: utf-8 -*-
"""core/test_email_html_dupa_commit.py — `trimite_email_html` nu se mai executa sub o conexiune.

**Ce s-a reparat.** Apelul are termen de **15 s**. Trei dintre cele 17 locuri de apel il faceau din
interiorul unui `with db.get_conn()`, deci legau o conexiune din cele zece ale pool-ului de latenta
unui serviciu strain. La doua dintre ele tranzactia era deja comisa — mutarea in afara blocului e
doar eliberarea conexiunii, fara nicio schimbare de semantica.

**La a treia — `pachet_poveste_set` — era si un defect de ORDINE.** `return r` statea in bloc, iar
`db.get_conn` comite la IESIREA din el: deci e-mailul pleca inainte ca raportul sa fie sigur salvat.
Un commit cazut lasa clientul cu «contabilul ti-a pregatit raportul lunar» pentru un raport care nu
exista. Contractul aprobat de arhitect, si probat mai jos:

    DB_COMMIT_SUCCESS  -> EMAIL_ALLOWED
    DB_COMMIT_FAILURE  -> EMAIL_NOT_SENT

**Doua feluri de proba, fiindca niciunul singur n-ar ajunge.** Cea STRUCTURALA (clichet 0 pe AST)
generalizeaza: prinde si al patrulea loc, cel scris maine. Cele FUNCTIONALE cheama rutele adevarate
si arata ce se intampla pe fiecare cale de esec — lucru pe care un scan pe arbore nu-l poate spune.
"""
from __future__ import annotations

import contextlib
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))
import inventar_email_html as inv  # noqa: E402

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _noduri_text(html):
    """Nodurile de TEXT ale randarii, curatate. Nu marcajul: un nume gasit intr-un atribut sau
    intr-un `<script>` nu e continut afisat."""
    from html.parser import HTMLParser

    class _P(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.texte = []
            self.etichete = []

        def handle_starttag(self, tag, attrs):
            self.etichete.append(tag)

        def handle_data(self, d):
            d = " ".join(d.split())
            if d:
                self.texte.append(d)

    p = _P()
    p.feed(html)
    return p.texte, p.etichete



# ============================================================
#  A. STRUCTURAL — clichet 0, cu anti-vacuum si calibrare
# ============================================================
def _toate():
    return inv.inventar(RADACINA)


def test_niciun_apel_nu_mai_sta_sub_o_conexiune():
    """CLICHET 0. Se asertează pe pozitii in arbore, nu pe text: un apel mutat inapoi in bloc ar
    trece orice cautare de sir."""
    sub = [x for x in _toate() if x["sub_conexiune"]]
    assert sub == [], (
        "apeluri `trimite_email_html` executate cat timp e tinuta o conexiune din pool:\n  "
        + "\n  ".join("%s (in `%s`)" % (x["fisier_linie"], x["functie"]) for x in sub)
        + "\nTermenul apelului e 15 s, iar pool-ul are 10 conexiuni.")


def test_anti_vacuum_scanul_chiar_vede_familia():
    """Fara asta, clichetul 0 ar fi trecut si daca scanul n-ar gasi NIMIC — un domeniu de cautare
    gresit raporteaza verde despre o lume pe care n-o vede."""
    toate = _toate()
    assert len(toate) >= 15, "scanul vede doar %d locuri de apel — domeniu prea mic" % len(toate)
    fisiere = [x["fisier_linie"].rsplit(":", 1)[0] for x in toate]
    assert fisiere.count("main.py") >= 10, "scanul nu vede main.py: %r" % sorted(set(fisiere))
    assert [f for f in fisiere if os.path.dirname(f) == "core"], (
        "scanul nu vede niciun modul din core/: %r" % sorted(set(fisiere)))


def test_calibrare_scanul_PRINDE_un_apel_sub_conexiune(tmp_path):
    """Directia cealalta (METODA §22): pe cod care ARE defectul, scanul il vede. Altfel «0» de mai
    sus ar putea insemna ca instrumentul nu stie sa caute."""
    (tmp_path / "core").mkdir()
    (tmp_path / "main.py").write_text(
        "def ruta():\n"
        "    with db.get_conn() as c:\n"
        "        _obs.trimite_email_html('a@b.c', 's', '<p>x</p>')\n", encoding="utf-8")
    gasite = inv.inventar(str(tmp_path))
    assert len(gasite) == 1, gasite
    assert gasite[0]["sub_conexiune"] is True, gasite[0]


def test_calibrare_scanul_NU_se_aprinde_pe_un_apel_din_afara(tmp_path):
    """Si nu raporteaza orice: un apel de dupa bloc nu e un defect."""
    (tmp_path / "core").mkdir()
    (tmp_path / "main.py").write_text(
        "def ruta():\n"
        "    with db.get_conn() as c:\n"
        "        x = 1\n"
        "    _obs.trimite_email_html('a@b.c', 's', '<p>x</p>')\n", encoding="utf-8")
    gasite = inv.inventar(str(tmp_path))
    assert len(gasite) == 1 and gasite[0]["sub_conexiune"] is False, gasite


# ============================================================
#  B. FUNCTIONAL — contractul, pe rutele adevarate
# ============================================================
class _Cursor:
    def __init__(self, raspunsuri):
        self._r = list(raspunsuri)
        self.executate = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, p=None):
        self.executate.append((" ".join(sql.split()), p))

    def fetchone(self):
        return self._r.pop(0) if self._r else None

    def fetchall(self):
        return []


class _Conn:
    def __init__(self, raspunsuri=(), commit_cade=False):
        self._c = _Cursor(raspunsuri)
        self.comis = 0
        self.commit_cade = commit_cade

    def cursor(self, *a, **k):
        return self._c

    def commit(self):
        if self.commit_cade:
            raise RuntimeError("commit a picat")
        self.comis += 1

    def rollback(self):
        pass


def _conn_fals(conn, cade_la_iesire=False):
    @contextlib.contextmanager
    def f(*a, **k):
        yield conn
        if cade_la_iesire:
            raise RuntimeError("commit a picat la iesirea din bloc")
        conn.comis += 1
    return f


class _Postas:
    def __init__(self, raspuns=True):
        self.trimise = []
        self.raspuns = raspuns

    def __call__(self, catre, subiect, html, *a, **k):
        self.trimise.append((catre, subiect, html))
        return self.raspuns


@pytest.fixture
def m():
    import main
    return main


def _pregateste_poveste(m, monkeypatch, conn, cade=False):
    postas = _Postas()
    monkeypatch.setattr(m, "_cere_perioada", lambda an, luna: None)
    monkeypatch.setattr(m, "_pachet_schema", lambda ctx, tid: "tenant_001")
    monkeypatch.setattr(m.db, "get_conn", _conn_fals(conn, cade))
    monkeypatch.setattr(m._pachete, "salveaza_poveste",
                        lambda *a, **k: {"ok": True, "status": "aprobat"})
    monkeypatch.setattr(m, "_email_client_tenant", lambda c, tid: "client@firma.ro")
    monkeypatch.setattr(m, "_nume_tenant", lambda c, tid: "Firma Alfa")
    monkeypatch.setattr(m._obs, "trimite_email_html", postas)
    return postas


class _Text:
    def __init__(self, status="aprobat", text="povestea lunii"):
        self.status = status
        self.text = text


def test_commit_reusit_emailul_pleaca(m, monkeypatch):
    """DB_COMMIT_SUCCESS -> EMAIL_ALLOWED."""
    conn = _Conn()
    postas = _pregateste_poveste(m, monkeypatch, conn)
    r = m.pachet_poveste_set(1, 2026, 6, _Text(), ctx={"firm": 1, "uid": 1})
    assert r["ok"] is True
    assert conn.comis == 1, "tranzactia nu s-a comis"
    assert len(postas.trimise) == 1, "e-mailul n-a plecat dupa un commit reusit"
    catre, subiect, html = postas.trimise[0]
    assert catre == "client@firma.ro"
    assert subiect.startswith("Raportul lunar")
    texte, _et = _noduri_text(html)
    assert [t for t in texte if "Firma Alfa" == t.strip()] or            [t for t in texte if t.strip().endswith("Firma Alfa")],         "numele firmei nu apare ca text afisat: %r" % texte


def test_commit_cazut_emailul_NU_pleaca(m, monkeypatch):
    """DB_COMMIT_FAILURE -> EMAIL_NOT_SENT. Asta e chiar defectul reparat: inainte, e-mailul
    pleca din interiorul blocului, deci si cand commitul de la iesire cadea."""
    conn = _Conn()
    postas = _pregateste_poveste(m, monkeypatch, conn, cade=True)
    with pytest.raises(RuntimeError):
        m.pachet_poveste_set(1, 2026, 6, _Text(), ctx={"firm": 1, "uid": 1})
    assert postas.trimise == [], (
        "a plecat un e-mail despre un raport care nu s-a salvat: %r" % (postas.trimise,))


def test_emailul_cazut_DUPA_commit_lasa_baza_comisa(m, monkeypatch):
    """Efectul ireversibil e ultimul, deci esecul lui nu mai poate intoarce nimic."""
    conn = _Conn()
    postas = _pregateste_poveste(m, monkeypatch, conn)
    postas.raspuns = False
    r = m.pachet_poveste_set(1, 2026, 6, _Text(), ctx={"firm": 1, "uid": 1})
    assert conn.comis == 1, "commitul s-a pierdut din cauza e-mailului"
    assert r["ok"] is True, "ruta a raportat esec pentru un act care a reusit"
    assert len(postas.trimise) == 1


def test_ciorna_nu_trimite_nimic(m, monkeypatch):
    """Conditia de business e NESCHIMBATA: se trimite doar pe `aprobat`."""
    conn = _Conn()
    postas = _pregateste_poveste(m, monkeypatch, conn)
    m.pachet_poveste_set(1, 2026, 6, _Text(status="ciorna"), ctx={"firm": 1, "uid": 1})
    assert postas.trimise == [], "a plecat un e-mail pentru o ciorna"
    assert conn.comis == 1


def test_fara_email_de_client_nu_se_trimite(m, monkeypatch):
    """Lipsa configuratiei: fara adresa, nu e nimic de trimis — nu un e-mail gol."""
    conn = _Conn()
    postas = _pregateste_poveste(m, monkeypatch, conn)
    monkeypatch.setattr(m, "_email_client_tenant", lambda c, tid: None)
    m.pachet_poveste_set(1, 2026, 6, _Text(), ctx={"firm": 1, "uid": 1})
    assert postas.trimise == []


def test_solicitarea_trimite_dupa_commit(m, monkeypatch):
    """A doua cale: raspunsul catre client. Continut si destinatar neschimbate."""
    conn = _Conn()
    postas = _Postas()
    monkeypatch.setattr(m, "_schema_sau_404", lambda ctx, tid: "tenant_001")
    monkeypatch.setattr(m.db, "get_conn", _conn_fals(conn))
    monkeypatch.setattr(m, "_email_client_tenant", lambda c, tid: "client@firma.ro")
    monkeypatch.setattr(m, "_nume_tenant", lambda c, tid: "Firma Alfa")
    monkeypatch.setattr(m._obs, "trimite_email_html", postas)

    class _S:
        mesaj = "am raspuns la intrebarea ta"
    r = m.cabinet_solicitari_raspunde(1, _S(), ctx={"firm": 1, "uid": 7})
    assert r["ok"] is True
    assert conn.comis >= 1
    catre, subiect, html = postas.trimise[0]
    assert catre == "client@firma.ro"
    assert subiect == "Raspuns nou de la contabilul tau"
    texte, _et = _noduri_text(html)
    assert [t for t in texte if t == "am raspuns la intrebarea ta"], (
        "mesajul nu apare ca text afisat: %r" % texte)


def test_solicitarea_escapeaza_mesajul_in_html(m, monkeypatch):
    """Continutul ramane NESCHIMBAT, inclusiv escaparea — mutarea n-a atins-o."""
    conn = _Conn()
    postas = _Postas()
    monkeypatch.setattr(m, "_schema_sau_404", lambda ctx, tid: "tenant_001")
    monkeypatch.setattr(m.db, "get_conn", _conn_fals(conn))
    monkeypatch.setattr(m, "_email_client_tenant", lambda c, tid: "client@firma.ro")
    monkeypatch.setattr(m, "_nume_tenant", lambda c, tid: "Firma Alfa")
    monkeypatch.setattr(m._obs, "trimite_email_html", postas)

    class _S:
        mesaj = "<script>furt()</script>"
    m.cabinet_solicitari_raspunde(1, _S(), ctx={"firm": 1, "uid": 7})
    html = postas.trimise[0][2]
    texte, etichete = _noduri_text(html)
    assert "script" not in etichete, (
        "mesajul clientului a produs un ELEMENT <script> in randare: %r" % etichete)
    assert [t for t in texte if t == "<script>furt()</script>"], (
        "mesajul n-a ajuns ca text afisat: %r" % texte)
