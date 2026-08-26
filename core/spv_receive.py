# -*- coding: utf-8 -*-
"""
core/spv_receive.py — cron RECEIVE e-Factura (F179): facturi de la furnizori din SPV.

Jumatatea de PRIMIRE a F126. Ruleaza pe timer (spv-receive.timer), listeaza mesajele filtru=P
(FACTURA PRIMITA) per tenant, descarca facturile NOI, le insereaza CIORNA in efactura_primite.
FOUR-EYES: NU creeaza cheltuiala automat - contabilul valideaza (pasul 5), abia atunci factura_id.

GARDURI (nenegociabile):
- Reutilizeaza efactura_send.lista_mesaje/descarca (apel_anaf pe PRINCIPAL, fara client paralel).
- DEDUP pe id_mesaj_anaf: pre-check + INSERT ... ON CONFLICT DO NOTHING (fereastra 2-3z suprapusa la
  30 min -> aceeasi factura la mai multe rulari). Nu re-descarca ce e deja importat.
- cif_beneficiar VALIDAT la insert (== CIF tenant), nu doar stocat. Pe token de cabinet care acopera
  N CIF-uri, factura se leaga de tenantul al carui CIF = cif_beneficiar. Mismatch -> SKIP + log
  anti-scurgere intre chiriasi (la nivel de insert, nu de afisare).
- Token expirat/mort -> apel_anaf face refresh; EroareSpv -> SKIP tenant/mesaj (auth-fail != eroare).
- MASINA DE STARI: descarcata (fallback neparsabil) / ciorna (parsata, prezentata) -> validata/respinsa
  DOAR prin four-eyes (om). factura_id NULL pana la validare.
"""
import os
import sys
import hashlib

from core import db
from core import spv_conector
from core import efactura_send as efs
from core import efactura_import as efi

MEDIU = os.environ.get("EFACTURA_MEDIU", "prod")
ZILE = int(os.environ.get("SPV_RECEIVE_ZILE", "3"))            # fereastra suprapusa, < 60 oficial
INTERVAL_SEC = float(os.environ.get("SPV_RECEIVE_INTERVAL_SEC", "1.0"))


def _digits(x):
    return "".join(c for c in str(x or "") if c.isdigit())


def _deja_importat(schema, id_mesaj):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM {schema}.efactura_primite WHERE id_mesaj_anaf=%s", (id_mesaj,))
            return cur.fetchone() is not None


def importa_mesaj(schema, principal, cif_tenant, msg, stat):
    """Un mesaj listaMesajeFactura -> rand efactura_primite (ciorna/descarcata). Idempotent + anti-scurgere."""
    id_mesaj = str(msg.get("id") or "")
    cif_ben = _digits(msg.get("cif_beneficiar"))
    # GARD anti-scurgere: importa DOAR daca beneficiarul e chiar tenantul
    if not cif_ben or cif_ben != _digits(cif_tenant):
        stat["scurgere_evitata"] += 1
        print("  ANTI-SCURGERE %s: mesaj %s cif_beneficiar=%s != cif tenant %s - NU import"
              % (schema, id_mesaj, cif_ben, _digits(cif_tenant)), file=sys.stderr)
        return
    if _deja_importat(schema, id_mesaj):     # dedup: nu re-descarca
        stat["deja"] += 1
        return
    try:
        r = efs.descarca(principal, id_mesaj, MEDIU)
    except spv_conector.EroareSpv as e:
        stat["skip_auth"] += 1
        print("  SKIP auth descarca %s/%s: %s" % (schema, id_mesaj, e), file=sys.stderr)
        return
    if getattr(r, "status_code", None) != 200 or not getattr(r, "content", None):
        stat["descarca_esec"] += 1
        return
    xml = None
    try:
        for _nume, xmlb in efi.extrage_fisiere("f.zip", r.content):
            xml = xmlb
            break
    except Exception:
        xml = None
    if not xml:
        stat["fara_xml"] += 1
        return
    xml_txt = xml.decode("utf-8", "replace") if isinstance(xml, (bytes, bytearray)) else xml
    sha = hashlib.sha256(xml_txt.encode("utf-8")).hexdigest()
    status = "descarcata"
    try:
        efi.parseaza_xml(xml, cif_tenant)    # doar valideaza parsabilitatea -> ciorna
        status = "ciorna"
    except Exception:
        status = "descarcata"                # fallback: descarcata, neparsabila (om o vede oricum)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.efactura_primite
                (id_mesaj_anaf, id_solicitare, cif_emitent, cif_beneficiar, tip,
                 xml_brut, xml_sha256, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id_mesaj_anaf) DO NOTHING""",
                (id_mesaj, msg.get("id_solicitare"), _digits(msg.get("cif_emitent")), cif_ben,
                 msg.get("tip"), xml_txt, sha, status))
    stat[status] += 1


def ruleaza(_dormi=None):
    import time
    _dormi = _dormi or time.sleep
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    stat = {"ciorna": 0, "descarcata": 0, "deja": 0, "scurgere_evitata": 0,
            "skip_auth": 0, "descarca_esec": 0, "fara_xml": 0, "tenanti_fara_cif": 0}
    for schema in scheme:
        with db.get_conn() as conn:
            principal = efs.principal_pentru_schema(conn, schema)
            with conn.cursor() as cur:
                cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
                row = cur.fetchone()
        cif = _digits(row[0]) if row and row[0] else ""
        if not cif:
            stat["tenanti_fara_cif"] += 1
            continue
        try:
            mesaje, eroare = efs.lista_mesaje(principal, cif, MEDIU, zile=ZILE, filtru="P")
        except spv_conector.EroareSpv as e:
            stat["skip_auth"] += 1
            print("  SKIP auth lista %s: %s" % (schema, e), file=sys.stderr)
            continue
        if eroare:
            print("  %s: lista fara mesaje/eroare: %s" % (schema, eroare))
            continue
        for msg in mesaje:
            try:
                importa_mesaj(schema, principal, cif, msg, stat)
            except Exception as e:
                print("  EROARE import %s/%s: %s" % (schema, msg.get("id"), e), file=sys.stderr)
            _dormi(INTERVAL_SEC)
    from datetime import datetime, timezone
    print("%s spv_receive terminat: %s" % (datetime.now(timezone.utc).isoformat(), stat))
    return stat


if __name__ == "__main__":
    from core import cron  # [R74] alerta la esec + bataie la reusita
    cron.ruleaza("spv_receive", ruleaza)
