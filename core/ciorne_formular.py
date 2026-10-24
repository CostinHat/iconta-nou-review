# -*- coding: utf-8 -*-
"""core/ciorne_formular.py — ciornele formularelor începute, păstrate pe server (deficiența 495, lotul 12, comanda 12.1, cu clasa ei).

Costin: „Factură: Ciorna facturii e salvată doar în browser; pe alt calculator nu se regăsește.” Până acum ciorna formularului
„Emite factură” — și a formularelor lungi de creare (salariatul nou, concediul medical, `static/js/ciorna_formular.js`) — stătea numai
în `localStorage`. Acum locul ei e `public.ciorne_formular` (`core/migrare_ciorne_formular.py`): un rând pe UTILIZATOR + FIRMĂ +
FORMULAR — ciorna unui utilizator nu apare la altul și nici la altă firmă (deficiența 65), iar pe alt calculator același utilizator, la
aceeași firmă, își regăsește formularul început.

Ecranele scriu ciorna întâi în browser (ca nimic să nu se piardă la o reîncărcare imediată), apoi o trimit aici; după ce serverul a
primit-o, copia din browser se șterge. La deschidere, o copie rămasă în browser (netrimisă, sau ciorna veche de dinainte de 495) se
urcă aici dacă e mai nouă; altfel se reface ciorna de aici. Ciorna se șterge pe drumurile de până acum (documentul salvat / emis,
„Renunță”, formularul golit de om).

Rutele (stratul HTTP, `main.py`): `GET/PUT/DELETE /tenants/{tenant_id}/ciorne-formular/{formular}`; ciorna e a celui care o scrie, la o
firmă la care are acces (`uc_comun._schema_sau_404`). Citirea cere doar sesiunea (`cere_context`); scrierea și ștergerea cer «Poate
pregăti» (`cere_drept(PREGATI)`), ca salvarea formularelor care își păstrează ciorna (emiterea facturii, salariatul nou, concediul
medical): cine nu poate salva documentul n-are ce formular începe pe firmă.

Straturi (P7): modulul ăsta e use-case-ul (deține tranzacția); SQL-ul e în `core/repo_ciorne_formular.py`.
"""
import json
import re

from core import db
from core import erori as _erori
from core import repo_ciorne_formular as _repo

#: Ciorna e un formular completat: câțiva KB. Peste prag nu e un formular început, e o cerere greșită.
LIMITA_OCTETI = 256 * 1024
#: Numele formularului: „factura”, „salariat_nou”, „concediu_medical:<id salariat>” (aceeași regulă ca CHECK-ul tabelei).
FORMULAR = re.compile(r"^[a-z][a-z0-9_]{0,40}(:[0-9]{1,12})?$")
MESAJ_PREA_MARE = ("Formularul început are prea mult text ca să fie păstrat pe server (peste 256 KB). Ce ai scris rămâne pe ecran; "
                   "salvează documentul sau scurtează textul.")
MESAJ_FORMA = "Ciorna trebuie trimisă ca formularul completat (câmpurile lui)."
MESAJ_FORMULAR = "Formularul %r nu e unul din formularele aplicației care își păstrează ciorna."


# ---------- use-case (rutele) ----------
def _acces(tenant_id, formular, ctx):
    if not FORMULAR.match(str(formular or "")):
        raise _erori.DateInvalide(MESAJ_FORMULAR % (formular,))
    from core import uc_comun as _uc
    _uc._schema_sau_404(ctx, tenant_id)   # firma există și utilizatorul are acces la ea; altfel 404, ca orice rută a firmei
    return int(ctx["uid"]), int(tenant_id)


def ciorna_citeste(tenant_id, formular, ctx):
    """Corpul rutei `GET /tenants/{tenant_id}/ciorne-formular/{formular}`: `{"ciorna": <formularul> | null}`."""
    uid, tid = _acces(tenant_id, formular, ctx)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            c = _repo.citeste(cur, uid, tid, formular)
        conn.rollback()
    return {"ciorna": c}


def ciorna_scrie(tenant_id, formular, corp, ctx):
    """Corpul rutei `PUT /tenants/{tenant_id}/ciorne-formular/{formular}` (`{"continut": {...}}`): `{"ok": true, "salvat_la": ...}`."""
    continut = corp.get("continut") if isinstance(corp, dict) else None
    if not isinstance(continut, dict):
        raise _erori.DateInvalide(MESAJ_FORMA)
    if len(json.dumps(continut, ensure_ascii=False).encode("utf-8")) > LIMITA_OCTETI:
        raise _erori.DateInvalide(MESAJ_PREA_MARE)
    uid, tid = _acces(tenant_id, formular, ctx)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cand = _repo.scrie(cur, uid, tid, formular, continut)
        conn.commit()
    return {"ok": True, "salvat_la": cand}


def ciorna_sterge(tenant_id, formular, ctx):
    """Corpul rutei `DELETE /tenants/{tenant_id}/ciorne-formular/{formular}`: `{"ok": true, "stearsa": bool}` (a doua ștergere nu e o eroare)."""
    uid, tid = _acces(tenant_id, formular, ctx)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            s = _repo.sterge(cur, uid, tid, formular)
        conn.commit()
    return {"ok": True, "stearsa": s}
