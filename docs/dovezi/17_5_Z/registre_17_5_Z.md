# Registre 17.5-Z (unelte) — rezumat factual

- Baza: main `254b3ec1ed33a31bab7dd3b3f6e7dd984cecc3d6` (J3 publicat); `baza.json` (1907 teste, 2 picate pe bază); P_Z `f66d0a524f86ad97dfc4304b4d0130c19d8947d7`.
- C (commitul verificat): `6ec19b133771319162505c3fa761e3018bd62312`. Prima rulare completă pe `10258dbaac1778c6545b0e7209efd78ca21a9fda`: ROȘU (1 test nou invalid, fără aserțiuni); reluare curată; rularea completă finală pe C: VERDE (1982 teste, regresie 0, restanță 2, invalid 0, infra 0, noi_verzi 75).
- Garda permanentă: `core/test_verificator_design_17_5_Z.py` (75 de cazuri, mock-uri/spy-uri), o singură dată în `scripts/poarta_nucleu.txt`.
- Istorice pe C: `core/test_verificator_design_16_7.py` 15 passed / 2 skipped; `core/test_unelte_17_5_U.py` 76 passed.
- Martor negativ în sandbox (API-uri de semnal mock): sursa veche 2 failed (killpg pe grup de PID străin și pe PID refolosit), sursa nouă 2 passed. Mutanți: 10/10 prinși.
- Brutele (loguri, JUnit, mutanți) sunt în raportul extern / ZIP, nu în Git.
