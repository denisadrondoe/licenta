"""Etapa 0 - populeaza proiectul de test cu un istoric fictiv.

Pentru fiecare task din config/date_test.yaml:
  1. creeaza task-ul in Jira (cu story points si asignare, daca e posibil),
  2. face un commit in repository-ul local al proiectului de test,
     "in numele" membrului, cu cheia Jira in mesaj (ex. "SCRUM-3 API pentru autentificare").

Pasi:
  1. Cloneaza proiectul de test:   git clone https://gitlab.com/licenta-denisa/proiect-test.git
  2. Ruleaza scriptul:             python scripts/populeaza_proiect_test.py --repo ../proiect-test
  3. Urca commit-urile in GitLab:  cd ../proiect-test  si apoi  git push

Optiuni:
  --fara-jira   nu contacteaza Jira; foloseste chei fictive SCRUM-1, SCRUM-2, ...
                (util ca sa testezi partea de Git fara conturi)
"""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

import yaml
from dotenv import load_dotenv

RADACINA = Path(__file__).resolve().parent.parent
load_dotenv(RADACINA / ".env")


def citeste_yaml(nume):
    with open(RADACINA / "config" / nume, encoding="utf-8") as f:
        return yaml.safe_load(f)


def conecteaza_jira():
    from jira import JIRA
    return JIRA(server=os.getenv("JIRA_URL"),
                basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_TOKEN")))


def camp_story_points(jira):
    for camp in jira.fields():
        if camp["name"].lower() in ("story point estimate", "story points"):
            return camp["id"]
    return None


def gaseste_account_id(jira, membru, asignabili):
    """Cauta membrul in Jira dupa email, apoi dupa nume."""
    try:
        gasiti = jira.search_users(query=membru["email"], maxResults=1)
        if gasiti:
            return gasiti[0].accountId
    except Exception:
        pass
    for u in asignabili:
        if u.get("displayName", "").lower() == membru["nume"].lower():
            return u["accountId"]
    return None


def creeaza_task_jira(jira, cheie_proiect, task, sp_camp, account_id):
    issue = jira.create_issue(fields={
        "project": {"key": cheie_proiect},
        "summary": task["titlu"],
        "issuetype": {"name": "Task"},
    })
    if sp_camp:
        try:
            issue.update(fields={sp_camp: task["story_points"]})
        except Exception as e:
            print(f"    (story points nesetate pentru {issue.key}: {e})")
    if account_id:
        try:
            issue.update(fields={"assignee": {"accountId": account_id}})
        except Exception as e:
            print(f"    (asignare esuata pentru {issue.key}: {e})")
    return issue.key


def scrie_fisier(repo, cale, cheie, task, membru):
    """Creeaza sau completeaza un fisier, cu un comentariu potrivit extensiei."""
    fisier = repo / cale
    fisier.parent.mkdir(parents=True, exist_ok=True)
    ext = fisier.suffix.lower()
    if ext in (".py", ".yml", ".yaml") or fisier.name == "Dockerfile":
        comentariu = "#"
    elif ext == ".sql":
        comentariu = "--"
    else:
        comentariu = "//"
    with open(fisier, "a", encoding="utf-8") as f:
        f.write(f"{comentariu} {cheie}: {task['titlu']} ({membru['nume']})\n")


def git(repo, *argumente, env=None):
    subprocess.run(["git", *argumente], cwd=repo, check=True, env=env,
                   stdout=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="calea catre clona locala a proiectului de test")
    parser.add_argument("--fara-jira", action="store_true", help="nu contacta Jira (chei fictive)")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        sys.exit(f"'{repo}' nu este un repository Git. Cloneaza mai intai proiectul de test.")

    echipa = {m["nume"]: m for m in citeste_yaml("echipa.yaml")["echipa"]}
    taskuri = citeste_yaml("date_test.yaml")["taskuri"]
    cheie_proiect = os.getenv("JIRA_PROJECT", "SCRUM")

    jira = sp_camp = None
    asignabili = []
    if not args.fara_jira:
        jira = conecteaza_jira()
        sp_camp = camp_story_points(jira)
        asignabili = jira._get_json("user/assignable/search",
                                    params={"project": cheie_proiect, "maxResults": 50})

    mapare = {}
    for i, task in enumerate(taskuri, start=1):
        membru = echipa.get(task["membru"])
        if membru is None:
            print(f"  Membrul '{task['membru']}' nu exista in echipa.yaml - task sarit.")
            continue

        if jira:
            account_id = gaseste_account_id(jira, membru, asignabili)
            cheie = creeaza_task_jira(jira, cheie_proiect, task, sp_camp, account_id)
            asignat = "asignat" if account_id else "NEASIGNAT (membrul nu e in Jira)"
        else:
            cheie = f"{cheie_proiect}-{i}"
            asignat = "fara Jira"

        for cale in task["fisiere"]:
            scrie_fisier(repo, cale, cheie, task, membru)

        env = dict(os.environ,
                   GIT_AUTHOR_NAME=membru["nume"], GIT_AUTHOR_EMAIL=membru["email"],
                   GIT_COMMITTER_NAME=membru["nume"], GIT_COMMITTER_EMAIL=membru["email"])
        git(repo, "add", "-A")
        git(repo, "commit", "-m", f"{cheie} {task['titlu']}", env=env)

        mapare[cheie] = {"titlu": task["titlu"], "membru": membru["nume"]}
        print(f"  {cheie:<9} {task['titlu']:<35} {membru['nume']:<17} {asignat}")

    with open(RADACINA / "mapare_taskuri.json", "w", encoding="utf-8") as f:
        json.dump(mapare, f, ensure_ascii=False, indent=2)

    print(f"\nGata: {len(mapare)} task-uri si commit-uri.")
    print(f"Urmatorul pas:  cd \"{repo}\"  si apoi  git push")


if __name__ == "__main__":
    main()
