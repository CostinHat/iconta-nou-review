# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), zona admin — suspendarea unui cabinet cu motiv (645), anunțurile (646), invitațiile retrase (646 e).

Anexa comenzii 13.1, 645 (decizia Costin + arhitect, 24.10.2026, verbatim): „motiv obligatoriu din listă fixă — neplată, la cererea
cabinetului, încălcarea termenilor, acces suspect / securitate, la cererea unei autorități — plus notă internă opțională. La logare apare
motivul ales, transparent, fără linie de contact (Costin, 24.10); nota internă nu se arată. […] Email către administratorul cabinetului
la suspendare, cu același motiv. Cine, când, motivul și reactivarea rămân în jurnal.”
646 a: „bifă explicită «Toate cabinetele» sus; fără nicio bifă trimiterea e refuzată”; 646 c: „lista anunțurilor trimise (către cine,
citit sau nu, retragere)”; 646 e: „retragerea unei invitații”.

Pe baza de TEST, în tranzacții anulate (cabinetul și utilizatorii sintetici nu rămân). Migrările lotului (`core/migrare_suspendari_cabinet.py`,
`core/migrare_anunturi_trimiteri.py`) se aplică în aceeași tranzacție — testul nu depinde de starea bazei.
"""
import contextlib
import datetime
import os
import re
import types

import pytest

from core import db, erori, invitatii as inv, repo_admin, uc_admin
from core import migrare_anunturi_trimiteri as m_an, migrare_suspendari_cabinet as m_sus


@contextlib.contextmanager
def _tranzactie_anulata():
    """`db.get_conn` legat la O conexiune, anulată la final: use-case-urile își deschid singure tranzacția (`with db.get_conn()`), deci
    le dăm aceeași conexiune, fără commit."""
    db.init_pool()
    with db.get_conn() as conn:
        m_sus.aplica(conn)
        m_an.aplica(conn)

        class _Fara_commit:
            """Conexiunea probei: commit-ul use-case-ului nu închide tranzacția (se anulează la final)."""
            def __getattr__(self, k):
                return getattr(conn, k)

            def commit(self):
                pass

            def rollback(self):   # citirile use-case-urilor se încheie cu rollback: tranzacția probei rămâne a probei
                pass

        prox = _Fara_commit()

        @contextlib.contextmanager
        def _aceeasi(*_a, **_k):
            yield prox

        vechi = db.get_conn
        db.get_conn = _aceeasi
        try:
            yield prox
        finally:
            db.get_conn = vechi
            conn.rollback()


@pytest.fixture()
def baza():
    with _tranzactie_anulata() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('Cabinet probă 645 (sintetic)') RETURNING id")
            cab = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email, password_hash, rol, activ, accounting_firm_id, prenume) "
                        "VALUES ('admin.645@exemplu.ro', 'x', 'admin_firma', true, %s, 'Ana') RETURNING id", (cab,))
            uid_admin = cur.fetchone()[0]
            cur.execute("SELECT id FROM public.users WHERE rol = 'superadmin' ORDER BY id LIMIT 1")
            sa = cur.fetchone()
        yield types.SimpleNamespace(conn=conn, cab=cab, uid_admin=uid_admin, superadmin=(sa[0] if sa else None))


def _ctx(b):
    return {"rol": "superadmin", "uid": b.superadmin, "firm": None}


def test_check_ul_bazei_are_exact_motivele_din_cod():
    """Lista fixă e una: cheile `uc_admin.MOTIVE_SUSPENDARE` = CHECK-ul tabelei (migrarea). MUTAȚIE: un motiv în plus în cod -> pică."""
    assert tuple(uc_admin.MOTIVE_SUSPENDARE) == m_sus.MOTIVE
    assert list(uc_admin.MOTIVE_SUSPENDARE.values()) == ["neplată", "la cererea cabinetului", "încălcarea termenilor și condițiilor",
                                                        "acces suspect / securitate", "la cererea unei autorități"]


def test_textul_de_logare_spune_motivul_fara_linie_de_contact():
    """„La logare apare motivul ales, transparent, fără linie de contact.” Fără motiv cunoscut (suspendat înainte de jurnal): numai
    faptul. MUTAȚIE: `text_suspendare` întoarce numai `TEXT_SUSPENDAT` -> pică."""
    assert uc_admin.text_suspendare("neplata") == "Cabinetul este suspendat. Motivul: neplată."
    assert uc_admin.text_suspendare(None) == "Cabinetul este suspendat."
    for m in uc_admin.MOTIVE_SUSPENDARE:
        t = uc_admin.text_suspendare(m)
        assert not re.search(r"contact|furnizor|telefon|@", t, re.I), t


def test_suspendarea_cere_motivul_din_lista(baza):
    """Fără motiv / cu un motiv din afara listei: refuz, nimic scris. MUTAȚIE: verificarea motivului scoasă -> pică."""
    for motiv in (None, "", "altceva"):
        with pytest.raises(erori.DateInvalide):
            uc_admin.admin_cabinet_suspenda(baza.cab, types.SimpleNamespace(motiv=motiv, nota_interna=None), _ctx(baza))
    with baza.conn.cursor() as cur:
        cur.execute("SELECT activ FROM public.accounting_firms WHERE id = %s", (baza.cab,))
        assert cur.fetchone()[0] is True
        assert repo_admin.suspendarea_deschisa(cur, baza.cab) is None


def test_suspendarea_scrie_jurnalul_trimite_emailul_si_reactivarea_il_inchide(baza, monkeypatch):
    """Suspendare cu „neplata” + notă internă: cabinetul inactiv; jurnalul (cine, când, motivul, nota); emailul către administratorul
    cabinetului, cu motivul și fără nota internă; logarea spune motivul. Reactivarea închide rândul (cine, când)."""
    from core import observare as obs
    trimise = []
    monkeypatch.setattr(obs, "trimite_email_html_sau_semnaleaza", lambda et, catre, subiect, html, **k: trimise.append((catre, subiect, html)) or True)
    r = uc_admin.admin_cabinet_suspenda(baza.cab, types.SimpleNamespace(motiv="neplata", nota_interna="  restanță din septembrie  "),
                                        _ctx(baza))
    assert r == {"ok": True, "motiv": "neplată", "emailuri_trimise": 1, "destinatari": 1}, r
    assert [t[0] for t in trimise] == ["admin.645@exemplu.ro"]
    assert "Motivul: <b>neplată</b>" in trimise[0][2] and "restanță" not in trimise[0][2]      # nota internă nu pleacă la cabinet
    with baza.conn.cursor() as cur:
        cur.execute("SELECT activ FROM public.accounting_firms WHERE id = %s", (baza.cab,))
        assert cur.fetchone()[0] is False
        j = uc_admin.jurnal_suspendari(cur, baza.cab)
        assert len(j) == 1 and j[0]["motiv_suspendare"] == "neplată" and j[0]["nota_interna"] == "restanță din septembrie"
        assert j[0]["suspendat_la"] and j[0]["reactivat_la"] is None and j[0]["emailuri_trimise"] == 1
        assert uc_admin.text_suspendare_cabinet(cur, baza.cab) == "Cabinetul este suspendat. Motivul: neplată."
    with pytest.raises(erori.Conflict):                                          # o singură suspendare deschisă
        uc_admin.admin_cabinet_suspenda(baza.cab, types.SimpleNamespace(motiv="securitate", nota_interna=None), _ctx(baza))
    uc_admin.admin_cabinet_reactiveaza(baza.cab, _ctx(baza))
    with baza.conn.cursor() as cur:
        j = uc_admin.jurnal_suspendari(cur, baza.cab)
        assert j[0]["reactivat_la"] is not None and repo_admin.suspendarea_deschisa(cur, baza.cab) is None
        cur.execute("SELECT activ FROM public.accounting_firms WHERE id = %s", (baza.cab,))
        assert cur.fetchone()[0] is True


def test_cabinetul_suspendat_inainte_de_jurnal_primeste_randul_fara_motiv(baza):
    """Datele existente: un cabinet deja suspendat (`activ = false`, fără jurnal) primește la migrare un rând deschis, cu motivul și data
    necunoscute — logarea spune numai „Cabinetul este suspendat.” (nu se inventează un motiv). Idempotent."""
    with baza.conn.cursor() as cur:
        cur.execute("UPDATE public.accounting_firms SET activ = false WHERE id = %s", (baza.cab,))
    m_sus.aplica(baza.conn)
    m_sus.aplica(baza.conn)
    with baza.conn.cursor() as cur:
        cur.execute("SELECT count(*), max(motiv), max(suspendat_la) FROM public.suspendari_cabinet WHERE cabinet_id = %s", (baza.cab,))
        assert cur.fetchone() == (1, None, None)
        assert uc_admin.text_suspendare_cabinet(cur, baza.cab) == "Cabinetul este suspendat."


def test_activitatea_cabinetelor_numara_utilizatorii_si_spune_motivul(baza, monkeypatch):
    """644 b („«Angajați» … înseamnă conturile de utilizator”): cheia e `nr_utilizatori`; 645: rândul cabinetului suspendat poartă motivul."""
    from core import observare as obs
    monkeypatch.setattr(obs, "trimite_email_html_sau_semnaleaza", lambda *a, **k: True)
    uc_admin.admin_cabinet_suspenda(baza.cab, types.SimpleNamespace(motiv="autoritate", nota_interna=None), _ctx(baza))
    rand = [c for c in uc_admin.admin_activitate_cabinete(_ctx(baza))["cabinete"] if c["id"] == baza.cab][0]
    assert rand["nr_utilizatori"] == 1 and "nr_angajati" not in rand
    assert rand["motiv_suspendare"] == "la cererea unei autorități" and rand["suspendat_la"] is not None


# ── 646: anunțurile ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _anunt(**k):
    d = dict(mesaj="Anunț de probă 646", cabinet_id=None, data_afisare=None, segment=None, cabinet_ids=None, tenant_ids=None)
    d.update(k)
    return types.SimpleNamespace(**d)


def test_anuntul_fara_destinatari_alesi_e_refuzat(baza):
    """646 a: „fără nicio bifă trimiterea e refuzată” — nici segmentul gol, nici „cabinete” fără listă nu mai înseamnă „toate”.
    MUTAȚIE: ramura „toate” pusă la loc pentru segmentul gol -> pică."""
    for d in (_anunt(), _anunt(segment="cabinete", cabinet_ids=[]), _anunt(segment="altceva")):
        with pytest.raises(erori.DateInvalide) as e:
            uc_admin.admin_anunt_creeaza(d, _ctx(baza))
        assert "Toate cabinetele" in str(e.value.args[0])
    with baza.conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.anunturi_cabinet WHERE mesaj = 'Anunț de probă 646'")
        assert cur.fetchone()[0] == 0


def test_trimiterea_se_listeaza_cu_cititul_si_se_retrage(baza):
    """646 c: trimiterea la cabinetul ales = un rând în lista trimiterilor (către 1, citit 0 din 1); retragerea o scoate din anunțurile
    cabinetului; a doua retragere e refuzată. 646 d: anunțul cabinetului poartă data (fereastra o arată)."""
    r = uc_admin.admin_anunt_creeaza(_anunt(segment="cabinete", cabinet_ids=[baza.cab]), _ctx(baza))
    assert r["trimise"] == 1 and r["lot"]
    t = [x for x in uc_admin.admin_anunturi_lista(_ctx(baza))["trimiteri"] if x["lot"] == r["lot"]][0]
    assert (t["destinatari"], t["citite"], t["retras_la"], t["cabinete"][0]["citit_la"]) == (1, 0, None, None)
    with baza.conn.cursor() as cur:
        a = repo_admin.anunturi_pentru_cabinet(cur, baza.cab)
        assert len(a) == 1 and a[0][2] is not None                                 # creat_la: data din fereastra anunțului
    uc_admin.admin_anunt_retrage(r["lot"], _ctx(baza))
    with baza.conn.cursor() as cur:
        assert repo_admin.anunturi_pentru_cabinet(cur, baza.cab) == []
    with pytest.raises(erori.Conflict):
        uc_admin.admin_anunt_retrage(r["lot"], _ctx(baza))


def test_anunturile_vechi_primesc_trimiterea_lor_la_migrare(baza):
    """Datele existente: rândurile de dinainte (fără `lot`) se leagă după trimiterea din care au venit — același mesaj, aceeași oră."""
    with baza.conn.cursor() as cur:
        cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj, creat_la) VALUES (%s, 'vechi 646', '2099-01-01 10:00'), "
                    "(%s, 'vechi 646', '2099-01-01 10:00'), (%s, 'alt vechi 646', '2099-01-02 10:00') RETURNING id",
                    (baza.cab, baza.cab, baza.cab))
        ids = [x[0] for x in cur.fetchall()]
        cur.execute("UPDATE public.anunturi_cabinet SET lot = NULL WHERE id = ANY(%s)", (ids,))
    m_an.aplica(baza.conn)
    with baza.conn.cursor() as cur:
        cur.execute("SELECT id, lot FROM public.anunturi_cabinet WHERE id = ANY(%s) ORDER BY id", (ids,))
        rez = cur.fetchall()
    assert [l for _i, l in rez] == [ids[0], ids[0], ids[2]], rez


# ── 646 e: invitația retrasă ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_invitatia_retrasa_nu_mai_creeaza_cont(baza):
    """646 e: retragerea unei invitații nefolosite: starea ei devine RETRASA (linkul nu mai creează cont), lista o arată „retrasă”, iar
    o a doua retragere nu mai are ce retrage. MUTAȚIE: verificarea `retrasa_la` scoasă din `stare` -> pică."""
    with baza.conn.cursor() as cur:
        tok = inv.creeaza(cur, "retras.646@exemplu.ro", None)
        cur.execute("SELECT id FROM public.invitatii_cabinet WHERE email = 'retras.646@exemplu.ro'")
        iid = cur.fetchone()[0]
        assert [x["stare"] for x in inv.lista(cur) if x["id"] == iid] == ["valabilă"]
        assert inv.retrage(cur, iid) == "retras.646@exemplu.ro"
        s = inv.stare(cur, tok)
        assert s["valida"] is False and s["refuz"]["cod"] == "RETRASA" and "retrasă" in s["refuz"]["motiv"]
        assert [x["stare"] for x in inv.lista(cur) if x["id"] == iid] == ["retrasă"]
        assert inv.retrage(cur, iid) is None
        with pytest.raises(ValueError):
            inv.consuma(cur, tok, "retras.646@exemplu.ro", baza.cab)


def test_datele_actului_din_propunerile_monitorului(baza):
    """646 b: propunerile monitorului fiscal poartă data publicării și data intrării în vigoare (None = nu apare în sursă)."""
    with baza.conn.cursor() as cur:
        cur.execute("INSERT INTO public.alerte_fiscale (sursa, titlu, rezumat, relevanta, vazut, data_vigoare, data_publicarii) "
                    "VALUES ('portal_alerta', 'Act de probă 646 b', 'r', 'mare', false, '2099-02-01', '2099-01-15') RETURNING id")
        aid = cur.fetchone()[0]
    a = [x for x in uc_admin.admin_alerte_fiscale(_ctx(baza))["alerte"] if x["id"] == aid][0]
    assert (a["data_publicarii"], a["data_vigoare"]) == ("2099-01-15", "2099-02-01")


def test_monitorul_cere_data_publicarii_ca_fapt():
    """646 b: analiza cere `data_publicarii` (un fapt, ca `data_vigoare`), iar o dată ghicită greșit nu se scrie."""
    from core import clasificator_alerte as ca, monitor_fiscal as mf
    assert "data_publicarii" in ca.CAMPURI_CERUTE and '"data_publicarii"' in mf.PROMPT
    assert mf._data_iso("2026-10-08") == "2026-10-08" and mf._data_iso("08.10.2026") is None and mf._data_iso(None) is None


def test_pragurile_sanatatii_stau_intr_un_singur_loc():
    """643: pragurile pe care le arată ecranul sunt ale alertei (`alerta_load`): încărcarea = numărul de procesoare, RAM / disc 75%,
    conexiunile = workeri × pool + 10."""
    from core import alerta_load as al
    p = al.praguri(4, "2", 10)
    assert p == {"load": 4.0, "ram_procent": 75, "disc_procent": 75, "conexiuni_db": 30}, p
    assert os.cpu_count() is None or al.praguri(None, None, 10)["load"] == 1.0
