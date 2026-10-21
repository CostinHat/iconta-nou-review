# -*- coding: utf-8 -*-
"""USE_CASE — compensarea creanțelor și datoriilor reciproce cu același partener (lotul 10, deficiența 428).

Deciziile Costin 20.10.2026 (verbatim în DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”): „Construiesc acum” — tabelă de
compensări (factura emisă ↔ factura primită, suma, data) și ecran; fiecare compensare stinge cele două facturi și mută TVA-ul prin același
punct ca banca și casa.

Temeiul și regulile: `core/compensari_api.py` (Codul civil art.1616-1617, HG 685/1999 anexa 2 art.5 și 11, OMFP 1802/2014 pct.56
alin.(3), HG 1/2016 pct.26 alin.(7) și (9), CF art.282 alin.(3), (8)). Aici: tranzacția, perioada (P15 — nota nouă nu intră într-o lună
închisă) și notele (ciornă — R36: nimic nu se scrie `validata` direct). Ștergerea unei compensări = ștergerea notei ei ciornă din
Registrul jurnal (rândul `compensari` cade cu ea, ON DELETE CASCADE); o notă validată se corectează prin storno, nu se șterge.
"""
import datetime as _dt

from core import compensari_api as _cz
from core import db
from core import erori as _erori
from core import uc_comun as _uc_comun


def compensari_propunere(tenant_id, ctx):
    """Partenerii cu facturi emise neîncasate și primite neplătite, cu facturile, restul fiecăreia și perechile propuse."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        return _cz.propunere(conn, schema)


def _refuz(e):
    return _erori.Conflict(e.mesaj) if e.cod == _cz.COD_STARE else _erori.DateInvalide(e.mesaj)


def compensari_genereaza(tenant_id, corp, ctx):
    """Scrie compensarea: corp {data, numar (numărul ordinului de compensare), perechi: [{factura_emisa_id, factura_primita_id, suma}]}.
    O notă ciornă pe pereche (401 = 4111 + liniile TVA la încasare ale ambelor facturi), toate cu documentul „Ordin de compensare nr … din
    …”. Întoarce notele (etichetele lor), liniile fiecăreia și totalul compensat."""
    if not isinstance(corp, dict):
        raise _erori.DateInvalide("Cererea trebuie să conțină data, numărul ordinului și perechile de facturi.")
    data = str(corp.get("data") or "").strip()
    numar = str(corp.get("numar") or "").strip()
    perechi = corp.get("perechi") or []
    if not numar:
        # HG 685/1999 anexa 2 art.11: „Ordinele de compensare au regim special, sunt numerotate din tipografie” — numărul e al ordinului
        raise _erori.CerereGresita({"mesaj": "Scrie numărul ordinului de compensare: e documentul justificativ al notei (HG 685/1999).",
                                    "erori_campuri": [{"camp": "cz-numar", "mesaj": "Scrie numărul ordinului de compensare."}]})
    if len(numar) > 40:
        raise _erori.DateInvalide("Numărul ordinului de compensare are cel mult 40 de caractere.")
    if not isinstance(perechi, list):
        raise _erori.DateInvalide("Perechile de facturi trebuie trimise ca listă.")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        _uc_comun._cere_luna_deschisa(conn, schema, data)   # validează și data (zi din calendar)
        zi = _dt.date.fromisoformat(data[:10])
        try:
            verificate = _cz.verifica(conn, schema, zi.isoformat(), perechi)
        except _cz.RefuzCompensare as e:
            conn.rollback()
            raise _refuz(e)
        doc = _cz.document(numar, zi)
        note, total = [], 0
        with conn.cursor() as cur:
            for p in verificate:
                iid, linii = _cz.scrie(cur, schema, zi, doc, p)
                note.append({"inregistrare_id": iid, "factura_emisa": p["emisa"]["document"], "factura_primita": p["primita"]["document"],
                             "suma": str(p["suma"]), "linii": [{"debit": d, "credit": c, "suma": str(v)} for d, c, v in linii]})
                total += p["suma"]
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrari": [n["inregistrare_id"] for n in note], "note": note, "document": doc,
                                          "total": str(total), "partener": verificate[0]["emisa"]["partener"]})
