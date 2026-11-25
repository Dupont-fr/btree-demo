"""Recherche du minimum dans un ABR."""
from tree_ops import BST

def main():
    t = BST()
    for v in [20, 10, 30, 5, 15, 25, 35]:
        t.insert(v)
    print("Arbre (infixe) :", t.inorder())
    print("--- Recherche du minimum ---")
    for s in t.minimum():
        print(" ", s["message"])

if __name__ == "__main__":
    main()
