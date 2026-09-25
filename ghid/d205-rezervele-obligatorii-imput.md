---
title: "D205 și rezervele obligatorii: ce se imput"
description: "Ce raportează efectiv declarația 205 (impozit reținut la sursă pe beneficiari de venit) și de ce rezerva legală obligatorie a unei societăți nu are legătură cu acest formular."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# D205 și rezervele obligatorii: ce se imput

Din cercetarea legislației, aceste două subiecte nu se intersectează. D205 este declarația informativă privind impozitul reținut la sursă și câștigurile/pierderile din investiții, pe beneficiari de venit — un formular care privește impozitul pe venit al persoanelor fizice beneficiare. Rezerva legală obligatorie, în schimb, e un concept complet diferit: procentul din profitul contabil pe care o societate e obligată să-l constituie ca rezervă, potrivit Codului fiscal și legislației societăților. Le clarificăm separat, pentru că e mai util decât o legătură forțată.

## Temeiul legal

::: ghid-temei
„Declarația informativă privind impozitul reținut la sursă și câștigurile/pierderile din investiții, pe beneficiari de venit"
— titlul formularului 205, aprobat prin Ordinul președintelui A.N.A.F. nr. 179/2022, cu modificările Ordinului nr. 303/2026 (sursă: anaf_surse/opanaf_303_2026_d205.txt)

„a) rezerva legală este deductibilă în limita unei cote de 5% aplicate asupra profitului contabil, la care se adaugă cheltuielile cu impozitul pe profit, până ce aceasta va atinge a cincea parte din capitalul social subscris și vărsat sau din patrimoniu, după caz."
— Legea nr. 227/2015 privind Codul fiscal, art. 26 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

**Ce raportează D205:** impozitul pe venit reținut la sursă de plătitorii de venit (dividende, dobânzi, drepturi de proprietate intelectuală, premii etc.), defalcat pe fiecare beneficiar persoană fizică, plus câștigurile/pierderile din investiții. Se depune anual de către plătitorii de venituri cu obligație de reținere la sursă. Nu conține și nu are cum să conțină informații despre rezerva legală a societății plătitoare — cele două privesc paliere fiscale diferite (impozitul pe venitul beneficiarului vs. impozitul pe profitul plătitorului).

**Ce e rezerva legală obligatorie:** un procent din profitul contabil (5%, cumulat până la 20% din capitalul social) pe care o societate trebuie să-l aloce anual la rezerve, înainte de a distribui profitul ca dividende. Fiscal, ea e deductibilă la calculul impozitului pe profit exact în limitele de mai sus — o problemă de calcul al profitului impozabil și de repartizare a profitului, nu de declarare a impozitului reținut la sursă.

## Ce se greșește în practică

- Se caută rubrici pentru rezerva legală în D205, deși formularul nu are și nu ar trebui să aibă vreo legătură cu acest calcul.
- Se omite constituirea rezervei legale obligatorii înainte de repartizarea profitului ca dividende, ceea ce afectează corectitudinea calculului deducerii de 5% și, indirect, chiar suma impozitului pe dividende reținută la sursă și raportată în D205.
- Se confundă rezerva legală (obligatorie, din Codul fiscal) cu alte rezerve statutare sau facultative constituite din profit, care au regim fiscal diferit.
- Se raportează în D205 un impozit pe dividende calculat greșit, pentru că baza de calcul (profitul net de repartizat) nu a scăzut corect rezerva legală obligatorie.

## Ce face iConta.eu

iConta.eu are un modul dedicat generării D205 (`d205.py`, cu funcțiile `calcul_d205`, `build_xml`, `erori_generare`), care calculează impozitul reținut la sursă pe beneficiar de venit direct din datele înregistrate în aplicație (dividende plătite, alte venituri cu reținere la sursă) și construiește XML-ul conform structurii ANAF. Constituirea rezervei legale obligatorii a societății este o operațiune separată, de repartizare a profitului, tratată la nivelul bilanțului — nu am găsit în cod o legătură automată între cele două, ceea ce confirmă și de ce ele nu se intersectează nici în lege.

[iConta.eu](/)
