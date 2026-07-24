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
