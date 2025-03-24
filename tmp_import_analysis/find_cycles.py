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
