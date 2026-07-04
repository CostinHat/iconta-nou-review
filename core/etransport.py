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
