"""Insertion dans un ARN (Arbre Rouge-Noir)."""
from tree_ops import RBTree

def main():
    t = RBTree()
    for v in [41, 38, 31, 12, 19, 8]:
        t.insert(v)
    print("Arbre initial (infixe) :", t.inorder())
    print("--- Insertion de 25 ---")
    for s in t.insert(25):
        print(" ", s["message"])
    print("Arbre apres insertion (infixe) :", t.inorder())
    print("Validation ARN :", t.validate())

if __name__ == "__main__":
    main()
