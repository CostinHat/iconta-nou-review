---
title: "Terenurile se amortizează contabil sau fiscal?"
description: "Regula unică, valabilă atât contabil cât și fiscal, potrivit căreia terenurile nu se amortizează, spre deosebire de investițiile efectuate pe ele."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Terenurile se amortizează contabil sau fiscal?

Răspunsul este identic din ambele perspective: terenurile nu se amortizează, nici contabil, nici fiscal. Regula e simplă și consecventă între cele două reglementări — atât Codul fiscal, cât și reglementările contabile aplicabile exclud explicit terenurile din categoria activelor amortizabile.

## Temeiul legal

::: ghid-temei
„241. - (1) Terenurile nu se amortizează. (2) Investițiile efectuate pentru amenajarea lacurilor, bălților, iazurilor, terenurilor și pentru alte lucrări similare se recuperează pe calea amortizării, prin includerea în cheltuielile de exploatare potrivit politicilor contabile aprobate, pe baza duratelor de viață utilă ale acestora."
— OMFP nr. 1.802/2014, Reglementări contabile privind situațiile financiare anuale individuale, pct. 241 alin. (1)-(2) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- **Contabil**: terenul, ca atare, nu se amortizează niciodată — el nu își pierde valoarea prin folosire, spre deosebire de o clădire sau un utilaj.
- **Fiscal**: Codul fiscal confirmă aceeași regulă, enumerând explicit terenurile printre activele care nu sunt amortizabile — „Nu reprezintă active amortizabile: a) terenurile, inclusiv cele împădurite" (art. 28 alin. (4) lit. a), Legea nr. 227/2015, sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt).
- **Excepția reală**: investițiile efectuate pe teren (amenajări, lucrări de îmbunătățire, defrișare, sistematizare) se amortizează separat, ca element distinct de teren, pe durata de viață utilă a investiției respective — nu terenul în sine crește sau scade valoarea prin amortizare, ci lucrarea adăugată pe el.
- Practic, evidența contabilă trebuie să separe clar valoarea terenului (neamortizabilă) de valoarea eventualelor investiții/amenajări asupra lui (amortizabile), chiar dacă ambele apar în același dosar al activului imobiliar.

## Ce se greșește în practică

- Se include, din greșeală, valoarea terenului în baza de calcul a amortizării unei clădiri construite pe el, majorând artificial cheltuiala deductibilă cu amortizarea — terenul trebuie separat de construcție încă de la achiziție sau recepție.
- Se amortizează întregul teren atunci când, de fapt, doar o investiție de amenajare (nivelare, sistematizare, drenaj) ar trebui amortizată — regula se aplică diferit pentru teren și pentru investiția de pe el.
- Se presupune că regula diferă între contabil și fiscal, generând tratamente separate inutil — pentru acest subiect, cele două reglementări converg spre aceeași soluție.
- Se ignoră tratamentul distinct al reevaluării terenurilor (permisă contabil, cu efecte specifice asupra valorii fiscale conform reglementărilor privind reevaluarea), confundând reevaluarea cu amortizarea — sunt operațiuni diferite.

## Ce face iConta.eu

iConta.eu are un modul de mijloace fixe care permite introducerea și amortizarea activelor pe baza duratei normale de funcționare stabilite de utilizator, pentru fiecare mijloc fix în parte. Din verificarea codului sursă (`core/d406_active.py`), motorul de amortizare **recunoaște contul 211 „Terenuri" ca o categorie separată, neamortizabilă**: dacă un activ înregistrat pe acest cont are o metodă de amortizare setată, calculul amortizării (folosit atât pentru afișarea listei de mijloace fixe, cât și pentru generarea notei lunare de amortizare) respinge operația și afișează o eroare, în loc să calculeze o amortizare inexistentă. Separarea terenului de eventualele investiții amortizabile de pe el rămâne însă responsabilitatea contabilului la configurarea fiecărui activ — aplicația nu face automat această distincție dacă cele două valori sunt introduse împreună, pe același activ.

[iConta.eu](/)
