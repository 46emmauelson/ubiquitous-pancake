# 💚 PayZen Python (Flask) — Application de Paiement Mobile

## 🚀 Démarrage rapide

```bash
# 1. Créer un environnement virtuel
python -m venv venv

# 2. Activer l'environnement
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python run.py
```

Ouvrez **http://localhost:5000** dans votre navigateur.
La base de données SQLite se crée automatiquement.

---

## 📁 Structure

```
PayZen-Python/
├── run.py                         ← Point d'entrée Flask
├── requirements.txt
├── app/
│   ├── __init__.py                ← App factory
│   ├── controllers/
│   │   ├── auth.py                ← Connexion / Inscription
│   │   └── dashboard.py          ← Dépôt, Transfert, Paiement, Retrait
│   ├── models/
│   │   ├── database.py            ← SQLite via sqlite3
│   │   ├── user.py
│   │   └── transaction.py
│   ├── static/
│   │   ├── css/app.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html
│       ├── auth/index.html
│       └── dashboard/
│           ├── index.html
│           ├── history.html
│           ├── profile.html
│           └── nav.html
├── database/
│   └── payzen.db                  ← Créé automatiquement
└── uploads/                       ← Fichiers médias
```

## ⚙️ Requis

- Python 3.9+
- Flask 3.x (inclus dans requirements.txt)
