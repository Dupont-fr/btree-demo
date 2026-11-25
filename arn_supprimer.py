"""Suppression dans un ARN."""
from tree_ops import RBTree

def main():
    t = RBTree()
    for v in [41, 38, 31, 12, 19, 8]:
        t.insert(v)
    print("Arbre initial (infixe) :", t.inorder())
    print("--- Suppression de 12 ---")
    for s in t.delete(12):
        print(" ", s["message"])
    print("Arbre apres suppression (infixe) :", t.inorder())
    print("Validation ARN :", t.validate())

if __name__ == "__main__":
    main()
