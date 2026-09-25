---
title: "De ce diferă CAS din D112 de CAS din contabilitate?"
description: "Cauze legale pentru care CAS-ul raportat prin D112 poate să nu fie simpla înmulțire brut × 25% folosită în notele contabile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# De ce diferă CAS din D112 de CAS din contabilitate?

Când suma de CAS din D112 nu se potrivește cu un calcul rapid „brut × 25%" făcut manual sau într-o notă contabilă, cauza cea mai frecventă nu e o eroare, ci o regulă legală care schimbă baza de calcul față de formula simplă.

## Temeiul legal

::: ghid-temei
„Contribuția de asigurări sociale datorată de către persoanele fizice care obțin venituri din salarii sau asimilate salariilor, în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial, calculată potrivit alin. (5), nu poate fi mai mică decât nivelul contribuției de asigurări sociale calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra salariului de bază minim brut pe țară în vigoare în luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ."
— Legea nr. 227/2015, art. 146 alin. (5^6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cauze reale ale diferenței, nu erori de calcul:

- **Baza minimă obligatorie** (art. 146 alin. (5^6)) — dacă brutul contractual e sub salariul minim pe economie (posibil la part-time), CAS nu se calculează pe brutul efectiv, ci pe pragul minim, proporționat cu zilele lucrătoare active în lună.
- **Luna incompletă** — pentru un salariat angajat sau plecat la mijlocul lunii, baza minimă se raportează la zilele lucrătoare din contract, nu la o lună întreagă, ceea ce produce un rezultat diferit de o simplă proporție pe zile calendaristice.
- **Concediul medical** — zilele acoperite de indemnizație schimbă baza și, uneori, procentele aplicate, față de o formulă simplificată „brut × 25%" care nu ia în calcul aceste zile separat.
- **Rotunjirea** — D112 rotunjește la nivel de angajat, per rând al declarației; o notă contabilă simplificată poate rotunji la alt nivel (per firmă, per total), ceea ce produce diferențe mici, dar reale.

## Ce se greșește în practică

- Se recalculează manual CAS ca „brut × 25%" pentru fiecare salariat, fără a verifica dacă se aplică baza minimă de la art. 146 alin. (5^6), în special la contractele part-time sau la salariul minim.
- Se compară un total lunar simplificat, calculat pe brutul mediu al firmei, cu totalul real din D112, care ia în calcul fiecare angajat separat, cu regulile lui specifice (facilitate, concediu medical, part-time).
- Se ignoră proratarea pe zile lucrătoare pentru lunile cu angajare/încetare la mijloc de lună, aplicând regula bazei minime pe luna întreagă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu recalculează independent CAS pentru fiecare salariat, printr-o a doua cale de verificare separată de generatorul principal al declarației, pentru cazul simplu (brut peste minim, lună întreagă, fără concediu medical, normă întreagă) — și blochează generarea cu motivul exact al angajatului dacă cele două căi de calcul nu coincid. Pentru cazurile cu facilitate la minim proratată sau alte combinații mai complexe, aplicația documentează explicit limitele acestei verificări.

[iConta.eu](/)
