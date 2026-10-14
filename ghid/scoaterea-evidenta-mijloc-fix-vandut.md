---
title: "Cum se face scoaterea din evidență a unui mijloc fix vândut"
description: "iConta.eu nu are un flux dedicat de vânzare a mijlocului fix — doar casare și reevaluare; la vânzare, valoarea rămasă din registru e punctul de plecare, iar restul se tratează manual."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum se face scoaterea din evidență a unui mijloc fix vândut

Important de clarificat de la început: vânzarea unui mijloc fix nu e același lucru cu casarea lui, iar registrul din iConta.eu tratează explicit doar casarea și reevaluarea.

## Temeiul legal

::: ghid-temei
„Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)."
— Codul fiscal (Legea 227/2015), art. 28 alin. (17) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

Legea tratează vânzarea și scoaterea din funcțiune sub aceeași regulă de calcul: rezultatul se determină pornind de la valoarea fiscală a activului, diminuată cu amortizarea fiscală înregistrată — adică exact valoarea rămasă (net book value) pe care o calculează registrul. Aceeași formulă de calcul nu înseamnă însă că cele două operațiuni se tratează identic în evidență: casarea e o scoatere din uz, vânzarea e un transfer către un terț.

## Ce se greșește în practică

Se folosește acțiunea "Casează" din registru pentru un activ care de fapt a fost vândut — rezultă o notă de casare (cu procesul-verbal al comisiei de casare ca document), nepotrivită pentru o vânzare. Sau se așteaptă ca butonul "Casează" să acopere și cazul unei vânzări, sau se calculează manual valoarea rămasă fără să se folosească amortizarea la zi calculată corect pe metoda reală a activului.

## Ce face iConta.eu

Ecranul de mijloace fixe are în interfață doar două acțiuni pe rând activ — **Casează** și **Reevaluează** — niciuna gândită pentru vânzare. Registrul poate însă calcula oricând, pe metoda reală a activului, valoarea rămasă la o dată dată (același calcul folosit la casare). Contabilul preia această valoare rămasă din coloana "rămas" a registrului pentru a determina rezultatul vânzării, dar înregistrarea propriu-zisă a vânzării și scoaterea din evidență a activului vândut nu sunt automatizate — spre deosebire de casare, care generează automat o notă și dezactivează activul. Pentru un activ vândut, aplicația nu îl dezactivează automat; contabilul tratează separat, manual, atât scoaterea din evidență, cât și înregistrarea vânzării.

[iConta.eu](/)
