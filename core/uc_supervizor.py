# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/supervizor`.

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

from core import db, auth_api, supervizor
from core.common import azi_ro


def supervizor_la_cerere(ctx):
    """[P7 · use-case] Corpul rutei `/supervizor`; docstringul ei a ramas in stratul HTTP."""
    azi = azi_ro()   # [fus] perioada evaluată = zi RO, ca la /control-fiscal și ca în cronul de 08:00
    with db.get_conn() as conn:
        ale_mele = auth_api.tenantii_userului(conn, ctx["uid"])
    # [P3, 09.09.2026] SCHEMA VINE DIN LISTA DEJA CITITĂ, nu se recere firmă cu firmă.
    #
    # Bucla de aici chema `auth_api.schema_tenant(c, uid, tid)` pentru fiecare firmă, fiecare cu
    # conexiunea ei din pool: măsurat, `q = 5 + 2*N`, `c = 4 + 1*N` — 2.005 interogări și 1.004
    # conexiuni la 1000 de firme, DOAR ca să afle numele schemei și să reverifice accesul.
    #
    # **Reverificarea era redundantă, și se poate arăta:** `tenantii_userului` filtrează pe exact
    # aceleași reguli ca `schema_tenant` — superadmin → firme fără cabinet; admin_firma → firmele
    # cabinetului lui; restul → prin `user_tenants` —, toate cu `activ = true`, și întoarce deja
    # `schema_name`. Pentru o firmă venită din acea listă, `schema_tenant` nu poate întoarce
    # altceva. Gardat de `core/test_p3_wave_a.py`, care compară cele două căi firmă cu firmă pe
    # portofoliul real, în loc să creadă echivalența pe cuvânt.
    #
    # Garda `if not schema` RĂMÂNE: e ieftină, iar o firmă fără `schema_name` n-are ce căuta în
    # rezultat. Ce dispare e conexiunea per firmă, nu verificarea.
    firme = []
    for f in ale_mele:
        schema = f.get("schema_name")
        if not schema:
            continue   # fara acces la tenant — nu se afiseaza (identic cu semaforul /control-fiscal)
        firme.append({"tenant_id": f.get("id"), "schema": schema, "nume": f.get("nume")})
    # [P1, 08.09.2026] CITEȘTE rezultatele persistate — NU recalculează portofoliul la fiecare GET.
    # Măsurat înainte: 9 ms/firmă, adică ~5 s la 1000 de firme, peste ținta cerută (p95 < 1 s).
    # Măsurat după, pe 1000 de firme cu sarcină realistă: p95 = 45 ms, într-o singură interogare.
    #
    # FIECARE FIRMĂ ÎȘI POARTĂ STAREA. O valoare veche NU se arată ca fiind curentă: `stare` e
    # `curent` / `invalidat` / `lipseste`, derivată din compararea versiunii sursei cu cea din care
    # s-a calculat rezultatul. Un rezultat `invalidat` se ARATĂ — e ultima măsurătoare bună — dar
    # etichetat, cu `calculat_la`. *O stare „în recalculare" declarată e acceptabilă; una veche și
    # tăcută nu e.*
    from core import supervizor_cache as _sc
    ids = [f["tenant_id"] for f in firme]
    with db.get_conn() as conn:
        stari = _sc.citeste(conn, ids, azi.year, azi.month)

    randuri = []
    for f in firme:
        st = stari.get(f["tenant_id"]) or {"rezultat": None, "stare": _sc.LIPSESTE,
                                           "calculat_la": None, "versiune_sursa": None,
                                           "versiune_curenta": 0}
        rez = st["rezultat"] or {}
        randuri.append({
            "tenant_id": f["tenant_id"], "nume": f.get("nume"),
            "constatari": rez.get("constatari") or [],
            "de_confirmat": rez.get("de_confirmat") or 0,
            "rezultat": rez.get("rezultat") or supervizor.NEVERIFICAT,
            # o firmă fără rezultat NU tace: spune că e NECALCULATĂ, cu aceeași formă tipată ca
            # celelalte două feluri de neverificare.
            "neverificat": rez.get("neverificat") or (
                None if st["stare"] != _sc.LIPSESTE else
                supervizor._neverificat(f, "rezultatul nu a fost calculat încă (recalculare "
                                           "asincronă); nu e un defect, e o așteptare",
                                        supervizor.NECALCULAT)),
            "prospetime": {"stare": st["stare"], "calculat_la": st["calculat_la"],
                           "versiune_sursa": st["versiune_sursa"],
                           "versiune_curenta": st["versiune_curenta"]},
        })

    nerecalculate = sum(1 for x in randuri if x["prospetime"]["stare"] != _sc.CURENT)
    return {
        "an": azi.year, "luna": azi.month,
        "domeniu": ("firmele la care are acces utilizatorul curent (%d), NU tot portofoliul; "
                    "supervizorul rulează zilnic pe portofoliu, ecranul arată partea ta" % len(firme)),
        "firme": randuri,
        "rezumat": supervizor.rezumat_din_randuri(randuri) if hasattr(supervizor, "rezumat_din_randuri")
                   else {"firme": len(randuri)},
        # Contor, nu afirmație: afirmația despre o firmă e `neverificat`, și e tipată. Firmele cu
        # `invalidat`/`lipseste` își poartă starea fiecare, în `prospetime.stare` — aici e doar
        # câte sunt.
        "nerecalculate": nerecalculate,
        "tipuri_neatribuite": supervizor.tipuri_neatribuite(),
    }
