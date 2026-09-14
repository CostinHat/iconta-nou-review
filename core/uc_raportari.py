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

from core import db
from core.mesaje import mesaj_din_cod, DOAR_ADMIN_ICONTA, FARA_ACCES_RAPORTARE, FARA_ACCES
import core.raportari_api as _rap
from core import erori as _erori
from core import db
from core.mesaje import (mesaj_din_cod, DOAR_ADMIN_ICONTA, FARA_ACCES)
from core import uc_comun as _uc_comun


def raportari_creeaza(date, ctx):
    """[P7 · use-case] Corpul rutei `/raportari`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        r = _rap.creeaza_raportare(conn, ctx["uid"], ctx.get("firm"), date.subiect, date.text)
    if not r.get("ok"):
        raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
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


def raportari_imagine(mid, continut, nume_fisier, tip_continut, ctx):
    """[P7 · use-case] Corpul rutei `/raportari/mesaj/{mid}/imagine`; docstringul ei a ramas in stratul HTTP."""
    import os as _os, uuid as _uuid
    tip = (tip_continut or "").lower()
    if tip not in ("image/png", "image/jpeg", "image/jpg", "image/webp"):
        raise _erori.FormatNeacceptat("Doar capturi de ecran (PNG, JPG, WEBP).")
    continut = continut
    if len(continut) > 8 * 1024 * 1024:
        raise _erori.IntrarePreaMare("Imaginea e prea mare (max 8MB).")
    with db.get_conn() as conn:
        info = _rap.autor_mesajului(conn, mid)
        if not info:
            raise _erori.Inexistent("Mesaj inexistent.")
        # acces: superadmin, sau autorul mesajului
        if ctx["rol"] != "superadmin" and info["mesaj_autor"] != ctx["uid"]:
            raise _erori.FaraDrept(FARA_ACCES)
        ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg",
               "image/webp": ".webp"}.get(tip, ".png")
        nume = "r%d_m%d_%s%s" % (info["raportare_id"], mid, _uuid.uuid4().hex[:8], ext)
        director = _os.path.join(_uc_comun._STATIC_DIR, "raportari")
        _os.makedirs(director, exist_ok=True)
        cale_disc = _os.path.join(director, nume)
        with open(cale_disc, "wb") as fh:
            fh.write(continut)
        cale_web = "/static/raportari/" + nume
        r = _rap.adauga_atasament(conn, mid, cale_web, nume_fisier)
    if not r.get("ok"):
        raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
    return {"ok": True, "cale": cale_web}

