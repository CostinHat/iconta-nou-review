---
title: "Ce trebuie să fac imediat după înființarea firmei"
description: "Obligațiile care curg din primele zile de la înmatriculare — vărsarea capitalului social și înregistrarea fiscală — conform Legii 31/1990 și Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce trebuie să fac imediat după înființarea firmei

Înmatricularea la Registrul Comerțului e doar primul pas. Din acel moment curg termene legale precise, atât pentru capitalul social, cât și pentru înregistrarea fiscală — și nerespectarea lor are sancțiuni proprii.

## Temeiul legal

::: ghid-temei
„Societatea cu răspundere limitată trebuie să verse 30% din valoarea capitalului social subscris nu mai târziu de 3 luni de la data înmatriculării, dar înainte de a începe operațiuni în numele societății, iar diferența de capital social subscris va fi vărsată: a) pentru aportul în numerar, în 12 luni de la data înmatriculării; b) pentru aportul în natură, în termen de cel mult 2 ani de la data înmatriculării."
— Legea 31/1990, art. 9^1 alin. (2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Din acest text și din regulile de înregistrare fiscală rezultă un calendar minim de urmărit imediat după înființare:

- **Cel târziu la 3 luni de la înmatriculare, dar înainte de a începe orice operațiune** pe numele societății: vărsarea a cel puțin 30% din capitalul social subscris.
- **În 12 luni de la înmatriculare**: completarea capitalului social pentru aportul în numerar; **în 2 ani**, pentru aportul în natură.
- În paralel, orice modificare ulterioară a datelor declarate fiscal la înființare (sediu, obiect de activitate, reprezentant etc.) trebuie adusă la cunoștința organului fiscal **în 15 zile** de la data producerii ei, prin declarație de mențiuni (Legea 207/2015, art. 88 alin. (1)).
- Opțiunile fiscale ale firmei nou-înființate (aplicarea regimului de microîntreprindere, înregistrarea în scopuri de TVA) se stabilesc de la același moment al înființării și au propriile termene și condiții, distincte de cele privind capitalul social.

## Ce se greșește în practică

- Se începe facturarea sau se derulează operațiuni pe firmă înainte de vărsarea celor 30% din capitalul social, deși legea impune explicit condiția „înainte de a începe operațiuni".
- Se uită complet de diferența de capital social nevărsată la constituire, iar termenele de 12 luni/2 ani trec neobservate.
- Se presupune că mențiunile ulterioare (schimbare de sediu, de exemplu) au același termen de 30 de zile ca declarația inițială de înregistrare fiscală, când termenul corect pentru modificări este de 15 zile.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu urmărește automat termenele de vărsare a capitalului social** — nu există în cod un modul dedicat care să rețină data înmatriculării și să alerteze la apropierea termenelor de 3 luni/12 luni/2 ani prevăzute de Legea 31/1990. Aplicația are un semafor de conformare fiscală (`core/control_fiscal_api.py`) care compară declarațiile fiscale datorate cu cele depuse pe baza vectorului fiscal al firmei, dar acesta pornește de la firma deja înregistrată fiscal, nu acoperă etapele civile/comerciale de după înmatriculare.

[iConta.eu](/)
