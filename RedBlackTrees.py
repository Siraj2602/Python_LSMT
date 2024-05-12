from collections import deque


BLACK = True
RED = False


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.p = None # parent
        self.color = RED
        self.left = None
        self.right = None

    def print_color(self):
        if self.color == BLACK:
            return '(b)'
        return '(r)'


class RedBlackTree:
    def __init__(self):
        self.NIL = Node(-1, None) # arbitrary value
        self.NIL.color = BLACK
        self.NIL.left = None
        self.NIL.right = None
        self.root = self.NIL
        self.length = 0

    # O(1)
    def left_rotate(self, x):
        y = x.right
        x.right = y.left 

        if y.left != self.NIL:
            y.left.p = x
        
        y.p = x.p 

        if x.p is None:
            self.root = y
        elif x == x.p.left:
            x.p.left = y
        else:
            x.p.right = y 

        y.left = x 
        x.p = y

    # O(1)
    def right_rotate(self, x):
        y = x.left 
        x.left = y.right 

        if y.right != self.NIL:
            y.right.p = x

        y.p = x.p 

        if x.p is None:
            self.root = y 
        elif x == x.p.right:
            x.p.right = y 
        else:
            x.p.left = y 

        y.right = x 
        x.p = y

    # O(logn) total
    def insert(self, element):
        key, value = element
        z = Node(key, value)
        self.length += 1
        z.left = self.NIL
        z.right = self.NIL

        y = None 
        x = self.root
        
        while x != self.NIL:
            y = x
            if z.key < x.key:
                x = x.left 
            else:
                x = x.right 
        
        z.p = y 
        if y == None:
            self.root = z 
        elif z.key < y.key: 
            y.left = z 
        else:
            y.right = z

        self.insert_fixup(z)

    # O(logn)
    def insert_fixup(self, z):
        while z.p and z.p.color == RED:
            if z.p == z.p.p.left:
                y = z.p.p.right 
                if y.color == RED:
                    z.p.color = BLACK
                    y.color = BLACK 
                    z.p.p.color = RED
                    z = z.p.p
                else:
                    if z == z.p.right:
                        z = z.p 
                        self.left_rotate(z)
                    z.p.color = BLACK
                    z.p.p.color = RED 
                    self.right_rotate(z.p.p)
            else:
                y = z.p.p.left 
                if y.color == RED:
                    z.p.color = BLACK
                    y.color = BLACK
                    z.p.p.color = RED
                    z = z.p.p
                else:
                    if z == z.p.left:
                        z = z.p 
                        self.right_rotate(z)
                    z.p.color = BLACK
                    z.p.p.color = RED 
                    self.left_rotate(z.p.p)
            if z == self.root:
                break
        self.root.color = BLACK

    # O(logn) total
    def delete(self, key):
        z = self.search(key)

        if z == self.NIL:
            return "Key not found!"

        y = z
        y_orig_color = y.color 
        
        # case 1
        if z.left == self.NIL:
            x = z.right 
            self.transplant(z, z.right)
        # case 2
        elif z.right == self.NIL:
            x = z.left
            self.transplant(z, z.left)
        # case 3
        else:
            y = self.minimum(z.right)
            y_orig_color = y.color
            x = y.right 
            
            if y.p == z:
                x.p = y
            else:
                self.transplant(y, y.right)
                y.right = z.right
                y.right.p = y
            
            self.transplant(z, y)
            y.left = z.left 
            y.left.p = y 
            y.color = z.color 
        
        if y_orig_color == BLACK:
            self.delete_fixup(x)

    # O(logn)
    def delete_fixup(self, x):
        while x != self.root and x.color == BLACK:
            if x == x.p.left:
                w = x.p.right
                # type 1
                if w.color == RED:
                    w.color = BLACK
                    x.p.color = RED
                    self.left_rotate(x.p)
                    w = x.p.right
                # type 2
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED 
                    x = x.p 
                else:
                    # type 3
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self.right_rotate(w)
                        w = x.p.right
                    # type 4
                    w.color = x.p.color 
                    x.p.color = BLACK 
                    w.right.color = BLACK 
                    self.left_rotate(x.p)
                    x = self.root
            else:
                w = x.p.left
                # type 1
                if w.color == RED:
                    w.color = BLACK
                    x.p.color = RED
                    self.right_rotate(x.p)
                    w = x.p.left
                # type 2
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED 
                    x = x.p 
                else:
                    # type 3
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self.left_rotate(w)
                        w = x.p.left
                    # type 4
                    w.color = x.p.color 
                    x.p.color = BLACK 
                    w.left.color = BLACK 
                    self.right_rotate(x.p)
                    x = self.root
        x.color = BLACK

    # O(1)
    def transplant(self, u, v):
        if u.p == None:
            self.root = v
        elif u == u.p.left:
            u.p.left = v 
        else:
            u.p.right = v
        v.p = u.p 

    # O(h) = O(logn) for RB trees
    def minimum(self, x):
        while x.left != self.NIL:
            x = x.left
        return x

    # O(h) = O(logn) for RB trees
    def search(self, key):
        x = self.root
        while x != self.NIL and key != x.key:
            if key < x.key:
                x = x.left
            else:
                x = x.right
        if x == self.NIL:
            return False
        return x

    def range_query(self, start_key, end_key):
        result = []
        self._range_query_helper(self.root, start_key, end_key, result)
        return result

    def _range_query_helper(self, node, start_key, end_key, result):
        if node is None:
            return
        
        # If node's key is within the range, recursively search left and right subtrees
        if start_key <= node.key <= end_key:
            self._range_query_helper(node.left, start_key, end_key, result)
            result.append((node.key, node.value))
            self._range_query_helper(node.right, start_key, end_key, result)
        # If node's key is less than start_key, search right subtree
        elif node.key < start_key:
            self._range_query_helper(node.right, start_key, end_key, result)
        # If node's key is greater than end_key, search left subtree
        elif node.key > end_key:
            self._range_query_helper(node.left, start_key, end_key, result)

    def _inorder_helper(self, node, result):
        if node == self.NIL:
            return
        self._inorder_helper(node.left, result)
        result.append((node.key, node.value))
        self._inorder_helper(node.right, result)

    def inorder_traversal(self):
        result = []
        self._inorder_helper(self.root, result)
        return result