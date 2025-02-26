import ast
import json

class ASTVisitor(ast.NodeVisitor):
    """
    Custom AST visitor to traverse and extract details from Python code.
    This class converts AST nodes into a JSON-compatible format.
    """
    def __init__(self):
        """Initializes an empty list to store extracted AST data."""
        self.data = []

    def generic_visit(self, node):
        """
        Processes each AST node and extracts relevant details such as type, line number, and column offset.
        Recursively visits child nodes if present.
        Returns:
            dict: A dictionary representation of the node.
        """
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

    def visit_Module(self, node):
        """
        Handles the top-level module node.
        Extracts all statements in the module body and stores them in a list.
        """
        module_dict = {"type": "Module", "body": []}
        self.data.append(module_dict)

        for statement in node.body:
            module_dict["body"].append(self.visit(statement))

        return module_dict

    def visit_FunctionDef(self, node):
        """
        Extracts function definitions, including function name, arguments, and body.
        Returns:
            dict: A dictionary representation of the function.
        """
        func_dict = {
            "type": "FunctionDef",
            "name": node.name,
            "lineno": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "body": [self.visit(stmt) for stmt in node.body],
        }
        return func_dict

    def visit_Assign(self, node):
        """
        Handles variable assignments.
        Extracts target variables and assigned values.
        Returns:
            dict: A dictionary representation of the assignment statement.
        """
        assign_dict = {
            "type": "Assign",
            "targets": [self.visit(target) for target in node.targets],
            "value": self.visit(node.value) if node.value else None,
            "lineno": node.lineno,
        }
        return assign_dict

    def visit_Name(self, node):
        """
        Extracts variable names and their context (e.g., Load, Store).
        Returns:
            dict: A dictionary representation of the variable.
        """
        return {"type": "Name", "id": node.id, "ctx": type(node.ctx).__name__}

    def visit_Call(self, node):
        """
        Extracts function calls, including function name and arguments.
        Returns:
            dict: A dictionary representation of the function call.
        """
        return {
            "type": "Call",
            "func": self.visit(node.func),
            "args": [self.visit(arg) for arg in node.args],
            "lineno": node.lineno,
        }

def analyze_ast(code):
    """
    Parses the given Python code into an Abstract Syntax Tree (AST) and converts it to JSON format.
    Returns:
        str: A JSON string representing the AST structure of the code.
    """
    try:
        tree = ast.parse(code)
        visitor = ASTVisitor()
        visitor.visit(tree)
        return json.dumps(visitor.data, indent=4)
    except SyntaxError as e:
        return json.dumps({"error": f"Syntax Error: {e.msg} at line {e.lineno}, column {e.offset}"}, indent=4)
