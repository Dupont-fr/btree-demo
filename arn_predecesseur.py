"""Predecesseur d'un noeud dans un ARN."""
from tree_ops import RBTree

def main():
    t = RBTree()
    for v in [41, 38, 31, 12, 19, 8]:
        t.insert(v)
    print("Arbre (infixe) :", t.inorder())
    cle = 12
    print(f"--- Predecesseur de {cle} ---")
    for s in t.predecessor(cle):
        print(" ", s["message"])

if __name__ == "__main__":
    main()
