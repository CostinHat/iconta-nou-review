---
title: "Cum calculez limita deductibilă pentru protocol?"
description: "Limita de deductibilitate a cheltuielilor de protocol este de 2% aplicată asupra profitului contabil, la care se adaugă impozitul pe profit și cheltuielile de protocol — baza de calcul se determină după ce se adună înapoi tocmai elementul care se limitează."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum calculez limita deductibilă pentru protocol?

Limita cheltuielilor de protocol nu se aplică direct pe profitul contabil brut, ci pe o bază de calcul construită special pentru acest scop — la care se adaugă înapoi atât impozitul pe profit, cât și cheltuielile de protocol în sine. E o construcție circulară aparent, dar precis definită de lege.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli au deductibilitate limitată: a) cheltuielile de protocol în limita unei cote de 2% aplicată asupra profitului contabil la care se adaugă cheltuielile cu impozitul pe profit și cheltuielile de protocol. În cadrul cheltuielilor de protocol se includ și cheltuielile înregistrate cu taxa pe valoarea adăugată colectată potrivit prevederilor titlului VII, pentru cadourile oferite de contribuabil, cu valoare mai mare de 100 lei."
— Legea nr. 227/2015 (Codul fiscal), art. 25 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Formula de calcul, pas cu pas:

- **Baza de calcul** = profitul contabil + cheltuielile cu impozitul pe profit + cheltuielile de protocol înregistrate în perioada respectivă. Se pornește de la profitul contabil, nu de la rezultatul fiscal deja ajustat.
- **Limita deductibilă** = 2% din această bază — tot ce depășește limita este cheltuială nedeductibilă la calculul rezultatului fiscal.
- În cheltuielile de protocol se include și **TVA colectată** pentru cadourile oferite contribuabilului cu o valoare mai mare de 100 lei — adică, dacă firma oferă un cadou de peste 100 lei unui client, TVA aferentă acelui cadou (colectată ca livrare asimilată) intră tot în categoria cheltuielilor de protocol supuse plafonării de 2%.
- Calculul se face cumulat, pe măsura avansării în cursul anului fiscal (trimestrial/anual, în funcție de perioada fiscală a firmei), pentru că baza de calcul (profitul contabil cumulat) se schimbă de la o perioadă la alta.

## Ce se greșește în practică

- Se aplică 2% direct pe profitul contabil raportat în bilanț, fără să se adune înapoi impozitul pe profit și cheltuielile de protocol — ceea ce subestimează limita deductibilă.
- Se omite includerea TVA colectată pentru cadourile de peste 100 lei în totalul cheltuielilor de protocol, deși legea o cere explicit.
- Se calculează limita o singură dată, la final de an, fără verificare trimestrială, ceea ce poate duce la plăți anticipate incorect calculate pe parcursul anului.

## Ce face iConta.eu

La data acestui ghid, iConta.eu clasifică cheltuielile introduse de utilizator pe conturile corespunzătoare (inclusiv contul de protocol), dar nu calculează automat plafonul de 2% din art. 25 alin. (3) lit. a) și nu ajustează automat rezultatul fiscal pentru partea care depășește limita — verificarea plafonului și ajustarea rezultatului fiscal aferent rămân un calcul pe care contabilul îl face manual, folosind datele contabile din aplicație.

[iConta.eu](/)
