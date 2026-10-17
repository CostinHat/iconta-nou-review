# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/raportari`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:840`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

import os

from core import db
from core.mesaje import mesaj_din_cod, DOAR_ADMIN_ICONTA, FARA_ACCES_RAPORTARE, FARA_ACCES
import core.raportari_api as _rap
from core import erori as _erori
from core import db
from core.mesaje import (mesaj_din_cod, DOAR_ADMIN_ICONTA, FARA_ACCES)
from core import fisiere_private as _fp


def raportari_creeaza(date, ctx):
    """[P7 · use-case] Corpul rutei `/raportari`; docstringul ei a ramas in stratul HTTP.

    [15.10.2026, deficienta 270d] `tip` = `cerere_import`: cererea de import din alta aplicatie. Primul mesaj il scrie aplicatia
    din `aplicatie` (omul trimite aplicatia si fisierele, nu un text); triajul AI nu se aplica — cererea e pentru echipa iConta."""
    tip = date.tip or "sesizare"
    text = date.text
    if tip == "cerere_import":
        text = "Cerere de import din aplicația «%s»." % (date.aplicatie or "").strip()
        if (date.text or "").strip():
            text += "\n\n" + date.text.strip()
    with db.get_conn() as conn:
        r = _rap.creeaza_raportare(conn, ctx["uid"], ctx.get("firm"), date.subiect, text, tip=tip, aplicatie=date.aplicatie)
        if r.get("ok"):
            # [17.10.2026, lotul 7 pct.2.3, verbatim în DECIZII] „Notificare pentru mine (superadmin) la fiecare cerere de import și
            # sesizare din Suport; acum ajung doar în Superadmin → Raportări.” În aceeași tranzacție cu cererea (o cerere anulată nu
            # anunță nimic); pleacă pe canalul superadminului după commit (`core/notificari.py`).
            from core import notificari as _notif_canal
            _notif_canal.pentru_superadmini(conn, tip, _rap.text_notificare(conn, r["raportare_id"]), "deschide:raportari")
    if not r.get("ok"):
        raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
    if tip == "sesizare":
        # [triaj_ai] AI raspunde la intrebarile de folosire sau escaladeaza (pentru_admin); nu blocheaza crearea
        import threading
        from core import raportari_ai as _rai
        threading.Thread(target=_rai.proceseaza, args=(r["raportare_id"], date.subiect, date.text), daemon=True).start()
    return r


def raportari_mele(ctx):
    """[P7 · use-case] Corpul rutei `/raportari/eu`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _rap.raportarile_mele(conn, ctx["uid"])


def raportari_contor(ctx):
    """[P7 · use-case] Corpul rutei `/raportari/contor`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _rap.contor_necitite(conn, ctx["uid"])


def raportari_admin(ctx):
    """[P7 · use-case] Corpul rutei `/raportari/admin`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        return _rap.toate_raportarile(conn)


def raportari_fir(rid, ctx):
    """[P7 · use-case] Corpul rutei `/raportari/{rid}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        r = _rap.firul_complet(conn, rid, cerut_de_uid=ctx["uid"], e_superadmin=(ctx["rol"] == "superadmin"))
        if not r.get("ok"):
            raise _erori.Inexistent(mesaj_din_cod(r.get("cod")))
        # acces: autorul firului sau superadmin
        if ctx["rol"] != "superadmin" and r["raportare"]["autor_id"] != ctx["uid"]:
            raise _erori.FaraDrept(FARA_ACCES_RAPORTARE)
        return r


def raportari_mesaj(rid, date, ctx):
    """[P7 · use-case] Corpul rutei `/raportari/{rid}/mesaj`; docstringul ei a ramas in stratul HTTP."""
    rol_autor = "admin" if ctx["rol"] == "superadmin" else "utilizator"
    with db.get_conn() as conn:
        # utilizatorul poate scrie doar in firele lui
        if rol_autor == "utilizator":
            f = _rap.firul_complet(conn, rid, cerut_de_uid=ctx["uid"], e_superadmin=False)
            if not f.get("ok"):
                raise _erori.Inexistent("Inexistent.")
            if f["raportare"]["autor_id"] != ctx["uid"]:
                raise _erori.FaraDrept(FARA_ACCES)
        r = _rap.adauga_mesaj(conn, rid, ctx["uid"], rol_autor, date.text)
    if not r.get("ok"):
        raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
    return r


def raportari_citit(rid, ctx):
    """[P7 · use-case] Corpul rutei `/raportari/{rid}/citit`; docstringul ei a ramas in stratul HTTP."""
    cine_rol = "admin" if ctx["rol"] == "superadmin" else "utilizator"
    with db.get_conn() as conn:
        # [izolare_raportari 09.08.2026] utilizatorul marcheaza citit DOAR firele lui (nu ale altui cabinet)
        if cine_rol == "utilizator":
            f = _rap.firul_complet(conn, rid, cerut_de_uid=ctx["uid"], e_superadmin=False)
            if not f.get("ok"):
                raise _erori.Inexistent("Inexistent.")
        return _rap.marcheaza_citit(conn, rid, cine_rol)


def raportari_stare(rid, date, ctx):
    """[P7 · use-case] Corpul rutei `/raportari/{rid}/stare`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        r = _rap.seteaza_stare(conn, rid, date.stare)
        conn.commit()
    if not r.get("ok"):
        raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
    return r


def raportari_pentru_admin(rid, date, ctx):
    """[P7 · use-case] Corpul rutei `/raportari/{rid}/pentru-admin`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        r = _rap.seteaza_pentru_admin(conn, rid, date.valoare)
    if not r.get("ok"):
        raise _erori.Inexistent(mesaj_din_cod(r.get("cod")))
    return r


def raportari_imagine(mid, continut, nume_fisier, ctx, cu_exporturi=False):
    """[P7 · use-case] Corpul rutei `/raportari/mesaj/{mid}/imagine` (capturi) si, cu `cu_exporturi`, al rutei
    `/raportari/mesaj/{mid}/fisier` (`raportari_fisier`).

    [15.10.2026, C36] Fisierul intra in depozitul privat (`core.fisiere_private`), nu in directorul servit: se descarca numai prin
    `/raportari/fisiere/{fid}`. Tipul se citeste din continut (semnatura), nu din `content_type`. Capturile (PNG / JPG / WEBP) se
    primesc pe orice fir; exporturile (CSV / XLS / XLSX / ZIP) numai pe ruta `/fisier` a unei cereri de import (270d)."""
    with db.get_conn() as conn:
        info = _rap.autor_mesajului(conn, mid)
        if not info:
            raise _erori.Inexistent("Mesaj inexistent.")
        # acces: superadmin, sau autorul mesajului
        if ctx["rol"] != "superadmin" and info["mesaj_autor"] != ctx["uid"]:
            raise _erori.FaraDrept(FARA_ACCES)
        permise = _fp.CAPTURI + (_fp.EXPORTURI if (cu_exporturi and info["tip"] == "cerere_import") else ())
        try:
            return dict(_fp.salveaza(conn, info["cabinet_id"], ctx["uid"], mid, nume_fisier, continut, permise), ok=True)
        except _fp.FisierRefuzat as e:
            raise (_erori.IntrarePreaMare if e.cod == "marime" else _erori.FormatNeacceptat)(str(e))


def raportari_fisier(mid, continut, nume_fisier, ctx):
    """[270d] Corpul rutei `/raportari/mesaj/{mid}/fisier`: capturile si exporturile unei cereri de import — acelasi corp ca la
    capturi (`raportari_imagine`), cu exporturile primite."""
    return raportari_imagine(mid, continut, nume_fisier, ctx, cu_exporturi=True)


def raportari_fisier_descarca(fid, ctx):
    """[C36] Corpul rutei `GET /raportari/fisiere/{fid}`: `(cale_pe_disc, nume, tip)` pentru echipa iConta sau autorul
    sesizarii, pe cabinetul lui; oricui altcuiva „nu exista” (404), ca la firul altui cabinet."""
    with db.get_conn() as conn:
        rand = _fp.al_firului(conn, fid, ctx["uid"], ctx.get("firm"), ctx["rol"] == "superadmin")
    if not rand:
        raise _erori.Inexistent(mesaj_din_cod("INEXISTENT"))
    cale = _fp.cale_pe_disc(rand)
    if not os.path.isfile(cale):
        raise _erori.Inexistent("Fișierul «%s» nu mai e în depozit." % rand["nume_orig"])
    return cale, rand["nume_orig"], rand["tip"]


def raportari_fisier_sterge(fid, ctx):
    """[270d] Corpul rutei `DELETE /raportari/fisiere/{fid}`: autorul sesizarii isi sterge fisierul — randul si fisierul de pe
    disc (dupa commit). Oricui altcuiva „nu exista”."""
    with db.get_conn() as conn:
        cale = _fp.sterge(conn, fid, ctx["uid"], ctx.get("firm"))
    if not cale:
        raise _erori.Inexistent(mesaj_din_cod("INEXISTENT"))
    if os.path.exists(cale):
        os.remove(cale)
    return {"ok": True, "sters": fid}
