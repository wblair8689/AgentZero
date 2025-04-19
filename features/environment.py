import sys
import os

# Add the project root directory (one level up from features) to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# src_path = os.path.join(project_root, 'src') # Old path

# Use project_root instead of src_path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Optional: You can define hooks like before_all, after_all, etc., here if needed later.
# def before_all(context):
#     pass

# def after_all(context):
#     pass 