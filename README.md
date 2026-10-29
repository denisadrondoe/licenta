# Licență – Sistem multi-agent pentru planificarea și alocarea task-urilor

Codul proiectului de diplomă. Sistemul lucrează cu:
- **Jira** – planificarea task-urilor (proiectul `SCRUM` de pe `drondoedenisa.atlassian.net`);
- **GitLab** – proiectul de test `licenta-denisa/proiect-test`, din care sistemul doar citește;
- **GitHub** – aici stă codul acesta.

---

## Pornire rapidă (pe orice laptop)

1. Instalează **Python** (bifează „Add python.exe to PATH”) și **Git**.
2. Clonează proiectul:
   ```
   git clone https://github.com/<utilizatorul-tau>/licenta.git
   ```
3. Intră în folderul `licenta` și dă **dublu-click pe `setup.bat`**. Acesta:
   - creează mediul virtual `.venv`;
   - instalează bibliotecile din `requirements.txt` (versiuni fixe – mediul e identic peste tot);
   - creează fișierul `.env` din `.env.example`.
4. Deschide `.env` și completează **tokenurile** (Jira, GitLab) și **cheia API** pentru LLM.
5. Verifică legăturile:
   ```
   .venv\Scripts\activate
   python scripts/test_conexiuni.py
   ```

### Ce este în Git și ce nu

| Ce | În Git? | Pe un laptop nou |
|---|---|---|
| Codul, `config/`, `requirements.txt`, `setup.bat` | Da | vin la clonare |
| `.venv` (mediul instalat) | Nu | îl creează `setup.bat` |
| `.env` (tokenuri, chei) | **Nu, niciodată** | îl creează `setup.bat`; completezi tokenurile |

---

## Etapa 0 – Pregătire (26 oct – 8 nov)

### Conturi
- [x] Jira: site `drondoedenisa.atlassian.net`, proiect Scrum cu cheia `SCRUM`
- [x] Token API Jira
- [x] GitLab: grupul `licenta-denisa`, proiectul `proiect-test`
- [x] Token GitLab cu permisiunea `read_api`
- [ ] GitHub: cont + repository privat `licenta` (fără README)
- [ ] LLM: cheie API (Anthropic sau Azure OpenAI)

### Mediul de lucru
- [ ] Python, Git, VS Code instalate (`python --version`, `git --version`)
- [ ] Git configurat:
      ```
      git config --global user.name "Denisa Drondoe"
      git config --global user.email "drondoedenisa5@gmail.com"
      ```
- [ ] `setup.bat` rulat, `.env` completat

### Primul upload pe GitHub (o singură dată, din folderul acesta)
```
git init -b main
git add .
git commit -m "Etapa 0: structura proiectului si scripturi de test"
git remote add origin https://github.com/<utilizatorul-tau>/licenta.git
git push -u origin main
```
La primul `push` se deschide o fereastră în care te autentifici în GitHub.
Verifică pe GitHub că fișierul `.env` **nu** apare în listă.

### Testul conexiunilor
```
.venv\Scripts\activate
python scripts/test_conexiuni.py              # doar verificări
python scripts/test_conexiuni.py --creeaza    # creează și un task de test în Jira
```

### Popularea proiectului de test
Creează în Jira 10 task-uri și în GitLab câte un commit pentru fiecare,
„în numele” membrilor echipei fictive, cu cheia Jira în mesaj:
```
cd ..
git clone https://gitlab.com/licenta-denisa/proiect-test.git
cd licenta
.venv\Scripts\activate
python scripts/populeaza_proiect_test.py --repo ../proiect-test
cd ../proiect-test
git push
```
La primul `push` în GitLab se deschide o fereastră de autentificare GitLab.

### Lectură (cu notițe – vor deveni capitolul 2)
- [ ] Wooldridge, *An Introduction to MultiAgent Systems* – primele capitole
- [ ] Guo et al. (2024), survey despre sisteme multi-agent bazate pe LLM
- [ ] Yao et al. (2023), ReAct

---

## Structura proiectului
```
licenta/
├── setup.bat                    pregătește mediul (dublu-click)
├── requirements.txt             bibliotecile, cu versiuni fixe
├── .env.example                 model pentru .env (fără secrete)
├── .gitignore                   ce NU intră în Git (.env, .venv, ...)
├── config/
│   ├── echipa.yaml              echipa fictivă (competențe, capacitate, concedii)
│   └── date_test.yaml           istoricul fictiv al proiectului de test
└── scripts/
    ├── test_conexiuni.py        verifică Jira, GitLab și LLM-ul
    └── populeaza_proiect_test.py  task-uri în Jira + commit-uri în GitLab
```
