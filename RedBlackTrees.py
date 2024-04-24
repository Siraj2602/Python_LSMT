class Node:
    def __init__(self, key, value, color='RED'):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.color = color

class RedBlackTree:
    def __init__(self):
        self.root = None
        self.length = 0

    def insert(self, key, value):
        node = Node(key, value)
        self._insert_helper(node)
        self.length += 1

    def _insert_helper(self, node):
        parent = None
        current = self.root

        while current is not None:
            parent = current
            if node.key < current.key:
                current = current.left
            else:
                current = current.right

        node.parent = parent
        if parent is None:
            self.root = node
        elif node.key < parent.key:
            parent.left = node
        else:
            parent.right = node

        node.left = None
        node.right = None
        node.color = 'RED'
        self._insert_fixup(node)

    def _insert_fixup(self, node):
        while node.parent is not None and node.parent.color == 'RED':
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle is not None and uncle.color == 'RED':
                    node.parent.color = 'BLACK'
                    uncle.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._left_rotate(node)
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._right_rotate(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle is not None and uncle.color == 'RED':
                    node.parent.color = 'BLACK'
                    uncle.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._right_rotate(node)
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._left_rotate(node.parent.parent)

        self.root.color = 'BLACK'

    def _left_rotate(self, node):
        right_child = node.right
        node.right = right_child.left
        if right_child.left is not None:
            right_child.left.parent = node
        right_child.parent = node.parent
        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child
        right_child.left = node
        node.parent = right_child

    def _right_rotate(self, node):
        left_child = node.left
        node.left = left_child.right
        if left_child.right is not None:
            left_child.right.parent = node
        left_child.parent = node.parent
        if node.parent is None:
            self.root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child
        left_child.right = node
        node.parent = left_child

    def delete(self, key):
        node = self.search(key)
        if node is None:
            return
        self._delete_node(node)
        self.length -= 1

    def _delete_node(self, node):
        if node.left is None or node.right is None:
            child = node.right if node.left is None else node.left
            self._transplant(node, child)
            if node.color == 'BLACK':
                self._delete_fixup(child)
        else:
            successor = self._minimum(node.right)
            original_color = successor.color
            self._transplant(successor, successor.right)
            successor.right = node.right
            successor.right.parent = successor
            self._transplant(node, successor)
            successor.left = node.left
            successor.left.parent = successor
            successor.color = node.color
            if original_color == 'BLACK':
                self._delete_fixup(successor)

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    def _delete_fixup(self, node):
        while node != self.root and node.color == 'BLACK':
            if node == node.parent.left:
                sibling = node.parent.right
                if sibling.color == 'RED':
                    sibling.color = 'BLACK'
                    node.parent.color = 'RED'
                    self._left_rotate(node.parent)
                    sibling = node.parent.right
                if (sibling.left.color == 'BLACK' and
                    sibling.right.color == 'BLACK'):
                    sibling.color = 'RED'
                    node = node.parent
                else:
                    if sibling.right.color == 'BLACK':
                        sibling.left.color = 'BLACK'
                        sibling.color = 'RED'
                        self._right_rotate(sibling)
                        sibling = node.parent.right
                    sibling.color = node.parent.color
                    node.parent.color = 'BLACK'
                    sibling.right.color = 'BLACK'
                    self._left_rotate(node.parent)
                    node = self.root
            else:
                sibling = node.parent.left
                if sibling.color == 'RED':
                    sibling.color = 'BLACK'
                    node.parent.color = 'RED'
                    self._right_rotate(node.parent)
                    sibling = node.parent.left
                if (sibling.right.color == 'BLACK' and
                    sibling.left.color == 'BLACK'):
                    sibling.color = 'RED'
                    node = node.parent
                else:
                    if sibling.left.color == 'BLACK':
                        sibling.right.color = 'BLACK'
                        sibling.color = 'RED'
                        self._left_rotate(sibling)
                        sibling = node.parent.left
                    sibling.color = node.parent.color
                    node.parent.color = 'BLACK'
                    sibling.left.color = 'BLACK'
                    self._right_rotate(node.parent)
                    node = self.root
        node.color = 'BLACK'

    def search(self, key):
        current = self.root
        while current is not None:
            if key == current.key:
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def _minimum(self, node):
        while node.left is not None:
            node = node.left
        return node

    def _inorder_helper(self, node, result):
        if node is None:
            return
        if node is not None:
            self._inorder_helper(node.left, result)
            result.append((node.key, node.value))
            self._inorder_helper(node.right, result)


    def inorder_traversal(self):
        result = []
        self._inorder_helper(self.root, result)
        return result

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


# Example usage:
"""
if __name__ == "__main__":
    rb_tree = RedBlackTree()
    keys = [10, 5, 15, 3, 7, 12, 18, 1, 4, 6, 8, 11, 13, 17, 20]

    for key in keys:
        rb_tree.insert(key)

    print("Length of Tree : ", rb_tree.length)
    print("Inorder traversal of the Red-Black Tree:")
    rb_tree.inorder_traversal()

    search_key = 10
    result = rb_tree.search(search_key)
    if result is not None:
        print(f"Node with key {search_key} found.")
    else:
        print(f"Node with key {search_key} not found.")

    delete_key = 15
    rb_tree.delete(delete_key)
    print(f"Node with key {delete_key} deleted.")
    print("Length of tree is ", rb_tree.length)

    print("Inorder traversal after deletion:")
    rb_tree.inorder_traversal()
"""