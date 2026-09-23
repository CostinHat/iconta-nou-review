---
title: "TVA la importul de bunuri: când devine exigibilă"
description: Exigibilitatea nu depinde de tratamentul TVA ales (vamă, certificat de amânare sau cost) — e stabilită înaintea acestei alegeri, prin regula de la art. 285, pe care aplicația nu o modelează.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA la importul de bunuri: când devine exigibilă

Întrebarea "când devine exigibilă TVA la import" este independentă de modul în care va fi ulterior tratată taxa (plată la vamă, autolichidare prin certificat de amânare sau cost pentru neplătitori) — exigibilitatea se stabilește înainte, după o regulă proprie, legată de taxele vamale.

## Temeiul legal

::: ghid-temei
„(1) În cazul în care, la import, bunurile sunt supuse taxelor vamale, taxelor agricole sau altor taxe europene similare, stabilite ca urmare a unei politici comune, faptul generator și exigibilitatea taxei pe valoarea adăugată intervin la data la care intervin faptul generator și exigibilitatea respectivelor taxe europene.
(2) În cazul în care, la import, bunurile nu sunt supuse taxelor europene prevăzute la alin. (1), faptul generator și exigibilitatea taxei pe valoarea adăugată intervin la data la care ar interveni faptul generator și exigibilitatea acelor taxe europene dacă bunurile importate ar fi fost supuse unor astfel de taxe."

— Codul fiscal (Legea 227/2015 consolidat), art. 285 alin. (1)-(2)
:::

Odată stabilită exigibilitatea conform art. 285, ea rămâne reperul de la care se raportează obligațiile ulterioare: plata la vamă (art. 326 alin. 3), sau, pentru firmele cu certificat de amânare, includerea taxei ca deja colectată și deductibilă „în decontul aferent perioadei fiscale în care ia naștere exigibilitatea" (art. 299 alin. 1 lit. d). Cu alte cuvinte, exigibilitatea nu e un detaliu tehnic separat de restul procesului — ea fixează perioada fiscală relevantă pentru toate pasurile care urmează.

## Ce se greșește în practică

- Se raportează TVA la import în luna în care s-a făcut plata la vamă, presupunând că plata și exigibilitatea coincid întotdeauna — regula de la art. 285 leagă exigibilitatea de faptul generator al taxelor vamale, nu neapărat de data plății.
- Se ignoră situația bunurilor aflate într-un regim vamal special (de exemplu antrepozitare), unde exigibilitatea se amână până la ieșirea din regim, conform art. 285 alin. (3).
- Se presupune că firmele cu certificat de amânare nu au nicio dată de exigibilitate de urmărit, deși tocmai perioada fiscală în care ia naștere exigibilitatea este cea în care taxa trebuie înscrisă, atât colectată, cât și deductibilă, conform art. 299 alin. (1) lit. d).

## Ce face iConta.eu

Motorul de calcul al importului nu are niciun parametru de dată — primește doar sume (valoare vamală, taxe, accize, accesorii) și o cotă de TVA declarată explicit, și întoarce baza de TVA și taxa aferentă. **Stabilirea momentului exigibilității, conform art. 285, nu este modelată în aplicație** și rămâne integral în responsabilitatea contabilului, care trebuie să identifice perioada fiscală corectă pe baza documentelor vamale ale operațiunii, indiferent de modul de tratare a TVA (vamă, certificat de amânare sau cost) calculat ulterior de aplicație.

[iConta.eu](/)
