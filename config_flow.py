from homeassistant import config_entries
from .const import DOMAIN
from typing import Optional
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.area_registry import async_get as areareg_async_get
from homeassistant.helpers.label_registry import async_get as labelreg_async_get
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv


_LOGGER = logging.getLogger(__name__)


class AreaLabelStatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """area label stat ConfigFlow."""

    async def async_step_user(self, user_input: Optional[dict] = None):
        """Set config flow."""
        area_registry = areareg_async_get(self.hass)
        _LOGGER.debug(user_input)
        areas = {area_id: area.name for area_id, area in area_registry.areas.items()}
        areas["all"] = "全部区域"
        label_registry = labelreg_async_get(self.hass)
        labels = {
            label_id: label.name for label_id, label in label_registry.labels.items()
        }
        if user_input is not None:
            areaStr = ""
            if "all" in user_input["area"]:
                areaStr = areas["all"]
            else:
                for area in user_input["area"]:
                    areaStr += "," + areas[area]
                areaStr = areaStr[1:]
            # areaStr = "[" + areaStr + "]"
            labelStr = ""
            for label in user_input["label"]:
                labelStr += "," + labels[label]
            labelStr = labelStr[1:]
            title = (
                "区域:"
                + areaStr
                + " 标签:"
                + labelStr
                + " 模式:"
                + ("合并" if user_input["mergeLabelStat"] else "分离")
            )
            # setting = copy.deepcopy(user_input)
            user_input["labels"] = labels
            user_input["areas"] = areas
            return self.async_create_entry(
                title=title,
                data=user_input,
            )
        schema = vol.Schema({})
        schema = schema.extend(
            {
                vol.Required("area", default=[]): vol.All(
                    cv.multi_select(areas), vol.Length(min=1, msg="至少选择一个选项")
                ),
                vol.Optional("label", default=[]): vol.All(
                    cv.multi_select(labels), vol.Length(min=1, msg="至少选择一个选项")
                ),
                vol.Optional("mergeLabelStat", default=False): bool,
                # vol.Optional("statStateIsOn", default=False): bool,
            },
        )
        return self.async_show_form(step_id="user", data_schema=schema)
