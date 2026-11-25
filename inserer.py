"""Insertion dans un ABR (Arbre Binaire de Recherche)."""
from tree_ops import BST

def main():
    t = BST()
    for v in [20, 10, 30, 5, 15, 25, 35]:
        t.insert(v)
    print("Arbre initial (infixe) :", t.inorder())
    print("--- Insertion de 12 ---")
    for s in t.insert(12):
        print(" ", s["message"])
    print("Arbre apres insertion (infixe) :", t.inorder())
    print("Validation ABR :", t.validate())

if __name__ == "__main__":
    main()
