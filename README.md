# Cookiecutter Template for Azure IoT Edge Python Module

`cookiecutter-azure-iot-edge-module` creates a base template to start a new Azure IoT Edge Python module

## Prerequisites
Install [Cookiecutter](https://github.com/audreyr/cookiecutter):
```
$ pip install -U cookiecutter
```

## Usage
```
$ cookiecutter https://github.com/sarthakvijayvergiya/azure-iot-edge-module.git --checkout main
```
and follow the interactive prompts.

If you prefer one-liner:
```
$ cookiecutter --no-input https://github.com/sarthakvijayvergiya/azure-iot-edge-module.git module_name=<module_name> image_repository=<image_repository> --checkout main
```

For example:
```
$ cookiecutter --no-input https://github.com/sarthakvijayvergiya/azure-iot-edge-module.git module_name=filterModule image_repository=localhost:5000/filtermodule --checkout main
```