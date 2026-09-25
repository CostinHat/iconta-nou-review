---
title: "Ce fac dacă am uitat să întocmesc NIR-ul?"
description: "Când este obligatorie Nota de recepție și constatare de diferențe (NIR) și cum se rezolvă situația în care recepția unor bunuri a rămas neînregistrată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am uitat să întocmesc NIR-ul?

NIR-ul (Nota de recepție și constatare de diferențe) e documentul standard prin care se confirmă intrarea în gestiune a unor bunuri. Vestea bună: NIR-ul nu e obligatoriu în toate cazurile — legea prevede explicit situațiile în care e necesar. Dacă bunurile intră într-una din aceste situații și NIR-ul chiar lipsește, el trebuie întocmit ulterior, cât mai aproape de data reală a recepției, pentru ca înregistrarea în gestiune și în contabilitate să aibă un document justificativ corect.

## Temeiul legal

::: ghid-temei
„(Cod 14-3-1A) Nota de recepție și constatare de diferențe (NIR) servește ca: - document pentru recepția bunurilor aprovizionate; - document justificativ pentru încărcare în gestiune; - document justificativ de înregistrare în contabilitate. Nota de recepție și constatare de diferențe se folosește ca document de recepție obligatoriu numai în cazul: - bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; - bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; - bunurilor materiale procurate de la persoane fizice; - bunurilor materiale care sosesc neînsoțite de documente de livrare; - bunurilor materiale care prezintă diferențe la recepție; - mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare. În cazurile în care nu este obligatorie întocmirea NIR-ului, recepția și încărcarea în gestiune, după caz, și înregistrarea în contabilitate se fac pe baza documentului de livrare care însoțește transportul (factura, avizul de însoțire a mărfii etc.)."
— OMFP nr. 2634/2015, anexa 2, norme specifice (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

- NIR-ul e obligatoriu doar în șase situații explicite: gestiuni diferite pe aceeași factură/aviz, bunuri primite în custodie/prelucrare, achiziții de la persoane fizice, bunuri sosite fără documente de livrare, bunuri cu diferențe la recepție, sau mărfuri în gestiuni la preț de vânzare.
- Dacă niciuna dintre aceste situații nu se aplică, recepția și înregistrarea în contabilitate se pot face direct pe baza documentului de livrare (factura sau avizul de însoțire) — fără NIR.
- Dacă bunurile sosesc în tranșe, „se întocmește câte un formular pentru fiecare tranșă, care se anexează apoi la factură sau la avizul de însoțire a mărfii".
- Dacă la recepție se constată diferențe, entitatea trebuie să stabilească prin proceduri proprii ce informații se înscriu în NIR (cantități/valori constatate în plus sau minus, persoanele care au făcut recepția etc.).

## Ce se greșește în practică

- Se presupune că NIR-ul e obligatoriu întotdeauna, pentru orice recepție de marfă, deși legea îl cere explicit doar în cele șase situații de mai sus.
- Se descoperă lipsa NIR-ului abia la inventar sau la control, moment în care reconstituirea datei și circumstanțelor reale ale recepției devine dificilă.
- Nu se întocmește NIR pentru achizițiile de la persoane fizice (unde e obligatoriu prin lege), considerându-se suficientă doar chitanța sau borderoul de achiziție.
- Se ignoră diferențele constatate la recepție (cantitativ sau valoric) și nu se documentează corect prin NIR, deși aceasta e una din situațiile explicit obligatorii.

## Ce face iConta.eu

Recepția și gestiunea stocurilor din iConta.eu au module dedicate (`stocuri.py`, `stocuri_api.py`), care generează NIR-ul din liniile de recepție (cantitate, preț de achiziție, cotă TVA), inclusiv pentru gestiuni la preț de vânzare (cu adaos comercial și TVA neexigibilă). Dacă un NIR a fost omis pentru o recepție care necesită unul, corectarea presupune completarea lui ulterioară, cu datele reale ale recepției — aplicația nu are, la acest moment, o funcție separată de „recuperare automată" a NIR-urilor lipsă pentru recepții deja vechi; NIR-ul se creează normal, oricând, pe baza documentelor de livrare păstrate.

[iConta.eu](/)
