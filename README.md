# Area Label Stat

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)  
[![Stable](https://img.shields.io/github/v/release/819548945/area_label_stat)](https://github.com/819548945/area_label_stat/releases/latest)

English | [简体中文](README_CN.md)

<img width="256" height="256" alt="icon" src="https://github.com/819548945/area_label_stat/blob/main/icon/icon.png?raw=true" />

A custom integration for Home Assistant that counts how many entities **with a given label** are in a **specific state** inside a chosen **area**.  
- Support for **multiple labels** in a single counter  
- Support for **filtering by any entity state**

---

## 1. Installation

Pick **one** of the methods below.

### Method 1 – HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/docs/setup/download) is already installed in Home Assistant.  
2. Open HACS → “Custom repositories” → paste  
   `https://github.com/819548945/area_label_stat` and choose category **Integration**.  
3. **Restart Home Assistant**.

### Method 2 – Manual

1. Download [`area_label_stat.zip`](https://github.com/819548945/area_label_stat/releases/latest).  
2. Extract it into `/config/custom_components/area_label_stat`.  
3. **Restart Home Assistant**.

After the restart, go to  
**Settings → Devices & Services → Integrations → “Area Label Stat”** and complete the configuration.  
All devices will be added automatically.

---

## Usage

1. Assign **labels** to the entities you want to track.  
2. Make sure those entities belong to a **Home-Assistant area**.  
3. Add the **Area Label Stat** integration and configure:  
   - area(s)  
   - label(s)  
   - state(s) to count  

---

## Screenshots

| Dashboard card examples |
|-------------------------|
| <img width="500" alt="card1" src="https://github.com/user-attachments/assets/99d5d895-d579-4ace-9062-c86e73b698dc" /> |
| <img width="500" alt="card2" src="https://github.com/user-attachments/assets/64551085-5b45-4df0-8acd-ab8486d76a51" /> |
| <img width="500" alt="card3" src="https://github.com/user-attachments/assets/90c8d08c-e0a8-4f69-af1f-99cba6ab1a5c" /> |
