---
title: "Ce amortizare este deductibilă la calculul impozitului pe profit?"
description: "Condițiile pe care trebuie să le îndeplinească un mijloc fix ca amortizarea lui să fie deductibilă fiscal, potrivit Codului fiscal, și ce active sunt excluse explicit."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce amortizare este deductibilă la calculul impozitului pe profit?

Nu orice cheltuială cu amortizarea contabilă e automat deductibilă la calculul impozitului pe profit. Codul fiscal definește precis ce înseamnă „mijloc fix amortizabil" din punct de vedere fiscal și exclude expres o serie de active, indiferent cum sunt tratate în contabilitate.

## Temeiul legal

::: ghid-temei
„(2) Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții:
a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative;
b) la data intrării în patrimoniul contribuabilului, are o valoare fiscală egală sau mai mare decât suma de 5.000 lei; această limită se actualizată anual, în funcție de indicele de inflație, prin hotărâre a Guvernului;
c) are o durată normală de utilizare mai mare de un an."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„(4) Nu reprezintă active amortizabile: a) terenurile, inclusiv cele împădurite; b) tablourile și operele de artă; c) fondul comercial; d) lacurile, bălțile și iazurile care nu sunt rezultatul unei investiții; [...] f) orice mijloc fix care nu își pierde valoarea în timp datorită folosirii, potrivit normelor; g) casele de odihnă proprii, locuințele de protocol, navele, aeronavele, vasele de croazieră, altele decât cele utilizate pentru desfășurarea activității economice; h) imobilizările necorporale cu durată de viață utilă nedeterminată, încadrate astfel potrivit reglementărilor contabile aplicabile."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă condițiile cumulative pe care trebuie să le îndeplinească un activ pentru ca amortizarea lui să fie fiscal deductibilă:

- Trebuie să fie **deținut și utilizat** efectiv în activitatea firmei — producție, livrare de bunuri, prestare de servicii, închiriere către terți sau în scopuri administrative. Un activ care stă neutilizat nu îndeplinește această condiție.
- Trebuie să aibă, la data intrării în patrimoniu, o **valoare fiscală de cel puțin 5.000 lei** (prag valabil pentru anul fiscal 2026, actualizat prin hotărâre de Guvern în funcție de inflație) — sub acest prag, cheltuiala se deduce integral, nu prin amortizare eșalonată.
- Trebuie să aibă o **durată normală de utilizare mai mare de un an** — un bun consumat sau folosit integral într-un an nu intră în categoria mijloacelor fixe amortizabile.
- Chiar dacă îndeplinesc condițiile de mai sus ca valoare și durată, sunt **excluse expres** de la amortizare: terenurile, tablourile și operele de artă, fondul comercial, lacurile/bălțile/iazurile care nu sunt rezultatul unei investiții, bunurile care nu-și pierd valoarea prin folosire, casele de odihnă proprii și locuințele de protocol (cu excepția celor utilizate direct în activitatea economică), precum și imobilizările necorporale cu durată de viață utilă nedeterminată.

## Ce se greșește în practică

- Se amortizează fiscal un teren înregistrat împreună cu o construcție, deși legea exclude explicit terenurile de la amortizare — doar construcția aferentă e amortizabilă.
- Se aplică pragul valoric de 5.000 lei mecanic, fără să se verifice și condiția separată a duratei de utilizare mai mare de un an — ambele condiții trebuie îndeplinite cumulativ, nu alternativ.
- Se amortizează fiscal o casă de odihnă sau o locuință de protocol deținută de firmă, ignorând excluderea explicită de la art. 28 alin. (4) lit. g), cu excepția cazului în care activul e efectiv utilizat în activitatea economică (de exemplu, ca spațiu de cazare pentru clienți plătitori).
- Se presupune că orice imobilizare necorporală se amortizează la fel ca una corporală — imobilizările necorporale cu durată de viață utilă nedeterminată sunt excluse explicit de la amortizarea fiscală.

## Ce face iConta.eu

Modulul de mijloace fixe din iConta.eu ține evidența activelor cu valoare, durată normală de funcționare și metodă de amortizare, calculează amortizarea lunară pe baza acestor date și generează notele contabile aferente, inclusiv în cazurile cu reevaluare. Aplicația identifică automat, după contul de imobilizare, terenurile (cont 211) și le exclude din calculul de amortizare, dar nu verifică automat celelalte categorii excluse explicit de la art. 28 alin. (4) (tablouri și opere de artă, fond comercial, lacuri/bălți/iazuri etc.) — încadrarea corectă a acestor active, ca amortizabile sau nu din punct de vedere fiscal, rămâne o decizie a contabilului la introducerea lor în evidență.

[iConta.eu](/)
