# -*- coding: utf-8 -*-
"""Job LUNAR de avertizare: valorile fiscale actualizate periodic (salariu minim, facilitati,
plafoane) se apropie de expirare.

DE CE: cota() RIDICA pentru date de dupa valabilitatea ultimei intrari (nu mai intoarce tacit
valoarea veche - commit 66c3865) -> un generator care cere valoarea pentru o perioada de dupa
acea data va REFUZA sa genereze. Schimbarile fiscale nu sunt aleatorii (salariul minim se schimba
in decembrie sau iulie), deci un termen anuntat INAINTE lasa timp sa verifici Monitorul Oficial si
sa actualizezi COTE in core/common.py, inainte sa se strice o generare.

Rulat LUNAR din cron (ziua 1, 06:00). Alerta prin canalul unic observare.alerteaza (throttling pe
cheie). Cron: 0 6 1 * * cd ~/iconta_nou && . db.env && python3 -m core.expirare_cote"""
import os

from core import observare
from core.common import EXPIRA_DUPA_LUNI, cote_care_expira

# Eticheta umana pentru fiecare valoare cu expirare. Acoperirea (ETICHETE == EXPIRA_DUPA_LUNI) e
# pazita de test: o valoare noua fara eticheta ar produce un mesaj sarac ("salariu_minim expira").
ETICHETE = {
    "salariu_minim": "Salariul minim brut",
    "facilitate_salariu_minim": "Facilitatea la salariul minim (partea neimpozabilă)",
    "plafon_facilitate_salariu_minim": "Plafonul facilității la salariul minim",
    "plafon_mijloc_fix": "Plafonul de încadrare ca mijloc fix",
}

# Generatoarele care CER valoarea prin cota() strict -> vor REFUZA sa genereze dupa expirare
# (verificat prin grep pe cota("<nume>"): d112 + salarizare, care alimenteaza D112 si D212).
# plafon_mijloc_fix nu e cerut de niciun generator prin cota() -> mesaj generic, fara a inventa.
CONSUMATORI = {
    "salariu_minim": "D112 și D212",
    "facilitate_salariu_minim": "D112 și D212",
    "plafon_facilitate_salariu_minim": "D112 și D212",
}


def _prag_zile():
    try:
        return max(1, int(os.environ.get("EXPIRARE_COTE_PRAG_ZILE", "60")))
    except (ValueError, TypeError):
        return 60


def acoperire_lipsa():
    """(valori cu expirare FARA eticheta, etichete FARA valoare cu expirare). Gol = acoperire completa.
    Garda: mesajul de alerta e util doar daca fiecare valoare cu expirare are o eticheta umana, iar o
    eticheta ramasa fara valoare (drift) semnaleaza ca registrul s-a schimbat si nimeni n-a aliniat."""
    fara_eticheta = sorted(n for n in EXPIRA_DUPA_LUNI if n not in ETICHETE)
    eticheta_straina = sorted(n for n in ETICHETE if n not in EXPIRA_DUPA_LUNI)
    return fara_eticheta, eticheta_straina


def _mesaj(x):
    et = ETICHETE.get(x["nume"], x["nume"].replace("_", " "))
    if x["zile"] < 0:
        termen = "a EXPIRAT deja la %s (acum %d zile)" % (x["expira"].isoformat(), -x["zile"])
    else:
        termen = "expiră la %s, peste %d zile" % (x["expira"].isoformat(), x["zile"])
    consum = CONSUMATORI.get(x["nume"])
    if consum:
        urmare = "Până atunci, %s vor REFUZA să genereze pentru perioade de după acea dată." % consum
    else:
        urmare = ("Actualizeaz-o înainte ca un calcul să o ceară pentru o perioadă ulterioară "
                  "(cota() ridică în mod strict).")
    return ("%s (%s lei, %s, în vigoare din %s) %s. "
            "Verifică în Monitorul Oficial dacă a apărut un act normativ nou și actualizează COTE "
            "în core/common.py. %s"
            % (et, x["valoare"], x["temei"], x["din"].isoformat(), termen, urmare))


def ruleaza(prag_zile=None, la_data=None, alerteaza=None):
    prag = prag_zile if prag_zile is not None else _prag_zile()
    _alerteaza = alerteaza or observare.alerteaza
    care = cote_care_expira(prag, la_data=la_data)
    if not care:
        print("toate valorile fiscale sunt în termen (prag %d zile)" % prag)
        return {"prag_zile": prag, "expira": 0, "alerte_trimise": 0}
    trimise = 0
    for x in care:
        et = ETICHETE.get(x["nume"], x["nume"])
        mesaj = _mesaj(x)
        subiect = (("Valoare fiscală EXPIRATĂ: %s" % et) if x["zile"] < 0
                   else ("Valoare fiscală expiră în %d zile: %s" % (x["zile"], et)))
        cheie = "expirare_cota:%s:%s" % (x["nume"], x["expira"].isoformat())
        print(mesaj)
        if _alerteaza(cheie, subiect, mesaj):
            trimise += 1
    return {"prag_zile": prag, "expira": len(care), "alerte_trimise": trimise}


if __name__ == "__main__":
    import json, datetime
    from core import cron
    cron.ruleaza("expirare_cote",
                 lambda: print("%s expirare_cote: %s" % (
                     datetime.datetime.now().isoformat(timespec="seconds"), json.dumps(ruleaza()))))
