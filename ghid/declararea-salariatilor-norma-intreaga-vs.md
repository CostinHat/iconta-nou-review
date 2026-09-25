---
title: "Declararea salariaților cu normă întreagă vs part-time în D112"
description: "Cum tratează legea și, real, aplicația, distincția dintre normă întreagă și normă parțială în declarația 112."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Declararea salariaților cu normă întreagă vs part-time în D112

Declarația 112 tratează diferit, din punct de vedere al contribuțiilor, un salariat cu normă întreagă față de unul cu normă parțială — nu pentru că legea ar interzice normele parțiale, ci pentru că a introdus, din 2022, o bază minimă de calcul care se aplică indiferent de tipul contractului. Pe lângă calculul propriu-zis, formularul 112 cere și declararea explicită a tipului de normă pentru fiecare salariat.

## Temeiul legal

::: ghid-temei
„Contribuția de asigurări sociale datorată de către persoanele fizice care obțin venituri din salarii sau asimilate salariilor, în baza unui contract individual de muncă cu normă întreagă sau cu timp parțial, calculată potrivit alin. (5), nu poate fi mai mică decât nivelul contribuției de asigurări sociale calculate prin aplicarea cotei prevăzute la art. 138 lit. a) asupra salariului de bază minim brut pe țară în vigoare în luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ."
— Legea 227/2015 (Codul fiscal), art. 146 alin. (5^6) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

- Legea nu tratează normă întreagă și normă parțială diferit ca principiu — ambele sunt supuse aceleiași reguli a bazei minime, dacă venitul e sub salariul minim brut pe țară.
- Ce contează pentru declarație nu e doar câtă contribuție iese, ci și **cum e marcat, formal, tipul de contract** — formularul 112 are un câmp dedicat (nomenclator cu valori „normă întreagă" și „P1"–„P7", pentru câte ore/zi la normă parțială), aprobat prin structura tehnică anexată Ordinului comun 605/95/928/2314/2026 (`anaf_surse/structura_D112_0726_030826.pdf`).
- Baza minimă (art. 146 alin. 5^6) se calculează proporțional cu numărul zilelor lucrătoare în care contractul a fost activ, nu ca sumă fixă lunară.

## Ce se greșește în practică

- Se presupune că, dacă venitul brut al unui salariat part-time e corect calculat și contribuțiile ies bine pe fluturaș, declarația 112 „e automat corectă" — corectitudinea valorică (banii) și corectitudinea declarativă (cum e marcat tipul de contract în XML) sunt două lucruri diferite.
- Se confundă suprataxarea (baza minimă) cu tipul de normă: suprataxarea se aplică oricărui contract, întreg sau parțial, dacă venitul e sub minim — nu doar celor part-time.
- Se ignoră faptul că numărul de ore/zi la normă parțială (P1..P7 din nomenclator) trebuie să fie strict mai mic decât norma standard a locului de muncă — o eroare de introducere aici produce respingere la validare.

## Ce face iConta.eu

iConta calculează corect, intern, distincția dintre normă întreagă și normă parțială: motorul de salarizare (`core/salarizare.py`) primește parametrul de normă parțială și aplică baza minimă proporțională exact ca în text, iar generatorul D112 (`core/d112.py`) refolosește același calcul ca statul de plată, ca sursă unică de adevăr.

Există însă o limită reală, verificată direct în cod la data acestui ghid: **câmpul din XML care declară tipul de contract față de ANAF (`B1_3`, cu valorile `N`/`P1`..`P7`) e scris hardcodat cu valoarea „N" (normă întreagă) pentru toți salariații**, indiferent dacă au contract part-time sau nu. Sumele bănești (contribuții, bază minimă) ies corect, dar acest câmp descriptiv e, în prezent, greșit pentru orice salariat part-time declarat prin iConta. E o limită cunoscută și documentată intern, aflată azi pe lista de lucru viitoare, nu o funcție finalizată — un ghid despre acest subiect nu poate afirma că aplicația marchează corect tipul de normă în declarația depusă.

[iConta.eu](/)
