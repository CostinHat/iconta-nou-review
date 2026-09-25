---
title: "Cum reconciliez fișa ANAF cu conturile de taxe din balanță?"
description: "Ce este, legal, fișa pe plătitor (evidența creanțelor fiscale) ținută de ANAF, și de ce o diferență față de balanța contabilă proprie nu înseamnă automat o eroare a firmei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum reconciliez fișa ANAF cu conturile de taxe din balanță?

„Fișa pe plătitor" din Spațiul Privat Virtual nu este o simplă informație de consultare, ci reflectarea oficială a evidenței pe care organul fiscal o ține pentru fiecare contribuabil — obligații declarate, plăți, compensări, dobânzi și penalități. Reconcilierea ei cu soldurile conturilor de taxe din balanța proprie (4423 TVA de plată, 441 impozit pe profit/micro, 444 impozit pe salarii etc.) este o verificare tehnică, dar bazată pe o evidență paralelă, ținută independent de contabilitatea firmei.

## Temeiul legal

::: ghid-temei
„ART. 153 Evidența creanțelor fiscale
(1) în scopul exercitării activității de colectare a creanțelor fiscale, organul fiscal organizează, pentru fiecare contribuabil/plătitor, evidența creanțelor fiscale și modul de stingere a acestora. Evidența se organizează pe baza titlurilor de creanță fiscală și a actelor referitoare la stingerea creanțelor fiscale.
(2) Contribuabilul/Plătitorul are acces la informațiile din evidența creanțelor fiscale, la cererea acestuia, adresată organului fiscal competent."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 153 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din text rezultă natura exactă a ceea ce numim, colocvial, „fișa ANAF":

- Este o **evidență ținută de organul fiscal**, separată de contabilitatea firmei, organizată „pe baza titlurilor de creanță fiscală" (declarațiile depuse, deciziile de impunere) „și a actelor referitoare la stingerea creanțelor" (plăți, compensări, executări silite) — deci reflectă ce a ajuns efectiv și a fost procesat la ANAF, nu neapărat ce a fost calculat corect de firmă.
- Accesul contribuabilului la această evidență se face „la cererea acestuia" — practic prin Spațiul Privat Virtual — nefiind o transmitere automată, sincronizată în timp real cu depunerea declarațiilor.
- O diferență între fișa ANAF și balanța proprie poate proveni din ambele direcții: o declarație depusă greșit sau nedepusă de firmă, dar și o eroare de procesare la ANAF, o plată alocată greșit, o compensare întârziată sau o decizie de impunere din oficiu necunoscută firmei.

## Ce se greșește în practică

- Se presupune automat că fișa ANAF este „adevărul" și se ajustează balanța proprie după ea, fără verificarea prealabilă a corectitudinii declarațiilor depuse — deși diferența poate proveni chiar dintr-o eroare de procesare la ANAF.
- Se ignoră decalajul de timp dintre depunerea unei declarații/efectuarea unei plăți și actualizarea evidenței ANAF, tratând orice diferență temporară ca pe o eroare reală.
- Se reconciliază doar soldurile finale, fără verificarea, pe fiecare tip de obligație și perioadă, a corespondenței între ce a fost declarat (titlul de creanță) și ce a fost plătit/compensat (stingerea), ceea ce poate ascunde erori compensate din întâmplare.

## Ce face iConta.eu

iConta.eu rulează un motor de control încrucișat între declarațiile calculate în aplicație (D300, D112, D390 etc.) și ce a fost efectiv depus/transmis la ANAF (inclusiv confruntarea între facturile transmise prin e-Factura și ce a fost declarat prin D394), semnalând neconcordanțele ca alertă pentru contabil. Aplicația nu importă însă automat fișa pe plătitor de la ANAF (soldul obligațiilor și plăților din evidența oficială a organului fiscal) și nu face reconcilierea directă a acesteia cu conturile de taxe din balanță — acest pas rămâne o verificare manuală, prin consultarea Spațiului Privat Virtual.

[iConta.eu](/)
