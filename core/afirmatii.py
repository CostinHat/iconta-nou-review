# -*- coding: utf-8 -*-
"""core/afirmatii.py — o AFIRMAȚIE despre datele firmei e un OBIECT, nu un șir (P3, 21.08.2026).

DE CE. Toate defectele de mesaj din 20-21.08 au fost defecte de DATE, apărute fiindcă afirmația era
proză: mesajul care cita motivul ALTEI perioade (motivul era indexat pe tip, nu legat de perioadă),
semnalul care repeta paragraful randat deasupra lui (nu știa că celălalt e pe ecran), starea blocată
fără remediu (remediul trăia în altă funcție), limita care dispare când nu există constatare.

Și partea care închide argumentul: până azi TOATE gărzile de mesaj erau regex pe proză, fiindcă proza
era tot ce aveam — iar de două ori într-o zi s-au întors împotriva noastră (gardul care s-a aprins pe
propria explicație; `lit.` aprins pe cuvântul „po-LIT-e)"). Nu erau gărzi proaste: erau gărzi obligate
să ghicească structura din text.

CE NU E ASTA. NU un șablon. Textul rămâne scris de om, în limba contabilului — e UN atribut, nu
recipientul tuturor. Un mesaj asamblat din câmpuri sună a formular („Obligație: D100. Perioadă: T4.").

GRANIȚA (decisă de Costin, 21.08): se aplică AFIRMAȚIILOR DESPRE DATELE FIRMEI — verdicte, motive,
blocaje, constatări. NU textelor de interfață (titluri, etichete, ajutoare): alea sunt design.

FELUL SE DECLARĂ, nu se deduce din prezența câmpurilor (R2′, 20.08). O deducție ar face ca un câmp
uitat să schimbe TĂCUT înțelesul afirmației — exact clasa pe care o vânăm.
"""

# Nomenclator ÎNCHIS. Un `fel` produs fără intrare aici = eroare, nu omisiune tăcută (tiparul
# VC_RANDATE). Câmpurile cerute urmează FORMA afirmației, nu invers.
FELURI = {
    # Necunoscuta e un INTERVAL pe axa timpului: „nu pot demonstra de când e firma înregistrată în
    # scopuri de TVA" acoperă perioadele trecute până la un punct.
    "necunoastere": ("fel", "tip", "motiv", "domeniu_de", "domeniu_pana"),
    # Un fapt constatat pe o perioadă ANUME. `temei_completitudine` e obligatoriu fiindcă un fapt
    # negativ („nicio operațiune IC în lună") e o afirmație despre lume, iar ea se sprijină pe ce ne
    # face să credem că am văzut tot. Fără el, „fapt" e doar o absență bine îmbrăcată.
    "fapt": ("fel", "tip", "motiv", "an", "luna", "temei_completitudine"),
    # NU am înregistrări într-o sursă NUMITĂ. Absența unei înregistrări nu e absența unui fapt —
    # de-aia `surse_consultate` e obligatoriu: fără el, nimeni nu știe unde s-a uitat.
    "absenta_observatie": ("fel", "tip", "motiv", "surse_consultate"),
    # Relație, nu interval: cât ține statutul, obligația nu există. Capătul de sus e DESCHIS prin
    # natura afirmației — a-l închide artificial ar afirma o graniță pe care realitatea n-o are.
    "statut": ("fel", "tip", "motiv", "statut", "statut_din"),
    # [21.08.2026] Al cincilea fel, adăugat fiindcă îl PRODUCEAM deja în două locuri fără să-l putem
    # numi: profilul declară „fără operațiuni IC" dar există facturi IC reale; și o depunere pe o
    # perioadă declarată neaplicabilă. Nu e necunoaștere — două afirmații care nu pot fi amândouă
    # adevărate. `sursele` le NUMEȘTE pe amândouă, altfel nu se poate arbitra.
    "contradictie": ("fel", "tip", "motiv", "sursele"),
    # [21.08.2026] Al saselea: verificarea INSASI s-a oprit. NU e necunoastere - aia ar ascunde-o ca
    # verdict permanent gri, exact ce refuza `_c_rupt` din control_incrucisat („lectia D300 mort"):
    # o verificare rupta arata la fel cu una care „nu poate spune", si asa a stat D300 mort. `eroare`
    # e obligatorie fiindca fara ea nimeni nu poate incepe s-o repare.
    "verificare_rupta": ("fel", "tip", "motiv", "eroare"),
    # [21.08.2026] Al saptelea: o VALOARE nu satisface o REGULA. Cele 46 de validari de rand la
    # import nu incap in celelalte - nu e necunoastere (stim foarte bine), nu e absenta (valoarea E
    # acolo, dar nu tine), nu e statut. `unde` = pe ce anume (randul 7, salariatul X); `regula` = de
    # ce nu tine. Fara amandoua, respingerea e un repros fara adresa.
    "neconformitate": ("fel", "tip", "motiv", "unde", "regula"),
}

# Câmpurile care au voie să fie None, fiecare cu motivul. Restul trebuie să poarte o valoare.
# Distincția care contează: cheia LIPSEȘTE (afirmație incompletă, eroare) vs cheia e prezentă cu None
# (necunoaștere DECLARATĂ). A doua e un răspuns; prima e o scăpare.
_POT_FI_NONE = {
    "domeniu_pana": "interval deschis la dreapta — necunoscuta ține până azi",
    "statut_din": "nu știm întotdeauna de când ține statutul; declarat necunoscut, nu omis",
    "luna": "afirmație pe AN (d101, d205), nu pe lună",
}


class AfirmatieIncompleta(ValueError):
    """Un câmp cerut de `fel` lipsește. Blocaj motivat, nu KeyError la randare."""


def afirmatie(fel, tip, motiv, **campuri):
    """Construiește o afirmație VALIDĂ sau ridică. Întoarce un dict simplu — payload-ul rămâne JSON,
    nu obiecte de transport."""
    if fel not in FELURI:
        raise AfirmatieIncompleta(
            "fel necunoscut %r; nomenclatorul e închis: %s" % (fel, ", ".join(sorted(FELURI))))
    a = {"fel": fel, "tip": tip, "motiv": motiv}
    a.update(campuri)
    lipsa = [c for c in FELURI[fel] if c not in a]
    if lipsa:
        raise AfirmatieIncompleta(
            "afirmație `%s` pentru %s fără câmpurile cerute: %s. Câmpurile urmează FORMA afirmației "
            "(vezi FELURI); dacă valoarea nu se cunoaște, pune cheia cu None acolo unde e permis, "
            "nu o omite — omisiunea nu se poate deosebi de o scăpare."
            % (fel, tip, ", ".join(lipsa)))
    goale = [c for c in FELURI[fel]
             if a.get(c) is None and c not in _POT_FI_NONE]
    if goale:
        raise AfirmatieIncompleta(
            "afirmație `%s` pentru %s cu câmpuri goale care nu pot fi goale: %s" % (fel, tip, ", ".join(goale)))
    return a


def necunoastere_pe_luna(tip, motiv, an, luna=None):
    """Forma cea mai deasa de necunoastere: „nu pot spune, pe perioada asta".

    Scoasa aici fiindca o scriau deja patru locuri, fiecare cu propria formatare a domeniului - iar
    cand `reconciliaza` producea textul si `_c_gri` ii punea domeniul, existau DOUA surse ale
    perioadei, care puteau sa nu coincida. Acum afirmatia isi poarta domeniul de la nastere.

    Domeniul e luna evaluata (sau anul, la declaratiile anuale). Deschis la dreapta NU se foloseste
    aici: o necunoastere fara capat de sus se citeste peste sase luni ca fapt permanent."""
    dom = ("%04d-%02d" % (an, luna)) if (an and luna) else (str(an) if an else None)
    return afirmatie("necunoastere", tip, motiv, domeniu_de=dom, domeniu_pana=dom)


def domeniu_text(a):
    """Perioada afirmației, în limba contabilului, pentru randare. NU inventează: dacă afirmația nu
    poartă domeniu (fel `statut`), întoarce None și cine randează decide ce face."""
    fel = a.get("fel")
    if fel == "fapt":
        return ("%02d.%04d" % (a["luna"], a["an"])) if a.get("luna") else str(a.get("an") or "")
    if fel == "necunoastere":
        de, pana = a.get("domeniu_de"), a.get("domeniu_pana")
        if de and pana:
            return "%s – %s" % (de, pana)
        if de:
            return "din %s" % de
        return None
    return None
