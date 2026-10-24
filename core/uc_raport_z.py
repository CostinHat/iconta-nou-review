# -*- coding: utf-8 -*-
"""core/uc_raport_z.py — USE-CASE: ștergerea raportului Z nevalidat (lotul 12, deficiența C139).

C139 (găsită de Code la scenariul pilot, pasul 13): „Un raport Z importat (ciornă) nu se poate șterge de nicăieri: Registrul jurnal refuză
nota derivată, iar pentru Raport Z nu există drum de ștergere — un fișier AMEF importat greșit rămâne în lună.” Jurnalul trimite nota
raportului Z înapoi la documentul ei (`note_derivate.UNDE["raport_z"]`), deci drumul ștergerii stă pe rândul Z-ului din ecranul Raport Z.

Regula (domeniul: `z_descarcare.plan_stergere` / `sterge_z`): numai cât nota Z-ului e CIORNĂ, luna nu e blocată și nimic din ce ține de el
nu e la validare în cabinet; se șterg, într-o singură tranzacție, Z-ul, nota lui și descărcările lui din stoc încă necontate (marfa revine
în stoc), iar urma rămâne în audit. Un Z validat nu se șterge — corectura e stornarea (OMFP 1802/2014 pct.69).
"""
from core import db
from core import erori as _erori
from core import uc_comun as _uc_comun


def horeca_z_sterge(tenant_id, nota_id, ctx):
    """Corpul rutei `DELETE /tenants/{tenant_id}/horeca/raport-z/{nota_id}`. Refuzul are textul domeniului, codul și temeiul; luna
    blocată -> `Blocat` (ca restul porții de perioadă), celelalte -> `Conflict` (starea de acum nu îngăduie ștergerea)."""
    from core import z_descarcare as _zd
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        plan = _zd.sterge_z(conn, schema, nota_id, user_id=int(ctx["uid"]), tenant_id=int(tenant_id))
    if plan is None:
        raise _erori.Inexistent("Raportul Z ales nu există.")
    if plan["refuz"]:
        # refuzul e o AFIRMAȚIE TIPATĂ (P8, decizia 21.08: `core/afirmatii.afirmatie`), cu `mesaj` pentru ecran (contractul G10)
        from core import afirmatii as _af
        detaliu = dict(_af.afirmatie("neconformitate", plan["cod"], plan["refuz"], unde=plan["z"]["document"],
                                     regula=_zd.TEMEI_STERGERE), mesaj=plan["refuz"], cod=plan["cod"], temei=_zd.TEMEI_STERGERE)
        raise (_erori.Blocat if plan["cod"] == _zd.COD_LUNA_BLOCATA else _erori.Conflict)(detaliu)
    return {"ok": True, "sters": plan["z"], "note_iesiri": plan["note_iesiri"], "miscari_stoc": len(plan["miscari"]),
            "rip": plan["rip"], "mesaj": plan["dupa"]}
