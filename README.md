[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

*Read this in other languages: [English](README.md), [Français](README.fr.md).*

[releases-shield]: https://img.shields.io/github/release/tartempio/iHost-Connect.svg?style=for-the-badge
[releases]: https://github.com/tartempio/iHost-Connect/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/tartempio/iHost-Connect.svg?style=for-the-badge
[commits]: https://github.com/tartempio/iHost-Connect/commits/main
[license-shield]: https://img.shields.io/github/license/tartempio/iHost-Connect.svg?style=for-the-badge
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/custom-components/hacs

# iHost Connect

A **Home Assistant** custom integration for the **SONOFF iHost** smart home gateway (eWeLink CUBE).

Monitor your iHost gateway directly from Home Assistant: CPU temperature, RAM usage, SD card usage, connected device count, security mode, and more. The integration communicates **locally** with your iHost — no cloud required.

_Please ⭐ this repo if you find it useful!_

---

## Features

- **Local polling** — all communication happens directly on your local network
- **Auto-discovery** — the iHost is automatically detected via Zeroconf (mDNS)
- **Sensors** — extensive runtime monitoring of your gateway
- **Binary sensor** — automatic firmware update detection (checks the [CUBE-OS GitHub releases](https://github.com/eWeLinkCUBE/CUBE-OS/releases))
- **Button** — reboot your iHost gateway from Home Assistant

### What this integration does NOT do

> **Note:** This integration is designed exclusively to **monitor the state of the iHost gateway itself**. It does **NOT** expose the individual smart home devices connected to your iHost (such as Zigbee sensors, switches, etc.), nor does it allow you to control them. To integrate and control your iHost devices in Home Assistant, we highly recommend using the **Matter Bridge** feature built into the iHost.

### Provided entities

#### Sensors

| Entity | Type | Description |
|---|---|---|
| Devices Count | Sensor | Number of devices connected to the iHost |
| Security Mode | Sensor | Active security mode (e.g. Home, Away, Disarmed) |

#### Diagnostic

| Entity | Type | Description |
|---|---|---|
| Last Boot | Sensor | Timestamp of the last gateway boot |
| CPU Temperature | Sensor | CPU temperature (°C) |
| CPU Usage | Sensor | CPU usage (%) |
| RAM Usage | Sensor | RAM usage (%) |
| SD Card Usage | Sensor | SD card usage (%) |
| IP Address | Sensor | Current IP address of the iHost |
| Firmware Update | Binary Sensor | `On` when a newer CUBE-OS firmware is available |

#### Configuration

| Entity | Type | Description |
|---|---|---|
| Reboot | Button | Send a reboot command to the iHost |

---

## Prerequisites

- A [SONOFF iHost](https://itead.cc/product/sonoff-ihost-smart-home-hub/) gateway running **CUBE-OS**
- The iHost must be **on the same local network** as your Home Assistant instance
- [HACS](https://hacs.xyz/) installed in Home Assistant

---

## Installation

### Via HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tartempio&repository=iHost-Connect&category=Integration)

Or manually:

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click the **⋮** menu (top right) → **Custom repositories**
4. Add `https://github.com/tartempio/iHost-Connect` with category **Integration**
5. Search for **iHost** and click **Download**
6. **Restart Home Assistant**

### Manual installation

<details>
<summary>Expand for details</summary>

1. Download the latest release from the [Releases page](https://github.com/tartempio/iHost-Connect/releases)
2. Copy the `custom_components/ihost` folder into your Home Assistant `config/custom_components/` directory
3. **Restart Home Assistant**

</details>

---

## Configuration

### Auto-discovery (recommended)

If your iHost is on the same network as Home Assistant, it will be **automatically discovered** via Zeroconf (mDNS). A notification will appear in the Home Assistant UI asking you to confirm the setup.

1. Go to **Settings → Integrations**
2. A discovered **iHost** entry will appear — click **Configure**
3. Follow the steps below to authorise the connection

### Manual setup

1. Go to **Settings → Integrations**
2. Click **+ Add Integration** and search for **iHost**
3. Enter the **IP address** of your iHost gateway

### Authorising the connection

After entering the IP address (or confirming auto-discovery), the integration will ask you to **approve the connection on the iHost web interface**:

1. Open your iHost web interface at `http://<ihost-ip>` in a browser
2. Initiate the token request from Home Assistant iHost integration
3. **Approve** the connection request — a button will appear to authorise the `HomeAssistant` application
4. Go back to Home Assistant and click **Submit** — the token will be retrieved automatically

> **Note:** You have approximately 60 seconds to approve the request on the iHost side before the connection times out.

---

## Data refresh

Sensor data is polled **every 60 seconds**. Firmware update availability is checked **every 6 hours** against the [CUBE-OS GitHub releases](https://github.com/eWeLinkCUBE/CUBE-OS/releases).

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Integration not discovered | Make sure your iHost is on the same subnet as Home Assistant and that mDNS traffic is allowed |
| Cannot connect | Verify the IP address is correct and that your iHost is reachable |
| Token not obtained | Make sure you approved the connection in the iHost web interface within the time limit |
| Sensors show `unavailable` | Check your Home Assistant logs for connection errors; restart the integration |

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

This integration uses the [eWeLink CUBE Open API](https://ewelink.cc/ewelink-cube/introduce-open-api/document).

---

## License

This project is licensed under the [MIT License](LICENSE).

DISCLAIMER: This project is an independent, community-developed Home Assistant
integration. The author is not affiliated with, endorsed by, or in any way
associated with eWeLink, eWeLink Cube, iHost, or Sonoff (ITEAD Intelligent
Systems Co., Ltd.). All product names, trademarks, and registered trademarks
are the property of their respective owners.
