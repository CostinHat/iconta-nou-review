---
title: "Cum schimb certificatul digital expirat pentru e-Factura?"
description: Nu există un buton separat de „schimbare certificat" — reconectarea SPV cu noul certificat calificat înlocuiește automat conexiunea veche. Explicăm de ce, tehnic, fiecare certificat nou înseamnă practic o nouă autorizare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum schimb certificatul digital expirat pentru e-Factura?

Certificatul calificat cu care contabilul s-a autorizat inițial la ANAF pentru SPV/e-Factura expiră, de regulă, după câțiva ani. Vestea bună: nu trebuie să cauți o funcție separată de „înlocuire certificat" — pași de la sine, refaci autorizarea SPV cu certificatul nou, exact ca prima dată.

## Temeiul legal

::: ghid-temei
„Persoanele juridice sau alte entități fără personalitate juridică se identifică electronic cu certificate calificate." — OMFP nr. 660/2017 privind aprobarea Procedurii de comunicare prin mijloace electronice de transmitere la distanță, art. 6 alin. (1)
:::

Identificarea la SPV se face prin certificatul calificat însuși, nu printr-un cont separat de „profil" pe care certificatul l-ar „alimenta". Când certificatul se schimbă (expiră, se reînnoiește, se schimbă furnizorul), practic se schimbă și mijlocul de identificare — de aici rezultă, tehnic, o nouă autorizare, nu o „actualizare" a celei vechi.

## Ce se întâmplă tehnic la reautorizare

Fiecare certificat calificat are un serial unic. Conexiunea SPV a cabinetului este legată de acest serial, nu doar de identitatea contabilului. Când reiei fluxul de autorizare SPV cu certificatul nou (același ecran, „Autorizare SPV" / „Conectare la ANAF"), aleși certificatul nou de pe token/cloud și introduci PIN-ul — exact ca la prima conectare. Rezultatul: conexiunea nouă, cu serialul noului certificat, devine cea activă, iar conexiunea veche, legată de certificatul expirat, este dezactivată automat. La un moment dat există **un singur token activ per cabinet** — nu rămân în paralel o conexiune veche „moartă" și una nouă.

Practic, nu există o rută separată de „schimbare certificat" — pentru că nu e nevoie de una: re-rularea autorizării inițiale face exact acest lucru.

## Ce se greșește în practică

- Se caută în meniu o opțiune specifică „schimbă certificatul" — nu există, pentru că nu e necesară; procedura corectă e reautorizarea SPV cu certificatul nou.
- Se așteaptă ca aplicația să continue să folosească certificatul vechi expirat „până la o resetare manuală" — de fapt, la prima încercare de comunicare cu ANAF folosind un token expirat, cererea eșuează, iar soluția e reconectarea, nu o resetare a stării interne.
- Se presupune că reconectarea cu un certificat nou ar necesita ștergerea manuală a conexiunii vechi înainte — dezactivarea conexiunii vechi e automată, la salvarea noului token.

## Ce face iConta.eu

La reluarea fluxului de autorizare SPV, iConta.eu trimite din nou contabilul către pagina de autentificare ANAF, unde acesta alege noul certificat calificat. La finalizarea cu succes, conexiunea nouă (token acces + refresh criptat) o înlocuiește pe cea legată de certificatul expirat, fără nicio acțiune manuală suplimentară de „curățare" a conexiunii vechi. Rezervă: mecanismul de autorizare/reautorizare este verificat cap-coadă în producție, dar cu certificatul administratorului platformei, care nu are drept SPV pe firme reale — fluxul complet, cu un certificat de cabinet cu drept efectiv pe un CIF, rămâne de confirmat cazuistic.

[iConta.eu](/)
