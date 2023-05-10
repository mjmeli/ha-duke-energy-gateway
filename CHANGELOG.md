# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

-

### Fixed

-

## [0.1.7] - 2023-05-10

### Fixed

- Update pydukeenergy version to 1.0.6 to get updated basic auth digest

## [0.1.6] - 2023-05-04

### Fixed

- fix await issue

## [0.1.5] - 2023-05-04

### Fixed

- update to async_write_ha_state

## [0.1.4] - 2023-01-06

### Fixed

- Update pydukeenergy version to 1.0.5 to increase time at which MQTT timeouts fail realtime stream

## [0.1.3] - 2023-01-06

### Fixed

- Update pydukeenergy version to 1.0.3 to fix realtime stream constantly timing out (fixes #153)

## [0.1.2] - 2022-09-07

### Fixed

- Update pydukeenergy version to 1.0.2 to fix account details errors on initialization (fixes #128)

## [0.1.1] - 2022-05-24

### Fixed

- Update pydukeenergy version to 1.0.1 to fix login issue by @mjmeli in #101 (fixes #100)

## [0.1.0] - 2021-12-28

This is a large feature update to the Duke Energy integration. This is a large refactoring of the integration required to implement a new sensor - realtime power usage!

Highlights of this release will be:

- Moved default meter selection logic into abstracted pyduke-energy function select_default_meter
- Implementation of real-time power usage sensor
  - New sensor `sensor.duke_energy_current_usage_w` that represents the real-time power usage in watts.
  - This data is pushed from the gateway device every 1-3 seconds. NOTE: This produces a lot of data. If this update interval is too frequent for you, you can configure a throttling interval in seconds via the integration configuration.
  - Note that since this is power usage, it cannot be used as-is for the Home Assistant energy dashboard. Instead, you can use the `sensor.duke_energy_usage_today_kwh` sensor, or you need to feed this real-time sensor through the Riemann sum integral integration.
- Add rounding to usage today sensor
- Additional debug logging for investigating issues

## [0.0.11] - 2021-12-15

### Fixed

- Tick `pyduke-energy` version to 0.0.15 to fix an issue where the usage measurement was extremely high (fixes #50)

## [0.0.10] - 2021-09-21

### Fixed

- Fix bug where we keep checking other meters when we have already found a matching one (fixes #18)

## [0.0.9] - 2021-09-08

### Fixed

- Handle API failures on invalid meters (fixes #16)

## [0.0.8] - 2021-09-01

### Added

- More logging when the usage API call fails

### Fixed

- Changed the sensor state class from `measurement` to `total_increasing` as per changes in HA 2021.9 (see #11)

## [0.0.7] - 2021-08-23

### Added

- Added some more logging into the smart meter auto-identification flow

### Fixed

- Fixed issue with detecting smart meter when accounts have a `bpNumber` (fixes #10)

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

[unreleased]: https://github.com//mjmeli/ha-duke-energy-gateway/compare/0.0.11...HEAD
[0.0.11]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.11
[0.0.10]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.10
[0.0.9]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.9
[0.0.8]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.8
[0.0.7]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.7
[0.0.6]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.6
[0.0.5]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.5
[0.0.4]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.4
[0.0.3]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.3
[0.0.2]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.2
[0.0.1]: https://github.com/mjmeli/ha-duke-energy-gateway/releases/tag/0.0.1
