## IMPORTANT - DEPRECATED

Duke Energy shut down the Gateway pilot program at the end of June 2023. This integration has stopped functioning and is deprecated.

# <img height="80" src="https://github.com/mjmeli/ha-duke-energy-gateway/blob/main/assets/logo.png?raw=true" alt="Duke Energy Logo"> Duke Energy Gateway

[![GitHub Release][releases-shield]][releases]
[![GitHub Build][build-shield]][build]
[![GitHub Activity][commits-shield]][commits]

[![License][license-shield]](LICENSE)
[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

This is a custom integration for [Home Assistant](https://www.home-assistant.io/). It pulls real-time energy usage from Duke Energy via the Duke Energy Gateway pilot program.

This integration leverages the [`pyduke-energy`](https://github.com/mjmeli/pyduke-energy) library, also written by me, to pull data. This API is _very_ unofficial and may stop working at any time (see [Disclaimer](https://github.com/mjmeli/pyduke-energy#Disclaimer)).

## Pre-Requisites! (Please Read)

You are required to have a Duke Energy Gateway connected to your smartmeter for this to work. This is a **separate** device than your Smart Meter and is provided by an invitation only program at the moment. If you don't know what this is, then you probably don't have it. This integration does not support any other method of retrieving data (see [Gateway Requirement](https://github.com/mjmeli/pyduke-energy#gateway-requirement)).

## Sensors

This component will set up the following entities:

### `sensor.duke_energy_current_usage_w`

- Represents the real-time _power_ usage in watts.
- This data is pushed from the gateway device every 1-3 seconds. _NOTE:_ This produces a lot of data. If this update interval is too frequent for you, you can configure a throttling interval in seconds (see [Configuration](#Configuration) below).
- Note that since this is power usage, it cannot be used as-is for the Home Assistant energy dashboard. Instead, you can use the `sensor.duke_energy_usage_today_kwh` sensor, or you need to feed this real-time sensor through the [Riemann sum integral integration](https://www.home-assistant.io/integrations/integration/).
- Additional attributes are available containing the meter ID and gateway ID.

### `sensor.duke_energy_usage_today_kwh`

- Represents today's _energy_ consumption in kilowatt-hours (from 0:00 local time to 23:59 local time, then resetting).
- This data is polled every 60 seconds, but data may be delayed up to 15 minutes due to delays in Duke Energy reporting it (see [Limitations](https://github.com/mjmeli/pyduke-energy#Limitations) in the `pyduke-energy` repo.).
- This can be used as-is for the Home Assistant energy consumption dashboard.
- Additional attributes are available containing the meter ID, gateway ID, and the timestamp of the last measurement.

## Installation

### HACS Installation

1. Add as a Custom Repository under Settings in HACS: `mjmeli/ha-duke-energy-gateway` and choose `Integration` as the Category.
2. Search for "Duke Energy Gateway" in HACS and the integration should now be returned as a search result. Click on it, click the "Download" button, and walk through the prompts to download.
3. Restart Home Assistant
4. In the HA UI go to "Settings" -> "Devices and Services", make sure you are on the Integrations tab, then click "+" and search for "Duke Energy Gateway". This will let you set it up.

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `duke_energy_gateway`.
4. Download _all_ the files from the `custom_components/duke_energy_gateway/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Settings" -> "Devices and Services", make sure you are on the Integrations tab, then click "+" and search for "Duke Energy Gateway". This will let you set it up.

## Configuration

Configuration will be done in the UI. Initially, you will need to provide the following data:

| Data       | Description                         |
| ---------- | ----------------------------------- |
| `email`    | Your login email to Duke Energy.    |
| `password` | Your login password to Duke Energy. |

After the integration is setup, you will be able to do further configuration by clicking "Configure" on the integration page. This will allow you to modify the following options:

| Data                                    | Description                                                                                                                                                                                                                                                                                                                                          |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Real-time Usage Update Interval (sec)` | By default, the real-time usage sensor will be updated any time a reading comes in. If this data is too frequent, you can configure this value to throttle the data. When set to a positive integer `X`, the sensor will only be updated once every `X` seconds. In other words, if set to 30, you will get a new real-time usage every ~30 seconds. |

### Meter Selection

The configuration flow will automatically attempt to identify your gateway and smartmeter. Right now, only one is supported per account. The first one identified will be used. If one cannot be found, the configuration process should fail.

If your meter selection fails, a first step should be to enable logging for the component (see [Logging](#Logging)). If this does not give insight into the problem, please open a GitHub issue.

### Logging

If you run into any issues and want to look into the logs, this integration provides verbose logging at the debug level. That can be enabled by adding the following to your `configuration.yaml` file.

```yaml
logger:
  default: info
  logs:
    custom_components.duke_energy_gateway: debug
    pyduke_energy.client: debug
    pyduke_energy.realtime: debug
```

## Development

I suggest using the dev container for development by opening in Visual Studio Code with `code .` and clicking on the option to re-open with dev container. In VS Code, you can run the task "Run Home Assistant on the port 9123" and then access it via http://localhost:9123.

If you want to install manually, you can install dev dependencies with `pip install -r requirements_dev.txt`.

Before commiting, run `pre-commit run --all-files`.

### Working With In Development `pyduke-energy` Versions

If you are working on implementing new changes from `pyduke-energy` but do not want to release version of that library, you can set up your development environment to install from a remote working branch.

1. Update [`requirements_dev.txt`](requirements_dev.txt) to replace the `main` in `git+https://github.com/mjmeli/pyduke-energy@main` with your working branch and update the username if you have a fork (e.g. `git+https://github.com/notmjmeli/pyduke-energy@new-feature-dev-branch`)
2. Uninstall locally cached version of `pyduke-energy`: `pip uninstall -y pyduke-energy`
3. Re-run requirements installation: `pip install -r requirements_dev.txt`

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/mjmeli
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/mjmeli/ha-duke-energy-gateway.svg?style=for-the-badge
[commits]: https://github.com/mjmeli/ha-duke-energy-gateway/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/mjmeli/ha-duke-energy-gateway.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40mjmeli-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mjmeli/ha-duke-energy-gateway.svg?style=for-the-badge
[releases]: https://github.com/mjmeli/ha-duke-energy-gateway/releases
[build-shield]: https://img.shields.io/github/actions/workflow/status/mjmeli/ha-duke-energy-gateway/tests.yaml?style=for-the-badge
[build]: https://github.com/mjmeli/ha-duke-energy-gateway/actions/workflows/tests.yaml
[user_profile]: https://github.com/mjmeli
