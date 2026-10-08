# -*- coding: utf-8 -*-
"""core/activitati_amef.py — activitățile exceptate de la obligația utilizării AMEF (D394 Î2). PUR, fără DB.

Sursa: OUG 28/1999 art.2 („Se exceptează de la prevederile art. 1 alin. (1) încasările efectuate din următoarele
activități: …”), forma consolidată din corpus (`anaf_surse/oug_28_1999.html`). Verificat 03.10.2026: lista NU e în
HG 479/2003 (normele trimit la ordonanță). Lit. p) e abrogată (Legea 136/2019) — nu se oferă.

Eticheta e scurtă, pentru ecran; textul de lege e cel din articol (`ART2`). D394 Î2 (OPANAF 2194/2025 lit.G) cere doar
încasările lunare din aceste activități, pe cote — litera se păstrează pe profil ca firma să-și știe temeiul exceptării.
"""

ART2 = ("OUG 28/1999 art.2", "anaf_surse/oug_28_1999.html",
        "Se exceptează de la prevederile art. 1 alin. (1) încasările efectuate din următoarele activități:")

#: litera din art.2 -> eticheta din ecran (rezumat; temeiul e articolul)
ACTIVITATI = {
    "a": "comerț ocazional cu produse agricole din producție proprie (producători agricoli individuali)",
    "b": "vânzarea de ziare și reviste prin distribuitori specializați",
    "c": "transport public local de persoane / metrou, pe bilete sau abonamente tipărite",
    "d": "încasări pe bonuri cu valoare fixă tipărite (spectacole, muzee, parcări, jocuri de noroc etc.)",
    "e": "asigurări, case de pensii, intermedieri financiare (nu schimbul valutar pentru persoane fizice)",
    "f": "profesii libere fără societate comercială",
    "g": "obiecte de cult și servicii religioase ale instituțiilor de cult",
    "h": "comerț cu amănuntul prin comis-voiajori sau prin corespondență",
    "i": "instalații, reparații și întreținere la domiciliul clientului",
    "j": "pachete de servicii turistice ale agențiilor de turism",
    "k": "utilități (energie, gaze, apă, telefonie, poștă, salubritate, televiziune, internet)",
    "l": "construcții, reparații, amenajări și întreținere de locuințe",
    "m": "transport feroviar public de călători, pe bilete sau abonamente tipărite",
    "n": "jocuri de noroc cu mijloace tehnice pe bază de acceptatoare de bancnote sau monede",
    "o": "parcări auto încasate prin automate cu acceptatoare de bancnote sau monede",
    "q": "comerț cash and carry către persoane fizice înregistrate la vânzător",
    "r": "transport rutier internațional contra cost de persoane",
    "s": "încărcarea vehiculelor electrice prin automate, exclusiv cu card sau portofel electronic",
}

#: OUG 28/1999 art.1 alin.(1) — de ce o firmă NEexceptată nu emite chitanță de vânzare fără factură
ART1 = ("OUG 28/1999 art.1 alin.(1)", "anaf_surse/oug_28_1999.html",
        "Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de "
        "credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a "
        "prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat "
        "electronice fiscale.")

#: OPANAF 2194/2025 anexa 2 pct.15–17 — totalul lunar Î2 se defalcă în bază + TVA, pe cote
INSTRUCTIUNI_G = ("OPANAF 2194/2025 anexa 2 pct.15-17", "anaf_surse/opanaf_2194_2025_d394.txt",
                  "15. Coloana \"Total încasări\" de la lit. G - se înscrie totalul încasărilor, în lei, lunare [...] "
                  "respectiv încasări lunare obţinute din activităţi exceptate de la obligaţia utilizării aparatelor "
                  "de marcat electronice fiscale [...] 16. Coloana \"Total bază impozabilă\" [...] defalcată pe cote de "
                  "TVA (21%, 19%, 11%, 9%, 5%) [...] 17. Coloana \"Taxa pe valoarea adăugată\" [...]")

COD_VANZARE_NEEXCEPTATA = "CHITANTA_VANZARE_FARA_EXCEPTARE_AMEF"
COD_NEDECLARATA = "AMEF_EXCEPTARE_NEDECLARATA"
COD_COTA_LIPSA = "CHITANTA_I2_FARA_COTA"
COD_COTA_NEPERMISA = "CHITANTA_I2_COTA_NEPERMISA"


def defalcare(suma, cota):
    """Suma încasată pe chitanță (cu TVA) -> (baza, tva), în lei cu bani.

    INTERPRETARE CU TEMEI: chitanța poartă suma încasată, iar D394 lit.G (`INSTRUCTIUNI_G`) cere totalul încasărilor
    împărțit în bază și TVA. Încasarea include taxa — principiul din CF art.282 alin.(8) („fiecare încasare totală sau
    parțială se consideră că include și taxa aferentă”), cu procedeul sutei mărite din HG 1/2016 (cota x 100 / (100 +
    cota)), rotunjit aritmetic. Aceeași metodă ca la rapoartele Z. Alternativa respinsă: cota aplicată pe sumă (ar fi
    considerat suma o bază și ar fi umflat încasarea). De reconfirmat dacă apare o normă care transează Î2.
    O SINGURĂ funcție pentru nota contabilă, D300 și D394 — cifrele nu pot diverge între ele."""
    from decimal import Decimal
    from core.tva_incasare import tva_din_incasare
    s = Decimal(str(suma))
    tva = tva_din_incasare(s, cota)
    return s - tva, tva


def _refuz(cod, mesaj, temei):
    """Excepția cu motivul ca DATĂ (cod + temei), construită aici — modulul care o ridică nu citează legea."""
    e = ValueError(mesaj)
    e.cod, e.temei = cod, temei
    return e


def refuz_vanzare_neexceptata():
    return _refuz(COD_VANZARE_NEEXCEPTATA,
                  "Chitanța nu s-a emis: o vânzare încasată în numerar fără factură se face cu bon fiscal (OUG 28/1999 "
                  "art. 1 alin. (1)). Chitanța de vânzare fără factură e doar pentru firmele cu activitate exceptată de "
                  "la casa de marcat (OUG 28/1999 art. 2) — dacă firma e în situația asta, marchează exceptarea în Date "
                  "firmă, la «Casa de marcat». Altfel, emite factura și chitanța din ea.", ART1[0])


def refuz_nedeclarata():
    """[lotul 07.10 B, comanda Costin A.3] faptul nu mai are implicit în schemă: se cere la prima folosire, o singură dată."""
    e = _refuz(COD_NEDECLARATA,
               "Chitanța fără factură nu s-a emis: în Date firmă, la «Casa de marcat», nu e declarat dacă firma are activitate "
               "exceptată de la casa de marcat (OUG 28/1999 art. 2). Declar-o o singură dată — de ea depinde dacă încasarea "
               "e vânzare (D394, încasări din activități exceptate) sau încasare de creanță.", ART2[0])
    e.ecran = "date_firma"
    return e


def refuz_cota_lipsa():
    return _refuz(COD_COTA_LIPSA,
                  "Chitanța nu s-a emis: alege cota de TVA a încasării (0% dacă activitatea e scutită). Firma e exceptată "
                  "de la casa de marcat, iar încasarea intră în declarația 394 la încasările din activități exceptate, "
                  "defalcată pe cote.", INSTRUCTIUNI_G[0])


COD_CLASIFICARE = "CHITANTA_I2_NU_SE_POATE_CLASIFICA"


def refuz_clasificare(motiv):
    return _refuz(COD_CLASIFICARE, "Cota nu s-a stabilit: %s" % motiv, INSTRUCTIUNI_G[0])


def refuz_cota_nepermisa(cota, permise):
    return _refuz(COD_COTA_NEPERMISA,
                  "Chitanța nu s-a emis: cota %s%% nu se poate folosi la data chitanței. Cotele posibile atunci: %s." % (
                      cota, ", ".join("%s%%" % p for p in permise)), INSTRUCTIUNI_G[0])


def detaliu(e):
    """Corpul refuzului (HTTP 400) ca AFIRMAȚIE TIPATĂ — ecranul citește `mesaj` și `cod`."""
    from core import afirmatii as _af
    from core import mesaje as _mesaje
    extra = ({"ecran": e.ecran, "camp_ecran": _mesaje.camp_ecran(e.cod)}   # butonul spre Date firmă, la câmpul cerut (api.js)
             if getattr(e, "ecran", None) else {})
    return _af.afirmatie("neconformitate", "chitanta", str(e), unde="Casă", regula=e.temei,
                         cod=e.cod, mesaj=str(e), temei=e.temei, **extra)


def cote_permise(la_data):
    """Cotele (procente întregi) cu care se poate emite o chitanță Î2 la data dată: în vigoare atunci ȘI cu rubrică în
    op2 (D394Validator v5: baza/TVA 21/20/19/11/9/5), plus 0 (activitate scutită — intră doar în totalul lunii).
    Registrul de cote nu acoperă data -> doar rubricile op2 + 0 (nu se refuză pe necunoaștere)."""
    from core.common import cote_tva_in_vigoare
    from core.d394 import OP2_RUBRICI_NOMENCL
    cote, _t = cote_tva_in_vigoare(la_data)
    rubrici = set(OP2_RUBRICI_NOMENCL) | {0}
    if cote is None:
        return sorted(rubrici, reverse=True)
    return sorted({int(c) for c in cote if int(c) == c} & rubrici, reverse=True)
