
# SnokHub - Docker Manager 🐳

![SnokHub Logo](snokhub_logo.png)

**SnokHub** is a comprehensive, modern, and user-friendly Docker management tool built with Python and GTK3. It provides a sleek interface to manage your Docker containers, images, volumes, and networks with ease.

## ✨ Features

- **📊 Dashboard & Stats**: Real-time overview of your Docker environment (containers, images, volumes, CPU/Memory usage).
- **📦 Container Management**: Start, stop, restart, delete, and view logs of containers.
- **🖼️ Image Management**: View, delete, and backup Docker images.
- **💾 Backup System**: Quick backup of images and export of container configurations.
- **🔍 Docker Hub Search**: Search for and view details of official and community images on Docker Hub.
- **🌐 Multi-Language Support**: Fully localized in **English**, **French (Français)**, and **Arabic (العربية)** with RTL support.
- **🎨 Modern UI**: Beautiful interface with **Dark/Light** themes and **Nova Round** font.
- **🔄 Auto-Update**: Built-in feature to update the application directly from GitHub.

## 🚀 Installation

### Prerequisites

Ensure you have Python 3 and Docker installed and running on your system.

```bash
# Install system dependencies (Debian/Ubuntu)
sudo apt install python3-gi python3-full python3-pip libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
```

### Install Python Libraries

```bash
pip3 install docker requests pycairo PyGObject
```

## 🛠️ Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SnokOS/SnokHub.git
   cd SnokHub
   ```

2. **Run the application:**
   ```bash
   python3 docker_manager.py
   ```

> **Note:** Ensure your user has permission to access the Docker daemon (usually by adding your user to the `docker` group).

## 🌍 Localization

SnokHub automatically detects your language preference but can be switched manually:
- 🇺🇸 **English**
- 🇫🇷 **Français**
- 🇸🇦 **العربية**

## 👨‍💻 Developer Info

- **Company**: [SnokOS](https://snokos.github.io/SnokOS/)
- **Developer**: Mahrez Ben Mohammed
- **Contact**: +216 26 360 802
- **License**: MIT

---
*Built with ❤️ by SnokOS Team*
