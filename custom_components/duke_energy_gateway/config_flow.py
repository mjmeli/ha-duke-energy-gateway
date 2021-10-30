"""Adds config flow for Duke Energy Gateway."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from pyduke_energy.client import DukeEnergyClient

from .const import CONF_EMAIL
from .const import CONF_PASSWORD
from .const import CONF_REALTIME_INTERVAL
from .const import CONF_REALTIME_INTERVAL_DEFAULT_SEC
from .const import DOMAIN


class DukeEnergyGatewayFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for duke_energy_gateway."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DukeEnergyGatewayOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_EMAIL): str, vol.Required(CONF_PASSWORD): str}
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, email, password):
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = DukeEnergyClient(email, password, session)
            account_list = await client.get_account_list()
            return account_list and len(account_list) > 0
        except Exception:  # pylint: disable=broad-except
            pass
        return False


class DukeEnergyGatewayOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for duke_energy_gateway."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        realtime_interval = self.options.get(
            CONF_REALTIME_INTERVAL, CONF_REALTIME_INTERVAL_DEFAULT_SEC
        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_REALTIME_INTERVAL,
                        default=realtime_interval,
                    ): int,
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        update_interval = self.options.get(
            CONF_REALTIME_INTERVAL, CONF_REALTIME_INTERVAL_DEFAULT_SEC
        )
        if update_interval < 0:
            return self.async_abort(reason="invalid_update_interval_value")
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_EMAIL), data=self.options
        )
