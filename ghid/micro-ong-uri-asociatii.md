---
title: "Micro pentru ONG-uri și asociații: se poate"
description: "Codul fiscal nu exclude explicit asociațiile și fundațiile din regimul microîntreprinderilor, dar trecerea la acest regim înseamnă renunțarea la scutirea specială de la art. 15."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro pentru ONG-uri și asociații: se poate

Regimul de impozit pe veniturile microîntreprinderilor (Titlul III din Codul fiscal) e un regim separat de cel special pentru organizații nonprofit (art. 15, Titlul II). Întrebarea dacă un ONG se poate încadra la micro nu are un răspuns de tip „da" sau „nu" simplu — depinde de condițiile generale de eligibilitate, dar și de consecința practică a alegerii.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. [...] d) capitalul social al acesteia este deținut de persoane, altele decât statul și unitățile administrativ-teritoriale; [...] g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3); [...] i) a depus în termen situațiile financiare anuale, dacă are această obligație potrivit legii."
— art. 47 alin. (1) din Legea 227/2015 (Codul fiscal) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Condiția de eligibilitate cea mai vizibilă pentru un ONG mic: venituri anuale sub echivalentul a **100.000 EUR**, calculate la cursul de la închiderea exercițiului financiar.
- Condiția de salariat (lit. g) e adesea greu de îndeplinit de asociațiile fără angajați, care funcționează doar cu voluntari — legea prevede o excepție la art. 48 alin. (3), pentru situații specifice, dar regula generală cere cel puțin un salariat.
- Lista celor care **nu** intră sub incidența regimului micro (art. 47 alin. 3) cuprinde bănci, asigurători, fonduri de garantare, entități din jocuri de noroc, petrol și gaze — **nu conține nicio excludere explicită a organizațiilor nonprofit**, deci acestea nu sunt excluse ca atare doar pentru forma juridică.
- Impozitul reglementat de Titlul III e **opțional** — persoana juridică română care îndeplinește condițiile poate opta pentru el, nu i se aplică automat.

Important de înțeles: dacă un ONG ar opta pentru impozitul pe veniturile microîntreprinderilor, baza de impozitare s-ar schimba complet — de la „rezultatul fiscal" calculat conform Titlului II (unde se aplică scutirile de la art. 15 pentru cotizații, donații, sponsorizări) la **veniturile totale** ale entității, definite la Titlul III. Practic, cotizațiile, donațiile și sponsorizările, azi neimpozabile necondiționat potrivit art. 15 alin. (2), ar deveni parte din baza impozabilă a regimului micro — de obicei un rezultat mult mai defavorabil decât regimul special de la art. 15. Din acest motiv, opțiunea pentru micro rămâne rar folosită de ONG-uri și trebuie analizată cu atenție, caz cu caz, împreună cu un consultant fiscal, înainte de a fi exercitată.

## Ce se greșește în practică

- Se presupune că un ONG e exclus din start din regimul micro, doar pentru că e organizație nonprofit — legea nu prevede o asemenea excludere pe formă juridică.
- Se ia decizia de a opta pentru micro doar pentru cota mică de impozitare (1%/3% din cifra de afaceri), fără să se calculeze ce se pierde: neimpozabilitatea necondiționată a cotizațiilor/donațiilor de la art. 15 alin. (2).
- Se ignoră condiția de la lit. g) (cel puțin un salariat) la o asociație formată exclusiv din voluntari, fără contract de muncă.

## Ce face iConta.eu

Funcționalitatea de contabilitate ONG din iConta.eu (`core/ong.py`) tratează exclusiv regimul special de la art. 15 din Codul fiscal — clasificarea veniturilor fără scop patrimonial pe grupa 73 și calculul plafonului de scutire pentru veniturile economice. **Aplicația nu are nicio funcție dedicată** verificării eligibilității pentru regimul microîntreprinderilor și nu calculează impozitul pe cifra de afaceri specific acestui regim pentru un ONG — subiectul aparține unui alt titlu al Codului fiscal, netratat de această funcționalitate.

[iConta.eu](/)
