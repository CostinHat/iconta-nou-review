---
title: "SAF-T și D394: ce verifici diferențe"
description: "De ce SAF-T (D406) și D394 pot avea cifre diferite fără să existe o eroare: D406 raportează întreaga evidență contabilă/fiscală, D394 doar subsetul de operațiuni B2B raportabil conform OPANAF 2194/2025."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T și D394: ce verifici diferențe

SAF-T (D406) și D394 nu ar trebui comparate cifră cu cifră, pentru că raportează lucruri diferite: D406 e evidența completă a firmei, D394 e doar operațiunile B2B taxabile în România, raportabile conform legii care guvernează D394.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană, aşa cum este definită la art. 266 alin. (1) pct. 24 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare."
— OPANAF 3769/2015, art. 1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)

„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025, Anexa 2 pct. 1 lit. b) (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Din aceste texte reiese exact perimetrul D394, cel care explică diferențele față de D406:

- D394 raportează doar operațiunile **taxabile în România**, cu locul livrării/prestării pe teritoriul național — livrările/prestările B2B interne, plus livrările intracomunitare și exporturile (ca operațiuni cu partener din categoria 3/4).
- **Achizițiile intracomunitare** sunt excluse explicit din D394 (merg în D390), deci apar în evidența contabilă (și în D406) fără corespondent în D394.
- D394 nu conține vânzările către persoane fizice fără CUI raportabile individual (decât agregat, ca bonuri fiscale care îndeplinesc condițiile unei facturi simplificate), în timp ce D406 (fișierul standard de control fiscal) reflectă întreaga evidență contabilă, inclusiv aceste operațiuni, individual.

Ce merită verificat concret, când apar diferențe: dacă o operațiune apare în D406, dar lipsește din D394, verifică întâi dacă e o achiziție intracomunitară (exclusă corect), o vânzare către persoană fizică fără factură cu partener identificat (nu intră individual), sau chiar o omisiune reală din declarația D394.

## Ce se greșește în practică

- Se așteaptă ca totalul veniturilor din D406 să coincidă cu totalul bazei impozabile din D394 — nu ar trebui, pentru că D406 conține toate operațiunile firmei, D394 doar subsetul B2B/taxabil raportabil.
- Se tratează orice diferență ca „eroare de declarare", fără să se verifice întâi dacă operațiunea lipsă din D394 e, de fapt, o achiziție intracomunitară — care se raportează corect în D390, nu în D394.
- Se ignoră faptul că D394 raportează bonurile fiscale/facturile simplificate agregat, pe total, nu operațiune cu operațiune — o comparație linie-cu-linie cu jurnalul complet din D406 va arăta mereu diferențe pe acest segment, fără să fie o eroare.

## Ce face iConta.eu

iConta.eu generează atât D406, cât și D394, fiecare validat local prin validatorul oficial ANAF (DUK) înainte de a fi considerat gata de depus. Generatorul D394 (`core/d394.py`) exclude explicit din calcul achizițiile de la parteneri din UE/non-UE (comentariu în cod: „ACHIZITIILE INTRACOMUNITARE NU INTRA IN D394 - se declara in D390"), exact regula citată mai sus.

La data acestui ghid, **iConta.eu nu are o funcție dedicată de comparare automată între D406 și D394** — nu există în cod un modul care confrunte cele două declarații între ele. O eventuală divergență trebuie interpretată manual, pe baza regulilor de scop de mai sus, nu presupusă automat ca eroare.

[iConta.eu](/)
