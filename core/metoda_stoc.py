# -*- coding: utf-8 -*-
"""core/metoda_stoc.py — metoda de evidență a stocului, setare EXPLICITĂ pe firmă (comanda Costin 06.10.2026 §6.3).

Verbatim: „Metoda de stoc e o setare explicită pe firmă (global-valoric / cantitativ-valoric), fără valoare implicită tăcută.
Indiferent de metodă, fiecare ieșire de marfă se descarcă o singură dată: factura fără articol la global-valoric și dubla
descărcare rețete + raport Z la HoReCa se închid.”

O IEȘIRE DE MARFĂ = O SINGURĂ DESCĂRCARE, după metodă (sursa UNICĂ a regulii):
  - GLOBAL-VALORIC: marfa iese prin DESCĂRCAREA LUNARĂ (`stocuri_api.descarca_luna`, K pe 371/378/4428), din toate vânzările
    lunii — raport Z și facturi, cu sau fără articol; ieșirile pe articol (factură, manuală, rețetă) se refuză;
  - CANTITATIV-VALORIC: marfa iese pe ARTICOL, la CMP (factură cu articol, ieșire manuală, rețetă — inclusiv raportul Z al
    HoReCa, prin rețete); descărcarea lunară globală se refuză; o linie de marfă (707) fără articol se refuză la emitere;
  - NEDECLARATĂ (NULL): nicio ieșire nu se descarcă și nicio factură cu marfă nu se emite până se declară metoda — refuz numit,
    cu trimitere la Date firmă. Fără implicit tăcut.
"""
GV = "global_valoric"
CV = "cantitativ_valoric"
ETICHETE = {GV: "global-valoric (preț cu amănuntul, 371/378/4428)", CV: "cantitativ-valoric (fișe de magazie, CMP)"}
COD_NEDECLARATA = "METODA_STOC_NEDECLARATA"
COD_ALTA = "METODA_STOC_ALTA"


def citeste(cur, schema=""):
    p = ('"%s".' % schema) if schema else ""
    cur.execute("SELECT metoda_stoc FROM %sfirma_profil LIMIT 1" % p)
    r = cur.fetchone()
    v = (r["metoda_stoc"] if isinstance(r, dict) else r[0]) if r else None
    return v if v in (GV, CV) else None


def refuz(cod, mesaj):
    e = ValueError(mesaj)
    e.cod, e.ecran = cod, "date_firma"
    return e


def cere(cur, schema, metoda, actiune):
    """Refuză `actiune` dacă metoda firmei nu e `metoda`. Mesajul numește ce lipsește și unde se declară."""
    m = citeste(cur, schema)
    if m is None:
        raise refuz(COD_NEDECLARATA, "%s nu se poate face: metoda de stoc a firmei nu e declarată. Declar-o în Date firmă "
                                     "(global-valoric sau cantitativ-valoric) — de ea depinde cum se descarcă marfa, o singură "
                                     "dată." % actiune)
    if m != metoda:
        raise refuz(COD_ALTA, "%s nu se face la firma cu stoc %s: acolo marfa se descarcă %s, o singură dată." % (
            actiune, ETICHETE[m], "lunar, din toate vânzările (descărcarea gestiunii)" if m == GV
            else "pe articol, la fiecare ieșire"))
    return m
