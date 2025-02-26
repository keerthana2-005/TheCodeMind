import ast
import json

class ASTVisitor(ast.NodeVisitor):
    
    # Initializes an empty list to store AST node data
    def __init__(self):
        self.data = []

    # Visits each AST node and returns its dictionary representation
    def generic_visit(self, node):
        node_dict = {"type": type(node).__name__}

        if hasattr(node, "lineno"):
            node_dict["lineno"] = node.lineno
        if hasattr(node, "col_offset"):
            node_dict["col_offset"] = node.col_offset

        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                node_dict[field] = [self.visit(item) for item in value if isinstance(item, ast.AST)]
            elif isinstance(value, ast.AST):
                node_dict[field] = self.visit(value)
            else:
                node_dict[field] = value

        return node_dict

    # Processes the module node and stores its body
    def visit_Module(self, node):
        module_dict = {"type": "Module", "body": []}
        self.data.append(module_dict)

        for statement in node.body:
            module_dict["body"].append(self.visit(statement))

        return module_dict

# Parses Python code into an AST and returns its JSON representation
def analyze_ast(code):
    try:
        tree = ast.parse(code)
        visitor = ASTVisitor()
        visitor.visit(tree)
        return json.dumps(visitor.data, indent=4)
    except SyntaxError as e:
        return json.dumps({"error": f"Syntax error: {e}"}, indent=4)
