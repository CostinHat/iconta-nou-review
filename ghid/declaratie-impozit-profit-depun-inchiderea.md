---
title: "Ce declarație de impozit pe profit depun la închiderea firmei?"
description: "La dizolvarea cu lichidare, obligația trimestrială de declarare a impozitului pe profit se suspendă — impozitul se stabilește o singură dată, la închiderea procedurii de lichidare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce declarație de impozit pe profit depun la închiderea firmei?

Când o firmă intră în lichidare, regulile obișnuite de declarare trimestrială a impozitului pe profit nu se mai aplică întocmai — legea prevede o regulă specială tocmai pentru perioada de lichidare.

## Temeiul legal

::: ghid-temei
„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42. Nu intră sub incidența acestor prevederi contribuabilii care se dizolvă cu lichidare, pentru perioada cuprinsă între prima zi a anului fiscal următor celui în care a fost deschisă procedura lichidării și data închiderii procedurii de lichidare."
— Codul fiscal (Legea 227/2015), art. 41 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret:

- Contribuabilii aflați în procedura de lichidare **nu mai depun declarații trimestriale** de impozit pe profit pentru perioada cuprinsă între prima zi a anului fiscal următor deschiderii lichidării și data închiderii procedurii — regula trimestrială obișnuită e suspendată pentru ei.
- Declarația anuală de impozit pe profit (D101) se depune, în mod obișnuit, până la 25 iunie inclusiv a anului următor celui de raportare (art. 42 alin. (1), termen valabil din 2026); pentru contribuabilii în lichidare, definitivarea impozitului are loc la închiderea procedurii, potrivit regulilor speciale ale acesteia.
- În cazul unui SRL care se dizolvă și se lichidează, câștigul obținut de asociați din partajul activelor rămase după plata creditorilor se impozitează separat, cu cota specifică lichidării de 10%, impozit final (Codul fiscal, art. 97 alin. (5)) — distinctă de cota de 16% aplicată dividendelor (art. 97 alin. (7)) —, cu obligația de a atașa la cererea de radiere dovada calculării, reținerii și plății acestui impozit.

## Ce se greșește în practică

- Se continuă depunerea declarațiilor trimestriale de impozit pe profit și după deschiderea procedurii de lichidare, deși legea suspendă această obligație pentru perioada respectivă.
- Se confundă impozitul pe profit al ultimei perioade de activitate cu impozitul pe câștigul din partaj datorat de asociați la lichidare — sunt obligații distincte, cu regimuri diferite.
- Nu se atașează la cererea de radiere dovada plății impozitului aferent lichidării, atunci când asociații au optat pentru împărțirea unanimă a activelor rămase.

## Ce face iConta.eu

Modulul de lichidare/radiere societate din iConta.eu este funcționalitate live: generează nota contabilă de valorificare a activelor în procedura de lichidare (vânzare activ imobilizat, cu TVA și descărcarea amortizării) și calculul partajului final pe baza bilanțului de lichidare (restituirea capitalului social, neimpozabilă, distinctă de rezerve/profituri, care reprezintă câștig impozabil), cu impozitarea câștigului asociaților la cota specifică lichidării de 10%, impozit final (CF art. 97 alin. (5)) — nu cota de dividende. Restul operațiunilor din perioada de lichidare (încasarea creanțelor, plata datoriilor, închiderea TVA) se înregistrează prin evidența contabilă generală a aplicației, ca orice altă operațiune. D101 (declarația anuală de impozit pe profit) este de asemenea live, generând XML validat din balanță. Aplicația **nu tratează însă automat** cazul special al suspendării declarării trimestriale pentru firmele aflate în lichidare — încadrarea corectă a perioadei și a obligațiilor declarative rămâne o verificare a contabilului.

[iConta.eu](/)
