import os
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

def run_and_save_notebook(notebook_path, timeout=300):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
    try:
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path) or '.'}})
    except CellExecutionError as e:
        print(f"Error executing the notebook {notebook_path}: {e}")
        sys.exit(1)
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print(f"Executed and saved: {notebook_path}")

def main():
    notebooks_dir = os.path.join(os.path.dirname(__file__), '..', 'notebooks')
    for fname in os.listdir(notebooks_dir):
        if fname.endswith('.ipynb'):
            run_and_save_notebook(os.path.join(notebooks_dir, fname))

if __name__ == "__main__":
    main()
