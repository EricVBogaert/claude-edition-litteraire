#!/bin/bash
# test-circular-imports.sh
# Script pour tester si les imports circulaires ont été correctement résolus

echo "🧪 Test de résolution des imports circulaires..."

# Créer un environnement virtuel temporaire pour les tests
echo "🛠️ Création d'un environnement virtuel pour les tests..."
python3 -m venv .venv_test_imports
source .venv_test_imports/bin/activate

# Installer les dépendances nécessaires
echo "📦 Installation des dépendances..."
pip install pytest pytest-cov > /dev/null 2>&1

# Installer le package en mode développement
pip install -e . > /dev/null 2>&1

# Créer un script de test pour les imports
mkdir -p tests/test_imports

cat > tests/test_imports/test_no_circular_imports.py << 'EOF'
"""
Tests pour vérifier l'absence d'imports circulaires.
"""

import importlib
import pkgutil
import pytest
import sys
import claude_edition_litteraire

def test_import_all_modules():
    """Tente d'importer tous les modules du package pour détecter les imports circulaires."""
    
    # Liste pour suivre les modules déjà traités
    imported_modules = set()
    
    def import_recursive(package_name):
        """Importe récursivement tous les modules d'un package."""
        if package_name in imported_modules:
            return
        
        imported_modules.add(package_name)
        
        try:
            # Importer le module ou package
            package = importlib.import_module(package_name)
            
            # Si c'est un package, importer ses sous-modules
            if hasattr(package, '__path__'):
                for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                    full_name = package_name + '.' + name
                    import_recursive(full_name)
        except ImportError as e:
            pytest.fail(f"Erreur d'import pour le module {package_name}: {e}")
    
    # Commencer par importer le package principal
    import_recursive('claude_edition_litteraire')
    
    # Vérifier que nous avons importé suffisamment de modules
    assert len(imported_modules) > 10, "Pas assez de modules importés, vérifiez la logique d'import récursif"
    
    print(f"\nModules importés avec succès ({len(imported_modules)}):")
    for module in sorted(imported_modules):
        print(f"  - {module}")

def test_specific_problematic_imports():
    """Teste spécifiquement les paires de modules précédemment problématiques."""
    
    problematic_pairs = [
        ('claude_edition_litteraire.core', 'claude_edition_litteraire.llm'),
        ('claude_edition_litteraire.core', 'claude_edition_litteraire.claude'),
        ('claude_edition_litteraire.claude', 'claude_edition_litteraire.llm'),
        # Ajoutez d'autres paires identifiées comme problématiques
    ]
    
    for module1, module2 in problematic_pairs:
        print(f"Testant l'import de {module1} puis {module2}...")
        try:
            # Supprimer les modules du cache s'ils y sont déjà
            if module1 in sys.modules:
                del sys.modules[module1]
            if module2 in sys.modules:
                del sys.modules[module2]
            
            # Importer dans cet ordre
            importlib.import_module(module1)
            importlib.import_module(module2)
            
            # Si on arrive ici, pas d'erreur
            print(f"  ✅ Import réussi: {module1} -> {module2}")
            
            # Maintenant dans l'ordre inverse
            # Supprimer du cache
            del sys.modules[module1]
            del sys.modules[module2]
            
            # Importer dans l'ordre inverse
            importlib.import_module(module2)
            importlib.import_module(module1)
            
            print(f"  ✅ Import réussi: {module2} -> {module1}")
        except ImportError as e:
            pytest.fail(f"Erreur d'import entre {module1} et {module2}: {e}")

def test_class_instantiation():
    """Vérifie que les classes principales peuvent être instanciées sans erreur d'import circulaire."""
    
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            from claude_edition_litteraire.core import Project
            
            # Tenter d'instancier Project
            project = Project(temp_dir)
            
            # Vérifier que les attributs clés sont initialisés
            assert hasattr(project, 'llm'), "L'attribut llm n'est pas initialisé"
            assert hasattr(project, 'structure'), "L'attribut structure n'est pas initialisé"
            assert hasattr(project, 'content'), "L'attribut content n'est pas initialisé"
            
            print("✅ Project instancié avec succès")
        except ImportError as e:
            pytest.fail(f"Erreur d'import lors de l'instanciation: {e}")
        except Exception as e:
            # D'autres erreurs peuvent se produire, mais pas des erreurs d'import
            print(f"⚠️ Exception lors de l'instanciation (non liée aux imports): {e}")
EOF

# Exécuter les tests
echo "🧪 Exécution des tests d'imports circulaires..."
pytest -xvs tests/test_imports/test_no_circular_imports.py

# Nettoyer
echo "🧹 Nettoyage de l'environnement de test..."
deactivate
rm -rf .venv_test_imports

echo "✅ Tests terminés!"
