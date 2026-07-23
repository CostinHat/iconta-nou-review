"""
core/termene_api.py — scadente fiscale VIITOARE pe portofoliu (orizont 60 zile).

Pentru fiecare firma deriva declaratiile datorate (refoloseste scadentarul din control_fiscal_api),
pastreaza doar cele cu termen in [azi, azi+60], nedepuse, si le grupeaza pe (data_termen, tip)
cu numarul de firme. Perspectiva = privire inainte (vs control_fiscal = privire inapoi).
"""
from __future__ import annotations
import datetime
from core import control_fiscal_api as cf
from core.migrare_api import regim_efectiv  # [regim] primitiva UNICA (partida simpla => None), langa STRATURI_META
from core.common import azi_ro  # [fus] fereastra [azi, azi+60] = VERDICT (ce vede contabilul), zi RO

ORIZONT_ZILE = 60


def termene_firma(vector, are_salariati, depuse, azi=None):
    """
    Intoarce lista declaratiilor datorate VIITOARE (termen in [azi, azi+orizont]), nedepuse.
    depuse = set de (tip, an, luna).
    """
    azi = azi or azi_ro()   # [fus] fereastra termenelor decide ce apare -> zi RO, robust la OS TZ
    limita = azi + datetime.timedelta(days=ORIZONT_ZILE)
    # luam toate datorate (control_fiscal include fereastra de urmarire);
    # pentru termene ne extindem pe orizontul mare evaluand direct scadentarul
    out = []
    # reconstruim datorate pe orizontul mare: cf.declaratii_datorate foloseste fereastra de 7 zile,
    # deci o reimplementam aici cu limita extinsa prin acelasi mecanism _termen.
    platitor_tva = bool(vector.get("platitor_tva"))
    decont = (vector.get("tip_decont") or "").lower()   # fara default tacit; "" (necompletat) -> nu ghicim periodicitatea
    # [regim] regimul CIT EFECTIV: partida simpla (pfa) => None => nu emite D100/D101. Callerul da
    # vector cu tip_firma + regim_fiscal (contract strict al regim_efectiv). Vezi DECIZII 23.07.
    regim = regim_efectiv(vector)
    ic = bool(vector.get("operatiuni_ic"))
    luni = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"]
    an = azi.year

    def adauga(tip, a, luna_p, perioada):
        tip = tip.lower()   # [tip_lowercase] cheie de join canonic; upper la randare (UI/termene.js)
        term = cf._termen(a, luna_p)
        if azi <= term <= limita and (tip, a, luna_p) not in depuse:
            out.append({"tip": tip, "an": a, "luna": luna_p,
                        "termen": term.isoformat(), "perioada": perioada})

    if platitor_tva:
        if decont == "trimestrial":
            for tri, lf in enumerate([3, 6, 9, 12], start=1):
                adauga("D300", an, lf, f"T{tri}")
        elif decont == "lunar":
            for luna in range(1, 13):
                adauga("D300", an, luna, luni[luna])
        # decont necompletat (vector incomplet) -> NU emitem termene D300; periodicitatea e necunoscuta,
        # nu se ghiceste (semaforul o marcheaza deja gri). Vezi DECIZII 23.07.
    if are_salariati:
        for luna in range(1, 13):
            adauga("D112", an, luna, luni[luna])
    if regim == "micro":
        for tri, lf in enumerate([3, 6, 9, 12], start=1):
            adauga("D100", an, lf, f"T{tri}")
    if ic:
        for luna in range(1, 13):
            adauga("D390", an, luna, luni[luna])
    return out


def portofoliu(firme_eval, azi=None, neevaluate=None):
    """
    firme_eval = lista de {tenant_id, nume, termene:[...]} (termene = output termene_firma).
    neevaluate = lista de {tenant_id, nume, cauza} - firme care NU au putut fi evaluate; NU se ascund
      (gri cu temei, aceeasi doctrina ca semaforul, DECIZII 23.07: gri = "nu am putut", nu tacere).
    Intoarce {grupuri:[{termen, items:[{tip, nr_firme, firme:[...]}]}], urmatoarea, neevaluate}.
    Grupat pe data termen, apoi pe tip, cu numarul si lista de firme.
    """
    azi = azi or azi_ro()   # [fus] fereastra termenelor decide ce apare -> zi RO, robust la OS TZ
    # acumulator: termen -> tip -> lista firme
    acc = {}
    for fe in firme_eval:
        for t in fe["termene"]:
            acc.setdefault(t["termen"], {}).setdefault(t["tip"], []).append(
                {"tenant_id": fe["tenant_id"], "nume": fe["nume"], "perioada": t["perioada"]})

    grupuri = []
    for termen in sorted(acc.keys()):
        items = []
        for tip in sorted(acc[termen].keys()):
            firme = acc[termen][tip]
            items.append({"tip": tip, "nr_firme": len(firme), "firme": firme})
        zile = (datetime.date.fromisoformat(termen) - azi).days
        grupuri.append({"termen": termen, "zile": zile, "items": items})

    # urmatoarea scadenta (prima din lista) pentru cardul de pe dashboard
    urmatoarea = None
    if grupuri:
        g = grupuri[0]
        # tipul cu cele mai multe firme la primul termen
        top = max(g["items"], key=lambda x: x["nr_firme"])
        urmatoarea = {"termen": g["termen"], "zile": g["zile"],
                      "tip": top["tip"], "nr_firme": top["nr_firme"]}

    return {"grupuri": grupuri, "urmatoarea": urmatoarea, "neevaluate": neevaluate or []}
