---
title: "Mesajele lunare din SPV despre fișierele casei de marcat: ce faci când apar erori?"
description: "ANAF trimite lunar în SPV mesaje despre fișierele cu probleme transmise de casa de marcat. Când apar erori, firma anunță imediat service-ul și se asigură că aparatul transmite din nou corect."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Mesajele lunare din SPV despre fișierele casei de marcat: ce faci când apar erori?

ANAF trimite lunar, în Spațiul Privat Virtual al firmei, mesaje despre eventualele disfuncționalități ale fișierelor transmise de casa de marcat. Ordinul nu prevede o procedură de răspuns la aceste mesaje. Când apare o eroare, firma își aplică obligațiile pe care le are deja din OUG 28/1999: **anunță imediat service-ul**, lasă intervenția doar pe seama persoanelor autorizate și se asigură că aparatul ajunge din nou să transmită corect.

Mesajul lunar este, practic, singurul semnal oficial că datele nu ajung corect la ANAF. Dacă nimeni nu citește SPV-ul firmei, problema iese la iveală abia la control.

## Temeiul legal

::: ghid-temei
„Lunar, Agenția Națională de Administrare Fiscală transmite către operatorii economici utilizatori de aparate de marcat electronice fiscale, prin intermediul serviciului „Spațiul Privat Virtual“, mesaje despre eventualele disfuncționalități privind fișierele transmise de la aparatele de marcat electronice fiscale către sistemul informatic."
— OPANAF 435/2021, art. 2 alin. (2) (sursă: anaf_surse/ordin_435_2021.html)
:::

::: ghid-temei
„În situația defectării aparatelor de marcat electronice fiscale utilizatorii sunt obligați ca, în momentul constatării defecțiunii, să anunțe distribuitorul autorizat care a livrat aparatul sau, după caz, unitatea acreditată pentru service a acestui distribuitor autorizat."
— OUG 28/1999, art. 1 alin. (6) (sursă: anaf_surse/oug_28_1999.html)

„e) să asigure funcționarea aparatului de marcat electronic fiscal în parametrii tehnici legali, pe toată durata de utilizare a acestuia; ... f) să permită intervenția tehnică numai a persoanelor autorizate pentru efectuarea operațiunilor de service asupra aparatului de marcat electronic fiscal;"
— OUG 28/1999, art. 4 alin. (12) lit. e) și f) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce faci, în ordine, când mesajul semnalează probleme:

1. **Identifici aparatul și perioada.** Compari mesajul cu rapoartele Z din evidență. Lipsesc zile? Numerele de ordine au goluri? Rapoartele Z sunt numerotate progresiv (art. 4 alin. (6) din OUG 28/1999), deci golurile se văd ușor.
2. **Anunți service-ul în modul convenit prin contract.** Notificarea făcută altfel decât au stabilit părțile nu este valabilă (art. 1 alin. (8^1)). Păstrezi dovada trimiterii.
3. **Lași intervenția doar tehnicianului autorizat** (art. 4 alin. (12) lit. f)). Nu reinstalați și nu resetați aparatul cu personal propriu.
4. **Dacă aparatul s-a defectat,** până la repunerea în funcțiune înregistrezi operațiunile în registrul special și emiți chitanțe (art. 1 alin. (8)).
5. **Dacă aparatul lucrează offline,** verifici dacă fișierele zilelor fiscale încheiate au fost exportate și depuse. Potrivit OPANAF 146/2018, anexa 2, aparatul cu obligație de transmitere își poate bloca emiterea bonurilor la atingerea termenului, iar deblocarea vine după transmiterea datelor.

Ce riscă firma dacă ignoră problema:

- **Neasigurarea conectării** (art. 10 lit. ff)): amendă de la 8.000 la 10.000 lei (art. 11 alin. (1) lit. l)).
- **Neanunțarea defecțiunii** (art. 10 lit. i)): amendă de la 2.000 la 4.000 lei (art. 11 alin. (1) lit. a)).
- **Nerespectarea art. 4 alin. (12) lit. e) sau f)** (art. 10 lit. u)): amendă de la 4.000 la 6.000 lei (art. 11 alin. (1) lit. b)).

Mesajul din SPV nu este, prin el însuși, un proces-verbal sau o decizie de impunere. Este însă o dovadă că firma a fost informată, iar la un control ulterior va fi greu de susținut că nu a știut de problemă.

::: ghid-exemplu
SC Exemplu SRL are două case de marcat. În mesajul lunar primit în SPV la începutul lui mai 2026 apare că aparatul de la punctul de lucru 2 nu a transmis datele din 14–17 aprilie 2026.

Contabilul verifică evidența. Rapoartele Z 0215–0218 există pe hârtie, dar seria din fișierele importate sare de la 0214 la 0219. Administratorul trimite notificarea prin e-mail, modalitatea prevăzută în contractul de service, și păstrează mesajul trimis. Tehnicianul remediază defecțiunea de comunicație. Contabilul arhivează mesajul SPV, notificarea și documentul de intervenție, apoi verifică în mesajul lunar următor că problema nu mai apare.
:::

## Ce se greșește în practică

- Nimeni nu urmărește SPV-ul firmei pentru mesajele despre casa de marcat, iar problema se descoperă la control.
- Defecțiunea se anunță telefonic, fără dovadă și altfel decât prevede contractul de service.
- Personalul propriu repornește sau reconfigurează aparatul, deși intervenția e permisă numai persoanelor autorizate.
- Se presupune că, dacă bonurile se tipăresc, totul e în regulă. Mesajul ANAF privește fișierele transmise, nu tipărirea.

## Ce face iConta.eu

iConta.eu nu citește mesajele din SPV ale firmelor. Monitorizarea lor automată nu este disponibilă, așa că mesajele lunare rămân de verificat de contabil sau de firmă, direct în SPV. Aplicația ajută la partea de evidență: importă rapoartele Z din fișierele exportate de aparat (XML sau .p7b), reține pentru fiecare numărul aparatului și numărul raportului și refuză un raport deja înregistrat. Aplicația nu semnalează automat golurile din serie; contabilul le verifică în lista notelor importate.

[iConta.eu](/)
