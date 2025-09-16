# pamo-report-builder
A utlility that parses a toml file and uses the content along with discrete functions to create a multi-sheet Excel worklbook.
### How to use
The pamo-report-builder should be installed automtaically by pvenv_setup but if this doesn't happen or if you don't want to use pvenv_setup you can install using the following Python code.
```python
!pip install git+https://github.com/ministryofjustice/pamo-report-builder.git
```
Once installed you can import the builder and generate a report as per the example below.
```python
from report_builder import create_report
create_report.build_from_toml("report_config.toml")
```
Once you have setup your project folder and the virtual environment, add your report_config.toml and builder.py files into the same folder.
For examples of these see https://github.com/ministryofjustice/pamo-report-builder/tree/main/src/examples
