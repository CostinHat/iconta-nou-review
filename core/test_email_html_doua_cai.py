# -*- coding: utf-8 -*-
"""core/test_email_html_doua_cai.py — cele doua cai C5 ratate de masuratoarea lexicala.

**De ce exista fisierul asta separat de `test_email_html_dupa_commit.py`.** Acela pazeste locurile
unde apelul statea LEXICAL intr-un `with get_conn` din aceeasi functie. Auditul mecanic de dupa a
gasit inca doua cai pe care garda aia nu le poate vedea: conexiunea e tinuta de APELANT, doua
functii mai sus. *Limita era scrisa langa garda; ce lipsea era s-o aplic si retroactiv.*

  1. `POST /pachete/{tenant_id}/trimite` — ruta tinea DOUA conexiuni peste apelul de 15 s;
  2. `notificari_scadenta.emite_pentru_firma` — tinea conexiunea firmei peste TOATA bucla, adica
     cate un apel pentru fiecare factura scadenta.

In niciuna, rezultatul e-mailului nu decide ce se scrie — deci remedierea minima: citirea ramane
unde e, efectul iese din bloc. Conditii, destinatari, continut si coduri de raspuns: neschimbate.
"""
from __future__ import annotations

import ast
import io
import os

from core import observare
from core import pachete_api as PA

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _Postas:
    def __init__(self, raspuns=True):
        self.trimise = []
        self.raspuns = raspuns

    def __call__(self, catre, subiect, html, **k):
        self.trimise.append((catre, subiect, html, k))
        return self.raspuns


# ============================================================
#  1. pachete_api — citirea nu mai trimite
# ============================================================
def test_pregateste_nu_trimite_nimic(monkeypatch):
    """Partea care are nevoie de conexiuni nu mai are niciun efect extern."""
    postas = _Postas()
    monkeypatch.setattr(observare, "trimite_email_html", postas)
    monkeypatch.setattr(PA, "rezumat_luna",
                        lambda *a, **k: {"email": "client@firma.ro", "nume_firma": "Alfa"})
    monkeypatch.setattr(PA, "get_poveste",
                        lambda *a, **k: {"exista": True, "status": "aprobat", "text": "povestea"})
    r = PA.pregateste(None, None, 1, 2026, 6, semnatura="S")
    assert r["ok"] is True and r["email"] == "client@firma.ro"
    assert postas.trimise == [], "pregatirea a trimis un e-mail"


def test_codurile_de_refuz_raman_aceleasi(monkeypatch):
    """Conditiile de business, neschimbate: fara email -> FARA_EMAIL; neaprobata -> NEAPROBATA."""
    monkeypatch.setattr(observare, "trimite_email_html", _Postas())
    monkeypatch.setattr(PA, "get_poveste",
                        lambda *a, **k: {"exista": True, "status": "aprobat", "text": "x"})
    monkeypatch.setattr(PA, "rezumat_luna", lambda *a, **k: {"email": "", "nume_firma": "Alfa"})
    assert PA.pregateste(None, None, 1, 2026, 6)["cod"] == "FARA_EMAIL"

    monkeypatch.setattr(PA, "rezumat_luna",
                        lambda *a, **k: {"email": "c@f.ro", "nume_firma": "Alfa"})
    monkeypatch.setattr(PA, "get_poveste",
                        lambda *a, **k: {"exista": True, "status": "ciorna", "text": "x"})
    assert PA.pregateste(None, None, 1, 2026, 6)["cod"] == "NEAPROBATA"


def test_trimite_pregatit_duce_mai_departe_refuzul(monkeypatch):
    postas = _Postas()
    monkeypatch.setattr(observare, "trimite_email_html", postas)
    r = PA.trimite_pregatit({"ok": False, "cod": "FARA_EMAIL"})
    assert r["cod"] == "FARA_EMAIL" and postas.trimise == []


def test_trimite_pregatit_raporteaza_esecul_lui_brevo(monkeypatch):
    monkeypatch.setattr(observare, "trimite_email_html", _Postas(raspuns=False))
    r = PA.trimite_pregatit({"ok": True, "email": "c@f.ro", "subiect": "s", "html": "<p>h</p>"})
    assert r == {"ok": False, "cod": "EMAIL_ESUAT"}


# ============================================================
#  2. STRUCTURAL — apelul nu mai sta sub conexiunea apelantului
# ============================================================
def _apel_sub_get_conn(cale, nume_functie, nume_apel):
    """Apelul `nume_apel` se executa lexical intr-un `with ...get_conn(...)` din `nume_functie`?"""
    arbore = ast.parse(io.open(os.path.join(RADACINA, cale), encoding="utf-8").read())
    fn = next((n for n in ast.walk(arbore)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == nume_functie), None)
    assert fn is not None, "nu gasesc %s in %s" % (nume_functie, cale)
    parinte = {}
    for n in ast.walk(fn):
        for c in ast.iter_child_nodes(n):
            parinte[c] = n
    gasit = []
    for n in ast.walk(fn):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        ident = (f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name)
                 else None)
        if ident != nume_apel:
            continue
        p, sub = parinte.get(n), False
        while p is not None:
            if isinstance(p, ast.With):
                for it in p.items:
                    e = it.context_expr
                    if (isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute)
                            and e.func.attr.startswith("get_conn")):
                        sub = True
            p = parinte.get(p)
        gasit.append(sub)
    return gasit


def test_ruta_pachet_trimite_apeleaza_DUPA_bloc():
    sub = _apel_sub_get_conn("main.py", "pachet_trimite", "trimite_pregatit")
    assert sub == [False], (
        "`trimite_pregatit` se executa cu conexiunile in mana: %r" % sub)


def test_jobul_de_notificari_apeleaza_DUPA_bloc():
    sub = _apel_sub_get_conn("core/notificari_scadenta.py", "emite_pentru_firma",
                             "trimite_email_html")
    assert sub == [False], (
        "bucla de notificari tine conexiunea peste apelurile la Brevo: %r" % sub)


def test_calibrare_detectorul_CHIAR_vede_un_apel_sub_conexiune():
    """ANTI-VACUUM, in cealalta directie: pe un apel care CHIAR sta in bloc, detectorul spune DA.

    `_plan_notificari(conn, azi)` se cheama din interiorul lui `with db.get_conn(schema)` — si
    acolo E locul lui, fiindca ala e chiar pasul de citire. Daca detectorul ar raporta `False` si
    pentru el, cele doua probe de mai sus ar trece pe o masuratoare oarba."""
    sub = _apel_sub_get_conn("core/notificari_scadenta.py", "emite_pentru_firma",
                             "_plan_notificari")
    assert sub == [True], (
        "detectorul nu vede un apel care chiar sta sub conexiune: %r" % sub)


def test_citirea_si_efectul_sunt_functii_DIFERITE():
    """Contractul: partea care are nevoie de conexiune nu mai are efect extern, si invers."""
    arbore = ast.parse(io.open(os.path.join(RADACINA, "core", "pachete_api.py"),
                               encoding="utf-8").read())
    nume = {n.name for n in ast.walk(arbore) if isinstance(n, ast.FunctionDef)}
    # algebra de multimi, nu `in`: un `in` se ancoreaza pe un nume care apare oricum, iar aici
    # intrebarea e despre MULTIMEA functiilor, nu despre prezenta unui sir.
    asteptate = {"pregateste", "trimite_pregatit"}
    assert asteptate - nume == set(), "lipsesc din modul: %r" % sorted(asteptate - nume)
    assert nume & {"trimite"} == set(), (
        "vechea `trimite` a ramas langa cele doua — logica paralela, iar reparatia n-ar ajunge la ea")
