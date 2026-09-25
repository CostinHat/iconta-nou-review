---
title: "Diferențe între casa de marcat și registrul de casă"
description: "Rolul distinct al aparatului de marcat electronic fiscal și al registrului de casă, conform OUG 28/1999 și OMFP 2634/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Diferențe între casa de marcat și registrul de casă

Cele două se confundă des, mai ales în firmele mici, pentru că amândouă au legătură cu numerarul. Rolul lor e însă complet diferit: una e un aparat fiscal reglementat separat, cealaltă e un registru contabil.

## Temeiul legal

::: ghid-temei
„(1) Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale. (2) Operatorii economici prevăzuți la alin. (1) [...] au obligația să emită bonuri fiscale cu aparate de marcat electronice fiscale și să le înmâneze clienților."
— OUG 28/1999, art. 1 alin. (1)-(2) (sursă: anaf_surse/oug_28_1999.html)

„REGISTRUL DE CASĂ (Cod 14-4-7A [...]) [...] servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP 2634/2015, Anexa 2, Cod 14-4-7A (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Diferența, punct cu punct:

- **Aparatul de marcat electronic fiscal (AMEF)** e un dispozitiv fizic reglementat de OUG 28/1999: obligatoriu la vânzarea cu amănuntul/prestări către populație, autorizat prin distribuitori, cu memorie fiscală supravegheată de ANAF. Rolul lui e să emită **bonul fiscal** și să genereze **raportul de închidere zilnică**.
- **Registrul de casă** e un document contabil reglementat de OMFP 2634/2015: ține evidența **tuturor** încasărilor și plăților în numerar prin casieria entității (nu doar cele de la AMEF), stabilește **soldul de casă** zilnic și e baza înregistrării în contabilitate a operațiunilor de casă.
- Un magazin cu AMEF are ambele documente, dar cu funcții complementare: sumele din raportul Z al aparatului **alimentează** registrul de casă ca o singură linie zilnică de încasări, alături de eventuale alte mișcări de numerar (plăți către furnizori, avansuri, depuneri la bancă) care nu trec deloc prin AMEF.
- O firmă fără obligație de AMEF (fără vânzări cu amănuntul către populație) poate avea registru de casă fără să aibă niciodată casă de marcat.

## Ce se greșește în practică

- Se confundă soldul de casă din registru cu banii "din casa de marcat" — registrul de casă include și plăți/încasări care nu trec deloc prin aparat (avansuri, achitări cash de facturi între firme).
- Se renunță la registrul de casă pe motiv că "există raportul Z" — raportul Z acoperă doar încasările prin AMEF, nu toate mișcările de numerar ale firmei.
- Se așteaptă ca cele două solduri (numerar fizic din sertarul casei de marcat vs. sold din registrul de casă) să coincidă automat, fără nicio reconciliere — coincid doar dacă toate mișcările de numerar sunt corect înregistrate în ambele.

## Ce face iConta.eu

La data acestui ghid, iConta.eu tratează cele două fluxuri prin module separate, coerent cu distincția legală: `core/amef_import.py` (`parseaza_raport_z()`) pentru citirea raportului fiscal al aparatului de marcat — din care `core/uc_tenants.py` (`horeca_import_amef()`) generează automat o notă contabilă zilnică (5311/5125 = 707 + TVA pe 4427) — și `core/casa.py` (`registru_casa()`, `sold_final()`) pentru registrul de casă propriu-zis, care ține soldul rulant al operațiunilor de numerar introduse manual (încasare client, plată furnizor, ridicare/depunere bancă, avans). Cele două fluxuri rămân, la acest moment, separate: nota generată din raportul Z nu intră și în `registru_casa()` ca o linie de operațiune, deci soldul de casă din registru și suma din raportul Z se urmăresc azi ca fluxuri distincte, nu unul integrat automat în celălalt.

[iConta.eu](/)
