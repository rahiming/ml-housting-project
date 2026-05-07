import os
import subprocess
import google.generativeai as genai

def get_git_diff():
    return subprocess.check_output(["git", "diff", "--cached"]).decode("utf-8")

def generate_commit_message(diff):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Génère un message de commit concis et professionnel pour ces changements :\n\n{diff}"
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
        subprocess.run(["git", "commit", "-m", message], check=True)
        
        # Push sur develop
        subprocess.run(["git", "push", "origin", "develop"], check=True)
        print("🚀 Changements poussés sur develop avec succès !")
        
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    ai_commit_push()