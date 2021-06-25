## Development ##
Before adding new commits make sure pre-commit is installed `https://pre-commit.com#install` and the following commands are executed inside the repository:
```
pre-commit clean
pre-commit install
pre-commit install-hooks
```
Before commiting run the hooks on all files:
```
pre-commit run --all-files
```

## Requirements
Python >= 3.8
QGIS >= 3.14

## Ohsome Qgis Plugin
Per default the QGIS native temporal feature (version >= 3.14) is activated, if the result contains suitable geometries.

The Temporal Controller can be accessed via `View` -> `Panels` -> `Temporal Controller`.



![Screenshot](static/ohsome_tab1.png)
![Screenshot](static/ohsome_tab2.png)
![Screenshot](static/ohsome_tab3.png)
