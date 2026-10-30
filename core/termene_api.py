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


def termene_firma(vector, are_salariati, depuse, azi=None, *, d390_fapt=None, d112_fapt=None, d390_luni_neplatitor=None,
                  declaratii_fapt=None, restante=False):
    """
    Declaratiile datorate VIITOARE (termen in [azi, azi+ORIZONT_ZILE]), nedepuse.

    Refoloseste MOTORUL UNIC control_fiscal_api.obligatii_datorate (aceeasi mapare 'cine ce datoreaza'
    ca semaforul), cu fereastra parametrizata: jos=azi (doar viitor), sus=60z. NU reimplementeaza
    maparea local (drift-ul vechi fabrica D100 pe PFA; vezi DECIZII 23.07). Consecinte automate:
      - marginirea B1, D394/D406/D101, D100 micro etc. vin din motor (termene nu mai sub-raporteaza);
      - D390 la neplatitor cu IC intra in `neclar` (gri art.317), NU in `datorate` -> nu apare ca scadenta
        ferma. Termene NU reafiseaza gri-ul (privire inainte; "nu pot verifica" e treaba semaforului).
    restante = [719, comanda 14.3] True: și declarațiile cu termenul TRECUT și nedepuse (a doua trecere, fără limită jos, din care se iau numai cele cu termenul trecut), fiecare marcată `restanta: True`;
        „O declarație datorată și nedepusă după termen trebuie să apară ca restanță, prima, nu să dispară” — aceleași obligații ca la semafor
        pe același motor. Implicit False (privire înainte, 60 de zile): o listă care nu cere restanțele rămâne cum era.
    depuse = set de (tip, an, luna) (tip lowercase, ca 'datorate').
    vector trebuie sa poarte partida_simpla (derivat de caller din tip_firma, ca la semafor).
    d112_fapt = callback D112 pe fapt lunar (salariat activ în lună, ca semaforul); None = boolean-ul `are_salariati` pe toate lunile.
    d390_fapt = callback D390 pe fapt lunar (caller-ul are conn_schema): luna deschisa (None) -> AFISAM
        (privire inainte; nu putem exclude operatiuni pana la finalul lunii); luna inchisa fara IC -> nu apare.
    d390_luni_neplatitor = [lotul 12, C162] callback an -> lunile in care NEplatitorul inregistrat art.317 datoreaza D390
        (`control_incrucisat.d390_luni_neplatitor`, ACEEASI sursa ca Control fiscal, `control_fiscal_api.evalueaza_firma`). Fara el,
        motorul punea D390 pe TOATE lunile neplatitorului art.317 cu operatiuni IC bifate — „Termene” si selectorul Declaratii aratau
        D390 si pe lunile fara nicio operatiune intracomunitara. TEMEI: CF art.325 alin.(2) — „Declarația se întocmește pentru fiecare
        lună calendaristică în care ia naștere exigibilitatea taxei pentru operațiunile prevăzute la alin. (1)”.
    declaratii_fapt = [lotul 13, deficiențele 538 / 591] callback (jos, sus_zile) -> rezultatul lui
        `control_fiscal_api.declaratii_fapt` pe aceeași fereastră: declarațiile datorate din OPERAȚIILE înregistrate, nu din vector — D301
        (neplătitorul cu achiziții intracomunitare, CF art.324 alin.(1): „până la data de 25 inclusiv a lunii următoare celei în care ia
        naștere exigibilitatea”) și D205 (dividendele). Până la 538 lista „Datorate de firmă” și Termene erau numai din vector: la F3
        (neplătitoare art.317, achiziția IE-100 validată pe 09/2026) D301 09/2026 lipsea, deci termenul de 26.10.2026 nu apărea nicăieri.
        Același calcul ca Control fiscal (semaforul), deci aceleași obligații pe toate ecranele; None (teste, matrice) -> numai vectorul.
    """
    azi = azi or azi_ro()   # [fus] fereastra termenelor decide ce apare -> zi RO, robust la OS TZ
    # [deficiența 300, 17.10.2026] D112 din FAPT (salariat activ în lună), ca semaforul — nu din „are salariați” azi aplicat oricărei luni
    def _datorate(limita, fapt_admis):
        rez = cf.obligatii_datorate(vector, are_salariati, azi, jos=limita, sus_zile=ORIZONT_ZILE, d390_fapt=d390_fapt, d112_fapt=d112_fapt,
                                    d390_luni_neplatitor=d390_luni_neplatitor)
        out = list(rez["datorate"])
        if declaratii_fapt is not None:   # [lotul 13, 538 / 591] D301 / D205 din operațiile înregistrate, pe aceeași fereastră
            vazute = {(d["tip"], d["an"], d["luna"]) for d in out}
            out += [d for d in (declaratii_fapt(limita, ORIZONT_ZILE) or {}).get("datorate", [])
                    if (d["tip"], d["an"], d["luna"]) not in vazute and fapt_admis(d)]
        return out
    datorate = _datorate(azi, lambda d: azi.isoformat() <= d["termen"])
    if restante:
        # [719] restanțele vin dintr-o a doua trecere pe același motor, FĂRĂ limită jos: din ea se iau numai cele cu termenul trecut. Privirea înainte
        # rămâne cea de până acum (luna deschisă cu operațiuni intracomunitare declarate = „posibilă”, nu gri ca la semafor)
        vazute = {(d["tip"], d["an"], d["luna"]) for d in datorate}
        datorate += [d for d in _datorate(None, lambda d: True)
                     if str(d["termen"])[:10] < azi.isoformat() and (d["tip"], d["an"], d["luna"]) not in vazute]
    out = [d for d in datorate if (d["tip"], d["an"], d["luna"]) not in depuse]
    if restante:   # [719] termenul trecut + nedepusă = restanță; restanțele primele, apoi după termen
        out = [dict(d, restanta=str(d["termen"])[:10] < azi.isoformat()) for d in out]
        out.sort(key=lambda d: (str(d["termen"])[:10], d["tip"]))
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
    # acumulator: termen -> tip -> {an, incert, firme}. (an+incert sunt determinate de PERIOADA, deci egale
    # pentru toate firmele dintr-un grup (termen,tip) - un termen+tip = o singura perioada.)
    acc = {}
    for fe in firme_eval:
        for t in fe["termene"]:
            g = acc.setdefault(t["termen"], {}).setdefault(
                t["tip"], {"an": t["an"], "incert": bool(t.get("incert")), "firme": []})
            g["firme"].append({"tenant_id": fe["tenant_id"], "nume": fe["nume"],
                               "cui": fe.get("cui"), "tip_firma": fe.get("tip_firma"),   # [P2] deschideFirma cere {id,nume,cui,tip_firma}
                               "regim_contabil": fe.get("regim_contabil"),               # [regim_card] contract strict meniuFirma
                               "perioada": t["perioada"],
                               # [lotul 10, deficiența 432] perioada dinaintea preluării, marcată (regula de la 157)
                               "inainte_de_preluare": bool(t.get("inainte_de_preluare"))})

    grupuri = []
    for termen in sorted(acc.keys()):
        items = []
        for tip in sorted(acc[termen].keys()):
            g = acc[termen][tip]
            items.append({"tip": tip, "nr_firme": len(g["firme"]), "an": g["an"],   # [P1c] an perioada
                          "incert": g["incert"], "firme": g["firme"]})               # [P4] perioada deschisa
        zile = (datetime.date.fromisoformat(termen) - azi).days
        grupuri.append({"termen": termen, "zile": zile, "items": items})

    # [719] restanțele (termen trecut, nedepuse) stau în capul listei, ca grupuri cu `zile` negativ; „următoarea scadență” e prima de azi încolo
    restante = sum(i["nr_firme"] for g in grupuri if g["zile"] < 0 for i in g["items"])
    urmatoarea = None
    viitoare = [g for g in grupuri if g["zile"] >= 0]
    if viitoare:
        g = viitoare[0]
        # tipul cu cele mai multe firme la primul termen
        top = max(g["items"], key=lambda x: x["nr_firme"])
        urmatoarea = {"termen": g["termen"], "zile": g["zile"],
                      "tip": top["tip"], "nr_firme": top["nr_firme"]}

    return {"grupuri": grupuri, "urmatoarea": urmatoarea, "restante": restante, "neevaluate": neevaluate or []}
