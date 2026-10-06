---
title: "Datele din casele de marcat: cum le corelează ANAF cu evidența contabilă și declarațiile?"
description: "Prin OUG 116/2023, datele caselor de marcat (RO e-Case de marcat) sunt sistem de interes strategic. ANAF le corelează cu evidența contabilă și fiscală, pentru neconcordanțe și profiluri de risc."
published: 2026-10-02
modified: 2026-10-03
poarta: v1
---

# Datele din casele de marcat: cum le corelează ANAF cu evidența contabilă și declarațiile?

OUG 116/2023 include Registrul național al aparatelor de marcat, numit „RO e-Case de marcat electronice", printre sistemele informatice de interes strategic național. Datele transmise de casele de marcat sunt folosite pentru a stabili **profiluri de risc** ale contribuabililor și pentru a identifica **neconcordanțe** prin comparare cu datele din **sistemul de declarare și din evidența contabilă și fiscală**. ANAF este obligată să folosească aceste informații, inclusiv prin structurile de control.

Practic, vânzările din rapoartele Z, înregistrate în contabilitate și declarate în deconturile de TVA, pot fi comparate cu datele pe care aparatul le-a transmis singur, fără un control la fața locului.

## Temeiul legal

::: ghid-temei
„Sistemele informatice prevăzute la alin. (3) , precum și datele și informațiile furnizate de către modulele de valorificare prevăzute la art. 1 sunt de interes strategic național [...] în scopul: a) de a obține informații referitoare la profile de risc specifice contribuabililor persoane fizice și juridice; ... b) de a identifica neconcordanțe și/sau inconsistențe între datele și informațiile furnizate de sistemul informatic de interes strategic național, denumit în continuare S.I.I.S.N., prin corelare cu datele și informațiile din sistemul de declarare/evidență contabilă și fiscală."
— OUG 116/2023, art. 2 alin. (1) (sursă: [OUG nr. 116/2023 privind gestionarea și evidențierea veniturilor curente ale bugetului public prin proiecte de digitalizare](https://legislatie.just.ro/Public/DetaliiDocument/277398))

„e) Sistemul informatic național RO e-Case de marcat electronice, reprezentând Registrul național de evidență a aparatelor de marcat electronice fiscale instalate în județe și în sectoarele municipiului București, prevăzut la art. 3^1 din Ordonanța de urgență a Guvernului nr. 28/1999"
— OUG 116/2023, art. 2 alin. (3) lit. e) (sursă: [OUG nr. 116/2023 privind gestionarea și evidențierea veniturilor curente ale bugetului public prin proiecte de digitalizare](https://legislatie.just.ro/Public/DetaliiDocument/277398))
:::

::: ghid-temei
„Informațiile obținute din profilul de risc al contribuabililor persoane fizice și juridice, precum și neconcordanțele și/sau necorelările din sistemul de declarare și/sau evidență contabilă și fiscală sunt utilizate în activitatea de administrare fiscală, inclusiv prin structurile de control fiscal, cu scopul de a valorifica de îndată, potrivit legii, informațiile obținute."
— OUG 116/2023, art. 4 alin. (3) (sursă: [OUG nr. 116/2023 privind gestionarea și evidențierea veniturilor curente ale bugetului public prin proiecte de digitalizare](https://legislatie.just.ro/Public/DetaliiDocument/277398))
:::

Ce prevede actul, punct cu punct:

- **Sursa datelor:** Registrul național și datele transmise de aparate prin conectarea la distanță, obligatorie potrivit art. 3^1 alin. (4) din OUG 28/1999.
- **Modulul de valorificare** pentru RO e-Case de marcat are termen de utilizare 1 aprilie 2024 (art. 8 alin. (2) lit. b)).
- **RO e-TVA** folosește datele din RO e-Factura și din RO e-Case de marcat pentru a precompleta deconturile de TVA (art. 3 alin. (1)). Decontul precompletat e pus la dispoziție, prin mijloace electronice, până la data de 5 inclusiv a lunii următoare termenului legal de depunere (art. 3 alin. (2)).
- **ANAF folosește obligatoriu** datele în administrarea fiscală (art. 4 alin. (1)), iar neconcordanțele ajung și la structurile de control fiscal (art. 4 alin. (3)).

Actul nu descrie concret testele de corelare, dar logica e clară: datele transmise de aparat trebuie să se regăsească în evidență și în declarații. Verificări utile, lunar:

1. Rapoartele Z înregistrate acoperă toate zilele de activitate și seria numerotată a fiecărui aparat.
2. Totalul vânzărilor și al TVA colectate din rapoartele Z se regăsește în conturile de venituri și de TVA colectată.
3. TVA colectată din rapoartele Z se regăsește în decontul de TVA depus și poate fi comparată cu decontul precompletat.
4. Încasările cu cardul din rapoartele Z se regăsesc, în timp, în extrasele bancare.

::: ghid-exemplu
SC Exemplu SRL, plătitoare de TVA lunar, are o casă de marcat. Pentru martie 2026, cele 26 de rapoarte Z transmise de aparat însumează vânzări de 121.000 lei, din care TVA de 21.000 lei la cota de 21% (100.000 × 21% = 21.000 lei).

Contabilul a înregistrat doar 25 de rapoarte Z: raportul din 14 martie, de 4.840 lei cu TVA de 840 lei inclus, a fost omis. În evidență și în D300 apare TVA colectată din vânzări cu bon de 20.160 lei, cu 840 lei mai puțin decât rezultă din datele aparatului. Este exact tipul de neconcordanță vizat de OUG 116/2023. Remediul: înregistrarea raportului omis și corectarea decontului.
:::

## Ce se greșește în practică

- Rapoartele Z se înregistrează lunar, cumulat, din memorie sau din totaluri estimate, nu raport cu raport.
- Se presupune că ANAF vede datele aparatului doar la un control la fața locului, deși ele ajung la ANAF prin conectarea aparatului.
- Decontul precompletat din RO e-TVA nu este consultat, iar diferențele față de propriul calcul nu sunt analizate.
- Încasările cu cardul din rapoartele Z nu sunt reconciliate cu extrasele, iar diferențele rămân neexplicate.

## Ce face iConta.eu

iConta.eu importă rapoartele Z din fișierele exportate de aparat (XML sau .p7b) și construiește pentru fiecare o notă în stare de ciornă: numerarul în 5311, cardul și celelalte plăți în 5125, TVA în 4427. Un raport deja înregistrat, cu același aparat și același număr, este refuzat. Decontul D300 generat de aplicație include și vânzările din rapoartele Z validate, defalcate pe cote; un raport Z validat fără defalcare pe cote oprește generarea decontului, cu raportul numit. În Control fiscal, aplicația compară TVA din decontul D300 calculat cu rulajele conturilor 4427 și 4426 și arată starea coerent, divergent sau neverificabil. Decontul precompletat din SPV nu este preluat automat; comparația cu el rămâne la contabil.

[iConta.eu](/)
