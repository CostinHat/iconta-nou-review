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

import re
from datetime import date

from core import common as _c
from core.pdf_util import data_ro

#: Data regimului pe care îl reproduce modulul: lista cotei reduse (`CATEGORII_11`) și excepțiile ei sunt cele din CF art.291, forma
#: Legii 141/2025 art.II pct.42, în vigoare la 01.08.2025. [R3b, 11.10.2026] Cotele nu se mai scriu aici (erau `COTA_STANDARD = 21`,
#: `COTA_REDUSA = 11`, ancorate — dublura cheilor `tva_standard`/`tva_redusa` din registru): se citesc din registru LA DATA REGIMULUI.
#: Nu la data operațiunii: întrebarea despre un produs din catalog n-are una, iar cota unei facturi o verifică emiterea, la data
#: facturii (`common.cote_tva_in_vigoare`). Un regim nou (alte categorii) înseamnă alt modul, nu doar altă cifră.
REGIM_LEGEA_141 = date(2025, 8, 1)


def cote_regim():
    """(standard, redusă) în procente întregi, din registru, la data regimului (CF art.291 alin.(1) și (2))."""
    return (int(_c.cota("tva_standard", REGIM_LEGEA_141)[0] * 100), int(_c.cota("tva_redusa", REGIM_LEGEA_141)[0] * 100))

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
        # [lotul 12, deficiența 471] textul intră în promptul modelului: numai cuvintele legii, niciun nume intern (înainte „vezi EXCEPTII_21”,
        # pe care modelul îl copia în justificarea afișată contabilului). CF art.291 alin.(2) lit.b) pct.1-4.
        "exceptii": "cu exceptia: bauturilor alcoolice; bauturilor nealcoolice cod NC 2202; alimentelor cu zahar adaugat, cu "
                    "minimum 10 g zahar total/100 g produs, altele decat laptele praf pentru nou-nascuti, sugari si copii de varsta "
                    "mica; suplimentelor alimentare (Legea 56/2021) -> cota standard",
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
                    "sau destinate exclusiv publicitatii -> cota standard",
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
                    "cod NC 2202 -> cota standard",
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
    std, red = cote_regim()
    linii = [
        "REGULA COTE TVA (art. 291 Cod fiscal, Legea 141/2025, de la %s):" % data_ro(REGIM_LEGEA_141),
        "Doua cote: %d%% standard (implicit) si %d%% redusa (doar lista de mai jos)." % (std, red),
        "",
        "COTA %d%% se aplica DOAR la:" % red,
    ]
    for c in CATEGORII_11:
        linie = f"- {c['descriere']} ({c['lege']})"
        if c.get("exceptii"):
            linie += f" [ATENTIE: {c['exceptii']}]"
        linii.append(linie)
    linii.append("")
    linii.append("RAMAN LA %d%% chiar daca par reduse:" % std)
    for e in EXCEPTII_21:
        linii.append(f"- {e['descriere']}")
    linii.append("")
    linii.append("Tot ce NU se incadreaza explicit la %d%% -> %d%%." % (red, std))
    linii.append("Serviciile obisnuite (consultanta, IT, transport, chirii comerciale, "
                 "constructii etc.) -> %d%%." % std)
    return "\n".join(linii)


#: [lotul 12, deficiența 471] Numele interne ale modulului, cu textul pe care îl vede contabilul în locul lor. Justificarea modelului se
#: arată în Produse (și se păstrează în `produse.justificare`): „EXCEPTII_21” ajungea acolo din prompt („vezi EXCEPTII_21”).
NUME_INTERNE = {"EXCEPTII_21": "excepțiile de la cota redusă", "CATEGORII_11": "categoriile cotei reduse"}
_NUME_INTERN = re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]*[A-Z0-9]\b")


def justificare_afisabila(text):
    """Justificarea fără niciun nume intern de program (`NUME_INTERNE` -> textul lor; orice alt `NUME_MARE_CU_LINIUTA` -> scos), cu
    spațiile strânse. Se aplică răspunsului modelului (`potriveste_cota`) și justificărilor deja păstrate (migrarea
    `core/migrare_produse_justificare.py`). None rămâne None."""
    if text is None:
        return None
    t = str(text)
    for k, v in NUME_INTERNE.items():
        t = t.replace(k, v)
    return re.sub(r"\s+([.,;:)])", r"\1", " ".join(_NUME_INTERN.sub("", t).split()))


def _nedeterminat(motiv):
    """Cota TVA nu s-a putut determina (AI indisponibil/esuat/raspuns invalid). NU se ghiceste
    21: un 21 marcat \"fallback\" ajunge in decont exact ca unul tacit daca factura se emite
    oricum. Se intoarce fara cota -> linia ramane incompleta -> emiterea se blocheaza (baza nula)."""
    return {"ok": False, "cod": "NEDETERMINAT", "cota": None, "categorie": "necunoscut",
            "justificare": motiv, "incredere": "mica", "sursa": "nedeterminat"}


def _fara_model(denum, platitor_tva):
    """Răspunsurile care nu cer modelul: denumirea goală și emitentul neplătitor (cota 0 prin lege). `None` = trebuie întrebat."""
    if not denum:
        return {"ok": False, "cod": "GOL", "mesaj": "denumire lipsă"}
    if not platitor_tva:
        return {"ok": True, "cota": 0, "categorie": "neplatitor_tva",
                "justificare": "Firma nu este platitoare de TVA.",
                "incredere": "mare", "sursa": "regula"}
    return None


def intreaba(denumiri, platitor_tva=True):
    """[R193, comanda Costin 10.10.2026 pct.2, verbatim: „R193: da, cele 10 căi care cer un răspuns AI ținând o conexiune la bază se
    mută înaintea conexiunii.”] Întrebarea către model, pusă cu pool-ul liber: `{(denumire, plătitor TVA): răspunsul}`. Cheia poartă
    și statutul de plătitor, ca tranzacția de după (care îl recitește) să nu folosească un răspuns dat pe altă premisă. Un element
    poate fi și perechea `(denumire, plătitor)` — `facturi_api.intrebari_model` o dă pentru contul de venit, care nu depinde de TVA."""
    out = {}
    for x in denumiri or ():
        d, p = x if isinstance(x, tuple) else (x, platitor_tva)
        d = (d or "").strip()
        if d and (d, bool(p)) not in out:
            out[(d, bool(p))] = potriveste_cota(d, platitor_tva=p)
    return out


def raspuns(raspunsuri, denumire, platitor_tva=True):
    """Răspunsul pregătit de `intreaba` pentru o denumire — ce citește codul care ține o conexiune. Nu întreabă modelul: un răspuns
    lipsă (denumire apărută între citire și emitere) e cota NEDETERMINATĂ, ca la un model indisponibil, nu o întrebare sub conexiune."""
    denum = (denumire or "").strip()
    fara_model = _fara_model(denum, platitor_tva)
    if fara_model is not None:
        return fara_model
    r = (raspunsuri or {}).get((denum, bool(platitor_tva)))
    return r if r is not None else _nedeterminat("Cota TVA nu s-a putut determina pentru această denumire. "
                                                 "Declară cota explicit pe linie.")


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
    fara_model = _fara_model(denum, platitor_tva)
    if fara_model is not None:
        return fara_model

    import json
    try:
        from core import ai_client
    except Exception:
        import ai_client  # rulare directa

    if not ai_client.disponibil():
        return _nedeterminat("AI indisponibil; cota TVA nu s-a putut determina. "
                             "Declara cota explicit pe linie.")

    std, red = cote_regim()
    sistem = (
        "Esti un expert fiscal roman. Stabilesti cota de TVA corecta pentru un "
        "produs sau serviciu, STRICT dupa regula oficiala de mai jos. "
        + ("Nu inventezi. Daca nu se incadreaza clar la %d%%, cota este %d%%.\n\n" % (red, std))
        + rezumat_pentru_ai()
    )
    prompt = (
        f'Produs/serviciu: "{denum}"\n\n'
        "Raspunde DOAR cu un obiect JSON, fara alt text, in formatul:\n"
        # `%` numai pe bucata lui: lipit implicit de f-string-ul de sus, ar formata și denumirea produsului (un „%” în ea ar strica promptul)
        + ('{"cota": %d sau %d, "categorie": "cheia categoriei sau standard", ' % (red, std)) +
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
        return _nedeterminat("Asistentul AI n-a răspuns (%s); cota TVA nu s-a putut determina. "
                             "Alege cota pe linie." % e)

    # extrag JSON-ul (poate veni cu text in jur)
    txt = raspuns.strip()
    if "```" in txt:
        txt = txt.replace("```json", "").replace("```", "").strip()
    try:
        a = int(txt.find("{")); b = int(txt.rfind("}"))
        obj = json.loads(txt[a:b+1])
    except Exception:
        return _nedeterminat("Răspunsul asistentului AI nu s-a putut citi; cota TVA nu s-a putut determina. "
                             "Alege cota pe linie.")

    cota = obj.get("cota")
    if cota not in cote_regim():
        return _nedeterminat("Asistentul AI a propus o cotă care nu există în lege (%r); cota TVA nu s-a putut "
                             "determina. Alege cota pe linie." % cota)
    return {"ok": True, "cota": int(cota),
            "categorie": obj.get("categorie") or "standard",
            "tip": obj.get("tip") or "marfa",  # #11 cont venit pe linie (marfa/produse/servicii)
            "justificare": justificare_afisabila(obj.get("justificare") or ""),   # [471] fără nume interne în textul arătat
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
