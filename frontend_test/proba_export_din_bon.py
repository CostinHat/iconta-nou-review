# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — punctul 3 (decizia Costin 03.10.2026): factura emisă pe baza bonului fiscal în exportul SAGA /
WinMentor și în D406. Cod vechi vs nou.

    python frontend_test/proba_export_din_bon.py <radacina_cod>
F1 (tenant_049) din baza de producție, octombrie 2026, într-o tranzacție ANULATĂ (`observare.alerteaza` neutralizat):
o factură obișnuită, o factură emisă pe baza bonului fiscal (0042 din 02.10) și stornarea facturii obișnuite.
  · cod VECHI: factura din bon iese în SAGA ca factură obișnuită (fără FacturaTip), în WinMentor cu ClasificareSAFT=380
    (fără InfoCM), storno-ul tot 380; în D406 cu TaxCode-ul cotei — programul extern / ANAF o văd ca vânzare nouă, peste
    raportul Z;
  · cod NOU: SAGA `<FacturaTip>f</FacturaTip>`; WinMentor CasaDeMarcat=D + NumarBonuri=1 + ClasificareSAFT=751, storno
    381; D406 TaxCode 310327 (în TaxTable), DUK valid. Nicio factură pierdută: toate trei sunt în ambele exporturi.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare, facturi_api, export_saga, export_winmentor, d406, duk  # noqa: E402
from core import efactura_send, efactura_trimitere  # noqa: E402

observare.alerteaza = lambda *a, **k: None
NOU = hasattr(export_winmentor, "clasificare")
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))
S = "tenant_049"
AN, LUNA = 2026, 10
LINIE = {"descriere": "Meniu zilei", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "um": "buc", "cont_venit": "707"}

db.init_pool()
with db.get_conn() as conn:
    cur = conn.cursor()
    try:
        cur.execute("SET search_path TO %s, public" % S)
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil' "
                    "AND column_name IN ('forma_juridica','capital_subscris')", (S,))
        if len(cur.fetchall()) == 2:   # lotul 19, decizia 12: societatea fără capital nu emite
            cur.execute("UPDATE firma_profil SET forma_juridica='SRL', capital_subscris=200 WHERE id=1")
        # CIUS-RO (BR-RO-100/110): în București localitatea e sectorul — F1 n-are sectorul în profil (tranzacție anulată)
        cur.execute("UPDATE firma_profil SET oras='Sector 1' WHERE id=1 AND upper(coalesce(judet,'')) IN ('B','BUCURESTI')")
        ids = {}
        r = facturi_api.creeaza_factura(conn, "PROBA-NORM-1", "2026-10-02", "emisa", [dict(LINIE)],
                                        tert_nume="CLIENT SRL", tert_cui="RO14399840", status="emisa",
                                        data_scadenta="2026-10-17")
        ids["obisnuita"] = r["factura_id"]
        r = facturi_api.creeaza_factura(conn, "PROBA-BON-1", "2026-10-02", "emisa", [dict(LINIE)],
                                        tert_nume="CLIENT SRL", tert_cui="RO14399840", status="emisa",
                                        data_scadenta="2026-10-17",
                                        bon_fiscal_nr="0042", bon_fiscal_data="2026-10-02")
        ids["din bon"] = r["factura_id"]
        # CIUS-RO BR-RO-110/111: cumpărătorul RO cere județ + localitate (creeaza_factura nu le primește ca parametri)
        cur.execute("UPDATE facturi SET tert_adresa='Str. Test 1', tert_oras='Sector 1', tert_judet='B' WHERE id = ANY(%s)",
                    (list(ids.values()),))
        r = facturi_api.storneaza(conn, ids["obisnuita"])
        ids["storno"] = r.get("factura_id") or r.get("id")
        from core import repo_notificari_scadenta as _rns
        cur.execute("SELECT platita_la FROM facturi WHERE id=%s", (ids["din bon"],))
        _pl = cur.fetchone()[0]
        _de_notificat = [x[0] for x in _rns.select_facturi(cur, "2026-12-31")]
        print("  factura din bon: platita_la=%s · în lista notificărilor de scadență către client: %s"
              % (_pl, ids["din bon"] in _de_notificat))
        luna_ids = export_saga.facturi_emise_luna(conn, S, AN, LUNA)
        print("  facturile probei: %s · exportul lunii le conține pe toate: %s (%d facturi emise în luna)"
              % (ids, all(i in luna_ids for i in ids.values()), len(luna_ids)))
        # SAGA — un XML per factură
        for et, fid in ids.items():
            firma, fact, linii = export_saga.date_factura(conn, S, fid)
            x = export_saga.xml_factura(firma, fact, linii)
            tip = re.search(r"<FacturaTip>(.*?)</FacturaTip>", x)
            print("  SAGA %-9s %s: FacturaTip=%s" % (et, fact["numar"], repr(tip.group(1)) if tip else "absent (factură obișnuită)"))
        # WinMentor — Facturi.txt
        fis = export_winmentor.export_luna(conn, S, AN, LUNA)
        txt = fis["Facturi.txt"].decode("cp1250")
        for bloc in re.split(r"\n(?=\[Factura_\d+\])", txt):
            m = re.search(r"NrDoc=(PROBA-[A-Z]+-1|[^\n]*)", bloc)
            if m and any(n in bloc for n in ("PROBA-NORM-1", "PROBA-BON-1")) or ("StornoAvans" not in bloc and "PROBA" in bloc):
                pass
        for fid in ids.values():
            cur.execute("SELECT numar FROM facturi WHERE id=%s", (fid,))
            nr = cur.fetchone()[0]
            m = re.search(r"\[Factura_\d+\]\nNrDoc=%s\n(.*?)(?=\n\[Items_)" % re.escape(nr), txt, re.S)
            campuri = dict(l.split("=", 1) for l in (m.group(1).split("\n") if m else []) if "=" in l)
            print("  WinMentor %-14s ClasificareSAFT=%s CasaDeMarcat=%s NumarBonuri=%s" % (
                nr, campuri.get("ClasificareSAFT"), campuri.get("CasaDeMarcat", "-"), campuri.get("NumarBonuri", "-")))
        # e-Factura (UBL) — validatorul oficial ANAF FACT1 (public, fără token)
        for et in ("obisnuita", "din bon"):
            try:
                ubl, _f = efactura_trimitere.genereaza_din_factura(conn, S, ids[et])
                tip = re.search(r"<cbc:InvoiceTypeCode>(.*?)</cbc:InvoiceTypeCode>", ubl).group(1)
                nota = re.search(r"<cbc:Note>(.*?)</cbc:Note>", ubl)
                ok, mesaje = efactura_send.valideaza(ubl)
                print("  e-Factura %-9s InvoiceTypeCode=%s Note=%s · FACT1: %s %s" % (
                    et, tip, repr(nota.group(1)) if nota else "-", "ok" if ok else "NEVALID", "; ".join(mesaje)[:200]))
            except Exception as e:
                print("  e-Factura %s REFUZ: %s" % (et, str(e)[:200]))
        # D406
        try:
            xml, res = d406.genereaza(conn, S, AN, LUNA)
            rad = ET.fromstring(xml.split("?>", 1)[1] if xml.startswith("<?xml") else xml)
            ns = rad.tag.split("}")[0] + "}"
            for inv in rad.iter(ns + "Invoice"):
                nr = inv.findtext(ns + "InvoiceNo")
                if nr and nr.startswith("PROBA") or (nr and "STORNO" in nr.upper()):
                    coduri = sorted({e.text for e in inv.iter(ns + "TaxCode")})
                    print("  D406 %-14s InvoiceType=%s TaxCode=%s" % (nr, inv.findtext(ns + "InvoiceType"), coduri))
            tt = sorted({e.findtext(ns + "TaxCode") for e in rad.iter(ns + "TaxCodeDetails")})
            print("  D406 TaxTable: %s" % tt)
            v = duk.valideaza(xml, "d406", an=AN, luna=LUNA, timeout=300)
            print("  DUK D406: %s%s" % (v["stare"], (" — " + (v.get("erori") or "").replace("\n", " ")[:300]) if v.get("erori") else ""))
        except Exception as e:
            print("  D406 REFUZ: %s" % str(e)[:400])
    finally:
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
