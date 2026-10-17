# Examples

This directory hosts example notebooks and usage snippets for the pyPCBA project.

## Install the project

The `pyPCBA_3_14` Conda environment includes the project as an editable install
when created from the repository root with `environment.yml`. To install the
project into an existing environment, run these commands from the repository
root:

```powershell
conda activate pyPCBA_3_14
python -m pip install -e .
```

In VS Code or Jupyter, select the `pyPCBA_3_14` kernel and restart it after
installing. The examples can then import modules such as
`from pyPCBA.lists import e_series`.
