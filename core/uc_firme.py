# -*- coding: utf-8 -*-
"""USE_CASE — corpurile rutelor `/firme`.

[P7 · valul use-case, 13.09.2026] Corpurile au plecat din `main.py` VERBATIM, cu tranzactiile lor
cu tot: `with db.get_conn()` se deschide aici, in stratul care detine unitatea de lucru, nu in
stratul HTTP. `HTTPException(cod, mesaj)` a devenit `_erori.<Clasa>(mesaj)`; codul se pune la loc
in invelisul din `main.py`, dintr-o harta fixa. Mesajul si ordinea efectelor sunt neatinse.
"""
from core import db, auth_api
from core import erori as _erori
from core import uc_comun as _uc_comun


def firma_verificari(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/firme/{tenant_id}/verificari`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("tenant inexistent sau fără acces")
    return _uc_comun._verificari_contabile(schema, an, luna)  # cf_verificari_v1
