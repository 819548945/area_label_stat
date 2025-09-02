from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import EntityCategory
from homeassistant.helpers.event import Event
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    async_get as async_get_entity_registry,
)
from homeassistant.helpers.entity import generate_entity_id
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
from .const import DOMAIN, MANUFACTURER
from homeassistant.components.sensor import SensorEntity, SensorStateClass
import logging


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a config entry."""
    areas = areareg_async_get(hass).areas

    labels = labelreg_async_get(hass).labels
    device_registry = async_get_device_registry(hass)
    sensor_configs = []
    for area in config_entry.data["area"]:
        deviceEntry = device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, config_entry.entry_id + "_" + area)},
            manufacturer=MANUFACTURER,
            name="区域:" + ("全部区域" if area == "all" else areas[area].name),
            suggested_area=None if area == "all" else areas[area].name,
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
                    config_entry.data["mergeLabelStat"],
                    config_entry.data["stateStat"],
                    None if area == "all" else areas[area],
                )
            )
        else:
            for lable in config_entry.data["label"]:
                sensor_configs.append(  # noqa: PERF401
                    LichSensorEntity(
                        hass,
                        deviceEntry,
                        [labels[lable]],
                        config_entry.data["mergeLabelStat"],
                        config_entry.data["stateStat"],
                        None if area == "all" else areas[area],
                    )
                )

    async_add_entities(sensor_configs)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:  # noqa: D103
    _LOGGER.debug("async_unload_entrys")
    return True


class LichSensorEntity(SensorEntity):
    """Set up a Sensor entry."""

    _LOGGER.debug("sensor py async_setup_entry")

    def __init__(
        self,
        hass: HomeAssistant,
        deviceEntry: DeviceEntry,
        labels: list[LabelEntry],
        mergeLabelStat: bool,
        stateStat: str,
        area: AreaEntry = None,
    ) -> None:
        """根据参数生成实体."""
        self._hass = hass
        self.stateStat = stateStat
        self._target_entity_ids = []
        _LOGGER.debug("--------get entity start-------")
        sensor_name = ""
        sensor_unique_id = deviceEntry.id + "_"
        entity_ids = []
        entity_registry: EntityRegistry = async_get_entity_registry(hass)
        lable_entity_ids = set()

        if mergeLabelStat:
            sensor_unique_id += "SUM"
        else:
            sensor_unique_id += labels[0].name
        for lable in labels:
            sensor_name += "," + lable.name
            lable_entity_id = {
                entity.entity_id
                for entity in entity_registry.entities.values()
                if lable.label_id in entity.labels
            }
            lable_entity_ids.update(lable_entity_id)

        sensor_name = sensor_name[1:]
        if area is not None:
            device_registry: DeviceRegistry = async_get_device_registry(hass)
            area_device_ids = {
                device.id
                for device in device_registry.devices.values()
                if device.area_id == area.id
            }
            area_entity_ids = {
                entity.entity_id
                for entity in entity_registry.entities.values()
                if entity.device_id in area_device_ids
            }
            ##直接在实体上配置的区域
            area_entity_ids1 = {
                entity.entity_id
                for entity in entity_registry.entities.values()
                if entity.area_id == area.id
                and (entity.labels & {lable.label_id for lable in labels})
            }
            entity_ids = list((area_entity_ids & lable_entity_ids) | area_entity_ids1)
        else:
            ##直接在实体上配置的区域
            area_entity_ids1 = {
                entity.entity_id
                for entity in entity_registry.entities.values()
                if (entity.labels & {lable.label_id for lable in labels})
            }
            entity_ids = list(lable_entity_ids | area_entity_ids1)
        _LOGGER.debug(f"entity_ids:{entity_ids}")  # noqa: G004
        _LOGGER.debug("---------get entity end-----------")
        self.entity_id = "sensor." + sensor_unique_id
        self._entity_key = sensor_unique_id
        self._attr_unique_id = sensor_unique_id
        self._attr_name = "标签:" + sensor_name
        self._attr_icon = "mdi:chart-areaspline-variant"
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_native_value = None
        self._attr_extra_state_attributes = {"entity_ids": entity_ids}
        self._attr_device_info = DeviceInfo(identifiers=deviceEntry.identifiers)
        self._unsub_state_change = None

    async def async_added_to_hass(self) -> None:
        """实体被添加到系统时调用，设置状态监听."""
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
        """实体被移除时调用，清理监听."""
        await super().async_will_remove_from_hass()
        if self._unsub_state_change:
            self._unsub_state_change()  # 取消监听

    async def _async_on_target_state_change(self, event: Event) -> None:
        # 目标实体状态变化时的回调
        await self._async_update_from_targets()
        self.async_write_ha_state()  # 通知HA更新状态

    async def _async_update_from_targets(self) -> None:
        # 获取所有目标实体的状态
        states = {"on": 0, "off": 0, "unavailable": 0}
        states_entity_id: dict[str, list] = {
            "on_entity_ids": [],
            "off_entity_ids": [],
            "unavailable_entity_ids": [],
            "unload_entity_ids": [],
        }
        for entity_id in self._attr_extra_state_attributes["entity_ids"]:
            _LOGGER.debug(f"update entity_id:{entity_id}")  # noqa: G004
            state_obj = self.hass.states.get(entity_id)
            _LOGGER.debug(f"update entity_id_state_obj:{state_obj}")  # noqa: G004
            if not state_obj:
                states_entity_id["unload_entity_ids"].append(entity_id)
            else:
                if state_obj.state in states:
                    states[state_obj.state] = states[state_obj.state] + 1
                else:
                    states[state_obj.state] = 1
                    states_entity_id[state_obj.state + "_entity_ids"] = []
                states_entity_id[state_obj.state + "_entity_ids"].append(entity_id)
                _LOGGER.debug(f"new states:{states}")  # noqa: G004
        count = len(self._attr_extra_state_attributes["entity_ids"])
        if self.stateStat == "count":
            self._attr_native_value = count
        else:
            self._attr_native_value = states[self.stateStat]
        attributes = states | states_entity_id
        attributes["count"] = count
        attributes["entity_ids"] = self._attr_extra_state_attributes["entity_ids"]
        self._attr_extra_state_attributes = attributes
