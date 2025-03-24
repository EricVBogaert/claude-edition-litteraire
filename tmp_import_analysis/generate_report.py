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
