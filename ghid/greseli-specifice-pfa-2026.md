---
title: "Greșeli specifice PFA în 2026"
description: "Pragurile de 12 și 24 de salarii minime brute pe țară din Codul fiscal, care decid dacă un PFA datorează CAS și la ce bază de calcul, și greșelile frecvente în aplicarea lor."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeli specifice PFA în 2026

Cea mai frecventă greșeală a unui PFA nu e la calculul impozitului pe venit, ci la stabilirea obligației de a plăti contribuția de asigurări sociale (CAS) — pentru că testul nu se face pe venitul dintr-o singură activitate, ci pe venitul cumulat din toate sursele independente.

## Temeiul legal

::: ghid-temei
„(1) Persoanele fizice care în anul fiscal pentru care se depune Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice prevăzută la art. 122 au realizat venituri din activitățile prevăzute la art. 137 alin. (1) lit. b) și b^1), din una sau mai multe surse și/sau categorii de venituri, a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale la o bază de calcul stabilită potrivit alin. (2).
(2) Baza anuală de calcul al contribuției de asigurări sociale [...] o reprezintă venitul ales de contribuabil, care nu poate fi mai mic decât: a) nivelul de 12 salarii minime brute pe țară, în cazul veniturilor realizate cuprinse între 12 salarii minime brute pe țară inclusiv și 24 de salarii minime brute pe țară; b) nivelul de 24 de salarii minime brute pe țară, în cazul veniturilor realizate cel puțin egale cu 24 de salarii minime brute pe țară.
(3) Încadrarea în plafonul anual [...] se efectuează prin cumularea veniturilor nete și/sau a normelor anuale de venit din activități independente [...]."
— Legea 227/2015 (Codul fiscal), art. 148 alin. (1)-(3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă mecanismul pe care majoritatea greșelilor îl ratează:

- Testul de 12 salarii minime brute pe țară **nu se aplică per activitate**, ci pe **valoarea cumulată** din toate sursele și categoriile de venituri din activități independente ale aceleiași persoane fizice, potrivit alin. (3).
- Sub 12 salarii minime cumulate, nu se datorează CAS. Între 12 și sub 24 de salarii minime, baza de calcul minimă e de 12 salarii minime. La 24 de salarii minime sau peste, baza minimă urcă la 24 de salarii minime — un prag în trepte, nu proporțional cu venitul real.
- Baza de calcul e „venitul ales de contribuabil", cu limita minimă de mai sus — nu venitul net efectiv realizat, care poate fi mai mare.

## Ce se greșește în practică

- Se verifică plafonul de 12 salarii minime separat pentru fiecare activitate independentă (de exemplu, un PFA cu venituri din două surse diferite), în loc să se cumuleze toate veniturile din activități independente ale aceleiași persoane, cum cere alin. (3).
- Se confundă pragul de 12 salarii minime (obligația de a plăti CAS) cu pragul de 24 de salarii minime (baza minimă de calcul crește) — sunt două praguri diferite, cu efecte diferite, nu un singur prag cu două nume.
- Se calculează salariul minim brut pe țară aplicabil pentru anul precedent, în loc de cel valabil pentru anul de referință al declarației — pragurile se raportează la salariul minim din anul respectiv, care se poate modifica pe parcursul anului.

## Ce face iConta.eu

La data acestui ghid, nu am putut confirma din codul aplicației un modul dedicat de verificare automată a încadrării unui PFA în pragurile de 12/24 de salarii minime pentru CAS, conform art. 148. Aplicația oferă evidența contabilă generală a veniturilor și cheltuielilor PFA; calculul pragurilor de CAS pentru Declarația unică rămâne, la acest stadiu, o verificare pe care contabilul trebuie s-o facă separat, cumulând manual toate sursele de venit independent ale persoanei.

[iConta.eu](/)
