---
title: "Cum se raportează NIR-urile în SAF-T (D406)"
description: "Ce este Nota de recepție și constatare de diferențe, când e obligatorie și cum ajunge ea, de fapt, în fișierul standard de control fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează NIR-urile în SAF-T (D406)

Nota de recepție și constatare de diferențe (NIR) e documentul cu care mărfurile și materialele intră oficial în gestiune. Contabilii care pregătesc SAF-T (declarația D406) caută adesea un câmp „NIR" în structura fișierului — dar SAF-T nu raportează formulare, ci operațiuni economice. Trebuie înțeles ce anume din NIR ajunge efectiv în declarație și de ce.

## Temeiul legal

::: ghid-temei
„ART. 59^1 Obligația de depunere a fișierului standard de control fiscal
(1) Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fișierul standard de control fiscal."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 59^1 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„(Cod 14-3-1A) Nota de recepție și constatare de diferențe (NIR) servește ca: document pentru recepția bunurilor aprovizionate; document justificativ pentru încărcare în gestiune; document justificativ de înregistrare în contabilitate. [...] se folosește ca document de recepție obligatoriu numai în cazul: bunurilor materiale cuprinse într-o factură sau aviz de însoțire a mărfii, care fac parte din gestiuni diferite; bunurilor materiale primite spre prelucrare, în custodie sau în păstrare; bunurilor materiale procurate de la persoane fizice; bunurilor materiale care sosesc neînsoțite de documente de livrare; bunurilor materiale care prezintă diferențe la recepție; mărfurilor intrate în gestiunile la care evidența se ține la preț de vânzare."
— OMFP nr. 2634/2015, Anexa 2, Grupa a III-a, Cod 14-3-1A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Din combinarea celor două texte rezultă mecanismul real:

- **NIR-ul e document justificativ de recepție**, obligatoriu doar în situațiile enumerate explicit (mărfuri din gestiuni diferite pe aceeași factură, bunuri primite spre prelucrare/custodie/păstrare, bunuri de la persoane fizice, bunuri fără document de livrare, diferențe la recepție, mărfuri la preț de vânzare). În celelalte cazuri, recepția și înregistrarea în contabilitate se fac direct pe baza facturii sau avizului de însoțire.
- **SAF-T nu are un câmp dedicat „NIR".** Fișierul standard de control fiscal (art. 59^1 din Codul de procedură fiscală) cere raportarea informațiilor din evidența contabilă și fiscală — adică înregistrările contabile rezultate (intrări de stoc, jurnalul de cumpărări, mișcările de gestiune), nu formularul-sursă în sine.
- **Diferențele constatate la recepție** (plus/minus față de document) sunt exact motivul pentru care NIR-ul devine obligatoriu — și tot aceste diferențe sunt cele care trebuie să se regăsească în valorile de intrare raportate în contabilitate, deci indirect în SAF-T.

## Ce se greșește în practică

- Se caută în structura XSD a D406 o secțiune „NIR" sau „14-3-1A" — nu există; ce se raportează e rezultatul contabil al recepției, nu formularul.
- Se emite NIR pentru orice marfă intrată, deși legea îl cere obligatoriu doar în cazurile enumerate — restul se pot recepționa direct pe bază de factură/aviz.
- Se ignoră diferențele constatate la recepție în valoarea înregistrată în gestiune, deși tocmai acestea sunt motivul pentru care norma cere un document distinct de constatare.

## Ce face iConta.eu

iConta.eu generează declarația D406/SAF-T din datele contabile deja înregistrate (facturi de achiziție, mișcări de stoc), conform structurii impuse de ANAF — modulele `core/d406.py`, `core/d406_active.py` și `core/d406_stocuri.py` din aplicație construiesc fișierul pornind de la aceste înregistrări. Aplicația nu are un formular separat de „Notă de recepție și constatare de diferențe" care să fie completat manual pentru fiecare intrare de marfă; recepția se reflectă prin înregistrarea facturii/avizului și, dacă apar diferențe cantitative sau valorice, prin corectarea directă a intrării de stoc.

[iConta.eu](/)
