---
title: Cum optimizez generarea SAF-T lunar
description: SAF-T se depune integral la fiecare raportare, fără corecții parțiale — orice eroare descoperită după transmitere cere retransmiterea completă a fișierului, ceea ce face din reconcilierea prealabilă singura optimizare care contează cu adevărat.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum optimizez generarea SAF-T lunar

„Optimizarea" generării SAF-T nu înseamnă neapărat viteză de generare — mecanismul legal al declarației D406 face ca o reconciliere temeinică, făcută o singură dată corect, să fie mult mai eficientă decât corectarea ulterioară a erorilor.

### De ce corecțiile parțiale nu sunt o opțiune

OPANAF nr. 1783/2021 exclude explicit corectarea parțială a unei declarații D406 deja transmise:

> „11. Pentru declaraţia informativă D406 transmisă cu erori identificate de Agenţia Naţională de Administrare Fiscală şi pentru care a fost comunicată recipisa ce le semnalează, contribuabilul retransmite integral Declaraţia informativă D406, care trebuie să cuprindă fişierul SAF-T corectat. 12. Nu este admisă transmiterea unor corecţii parţiale prin transmiterea selectivă a înregistrărilor sau câmpurilor corectate pentru Declaraţia informativă D406 anterior transmisă şi pentru care au fost primite recipise ce semnalau erori."

Practic: dacă generezi SAF-T fără verificare prealabilă și primești erori de la ANAF, nu poți retrimite doar câmpurile greșite — trebuie regenerat și retransmis fișierul integral. Costul unei erori nedescoperite la timp e mult mai mare decât timpul investit în reconciliere înainte de depunere.

### Termenul de generare — cât timp ai efectiv

OPANAF nr. 1783/2021 fixează fereastra de transmitere:

> „13. Transmiterea Declaraţiei informative D406 se poate face de către contribuabilii/plătitorii cu obligaţia de depunere, începând cu prima zi calendaristică a lunii următoare perioadei pentru care obligaţia devine activă, până la data-limită de depunere - ultima zi a lunii care urmează perioadei pentru care se face raportarea."

Ai practic o lună întreagă calendaristică pentru generarea, verificarea și transmiterea fișierului — nu e o fereastră îngustă care justifică graba în detrimentul verificării.

### Unde apar cel mai frecvent erorile care obligă la retransmitere integrală

| Sursă tipică de eroare | Cum se previne |
|---|---|
| Divergențe între jurnalele de TVA și SAF-T | Reconciliere cu D300 înainte de generare, nu după |
| Coduri de partener/client incomplete sau inconsistente | Verificare a nomenclatoarelor interne înainte de export |
| Secțiuni goale generate incorect (în loc de secțiuni auto-închise, gol corect) | Validare cu instrumentul oficial înainte de transmitere |
| Date dintr-o lună fără activitate | Raportare „pe zero", nu omiterea completă a perioadei |

### Fișierele mari — segmentare, nu omitere

Pentru volume mari de date, OPANAF nr. 1783/2021 prevede împărțirea declarației pe segmente atunci când dimensiunea depășește limita platformei de încărcare — nu omiterea unor secțiuni pentru a „încăpea" în limită. Informațiile trebuie transmise complet, chiar dacă necesită mai multe segmente pentru aceeași perioadă de raportare.

### Practic, pentru un flux lunar eficient

- Nu genera SAF-T din date brute netratate — pornește de la o evidență contabilă deja reconciliată cu decontul de TVA al aceleiași perioade.
- Validează fișierul cu instrumentul oficial de validare înainte de transmitere, nu doar la primirea unei recipise cu erori.
- Documentează o procedură internă recurentă (aceleași verificări, în aceeași ordine, în fiecare lună) — reduce riscul de eroare umană mai eficient decât orice ajustare tehnică ulterioară.
- Ține cont că fereastra de o lună calendaristică e suficientă pentru un ciclu complet: generare → verificare → corecție internă → transmitere.
