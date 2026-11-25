"""Recherche du maximum dans un ARN."""
from tree_ops import RBTree

def main():
    t = RBTree()
    for v in [41, 38, 31, 12, 19, 8]:
        t.insert(v)
    print("Arbre (infixe) :", t.inorder())
    print("--- Recherche du maximum ---")
    for s in t.maximum():
        print(" ", s["message"])

if __name__ == "__main__":
    main()
