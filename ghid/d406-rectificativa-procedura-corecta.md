---
title: "D406 rectificativă: procedura corectă"
description: "Regula ANAF pentru corectarea unei Declarații informative D406: fișier SAF-T integral retransmis, niciodată corecții selective pe înregistrări sau câmpuri."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D406 rectificativă: procedura corectă

Spre deosebire de alte declarații care permit corecții punctuale, Declarația informativă D406 (SAF-T) are o regulă de rectificare rigidă și explicită: corecția se face **exclusiv** prin retransmiterea întregului fișier SAF-T, refăcut corect. Legea interzice expres transmiterea selectivă a doar înregistrărilor sau câmpurilor greșite.

## Temeiul legal

::: ghid-temei
„11. Pentru declaraţia informativă D406 transmisă cu erori identificate de Agenţia Naţională de Administrare Fiscală şi pentru care a fost comunicată recipisa ce le semnalează, contribuabilul retransmite integral Declaraţia informativă D406, care trebuie să cuprindă fişierul SAF-T corectat.
12. Nu este admisă transmiterea unor corecţii parţiale prin transmiterea selectivă a înregistrărilor sau câmpurilor corectate pentru Declaraţia informativă D406 anterior transmisă şi pentru care au fost primite recipise ce semnalau erori."
— OPANAF 1783/2021, Anexa 4, pct. 11-12 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)

„6. În situaţia în care contribuabilul constată anumite erori în declaraţia depusă iniţial, acesta poate depune declaraţii rectificative."
— OPANAF 1783/2021, Anexa 4, pct. 6 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Procedura corectă, rezultată direct din text:

1. **Nu se corectează „pe bucăți".** Indiferent dacă greșeala e o singură factură mapată greșit sau un cod de taxă eronat pe zece linii, corecția tot fișierul SAF-T o cere — pct. 12 exclude explicit orice transmitere selectivă.
2. **Sursa corecției poate fi voluntară sau impusă.** Fie contribuabilul găsește singur eroarea (pct. 6, oricând, din proprie inițiativă), fie ANAF o semnalează printr-o recipisă (pct. 11) — în al doilea caz, retransmiterea integrală e obligatorie ca răspuns la acea recipisă.
3. **Fișierul retransmis înlocuiește, nu completează.** Rectificativa D406 e o depunere nouă, completă — nu un „diff" aplicat peste cea veche.

## Ce se greșește în practică

- Se pregătește un fișier SAF-T care conține doar tranzacțiile/înregistrările corectate, presupunând că sistemul ANAF le va „îmbina" cu declarația inițială — practică interzisă explicit (pct. 12).
- Se tratează o recipisă de eroare de la ANAF ca pe o simplă informare, fără să se declanșeze efectiv procedura de retransmitere integrală descrisă la pct. 11.
- Se amână corectarea unei erori descoperite intern, așteptând ca ANAF s-o semnaleze — deși pct. 6 permite (și, practic, recomandă) corectarea din proprie inițiativă, imediat ce eroarea e constatată.

## Ce face iConta.eu

Aplicația nu are un flux separat, dedicat, pentru „rectificativă D406" — codul modulului D406 nu conține niciun concept de corecție sau versiune rectificativă distinctă de o depunere obișnuită. O redepunere D406 pentru aceeași perioadă urmează fluxul generic valabil pentru orice declarație: generare, coadă de aprobare, depunere — regenerarea produce, de fiecare dată, fișierul SAF-T complet pentru perioada respectivă (nu un fișier parțial), ceea ce e conform structural cu cerința legală de la pct. 11-12, chiar dacă aplicația nu are o etichetă sau un ecran specific de „rectificativă SAF-T".

La nivel de bază de date, fiecare depunere (inclusiv o redepunere pentru aceeași lună) primește un număr de versiune propriu și e păstrată distinct de cea anterioară, fără suprascriere — astfel încât istoricul depunerilor succesive pentru o perioadă rămâne disponibil intern. Aplicația nu verifică însă automat dacă fișierul retransmis corectează efectiv problema semnalată de ANAF prin recipisă — corespondența dintre eroarea semnalată și conținutul corectat rămâne responsabilitatea contabilului.

[iConta.eu](/)
