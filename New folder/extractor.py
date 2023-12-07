import nbformat
from nbconvert import PythonExporter
import ast
import sys


def convert_notebook_to_script(notebook_path, script_path):
    # Load notebook
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    # Convert to Python script
    python_exporter = PythonExporter()
    python_script, _ = python_exporter.from_notebook_node(nb)

    # Write to .py file
    with open(script_path, 'w') as f:
        f.write(python_script)


def extract_functions_and_imports(filename):

  functions = {}
  imports = []
  
  with open(filename, "r") as source:
    lines = source.readlines()

    # Start reading imports after the start marker and stop at the end marker
    read_imports = False
    for line in lines:
        if "# -- IMPORTS START --" in line:
            read_imports = True
        elif "# -- IMPORTS END --" in line:
            read_imports = False
        elif read_imports:
            imports.append(line.strip())

    print(lines)
    # Now parse the source code into an AST
    tree = ast.parse("".join(lines))

    for node in ast.walk(tree):
      if isinstance(node, ast.FunctionDef):
        functions[node.name] = ast.unparse(node)
        
  return imports, functions


if __name__ == "__main__":

  if len(sys.argv) < 2:
    print("Usage: python script.py <notebook>")
    sys.exit(1)

  notebook_name = sys.argv[1]

  if not notebook_name.endswith(".ipynb"):
    print("Invalid notebook name")
    sys.exit(1)

  notebook_base = notebook_name[:-6]
  py_file = notebook_base + ".py"

  # Convert notebook to py script
  convert_notebook_to_script(notebook_name, py_file)  

  # Extract functions and imports
  imports, functions = extract_functions_and_imports(py_file)

  # Write imports and functions to output 
  with open(py_file, "w") as f:
    f.write("\n".join(imports) + "\n\n")
    for name, func in functions.items():
      f.write(func + "\n\n")

  print(f"Generated {py_file} from {notebook_name}")
