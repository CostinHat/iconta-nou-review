---
title: "Impozitarea veniturilor birourilor notariale"
description: "De ce veniturile notarilor publici se impozitează ca venituri din profesii liberale, conform Titlului IV din Codul fiscal, nu ca impozit pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitarea veniturilor birourilor notariale

Notarii publici nu se impozitează ca o societate comercială obișnuită, cu impozit pe profit sau pe veniturile microîntreprinderilor — activitatea notarială e o profesie liberală, iar veniturile obținute din exercitarea ei intră sub regimul „venituri din activități independente", reglementat de Titlul IV din Codul fiscal (impozitul pe venit), nu sub Titlul II (impozitul pe profit).

## Temeiul legal

::: ghid-temei
„Articolul 67 Definirea veniturilor din activități independente (1) Veniturile din activități independente cuprind veniturile din activități de producție, comerț, prestări de servicii și veniturile din profesii liberale, realizate în mod individual și/sau într-o formă de asociere, inclusiv din activități adiacente. [...] (2) Constituie venituri din profesii liberale veniturile obținute din prestarea de servicii cu caracter profesional, potrivit actelor normative speciale care reglementează organizarea și exercitarea profesiei respective."
— Legea nr. 227/2015 privind Codul fiscal, art. 67 alin. (1) și (2), Capitolul II, Titlul IV (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Codul fiscal definește „profesiile liberale" ca fiind „acele ocupații exercitate pe cont propriu de persoane fizice, potrivit actelor normative speciale care reglementează organizarea și exercitarea profesiei respective" (art. 7 pct. 34) — definiție sub care se încadrează activitatea notarială, reglementată prin legea specială a profesiei de notar public. Din coroborarea celor două articole rezultă:

- **Veniturile obținute de notarul public** din exercitarea profesiei (onorarii pentru autentificări, succesiuni, alte acte notariale) sunt venituri din profesii liberale, o subcategorie a veniturilor din activități independente (art. 67 alin. 1-2), impuse conform regulilor din Titlul IV, nu conform impozitului pe profit din Titlul II.
- **Veniturile adiacente** primite de notar — de exemplu, remunerația pentru administrarea unei mase patrimoniale în calitate de fiduciar — se cumulează cu veniturile din activitatea de bază și se impozitează împreună cu acestea, conform Cap. II al Titlului IV, nu separat.
- Regimul specific de calcul al bazei impozabile (sistem real sau alte reguli aplicabile veniturilor din activități independente) urmează prevederile generale ale Capitolului II, Titlul IV, aplicabile tuturor profesiilor liberale, nu o regulă distinctă doar pentru notari.

## Ce se greșește în practică

- Se tratează biroul notarial ca pe o firmă obișnuită, aplicându-i regulile de impozit pe profit sau pe veniturile microîntreprinderilor — activitatea notarială, ca profesie liberală, e supusă regimului veniturilor din activități independente (Titlul IV), distinct de impozitul pe profit al persoanelor juridice.
- Se omite cumularea veniturilor adiacente (de exemplu, remunerația de fiduciar) cu veniturile din activitatea notarială de bază, la calculul impozitului — art. 67 combinat cu prevederile privind veniturile adiacente cere impunerea cumulată, nu tratarea lor ca venituri separate, cu regim fiscal diferit.
- Se confundă calitatea de contribuabil persoană fizică (notarul, ca titular al profesiei liberale) cu forma de organizare a activității (birou individual sau societate profesională) — forma de organizare nu schimbă, prin ea însăși, natura veniturilor ca fiind din profesii liberale.

## Ce face iConta.eu

Aplicația oferă evidența contabilă generală, dar la data acestui ghid **nu are un modul specific** dedicat calculului impozitului pe venit pentru profesii liberale (inclusiv notari), cu particularitățile Titlului IV din Codul fiscal — funcționalitatea de calcul al impozitului pe profit/microîntreprinderi din `core/d100.py` acoperă persoanele juridice supuse Titlului II, nu regimul veniturilor din activități independente al persoanelor fizice care exercită o profesie liberală. Calculul impozitului pe venit pentru un birou notarial individual rămâne, la această dată, în afara funcționalităților specifice ale aplicației.

[iConta.eu](/)
