from .node_visitor import NodeVisitor



class SqlBuilder(NodeVisitor):

    def build(self, node):
        return self.visit(node)