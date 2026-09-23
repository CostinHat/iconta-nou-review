---
title: "Declararea TVA la importul de bunuri: cum procedez"
description: Baza de TVA la import se calculează din valoarea în vamă plus taxe și accesorii, dar cota trebuie declarată explicit de fiecare dată — aplicația nu presupune niciodată cota standard curentă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Declararea TVA la importul de bunuri: cum procedez

Pentru un import de bunuri din afara Uniunii Europene, TVA-ul se calculează pornind de la valoarea în vamă a bunurilor, nu de la prețul de pe factura furnizorului. Peste această valoare se adaugă taxele vamale, accizele (dacă e cazul) și cheltuielile accesorii până la primul loc de destinație din România, iar rezultatul este baza de TVA la care se aplică cota.

## Temeiul legal

::: ghid-temei
„(1) Baza de impozitare pentru importul de bunuri este valoarea în vamă a bunurilor, stabilită conform legislației vamale în vigoare, la care se adaugă orice taxe, impozite, comisioane și alte taxe datorate în afara României, precum și cele datorate ca urmare a importului bunurilor în România, cu excepția taxei pe valoarea adăugată care urmează a fi percepută.
(2) Baza de impozitare cuprinde cheltuielile accesorii, precum comisioanele, cheltuieli de ambalare, transport și asigurare, care intervin până la primul loc de destinație a bunurilor în România, în măsura în care aceste cheltuieli nu au fost cuprinse în baza de impozitare stabilită conform alin. (1) [...]"

— Codul fiscal (Legea 227/2015 consolidat), art. 289 alin. (1)-(2)
:::

Formula practică este deci: **baza de TVA = valoare vamală + taxe vamale + accize + cheltuieli accesorii**. Peste taxa vamală calculată (valoare vamală × procentul din tariful vamal), se obține baza pe care se aplică cota de TVA declarată pentru operațiune.

Modul concret în care se plătește/deduce TVA-ul calculat depinde de statutul firmei:

::: ghid-temei
„c) pentru taxa achitată pentru importul de bunuri, altele decât cele prevăzute la lit. d), să dețină declarația vamală de import sau actul constatator emis de organele vamale, care să menționeze persoana impozabilă ca importator al bunurilor din punctul de vedere al taxei, precum și documente care să ateste plata taxei de către importator [...] d) pentru taxa datorată pentru importul de bunuri efectuat conform art. 326 alin. (4) și (5) [...] persoana impozabilă trebuie să înscrie taxa pe valoarea adăugată ca taxă colectată în decontul aferent perioadei fiscale în care ia naștere exigibilitatea."

— Codul fiscal (Legea 227/2015 consolidat), art. 299 alin. (1) lit. c)-d)
:::

Practic există trei situații: firma plătește TVA direct la vamă și o deduce pe baza DVI (lit. c), firma are certificat de amânare de la plată și reflectă totul în decont, fără plată efectivă (lit. d, condiționat de art. 326 alin. 4), sau firma nu e plătitoare de TVA și taxa plătită la vamă intră direct în costul bunului, nedeductibilă.

## Ce se greșește în practică

- Se lasă cota de TVA "implicită" (de obicei cea standard curentă), fără să se verifice dacă operațiunea concretă are altă cotă — o cotă presupusă automat se poate desincroniza tacit de la o schimbare legislativă, iar o operațiune mai veche poate avea altă cotă decât una de azi.
- Se introduce procentul taxei vamale ca sumă absolută în loc de procent din valoarea vamală — o greșeală care a produs, în trecut, o taxă vamală de 5.000 lei la o valoare vamală de 1.000 lei, în loc de procentul corect aplicat.
- Se confundă baza de TVA cu prețul facturii externe, ignorând că taxele vamale și cheltuielile accesorii (transport, asigurare) până la primul loc de destinație din România intră obligatoriu în bază.

## Ce face iConta.eu

Ecranul „Import extracomunitar (DVI)" (categoria Operațiuni speciale > Extern) cere data, valoarea vamală, contul de destinație (sugestie 371), procentul taxei vamale (opțional, validat strict între 0 și 100), accizele și accesoriile (opționale), plus cota de TVA. Cota **nu are valoare implicită** — dacă lipsește, aplicația respinge operațiunea și cere să fie declarată explicit, exact pentru a evita ca o cotă scrisă undeva să rămână desincronizată de lege.

Din aceste date, motorul de calcul produce taxa vamală, baza de TVA și modul de tratare a TVA (plată la vamă, autolichidare prin certificat de amânare, sau cost pentru neplătitori), iar aplicația generează automat nota contabilă corespunzătoare: linia de bază pe contul de destinație (ex. 371) față de 401, taxa vamală pe 446 dacă există, și linia de TVA specifică modului ales (4426=4427 pentru certificat de amânare, 4426=446 pentru plată la vamă, sau TVA inclus în costul de pe contul de destinație pentru neplătitori).

[iConta.eu](/)
