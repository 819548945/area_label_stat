from homeassistant import config_entries
from .const import DOMAIN
from typing import Optional, Any
from homeassistant.helpers.area_registry import async_get as areareg_async_get
from homeassistant.helpers.label_registry import async_get as labelreg_async_get
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)


def _getAreas(self):
    areas = {
        area_id: area.name
        for area_id, area in areareg_async_get(self.hass).areas.items()
    }
    areas["all"] = "全部区域"
    return areas


def _getLabels(self):
    return {
        label_id: label.name
        for label_id, label in labelreg_async_get(self.hass).labels.items()
    }


def _getTitle1(self, user_input, areas, labels):
    areaStr = ""
    if "all" in user_input["area"]:
        areaStr = areas["all"]
    else:
        for area in user_input["area"]:
            areaStr += "," + areas[area]
        areaStr = areaStr[1:]
    title = user_input.get("title", "")
    if title != "":
        return title
    labelStr = ""
    for label in user_input["label"]:
        labelStr += "," + labels[label]
    labelStr = labelStr[1:]
    return (
        "区域:"
        + areaStr
        + " 标签:"
        + labelStr
        + " 模式:"
        + ("合并" if user_input["mergeLabelStat"] else "分离")
    )


def _getUserFrom1(self, areas, labels, data):
    schema = vol.Schema({})

    return schema.extend(
        {
            vol.Optional("title", default=data.get("title", "") if data else ""): str,
            vol.Required("area", default=data["area"] if data else []): vol.All(
                cv.multi_select(areas), vol.Length(min=1, msg="至少选择一个选项")
            ),
            vol.Optional("label", default=data["label"] if data else []): vol.All(
                cv.multi_select(labels), vol.Length(min=1, msg="至少选择一个选项")
            ),
            vol.Optional(
                "mergeLabelStat", default=data["mergeLabelStat"] if data else False
            ): bool,
            vol.Required(
                "stateStat", default=data["stateStat"] if data else "on"
            ): vol.In(
                {
                    "on": "on",
                    "off": "off",
                    "count": "count",
                    "unavailable": "unavailable",
                }
            ),
        },
    )


class AreaLabelStatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """area label stat ConfigFlow."""

    async def async_step_user(self, user_input: Optional[dict] = None):
        """Set config flow."""

        areas = _getAreas(self)
        labels = _getLabels(self)
        if user_input is not None:
            return self.async_create_entry(
                title=_getTitle1(self, user_input, areas, labels),
                data=user_input,
            )
        return self.async_show_form(
            step_id="user",
            data_schema=_getUserFrom1(self, areas, labels, None),
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        old_configure_entry = self._get_reconfigure_entry()
        areas = _getAreas(self)
        labels = _getLabels(self)
        if user_input is not None:
            return self.async_update_reload_and_abort(
                title=_getTitle1(self, user_input, areas, labels),
                entry=old_configure_entry,
                data_updates=user_input,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_getUserFrom1(self, areas, labels, old_configure_entry.data),
        )
