---
title: "De ce apare diferență între statul de salarii și contul 421?"
description: "Contul 421 reflectă drepturile salariale datorate, nu doar salariul net de plată — diferențele apar frecvent din avansuri, rețineri sau sume neridicate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# De ce apare diferență între statul de salarii și contul 421?

Contabilii verifică des soldul contului 421 „Personal — salarii datorate" în raport cu totalurile din statul de plată și găsesc diferențe pe care nu le înțeleg imediat. Explicația e în felul în care funcționează acest cont: el nu ține doar evidența „netului de plată", ci a tuturor drepturilor salariale brute, din care se scad apoi reținerile.

## Temeiul legal

::: ghid-temei
„Cu ajutorul acestui cont se ține evidența decontărilor cu personalul pentru drepturile salariale cuvenite acestuia în bani sau în natură, inclusiv a sporurilor, adaosurilor, premiilor din fondul de salarii etc. Contul 421 «Personal - salarii datorate» este un cont de pasiv. În creditul contului 421 «Personal - salarii datorate» se înregistrează: – salariile și alte drepturi cuvenite personalului (641); [...] În debitul contului 421 «Personal - salarii datorate» se înregistrează: – rețineri din salarii reprezentând avansuri acordate personalului, sume opozabile salariaților datorate terților, contribuția pentru asigurări sociale, contribuția pentru ajutorul de șomaj, garanții, impozitul pe salarii, precum și alte rețineri datorate (425, 427, 431, 437, 428, 444); [...] – drepturi de personal neridicate (426); – salariile nete achitate personalului (512, 531)."
— OMFP 1.802/2014, Reglementările contabile, descrierea funcțiunii contului 421 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din această descriere rezultă de ce soldul contului 421, la un moment dat, nu coincide automat cu „netul de plată" din statul de salarii al lunii curente:

- Contul 421 se creditează cu **întreaga sumă brută** cuvenită personalului (salariu, sporuri, adaosuri, prime), nu doar cu netul — soldul creditor la un moment dat reprezintă toate drepturile datorate, neachitate încă.
- Se debitează cu **toate reținerile** (avansuri acordate anterior prin contul 425, contribuții CAS/CASS, impozit, popriri către terți prin contul 427, garanții) — nu doar cu suma efectiv virată în bancă sau plătită cash.
- **Avansurile de salariu** acordate în cursul lunii (cont 425) se scad din contul 421 la data statului de plată, deci un avans plătit în avans-lună, netrecut corect prin 425, produce automat o diferență.
- **Drepturile neridicate** (cont 426) — de exemplu, salariul unui angajat care nu s-a prezentat să-l ridice cash la termen — rămân în evidență separat, ceea ce poate crea, temporar, o diferență între soldul 421 și sumele efectiv plătite din statul de plată respectiv.

## Ce se greșește în practică

- Se compară direct soldul 421 cu „netul de plată" al lunii, ignorând faptul că avansurile, popririle și garanțiile trec și ele prin acest cont, la debit.
- Se înregistrează avansul de salariu direct în debitul contului 421, la data acordării, în loc să treacă mai întâi prin contul 425 „Avansuri acordate personalului" și să se regularizeze abia la statul de plată final.
- Nu se urmărește separat contul 426 „Drepturi de personal neridicate" pentru sumele care rămân nedecontate pentru că angajatul nu s-a prezentat la plată, ceea ce lasă solduri „fantomă" în 421.
- Se compensează, informal, diferențe de rotunjire între statul de salarii și notele contabile, în loc de a identifica exact cauza (avans neînregistrat corect, reținere omisă, eroare de calcul al contribuțiilor).

## Ce face iConta.eu

iConta.eu generează automat notele contabile pentru salarizare pornind chiar de la această structură a contului 421: creditul contului reflectă salariul brut calculat (641=421), iar debitul reflectă separat contribuțiile reținute (CAS către 4315, CASS către 4316, impozit către 444) și, la final, netul plătit efectiv. Orice diferență între soldul contabil al contului 421 și statul de plată poate fi astfel urmărită direct pe liniile generate automat de motorul de salarizare, fără recalcul manual.

[iConta.eu](/)
