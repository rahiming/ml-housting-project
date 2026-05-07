import os
import shutil
import subprocess

import google.generativeai as genai

GIT_PATH = shutil.which("git") or "git"


def get_git_diff():
    return subprocess.check_output([GIT_PATH, "diff", "--cached"]).decode("utf-8")  # noqa: S603


def generate_commit_message(diff):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")
    prompt = (
        "Génère un message de commit concis et professionnel "
        f"pour ces changements :\n\n{diff}"
    )
    response = model.generate_content(prompt)
    return response.text.strip()


def ai_commit_push():
    try:
        diff = get_git_diff()
        if not diff:
            print("Aucun changement indexé (staged). Utilise 'git add'.")
            return

        message = generate_commit_message(diff)
        print(f"Message suggéré : {message}")

        # Exécution du commit
        subprocess.run([GIT_PATH, "commit", "-m", message], check=True)  # noqa: S603

        # Push sur develop
        subprocess.run([GIT_PATH, "push", "origin", "develop"], check=True)  # noqa: S603
        print("🚀 Changements poussés sur develop avec succès !")

    except Exception as e:
        print(f"Erreur : {e}")


if __name__ == "__main__":
    ai_commit_push()
