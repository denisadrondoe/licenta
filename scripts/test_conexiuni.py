"""Etapa 0 - verifica legaturile cu Jira, GitLab si LLM-ul.

Rulare (din folderul cod-licenta, cu mediul virtual activat):
    python scripts/test_conexiuni.py              # doar verificari (nu modifica nimic)
    python scripts/test_conexiuni.py --creeaza    # creeaza si un task de test in Jira

Fiecare test afiseaza OK sau EROARE, cu un mesaj despre ce trebuie corectat.
"""
import os
import sys
import argparse

from dotenv import load_dotenv

load_dotenv()

VARIABILE = {
    "Jira": ["JIRA_URL", "JIRA_EMAIL", "JIRA_TOKEN", "JIRA_PROJECT"],
    "GitLab": ["GITLAB_URL", "GITLAB_TOKEN", "GITLAB_PROJECT"],
    "LLM": ["ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"],
}


def titlu(text):
    print(f"\n=== {text} ===")


def ok(text):
    print(f"  [OK]     {text}")


def eroare(text):
    print(f"  [EROARE] {text}")


def verifica_env():
    titlu("Fisierul .env")
    lipsa = [v for grup in VARIABILE.values() for v in grup if not os.getenv(v)]
    if lipsa:
        eroare("Lipsesc variabilele: " + ", ".join(lipsa))
        print("           Copiaza .env.example ca .env si completeaza valorile.")
        return False
    ok("Toate variabilele sunt completate")
    return True


def gaseste_camp_story_points(jira):
    """Numele campului difera intre tipurile de proiecte Jira."""
    for camp in jira.fields():
        if camp["name"].lower() in ("story point estimate", "story points"):
            return camp["id"], camp["name"]
    return None, None


def test_jira(creeaza_task):
    titlu("Jira")
    try:
        from jira import JIRA
        jira = JIRA(server=os.getenv("JIRA_URL"),
                    basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_TOKEN")))
        ok(f"Conectat ca: {jira.current_user()}")
    except Exception as e:
        eroare(f"Nu ma pot conecta: {e}")
        print("           Verifica JIRA_URL, JIRA_EMAIL si JIRA_TOKEN.")
        return False

    cheie = os.getenv("JIRA_PROJECT")
    try:
        proiect = jira.project(cheie)
        ok(f"Proiect gasit: {proiect.key} - {proiect.name}")
    except Exception:
        eroare(f"Proiectul cu cheia '{cheie}' nu exista sau nu ai acces la el.")
        return False

    camp_id, camp_nume = gaseste_camp_story_points(jira)
    if camp_id:
        ok(f"Camp story points: '{camp_nume}' (id: {camp_id})")
    else:
        eroare("Nu am gasit campul de story points. Adauga-l din setarile proiectului.")

    try:
        membri = jira._get_json("user/assignable/search", params={"project": cheie, "maxResults": 50})
        nume = [u["displayName"] for u in membri]
        ok(f"Membri care pot primi task-uri ({len(nume)}): " + ", ".join(nume))
    except Exception as e:
        eroare(f"Nu pot citi membrii proiectului: {e}")

    if creeaza_task:
        try:
            task = jira.create_issue(fields={
                "project": {"key": cheie},
                "summary": "Task de test creat din Python (Etapa 0)",
                "issuetype": {"name": "Task"},
            })
            ok(f"Task creat: {task.key} -> {os.getenv('JIRA_URL')}/browse/{task.key}")
        except Exception as e:
            eroare(f"Nu am putut crea task-ul: {e}")
            return False
    return True


def test_gitlab():
    titlu("GitLab")
    try:
        import gitlab
        gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), private_token=os.getenv("GITLAB_TOKEN"))
        proiect = gl.projects.get(os.getenv("GITLAB_PROJECT"))
        ok(f"Proiect gasit: {proiect.path_with_namespace}")
    except Exception as e:
        eroare(f"Nu pot accesa proiectul: {e}")
        print("           Verifica GITLAB_TOKEN (permisiunea read_api) si GITLAB_PROJECT.")
        return False

    try:
        commituri = proiect.commits.list(per_page=5, get_all=False)
        if not commituri:
            ok("Conexiune OK, dar proiectul nu are inca niciun commit.")
        for c in commituri:
            ok(f"Commit: {c.author_name:<18} | {c.title}")
    except Exception as e:
        eroare(f"Nu pot citi commit-urile: {e}")
        return False
    return True


def test_llm():
    titlu("LLM (Anthropic)")
    try:
        from anthropic import Anthropic
        client = Anthropic()  # citeste ANTHROPIC_API_KEY din mediu
        raspuns = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL"),
            max_tokens=50,
            messages=[{"role": "user", "content": "Raspunde doar cu: Conexiune reusita."}],
        )
        ok(f"Raspuns: {raspuns.content[0].text.strip()}")
        return True
    except Exception as e:
        eroare(f"Apelul a esuat: {e}")
        print("           Verifica ANTHROPIC_API_KEY, creditul din cont si ANTHROPIC_MODEL.")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creeaza", action="store_true", help="creeaza un task de test in Jira")
    args = parser.parse_args()

    if not verifica_env():
        sys.exit(1)
    rezultate = {
        "Jira": test_jira(args.creeaza),
        "GitLab": test_gitlab(),
        "LLM": test_llm(),
    }
    titlu("Rezumat")
    for nume, rezultat in rezultate.items():
        (ok if rezultat else eroare)(nume)
    if all(rezultate.values()):
        print("\nTotul functioneaza. Etapa 0 - partea tehnica este incheiata!")


if __name__ == "__main__":
    main()
