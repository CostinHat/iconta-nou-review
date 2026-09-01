# -*- coding: utf-8 -*-
"""RAPORT INTERN de VECHIME A CONFIRMARII (Modelul de temei 01.08, pct.2).

FOST job de expirare (pana la 01.08): semnala valori apropiate de un data_out INVENTAT
(EXPIRA_DUPA_LUNI, scos). Modelul de temei corectat: o lege spune de CAND intra in vigoare, nu pana
cand - data_out se DERIVA din succesor, iar valoarea CURENTA nu expira. Semnalul util nu e "expira"
(fals - legea n-a spus asta), ci "n-a mai fost confirmata la sursa de N luni" (verificat_la vechi).

ALERTA INTERNA catre dezvoltator (canalul observare.alerteaza), NU in interfata contabilului -
contabilul plateste tocmai ca sa nu urmareasca legislatia. Fereastra intre publicarea in MO si
actualizarea in aplicatie NU se poate inchide automat (nu exista API legislativ RO fiabil, masurat
31.07) - doar raportata: cand dezvoltatorul afla de o modificare, o aplica si actualizeaza verificat_la.

Rulabil: python3 -m core.expirare_cote. Rulat LUNAR din cron (ziua 1) - RAPORT, nu blocaj la calcul."""
import os

from core import observare
from core.common import COTE, cote_neconfirmate

# Eticheta umana pentru fiecare cheie din COTE. Acoperirea (ETICHETE == chei COTE) e pazita de test:
# o valoare noua fara eticheta ar produce un mesaj sarac; o eticheta ramasa fara cheie = drift.
ETICHETE = {
    "impozit_micro": "Cota impozit micro (1%)",
    "impozit_profit": "Cota impozit pe profit (16%)",
    "tva_standard": "Cota standard TVA",
    "tva_redusa": "Cota redusa TVA",
    "tva_redusa_9": "Cota redusa TVA 9% (istoric, comasata in 11% de la 01.08.2025)",
    "tva_redusa_5": "Cota redusa TVA 5% (istoric, comasata in 11% de la 01.08.2025)",
    "impozit_dividend": "Cota impozit pe dividende (regim dividende + lichidare)",
    "plafon_tva_incasare": "Plafonul TVA la incasare",
    "plafon_mijloc_fix": "Plafonul de incadrare ca mijloc fix",
    "plafon_sold_casa": "Plafonul soldului de casa",
    "plafon_avans_decontare": "Plafonul avansului de decontare",
    "cas": "Cota CAS (pensie)",
    "cass": "Cota CASS (sanatate)",
    "impozit_venit": "Cota impozit pe venit",
    "cam": "Cota CAM (asiguratorie pentru munca)",
    "salariu_minim": "Salariul minim brut",
    "facilitate_salariu_minim": "Facilitatea la salariul minim (partea neimpozabila)",
    "plafon_facilitate_salariu_minim": "Plafonul facilitatii la salariul minim",
    "tichet_masa_plafon": "Valoarea maxima a tichetului de masa",
    "plafon_intrastat": "Pragul Intrastat (expedieri / introduceri, separat pe flux)",
}


def _prag_luni():
    try:
        return max(1, int(os.environ.get("CONFIRMARE_COTE_PRAG_LUNI", "6")))
    except (ValueError, TypeError):
        return 6


def acoperire_lipsa():
    """(chei COTE FARA eticheta, etichete FARA cheie COTE). Gol = acoperire completa. Garda: raportul
    e util doar daca fiecare valoare are eticheta umana; o eticheta fara cheie (drift) = registrul s-a
    schimbat si nimeni n-a aliniat."""
    fara_eticheta = sorted(n for n in COTE if n not in ETICHETE)
    eticheta_straina = sorted(n for n in ETICHETE if n not in COTE)
    return fara_eticheta, eticheta_straina


def _prag_pentru(_nume, temei):
    """Pragul de reverificare al unei valori, din categoria calculata a articolului ei.

    `None` inseamna *nu se poate calcula* — si atunci `cote_neconfirmate` pastreaza pragul global,
    fara ca valoarea sa iasa din monitorizare. Importul e LOCAL, nu la nivel de modul: `reverificare`
    citeste corpusul si `dependenti_act`, iar un import de sus l-ar trage in fiecare pornire a
    aplicatiei pentru un job care ruleaza o data pe luna.
    """
    try:
        from core.reverificare import categorie
        return categorie(temei)["prag_luni"]
    except Exception:
        # Un instrument de clasificare care crapa NU are voie sa opreasca raportul de vechime.
        # Cade pe pragul global, si asta se vede in `prag_sursa`.
        return None


def _mesaj(x):
    et = ETICHETE.get(x["nume"], x["nume"].replace("_", " "))
    if x["verificat_la"] is None:
        vech = "NU are data de confirmare la sursa (verificat_la lipsa)"
    else:
        vech = ("confirmata ultima data la %s (acum ~%d luni)"
                % (x["verificat_la"].isoformat(), x["luni_de_la_confirmare"]))
    vech += " · prag %d luni (%s)" % (x.get("prag_luni", 0), x.get("prag_sursa", "global"))
    return ("%s (%s, %s, in vigoare din %s) %s. Verifica in Monitorul Oficial daca a aparut un act "
            "normativ nou; daca valoarea e neschimbata, actualizeaza verificat_la in core/common.py, "
            "daca s-a schimbat, adauga valoarea noua (data_out se deriva automat)."
            % (et, x["valoare"], x["temei"], x["din"].isoformat(), vech))


def ruleaza(prag_luni=None, la_data=None, alerteaza=None):
    prag = prag_luni if prag_luni is not None else _prag_luni()
    _alerteaza = alerteaza or observare.alerteaza
    # PRAG PER ARTICOL (R109). `prag` ramane PODEAUA: o valoare nu poate primi un prag mai LARG
    # decat cel global — vezi `cote_neconfirmate`. Masurat inainte de a lega: 0 -> 3 alerte, toate
    # din clasa VOLATIL/DEPUS (dividende, micro, impozit pe venit), zero mai larg.
    care = cote_neconfirmate(prag, la_data=la_data, prag_pentru=_prag_pentru)
    if not care:
        print("toate valorile fiscale au fost confirmate in pragul lor (podea globala %d luni)" % prag)
        return {"prag_luni": prag, "neconfirmate": 0, "alerte_trimise": 0}
    # O SINGURA alerta pe rulare, toate valorile grupate (un paragraf fiecare, in ordinea vechimii).
    corp = (chr(10) + chr(10)).join(_mesaj(x) for x in care)
    n = len(care)
    subiect = ("O valoare fiscala n-a mai fost confirmata in pragul ei" if n == 1
               else "%d valori fiscale n-au mai fost confirmate in pragul lor" % n)
    cheie = "confirmare_cote:" + ",".join(
        "%s@%s" % (x["nume"], x["verificat_la"].isoformat() if x["verificat_la"] else "nicicand") for x in care)
    print(corp)
    trimise = 1 if _alerteaza(cheie, subiect, corp) else 0
    return {"prag_luni": prag, "neconfirmate": n, "alerte_trimise": trimise}


if __name__ == "__main__":
    import json, datetime
    from core import cron
    cron.ruleaza("expirare_cote",
                 lambda: print("%s expirare_cote: %s" % (
                     datetime.datetime.now().isoformat(timespec="seconds"), json.dumps(ruleaza()))))
