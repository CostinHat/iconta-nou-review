"""
core/cote_tva.py — regula oficiala a cotelor de TVA (art. 291 Cod fiscal,
modificat prin Legea 141/2025, in vigoare de la 01.08.2025).

De la 01.08.2025 exista DOUA cote:
  - 21% cota standard (art. 291 alin. 1) — tot ce nu e explicit la 11%
  - 11% cota redusa unica (art. 291 alin. 2) — lista limitativa de mai jos

Cotele de 5% si 9% au fost ABROGATE.

Acest modul e SURSA DE ADEVAR pe care se sprijina potrivirea AI (denumire produs
-> cota). Nu se ghiceste nimic: regula e reprodusa din lege, cu excepatiile ei.

Structura CATEGORII_11 e gandita ca sa poata fi injectata in promptul AI ca
referinta, iar EXCEPTII_21 marcheaza produsele care par sa fie in lista redusa
dar raman la 21% (alcool, bauturi NC 2202, alimente cu zahar >10g, suplimente).
"""

COTA_STANDARD = 21
COTA_REDUSA = 11

# Categoriile la care se aplica cota redusa de 11% (art. 291 alin. 2, lit. a-n)
# Fiecare intrare: cheie interna + descriere (asa cum apare in lege) + exemple.
CATEGORII_11 = [
    {
        "cheie": "medicamente",
        "lege": "art. 291 (2) a)",
        "descriere": "Medicamente de uz uman",
        "exemple": ["medicamente", "antibiotice", "vaccinuri de uz uman"],
    },
    {
        "cheie": "alimente",
        "lege": "art. 291 (2) b)",
        "descriere": "Alimente si bauturi pentru consum uman si animal; animale si "
                     "pasari vii din specii domestice",
        "exemple": ["paine", "lapte", "carne", "legume", "fructe", "oua",
                    "faina", "ulei", "apa plata", "furaje", "gaini vii"],
        "exceptii": "vezi EXCEPTII_21 (alcool, NC 2202, zahar >10g/100g, suplimente)",
    },
    {
        "cheie": "apa_canalizare",
        "lege": "art. 291 (2) c)",
        "descriere": "Servicii de alimentare cu apa si de canalizare",
        "exemple": ["furnizare apa potabila", "servicii canalizare"],
    },
    {
        "cheie": "apa_irigatii",
        "lege": "art. 291 (2) d)",
        "descriere": "Livrarea apei pentru irigatii in agricultura",
        "exemple": ["apa irigatii"],
    },
    {
        "cheie": "agricultura",
        "lege": "art. 291 (2) e) si f)",
        "descriere": "Ingrasaminte si pesticide agricole, seminte si produse "
                     "agricole pentru insamantare/plantare, servicii agricole",
        "exemple": ["ingrasaminte", "pesticide", "seminte", "servicii agricole"],
    },
    {
        "cheie": "carti_publicatii",
        "lege": "art. 291 (2) g)",
        "descriere": "Manuale scolare, carti, ziare si reviste (fizic sau electronic)",
        "exemple": ["carte", "manual scolar", "ziar", "revista"],
        "exceptii": "cu exceptia celor cu continut predominant video/muzical audio "
                    "sau destinate exclusiv publicitatii -> 21%",
    },
    {
        "cheie": "acces_cultural",
        "lege": "art. 291 (2) h)",
        "descriere": "Acces la castele, muzee, case memoriale, monumente istorice, "
                     "monumente de arhitectura si arheologice, gradini zoologice si botanice",
        "exemple": ["bilet muzeu", "acces gradina zoologica", "bilet monument istoric"],
    },
    {
        "cheie": "lemn_foc",
        "lege": "art. 291 (2) i)",
        "descriere": "Lemn de foc (trunchiuri, butuci, vreascuri), rumegus, pelete, "
                     "brichete din lemn — catre persoane fizice utilizatori finali",
        "exemple": ["lemn de foc", "pelete lemn", "brichete lemn", "rumegus"],
    },
    {
        "cheie": "locuinte_sociale",
        "lege": "art. 291 (2) l)",
        "descriere": "Livrarea locuintelor ca parte a politicii sociale (camine batrani, "
                     "case de copii, centre pentru minori cu handicap)",
        "exemple": ["locuinta politica sociala", "camin batrani"],
    },
    {
        "cheie": "cazare",
        "lege": "art. 291 (2) m)",
        "descriere": "Cazare hoteliera sau in sectoare cu functie similara, inclusiv "
                     "inchirierea terenurilor amenajate pentru camping",
        "exemple": ["cazare hotel", "cazare pensiune", "loc camping", "cazare cu mic dejun"],
    },
    {
        "cheie": "restaurant_catering",
        "lege": "art. 291 (2) n)",
        "descriere": "Servicii de restaurant si de catering",
        "exemple": ["meniu restaurant", "catering eveniment", "servire masa"],
        "exceptii": "cu exceptia bauturilor alcoolice si a bauturilor nealcoolice "
                    "cod NC 2202 -> 21%",
    },
]

# Excepatii: par sa fie in categoriile reduse, dar raman la 21% (art. 291 alin. 2)
EXCEPTII_21 = [
    {
        "cheie": "bauturi_alcoolice",
        "descriere": "Bauturi alcoolice (bere, vin, spirtoase) — chiar si in restaurant/catering",
        "exemple": ["bere", "vin", "vodca", "whisky", "sampanie"],
    },
    {
        "cheie": "bauturi_nc2202",
        "descriere": "Bauturi nealcoolice cod NC 2202: ape minerale/gazoase cu zahar/"
                     "aromatizate, sucuri, bauturi racoritoare",
        "exemple": ["cola", "suc acidulat", "energizant", "apa aromatizata", "limonada imbuteliata"],
    },
    {
        "cheie": "alimente_zahar",
        "descriere": "Alimente cu zahar adaugat, continut total zahar >= 10g/100g "
                     "(altele decat lapte praf pentru sugari)",
        "exemple": ["ciocolata", "bomboane", "prajituri cu zahar", "biscuiti dulci"],
    },
    {
        "cheie": "suplimente",
        "descriere": "Suplimente alimentare (Legea 56/2021)",
        "exemple": ["vitamine supliment", "proteine pudra", "suplimente sport"],
    },
    {
        "cheie": "carti_media",
        "descriere": "Carti/publicatii cu continut predominant video/muzical audio "
                     "sau destinate exclusiv publicitatii",
        "exemple": ["revista cu CD muzical", "catalog publicitar"],
    },
]


def rezumat_pentru_ai():
    """
    Intoarce un text compact cu regula (categorii 11% + exceptii 21%),
    de injectat in promptul AI ca referinta. Fara diacritice, concis.
    """
    linii = [
        "REGULA COTE TVA (art. 291 Cod fiscal, Legea 141/2025, de la 01.08.2025):",
        "Doua cote: 21% standard (implicit) si 11% redusa (doar lista de mai jos).",
        "",
        "COTA 11% se aplica DOAR la:",
    ]
    for c in CATEGORII_11:
        linie = f"- {c['descriere']} ({c['lege']})"
        if c.get("exceptii"):
            linie += f" [ATENTIE: {c['exceptii']}]"
        linii.append(linie)
    linii.append("")
    linii.append("RAMAN LA 21% chiar daca par reduse:")
    for e in EXCEPTII_21:
        linii.append(f"- {e['descriere']}")
    linii.append("")
    linii.append("Tot ce NU se incadreaza explicit la 11% -> 21%.")
    linii.append("Serviciile obisnuite (consultanta, IT, transport, chirii comerciale, "
                 "constructii etc.) -> 21%.")
    return "\n".join(linii)


def _nedeterminat(motiv):
    """Cota TVA nu s-a putut determina (AI indisponibil/esuat/raspuns invalid). NU se ghiceste
    21: un 21 marcat \"fallback\" ajunge in decont exact ca unul tacit daca factura se emite
    oricum. Se intoarce fara cota -> linia ramane incompleta -> emiterea se blocheaza (baza nula)."""
    return {"ok": False, "cod": "NEDETERMINAT", "cota": None, "categorie": "necunoscut",
            "justificare": motiv, "incredere": "mica", "sursa": "nedeterminat"}


def potriveste_cota(denumire, platitor_tva=True):
    """  [p96_potriveste]
    Potriveste denumirea unui produs/serviciu cu cota TVA corecta, folosind
    regula oficiala (art. 291) + AI. Intoarce dict:
      {ok, cota, categorie, justificare, incredere, sursa}
    - Daca firma NU e platitoare TVA -> cota 0 direct (fara AI).
    - Daca AI e indisponibil, esueaza sau raspunde neinterpretabil -> NEDETERMINAT
      (ok=False, cota=None, sursa='nedeterminat'), NU cota standard. Vezi
      `_nedeterminat` pentru rationament: un 21 marcat "fallback" ajunge in decont
      exact ca unul tacit, daca factura se emite oricum. Linia ramane incompleta,
      emiterea se blocheaza (regula bazei nule), iar contabilul declara cota explicit.
    incredere: 'mare' / 'medie' / 'mica' (cat de sigur e AI).

    Docstring-ul asta a spus pana la 20.08.2026 exact pe dos ("fallback: cota standard
    21%, ca sa nu blocheze fluxul") - afirmatie ramasa de la o versiune anterioara si
    niciodata verificata la sursa. Codul are dreptate si poarta motivul; regula nu se
    inmoaie ca sa se potriveasca unui text. Legat de `test_granite_cota.py` TEMA D.
    """
    denum = (denumire or "").strip()
    if not denum:
        return {"ok": False, "cod": "GOL", "mesaj": "denumire lipsă"}

    if not platitor_tva:
        return {"ok": True, "cota": 0, "categorie": "neplatitor_tva",
                "justificare": "Firma nu este platitoare de TVA.",
                "incredere": "mare", "sursa": "regula"}

    import json
    try:
        from core import ai_client
    except Exception:
        import ai_client  # rulare directa

    if not ai_client.disponibil():
        return _nedeterminat("AI indisponibil; cota TVA nu s-a putut determina. "
                             "Declara cota explicit pe linie.")

    sistem = (
        "Esti un expert fiscal roman. Stabilesti cota de TVA corecta pentru un "
        "produs sau serviciu, STRICT dupa regula oficiala de mai jos. "
        "Nu inventezi. Daca nu se incadreaza clar la 11%, cota este 21%.\n\n"
        + rezumat_pentru_ai()
    )
    prompt = (
        f'Produs/serviciu: "{denum}"\n\n'
        "Raspunde DOAR cu un obiect JSON, fara alt text, in formatul:\n"
        '{"cota": 11 sau 21, "categorie": "cheia categoriei sau standard", '
        '"tip": "marfa sau produse sau servicii", '
        '"justificare": "o fraza scurta cu temeiul legal", '
        '"incredere": "mare/medie/mica"}\n'
        "Daca denumirea e ambigua (ex. poate fi si aliment si supliment), pune "
        "incredere 'mica' si alege varianta cea mai probabila."
        " tip = clasificarea contabila a contului de venit (OMFP 1802/2014): "
        "marfa = bunuri cumparate spre revanzare (707); produse = produse finite "
        "fabricate de firma (701); servicii = prestari (consultanta, IT, transport, "
        "chirii etc.) (704). Alege tipul dupa natura reala a denumirii."
    )
    try:
        raspuns = ai_client.genereaza_text(prompt, sistem=sistem,
                                           max_tokens=300, temperatura=0)
    except Exception as e:
        return _nedeterminat("AI a esuat (%s); cota TVA nu s-a putut determina. "
                             "Declara cota explicit pe linie." % e)

    # extrag JSON-ul (poate veni cu text in jur)
    txt = raspuns.strip()
    if "```" in txt:
        txt = txt.replace("```json", "").replace("```", "").strip()
    try:
        a = int(txt.find("{")); b = int(txt.rfind("}"))
        obj = json.loads(txt[a:b+1])
    except Exception:
        return _nedeterminat("Raspuns AI neinterpretabil; cota TVA nu s-a putut determina. "
                             "Declara cota explicit pe linie.")

    cota = obj.get("cota")
    if cota not in (COTA_STANDARD, COTA_REDUSA):
        return _nedeterminat("AI a intors o cota neacceptata (%r); cota TVA nu s-a putut "
                             "determina. Declara cota explicit." % cota)
    return {"ok": True, "cota": int(cota),
            "categorie": obj.get("categorie") or "standard",
            "tip": obj.get("tip") or "marfa",  # #11 cont venit pe linie (marfa/produse/servicii)
            "justificare": obj.get("justificare") or "",
            "incredere": obj.get("incredere") or "medie",
            "sursa": "ai"}


# STERS 20.08.2026: `cote_valide()` - lista [21, 11, 0] FARA data, cu ZERO consumatori.
# Nu era inofensiva prin nefolosire: chemata pe o factura din iunie 2025 ar fi respins 19% ca
# "invalida", adica ar fi transformat cota corecta de atunci intr-o eroare. Validarea period-aware
# exista deja in `common.cota(...)` / `common.cota_ceruta(...)`; a doua lista, fara perioada, ar fi
# fost logica paralela. Reparatia reala e stergerea, nu conservarea unui cod mort care asteapta
# primul apelant. Gardat de `test_granite_cota.py` TEMA D.


if __name__ == "__main__":
    print(rezumat_pentru_ai())
