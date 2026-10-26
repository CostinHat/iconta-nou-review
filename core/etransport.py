# -*- coding: utf-8 -*-
"""e-Transport v2 - generator XML notificare (mfp:anaf:dgti:eTransport:declaratie:v2).
Structura per exemplele oficiale MF (ttn_01_notificare_v2.xml). Upload: manual in SPV (v1).
Tipuri operatiune uzuale: 10=AIC (achizitie intracom.), 20=LIC (livrare intracom.),
30=TTN (transport national). Scop uzual: 101 (comercializare)."""
from xml.sax.saxutils import quoteattr

NS = "mfp:anaf:dgti:eTransport:declaratie:v2"

def _a(n, v):
    if v is None or v == "":
        return ""
    return " %s=%s" % (n, quoteattr(str(v)))

def xml_notificare(cui_declarant, corp):
    """corp:
      ref (optional), cod_tip_operatiune, bunuri:[{cod_scop, cod_tarifar, denumire, cantitate,
      um, greutate_neta, greutate_bruta, valoare_fara_tva}],
      partener:{cod_tara, cod, denumire},
      transport:{nr_vehicul, nr_remorca1?, cod_tara_org, cod_org, denumire_org, data},
      start:{cod_judet, localitate, strada, numar?, cod_postal?, alte_info?},
      final:{...la fel}"""
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    H.append('<eTransport xmlns="%s"%s%s>' % (
        NS, _a("codDeclarant", cui_declarant), _a("refDeclarant", corp.get("ref"))))
    H.append('  <notificare%s>' % _a("codTipOperatiune", corp["cod_tip_operatiune"]))
    for b in corp["bunuri"]:
        H.append('    <bunuriTransportate%s%s%s%s%s%s%s%s/>' % (
            _a("codScopOperatiune", b["cod_scop"]), _a("codTarifar", b["cod_tarifar"]),
            _a("denumireMarfa", b["denumire"]), _a("cantitate", b["cantitate"]),
            _a("codUnitateMasura", b["um"]), _a("greutateNeta", b["greutate_neta"]),
            _a("greutateBruta", b["greutate_bruta"]),
            _a("valoareLeiFaraTva", b["valoare_fara_tva"])))
    p = corp["partener"]
    H.append('    <partenerComercial%s%s%s/>' % (
        _a("codTara", p["cod_tara"]), _a("cod", p.get("cod")), _a("denumire", p["denumire"])))
    t = corp["transport"]
    H.append('    <dateTransport%s%s%s%s%s%s/>' % (
        _a("nrVehicul", t["nr_vehicul"]), _a("nrRemorca1", t.get("nr_remorca1")),
        _a("codTaraOrgTransport", t["cod_tara_org"]), _a("codOrgTransport", t["cod_org"]),
        _a("denumireOrgTransport", t["denumire_org"]), _a("dataTransport", t["data"])))
    def loc(tag, l):
        H.append('    <%s>' % tag)
        H.append('      <locatie%s%s%s%s%s%s/>' % (
            _a("codJudet", l["cod_judet"]), _a("denumireLocalitate", l["localitate"]),
            _a("denumireStrada", l["strada"]), _a("numar", l.get("numar")),
            _a("codPostal", l.get("cod_postal")), _a("alteInfo", l.get("alte_info"))))
        H.append('    </%s>' % tag)
    loc("locStartTraseuRutier", corp["start"])
    loc("locFinalTraseuRutier", corp["final"])
    for d in corp.get("documente", []):
        H.append('    <documenteTransport%s%s%s%s/>' % (
            _a("tipDocument", d["tip"]), _a("numarDocument", d.get("numar")),
            _a("dataDocument", d["data"]), _a("observatii", d.get("observatii"))))
    H.append('  </notificare>')
    H.append('</eTransport>')
    return "\n".join(H)


def campuri_required_lipsa(corp):
    """Campuri OBLIGATORII (schema eTransport) goale/lipsa -> lista {camp, eticheta}. Backendul e POARTA
    autoritara: NU se omite tacit un atribut required (fostul _a returna "" pe gol -> XML invalid generat
    "cu succes", cauza bug-ului 24.07: codTarifar+denumire lipseau din XML lasand campurile goale).
    Etichetele = numele din formular (etransport_ecran.js). Obligativitatea: atribute use="required" din
    SchemaSimtic (nume comune v1/v2) + structura exemplelor oficiale v2. NB: XSD-ul local e v1, STRUCTURAL
    diferit de v2 (atribute/elemente redenumite, enum-uri schimbate) -> validarea XSD completa cere schema v2,
    care lipseste pe sistem (DE_FACUT). Acest guard acopera PREZENTA campurilor required, nu tot XSD-ul."""
    lipsa = []
    def _sir(v, camp, et):
        if v is None or str(v).strip() == "":
            lipsa.append({"camp": camp, "eticheta": et})
    def _poz(v, camp, et):
        try:
            ok = float(v) > 0
        except (TypeError, ValueError):
            ok = False
        if not ok:
            lipsa.append({"camp": camp, "eticheta": et})
    _sir(corp.get("cod_tip_operatiune"), "et-tip", "Tip operațiune")
    bunuri = corp.get("bunuri") or []
    if not bunuri:
        lipsa.append({"camp": "et-bunuri", "eticheta": "Cel puțin un bun transportat"})
    for i, b in enumerate(bunuri):
        n = i + 1
        _sir(b.get("cod_scop"), f"b{i}-cod_scop", f"Bun {n}: Scop")
        _sir(b.get("cod_tarifar"), f"b{i}-cod_tarifar", f"Bun {n}: Cod tarifar (NC)")
        _sir(b.get("denumire"), f"b{i}-denumire", f"Bun {n}: Denumire marfă")
        _sir(b.get("um"), f"b{i}-um", f"Bun {n}: UM")
        _poz(b.get("cantitate"), f"b{i}-cantitate", f"Bun {n}: Cantitate")
        _poz(b.get("greutate_neta"), f"b{i}-greutate_neta", f"Bun {n}: Greutate netă")
        _poz(b.get("greutate_bruta"), f"b{i}-greutate_bruta", f"Bun {n}: Greutate brută")
        _poz(b.get("valoare_fara_tva"), f"b{i}-valoare_fara_tva", f"Bun {n}: Valoare fără TVA")
    p = corp.get("partener") or {}
    _sir(p.get("cod_tara"), "p-cod_tara", "Partener: Cod țară")
    _sir(p.get("denumire"), "p-denumire", "Partener: Denumire")
    t = corp.get("transport") or {}
    _sir(t.get("nr_vehicul"), "t-nr_vehicul", "Transport: Nr. vehicul")
    _sir(t.get("cod_tara_org"), "t-cod_tara_org", "Transport: Țara transportator")
    _sir(t.get("cod_org"), "t-cod_org", "Transport: CUI transportator")
    _sir(t.get("denumire_org"), "t-denumire_org", "Transport: Denumire transportator")
    _sir(t.get("data"), "t-data", "Transport: Data transport")
    for cheie, nume, pre in (("start", "Loc de pornire", "s"), ("final", "Loc de sosire", "f")):
        l = corp.get(cheie) or {}
        _sir(l.get("cod_judet"), f"{pre}-judet", f"{nume}: Județ")
        _sir(l.get("localitate"), f"{pre}-localitate", f"{nume}: Localitate")
        _sir(l.get("strada"), f"{pre}-strada", f"{nume}: Strada")
    return lipsa


# ── [lotul 13, deficiența 534] NOTIFICAREA COMPLETATĂ DIN FACTURĂ SAU DIN NIR ──────────────────────────────────────────────────────────
# „Notificarea se completează de la zero (bunuri, cod NC, cantități, greutăți, valoare, partener, adrese), deși datele sunt pe factură sau
# NIR; locul de pornire nu vine din adresa firmei/gestiunii; «H87» și «RO» precompletate (504). Se completează din factură sau NIR.”
# Ce aduce documentul: bunurile (denumirea, cantitatea, UM-ul în codul UN/ECE — aceeași hartă ca e-Factura, `efactura_send._UM`; o unitate
# necunoscută rămâne GOALĂ, nu „H87” —, valoarea fără TVA în lei), partenerul (țara, codul, denumirea), locul de pornire și cel de sosire
# (adresa firmei din Date firmă, adresa partenerului de pe document / din fișa lui) și tipul operațiunii dedus din direcție și țară
# (vizibil și modificabil pe ecran). Ce NU e pe document rămâne gol, de completat: scopul, codul NC, greutățile, transportul.
# Codurile tipului de operațiune: aceleași ca lista ecranului (10 AIC, 20 LIC, 30 transport național, 40 import, 50 export).

_UE = ("AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "GR", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL",
       "PL", "PT", "SE", "SI", "SK")
#: ce rămâne de completat după aducerea din document (nu e pe factură / NIR)
DE_COMPLETAT = ("scopul fiecărui bun", "codul NC", "greutatea netă și brută", "vehiculul și transportatorul", "data transportului")


def tip_operatiune(intrare, tara):
    """Tipul operațiunii e-Transport dedus din direcție (`intrare` = marfa vine la firmă) și țara partenerului: RO -> 30; UE -> 10 / 20;
    din afara UE -> 40 / 50."""
    t = str(tara or "RO").strip().upper() or "RO"
    if t == "RO":
        return "30"
    if t in _UE:
        return "10" if intrare else "20"
    return "40" if intrare else "50"


def _tara_din_cod(cod, implicit="RO"):
    c = str(cod or "").strip().upper()
    return c[:2] if c[:2].isalpha() else implicit


def _loc(adresa, oras, judet):
    from core import efactura_send as _es
    jc = _es._jud(judet)
    return {"cod_judet": jc[3:] if jc else "", "localitate": str(oras or "").strip(), "strada": str(adresa or "").strip()}


def _um_unece(um):
    from core import efactura_send as _es
    return _es._UM.get(_es._norm(um)) or ""


def _bani(x):
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def din_document(conn, schema, fel, doc_id):
    """Propunerea notificării din factura `doc_id` (fel „factura”) sau din NIR-ul `doc_id` (fel „nir”): {cod_tip_operatiune, ref,
    bunuri, partener, start, final, de_completat}; None dacă documentul nu există."""
    from decimal import Decimal
    from psycopg2.extras import RealDictCursor
    from core import eticheta_nota as _et
    s = '"%s".' % str(schema).strip('"')
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT nume, adresa, oras, judet FROM %sfirma_profil WHERE id = 1" % s)
        firma = cur.fetchone() or {}
        loc_firma = _loc(firma.get("adresa"), firma.get("oras"), firma.get("judet"))
        if fel == "factura":
            cur.execute("SELECT id, directie, tert_nume, tert_cui, tert_tara, tert_adresa, tert_oras, tert_judet, curs_bnr, moneda "
                        "FROM %sfacturi WHERE id = %%s" % s, (doc_id,))
            f = cur.fetchone()
            if not f:
                return None
            cur.execute("SELECT descriere, cantitate, um, pret_unitar, valoare_neta FROM %sfactura_linii WHERE factura_id = %%s ORDER BY id"
                        % s, (doc_id,))
            curs = Decimal(str(f["curs_bnr"] or 1))
            bunuri = [{"denumire": l["descriere"] or "", "cantitate": str(l["cantitate"]), "um": _um_unece(l["um"]),
                       "valoare_fara_tva": _bani((Decimal(str(l["valoare_neta"])) if l["valoare_neta"] is not None
                                                  else Decimal(str(l["cantitate"] or 0)) * Decimal(str(l["pret_unitar"] or 0))) * curs)}
                      for l in cur.fetchall()]
            tara = str(f["tert_tara"] or "").strip().upper() or _tara_din_cod(f["tert_cui"])
            intrare = f["directie"] == "primita"
            partener = {"cod_tara": tara, "cod": str(f["tert_cui"] or "").strip(), "denumire": f["tert_nume"] or ""}
            loc_partener = _loc(f["tert_adresa"], f["tert_oras"], f["tert_judet"]) if tara == "RO" else \
                {"cod_judet": "", "localitate": str(f["tert_oras"] or "").strip(), "strada": str(f["tert_adresa"] or "").strip()}
            ref = _et.factura(cur, schema, doc_id)
        elif fel == "nir":
            cur.execute("SELECT id, numar, data, furnizor, cui FROM %snir WHERE id = %%s" % s, (doc_id,))
            n = cur.fetchone()
            if not n:
                return None
            cur.execute("SELECT l.denumire, l.cantitate, l.pret_achizitie, a.um FROM %snir_linii l LEFT JOIN %sarticole a ON a.id = l.articol_id "
                        "WHERE l.nir_id = %%s ORDER BY l.id" % (s, s), (doc_id,))
            bunuri = [{"denumire": l["denumire"] or "", "cantitate": str(l["cantitate"]), "um": _um_unece(l["um"]),
                       "valoare_fara_tva": _bani(Decimal(str(l["cantitate"] or 0)) * Decimal(str(l["pret_achizitie"] or 0)))}
                      for l in cur.fetchall()]
            tara = _tara_din_cod(n["cui"])
            intrare = True
            partener = {"cod_tara": tara, "cod": str(n["cui"] or "").strip(), "denumire": n["furnizor"] or ""}
            from core import cui_forma as _cf
            cur.execute("SELECT adresa, oras, judet FROM %sfurnizori WHERE %s = %%s ORDER BY id LIMIT 1" % (s, _cf.SQL.format(c="cui")),
                        (_cf.stocare(n["cui"]) or "",))
            fz = cur.fetchone() or {}
            loc_partener = _loc(fz.get("adresa"), fz.get("oras"), fz.get("judet"))
            from core.pdf_util import data_ro
            ref = "NIR %s din %s" % (n["numar"], data_ro(n["data"]))
        else:
            raise ValueError("Documentul din care se completează notificarea e o factură sau un NIR.")
    return {"cod_tip_operatiune": tip_operatiune(intrare, tara), "ref": ref[:100], "bunuri": bunuri, "partener": partener,
            "start": loc_partener if intrare else loc_firma, "final": loc_firma if intrare else loc_partener,
            "de_completat": list(DE_COMPLETAT)}


def documente_recente(conn, schema, zile=60):
    """Documentele din care se poate completa notificarea: facturile (emise și primite, nu proforme) și NIR-urile din ultimele `zile`
    zile, cele mai noi întâi — {facturi: [{id, eticheta, partener}], nir: [{id, eticheta, partener}]}."""
    from psycopg2.extras import RealDictCursor
    from core import eticheta_nota as _et
    from core.pdf_util import data_ro
    s = '"%s".' % str(schema).strip('"')
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, directie, tip, serie, numar, data_emitere, tert_nume FROM %sfacturi WHERE COALESCE(tip, 'factura') = 'factura' "
                    "AND storno_din_id IS NULL AND COALESCE(status, '') NOT IN ('anulata', 'ciorna') "
                    "AND data_emitere >= CURRENT_DATE - %%s ORDER BY data_emitere DESC, id DESC LIMIT 200" % s, (zile,))
        facturi = [{"id": r["id"], "eticheta": _et.factura_din_rand(r), "partener": r["tert_nume"] or "",
                    "directie": r["directie"]} for r in cur.fetchall()]
        cur.execute("SELECT id, numar, data, furnizor FROM %snir WHERE data >= CURRENT_DATE - %%s ORDER BY data DESC, id DESC LIMIT 200" % s,
                    (zile,))
        nir = [{"id": r["id"], "eticheta": "NIR %s din %s" % (r["numar"], data_ro(r["data"])), "partener": r["furnizor"] or ""}
               for r in cur.fetchall()]
    return {"facturi": facturi, "nir": nir}


def din_document_uc(tenant_id, fel, doc_id, ctx):
    """Corpul rutei `GET /tenants/{tenant_id}/etransport/din-document` (fără `fel`: lista documentelor din care se poate completa)."""
    from core import db, erori as _erori, uc_comun as _uc
    schema = _uc._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        if not fel:
            return documente_recente(conn, schema)
        try:
            r = din_document(conn, schema, fel, int(doc_id or 0))
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    if r is None:
        raise _erori.Inexistent("Documentul nu mai există.")
    return r
