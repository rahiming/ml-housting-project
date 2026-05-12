"""Génère le guide MLFlow au format .docx."""

import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

doc = Document()


# ── Helpers ───────────────────────────────────────────────────────────────────
def set_font(run, bold=False, italic=False, size=11, color=None, name="Calibri"):
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = name
    if color:
        run.font.color.rgb = RGBColor(*color)


def h(level, text):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(14 if level <= 2 else 8)
    p.paragraph_format.space_after = Pt(4)
    return p


def para(text="", bold_prefix=None, indent=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if bold_prefix:
        r = p.add_run(bold_prefix)
        set_font(r, bold=True)
    if text:
        r = p.add_run(text)
        set_font(r)
    return p


def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.5 + level * 0.5)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    set_font(r)


def numbered(text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    set_font(r)


def shade_para(p, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    p._p.get_or_add_pPr().append(shd)


def code(lines):
    for line in lines.split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(line if line else " ")
        r.font.name = "Courier New"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x1E, 0x1E, 0x1E)
        shade_para(p, "F0F0F0")
    doc.add_paragraph()


def tip(label, text, fill="FFF3CD"):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r1 = p.add_run(label + "  ")
    set_font(
        r1,
        bold=True,
        color=(0x85, 0x63, 0x04) if fill == "FFF3CD" else (0x0C, 0x54, 0x6D),
    )
    r2 = p.add_run(text)
    set_font(r2, color=(0x49, 0x33, 0x00) if fill == "FFF3CD" else (0x0C, 0x54, 0x6D))
    shade_para(p, fill)


# ═══════════════════════════════════════════════════════════════════════════════
# TITRE
# ═══════════════════════════════════════════════════════════════════════════════
tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tp.paragraph_format.space_before = Pt(60)
r = tp.add_run("Guide d'intégration MLFlow")
r.bold = True
r.font.size = Pt(26)
r.font.name = "Calibri"
r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

sp = doc.add_paragraph()
sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sp.add_run("Projet fil rouge — Industrialisation ML")
r.font.size = Pt(14)
r.font.name = "Calibri"
r.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

sp2 = doc.add_paragraph()
sp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sp2.add_run("Traçabilité des expériences avec MLFlow")
r.font.size = Pt(13)
r.italic = True
r.font.name = "Calibri"
r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# SOMMAIRE
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Sommaire")
toc = [
    ("Partie 1", "Pourquoi MLFlow ? Concepts fondamentaux"),
    ("Partie 2", "Installation et configuration"),
    (
        "Partie 3",
        "Intégrer MLFlow dans le pipeline principal (src/training/pipeline.py)",
    ),
    ("Partie 4", "Intégrer MLFlow dans le notebook 02 (modèles A/B)"),
    ("Partie 5", "Lancer l'interface MLFlow UI"),
    ("Partie 6", "Lire et interpréter les résultats"),
    ("Partie 7", "MLFlow Model Registry (niveau avancé)"),
    ("Partie 8", "Récapitulatif des fichiers modifiés"),
    ("Annexe", "Aide-mémoire des commandes MLFlow"),
]
for num, title in toc:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r1 = p.add_run(num + "  —  ")
    r1.bold = True
    r1.font.size = Pt(11)
    r1.font.name = "Calibri"
    r2 = p.add_run(title)
    r2.font.size = Pt(11)
    r2.font.name = "Calibri"

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 1 — POURQUOI MLFLOW
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 1 — Pourquoi MLFlow ? Concepts fondamentaux")
para(
    "En machine learning, entraîner un modèle est rarement une action unique. "
    "On relance le pipeline plusieurs fois avec des paramètres différents, on compare les "
    "résultats, on décide lequel mettre en production. Sans outil dédié, cette gestion "
    "devient vite chaotique : des fichiers JSON dispersés, des noms de modèles inventés au "
    "fil des runs, aucun moyen rapide de retrouver quel jeu de paramètres a donné le meilleur "
    "résultat."
)
para(
    "MLFlow est l'outil standard de l'industrie pour résoudre ce problème. Il enregistre "
    "automatiquement chaque expérience d'entraînement et expose une interface web pour les comparer."
)

h(2, "1.1  Les 4 composants de MLFlow")
concepts = [
    (
        "MLFlow Tracking",
        "Enregistre les paramètres, métriques et artefacts de chaque run. C'est la partie centrale de ce guide.",
    ),
    (
        "MLFlow Projects",
        "Permet de packager un projet ML de manière reproductible (fichier MLproject). Non utilisé ici.",
    ),
    (
        "MLFlow Models",
        "Format standardisé pour sauvegarder et charger des modèles, quel que soit le framework.",
    ),
    (
        "MLFlow Model Registry",
        "Registre centralisé pour versionner et promouvoir les modèles (Staging → Production). Abordé en Partie 7.",
    ),
]
for name, desc in concepts:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Cm(0.5)
    r1 = p.add_run("▸  " + name + " : ")
    set_font(r1, bold=True, color=(0x1F, 0x49, 0x7D))
    r2 = p.add_run(desc)
    set_font(r2)

h(2, "1.2  Vocabulaire essentiel")
vocab = [
    (
        "Experiment",
        'Groupe de runs liés à un même objectif. Ex : "housing_price_prediction".',
    ),
    ("Run", "Une exécution unique du pipeline. Chaque python main.py crée un run."),
    (
        "Parameter",
        "Valeur fixée avant l'entraînement. Ex : n_estimators=100, random_state=42.",
    ),
    (
        "Metric",
        "Valeur mesurée après l'entraînement. Ex : mae=0.45, rmse=0.62, r2=0.81.",
    ),
    (
        "Artifact",
        "Fichier produit par le run. Ex : le modèle .joblib, le fichier de métriques JSON.",
    ),
    ("Tag", "Métadonnée libre. Ex : auteur, version du dataset."),
]
for term, definition in vocab:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.5)
    r1 = p.add_run(term.ljust(14))
    set_font(r1, bold=True, name="Courier New", size=10)
    r2 = p.add_run(" — " + definition)
    set_font(r2)

h(2, "1.3  Ce que MLFlow change dans ce projet")
para("Avant MLFlow (situation actuelle du projet) :")
bullet(
    "Les métriques sont dans artifacts/metrics/metrics_v1.json, metrics_v2.json, etc."
)
bullet("Pour comparer deux runs, il faut ouvrir chaque fichier JSON manuellement.")
bullet("Aucune trace des paramètres utilisés pour entraîner chaque modèle.")
para("Après intégration de MLFlow :")
bullet(
    "Chaque run est enregistré automatiquement avec ses paramètres, métriques et modèle."
)
bullet("Une interface web (mlflow ui) affiche un tableau comparatif de tous les runs.")
bullet("Le meilleur modèle est identifiable en un clic sans toucher aux fichiers.")
bullet("Les fichiers JSON existants sont conservés — MLFlow s'ajoute, ne remplace pas.")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 2 — INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 2 — Installation et configuration")

h(2, "2.1  Installer MLFlow")
para("Dans le terminal, avec l'environnement virtuel activé :")
code("pip install mlflow==2.22.0")
para("Ajouter à requirements.txt (racine du projet) :")
code("mlflow==2.22.0")
tip(
    "ℹ️ Note :",
    "MLFlow n'est PAS ajouté à backend/requirements.txt. "
    "Le backend Render charge uniquement les .joblib déjà entraînés — "
    "MLFlow est un outil de développement local uniquement.",
)

h(2, "2.2  Mettre à jour .gitignore")
para("Vérifier que .gitignore contient (ou ajouter) :")
code("# MLFlow\nmlruns/\nmlartifacts/")
para(
    "Le dossier mlruns/ est la base de données locale de MLFlow. "
    "Il peut être volumineux et ne doit pas être commité dans Git."
)

h(2, "2.3  Vérifier l'installation")
code('python -c "import mlflow; print(mlflow.__version__)"')
para("Résultat attendu : 2.22.0")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 3 — PIPELINE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 3 — Intégrer MLFlow dans le pipeline principal")
para(
    "Le fichier à modifier est src/training/pipeline.py. "
    "C'est lui qui orchestre chargement des données → entraînement → évaluation → sauvegarde. "
    "On va envelopper les étapes d'entraînement et d'évaluation dans un mlflow.start_run() "
    "pour tout tracer automatiquement."
)

h(2, "3.1  Comprendre la structure actuelle")
para("La fonction run_pipeline() réalise aujourd'hui :")
numbered("Chargement des données avec load_housing_data()")
numbered("Séparation features/target, puis split train/test")
numbered("Entraînement du modèle avec train_model()")
numbered("Évaluation avec evaluate_model() → mae, rmse, r2")
numbered("Sauvegarde du .joblib et du .json des métriques dans artifacts/")

h(2, "3.2  Code AVANT modification (extrait de pipeline.py)")
code(
    "# VERSION ACTUELLE — src/training/pipeline.py (extrait)\n"
    "\n"
    "import json\n"
    "import logging\n"
    "from pathlib import Path\n"
    "import joblib\n"
    "\n"
    'def run_pipeline(artifacts_dir: str = "artifacts", version: str = "") -> dict:\n'
    "    ...\n"
    "    model   = train_model(X_train, y_train)\n"
    "    metrics = evaluate_model(model, X_test, y_test)\n"
    "\n"
    "    joblib.dump(model, model_file)\n"
    "    joblib.dump(model, latest_path)\n"
    "\n"
    '    with open(metrics_file, "w", encoding="utf-8") as f:\n'
    "        json.dump(metrics, f, indent=2)\n"
    "\n"
    "    return metrics"
)

h(2, "3.3  Code APRÈS modification (version complète à remplacer)")
para("Remplacer l'intégralité de src/training/pipeline.py par le code suivant :")
code(
    '"""Orchestration du pipeline ML avec tracking MLFlow."""\n'
    "\n"
    "import json\n"
    "import logging\n"
    "from pathlib import Path\n"
    "\n"
    "import joblib\n"
    "import mlflow\n"
    "import mlflow.sklearn\n"
    "\n"
    "from src.common.features import split_features_target, split_train_test\n"
    "from src.training.data import load_housing_data\n"
    "from src.training.evaluate import evaluate_model\n"
    "from src.training.train import train_model\n"
    "\n"
    "logger = logging.getLogger(__name__)\n"
    "\n"
    'MLFLOW_EXPERIMENT = "housing_price_prediction"\n'
    "\n"
    "\n"
    'def get_next_version(artifacts_dir: str = "artifacts") -> str:\n'
    '    """Calcule la prochaine version de modele disponible."""\n'
    "    path = Path(artifacts_dir).resolve()\n"
    '    models_path = path / "models"\n'
    "    if not models_path.exists():\n"
    '        return "v1"\n'
    "    existing_versions = []\n"
    '    for model_file in models_path.glob("model_v*.joblib"):\n'
    "        try:\n"
    '            version_number = int(model_file.stem.split("_v")[-1])\n'
    "            existing_versions.append(version_number)\n"
    "        except (ValueError, IndexError):\n"
    '            logger.warning("Nom de modele ignore : %s", model_file)\n'
    "    next_version = max(existing_versions, default=0) + 1\n"
    '    return f"v{next_version}"\n'
    "\n"
    "\n"
    'def run_pipeline(artifacts_dir: str = "artifacts", version: str = "") -> dict:\n'
    '    """Execute le pipeline complet avec tracking MLFlow."""\n'
    "    artifacts_path = Path(artifacts_dir).resolve()\n"
    '    models_path    = artifacts_path / "models"\n'
    '    metrics_path   = artifacts_path / "metrics"\n'
    "    models_path.mkdir(parents=True, exist_ok=True)\n"
    "    metrics_path.mkdir(parents=True, exist_ok=True)\n"
    "\n"
    "    # ── Chargement des données ────────────────────────────────────────\n"
    "    df = load_housing_data()\n"
    "    X, y = split_features_target(df)\n"
    "    X_train, X_test, y_train, y_test = split_train_test(X, y)\n"
    "\n"
    "    # ── MLFlow : créer / réutiliser l'expérience ──────────────────────\n"
    "    mlflow.set_experiment(MLFLOW_EXPERIMENT)\n"
    "\n"
    '    with mlflow.start_run(run_name=f"run_{version}" if version else None):\n'
    "\n"
    "        # 1. Paramètres\n"
    '        mlflow.log_param("model_type",   "RandomForestRegressor")\n'
    '        mlflow.log_param("n_estimators", 100)\n'
    '        mlflow.log_param("random_state", 42)\n'
    '        mlflow.log_param("version",      version or "latest")\n'
    '        mlflow.log_param("train_size",   len(X_train))\n'
    '        mlflow.log_param("test_size",    len(X_test))\n'
    "\n"
    "        # 2. Entraînement\n"
    "        model = train_model(X_train, y_train)\n"
    '        logger.info("Modele entraine avec succes.")\n'
    "\n"
    "        # 3. Métriques\n"
    "        metrics = evaluate_model(model, X_test, y_test)\n"
    '        mlflow.log_metric("mae",  metrics["mae"])\n'
    '        mlflow.log_metric("rmse", metrics["rmse"])\n'
    '        mlflow.log_metric("r2",   metrics["r2"])\n'
    '        logger.info("Metriques loggees : %s", metrics)\n'
    "\n"
    "        # 4. Sauvegarde joblib (chemin existant conservé)\n"
    '        suffix       = f"_{version}" if version else ""\n'
    '        model_file   = models_path  / f"model{suffix}.joblib"\n'
    '        metrics_file = metrics_path / f"metrics{suffix}.json"\n'
    "        joblib.dump(model, model_file)\n"
    '        joblib.dump(model, models_path / "model_latest.joblib")\n'
    '        with open(metrics_file, "w", encoding="utf-8") as f:\n'
    "            json.dump(metrics, f, indent=2)\n"
    "\n"
    "        # 5. Artefacts MLFlow\n"
    "        mlflow.sklearn.log_model(\n"
    "            sk_model=model,\n"
    '            artifact_path="model",\n'
    '            registered_model_name=f"housing_{version}" if version else "housing_latest",\n'
    "        )\n"
    '        mlflow.log_artifact(str(metrics_file), artifact_path="metrics")\n'
    '        logger.info("Run MLFlow enregistre avec succes.")\n'
    "\n"
    "    return metrics"
)

h(2, "3.4  Explication des ajouts ligne par ligne")
explanations = [
    (
        "mlflow.set_experiment(MLFLOW_EXPERIMENT)",
        "Crée ou sélectionne l'expérience nommée 'housing_price_prediction'. Tous les runs de ce "
        "projet seront regroupés sous cette expérience dans l'UI.",
    ),
    (
        "with mlflow.start_run(run_name=...):",
        "Ouvre un contexte de run. Tout ce qui est logué à l'intérieur du bloc with est associé "
        "à ce run. À la sortie du with, le run est automatiquement clôturé et enregistré.",
    ),
    (
        "mlflow.log_param(clé, valeur)",
        "Enregistre un paramètre (valeur fixe avant l'entraînement). Utilisé pour n_estimators, "
        "random_state, etc. Affiché dans la colonne 'Parameters' de l'UI.",
    ),
    (
        "mlflow.log_metric(clé, valeur)",
        "Enregistre une métrique numérique (résultat de l'entraînement). Utilisé pour mae, rmse, r2. "
        "Permet la comparaison visuelle entre runs dans l'UI.",
    ),
    (
        "mlflow.sklearn.log_model(..., registered_model_name=...)",
        "Sauvegarde le pipeline sklearn complet comme artefact MLFlow et l'enregistre dans le "
        "Model Registry sous le nom donné.",
    ),
    (
        "mlflow.log_artifact(chemin)",
        "Copie un fichier existant (ici metrics.json) dans le stockage MLFlow pour qu'il soit "
        "visible et téléchargeable depuis l'UI.",
    ),
]
for fn, expl in explanations:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(0.5)
    r1 = p.add_run(fn + "\n")
    set_font(r1, bold=True, name="Courier New", size=9, color=(0x1F, 0x49, 0x7D))
    r2 = p.add_run("    → " + expl)
    set_font(r2, color=(0x40, 0x40, 0x40))

h(2, "3.5  Tester")
para("Dans le terminal (racine du projet) :")
code("python main.py")
para("Un dossier mlruns/ est créé. Résultat attendu dans la console :")
code(
    "INFO | run_pipeline | Modele entraine avec succes.\n"
    "INFO | run_pipeline | Metriques loggees : {'mae': 0.33, 'rmse': 0.51, 'r2': 0.84}\n"
    "INFO | run_pipeline | Run MLFlow enregistre avec succes.\n"
    "Pipeline termine avec succes.\n"
    "Version : v3   MAE : 0.3342   RMSE : 0.5123   R2 : 0.8401"
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 4 — NOTEBOOK 02
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 4 — Intégrer MLFlow dans le notebook 02 (modèles A/B)")
para(
    "Le notebook notebooks/02_train_ab_models.ipynb entraîne deux modèles : "
    "le modèle A (RandomForest, champion) et le modèle B (GradientBoosting, challenger). "
    "C'est l'endroit idéal pour comparer directement deux architectures dans MLFlow."
)

h(2, "4.1  Cellule 1 — Ajouter l'import mlflow")
para("Modifier la cellule 1 (imports) pour ajouter mlflow :")
code(
    "# Cellule 1 - Charger les bibliothèques\n"
    "from pathlib import Path\n"
    "import json\n"
    "import shutil\n"
    "import joblib\n"
    "import mlflow\n"
    "import mlflow.sklearn\n"
    "import numpy as np\n"
    "\n"
    "from sklearn.datasets import fetch_california_housing\n"
    "from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor\n"
    "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n"
    "from sklearn.model_selection import train_test_split\n"
    "from sklearn.pipeline import Pipeline\n"
    "from sklearn.preprocessing import StandardScaler"
)

h(2, "4.2  Insérer une nouvelle cellule après le chargement des données")
para("Après la cellule de chargement du dataset, insérer :")
code(
    "# Cellule 2b — Configurer MLFlow\n"
    'mlflow.set_experiment("housing_ab_models")\n'
    'print("Expérience MLFlow configurée : housing_ab_models")'
)

h(2, "4.3  Cellule 4 — Remplacer l'entraînement du modèle A")
para("Remplacer la cellule 4 actuelle (entraînement modèle A) par :")
code(
    "# Cellule 4 - Entraîner le modèle A (champion) avec MLFlow\n"
    'with mlflow.start_run(run_name="model_A_RandomForest"):\n'
    "\n"
    "    params_a = {\n"
    '        "model_type":   "RandomForestRegressor",\n'
    '        "n_estimators": 30,\n'
    '        "max_depth":    8,\n'
    '        "random_state": 42,\n'
    '        "role":         "champion",\n'
    "    }\n"
    "    mlflow.log_params(params_a)\n"
    "\n"
    "    model_a = Pipeline([\n"
    '        ("scaler", StandardScaler()),\n'
    '        ("model",  RandomForestRegressor(\n'
    '            n_estimators=params_a["n_estimators"],\n'
    '            max_depth=params_a["max_depth"],\n'
    '            random_state=params_a["random_state"],\n'
    "            n_jobs=-1,\n"
    "        )),\n"
    "    ])\n"
    "    model_a.fit(X_train, y_train)\n"
    "\n"
    "    metrics_a = evaluate_pipeline(model_a, X_test, y_test)\n"
    "    mlflow.log_metrics(metrics_a)\n"
    "\n"
    "    mlflow.sklearn.log_model(\n"
    "        model_a,\n"
    '        artifact_path="model",\n'
    '        registered_model_name="housing_model_A",\n'
    "    )\n"
    '    print("Modèle A :", metrics_a)'
)

h(2, "4.4  Cellule 5 — Remplacer l'entraînement du modèle B")
code(
    "# Cellule 5 - Entraîner le modèle B (challenger) avec MLFlow\n"
    'with mlflow.start_run(run_name="model_B_GradientBoosting"):\n'
    "\n"
    "    params_b = {\n"
    '        "model_type":    "GradientBoostingRegressor",\n'
    '        "n_estimators":  80,\n'
    '        "learning_rate": 0.05,\n'
    '        "random_state":  42,\n'
    '        "role":          "challenger",\n'
    "    }\n"
    "    mlflow.log_params(params_b)\n"
    "\n"
    "    model_b = Pipeline([\n"
    '        ("scaler", StandardScaler()),\n'
    '        ("model",  GradientBoostingRegressor(\n'
    '            n_estimators=params_b["n_estimators"],\n'
    '            learning_rate=params_b["learning_rate"],\n'
    '            random_state=params_b["random_state"],\n'
    "        )),\n"
    "    ])\n"
    "    model_b.fit(X_train, y_train)\n"
    "\n"
    "    metrics_b = evaluate_pipeline(model_b, X_test, y_test)\n"
    "    mlflow.log_metrics(metrics_b)\n"
    "\n"
    "    mlflow.sklearn.log_model(\n"
    "        model_b,\n"
    '        artifact_path="model",\n'
    '        registered_model_name="housing_model_B",\n'
    "    )\n"
    '    print("Modèle B :", metrics_b)'
)

h(2, "4.5  La cellule de sauvegarde (Cellule 6) reste inchangée")
para(
    "La cellule qui sauvegarde les .joblib dans artifacts/models/ n'est pas modifiée. "
    "MLFlow conserve ses propres copies dans mlruns/ — les deux coexistent sans conflit."
)
tip(
    "💡 Astuce :",
    "mlflow.log_params() et mlflow.log_metrics() au pluriel acceptent un dictionnaire "
    "et loguent tout en une seule ligne. Préférer cette forme quand on a plusieurs "
    "paramètres à enregistrer.",
    "D1ECF1",
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 5 — UI
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 5 — Lancer l'interface MLFlow UI")

h(2, "5.1  Commande de lancement")
para("Dans un terminal, à la racine du projet :")
code("mlflow ui")
para("Résultat :")
code(
    "[INFO] Starting gunicorn 21.2.0\n"
    "[INFO] Listening at: http://127.0.0.1:5000\n"
    "[INFO] Using worker: sync"
)
para("Ouvrir un navigateur à l'adresse : http://127.0.0.1:5000")
tip(
    "⚠️ Important :",
    "Ce serveur est local uniquement. Il lit le dossier mlruns/ du répertoire courant. "
    "Il doit être lancé depuis la racine du projet.",
)

h(2, "5.2  Changer le port si 5000 est occupé (Mac)")
para("Sur macOS, le port 5000 est parfois utilisé par AirPlay. Utiliser :")
code("mlflow ui --port 5001")
para("Puis ouvrir http://127.0.0.1:5001")

h(2, "5.3  Ce qu'on voit dans l'interface")
bullet(
    "Colonne gauche : la liste des expériences (housing_price_prediction, housing_ab_models)."
)
bullet("Zone centrale : tableau de tous les runs avec leurs paramètres et métriques.")
bullet("Bouton « Compare » : graphique de comparaison entre runs sélectionnés.")
bullet("Détail d'un run : artefacts (modèle .pkl, fichiers JSON) téléchargeables.")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 6 — INTERPRÉTER
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 6 — Lire et interpréter les résultats")

h(2, "6.1  Comprendre le tableau des runs")
col_data = [
    ("Run Name", "Nom donné au run (ex: run_v3, model_A_RandomForest)"),
    ("Start Time", "Date et heure de lancement"),
    ("Duration", "Durée d'exécution du run"),
    ("Parameters", "Valeurs loggées avec mlflow.log_param()"),
    ("Metrics", "mae, rmse, r2 loggés avec mlflow.log_metric()"),
    ("Tags", "Métadonnées libres (auteur, dataset, etc.)"),
]
table = doc.add_table(rows=1, cols=2)
table.style = "Table Grid"
hdr = table.rows[0].cells
hdr[0].text = "Colonne"
hdr[1].text = "Contenu"
for cell in hdr:
    cell.paragraphs[0].runs[0].bold = True
    cell.paragraphs[0].runs[0].font.size = Pt(10)
for col, desc in col_data:
    row_cells = table.add_row().cells
    row_cells[0].text = col
    row_cells[1].text = desc
    for c in row_cells:
        c.paragraphs[0].runs[0].font.size = Pt(10)
doc.add_paragraph()

h(2, "6.2  Comparer deux runs")
numbered("Cocher les cases des deux runs à comparer dans le tableau.")
numbered("Cliquer sur le bouton bleu « Compare ».")
numbered(
    "MLFlow affiche un graphique en barres et un tableau côte-à-côte des métriques."
)
numbered("Le meilleur run est celui avec R² le plus élevé et MAE le plus faible.")

h(2, "6.3  Accéder aux artefacts d'un run")
numbered("Cliquer sur le nom d'un run dans le tableau.")
numbered("Faire défiler jusqu'à la section « Artifacts ».")
numbered("Le dossier model/ contient le modèle sauvegardé par MLFlow.")
numbered(
    "Le dossier metrics/ contient le fichier .json copié par mlflow.log_artifact()."
)
numbered("Ces fichiers peuvent être téléchargés directement depuis l'interface.")

h(2, "6.4  Identifier le meilleur run depuis le code Python")
para("Pour automatiser la sélection du meilleur modèle sans passer par l'interface :")
code(
    "import mlflow\n"
    "\n"
    "client = mlflow.tracking.MlflowClient()\n"
    "\n"
    "# Récupérer l'ID de l'expérience\n"
    'experiment = client.get_experiment_by_name("housing_ab_models")\n'
    "\n"
    "# Chercher le meilleur run selon r2 décroissant\n"
    "best_run = client.search_runs(\n"
    "    experiment_ids=[experiment.experiment_id],\n"
    '    order_by=["metrics.r2 DESC"],\n"'
    "    max_results=1,\n"
    ")[0]\n"
    "\n"
    'print("Meilleur run   :", best_run.info.run_id)\n'
    'print("Run name       :", best_run.data.tags.get("mlflow.runName"))\n'
    'print("R²             :", best_run.data.metrics["r2"])\n'
    'print("MAE            :", best_run.data.metrics["mae"])\n'
    'print("n_estimators   :", best_run.data.params.get("n_estimators"))'
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 7 — MODEL REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 7 — MLFlow Model Registry (niveau avancé)")
para(
    "Le Model Registry est un registre centralisé qui permet de versionner les modèles "
    "et de les promouvoir entre étapes : None → Staging → Production → Archived."
)
tip(
    "ℹ️ Note :",
    "Le Model Registry est déjà activé dans les modifications des Parties 3 et 4 "
    "via le paramètre registered_model_name dans mlflow.sklearn.log_model(). "
    "Cette partie explique comment l'utiliser.",
    "D1ECF1",
)

h(2, "7.1  Voir les modèles enregistrés dans l'UI")
numbered(
    "Dans l'interface MLFlow UI (http://127.0.0.1:5000), cliquer sur l'onglet « Models »."
)
numbered("La liste apparaît : housing_model_A, housing_model_B, housing_latest.")
numbered("Cliquer sur un modèle pour voir toutes ses versions.")
numbered("Chaque version est liée au run qui l'a produite.")

h(2, "7.2  Promouvoir un modèle en production via Python")
code(
    "import mlflow\n"
    "\n"
    "client = mlflow.tracking.MlflowClient()\n"
    "\n"
    "# Promouvoir la version 1 du modèle A en Production\n"
    "client.transition_model_version_stage(\n"
    '    name="housing_model_A",\n'
    "    version=1,\n"
    '    stage="Production",\n'
    ")\n"
    'print("Modèle A v1 promu en Production")\n'
    "\n"
    "# Promouvoir la version 1 du modèle B en Staging\n"
    "client.transition_model_version_stage(\n"
    '    name="housing_model_B",\n'
    "    version=1,\n"
    '    stage="Staging",\n'
    ")\n"
    'print("Modèle B v1 promu en Staging")'
)

h(2, "7.3  Charger un modèle depuis le Registry")
code(
    "import mlflow.sklearn\n"
    "\n"
    "# Charger le modèle actuellement en Production\n"
    'model = mlflow.sklearn.load_model("models:/housing_model_A/Production")\n'
    "prediction = model.predict(X_test[:5])\n"
    "print(prediction)"
)
tip(
    "💡 Pour aller plus loin :",
    "Dans un contexte avancé, le backend FastAPI pourrait charger le modèle directement "
    "depuis le Model Registry MLFlow au lieu de lire le .joblib. Cela permettrait de "
    "changer le modèle en production sans redéployer le conteneur Docker.",
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTIE 8 — RÉCAPITULATIF
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Partie 8 — Récapitulatif des fichiers modifiés")

files_summary = [
    ("requirements.txt", "Ajout de mlflow==2.22.0", "Installer la dépendance"),
    (
        ".gitignore",
        "Ajout de mlruns/ et mlartifacts/",
        "Ne pas commiter la BDD MLFlow locale",
    ),
    (
        "src/training/pipeline.py",
        "Import mlflow + set_experiment + start_run + log_param/metric/model",
        "Traçabilité du pipeline principal",
    ),
    (
        "notebooks/02_train_ab_models.ipynb",
        "Import mlflow + set_experiment + start_run dans cellules 4 et 5",
        "Traçabilité des modèles A et B",
    ),
]
table2 = doc.add_table(rows=1, cols=3)
table2.style = "Table Grid"
hdr2 = table2.rows[0].cells
hdr2[0].text = "Fichier"
hdr2[1].text = "Modification"
hdr2[2].text = "Objectif"
for cell in hdr2:
    cell.paragraphs[0].runs[0].bold = True
    cell.paragraphs[0].runs[0].font.size = Pt(10)
for fname, mod, obj in files_summary:
    rc = table2.add_row().cells
    rc[0].text = fname
    rc[1].text = mod
    rc[2].text = obj
    for c in rc:
        c.paragraphs[0].runs[0].font.size = Pt(9)
doc.add_paragraph()

para("Fichiers NON modifiés :")
bullet(
    "backend/requirements.txt — MLFlow n'est pas nécessaire dans le conteneur de production."
)
bullet("backend/app.py — Le backend charge toujours les .joblib, aucun changement.")
bullet("src/training/train.py — La logique d'entraînement reste identique.")
bullet("src/training/evaluate.py — La logique d'évaluation reste identique.")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ANNEXE
# ═══════════════════════════════════════════════════════════════════════════════
h(1, "Annexe — Aide-mémoire des commandes MLFlow")

h(2, "Fonctions Python essentielles")
api_cmds = [
    ("mlflow.set_experiment(nom)", "Crée ou sélectionne une expérience par nom"),
    ("mlflow.start_run(run_name=nom)", "Ouvre un run (utiliser avec with)"),
    ("mlflow.log_param(clé, valeur)", "Logue un paramètre unique"),
    ("mlflow.log_params(dict)", "Logue plusieurs paramètres depuis un dict"),
    ("mlflow.log_metric(clé, valeur)", "Logue une métrique numérique"),
    ("mlflow.log_metrics(dict)", "Logue plusieurs métriques depuis un dict"),
    ("mlflow.log_artifact(chemin_fichier)", "Copie un fichier dans MLFlow"),
    ("mlflow.sklearn.log_model(model, path)", "Sauvegarde un modèle sklearn"),
    ("mlflow.set_tag(clé, valeur)", "Ajoute une métadonnée libre au run"),
]
for fn, desc in api_cmds:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.3)
    r1 = p.add_run(fn)
    set_font(r1, bold=True, name="Courier New", size=9, color=(0x1F, 0x49, 0x7D))
    r2 = p.add_run("\n    " + desc)
    set_font(r2, size=10)

h(2, "Commandes terminal")
terminal_cmds = [
    ("mlflow ui", "Lance l'interface sur http://127.0.0.1:5000"),
    ("mlflow ui --port 5001", "Lance sur un autre port"),
    ("mlflow runs list --experiment-name nom", "Liste les runs d'une expérience"),
    ("mlflow artifacts list --run-id <id>", "Liste les artefacts d'un run"),
]
for cmd, desc in terminal_cmds:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.3)
    r1 = p.add_run(cmd)
    set_font(r1, bold=True, name="Courier New", size=9, color=(0x1F, 0x49, 0x7D))
    r2 = p.add_run("  →  " + desc)
    set_font(r2, size=10)

h(2, "Flux recommandé pour la soutenance")
workflow = [
    "Lancer python main.py deux ou trois fois (varier n_estimators : 50, 100, 200 dans train.py).",
    "Exécuter le notebook 02_train_ab_models.ipynb en entier.",
    "Lancer mlflow ui depuis la racine du projet.",
    "Ouvrir http://127.0.0.1:5000 et montrer le tableau des runs.",
    "Sélectionner model_A_RandomForest et model_B_GradientBoosting → cliquer Compare.",
    "Expliquer le graphique de comparaison R²/MAE et quel modèle serait promu en Production.",
    "Dans l'onglet Models, montrer housing_model_A et housing_model_B dans le Registry.",
]
for step in workflow:
    numbered(step)

# Footer
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Guide rédigé pour le projet fil rouge — Industrialisation ML")
r.italic = True
r.font.size = Pt(9)
r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

# ── Sauvegarde ────────────────────────────────────────────────────────────────
out_path = "d:/Projects/ml-housing-project/docs/Guide_MLFlow.docx"
os.makedirs("d:/Projects/ml-housing-project/docs", exist_ok=True)
doc.save(out_path)
print(f"Sauvegardé : {out_path}")
