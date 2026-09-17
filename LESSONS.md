# Lessons

- After merging packaging metadata into a uv project, run `uv lock` and then `uv lock --check` before committing.
- A local `.venv` can make source-distribution builds fail on absolute interpreter symlinks; verify the wheel build separately and test sdist creation from a clean source tree.
