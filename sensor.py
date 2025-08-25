from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import EntityCategory
from homeassistant.helpers.event import Event
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    async_get as async_get_entity_registry,
)
from homeassistant.helpers.label_registry import (
    async_get as labelreg_async_get,
    LabelEntry,
)
from homeassistant.helpers.area_registry import (
    async_get as areareg_async_get,
    AreaEntry,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.device_registry import (
    DeviceRegistry,
    DeviceEntry,
    DeviceInfo,
    async_get as async_get_device_registry,
)
from .const import DOMAIN
from homeassistant.components.sensor import SensorEntity, SensorStateClass
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a config entry."""
    _LOGGER.debug("sensor.py async_setup_entry")
    areas = areareg_async_get(hass).areas

    labels = labelreg_async_get(hass).labels
    device_registry = async_get_device_registry(hass)
    sensor_configs = []
    for area in config_entry.data["area"]:
        deviceEntry = device_registry.async_get_device(
            identifiers={(DOMAIN, config_entry.entry_id + "_" + area)}
        )
        if config_entry.data["mergeLabelStat"]:
            sensor_configs.append(
                LichSensorEntity(
                    hass,
                    deviceEntry,
                    [
                        labels[entity]
                        for entity in config_entry.data["label"]
                        if entity in labels
                    ],
                    None if area == "all" else areas[area],
                )
            )
        else:
            for lable in config_entry.data["label"]:
                sensor_configs.append(
                    LichSensorEntity(
                        hass,
                        deviceEntry,
                        [labels[lable]],
                        None if area == "all" else areas[area],
                    )
                )
    async_add_entities(sensor_configs)
    _LOGGER.info(sensor_configs)


class LichSensorEntity(SensorEntity):
    """Set up a Sensor entry."""

    _LOGGER.info("sensor py async_setup_entry")

    def __init__(
        self,
        hass: HomeAssistant,
        deviceEntry: DeviceEntry,
        labels: list[LabelEntry],
        area: AreaEntry = None,
    ):
        self._target_entity_ids = []
        _LOGGER.debug("--------get entity start-------")
        sensor_name = ""
        sensor_unique_id = deviceEntry.id
        entity_ids = []
        entity_registry: EntityRegistry = async_get_entity_registry(hass)
        lable_entity_ids = []
        for lable in labels:
            sensor_name += "," + lable.name
            sensor_unique_id += "_" + lable.label_id
            lable_entity_ids.extend(
                [
                    entity.entity_id
                    for entity in entity_registry.entities.values()
                    if lable.label_id in entity.labels
                ]
            )
        sensor_name = sensor_name[1:]
        _LOGGER.debug(sensor_unique_id)
        _LOGGER.debug(lable_entity_ids)
        _LOGGER.info(area)
        if area != None:
            device_registry: DeviceRegistry = async_get_device_registry(hass)
            area_device_ids = [
                device.id
                for device in device_registry.devices.values()
                if device.area_id == area.id
            ]
            area_entity_ids = [
                entity.entity_id
                for entity in entity_registry.entities.values()
                if entity.device_id in area_device_ids
            ]
            _LOGGER.debug(area_entity_ids)
            entity_ids = list(set(area_entity_ids) & set(lable_entity_ids))
        else:
            entity_ids = lable_entity_ids
        _LOGGER.debug(entity_ids)
        _LOGGER.debug("---------get entity end-----------")

        self._device_id = deviceEntry.id
        self._attr_unique_id = sensor_unique_id
        self._attr_name = "标签:" + sensor_name
        self._attr_icon = "mdi:chart-areaspline-variant"
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_native_value = len(entity_ids)
        self._attr_extra_state_attributes = {"entity_ids": entity_ids}
        self._attr_device_info = DeviceInfo(identifiers=deviceEntry.identifiers)

    async def async_added_to_hass(self) -> None:
        # 实体被添加到系统时调用，设置状态监听.
        await super().async_added_to_hass()
        # 监听目标实体的状态变化
        self._unsub_state_change = async_track_state_change_event(
            self.hass,
            self._attr_extra_state_attributes["entity_ids"],
            self._async_on_target_state_change,  # 状态变化时的回调函数
        )

        # 初始化时获取一次当前状态
        await self._async_update_from_targets()

    async def async_will_remove_from_hass(self) -> None:
        # 实体被移除时调用，清理监听
        await super().async_will_remove_from_hass()
        if self._unsub_state_change:
            self._unsub_state_change()  # 取消监听

    async def _async_on_target_state_change(self, event: Event) -> None:
        # 目标实体状态变化时的回调
        await self._async_update_from_targets()
        self.async_write_ha_state()  # 通知HA更新状态

    async def _async_update_from_targets(self) -> None:
        # 获取所有目标实体的状态
        states = {}
        states_entity_id: dict[str, list] = {}
        for entity_id in self._attr_extra_state_attributes["entity_ids"]:
            state_obj = self.hass.states.get(entity_id)
            if hasattr(states, state_obj.state):
                states[state_obj.state] = states[state_obj.state] + 1
            else:
                states[state_obj.state] = 1
                states_entity_id[state_obj.state + "_entity_ids"] = []
            states_entity_id[state_obj.state + "_entity_ids"].append(entity_id)
        _LOGGER.debug(states)
        _LOGGER.debug(states_entity_id)
        attributes = states | states_entity_id
        attributes["entity_ids"] = self._attr_extra_state_attributes["entity_ids"]
        self._attr_extra_state_attributes = attributes
