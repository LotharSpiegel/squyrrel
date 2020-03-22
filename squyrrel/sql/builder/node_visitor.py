

class NodeVisitor:

    def visit(self, node, *args, **kwargs):
        cls_ = type(node)
        method_name = 'visit_' + cls_.__name__
        visitor = getattr(self, method_name, None)
        if visitor is None:
            for ancestor in cls_.__mro__:
                method_name = 'visit_' + ancestor.__name__
                visitor = getattr(self, method_name, None)
                if visitor:
                    break

        if visitor:
            return visitor(node, *args, **kwargs)
        else:
            # print(f'no visit_ found for {cls_.__name__}')
            try:
                return repr(node)
            except TypeError:
                raise Exception(f'Node {node.__class__.__name__}.__repr__ did not return str!')
            #return self.generic_visit(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        text = 'No visit_{} method'.format(type(node).__name__)
        return text