# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), zona admin — Suportul: triajul AI (572, 573), răspunsul echipei în clopoțel (648), notificarea de control
fiscal (570).

Anexa comenzii 13.1, verbatim:
  572: „Răspuns la «Cum adaug un asistent nou?»: fără diacritice, ghicit («de obicei '+'…»), roluri interne din cod
       (superadmin/admin_firma/angajat) în loc de drepturile reale, aliniat la dreapta. Când nu știe sigur, trebuie să escaladeze.”
  573: „La sesizarea escaladată nu se vede clasificarea/motivul AI; mesajul automat către utilizator e fără diacritice.”
  648: „Răspunsul la o sesizare trebuie să ajungă în clopoțel (și pe email, dacă utilizatorul nu e conectat).”
Cer peticele `l13_petice/admin_8.json` (`raportari_ai`) și `admin_9.json` (`notificari.TIPURI`). AI-ul e simulat (`ICONTA_AI_SIMULAT` sau
`monkeypatch`): niciun apel spre API. Pe baza de TEST, în tranzacții anulate.
"""
import json
import types

import pytest

from core import db, raportari_api, uc_raportari
from core import migrare_triaj_sesizari as m_triaj


# ── 572: ce nu pleacă la om ──────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("raspuns, motiv", [
    ("Mergi in Asistenti si apasa + . Rolul angajat poate pregati.", "fără diacritice"),
    ("De obicei apeși pe „+” din ecranul Asistenți.", "nu era sigur"),
    ("Contul cu rolul admin_firma adaugă asistenții din ecranul Asistenți.", "rol din cod"),
    ("Doar superadmin poate face asta.", "rol din cod"),
])
def test_raspunsul_care_ghiceste_sau_numeste_roluri_din_cod_se_escaladeaza(raspuns, motiv):
    """MUTAȚIE: `verifica_raspuns` întoarce None -> răspunsul pleacă la om -> pică."""
    from core import raportari_ai as rai
    assert motiv in (rai.verifica_raspuns(raspuns) or ""), (raspuns, rai.verifica_raspuns(raspuns))


def test_raspunsul_bun_pleaca():
    from core import raportari_ai as rai
    assert rai.verifica_raspuns("Din pagina principală deschide cardul „Asistenți”, apasă „Adaugă asistent”, scrie emailul colegului și "
                                "bifează firmele lui. Drepturile se aleg acolo: «Poate pregăti», «Poate valida», «Poate depune».") is None


def test_baza_de_cunostinte_fara_roluri_din_cod_si_fara_functii_de_platforma():
    """572: modelul copia rolurile din registru; baza primită spune rolurile în cuvintele aplicației și nu are funcțiile platformei."""
    from core import raportari_ai as rai
    rai._BAZA = None
    b = rai._baza_cunostinte()
    assert "admin_firma" not in b and "superadmin" not in b and "Suspendare cabinet" not in b, [l for l in b.splitlines() if "admin_firma" in l][:2]
    assert rai.fara_roluri_interne("token JWT cu rol (superadmin/admin_firma/angajat/client)") == "token JWT cu rol rolul utilizatorului"


def test_triajul_care_ghiceste_escaladeaza_cu_motivul_pastrat(monkeypatch):
    """572 + 573: modelul răspunde ghicit, fără diacritice -> sesizarea merge la echipă (`pentru_admin`), cu motivul scris pe sesizare,
    iar utilizatorul primește confirmarea cu diacritice (`TEXT_ESCALADARE`), nu răspunsul ghicit."""
    from core import ai_client, raportari_ai as rai
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    monkeypatch.setattr(ai_client, "genereaza_text", lambda *a, **k: json.dumps(
        {"decizie": "raspund", "raspuns": "De obicei apasa + in Asistenti; rolul admin_firma poate adauga."}))
    db.init_pool()
    with db.get_conn() as conn:
        m_triaj.aplica(conn)
        with conn.cursor() as c:
            c.execute("SELECT id, accounting_firm_id FROM public.users WHERE rol = 'admin_firma' ORDER BY id LIMIT 1")
            uid, cab = c.fetchone()
        r = raportari_api.creeaza_raportare(conn, uid, cab, "Asistent nou", "Cum adaug un asistent nou?")
        rid = r["raportare_id"]
        decizie = rai.triaj("Asistent nou", "Cum adaug un asistent nou?")
        assert decizie["decizie"] == "escaladez" and decizie["motiv"].startswith("Asistentul AI a încercat să răspundă, dar"), decizie
        # ce scrie `proceseaza` (peticul 573), pe conexiunea probei
        raportari_api.seteaza_pentru_admin(conn, rid, True)
        raportari_api.scrie_triajul(conn, rid, "escaladare", decizie["motiv"])
        raportari_api.adauga_mesaj(conn, rid, None, "ai", raportari_api.TEXT_ESCALADARE, schimba_stare=False, veste=False)
        f = raportari_api.firul_complet(conn, rid, cerut_de_uid=None, e_superadmin=True)["raportare"]
        assert (f["triaj_decizie"], f["triaj_motiv"]) == ("escaladare", decizie["motiv"])
        assert [m["text"] for m in f["mesaje"] if m["rol_autor"] == "ai"] == ["Sesizarea ta a fost transmisă echipei iConta.eu. Vei primi "
                                                                              "răspunsul aici, în acest fir."]
        u = raportari_api.firul_complet(conn, rid, cerut_de_uid=uid, e_superadmin=False)["raportare"]
        assert "triaj_motiv" not in u                                                # motivul intern nu ajunge la utilizator
        conn.rollback()


def test_confirmarile_vechi_primesc_diacriticele_la_migrare():
    """573, datele existente: confirmarea veche, fără diacritice, devine textul de acum; sesizările escaladate fără decizie scrisă primesc
    decizia „escaladare” și motivul „nu s-a păstrat” spus ca atare (nu se inventează)."""
    db.init_pool()
    with db.get_conn() as conn:
        m_triaj.aplica(conn)
        with conn.cursor() as c:
            c.execute("SELECT id, accounting_firm_id FROM public.users WHERE rol = 'admin_firma' ORDER BY id LIMIT 1")
            uid, cab = c.fetchone()
        rid = raportari_api.creeaza_raportare(conn, uid, cab, "veche", "sesizare veche 573")["raportare_id"]
        with conn.cursor() as c:
            c.execute("UPDATE public.raportari SET pentru_admin = true, triaj_decizie = NULL WHERE id = %s", (rid,))
            c.execute("INSERT INTO public.raportari_mesaje (raportare_id, rol_autor, text, citit) VALUES (%s, 'ai', %s, true)",
                      (rid, m_triaj.TEXT_VECHI))
        m_triaj.aplica(conn)
        with conn.cursor() as c:
            c.execute("SELECT triaj_decizie, triaj_motiv FROM public.raportari WHERE id = %s", (rid,))
            assert c.fetchone() == ("escaladare", m_triaj.MOTIV_VECHI)
            c.execute("SELECT text FROM public.raportari_mesaje WHERE raportare_id = %s AND rol_autor = 'ai'", (rid,))
            assert c.fetchall() == [(raportari_api.TEXT_ESCALADARE,)]
        conn.rollback()


# ── 648: răspunsul echipei ajunge în clopoțel ────────────────────────────────────────────────────────────────────────────────────
def test_raspunsul_adminului_scrie_notificarea_autorului(monkeypatch):
    """648: răspunsul Admin iConta într-un fir -> o notificare `raspuns_suport` pentru autorul sesizării, cu subiectul, legată de Suport
    (`deschide:raport`), de livrat pe canalul omului. MUTAȚIE: `_anunta_raspunsul` scos din `raportari_mesaj` -> pică."""
    import contextlib
    from core import notificari
    assert notificari.TIPURI["raspuns_suport"]["deschide"] == "raport" and notificari.implicit("raspuns_suport")
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute("SELECT id, accounting_firm_id FROM public.users WHERE rol = 'admin_firma' ORDER BY id LIMIT 1")
            uid, cab = c.fetchone()
            c.execute("SELECT id FROM public.users WHERE rol = 'superadmin' ORDER BY id LIMIT 1")
            sa = c.fetchone()[0]
        rid = raportari_api.creeaza_raportare(conn, uid, cab, "Export SAGA 648", "Cum export în SAGA?")["raportare_id"]

        class _P:
            def __getattr__(self, k):
                return getattr(conn, k)

            def commit(self):
                pass

        @contextlib.contextmanager
        def _aceeasi(*_a, **_k):
            yield _P()
        monkeypatch.setattr(db, "get_conn", _aceeasi)
        uc_raportari.raportari_mesaj(rid, types.SimpleNamespace(text="Exportul e în Facturi → Export."), {"rol": "superadmin", "uid": sa})
        with conn.cursor() as c:
            c.execute("SELECT tip, text, link, de_livrat FROM public.notificari WHERE user_id = %s ORDER BY id DESC LIMIT 1", (uid,))
            n = c.fetchone()
        conn.rollback()
    assert n == ("raspuns_suport", "Echipa iConta.eu ți-a răspuns la sesizarea „Export SAGA 648”. Răspunsul e în Suport.", "deschide:raport",
                 True), n


def test_textul_notificarii_raspunsului_se_scurteaza():
    t = uc_raportari.text_notificare_raspuns(None, "x" * 200)
    assert t.startswith("Echipa iConta.eu ți-a răspuns la sesizarea „") and "…”" in t and len(t) < 160
