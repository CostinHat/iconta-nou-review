# 17.5-Q9 — frazele §4 pct.1 (scrise înaintea reparației, 25.11.2026 ~05:35; neschimbate în raport)

Punctul de pornire e produsul C2 289f094f al lui 17.5-Q8 (decizia 8); frazele spun ce urmăresc în Q9, cu deciziile 9–14 ale comenzii.

| Poziție | Fraza (cum am înțeles-o și ce urmăresc) |
|---|---|
| F019 / DS.2 / REAL e.1, e.2, B4 a.1 | În fereastra „De depus” rămâne o singură acțiune principală, la vedere; „Validează” rămâne pe fiecare rând al notelor în ciornă, dar ca buton secundar; cu coada populată cardul se numește „De validat” și secțiunea „Note de validat” are aceeași cifră ca GET /coada. |
| F022 / FISC.8 / REAL e.4 | „Luna comparată” oferă numai lunile de la preluarea firmei încoace, iar semnalul D390 nu mai e tăiat în mijlocul parantezei. |
| F015, F017 / DS.4 / REAL e.3 | După alegerea tipului în Casă, motivul de sub buton spune ce lipsește de fapt (partenerul, suma), nu „tipul”. |
| P2 (regresia e2e_bon_cui_17_5_P2) | Blocul fiscal al bonului (#d-fiscal: codul cumpărătorului, verdictul TVA, nota 6022) se vede sub titlu în fereastra de sus și în ordinea nativă a plasei, nu numai când testul rulează izolat; caut starea lăsată de un test anterior care îl ascunde și repar cauza în produs. |
| F017 / FINAL.3 | Partenerul din Casă se găsește și după nume (cu numele din registru), iar chitanța pe un sold preluat spune „sold preluat la …”, nu „factura Sold la …”. |
| F018 / FINAL.4 | Partenerii se adaugă, se caută, se editează explicit și se șterg dintr-un registru unic (Parteneri și fișa partenerului); Clienți și Furnizori rămân ferestre filtrate ale aceluiași registru, cu formularul și «Salvează» pe rând. |
| F023 / DS.4, DS.5 | Căutarea articolului nu mai scrie „Nimic din listă…” deasupra unui rezultat găsit, iar prețul preluat din articol apare românește („100,00”). |
| F025 / DS.2 | În Închidere lună o singură acțiune principală: când reevaluarea oprește închiderea, „Reevaluare valută” e principală și „Blochează luna” secundară. |
| F031 / DS.2, DS.6, FISC.2 | Pe pasul 2 al declarațiilor o singură principală („Regenerează …” secundar), avertismentele lungi stau sub „▾ detalii”, iar F1A 17 (id 73) e exclusă din rd.9 cu motivul și refuzul de coadă numite, fără blocarea generală a facturilor cu note în ciornă. |
| F034 / DS.5 | Textele D394 sunt cu diacritice, fără majuscule de accent și fără „->”, cu «EXCLUSE» păstrat literal în avertismentul operațiunilor N. |
| F035 / FISC.4 | În D406 nota 146 apare cu descrierea refăcută, rapoartele Z au jurnalul lor (nu „Diverse”), iar factura pe bon nu e numărată ca „factură fără notă”. |
| F043 / STOC.2 | La validarea facturii primite se văd scadența, cumpărătorul și UM-ul liniilor; „Validează” e acțiunea principală; sumele NIR apar românește. |
| F045, F252 / FINAL.5, DS.3 | PDF-ul facturii are adresa cumpărătorului și se descarcă cu numele seriei și numărului; pe factura emisă nu mai apar „Transformă în factură” și „Șterge factura”. |
| F046 / STOC.3 | Nota de stornare se numește „Stornare factura <serie nr> din <data>”; ordinea validării (originalul, apoi stornarea) rămâne cea de azi, cu refuzul ordinii inverse. |
| F054 / DS.2, DS.3, FINAL.10a | În Registru jurnal „Validează” e secundar; pe nota validată și pe cea la validare nu mai apar butoanele fără obiect; o notă manuală datată înaintea preluării cere confirmare înainte de salvare. |
| F061 / FINAL.10b | La o firmă neplătitoare de TVA, TVA-ul cheltuielilor de deplasare intră în cheltuială (625), nu în 4426. |
| F070 / FINAL.6 | „Salvează” pe o denumire care există spune asta fără să adauge produsul; temeiul cotei rămâne pe rând, întreg; cu formularul deschis o singură principală. |
| F073 / FISC.6 | Alocarea încasărilor nu mai propune factura emisă pe bon (încasată la casa de marcat). |
| F080, F087 / DS.2, DS.8 | „Contabilizează statul” e acțiunea principală a statului; calculul salarial și repartizarea CAM 113/157 dau totalurile scenariului (12.000 / 270 / 12.270). |
| F085 / STOC.5 | Scadențele documentate rămân: facturile 66 și 71 „fără scadență în sistem”, fără termen inventat pe FB-7. |
| F089 / STOC.1, DS.2 | Ieșirea se judecă față de stocul de la data ei, refuzul spune cantitatea disponibilă atunci, fișa nu mai cade cu 500, iar „Mișcări” are o singură principală. |
| F118 / FINAL.7 | Închidere lună arată istoricul perioadei: cine a blocat / deblocat, când și cu ce motiv. |
| F126 / DS.3 | Pe factura acceptată în SPV „Trimite în SPV” nu mai apare; cât e la ANAF stă inactiv cu motiv. |
| F162, F169 / FISC.7 | Verdictul „coincid” arată cifrele ambelor părți. |
| F172 / DS.5, STOC.6 | Citatul „Nu, doar factură” se închide cu ghilimeaua românească, iar răspunsul la „Pleacă marfa acum?” nu se mai reia dintr-o ciornă de altă dată. |
| F176 / DS.6, FINAL.8 | Fereastra firmei numește emitentul certificatului SPV, iar sumarul firmelor fără drept e un semnal scurt cu detaliile pliate. |
| F183 / FINAL.9 | Fiecare divergență din auditul de preluare are butonul spre pasul de import care o repară. |
| F011 / FINAL.1 | Mesajul de după importul extrasului numără ca cipul și spune câte dintre liniile fără potrivire sunt operațiuni ale băncii. |
| F254 / FISC.5 | Fișa facturii pe bon spune „emisă pe baza bonului fiscal”, nu o arată „de preluat” și nu cere notă; D300 nu o numără a doua oară. |
| DS.1 | Sub 700 px tabelul cu coloane strivite devine stivă de rânduri cu etichete. |
| DS.7 | Grupul «Datorate înainte de preluarea în iConta.eu» rămâne desfăcut la intrare, iar „Continuă →” se vede după selecție. |
