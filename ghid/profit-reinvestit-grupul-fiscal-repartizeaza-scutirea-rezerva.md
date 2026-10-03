---
title: "Profit reinvestit în grupul fiscal: cum se repartizează scutirea și rezerva între membri?"
description: "Persoana juridică responsabilă scade scutirea pentru profitul reinvestit din impozitul grupului și comunică fiecărui membru partea lui, proporțional cu sumele transmise. Membrul constituie rezerva pe baza ei."
published: 2026-10-02
modified: 2026-10-02
poarta: v1
---

# Profit reinvestit în grupul fiscal: cum se repartizează scutirea și rezerva între membri?

Într-un grup fiscal, fiecare membru își calculează scutirea pentru profitul reinvestit și o transmite persoanei juridice responsabile. Aceasta scade sumele din impozitul pe profit al grupului, **în limita impozitului datorat de grup**. Apoi comunică fiecărui membru partea care îi revine din suma efectiv scăzută, **proporțional cu sumele transmise**. Membrul constituie rezerva pe baza sumei comunicate de persoana juridică responsabilă, nu pe baza calculului său inițial.

Diferența contează când impozitul grupului nu ajunge pentru toate scutirile. Atunci fiecare membru primește doar o parte din scutirea calculată individual, iar rezerva se ajustează în consecință.

## Temeiul legal

::: ghid-temei
„persoana juridică responsabilă care efectuează scăderea sumei aferente impozitului pe profit scutit din impozitul pe profit datorat de grupul fiscal comunică fiecărui membru care a transmis astfel de sume partea ce îi revine acestuia din suma scăzută la nivelul grupului fiscal;"
— Codul fiscal (Legea 227/2015), art. 42^5 alin. (4^2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„partea care se comunică fiecărui membru, potrivit lit. a) , se determină înmulțind suma scăzută la nivelul grupului fiscal cu raportul dintre sumele transmise de fiecare membru și totalul sumelor primite de persoana responsabilă de la membrii grupului fiscal;"
— Codul fiscal (Legea 227/2015), art. 42^5 alin. (4^2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„suma care se repartizează de către membrul grupului fiscal pentru constituirea rezervei, potrivit art. 22 alin. (5) , este cea comunicată de persoana juridică responsabilă"
— Codul fiscal (Legea 227/2015), art. 42^5 alin. (4^2) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„Aceste sume se scad în limita impozitului pe profit datorat de grupul fiscal."
— Codul fiscal (Legea 227/2015), art. 42^5 alin. (4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii:

1. **Fiecare membru calculează scutirea** potrivit art. 22, pentru activele puse în funcțiune. Calculează și un impozit pe profit propriu, folosit numai pentru a determina sumele care se comunică. Acest impozit nu se datorează și nu se transmite (art. 42^5 alin. (4^1)).
2. **Membrul transmite suma** persoanei juridice responsabile, împreună cu celelalte sume care se scad din impozit (art. 42^5 alin. (4)).
3. **Persoana juridică responsabilă scade sumele** din impozitul grupului, dar numai în limita acestuia.
4. **Repartizarea:** suma scăzută efectiv × (suma transmisă de membru / totalul sumelor primite).
5. **Membrul constituie rezerva** pe baza sumei comunicate (lit. c)). Potrivit art. 22 alin. (5), profitul scutit, mai puțin partea aferentă rezervei legale, se repartizează cu prioritate la rezerve, la sfârșitul exercițiului sau în anul următor.

Un punct interpretabil: lit. b) operează cu sume de impozit scutit, iar art. 22 alin. (5) cere repartizarea la rezerve a „sumei profitului" scutit. Lit. c) spune doar că suma pentru rezervă este „cea comunicată". Recomandarea prudentă: persoana juridică responsabilă comunică explicit atât impozitul scutit repartizat, cât și profitul corespunzător. Membrul documentează în hotărârea de repartizare cum a stabilit suma rezervei.

Persoana juridică responsabilă evidențiază în registrul de evidență fiscală sumele care se scad din impozitul grupului (art. 42^5 alin. (5)).

::: ghid-exemplu
Grupul fiscal format din SC Exemplu SRL (persoana juridică responsabilă) și două filiale are în 2026 un impozit pe profit consolidat de 40.000 lei. Scutiri pentru profit reinvestit transmise:
- filiala A: 30.000 lei;
- filiala B: 20.000 lei;
- total: 50.000 lei.

Se pot scădea doar 40.000 lei, cât e impozitul grupului. Repartizare:
- filiala A: 40.000 × 30.000 / 50.000 = 24.000 lei;
- filiala B: 40.000 × 20.000 / 50.000 = 16.000 lei.

La cota de 16%, impozitul scutit de 24.000 lei corespunde unui profit de 24.000 / 16% = 150.000 lei, iar cel de 16.000 lei unui profit de 100.000 lei. Acestea sunt reperele pentru rezervă, mai puțin partea aferentă rezervei legale, nu cei 187.500 lei, respectiv 125.000 lei calculați inițial (30.000 / 16% și 20.000 / 16%).
:::

## Ce se greșește în practică

- Membrul constituie rezerva pe baza scutirii calculate individual, nu pe baza sumei comunicate de persoana juridică responsabilă.
- Scutirile se scad integral, deși depășesc impozitul grupului.
- Repartizarea se face după alt criteriu (cifra de afaceri, capitalul), nu după raportul legal dintre sumele transmise.
- Impozitul calculat de membru „pentru comunicare" se înregistrează ca datorie proprie, deși legea spune că nu se datorează.
- Persoana juridică responsabilă nu comunică în scris repartizarea, iar membrii nu au documentul pe care se sprijină rezerva.

## Ce face iConta.eu

iConta.eu calculează declarația individuală de impozit pe profit (D101) din balanța fiecărei firme și generează XML validat. Aplicația nu calculează scutirea pentru profitul reinvestit și nu repartizează sumele între membrii grupului. Declarația consolidată a grupului (D101G) nu se poate genera încă din interfață. Calculul scutirii, repartizarea făcută de persoana juridică responsabilă și constituirea rezervei le face contabilul.

[iConta.eu](/)
