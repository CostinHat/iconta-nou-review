# -*- coding: utf-8 -*-
"""core/registru_interpretari.py — alegerile pe care legea le-a lasat deschise. (P11, 22.08.2026)

Al doilea fel de intrare din registru (Partea III): TEMEI se verifica, INTERPRETAREA se DISCUTA.
Amestecarea lor e interzisa fiindca se revizuiesc diferit - iar o alegere de-a noastra care poarta
marcajul unui temei devine imposibil de repus in discutie.

INTRARILE DE AICI SUNT CELE GASITE PRIN MASURATOARE pe 22.08, nu inventate. Confruntarea cu planul
normativ a scanat 15 egalitati stricte pe valori de registru si a confirmat DOUA, la re-citire pe
context. Restul erau comparatii de formatare, verificari de zero si stari interne.

CE NU E AICI, si de ce conteaza ca scrie: alegerile care NU iau forma unei comparatii. Codificarea
trimestriala 09, ordinea de aplicare a scazamintelor, felul de rotunjire - niciuna nu se vede printr-o
scanare de comparatii. Numarul de intrari de aici NU e numarul interpretarilor din aplicatie; e
numarul celor RECUNOSCUTE. Diferenta e declarata in ARHITECTURA_NORMATIV la interdictia 22.
"""
from core.interpretare import Interpretare

_LISTA = [
    Interpretare(
        cheie="incadrat_la_minim",
        text_citat="persoanele fizice care realizeaza venituri din salarii ... incadrate cu salariul "
                   "de baza minim brut pe tara garantat in plata",
        de_ce_lasa_loc="expresia «incadrat cu» nu spune daca inseamna EXACT salariul minim sau CEL "
                       "MULT salariul minim; un brut cu un leu peste minim e sau nu incadrat cu el?",
        forma="termen_nedefinit",
        variante=[
            ("egalitate_stricta", "brutul contractual e EXACT salariul minim; un leu peste stinge "
                                  "facilitatea"),
            ("prag_maxim", "brutul contractual e CEL MULT salariul minim; facilitatea se pastreaza "
                           "pana la nivelul minimului"),
        ],
        ales="egalitate_stricta",
        motiv="«incadrat cu» descrie nivelul de incadrare din contract, nu o limita superioara; iar "
              "alin.(4) prorateaza facilitatea pe fereastra activa, ceea ce presupune un nivel FIX, "
              "nu un interval. Consecinta e vizibila pentru patron: un leu peste minim costa "
              "salariatul ~82 lei.",
        de_cine="costin",
        la_data="2026-08-22",
        temei_legat="OUG 156/2024 art.LXVI",
    ),
    Interpretare(
        cheie="podea_part_time_minus_facilitate",
        text_citat="nivelul salariului minim brut pe tara ... SE DIMINUEAZA cu 300 lei",
        de_ce_lasa_loc="derogarea poate fi citita ca REDEFINIRE a nivelului de referinta (deci se "
                       "aplica si la baza minima part-time) sau ca FACILITATE acordata doar la norma "
                       "intreaga (deci part-time-ul pastreaza nivelul integral). Structura publicata "
                       "de autoritate o pune INAUNTRUL formulei part_time; textul legii vorbeste de "
                       "norma intreaga.",
        forma="forma_publicata_difera_de_text",
        variante=[
            ("nivel_redefinit", "podeaua part-time = (salariu minim - 300) prorata; urmeaza "
                                "structura ANAF si validatorul"),
            ("facilitate_doar_norma_intreaga", "podeaua part-time = salariu minim integral prorata; "
                                               "urmeaza litera art. despre norma intreaga"),
        ],
        ales="nivel_redefinit",
        motiv="derogarea REDEFINESTE nivelul de referinta (3750 in S1 2026 / 4125 in S2), nu acorda "
              "o facilitate; structura ANAF o pune in formula part_time (l.3128-3129 pentru B4_7P), "
              "iar arbitrul o confirma. Alegerea inversa a produs, intre 06 si 20.08.2026, sume "
              "diferite pe fluturas si pe D112 pentru acelasi salariat (70,25 lei/luna).",
        de_cine="costin",
        la_data="2026-08-20",
        arbitru="DUK regula SP1B4_1",
        arbitru_confirma=True,
        arbitru_spune="validatorul calculeaza 3750 si semnaleaza 4050/4325 ca atentionare",
        temei_legat="OUG 156/2024 art.LXVI alin.(5) = OUG 89/2025 art.III",
    ),
]

INTERPRETARI = {i.cheie: i for i in _LISTA}


def deschise():
    """Interpretarile pe care arbitrul le contrazice si care asteapta lamurire."""
    from core.interpretare import interpretari_deschise
    return interpretari_deschise(_LISTA)


if __name__ == "__main__":
    print("interpretari declarate: %d" % len(INTERPRETARI))
    for k, i in INTERPRETARI.items():
        print("  %-38s %s" % (k, i))
    d = deschise()
    print("dezacorduri DESCHISE cu arbitrul: %d%s"
          % (len(d), (" -> " + ", ".join(x.cheie for x in d)) if d else ""))
