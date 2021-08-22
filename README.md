# <img height="80" src="https://github.com/mjmeli/ha-duke-energy-gateway/blob/main/icons/full_logo.png?raw=true" alt="Duke Energy Logo"> Duke Energy Gateway

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

This is a custom integration for [Home Assistant](https://www.home-assistant.io/). It pulls near-real-time energy usage from Duke Energy via the Duke Energy Gateway pilot program.

This component will set up the following entities.

| Platform                             | Description                                                                                                                                                                                                           |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sensor.duke_energy_usage_today_kwh` | Represents today's energy consumption (from 0:00 local time to 23:59 local time, then resetting). Additional attributes are available containing the meter ID, gateway ID, and the timestamp of the last measurement. |

This integration leverages the [`pyduke-energy`](https://github.com/mjmeli/pyduke-energy) library, also written by me, to pull data. This API is _very_ unofficial and may stop working at any time (see [Disclaimer](https://github.com/mjmeli/pyduke-energy#Disclaimer)). Also, you are required to have a Duke Energy Gateway connected to your smartmeter for this to work. This integration does not support any other method of retrieving data (see [Gateway Requirement](https://github.com/mjmeli/pyduke-energy#gateway-requirement)).

Energy usage will be provided as _daily_ data, resetting at midnight local time. At the moment, the API appears to be limited to providing new records every 15 minutes, meaning readings could be delayed up to 15 minutes. For more information, see [limitations](https://github.com/mjmeli/pyduke-energy#limitations) in the `pyduke-energy` repo.

## Installation

### HACS Installation

1. Add as a Custom Repository under Settings in HACS: `mjmeli/ha-duke-energy-gateway` and choose `Integration` as the Category.
2. Restart Home Assistant
3. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Duke Energy Gateway"

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `duke_energy_gateway`.
4. Download _all_ the files from the `custom_components/duke_energy_gateway/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Duke Energy Gateway"

## Configuration is done in the UI

Configuration will be done in the UI. You will need to provide the following data:

| Data       | Description                         |
| ---------- | ----------------------------------- |
| `email`    | Your login email to Duke Energy.    |
| `password` | Your login password to Duke Energy. |

### Meter Selection

The configuration flow will automatically attempt to identify your gateway and smartmeter. Right now, only one is supported per account. The first one identified will be used. If one cannot be found, the configuration process should fail.

## Development

After cloning the repo, you can install dev dependencies with `pip install -r requirements_dev.txt`. Then, open Visual Studio Code with `code .` and make sure to re-open with the dev container. In VS Code, you can run the task "Run Home Assistant on the port 9123" and then access it via http://localhost:9123.

Before commiting, run `pre-commit run --all-files`.

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
[user_profile]: https://github.com/mjmeli
