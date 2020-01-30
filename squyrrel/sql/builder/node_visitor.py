

class NodeVisitor:

    def visit(self, node, *args, **kwargs):
        #print(self.__class__.__name__)
        cls_ = type(node)
        method_name = 'visit_' + cls_.__name__
        #print('method_name', method_name)
        visitor = getattr(self, method_name, None)
        if visitor is None:
            #print('Did not find ',method_name)
            for ancestor in cls_.__mro__:
                method_name = 'visit_' + ancestor.__name__
                visitor = getattr(self, method_name, None)
                if visitor:
                    break

        #print(visitor)
        if visitor:
            #print('visitor:', method_name)
            return visitor(node, *args, **kwargs)
        else:
            return str(node)
            #return self.generic_visit(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        text = 'No visit_{} method'.format(type(node).__name__)
        return text