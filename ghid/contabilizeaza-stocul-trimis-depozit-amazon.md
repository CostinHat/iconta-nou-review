---
title: "Cum se contabilizează stocul trimis într-un depozit Amazon din alt stat UE?"
description: "Regimul TVA și contabil al mărfii proprii mutate într-un depozit din alt stat membru (tip Amazon FBA): transfer asimilat livrării intracomunitare, cu excepția nontransferurilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează stocul trimis într-un depozit Amazon din alt stat UE?

Când o firmă românească își expediază propria marfă către un depozit dintr-un alt stat membru (tipic pentru vânzătorii care folosesc rețeaua de depozite Amazon — FBA), operațiunea nu este o vânzare, dar Codul fiscal o tratează, în anumite condiții, ca și cum ar fi una: e vorba de un „transfer" de bunuri proprii.

## Temeiul legal

::: ghid-temei
„(10) Este asimilat cu livrarea intracomunitară cu plată transferul de către o persoană impozabilă de bunuri aparținând activității sale economice din România într-un alt stat membru, cu excepția nontransferurilor prevăzute la alin. (12).
(11) Transferul prevăzut la alin. (10) reprezintă expedierea sau transportul oricăror bunuri mobile corporale din România către alt stat membru, de persoana impozabilă sau de altă persoană în contul său, pentru a fi utilizate în scopul desfășurării activității sale economice."
— Codul fiscal (Legea 227/2015), art. 270 alin. (10)-(11) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă mecanica pe care contabilitatea trebuie s-o reflecte:

- Expedierea mărfii proprii către depozitul din alt stat membru este **asimilată unei livrări intracomunitare**, chiar dacă nu există niciun client la celălalt capăt în momentul transportului.
- Bunul rămâne proprietatea aceleiași firme — nu apare o factură de vânzare către un terț, dar operațiunea generează totuși obligații de TVA specifice unei livrări intracomunitare (declarare, posibilă înregistrare în TVA în statul de destinație).
- Excepție: dacă mișcarea se încadrează la unul din cazurile de **nontransfer** de la art. 270 alin. (12) (de exemplu bunuri duse temporar pentru prelucrare și reexpediate, sau pentru vânzarea la distanță efectuată chiar din acel stat conform art. 275 alin. (2)), operațiunea nu e tratată ca transfer și nu declanșează aceste obligații — cel puțin până când vreuna dintre condiții încetează să mai fie îndeplinită (art. 270 alin. (13)).

## Ce se greșește în practică

- Se tratează expedierea mărfii către depozitul Amazon din alt stat ca pe o simplă mișcare fizică de stoc, fără nicio implicație fiscală, pentru că „marfa tot a firmei rămâne".
- Nu se verifică dacă situația concretă se încadrează la unul din cazurile de nontransfer de la alin. (12) — în lipsa acestei verificări, fie se declară inutil un transfer, fie se omite unul real.
- Se ignoră faptul că, odată ce marfa e vândută din depozitul extern, vânzarea ulterioară se supune regulilor fiscale ale statului în care se află stocul, nu celor din România — de multe ori cu obligația de înregistrare în scopuri de TVA acolo.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcționalitate dedicată transferurilor de stoc propriu în alt stat membru**. Modulele de stocuri din aplicație (gestiune cantitativ-valorică și global-valorică, conform OMFP 1802/2014) acoperă mișcările de marfă în interiorul unei singure firme românești — inclusiv transferuri între gestiuni sau depozite interne — dar nu construiesc automat monografia specifică unui transfer intracomunitar asimilat livrării, și nu gestionează o eventuală înregistrare în scopuri de TVA într-un alt stat membru. Contabilizarea unei astfel de operațiuni rămâne, azi, în sarcina contabilului, care înregistrează manual notele contabile și urmărește obligațiile declarative aferente.

[iConta.eu](/)
