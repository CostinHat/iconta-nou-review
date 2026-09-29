---
title: "Furnizorul în TVA la încasare omite mențiunea de pe factură: când deduce beneficiarul TVA?"
description: "Tot la plată: dacă furnizorul era înscris în Registrul TVA la încasare la data facturii, lipsa mențiunii nu schimbă regimul, iar beneficiarul deduce TVA doar pe măsură ce plătește."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Furnizorul în TVA la încasare omite mențiunea de pe factură: când deduce beneficiarul TVA?

Beneficiarul deduce TVA **tot la data plății**, nu la data facturii. Dacă furnizorul era înscris în Registrul persoanelor impozabile care aplică sistemul TVA la încasare la data emiterii facturii, lipsa mențiunii „TVA la încasare" nu scoate operațiunea din sistem. Dreptul de deducere al beneficiarului rămâne amânat până plătește factura.

Contează la control: un beneficiar care a dedus integral la primirea facturii, pe motiv că mențiunea lipsea, poate avea deducerea mutată în perioadele în care a plătit efectiv. Mutarea poate aduce și accesorii.

## Temeiul legal

::: ghid-temei
„În situația în care furnizorul/prestatorul este înscris în Registrul persoanelor impozabile care aplică sistemul TVA la încasare la data emiterii unei facturi, dar omite să înscrie mențiunea "TVA la încasare", operațiunea respectivă nefiind exclusă de la aplicarea sistemului TVA la încasare conform prevederilor art. 282 alin. (6) din Codul fiscal, beneficiarul își exercită dreptul de deducere în conformitate cu prevederile art. 297 alin. (2) din Codul fiscal, cu excepția situației în care sunt aplicabile prevederile art. 324 alin. (13) din Codul fiscal."
— HG 1/2016, Normele metodologice ale Codului fiscal, titlul VII, pct. 67 alin. (6) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă care aplică sistemul TVA la încasare conform prevederilor art. 282 alin. (3)-(8) este amânat până la data la care taxa aferentă bunurilor și serviciilor care i-au fost livrate/prestate a fost plătită furnizorului/prestatorului său."
— Codul fiscal (Legea 227/2015), art. 297 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum verifici, pe o factură fără mențiune:

1. **Furnizorul era în Registru la data facturii?** Verificarea se face în Registrul persoanelor impozabile care aplică sistemul TVA la încasare, pentru data emiterii. Dacă da, deducerea e amânată până la plată.
2. **Operațiunea intră în sistem?** Unele operațiuni sunt excluse de lege chiar la un furnizor în TVA la încasare (art. 282 alin. (6) din Codul fiscal): taxarea inversă, livrările scutite, regimurile speciale de la art. 311-313 și livrările către persoane afiliate. Pentru acestea se aplică regulile generale, iar beneficiarul deduce la exigibilitate, potrivit art. 297 alin. (1).
3. **Excepția art. 324 alin. (13).** Dacă furnizorul a fost înscris în Registru din eroarea organelor fiscale și apoi radiat printr-o decizie de îndreptare, pe acea perioadă se aplică regulile generale de exigibilitate, iar deducerea urmează art. 297 alin. (1).
4. **Plățile parțiale.** La plată parțială, taxa deductibilă se determină prin procedeul sutei mărite, aplicat sumei plătite, la cota din factură.

::: ghid-exemplu
SC Exemplu SRL primește în mai 2026 o factură de 10.000 lei plus 2.100 lei TVA (21%) de la un furnizor înscris în Registrul TVA la încasare, dar factura nu are mențiunea. SC Exemplu SRL plătește 6.050 lei în iunie și restul în iulie.

- Mai: TVA de 2.100 lei se înregistrează ca neexigibilă (4428), nu se deduce.
- Iunie: TVA deductibilă = 6.050 x 21/121 = 1.050 lei.
- Iulie: se deduce restul de 1.050 lei.
:::

## Ce se greșește în practică

- Se deduce integral la data facturii pentru că mențiunea lipsește, fără verificarea furnizorului în Registru.
- Se verifică furnizorul în Registru la data plății sau la data înregistrării, nu la data emiterii facturii, cum cere norma.
- Se amână deducerea și pentru operațiuni excluse din sistem, cum sunt cele cu taxare inversă sau livrările scutite.
- Se aplică suta mărită cu o cotă diferită de cea din factură.

## Ce face iConta.eu

Pe factura primită, iConta.eu are o bifă „furnizor cu TVA la încasare”, care amână deducerea: decontul D300 preia taxa deductibilă din plățile alocate facturii, nu din data facturii. La o firmă în regim normal, o astfel de factură nu e contată automat; contabilul o contează din butonul de contabilizare, după ce verifică situația. La salvarea facturii primite, aplicația interoghează ANAF pentru CUI-ul furnizorului și preia statutul TVA la încasare valabil la data emiterii facturii; dacă ANAF nu răspunde, rămâne bifa pusă de contabil. Aplicația nu judecă după lipsa sau prezența mențiunii de pe factură. Fiindcă statutul se interoghează la data emiterii, și pentru facturile mai vechi se aplică regimul furnizorului valabil la momentul emiterii, nu cel de azi.

[iConta.eu](/)
