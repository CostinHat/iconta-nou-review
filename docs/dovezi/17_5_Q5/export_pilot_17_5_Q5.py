"""Exporturile Pilot ale lotului 17.5-Q5 (comanda pct.10): un rând pe fiecare din cele 45 de poziții (codurile din reper_r62_17_5_Q5.csv), 1 / 0 / -
pe cele șase criterii, E = c32532357caa (E Q2) și C = C Q5 (produsul = C2 Q3 fb5208ee pe bloburi). Fiecare măsurare are proveniența: «Q5» = măsurată în acest lot
(proba e.* pe P, regresiile pe P, «inainte»/«dupa» pe C), «Q3 adoptat» = măsurarea lui 17.5-Q3 pe o fereastră al cărei cod e identic în C Q5 (în afara ?v=).
Un criteriu nemăsurat rămâne «-». Uz: python3 export_pilot_17_5_Q5.py <reper_r62.csv> <iesire_E.csv> <iesire_C.csv>"""
import csv
import sys

CRITERII = ("Funcțional", "Aspect", "Design", "Simplitate", "Conformitate", "Stabilitate")
I = {c: i for i, c in enumerate(CRITERII)}

# cod -> (măsurat pe E, măsurat pe C, dovada)
M = {
    'F011': ({'Design': '0'}, {'Design': '1'}, '761: «Contează» principal pe 11 rânduri pe E (a.3=11, e.5 pică; Q3 «inainte» și Q5 «inainte») → secundar pe C Q5 (e.5 trece în proba dedicată pe P și în poartă; a.3 în «dupa» pe C Q5)'),
    'F012': ({'Design': '0'}, {'Design': '1'}, 'aceeași fereastră Bancă (761; e.5 / a.3 Q5)'),
    'F073': ({'Design': '0'}, {'Design': '1'}, 'aceeași fereastră Bancă (761; e.5 / a.3 Q5)'),
    'F015': ({'Design': '0'}, {'Design': '1'}, '855: «+ Chitanță fără factură» inactiv cu motivul numai în title → motivul scris lângă buton'),
    'F017': ({'Design': '0', 'Funcțional': '1', 'Conformitate': '1'}, {'Design': '1', 'Funcțional': '1', 'Conformitate': '1'}, '855 (Design); e2e_pilot_f017.py trece; PDF CHF1 nr. 2: serie, număr, dată, 1.210,00 și «una mie două sute zece lei» = chitanța din bază'),
    'F025': ({'Design': '0'}, {'Design': '0'}, '862: «Propune regularizarea TVA» secundar pe C; «Reevaluare valută» rămâne principal în corp (regula 429), deci tot două principale'),
    'F045': ({'Design': '0', 'Conformitate': '1'}, {'Design': '1', 'Conformitate': '1'}, '863 (Istoric facturi, «Arată încă 0» → inactiv cu motiv vizibil); PDF: CUI 403000015 (negăsit la ANAF) fără RO, DANTE «RO14399840»'),
    'F046': ({'Funcțional': '0', 'Design': '0'}, {'Funcțional': '1', 'Design': '1'}, '852 (explicația notei 30 / cantitatea notelor 8, 32 corectate la afișare); 619 nereprodus pe calea de azi; Design = 863'),
    'F054': ({'Design': '0'}, {'Design': '0'}, '860 parțial pe C2 = C Q5: «Generează amortizarea» secundar și «+ Notă nouă» unicul principal, dar motivul lui «Blochează luna» inactiv nu se vede la ≤ 700 px (`.motiv-blocare`, stil.css, cerut de X09) — limita se predă lui Q4'),
    'F078': ({'Design': '0'}, {'Design': '1'}, '859: «+ Salariat nou» secundar, «Contabilizează statul» în bară'),
    'F080': ({'Design': '0', 'Conformitate': '1'}, {'Design': '1', 'Conformitate': '1'}, '859 (Design); deducerea 562 = 13% × 4.325 rotunjit matematic (art.77 alin.(4) CF, HG 146/2026, d112_struct_anaf.txt l.192–193)'),
    'F087': ({'Design': '0'}, {'Design': '1'}, '859: Salariați fără al doilea principal'),
    'F081': ({'Funcțional': '1', 'Aspect': '1', 'Design': '1', 'Simplitate': '1', 'Conformitate': '1', 'Stabilitate': '1'}, {'Funcțional': '1', 'Aspect': '1', 'Design': '1', 'Simplitate': '1', 'Conformitate': '1', 'Stabilitate': '1'}, 'sonda5 (F081.json) pe E și C, scenariul corectat (868): 09/2026 → 26.10 D100/D112/D300/D301/D390, 30.10 D394, 02.11 D406; antet Termen/Declarație/Firme/Stare, 0 rânduri-titlu, «Termen» pe fiecare rând; fără derulare orizontală la 1366 și 2133 (603: captura de diagnostic după încălzirea calculului de fundal + matricea, 0 tăieturi); un principal («Descarcă PDF», în bară); un clic din cabinet, o zonă de derulare; aceeași sursă ca Control fiscal (core/termene_api.py:10,21); a doua deschidere identică, fără erori în consolă; f.4 (antetul Termene) în «dupa» pe C Q5'),
    'F084': ({'Design': '0'}, {'Design': '1'}, 'C236: zona pasivă Solduri inițiale — e.1/e.2 pică pe E (REAL Q5), trec pe P Q5 (cursor default pe 7 noduri, aspect identic repaus/hover, F1 și F7, 1366 și 603)'),
    'F089': ({'Funcțional': '1', 'Aspect': '1', 'Design': '0', 'Simplitate': '1', 'Conformitate': '1', 'Stabilitate': '1'}, {'Funcțional': '1', 'Aspect': '1', 'Design': '1', 'Simplitate': '1', 'Conformitate': '1', 'Stabilitate': '1'}, 'Design: e.4 trece pe P Q5 și a.2 în «dupa» pe C Q5 («Descarcă gestiunea lunii» secundar, «+ NIR nou» unicul principal); ceilalți 5 criterii: 858: «Descarcă gestiunea lunii» secundar pe C (a.2=0, e.4 trece), principal în corp pe E; sonda5/7: tabelul articol/UM/cantitate/CMP/valoare, total 6.272,38 = 371 din balanța 31.10.2026, ieșirea de 100.000 buc refuzată fără scriere (34 → 34 mișcări), fișa Marfa A fără dubluri (primele 15 mișcări citite), Borderou și fișa cu diacritice; fără derulare orizontală la 3 rezoluții; un clic din fereastra firmei, cel mult o zonă de derulare; a doua deschidere identică, fără erori în consolă'),
    'F118': ({'Design': '0'}, {'Design': '1'}, '861: un singur «Deblochează luna», în bara ferestrei deblocării; 860; pe P Q5 e2e_pilot_luna.py::test_pilot_39 trece (blocată → deblocată cu motiv → blocată), fereastra se închide la clic (corecția C2)'),
    'F122': ({'Design': '0'}, {'Design': '0'}, '«▾ detalii» repetă textul vizibil (piesa ds_piese.js, în afara perimetrului); 9 linii fără zonă proprie de ~200 px'),
    'F126': ({'Design': '0'}, {'Design': '1'}, '863 (Istoric facturi)'),
    'F172': ({'Design': '0'}, {'Design': '1'}, 'poarta «Pleacă marfa acum?»: «Emite factură» inactiv cu motiv cât poarta e deschisă; cele două alegeri în casetă'),
    'F252': ({'Design': '0'}, {'Design': '1'}, 'după emitere: «Emisă ✓» cu motivul lui, fără «Completează datele cerute…»'),
    'F254': ({'Design': '0'}, {'Design': '0'}, 'Raport Z: «▾ detalii» repetă textul casetei (piesa ds_piese.js); fișa F1A13: referința bonului și tratamentul păstrate'),
    'F031': ({'Funcțional': '0', 'Conformitate': '0'}, {'Funcțional': '0', 'Conformitate': '0'}, '694.1 nerezolvată (în afara perimetrului: testele deciziei 484)'),
    'F169': ({'Funcțional': '0', 'Conformitate': '0'}, {'Funcțional': '0', 'Conformitate': '0'}, '694.1 nerezolvată'),
    'F022': ({'Funcțional': '1'}, {'Funcțional': '1'}, '750 nereprodus pe copie: 3 facturi → 3 rânduri, numere reale, fără dubluri'),
}

PROVENIENTA = {
    'F011': 'Q5',
    'F012': 'Q5',
    'F073': 'Q5',
    'F015': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F017': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F025': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F045': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F046': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F054': 'Q5 (codul C2 + X09 trece pe P Q5)',
    'F078': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F080': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F087': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F081': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal) + f.4 Q5',
    'F084': 'Q5',
    'F089': 'Q5 (Design) + Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal) (Funcțional, Aspect, Simplitate, Conformitate, Stabilitate)',
    'F118': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal) + pilot_39 Q5',
    'F122': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F126': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F172': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F252': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F254': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F031': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F169': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
    'F022': 'Q3 adoptat (sondele Q3 pe P b0e45e0a / C f6792fcb; codul ferestrei identic cu C2 fb5208ee = C Q5 în afara ?v=: diff b0e45e0a→fb5208ee are 19 linii de conținut, numai Registru jurnal)',
}



def rand(cod, masurat, dovada, eticheta):
    v = ["-"] * 6
    for c, x in masurat.items():
        v[I[c]] = x
    verdict = "ok" if v == ["1"] * 6 else ("nu merge" if "0" in v else "nemăsurat complet")
    obs = "%s — %s [proveniență: %s]" % (eticheta, dovada, PROVENIENTA[cod]) if dovada else "%s — nemăsurat în lot" % eticheta
    return [cod, *v, verdict, obs]


def main(reper, iesire_e, iesire_c):
    with open(reper, encoding="utf-8-sig", newline="") as f:
        coduri = [r["Cod"].strip() for r in csv.DictReader(f)]
    assert len(coduri) == 45 and len(set(coduri)) == 45
    antet = ["Cod", *CRITERII, "Verdict", "Ce lipsește / observații (17.5-Q5, copia de test iconta_test-20261104-171456)"]
    for cale, k, et in ((iesire_e, 0, "E c32532357caa"), (iesire_c, 1, "C 17.5-Q5")):
        with open(cale, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(antet)
            for cod in coduri:
                m = M.get(cod)
                w.writerow(rand(cod, m[k] if m else {}, m[2] if m else "", et))


if __name__ == "__main__":
    main(*sys.argv[1:])
