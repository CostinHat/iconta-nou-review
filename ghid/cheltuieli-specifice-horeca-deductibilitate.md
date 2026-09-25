---
title: "Cheltuieli specifice pentru HoReCa: deductibilitate"
description: "Ce se întâmplă fiscal cu bacșișul încasat de restaurante și baruri (CAEN 5610/5630) și când bacșișul evidențiat pe factură se tratează ca o cheltuială de protocol, cu plafon de deductibilitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cheltuieli specifice pentru HoReCa: deductibilitate

Cea mai mare parte a costurilor unui restaurant sau bar (materie primă, marfă, utilități, personal) se supune regulilor generale de deductibilitate din Codul fiscal, fără particularități HoReCa. Elementul cu adevărat specific acestui sector, introdus printr-o lege dedicată, e **bacșișul** — care nu e nici venit, nici cheltuială pentru firmă, cu o singură excepție notabilă: cazul în care e evidențiat pe factură.

## Temeiul legal

::: ghid-temei
„Prin bacșiș se înțelege orice sumă de bani oferită în mod voluntar de client, în plus față de contravaloarea bunurilor livrate sau a serviciilor prestate de către operatorii economici care desfășoară activități corespunzătoare codurilor CAEN: 5610 - «Restaurante», 5630 - «Baruri și alte activități de servire a băuturilor». [...] (9) [...] sumele provenite din încasarea bacșișului de la client de către operatorul economic nu pot fi asimilate unui element de natura veniturilor pentru acesta din urmă, iar distribuirea acestora către salariați nu poate fi asimilată unui element de natura cheltuielilor."
— Legea 376/2022, care introduce art. 2^3 în OUG 28/1999, alin. (1) și (9) (sursă: anaf_surse/legea_376_2022_modificarea_completarea_ordonantei_urgenta_guvernului.txt)
:::

Excepția relevantă pentru „deductibilitate" apare la alin. (7) al aceluiași articol: dacă bacșișul e evidențiat distinct **pe factură**, la cererea clientului, el „se înregistrează pe cheltuieli de protocol și are regimul fiscal al acestora" — deci intră sub plafonul de deductibilitate limitată din Codul fiscal:

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: a) cheltuielile de protocol în limita unei cote de 2% aplicată asupra profitului contabil la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol. În cadrul cheltuielilor de protocol se includ și cheltuielile înregistrate cu taxa pe valoarea adăugată colectată [...], pentru cadourile oferite de contribuabil, cu valoare mai mare de 100 lei."
— Codul fiscal (Legea 227/2015), art. 25 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Restul restului de costuri specifice HoReCa (materie primă, ambalaje, utilități, chirie spațiu) urmează regula generală de deductibilitate din art. 25 alin. (1) CF — „cheltuieli efectuate în scopul desfășurării activității economice" — fără un regim particular pentru sectorul HoReCa în legislația verificată.

## Ce se greșește în practică

- Se înregistrează bacșișul încasat la venituri și cel distribuit la cheltuieli, ca și cum ar fi o operațiune obișnuită de intermediere — legea interzice explicit ambele calificări (alin. (9)).
- Se aplică impozitul de 10% și plafonul de protocol de 2% simultan pe același bacșiș — cele două regimuri se exclud: traseul „încasare pe bon → distribuire la salariați" e impozitat cu 10% ca venit din alte surse al salariatului (alin. (10)), în timp ce traseul „bacșiș pe factură" merge la protocolul firmei (alin. (7)) — se confundă des cele două situații.
- Se caută un plafon special „HoReCa" pentru cheltuielile obișnuite (marfă, materie primă) — nu există un asemenea regim; ele urmează regula generală de deductibilitate a art. 25 CF.

## Ce face iConta.eu

Elementul specific HoReCa pe care iConta.eu îl implementează efectiv este **F010 — Bacșiș HoReCa** (`core/bacsis.py`), pentru traseul obișnuit: încasarea bacșișului pe bon (461=462 la încasare, 5121/5311=461) și distribuirea lui la salariați, cu reținerea automată a impozitului de 10% (`462=446`, plata netă `462=5121/5311`), rotunjit la 2 zecimale. Motorul respinge orice sumă de zero sau negativă, cu mesaj explicit.

Traseul de la alin. (7) — bacșișul evidențiat distinct pe factură, la cererea clientului, tratat ca cheltuială de protocol — **nu e implementat separat în cod**: nu există un flux dedicat care să facă legătura automată dintre acest caz și plafonul de 2% din art. 25 alin. (3) lit. a) CF. Pentru costurile obișnuite ale unui local (marfă, materie primă, utilități), iConta.eu nu are o funcționalitate dedicată de verificare a deductibilității specifice HoReCa — ele se înregistrează prin fluxurile generale de achiziții și cheltuieli ale aplicației, cu aceleași reguli fiscale ca la orice altă firmă.

[iConta.eu](/)
