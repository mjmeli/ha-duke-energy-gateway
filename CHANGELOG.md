# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

-

### Fixed

-

## [0.0.6] - 2021-08-23

### Fixed

- Fixed bug that happens at midnight when initial data for the day is not reported for 15-30 minutes.

## [0.0.5] - 2021-08-22

### Fixed

- Usage sensor not being setup with the correct unit_of_measurement (which is needed to show it in the energy dashboard).

## [0.0.4] - 2021-08-22

### Fixed

- Usage sensor not being tracked with a state_class of measurement (which is needed to show it in the energy dashboard).

## [0.0.3] - 2021-08-22

### Fixed

- Integration not working in version 2021.8. This will need to be reverted in 2021.9.

## [0.0.2] - 2021-08-22

### Added

- Repo cleanup

## [0.0.1] - 2021-08-22

### Added

- Pulls today's current energy usage into entity sensor.duke_energy_usage_today_kwh

[unreleased]: https://github.com//mjmeli/ha-duke-energy-gateway/compare/0.0.6...HEAD
[0.0.6]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.6
[0.0.5]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.5
[0.0.4]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.4
[0.0.3]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.3
[0.0.2]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.2
[0.0.1]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.1
