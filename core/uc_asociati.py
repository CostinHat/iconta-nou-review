# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/tenants/{tenant_id}/asociati` (deficiența 431, lotul 10, comanda Costin 10.1).

[lotul 10, deficiența 431] „Fluxul e unul singur: asociații și cotele (cu istoricul cesiunilor) în datele firmei […]”. Secțiunea
„Asociați” din Date firmă: citirea, corectura structurii curente și cesiunea de părți sociale (cu data ei). Verificarea și scrierea
sunt ale importului (`asociati_import_api.verifica_randuri` / `importa` / `arhiveaza_pentru_cesiune`) — o singură logică, cu ecranul
de import; citirea pentru ecran e `asociati_api`. Use-case-ul deține tranzacția: un refuz nu lasă nimic scris (`db.get_conn` anulează
la excepție). Orice schimbare intră în jurnalul Date firmă (comanda Costin 06.10.2026 §6.4: „Orice modificare se jurnalizează (cine,
când, valoare veche → nouă)”), câmpul „asociati”.
"""
from core import db
from core import erori as _erori
from core import uc_comun as _uc_comun
from core import asociati_api as _as
from core import asociati_import_api as _imp
from core import repo_firma_profil as _rfp
from core.pdf_util import data_ro as _data_ro


def _text_structura(lista):
    """„Ion Popescu (1800101…) 60%; Ana Pop 40%” — forma de jurnal a unei structuri."""
    return "; ".join("%s %s%%" % (a["nume"], a["cota"]) for a in lista) or None


def asociati_citeste(tenant_id, ctx):
    """[431] Corpul rutei GET `/tenants/{tenant_id}/asociati`: structura curentă, de când e valabilă, istoricul cesiunilor."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        return _as.citeste(cur)


def _verifica(randuri):
    """Refuzul numit, pe câmpuri, înaintea oricărei scrieri: rândurile fără cotă, apoi verificarea comună (cu ANAF pentru CUI)."""
    if not randuri:
        raise _erori.DateInvalide("Scrie cel puțin un asociat, cu numele, CNP-ul (sau CUI-ul) și cota lui.")
    er = _as.erori_cota_lipsa(randuri)
    anaf = _imp.verificare_anaf(randuri) if not er else None
    if not er:
        er = _as.erori_pe_campuri(_imp.verifica_randuri(randuri, anaf))
    if er:
        mesaj = "; ".join(e["mesaj"] for e in er[:6])
        raise _erori.DateInvalide({"mesaj": "Asociații nu s-au salvat: %s." % mesaj,
                                   "erori_campuri": [e for e in er if e["camp"]]})
    return anaf


def _scrie(tenant_id, ctx, randuri, data_cesiune=None):
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    anaf = _verifica(randuri)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            inainte = _text_structura(_as.curenta(cur))
        from core import migrare_api as _mig
        try:
            # [lotul 10, deficiența 426] Date firmă → Asociați e corectura EXPLICITĂ a structurii arătate pe același ecran (cu jurnal
            # vechi -> nou): salvarea ei e confirmarea; poarta înlocuirii tăcute e a importului de migrare (`migrare.js`)
            rez = _imp.importa(conn, randuri, data_cesiune=data_cesiune, anaf=anaf, inlocuieste=True)
        except _mig.InlocuireNeconfirmata as e:   # contractul clasei (gard 426); cu `inlocuieste=True` nu se ridică
            raise _erori.Conflict(str(e))
        except ValueError as e:
            raise _erori.DateInvalide({"mesaj": str(e), "erori_campuri": [{"camp": "as-data-cesiune", "mesaj": str(e)}]}
                                      if data_cesiune else str(e))
        with conn.cursor() as cur:
            dupa = _text_structura(_as.curenta(cur))
            if data_cesiune:
                dupa = "%s (cesiune de la %s)" % (dupa, _data_ro(str(data_cesiune)[:10]))
            _rfp.jurnalizeaza_campuri(cur, {"asociati": inainte}, {"asociati": dupa}, ctx["uid"])
            return dict({"ok": True}, **rez, **_as.citeste(cur))


def asociati_salveaza(tenant_id, corp, ctx):
    """[431] Corpul rutei POST `/tenants/{tenant_id}/asociati`: CORECTURA structurii curente (scrisă greșit) — fără istoric."""
    return _scrie(tenant_id, ctx, _as.randuri_din_corp((corp or {}).get("randuri")))


def asociati_cesiune(tenant_id, corp, ctx):
    """[431] Corpul rutei POST `/tenants/{tenant_id}/asociati/cesiune`: transmiterea părților sociale (Legea 31/1990 art.202 alin.(1))
    de la `data_cesiune` — structura de până atunci intră în istoric, valabilă până în ziua dinainte (art.67 alin.(6))."""
    dc = str((corp or {}).get("data_cesiune") or "").strip()
    if not dc:
        m = "Scrie data cesiunii — de la ea dividendele se cuvin noii structuri (Legea 31/1990 art. 67 alin. (6))."
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "as-data-cesiune", "mesaj": m}]})
    return _scrie(tenant_id, ctx, _as.randuri_din_corp((corp or {}).get("randuri")), data_cesiune=dc)
