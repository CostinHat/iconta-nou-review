---
title: "Cum îmi suspend PFA-ul când nu am activitate"
description: "Efectul fiscal al mențiunii de suspendare a activității înscrise la registrul comerțului — de când încetează obligațiile declarative."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum îmi suspend PFA-ul când nu am activitate

Suspendarea activității unei PFA e, în esență, o mențiune înscrisă la registrul comerțului — actul de autorizare propriu-zis al PFA-urilor (OUG 44/2008) nu se află printre sursele consultate pentru acest ghid, deci pașii administrativi ai suspendării nu pot fi citați aici verbatim. Ce e verificabil la sursă e efectul fiscal al acestei mențiuni: din ce moment încetează obligația de a depune declarații.

## Temeiul legal

::: ghid-temei
„Entitățile înregistrate în registrul comerțului, pentru care există înscrise mențiuni privind inactivitatea temporară, nu au obligația depunerii declarațiilor fiscale pentru perioada în care se află în inactivitate temporară, începând cu data de 1 a lunii următoare înscrierii mențiunii privind inactivitatea temporară în registrul comerțului."
— Legea 207/2015, art. 101 alin. (4^1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă concret din text pentru o PFA fără activitate:

- **Momentul încetării obligației declarative** nu e data cererii de suspendare, ci **prima zi a lunii următoare** înscrierii mențiunii în registrul comerțului — o suspendare cerută la mijlocul lunii nu scutește PFA de declarațiile lunii în curs.
- **Limita de timp**: efectul suspendării încetează fie la reluarea activității, fie „la împlinirea unui termen de 3 ani de la data înregistrării în registrul comerțului a mențiunii" (art. 101 alin. 4^3) — suspendarea nu poate fi menținută la nesfârșit fără consecințe.
- **Obligațiile din perioada anterioară rămân**: „Obligațiile de declarare, aferente activității desfășurate anterior înregistrării inactivității temporare/suspendării, se mențin" (art. 101 alin. 4^4) — suspendarea nu șterge declarațiile deja datorate pentru perioada activă.

## Ce se greșește în practică

- Se consideră că obligațiile declarative încetează chiar din ziua depunerii cererii de suspendare, ignorând regula legală: efectul începe abia din prima zi a lunii următoare înscrierii mențiunii (art. 101 alin. 4^1).
- Se lasă suspendarea „deschisă" mai mult de 3 ani, fără reluare sau altă acțiune, presupunând că regimul continuă automat — legea limitează explicit efectul la acest termen (art. 101 alin. 4^3).
- Se presupune că suspendarea anulează retroactiv declarațiile nedepuse din perioada de activitate anterioară — alin. (4^4) spune clar contrariul.

## Ce face iConta.eu

iConta.eu urmărește PFA/II/PFL ca „partidă simplă", cu declarațiile specifice acestei forme (D212 — Declarația unică). Nu am identificat în cod o funcție care să gestioneze automat mențiunea de suspendare a activității la registrul comerțului sau care să calculeze, pe baza acestei mențiuni, data de la care obligațiile declarative încetează, conform art. 101 alin. (4^1) — acest pas administrativ, la ONRC, și urmărirea efectului lui fiscal rămân, la această dată, în afara aplicației.

[iConta.eu](/)
