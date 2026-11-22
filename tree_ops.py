"""Operations on Binary Search Trees (ABR) and Red-Black Trees (ARN).

This module implements the algorithms from the course (FOSSO, Chapitre II)
and produces detailed step-by-step traces for visualisation.
"""
import copy


class Node:
    def __init__(self, key, color="black"):
        self.key = key
        self.color = color  # "red" | "black"
        self.left = None
        self.right = None
        self.parent = None

    def __repr__(self):
        return f"Node({self.key},{self.color})"


# ---------------------------------------------------------------------------
# Binary Search Tree (ABR)
# ---------------------------------------------------------------------------
class BST:
    def __init__(self):
        self.root = None

    # ---- helpers ----
    def _snap(self, steps, msg, highlight=None):
        steps.append({
            "message": msg,
            "tree": self.snapshot(),
            "highlight": list(highlight) if highlight else [],
        })

    def snapshot(self):
        return self._snap_node(self.root)

    def _snap_node(self, node):
        if node is None:
            return None
        return {
            "key": node.key,
            "color": "black",
            "left": self._snap_node(node.left),
            "right": self._snap_node(node.right),
        }

    def _find(self, key):
        cur = self.root
        while cur is not None:
            if key == cur.key:
                return cur
            if key < cur.key:
                cur = cur.left
            else:
                cur = cur.right
        return None

    def _min_node(self, node):
        cur = node
        while cur is not None and cur.left is not None:
            cur = cur.left
        return cur

    def _max_node(self, node):
        cur = node
        while cur is not None and cur.right is not None:
            cur = cur.right
        return cur

    # ---- traversals ----
    def preorder(self):
        out = []

        def dfs(n):
            if n is None:
                return
            out.append(n.key)
            dfs(n.left)
            dfs(n.right)

        dfs(self.root)
        return out

    def inorder(self):
        out = []

        def dfs(n):
            if n is None:
                return
            dfs(n.left)
            out.append(n.key)
            dfs(n.right)

        dfs(self.root)
        return out

    def postorder(self):
        out = []

        def dfs(n):
            if n is None:
                return
            dfs(n.left)
            dfs(n.right)
            out.append(n.key)

        dfs(self.root)
        return out

    def breadth_first(self):
        out = []
        if self.root is None:
            return out
        q = [self.root]
        while q:
            n = q.pop(0)
            out.append(n.key)
            if n.left is not None:
                q.append(n.left)
            if n.right is not None:
                q.append(n.right)
        return out

    # ---- stats ----
    def height(self):
        def h(n):
            if n is None:
                return 0
            return 1 + max(h(n.left), h(n.right))

        return h(self.root)

    def count(self):
        def c(n):
            if n is None:
                return 0
            return 1 + c(n.left) + c(n.right)

        return c(self.root)

    def black_height(self):
        return self.height()  # not meaningful for BST; reuse height

    def stats(self):
        return {
            "type": "bst",
            "count": self.count(),
            "height": self.height(),
            "min": (self._min_node(self.root).key if self.root is not None else None),
            "max": (self._max_node(self.root).key if self.root is not None else None),
        }

    def validate(self):
        violations = []
        # BST property
        def check(n, lo, hi):
            if n is None:
                return
            if lo is not None and n.key < lo:
                violations.append(f"Violation ABR: {n.key} < {lo}")
            if hi is not None and n.key >= hi:
                violations.append(f"Violation ABR: {n.key} >= {hi}")
            check(n.left, lo, n.key)
            check(n.right, n.key, hi)

        check(self.root, None, None)
        if not violations:
            violations.append("OK: propriete d'ABR respectee.")
        return violations

    # ---- search ----
    def search(self, key):
        steps = []
        cur = self.root
        if cur is None:
            self._snap(steps, "Arbre vide.", [])
            return steps
        while cur is not None:
            if key == cur.key:
                self._snap(steps, f"Trouve: {key} == {cur.key}.", [cur.key, key])
                return steps
            if key < cur.key:
                self._snap(steps, f"Comparaison {key} < {cur.key}: descente a gauche.", [cur.key, key])
                cur = cur.left
            else:
                self._snap(steps, f"Comparaison {key} > {cur.key}: descente a droite.", [cur.key, key])
                cur = cur.right
        self._snap(steps, f"{key} non trouve dans l'arbre.", [])
        return steps

    # ---- min / max ----
    def minimum(self):
        steps = []
        cur = self.root
        if cur is None:
            self._snap(steps, "Arbre vide.", [])
            return steps
        while cur.left is not None:
            self._snap(steps, f"Descente gauche: {cur.key} -> {cur.left.key}.", [cur.key, cur.left.key])
            cur = cur.left
        self._snap(steps, f"Minimum = {cur.key}.", [cur.key])
        return steps

    def maximum(self):
        steps = []
        cur = self.root
        if cur is None:
            self._snap(steps, "Arbre vide.", [])
            return steps
        while cur.right is not None:
            self._snap(steps, f"Descente droite: {cur.key} -> {cur.right.key}.", [cur.key, cur.right.key])
            cur = cur.right
        self._snap(steps, f"Maximum = {cur.key}.", [cur.key])
        return steps

    # ---- successor / predecessor ----
    def successor(self, key):
        steps = []
        node = self._find(key)
        if node is None:
            self._snap(steps, f"Clé {key} introuvable.", [])
            return steps
        if node.right is not None:
            cur = node.right
            self._snap(steps, f"Successeur: sous-arbre droit de {key}; minimum de ce sous-arbre.", [key, cur.key])
            while cur.left is not None:
                self._snap(steps, f"Descente gauche: {cur.key} -> {cur.left.key}.", [cur.key, cur.left.key])
                cur = cur.left
            self._snap(steps, f"Successeur de {key} = {cur.key}.", [key, cur.key])
        else:
            cur = node
            parent = node.parent
            while parent is not None and cur is parent.right:
                self._snap(steps, f"Remontee: {cur.key} est fils droit de {parent.key}.", [cur.key, parent.key])
                cur = parent
                parent = parent.parent
            if parent is None:
                self._snap(steps, f"Pas de successeur pour {key}.", [key])
            else:
                self._snap(steps, f"Successeur de {key} = {parent.key}.", [key, parent.key])
        return steps

    def predecessor(self, key):
        steps = []
        node = self._find(key)
        if node is None:
            self._snap(steps, f"Clé {key} introuvable.", [])
            return steps
        if node.left is not None:
            cur = node.left
            self._snap(steps, f"Predecesseur: sous-arbre gauche de {key}; maximum de ce sous-arbre.", [key, cur.key])
            while cur.right is not None:
                self._snap(steps, f"Descente droite: {cur.key} -> {cur.right.key}.", [cur.key, cur.right.key])
                cur = cur.right
            self._snap(steps, f"Predecesseur de {key} = {cur.key}.", [key, cur.key])
        else:
            cur = node
            parent = node.parent
            while parent is not None and cur is parent.left:
                self._snap(steps, f"Remontee: {cur.key} est fils gauche de {parent.key}.", [cur.key, parent.key])
                cur = parent
                parent = parent.parent
            if parent is None:
                self._snap(steps, f"Pas de predecesseur pour {key}.", [key])
            else:
                self._snap(steps, f"Predecesseur de {key} = {parent.key}.", [key, parent.key])
        return steps

    # ---- insert ----
    def insert(self, key):
        steps = []
        if self.root is None:
            self.root = Node(key)
            self._snap(steps, f"Arbre vide: {key} devient la racine.", [key])
            return steps
        path = []
        parent = None
        cur = self.root
        while cur is not None:
            parent = cur
            if key < cur.key:
                self._snap(steps, f"Comparaison {key} < {cur.key}: descente a gauche.", [cur.key, key])
                cur = cur.left
            else:
                self._snap(steps, f"Comparaison {key} >= {cur.key}: descente a droite.", [cur.key, key])
                cur = cur.right
            path.append(parent.key)
        new = Node(key)
        new.parent = parent
        if key < parent.key:
            parent.left = new
            side = "gauche"
        else:
            parent.right = new
            side = "droite"
        self._snap(steps, f"Insertion de {key} comme fils {side} de {parent.key}.", [key, parent.key])
        return steps

    # ---- delete ----
    def delete(self, key):
        steps = []
        node = self._find(key)
        if node is None:
            self._snap(steps, f"Clé {key} introuvable.", [])
            return steps
        if node.left is None and node.right is None:
            if node.parent is None:
                self.root = None
            elif node is node.parent.left:
                node.parent.left = None
            else:
                node.parent.right = None
            self._snap(steps, f"Feuille {key}: detachee.", [key])
        elif node.left is None or node.right is None:
            child = node.left if node.left is not None else node.right
            if node.parent is None:
                self.root = child
            elif node is node.parent.left:
                node.parent.left = child
            else:
                node.parent.right = child
            child.parent = node.parent
            self._snap(steps, f"Noeud {key} a un enfant: remplace par {child.key}.", [key, child.key])
        else:
            succ = self._min_node(node.right)
            self._snap(steps, f"Noeud {key} a deux enfants: successeur = {succ.key}. Copie de la clé.", [key, succ.key])
            node.key = succ.key
            # delete succ (at most one child)
            parent = succ.parent
            child = succ.right
            if parent is None:
                self.root = child
            elif succ is parent.left:
                parent.left = child
            else:
                parent.right = child
            if child is not None:
                child.parent = parent
            self._snap(steps, f"Suppression du successeur {succ.key} (clé copiée).", [succ.key])
        return steps

    # ---- rotations ----
    def rotate_left(self, key):
        steps = []
        x = self._find(key)
        if x is None or x.right is None:
            self._snap(steps, f"Rotation gauche impossible sur {key}.", [])
            return steps
        y = x.right
        x.right = y.left
        if y.left is not None:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        self._snap(steps, f"Rotation GAUCHE sur {key}: {y.key} devient racine du sous-arbre.", [key, y.key])
        return steps

    def rotate_right(self, key):
        steps = []
        x = self._find(key)
        if x is None or x.left is None:
            self._snap(steps, f"Rotation droite impossible sur {key}.", [])
            return steps
        y = x.left
        x.left = y.right
        if y.right is not None:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.right = x
        x.parent = y
        self._snap(steps, f"Rotation DROITE sur {key}: {y.key} devient racine du sous-arbre.", [key, y.key])
        return steps


# ---------------------------------------------------------------------------
# Red-Black Tree (ARN)
# ---------------------------------------------------------------------------
class RBTree:
    def __init__(self):
        self.NIL = Node(None, "black")
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.NIL.parent = None
        self.root = self.NIL

    def _is_nil(self, n):
        return n is self.NIL or n is None

    def _snap(self, steps, msg, highlight=None):
        steps.append({
            "message": msg,
            "tree": self.snapshot(),
            "highlight": list(highlight) if highlight else [],
        })

    def snapshot(self):
        return self._snap_node(self.root, set())

    def _snap_node(self, node, _seen=None):
        if node is self.NIL or node is None:
            return None
        if _seen is None:
            _seen=set()
        if id(node) in _seen:
            raise RuntimeError(f"CYCLE at node {node.key}")
        _seen.add(id(node))
        return {
            "key": node.key,
            "color": node.color,
            "left": self._snap_node(node.left, _seen),
            "right": self._snap_node(node.right, _seen),
        }

    def _find(self, key):
        cur = self.root
        while cur is not self.NIL:
            if key == cur.key:
                return cur
            if key < cur.key:
                cur = cur.left
            else:
                cur = cur.right
        return None

    def _min_node(self, node):
        cur = node
        while cur.left is not self.NIL:
            cur = cur.left
        return cur

    def _max_node(self, node):
        cur = node
        while cur.right is not self.NIL:
            cur = cur.right
        return cur

    # ---- traversals ----
    def preorder(self):
        out = []

        def dfs(n):
            if n is self.NIL:
                return
            out.append(n.key)
            dfs(n.left)
            dfs(n.right)

        dfs(self.root)
        return out

    def inorder(self):
        out = []

        def dfs(n):
            if n is self.NIL:
                return
            dfs(n.left)
            out.append(n.key)
            dfs(n.right)

        dfs(self.root)
        return out

    def postorder(self):
        out = []

        def dfs(n):
            if n is self.NIL:
                return
            dfs(n.left)
            dfs(n.right)
            out.append(n.key)

        dfs(self.root)
        return out

    def breadth_first(self):
        out = []
        if self.root is self.NIL:
            return out
        q = [self.root]
        while q:
            n = q.pop(0)
            out.append(n.key)
            if n.left is not self.NIL:
                q.append(n.left)
            if n.right is not self.NIL:
                q.append(n.right)
        return out

    # ---- stats ----
    def height(self):
        def h(n):
            if n is self.NIL:
                return 0
            return 1 + max(h(n.left), h(n.right))

        return h(self.root)

    def count(self):
        def c(n):
            if n is self.NIL:
                return 0
            return 1 + c(n.left) + c(n.right)

        return c(self.root)

    def black_height(self):
        # black height of root (number of black nodes on path to leaf, incl. NIL, excl. root? we report node count style)
        def bh(n):
            if n is self.NIL:
                return 1
            left = bh(n.left)
            return (left + (1 if n.color == "black" else 0))

        if self.root is self.NIL:
            return 0
        # subtract root? report bh of root = black nodes below root incl NIL
        return bh(self.root.left) if False else (self._bh(self.root))

    def _bh(self, n):
        if n is self.NIL:
            return 1
        return self._bh(n.left) + (0 if n.color == "red" else 0)  # placeholder, replaced below

    def stats(self):
        return {
            "type": "rb",
            "count": self.count(),
            "height": self.height(),
            "black_height": self._real_bh(self.root),
            "min": (self._min_node(self.root).key if self.root is not self.NIL else None),
            "max": (self._max_node(self.root).key if self.root is not self.NIL else None),
        }

    def _real_bh(self, n):
        # number of black nodes on path from n (exclusive) to NIL (inclusive)
        if n is self.NIL:
            return 1
        # go left
        cnt = 0
        cur = n.left if n.left is not self.NIL else n.right
        # simpler: follow left spine
        cur = n
        c = 0
        while cur is not self.NIL:
            if cur.color == "black":
                c += 1
            # move to a child; if both nil stop
            if cur.left is not self.NIL:
                cur = cur.left
            elif cur.right is not self.NIL:
                cur = cur.right
            else:
                break
        # include NIL leaf
        return c + 1 - (1 if n.color == "black" else 0)  # exclude n itself

    def validate(self):
        violations = []
        if self.root is self.NIL:
            violations.append("OK: arbre vide.")
            return violations
        if self.root.color != "black":
            violations.append("Violation 2: la racine n'est pas noire.")
        # property 4 + black height equality
        counts = []

        def dfs(n, black_cnt):
            if n is self.NIL:
                counts.append(black_cnt + 1)  # NIL is black
                return
            new_cnt = black_cnt + (1 if n.color == "black" else 0)
            if n.color == "red":
                if not self._is_nil(n.left) and n.left.color == "red":
                    violations.append(f"Violation 4: noeud rouge {n.key} a enfant gauche rouge.")
                if not self._is_nil(n.right) and n.right.color == "red":
                    violations.append(f"Violation 4: noeud rouge {n.key} a enfant droit rouge.")
            dfs(n.left, new_cnt)
            dfs(n.right, new_cnt)

        dfs(self.root, 0)
        if len(set(counts)) > 1:
            violations.append(f"Violation 5: hauteurs noires inegales {counts}.")
        if not violations:
            violations.append("OK: arbre rouge-noir valide (proprietes 1-5).")
        return violations

    # ---- rotations ----
    def _rotate_left(self, x, steps, msg=None):
        y = x.right
        if y is self.NIL:
            self._snap(steps, "Rotation gauche impossible.", [])
            return
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        if msg is None:
            msg = f"Rotation GAUCHE sur {x.key}: {y.key} devient racine du sous-arbre."
        self._snap(steps, msg, [x.key, y.key])

    def _rotate_right(self, x, steps, msg=None):
        y = x.left
        if y is self.NIL:
            self._snap(steps, "Rotation droite impossible.", [])
            return
        x.left = y.right
        if y.right is not self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.right = x
        x.parent = y
        if msg is None:
            msg = f"Rotation DROITE sur {x.key}: {y.key} devient racine du sous-arbre."
        self._snap(steps, msg, [x.key, y.key])

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    # ---- search ----
    def search(self, key):
        steps = []
        cur = self.root
        if cur is self.NIL:
            self._snap(steps, "Arbre vide.", [])
            return steps
        while cur is not self.NIL:
            if key == cur.key:
                self._snap(steps, f"Trouve: {key} == {cur.key}.", [cur.key, key])
                return steps
            if key < cur.key:
                self._snap(steps, f"Comparaison {key} < {cur.key}: descente a gauche.", [cur.key, key])
                cur = cur.left
            else:
                self._snap(steps, f"Comparaison {key} > {cur.key}: descente a droite.", [cur.key, key])
                cur = cur.right
        self._snap(steps, f"{key} non trouve dans l'arbre.", [])
        return steps

    def minimum(self):
        steps = []
        cur = self.root
        if cur is self.NIL:
            self._snap(steps, "Arbre vide.", [])
            return steps
        while cur.left is not self.NIL:
            self._snap(steps, f"Descente gauche: {cur.key} -> {cur.left.key}.", [cur.key, cur.left.key])
            cur = cur.left
        self._snap(steps, f"Minimum = {cur.key}.", [cur.key])
        return steps

    def maximum(self):
        steps = []
        cur = self.root
        if cur is self.NIL:
            self._snap(steps, "Arbre vide.", [])
            return steps
        while cur.right is not self.NIL:
            self._snap(steps, f"Descente droite: {cur.key} -> {cur.right.key}.", [cur.key, cur.right.key])
            cur = cur.right
        self._snap(steps, f"Maximum = {cur.key}.", [cur.key])
        return steps

    def successor(self, key):
        steps = []
        node = self._find(key)
        if node is None:
            self._snap(steps, f"Clé {key} introuvable.", [])
            return steps
        if node.right is not self.NIL:
            cur = node.right
            self._snap(steps, f"Successeur: sous-arbre droit de {key}; minimum.", [key, cur.key])
            while cur.left is not self.NIL:
                self._snap(steps, f"Descente gauche: {cur.key} -> {cur.left.key}.", [cur.key, cur.left.key])
                cur = cur.left
            self._snap(steps, f"Successeur de {key} = {cur.key}.", [key, cur.key])
        else:
            cur = node
            parent = node.parent
            while parent is not None and cur is parent.right:
                self._snap(steps, f"Remontee: {cur.key} fils droit de {parent.key}.", [cur.key, parent.key])
                cur = parent
                parent = parent.parent
            if parent is None:
                self._snap(steps, f"Pas de successeur pour {key}.", [key])
            else:
                self._snap(steps, f"Successeur de {key} = {parent.key}.", [key, parent.key])
        return steps

    def predecessor(self, key):
        steps = []
        node = self._find(key)
        if node is None:
            self._snap(steps, f"Clé {key} introuvable.", [])
            return steps
        if node.left is not self.NIL:
            cur = node.left
            self._snap(steps, f"Predecesseur: sous-arbre gauche de {key}; maximum.", [key, cur.key])
            while cur.right is not self.NIL:
                self._snap(steps, f"Descente droite: {cur.key} -> {cur.right.key}.", [cur.key, cur.right.key])
                cur = cur.right
            self._snap(steps, f"Predecesseur de {key} = {cur.key}.", [key, cur.key])
        else:
            cur = node
            parent = node.parent
            while parent is not None and cur is parent.left:
                self._snap(steps, f"Remontee: {cur.key} fils gauche de {parent.key}.", [cur.key, parent.key])
                cur = parent
                parent = parent.parent
            if parent is None:
                self._snap(steps, f"Pas de predecesseur pour {key}.", [key])
            else:
                self._snap(steps, f"Predecesseur de {key} = {parent.key}.", [key, parent.key])
        return steps

    # ---- insert ----
    def insert(self, key):
        steps = []
        z = Node(key, "red")
        y = None
        x = self.root
        path = []
        while x is not self.NIL:
            y = x
            path.append(x.key)
            if key < x.key:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y is None:
            self.root = z
            msg_path = "Arbre vide: z devient racine."
        else:
            if key < y.key:
                y.left = z
            else:
                y.right = z
            msg_path = "Descente: " + " -> ".join(map(str, path)) + f". Insertion de {key} sous {y.key}."
        z.left = self.NIL
        z.right = self.NIL
        # NIL parents (optional)
        self.NIL.parent = z
        self._snap(steps, f"Insertion ABR: {msg_path} Noeud {key} cree ROUGE.", [key])
        self._insert_fixup(z, steps)
        if self.root is not self.NIL and self.root.color != "black":
            self.root.color = "black"
            self._snap(steps, "La racine est colorée en NOIR (propriété 2).", [self.root.key])
        return steps

    def _insert_fixup(self, z, steps):
        while z.parent is not None and z.parent is not self.NIL and z.parent.color == "red":
            p = z.parent
            g = p.parent
            if g is None or g is self.NIL:
                break
            if p is g.left:
                y = g.right
                if y is not self.NIL and y.color == "red":
                    p.color = "black"
                    y.color = "black"
                    g.color = "red"
                    self._snap(steps, f"Cas 1 (oncle {y.key} rouge): {p.key},{y.key} -> NOIR, {g.key} -> ROUGE.", [z.key, p.key, y.key, g.key])
                    z = g
                else:
                    if z is p.right:
                        z = p
                        self._rotate_left(z, steps, f"Rotation GAUCHE sur {z.key} (preparation cas interne).")
                    p = z.parent
                    g = p.parent if p is not None else None
                    if g is None or g is self.NIL:
                        break
                    p.color = "black"
                    g.color = "red"
                    self._rotate_right(g, steps, f"Cas 2 (oncle noir): recoloration + rotation DROITE sur {g.key}.")
            else:
                y = g.left
                if y is not self.NIL and y.color == "red":
                    p.color = "black"
                    y.color = "black"
                    g.color = "red"
                    self._snap(steps, f"Cas 1 (oncle {y.key} rouge): {p.key},{y.key} -> NOIR, {g.key} -> ROUGE.", [z.key, p.key, y.key, g.key])
                    z = g
                else:
                    if z is p.left:
                        z = p
                        self._rotate_right(z, steps, f"Rotation DROITE sur {z.key} (preparation cas interne).")
                    p = z.parent
                    g = p.parent if p is not None else None
                    if g is None or g is self.NIL:
                        break
                    p.color = "black"
                    g.color = "red"
                    self._rotate_left(g, steps, f"Cas 2 (oncle noir): recoloration + rotation GAUCHE sur {g.key}.")

    # ---- delete ----
    def delete(self, key):
        steps = []
        z = self._find(key)
        if z is None:
            self._snap(steps, f"Clé {key} introuvable.", [])
            return steps
        y = z
        y_orig_color = y.color
        y_parent = y.parent
        if z.left is self.NIL and z.right is self.NIL:
            x = z.right
            self._transplant(z, z.right)
            self._snap(steps, f"Noeud {key} est une feuille ({z.color}): supprime.", [key])
        elif z.left is self.NIL:
            x = z.right
            self._transplant(z, z.right)
            self._snap(steps, f"Noeud {key} a un enfant droit: remplace par {x.key if x is not self.NIL else 'NIL'}.", [key])
        elif z.right is self.NIL:
            x = z.left
            self._transplant(z, z.left)
            self._snap(steps, f"Noeud {key} a un enfant gauche: remplace par {x.key if x is not self.NIL else 'NIL'}.", [key])
        else:
            y = self._min_node(z.right)
            y_orig_color = y.color
            y_parent = y.parent
            x = y.right
            if y.parent == z:
                if x is self.NIL:
                    x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
            self._snap(steps, f"Noeud {key} a deux enfants: remplace par successeur {y.key}.", [key, y.key])
        if y_orig_color == "black":
            self._delete_fixup(x, steps)
        # root black
        if self.root is not self.NIL and self.root.color != "black":
            self.root.color = "black"
            self._snap(steps, "La racine est colorée en NOIR.", [self.root.key])
        return steps

    def _delete_fixup(self, x, steps):
        while x is not self.root and (x is self.NIL or x.color == "black"):
            if x.parent is None:
                break
            if x is x.parent.left:
                w = x.parent.right
                if w is self.NIL:
                    x = x.parent
                    continue
                if w.color == "red":
                    w.color = "black"
                    x.parent.color = "red"
                    self._rotate_left(x.parent, steps, "Cas 1 (frere rouge): rotation gauche.")
                    w = x.parent.right
                    if w is self.NIL:
                        x = x.parent
                        continue
                if (w.left is self.NIL or w.left.color == "black") and (w.right is self.NIL or w.right.color == "black"):
                    if w is not self.NIL:
                        w.color = "red"
                    self._snap(steps, f"Cas 2 (frere noir, enfants noirs): {w.key if w is not self.NIL else 'NIL'} -> ROUGE, remontee.", [w.key] if w is not self.NIL else [])
                    x = x.parent
                else:
                    if w.right is self.NIL or w.right.color == "black":
                        if w.left is not self.NIL:
                            w.left.color = "black"
                        w.color = "red"
                        self._rotate_right(w, steps, "Cas 3: rotation droite sur frere.")
                        w = x.parent.right
                        if w is self.NIL:
                            x = x.parent
                            continue
                    w.color = x.parent.color
                    x.parent.color = "black"
                    if w.right is not self.NIL:
                        w.right.color = "black"
                    self._rotate_left(x.parent, steps, "Cas 4: rotation gauche sur parent.")
                    x = self.root
            else:
                w = x.parent.left
                if w is self.NIL:
                    x = x.parent
                    continue
                if w.color == "red":
                    w.color = "black"
                    x.parent.color = "red"
                    self._rotate_right(x.parent, steps, "Cas 1 (frere rouge): rotation droite.")
                    w = x.parent.left
                    if w is self.NIL:
                        x = x.parent
                        continue
                if (w.right is self.NIL or w.right.color == "black") and (w.left is self.NIL or w.left.color == "black"):
                    if w is not self.NIL:
                        w.color = "red"
                    self._snap(steps, f"Cas 2 (frere noir, enfants noirs): {w.key if w is not self.NIL else 'NIL'} -> ROUGE, remontee.", [w.key] if w is not self.NIL else [])
                    x = x.parent
                else:
                    if w.left is self.NIL or w.left.color == "black":
                        if w.right is not self.NIL:
                            w.right.color = "black"
                        w.color = "red"
                        self._rotate_left(w, steps, "Cas 3: rotation gauche sur frere.")
                        w = x.parent.left
                        if w is self.NIL:
                            x = x.parent
                            continue
                    w.color = x.parent.color
                    x.parent.color = "black"
                    if w.left is not self.NIL:
                        w.left.color = "black"
                    self._rotate_right(x.parent, steps, "Cas 4: rotation droite sur parent.")
                    x = self.root
        if x is not self.NIL and x is not None:
            x.color = "black"
            self._snap(steps, "Correction terminee: noeud courant -> NOIR.", [x.key])
        elif x is self.NIL:
            # root side; nothing
            pass

    # ---- rotations (public) ----
    def rotate_left(self, key):
        steps = []
        x = self._find(key)
        if x is None or x.right is self.NIL:
            self._snap(steps, f"Rotation gauche impossible sur {key}.", [])
            return steps
        self._rotate_left(x, steps, f"Rotation GAUCHE sur {key}.")
        return steps

    def rotate_right(self, key):
        steps = []
        x = self._find(key)
        if x is None or x.left is self.NIL:
            self._snap(steps, f"Rotation droite impossible sur {key}.", [])
            return steps
        self._rotate_right(x, steps, f"Rotation DROITE sur {key}.")
        return steps

    # ---- black height helper unused cleanup ----
    def black_height(self):
        return self._real_bh(self.root)


# ---------------------------------------------------------------------------
# Builders from snapshot
# ---------------------------------------------------------------------------
def build_tree(tree_type, snap):
    if tree_type == "bst":
        t = BST()
        t.root = _build_bst(snap)
        return t
    else:
        t = RBTree()
        if snap is None:
            t.root = t.NIL
        else:
            t.root = _build_rb(snap, None, t)
        return t


def _build_bst(snap, parent=None):
    if snap is None:
        return None
    n = Node(snap["key"])
    n.parent = parent
    n.left = _build_bst(snap.get("left"), n)
    n.right = _build_bst(snap.get("right"), n)
    return n


def _build_rb(snap, parent, tree):
    if snap is None:
        return tree.NIL
    n = Node(snap["key"], snap.get("color", "black"))
    n.parent = parent
    n.left = _build_rb(snap.get("left"), n, tree)
    n.right = _build_rb(snap.get("right"), n, tree)
    return n


# Example presets
BST_EXAMPLE = [20, 10, 30, 5, 15, 25, 35, 3, 7, 13, 17, 22, 27, 33, 40]
RB_EXAMPLE = [41, 38, 31, 12, 19, 8]
