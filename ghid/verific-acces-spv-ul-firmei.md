---
title: Cum verific cine are acces la SPV-ul firmei?
description: iConta nu listează utilizatorii cu acces la SPV-ul unei firme — administrarea persoanelor autorizate (reprezentant legal, desemnat sau împuternicit) se face exclusiv în portalul ANAF. iConta verifică doar dacă propria conexiune OAuth acoperă un anumit CIF.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific cine are acces la SPV-ul firmei?

Trebuie spus onest de la început: iConta nu are o funcție care să listeze persoanele cu acces la Spațiul Privat Virtual (SPV) al unei firme. Administrarea utilizatorilor SPV — cine e reprezentant legal, reprezentant desemnat sau împuternicit — se face exclusiv în portalul ANAF, în afara oricărei aplicații de contabilitate.

## Temeiul legal

::: ghid-temei
"Persoanele juridice sau alte entităţi fără personalitate juridică se pot identifica în mediul electronic astfel: a) cu certificatul calificat al persoanei juridice [...]; b) cu certificatul calificat deţinut de persoana fizică reprezentant legal [...]; c) cu certificatul calificat deţinut de reprezentantul desemnat [...]; d) cu certificatul calificat deţinut de **împuternicitul** persoanei juridice [...]." — OMFP 660/2017, art. 15 alin. (1)

"Utilizarea SPV prin împuternicit sau prin reprezentantul desemnat este posibilă dacă îndeplineşte, cumulativ, următoarele condiţii: a) împuternicirea sau mandatul de reprezentare este **generală/general** pentru toate operaţiunile din SPV; b) împuternicirea sau mandatul de reprezentare conţine acordul cu privire la accesul la informaţiile referitoare la **istoricul acţiunilor anterioare** din SPV al persoanei reprezentate [...]." — OMFP 660/2017, art. 15 alin. (9)

Revocarea: "Persoana fizică/Reprezentantul legal al unei persoane juridice [...] care este înregistrată ca utilizator SPV [...] poate solicita revocarea calităţii de: a) împuternicit al său [...]; b) reprezentant desemnat al său [...]" — iar cererea de revocare "cuprinde următoarele informaţii obligatorii: a) datele de identificare ale persoanei revocate; b) calitatea de împuternicit sau reprezentant desemnat, după caz." — OMFP 660/2017, art. 18 alin. (1), (3)
:::

Procedura de acces la SPV pentru o persoană juridică — cine poate fi reprezentant legal, reprezentant desemnat sau împuternicit, cum se aprobă și cum se revocă o astfel de calitate — e reglementată integral de OMFP 660/2017, art. 15-19. Cererea de înregistrare ca utilizator SPV se depune prin aplicația informatică dedicată a ANAF; aprobarea se face automat, dacă datele se verifică, sau la ghișeu, dacă nu. Revocarea unei împuterniciri se face tot prin SPV, nu prin nicio aplicație terță.

## Ce se greșește în practică

Cea mai frecventă greșeală e presupunerea că o aplicație de contabilitate, odată conectată la SPV, poate arăta „cine mai are acces" — nicio aplicație terță nu are vizibilitate asupra listei complete de utilizatori SPV ai unei firme; acea informație există doar în portalul ANAF, pentru cei care au deja calitatea de a o vedea acolo (de regulă reprezentantul legal).

## Ce face iConta.eu

Aici trebuie o precizare onestă a limitei aplicației: iConta **nu** listează utilizatorii cu acces SPV ai unei firme. Singurul lucru pe care aplicația îl poate verifica e dacă *propria conexiune OAuth conectată în iConta* (certificatul calificat al cabinetului, autorizat prin Setări → Conectare SPV) acoperă un anumit CIF — adică dacă acel certificat are drept de e-Factura/e-Transport pe firma respectivă. Această verificare e empirică: se face printr-un apel de test către ANAF pentru CIF-ul respectiv, iar rezultatul ("are drept" sau nu) se citește din conținutul răspunsului ANAF, nu dintr-un cod de eroare HTTP.

Această verificare răspunde la o întrebare diferită de titlul de mai sus — „acoperă certificatul conectat în iConta acest CIF?", nu „ce persoane au acces la SPV-ul firmei". Pentru a afla exact cine (ce persoane, cu ce calitate) are acces la SPV-ul unei firme, verificarea trebuie făcută direct în portalul ANAF SPV, secțiunea de administrare a utilizatorilor — în afara iConta.

[iConta.eu](/)
