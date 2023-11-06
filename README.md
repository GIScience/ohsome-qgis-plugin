# ohsomeTools: ohsome API QGIS Plugin

- [ohsomeTools: ohsome API QGIS Plugin](#ohsometools-ohsome-api-qgis-plugin)
  * [Functionalities](#functionalities)
    + [General](#general)
    + [Customization](#customization)
  * [Getting Started](#getting-started)
    + [Prerequisites](#prerequisites)
    + [Installation](#installation)
      - [Install via private QGIS repository](#install-via-private-qgis-repository)
      - [Install manually from GitHub](#install-manually-from-github)
  * [License](#license)
  * [Acknowledgements](#acknowledgements)
  * [Development](#development)


Per default the QGIS native temporal feature (version >= 3.14) is activated, if the result contains suitable geometries.

The Temporal Controller can be accessed via `View` -> `Panels` -> `Temporal Controller`.

![Screenshot](static/ohsome_tab1.png)
![Screenshot](static/ohsome_tab2.png)

**Note, only QGIS >= v3.14 is supported.**

Set of tools to use the [ohsome API](https://api.ohsome.org) in QGIS.

ohsomeTools gives you easy access to the following API endpoints:

- [Elements Aggregation](https://docs.ohsome.org/ohsome-api/stable/endpoints.html#elements-aggregation)
- [Users Aggregation](https://docs.ohsome.org/ohsome-api/stable/endpoints.html#users-aggregation)
- [Contributions Aggregation](https://docs.ohsome.org/ohsome-api/stable/endpoints.html#contributions-aggregation)
- [Elements Extraction](https://docs.ohsome.org/ohsome-api/stable/endpoints.html#elements-extraction)
- [Elements Full History Extraction](https://docs.ohsome.org/ohsome-api/stable/endpoints.html#elements-full-history-extraction)
- [Contributions Extraction](https://docs.ohsome.org/ohsome-api/stable/endpoints.html#contributions-extraction)

For additional information on how to use the individual GUI elements:
- [Filter](https://docs.ohsome.org/ohsome-api/stable/filter.html)
- [Grouping](https://docs.ohsome.org/ohsome-api/stable/group-by.html)
- [Time/Intervals](https://docs.ohsome.org/ohsome-api/stable/time.html)

The [API Documentation]([API Endpoints](https://docs.ohsome.org/ohsome-api/stable/endpoints.html)) offers plenty of
resources on how to use the API. You can use the information analog for the QGIS plugin.

In case of issues/bugs, please use the [issue tracker](https://github.com/GIScience/ohsome-qgis-plugin/issues).

See also:

- Host your own local [docker instance](https://github.com/GIScience/ohsome-api-dockerized) of the ohsome API for faster
  usage.
- Check out the [ohsome dashboard](https://ohsome.org/apps/dashboard) or ohsomeHeX (the
  [OSM History Explorer](https://ohsome.org/apps/osm-history-explorer)) to get an idea of what is possible by using the
  ohsome API.

## Functionalities

### General

Use QGIS to query OSM data with defining spatial and temporal requests by using the ohsome API.

The current state offers only GUI related requests with limited batch functionalities.

### Customization

The API is free of charge and doesn't require any registration or API-Key.

For faster results without size or time limits by the public API it is possible to host a private instance by using a
local [Dockerized ohsome API](https://github.com/GIScience/ohsome-api-dockerized).

Configuration takes place either from the Web menu entry *ohsomeTools* ► *Provider settings*. Or from *Config* button in
the GUI.

## Getting Started

### Prerequisites

QGIS version: min. **v3.14**

### Installation

#### Install via QGIS repository

Install from the QGis-plugin-manager. Just search for ohsomeTools and click install.   
- `Plugins -> Manage and Install Plugins -> Not Installed -> Search for "OhsomeTools" -> Click "Install Plugin"`

#### Install via private QGIS repository

Open the repository manager:
- `Plugins -> Manage and Install Plugins -> Settings -> Scroll down to "Plugin Repositories" -> Press Add`

Insert and apply the following details for a new private qgis repository:
```text
Name: ohsomeTools
URL: https://raw.githubusercontent.com/GIScience/ohsome-qgis-plugin/main/qgis-private-release.xml
Parameters: Should be at least "?qgis=3.14". If it is lower than .14 please upgrade your QGIS.
Authentication: Leave empty
Enabled: Check.
```

Go to all and search for "ohsome". The plugin should appear as "ohsomeTools".
Click and install.
If it tells you "There is a new update available", just ignore it.



#### Install manually from GitHub

- [Download](https://github.com/GIScience/ohsome-qgis-plugin/archive/main.zip) ZIP file from GitHub
- Unzip folder contents and copy `ohsomeTools` folder to:
    - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
    - Windows: `C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
    - Mac OS: `Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`

## License

This project is published under the GPLv3 license,
see [LICENSE.md](https://github.com/GIScience/ohsome-qgis-plugin/blob/master/LICENSE) for details.

## Acknowledgements

This project was first started by [Julian Psotta](https://github.com/MichaelsJP)
under [https://github.com/MichaelsJP/ohsome-qgis-plugin](https://github.com/MichaelsJP/ohsome-qgis-plugin).

## Development

Before adding new commits make sure pre-commit is installed `https://pre-commit.com#install` and the following commands
need to be executed inside the repository:

```
pre-commit clean
pre-commit install
pre-commit install-hooks
```

Before committing run the hooks on all files:

```
pre-commit run --all-files
```
