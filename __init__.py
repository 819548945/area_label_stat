"""The aaa integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import device_registry as dr

import logging
from .const import SUPPORTED_DOMAINS, VERSION, MANUFACTURER, DOMAIN

PLATFORM_SCHEMA = {}
_LOGGER = logging.getLogger(__name__)


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # """Set up aaa from a config entry."""
    device_registry = dr.async_get(hass)

    _LOGGER.info("async_setup_entry")

    areas = entry.data["areas"]
    for area in entry.data["area"]:
        de = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, entry.entry_id + "_" + area)},
            manufacturer=MANUFACTURER,
            name="区域:" + areas[area],
            suggested_area=None if area == "all" else area,
        )
        #  _LOGGER.info(de.id)
        hass.config_entries.async_update_entry(entry, data=entry.data)
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)
    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_DOMAINS)
    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # """Unload a config entry."""
    _LOGGER.info("async_unload_entry")
    # entry.get

    #  return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    _LOGGER.info("async_setup")
    return True
