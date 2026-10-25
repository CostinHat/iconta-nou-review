# -*- coding: utf-8 -*-
"""USE_CASE — notificarea termenelor (deficiența 320, comanda Costin 17.10.2026 7.2, verbatim în DECIZII; tipul `termen_declaratie`).

Cardul 319 promite „termene de declarații” printre notificări, iar 320 cere „toate tipurile de notificări ale aplicației”: o dată pe zi, după
ora `ORA`, fiecare declarație datorată și încă nedepusă al cărei termen e peste `ZILE_INAINTE` zile intră în clopoțelul celor care pregătesc
pe firmă (administratorul cabinetului, asistenții cu „Poate pregăti” cărora le e alocată) — și pleacă pe canalul lor, dacă au bifat
„Termene și declarații” (bifate din oficiu). Termenele sunt ale motorului unic (`firma_rezumat`, aspectul „termene” — același calcul ca
ecranul Termene); o firmă cu termenele încă nerecalculate nu primește nimic în ziua aceea (nu se ghicește).

Rulează în bucla de sănătate, numai pe instanța lider (`main._ciclu_sanatate`); ziua se revendică în bază (`repo_notificari_termene`), deci
oricâte procese, o singură rulare pe zi.
"""
import datetime

from core import db
from core import repo_notificari_termene as _repo

ZILE_INAINTE = 3
ORA = 8


def de_notificat(termene, azi):
    """PURĂ. Termenele de peste `ZILE_INAINTE` zile, din lista motorului ([{tip, an, luna, perioada, termen}])."""
    tinta = (azi + datetime.timedelta(days=ZILE_INAINTE)).isoformat()
    return [t for t in termene or [] if str(t.get("termen"))[:10] == tinta]


def text(nume_firma, t):
    from core.common import cate
    from core.pdf_util import data_ro
    return "%s: %s · %s are termenul pe %s (peste %s) și nu e încă depusă." % (
        nume_firma, str(t.get("tip") or "").upper(), t.get("perioada") or "", data_ro(str(t.get("termen"))[:10]),
        cate(ZILE_INAINTE, "zi", "zile"))


def ruleaza(acum=None):
    """Câte notificări a scris (0 dacă ziua a fost deja notificată sau e prea devreme)."""
    import zoneinfo
    from core import firma_rezumat as _fr, notificari_api as _notif
    acum = acum or datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Bucharest"))
    if acum.hour < ORA:
        return 0
    azi = acum.date()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if not _repo.revendica_ziua(cur, azi.isoformat()):
                conn.rollback()
                return 0
            firme = _repo.firmele_cabinetelor(cur)
        conn.commit()
        rezumat = _fr.citeste(conn, [f[0] for f in firme], ["termene"], azi=azi)
        n = 0
        for tid, nume, cabinet in firme:
            st = (rezumat.get(tid) or {}).get("termene") or {}
            if st.get("stare") != _fr.CURENT:
                continue
            de_spus = de_notificat(((st.get("date") or {}).get("eval") or {}).get("termene"), azi)
            if not de_spus:
                continue
            with conn.cursor() as cur:
                uids = _repo.destinatarii_firmei(cur, cabinet, tid)
            for t in de_spus:
                for uid in uids:
                    _notif.adauga(conn, uid, "termen_declaratie", text(nume, t))
                    n += 1
        conn.commit()
    return n


def notifica_pe_conexiune(conn, schema, tip, text_fn):
    """[320] O notificare `tip` pentru cei care pregătesc pe firma din `schema` (administratorul cabinetului, asistenții cu „Poate pregăti”
    cărora le e alocată); `text_fn(nume_firma)` dă textul. Întoarce câte s-au scris.
    [lotul 12, C109] În tranzacția apelantului (nu deschide, nu comite): notificarea refuzului unei facturi recurente intră ODATĂ cu starea
    refuzului scrisă pe șablon — amândouă sau niciuna. O firmă fără cabinet n-are pe cine anunța (ca la termene și la SPV)."""
    from core import notificari_api as _notif
    with conn.cursor() as cur:
        f = _repo.firma_din_schema(cur, schema)
        if not f or not f[2]:
            return 0
        uids = _repo.destinatarii_firmei(cur, f[2], f[0])
    for uid in uids:
        _notif.adauga(conn, uid, tip, text_fn(f[1]))
    return len(uids)


def notifica_firma(schema, tip, text_fn):
    """`notifica_pe_conexiune` pe o conexiune proprie, comisă (citirea din SPV, după ce a adus facturile noi)."""
    with db.get_conn() as conn:
        n = notifica_pe_conexiune(conn, schema, tip, text_fn)
        conn.commit()
    return n
