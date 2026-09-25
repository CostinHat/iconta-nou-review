---
title: "Cine plătește primele zile de concediu medical?"
description: "Regula legală privind cine suportă indemnizația de concediu medical — angajatorul sau FNUASS — pe zile, inclusiv excepția pentru izolare, și cum o aplică motorul de calcul din iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cine plătește primele zile de concediu medical?

Indemnizația de concediu medical nu e suportată integral de casa de sănătate. Pentru boala obișnuită, primele zile cad în sarcina angajatorului, iar restul perioadei — din bugetul Fondului național unic de asigurări sociale de sănătate (FNUASS). Legea prevede însă și excepții explicite de la această împărțire, cea mai importantă fiind izolarea.

## Temeiul legal

::: ghid-temei
„Indemnizațiile pentru incapacitate temporară de muncă se suportă după cum urmează: A. de către angajator, din prima zi până în a 5-a zi de incapacitate temporară de muncă, cu excepția indemnizațiilor aferente certificatelor de concediu medical acordate persoanelor asigurate pentru care a fost instituită măsura izolării, potrivit Legii nr. 136/2020; B. din bugetul Fondului național unic de asigurări sociale de sănătate, începând cu: a) ziua următoare celor suportate de angajator, conform lit. A [...]; [...] c) prima zi de incapacitate temporară de muncă, în cazul persoanelor asigurate pentru care a fost instituită măsura izolării, potrivit Legii nr. 136/2020."
— OUG 158/2005, art. 12 (sursă: anaf_surse/oug_158_2005_consolidat.txt)
:::

Regula, pe scurt:

- **Zilele 1–5** de incapacitate temporară de muncă (boală obișnuită) le suportă **angajatorul**.
- **Din ziua a 6-a** până la încetarea incapacității, plata trece în sarcina **FNUASS**.
- **Excepția explicită**: pentru certificatele acordate persoanelor aflate sub măsura izolării (Legea 136/2020), angajatorul **nu suportă nimic** — FNUASS plătește integral, din prima zi.
- Pentru certificatele eliberate în fereastra 1 februarie 2026 – 31 decembrie 2027 (OUG 91/2025), împărțirea zilelor se schimbă cu o zi (angajatorul suportă zilele 2–6, nu 1–5), ca urmare a diminuării generale de o zi a indemnizației.

## Ce se greșește în practică

- Se presupune că angajatorul suportă mereu primele 5 zile, fără să se verifice dacă certificatul e pentru izolare — caz în care legea exceptează explicit angajatorul de la orice plată.
- Se aplică regula clasică (zilele 1–5 angajator) și pentru certificatele din fereastra de diminuare 2026–2027, unde intervalul real e zilele 2–6.
- Se confundă izolarea (Legea 136/2020, suportată integral de FNUASS) cu carantina obișnuită sau cu alte coduri de indemnizație suportate parțial de angajator.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`) împarte automat zilele plătite între angajator și FNUASS și întoarce direct, pentru fiecare certificat, zilele și sumele pe fiecare sursă — vizibile contabilului la introducerea certificatului în fișa salariatului.

O eroare reală, verificată în cod: pentru certificatele cu codul de **izolare**, aplicația alocă în continuare o porțiune din indemnizație în sarcina angajatorului (până la 5 zile), deși legea, citată mai sus, exceptează explicit izolarea de la regula generală și cere ca FNUASS să suporte totul din prima zi. Sursa erorii pare să fie faptul că lista internă de coduri „suportate integral din FNUASS" a fost construită după structura declarației D112, care nu include separat codul de izolare în acea listă, fără o verificare încrucișată cu textul art. 12 din OUG 158/2005. Pentru certificatele de izolare, verificați manual, până la corectare, că suma reținută ca fiind „în sarcina angajatorului" e de fapt zero.

[iConta.eu](/)
