from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import device_registry as dr, entity_registry as er
import logging
from .const import SUPPORTED_DOMAINS
import asyncio

PLATFORM_SCHEMA = {}
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up area_label_stat from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_DOMAINS)
    return True


async def async_unload_entry(hass: HomeAssistant, configEntry: ConfigEntry) -> bool:
    """Unload area_label_stat from a config entry."""
    _LOGGER.debug("async_unload_entry")
    entity_registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(
        entity_registry, config_entry_id=configEntry.entry_id
    )
    for entity in entities:
        entity_registry.async_remove(entity.entity_id)
        hass.states.async_remove(entity.entity_id)
    device_registry = dr.async_get(hass)
    entities = dr.async_entries_for_config_entry(
        device_registry, config_entry_id=configEntry.entry_id
    )
    for entity in entities:
        device_registry.async_remove_device(entity.id)
    await hass.config_entries.async_unload_platforms(configEntry, SUPPORTED_DOMAINS)
    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up area_label_stat from a config entry."""
    _LOGGER.debug("area_label_stat async_setup wait")
    await asyncio.sleep(20)
    _LOGGER.debug("area_label_stat async_setup wait ends")
    return True
