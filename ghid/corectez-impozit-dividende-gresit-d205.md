---
title: Cum corectez impozitul pe dividende declarat greșit în D205?
description: D205 e declarație informativă, deci se poate rectifica indiferent de perioada la care se referă, doar cu pozițiile corectate; iConta.eu nu generează momentan rectificativa — corecția se tratează în afara fluxului automat.
published: 2026-09-22
modified: 2026-10-13
poarta: v1
---

# Cum corectez impozitul pe dividende declarat greșit în D205?

Dacă ați descoperit, după depunerea D205, că impozitul pe dividende declarat pentru un beneficiar e greșit, primul pas util este să vă asigurați că e într-adevăr o eroare (vezi ghidul despre cota de impozit calculată „greșit" — deseori e vorba de aplicarea corectă a ratei pe data distribuirii, nu de o eroare a aplicației). Dacă e confirmat că e o eroare reală, e important să înțelegeți limitarea actuală a aplicației înainte de a promite un flux concret.

## Temeiul legal

::: ghid-temei
„Declaraţia rectificativă se întocmeşte pe tipuri de venit şi va cuprinde numai poziţiile corectate, declarate eronat în declaraţia iniţială, sau poziţiile care, în mod eronat, nu au fost cuprinse în declaraţia iniţială." (OPANAF 179/2022, I.5.2-5.3, l.250-261)

„la col. 3-6 [cap. V dividende] se va înscrie cifra «0» (zero)" — pentru ștergerea unei poziții greșite (OPANAF 179/2022, I.5.2-5.3, l.250-261)

„Declaraţia rectifcativa N(1) DA d_rec=(0,1) 0-initiala 1-rectificativa. Declaratia rectificativa va contine doar inregistrarile care reprezinta corectii fata de raportarea initiala." (structura D205, OPANAF 102/2025, rd.4)

„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă. (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1)-(3) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. [...] Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata."
— Codul fiscal (Legea 227/2015), art. 97 alin. (7) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce prevede legea pentru o corecție

D205 („Declaraţie informativă privind impozitul reţinut la sursă şi câştigurile/pierderile din investiţii, pe beneficiari de venit") e declarație **informativă**, nu de impunere: se poate corecta indiferent de perioada la care se referă, nu doar în termenul de prescripție (art. 105 alin. (2) CPF). Practic nu există un termen-limită strict pentru rectificativă — dar cu cât corectezi mai târziu, cu atât crește riscul unei notificări de conformare sau al unei inspecții, mai ales dacă diferența afectează și impozitul efectiv virat.

Legal, corectarea unei declarații D205 depuse greșit se face printr-o declarație rectificativă, care nu retransmite toată declarația, ci doar pozițiile corectate față de declarația inițială — inclusiv poziții omise inițial. Pentru a șterge complet o poziție greșit declarată la capitolul de dividende, regula ANAF cere completarea cu cifra „0" pe coloanele de sumă (distribuit, plătit, bază, impozit) pentru acea poziție, în rectificativă.

Pașii, în ordine:

1. **Identifică eroarea exact** — beneficiar greșit, sumă brută greșită, cotă de impozit greșită (cota în vigoare la art. 97 alin. (7) e 16%; cota aplicabilă se verifică după data distribuirii) sau perioadă de raportare greșită.
2. **Verifică dacă eroarea afectează și suma virată la buget.** Corectarea D205 nu stinge o diferență de plată: dacă s-a reținut și virat mai puțin impozit, diferența se achită separat, plus eventualele accesorii. Reperul e termenul de virare: 25 inclusiv a lunii următoare plății dividendelor; pentru dividendele distribuite, dar neplătite până la sfârșitul anului în care s-a aprobat distribuirea, 25 ianuarie inclusiv a anului următor (art. 97 alin. (7)).
3. **Depune rectificativa** bifând căsuța de declarație rectificativă, cu pozițiile corectate completate integral (datele beneficiarului corectat), respectiv cu „0" pe pozițiile de eliminat.
4. **Păstrează documentele justificative** — hotărârea AGA de distribuire a dividendelor, registrul asociaților, extrasele de cont care arată data plății efective (de care depinde termenul de virare a impozitului).

## Ce se greșește în practică

- Se așteaptă un buton „generează rectificativă" în aplicație, presupunând că funcționează la fel ca la alte declarații.
- Se retrimite integral D205 cu toate pozițiile, în loc de doar pozițiile corectate, așa cum cere procedura de rectificativă.
- Se corectează eroarea doar în contabilitatea internă (nota contabilă), fără să se depună vreo rectificativă la ANAF, lăsând declarația inițială greșită nemodificată oficial.
- Se ignoră faptul că o poziție greșită se șterge cu „0" pe coloanele de sumă, nu prin omiterea ei din rectificativă.
- Se consideră că depunerea rectificativei D205 rezolvă și diferența de impozit nevirată — plata diferenței (și a accesoriilor) e o obligație separată.
- Se amână corectarea până la o eventuală notificare de conformare; corectarea din proprie inițiativă, imediat ce se observă eroarea, e mai simplă și mai ieftină.

## Ce face iConta.eu

În acest moment, aplicația generează D205 exclusiv ca declarație inițială — căsuța „declarație rectificativă" din formularul oficial nu poate fi bifată din aplicație și nu există un mecanism prin care să se producă o declarație rectificativă cu doar pozițiile corectate. Dacă identificați o eroare reală în impozitul pe dividende deja declarat, corectarea trebuie tratată în afara fluxului automat de generare din aplicație; vă recomandăm să verificați cu echipa de suport iConta.eu care este procedura curentă recomandată pentru situația dumneavoastră, înainte de a depune orice corecție la ANAF.

[iConta.eu](/)
