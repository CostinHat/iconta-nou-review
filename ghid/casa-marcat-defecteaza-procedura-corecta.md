---
title: "Casa de marcat se defectează: procedura corectă"
description: "Obligațiile exacte la defectarea aparatului de marcat electronic fiscal — registrul special, chitanțele și notificarea distribuitorului — conform OUG 28/1999."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Casa de marcat se defectează: procedura corectă

Defectarea aparatului de marcat electronic fiscal nu oprește activitatea și nu scutește de obligații — legea prevede exact ce trebuie făcut, din momentul constatării defecțiunii.

## Temeiul legal

::: ghid-temei
„(8) În cazul defectării aparatelor de marcat electronice fiscale, până la repunerea în funcțiune a acestora, operatorii economici utilizatori sunt obligați să înregistreze într-un registru special, întocmit în acest sens, toate operațiunile efectuate și să emită chitanțe, în condițiile legii, pentru respectivele operațiuni și facturi, la cererea clientului. [...] (8^1) În cazul prevăzut la alin. (8), operatorii economici utilizatori au obligația să notifice imediat distribuitorul autorizat sau unitatea de service acreditată, astfel încât utilizatorul să poată să facă dovada comunicării notificării la distribuitorul autorizat sau unitatea de service acreditată, în fața organelor de control."
— OUG 28/1999, art. 1 alin. (8) și (8^1) (sursă: anaf_surse/oug_28_1999.html)
:::

Procedura, în ordine:

1. **Notificare imediată** a distribuitorului autorizat care a livrat aparatul, sau a unității de service acreditate a acestuia — în forma stabilită prin contract între părți; legea cere ca utilizatorul să poată **dovedi** comunicarea notificării în fața organelor de control, deci comunicarea trebuie făcută în scris/verificabil, nu doar telefonic informal.
2. **Deschiderea registrului special**, întocmit exact pentru această situație, în care se înregistrează **toate operațiunile efectuate** cât timp aparatul e defect.
3. **Emiterea de chitanțe** pentru operațiunile efectuate în această perioadă, și **facturi la cererea clientului** — activitatea continuă, doar documentul de vânzare se schimbă.
4. Excepția: obligația registrului special nu se aplică transportului în regim de taxi și nici operatorilor care folosesc AMEF integrate în echipamente nesupravegheate.
5. Registrul special și raportul fiscal de închidere zilnică se **arhivează 5 ani**, calculați de la 1 iulie a anului următor încheierii exercițiului financiar.

## Ce se greșește în practică

- Se oprește vânzarea până la repararea aparatului, considerând că nu se poate vinde fără AMEF — legea prevede exact procedura alternativă (registru special + chitanțe), nu întreruperea activității.
- Se anunță verbal defecțiunea, fără nicio urmă scrisă — legea cere ca notificarea să poată fi dovedită la control, deci un simplu telefon fără confirmare nu îndeplinește cerința.
- Se completează registrul special retroactiv, "din memorie", la finalul zilei — corect e înregistrarea operațiunilor pe măsură ce au loc, ca la orice document de evidență operativă.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul dedicat registrului special pentru perioada de defectare a aparatului de marcat — aplicația oferă `core/chitante.py` (`pdf_chitanta()`) pentru emiterea chitanțelor, care poate fi folosită și în această situație, dar înregistrarea operațiunilor în registrul special propriu-zis și notificarea documentată a distribuitorului rămân, azi, în afara funcționalității aplicației.

[iConta.eu](/)
