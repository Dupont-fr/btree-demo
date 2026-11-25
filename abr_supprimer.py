"""Suppression dans un ABR."""
from tree_ops import BST

def main():
    t = BST()
    for v in [20, 10, 30, 5, 15, 25, 35]:
        t.insert(v)
    print("Arbre initial (infixe) :", t.inorder())
    print("--- Suppression de 10 ---")
    for s in t.delete(10):
        print(" ", s["message"])
    print("Arbre apres suppression (infixe) :", t.inorder())
    print("Validation ABR :", t.validate())

if __name__ == "__main__":
    main()
