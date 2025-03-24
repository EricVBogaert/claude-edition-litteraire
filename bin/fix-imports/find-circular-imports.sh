#!/bin/bash
# find-circular-imports.sh
# Script pour identifier les cycles d'imports dans le projet

echo "🔍 Recherche des imports circulaires dans le projet..."

# Créer un répertoire temporaire pour les rapports
mkdir -p ./tmp_import_analysis

# Utiliser grep pour trouver tous les imports
echo "📊 Analyse des fichiers Python..."
find ./claude_edition_litteraire -name "*.py" -type f | xargs grep -l "^import\|^from" > ./tmp_import_analysis/files_with_imports.txt

# Fonction pour extraire les imports d'un fichier
extract_imports() {
    local file=$1
    local base_module="claude_edition_litteraire"
    
    # Extraire les imports qui concernent notre propre package
    grep "^from $base_module\|^import $base_module" "$file" | \
    sed -E 's/from (claude_edition_litteraire[^ ]*).*/\1/g; s/import (claude_edition_litteraire[^ ]*).*/\1/g' | \
    sort -u > "./tmp_import_analysis/$(basename "$file")_imports.txt"
    
    # Ajouter le nom du module lui-même (basé sur le chemin de fichier)
    module_name=$(echo "$file" | sed -E "s/\.\/${base_module//\./\\/}\/(.*).py/${base_module}.\1/g" | sed 's/\//./g')
    echo "$module_name" > "./tmp_import_analysis/$(basename "$file")_module.txt"
}

# Extraire les imports pour chaque fichier
while read -r file; do
    extract_imports "$file"
done < ./tmp_import_analysis/files_with_imports.txt

# Rechercher les cycles d'imports
echo "🔄 Recherche des cycles d'imports..."

# On va construire un graphe représenté par une liste d'adjacence
GRAPH_FILE="./tmp_import_analysis/import_graph.txt"
> "$GRAPH_FILE"  # Créer/vider le fichier

while read -r file; do
    module_file="./tmp_import_analysis/$(basename "$file")_module.txt"
    imports_file="./tmp_import_analysis/$(basename "$file")_imports.txt"
    
    if [[ -f "$module_file" && -f "$imports_file" ]]; then
        module=$(cat "$module_file")
        
        while read -r imported; do
            # Ne pas ajouter les imports de sous-modules comme cycle
            if ! [[ "$module" == "$imported"* ]]; then
                echo "$module -> $imported" >> "$GRAPH_FILE"
            fi
        done < "$imports_file"
    fi
done < ./tmp_import_analysis/files_with_imports.txt

# Détection des cycles avec Python
cat > ./tmp_import_analysis/find_cycles.py << EOF
import sys
from collections import defaultdict

def find_cycles(graph):
    """Trouve les cycles dans un graphe dirigé."""
    visited = set()
    path = []
    path_set = set()
    cycles = []
    
    def dfs(node):
        if node in path_set:
            # Cycle trouvé
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        
        if node in visited:
            return
        
        visited.add(node)
        path.append(node)
        path_set.add(node)
        
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        
        path.pop()
        path_set.remove(node)
    
    # Construire le graphe à partir du fichier
    adj_list = defaultdict(list)
    with open(sys.argv[1], 'r') as f:
        for line in f:
            line = line.strip()
            if ' -> ' in line:
                source, target = line.split(' -> ')
                adj_list[source].append(target)
    
    # Rechercher les cycles à partir de chaque nœud
    for node in adj_list:
        if node not in visited:
            dfs(node)
    
    return cycles

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_cycles.py graph_file")
        sys.exit(1)
    
    cycles = find_cycles(sys.argv[1])
    
    if not cycles:
        print("Aucun cycle d'imports détecté ! 🎉")
    else:
        print(f"⚠️ {len(cycles)} cycles d'imports détectés:")
        
        for i, cycle in enumerate(cycles, 1):
            path = " -> ".join(cycle)
            print(f"Cycle {i}: {path}")
EOF

# Exécuter la détection de cycles
echo "📝 Résultats de l'analyse:"
python3 ./tmp_import_analysis/find_cycles.py "$GRAPH_FILE"

# Générer un rapport détaillé
echo "📊 Génération du rapport détaillé..."
cat > ./tmp_import_analysis/generate_report.py << EOF
import os
import sys
from collections import defaultdict

def generate_report():
    """Génère un rapport détaillé des imports."""
    
    # Construire le graphe à partir du fichier
    graph = defaultdict(list)
    reverse_graph = defaultdict(list)
    
    with open("./tmp_import_analysis/import_graph.txt", 'r') as f:
        for line in f:
            line = line.strip()
            if ' -> ' in line:
                source, target = line.split(' -> ')
                graph[source].append(target)
                reverse_graph[target].append(source)
    
    # Identifier les modules problématiques
    problematic_modules = set()
    for source in graph:
        for target in graph[source]:
            if source in reverse_graph.get(target, []):
                problematic_modules.add(source)
                problematic_modules.add(target)
    
    # Générer le rapport
    with open("import_cycles_report.md", 'w') as f:
        f.write("# Analyse des Cycles d'Imports\n\n")
        
        if not problematic_modules:
            f.write("📊 **Aucun cycle d'import détecté !** 🎉\n")
            return
        
        f.write(f"## Modules problématiques ({len(problematic_modules)})\n\n")
        
        for module in sorted(problematic_modules):
            f.write(f"### {module}\n\n")
            f.write("#### Importe:\n")
            for target in sorted(graph.get(module, [])):
                if target in problematic_modules:
                    f.write(f"- **{target}** ⚠️\n")
                else:
                    f.write(f"- {target}\n")
            
            f.write("\n#### Importé par:\n")
            for source in sorted(reverse_graph.get(module, [])):
                if source in problematic_modules:
                    f.write(f"- **{source}** ⚠️\n")
                else:
                    f.write(f"- {source}\n")
            
            f.write("\n")
        
        f.write("## Recommandations\n\n")
        f.write("Pour résoudre les cycles d'imports:\n\n")
        f.write("1. Utiliser l'import tardif (lazy import) dans les méthodes plutôt qu'au niveau du module\n")
        f.write("2. Restructurer en déplaçant certaines fonctionnalités vers des modules intermédiaires\n")
        f.write("3. Implémenter un pattern d'injection de dépendances\n")
        f.write("4. Utiliser des interfaces abstraites\n")

if __name__ == "__main__":
    generate_report()
EOF

python3 ./tmp_import_analysis/generate_report.py
echo "📑 Rapport détaillé généré: import_cycles_report.md"

echo "🧹 Nettoyage des fichiers temporaires..."
#rm -rf ./tmp_import_analysis

echo "✅ Analyse terminée!"
