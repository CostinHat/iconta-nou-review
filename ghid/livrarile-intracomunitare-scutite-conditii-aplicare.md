---
title: Livrările intracomunitare scutite: condiții de aplicare
description: Scutirea de TVA cu drept de deducere la livrarea intracomunitară e condiționată cumulativ de codul de TVA valid al cumpărătorului și de dovada transportului în alt stat membru; fără oricare din ele, operațiunea nu e scutită și se facturează cu TVA.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Livrările intracomunitare scutite: condiții de aplicare

O livrare de bunuri către un client dintr-un alt stat membru nu e scutită de TVA doar pentru că traversează o graniță intracomunitară. Scutirea e condiționată, iar condițiile sunt cumulative — lipsa oricăreia le anulează pe amândouă.

## Temeiul legal

::: ghid-temei
„Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” — CF art. 294 alin. (2) lit. a) (sursă: `cod_fiscal_227_2015_consolidat.txt`, L18397+, verificat în dosarul F050).
:::

## Cele două condiții

**Codul de TVA valid al cumpărătorului**, comunicat furnizorului înainte de operațiune. Nu contează dacă firma cumpărătoare există și e înregistrată fiscal în statul ei — contează dacă are cod valid **pentru operațiuni intracomunitare**, verificabil în VIES. Un cod suspendat, anulat sau neînregistrat în VIES rupe condiția.

**Dovada transportului** bunurilor din România către celălalt stat membru. Fără ea, operațiunea nu poate fi susținută ca livrare intracomunitară, indiferent cât de valid e codul cumpărătorului.

Ambele condiții sunt de fond, nu formale: lipsa oricăreia înseamnă că scutirea nu se aplică, iar operațiunea se facturează cu TVA din România, ca o livrare internă.

## Ce se greșește în practică

Cea mai frecventă greșeală e verificarea codului de TVA **după** emiterea facturii, nu înainte — moment în care, dacă a fost anulat între timp, corectarea presupune deja stornare și reemitere. A doua greșeală frecventă e tratarea „am trimisă cu curier” ca dovadă suficientă de transport, fără document care să lege expres livrarea de operațiune. A treia: se aplică scutirea și pentru operațiuni care, de fapt, intră sub incidența art. 307 alin. (3)-(6) — beneficiarul e obligat la plată dintr-un alt motiv decât o livrare intracomunitară — ceea ce produce încadrare greșită atât în evidență, cât și în D390.

## Ce face iConta.eu

Ecranul de operațiune „Extern” — livrare/prestare intracomunitară — cere codul de TVA al clientului și, opțional, dovada transportului. La emiterea unei facturi cu cod de TVA de prefix non-românesc, sistemul verifică automat starea codului în VIES și afișează rezultatul (valid/invalid) sau avertismentul „VIES indisponibil” dacă serviciul Comisiei Europene nu răspunde. Validarea celor două condiții ale scutirii — cod valid + dovadă transport — e verificată explicit de motorul intern al operațiunilor intracomunitare; când oricare lipsește, sistemul returnează o eroare clară: operațiunea trebuie facturată cu TVA, nu tratată ca livrare intracomunitară scutită.

[iConta.eu](/)
