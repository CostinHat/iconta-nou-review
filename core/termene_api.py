"""
core/termene_api.py — scadente fiscale VIITOARE pe portofoliu (orizont 60 zile).

Pentru fiecare firma deriva declaratiile datorate (refoloseste scadentarul din control_fiscal_api),
pastreaza doar cele cu termen in [azi, azi+60], nedepuse, si le grupeaza pe (data_termen, tip)
cu numarul de firme. Perspectiva = privire inainte (vs control_fiscal = privire inapoi).
"""
from __future__ import annotations
import datetime
from core import control_fiscal_api as cf
from core.common import azi_ro  # [fus] fereastra [azi, azi+60] = VERDICT (ce vede contabilul), zi RO

ORIZONT_ZILE = 60


def termene_firma(vector, are_salariati, depuse, azi=None, *, d390_fapt=None):
    """
    Declaratiile datorate VIITOARE (termen in [azi, azi+ORIZONT_ZILE]), nedepuse.

    Refoloseste MOTORUL UNIC control_fiscal_api.obligatii_datorate (aceeasi mapare 'cine ce datoreaza'
    ca semaforul), cu fereastra parametrizata: jos=azi (doar viitor), sus=60z. NU reimplementeaza
    maparea local (drift-ul vechi fabrica D100 pe PFA; vezi DECIZII 23.07). Consecinte automate:
      - marginirea B1, D394/D406/D101, D100 micro etc. vin din motor (termene nu mai sub-raporteaza);
      - D390 la neplatitor cu IC intra in `neclar` (gri art.317), NU in `datorate` -> nu apare ca scadenta
        ferma. Termene NU reafiseaza gri-ul (privire inainte; "nu pot verifica" e treaba semaforului).
    depuse = set de (tip, an, luna) (tip lowercase, ca 'datorate').
    vector trebuie sa poarte partida_simpla (derivat de caller din tip_firma, ca la semafor).
    d390_fapt = callback D390 pe fapt lunar (caller-ul are conn_schema): luna deschisa (None) -> AFISAM
        (privire inainte; nu putem exclude operatiuni pana la finalul lunii); luna inchisa fara IC -> nu apare.
    """
    azi = azi or azi_ro()   # [fus] fereastra termenelor decide ce apare -> zi RO, robust la OS TZ
    rez = cf.obligatii_datorate(vector, are_salariati, azi, jos=azi, sus_zile=ORIZONT_ZILE, d390_fapt=d390_fapt)
    return [d for d in rez["datorate"] if (d["tip"], d["an"], d["luna"]) not in depuse]


def portofoliu(firme_eval, azi=None, neevaluate=None):
    """
    firme_eval = lista de {tenant_id, nume, termene:[...]} (termene = output termene_firma).
    neevaluate = lista de {tenant_id, nume, cauza} - firme care NU au putut fi evaluate; NU se ascund
      (gri cu temei, aceeasi doctrina ca semaforul, DECIZII 23.07: gri = "nu am putut", nu tacere).
    Intoarce {grupuri:[{termen, items:[{tip, nr_firme, firme:[...]}]}], urmatoarea, neevaluate}.
    Grupat pe data termen, apoi pe tip, cu numarul si lista de firme.
    """
    azi = azi or azi_ro()   # [fus] fereastra termenelor decide ce apare -> zi RO, robust la OS TZ
    # acumulator: termen -> tip -> {an, incert, firme}. (an+incert sunt determinate de PERIOADA, deci egale
    # pentru toate firmele dintr-un grup (termen,tip) - un termen+tip = o singura perioada.)
    acc = {}
    for fe in firme_eval:
        for t in fe["termene"]:
            g = acc.setdefault(t["termen"], {}).setdefault(
                t["tip"], {"an": t["an"], "incert": bool(t.get("incert")), "firme": []})
            g["firme"].append({"tenant_id": fe["tenant_id"], "nume": fe["nume"],
                               "cui": fe.get("cui"), "tip_firma": fe.get("tip_firma"),   # [P2] deschideFirma cere {id,nume,cui,tip_firma}
                               "perioada": t["perioada"]})

    grupuri = []
    for termen in sorted(acc.keys()):
        items = []
        for tip in sorted(acc[termen].keys()):
            g = acc[termen][tip]
            items.append({"tip": tip, "nr_firme": len(g["firme"]), "an": g["an"],   # [P1c] an perioada
                          "incert": g["incert"], "firme": g["firme"]})               # [P4] perioada deschisa
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
