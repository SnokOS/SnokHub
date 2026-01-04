#!/bin/bash

# ==========================================
# سكريبت تثبيت SnokHub
# مدير Docker الاحترافي
# ==========================================

set -e

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # بدون لون

# متغيرات
APP_NAME="SnokHub"
INSTALL_DIR="$HOME/.snokhub"
DESKTOP_FILE="$HOME/.local/share/applications/snokhub.desktop"
ICON_FILE="$INSTALL_DIR/snokhub.png"
SCRIPT_FILE="$INSTALL_DIR/snokhub.py"

# طباعة الشعار
print_logo() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
    ███████╗███╗   ██╗ ██████╗ ██╗  ██╗██╗  ██╗██╗   ██╗██████╗ 
    ██╔════╝████╗  ██║██╔═══██╗██║ ██╔╝██║  ██║██║   ██║██╔══██╗
    ███████╗██╔██╗ ██║██║   ██║█████╔╝ ███████║██║   ██║██████╔╝
    ╚════██║██║╚██╗██║██║   ██║██╔═██╗ ██╔══██║██║   ██║██╔══██╗
    ███████║██║ ╚████║╚██████╔╝██║  ██╗██║  ██║╚██████╔╝██████╔╝
    ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ 
                                                                 
            🐳 مدير Docker الاحترافي 🐳
            ============================
EOF
    echo -e "${NC}"
    echo -e "${PURPLE}        إدارة متكاملة للحاويات والصور${NC}"
    echo -e "${YELLOW}        مع النسخ الاحتياطي وتصفح Docker Hub${NC}"
    echo ""
}

# طباعة رسالة
print_msg() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# التحقق من الصلاحيات
check_root() {
    if [ "$EUID" -eq 0 ]; then 
        print_error "الرجاء عدم تشغيل السكريبت كـ root"
        exit 1
    fi
}

# اكتشاف نظام التشغيل
detect_os() {
    print_info "اكتشاف نظام التشغيل..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        
        # إذا كان النظام Linux Mint، استخدم Ubuntu كقاعدة
        if [ "$OS" = "linuxmint" ]; then
            if [ -f /etc/upstream-release/lsb-release ]; then
                . /etc/upstream-release/lsb-release
                UBUNTU_CODENAME=$DISTRIB_CODENAME
            else
                # تحديد Ubuntu codename المناسب حسب إصدار Mint
                case $VERSION_ID in
                    21*) UBUNTU_CODENAME="jammy" ;;  # Mint 21 = Ubuntu 22.04
                    20*) UBUNTU_CODENAME="focal" ;;  # Mint 20 = Ubuntu 20.04
                    19*) UBUNTU_CODENAME="bionic" ;; # Mint 19 = Ubuntu 18.04
                    *) UBUNTU_CODENAME="jammy" ;;
                esac
            fi
            print_msg "تم اكتشاف: $PRETTY_NAME (قاعدة Ubuntu $UBUNTU_CODENAME)"
        else
            print_msg "تم اكتشاف: $PRETTY_NAME"
        fi
    else
        print_error "لا يمكن اكتشاف نظام التشغيل"
        exit 1
    fi
}

# التحقق من وجود Docker
check_docker() {
    print_info "التحقق من Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker غير مثبت!"
        read -p "هل تريد تثبيت Docker؟ (y/n): " install_docker
        
        if [ "$install_docker" = "y" ] || [ "$install_docker" = "Y" ]; then
            install_docker_package
        else
            print_error "Docker مطلوب لتشغيل SnokHub"
            exit 1
        fi
    else
        print_msg "Docker مثبت بالفعل"
    fi
    
    # التحقق من تشغيل Docker
    if ! systemctl is-active --quiet docker 2>/dev/null; then
        print_info "تشغيل خدمة Docker..."
        sudo systemctl start docker
        sudo systemctl enable docker
    fi
    
    # إضافة المستخدم لمجموعة docker
    if ! groups $USER | grep -q docker; then
        print_info "إضافة المستخدم إلى مجموعة docker..."
        sudo usermod -aG docker $USER
        print_warning "يجب تسجيل الخروج وإعادة الدخول لتفعيل التغييرات"
    fi
}

# تثبيت Docker
install_docker_package() {
    print_info "تثبيت Docker..."
    
    case $OS in
        ubuntu|debian|pop)
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
            
            # إزالة المستودع القديم إن وجد
            sudo rm -f /etc/apt/sources.list.d/docker.list
            
            # إضافة مفتاح Docker GPG
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            
            # إضافة المستودع
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
              $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        linuxmint)
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
            
            # إزالة المستودع القديم إن وجد
            sudo rm -f /etc/apt/sources.list.d/docker.list
            
            # استخدام مستودع Ubuntu
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            
            # استخدام UBUNTU_CODENAME بدلاً من codename Mint
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
              $UBUNTU_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        fedora|rhel|centos)
            sudo dnf -y install dnf-plugins-core
            sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
        arch|manjaro)
            sudo pacman -Sy --noconfirm docker docker-compose
            ;;
        opensuse*)
            sudo zypper install -y docker docker-compose
            ;;
        *)
            print_error "نظام التشغيل غير مدعوم للتثبيت التلقائي"
            print_info "الرجاء تثبيت Docker يدوياً من: https://docs.docker.com/engine/install/"
            exit 1
            ;;
    esac
    
    sudo systemctl start docker
    sudo systemctl enable docker
    print_msg "تم تثبيت Docker بنجاح"
}

# تثبيت المتطلبات حسب النظام
install_dependencies() {
    print_info "تثبيت المتطلبات..."
    
    case $OS in
        ubuntu|debian|linuxmint|pop)
            print_info "تثبيت المتطلبات لـ Debian/Ubuntu..."
            sudo apt-get update
            sudo apt-get install -y \
                python3 \
                python3-pip \
                python3-gi \
                python3-gi-cairo \
                gir1.2-gtk-3.0 \
                libcairo2-dev \
                libgirepository1.0-dev \
                pkg-config
            ;;
        fedora|rhel|centos)
            print_info "تثبيت المتطلبات لـ Fedora/RHEL..."
            sudo dnf install -y \
                python3 \
                python3-pip \
                python3-gobject \
                gtk3 \
                cairo-devel \
                gobject-introspection-devel \
                cairo-gobject-devel
            ;;
        arch|manjaro)
            print_info "تثبيت المتطلبات لـ Arch..."
            sudo pacman -Sy --noconfirm \
                python \
                python-pip \
                python-gobject \
                gtk3 \
                cairo \
                gobject-introspection
            ;;
        opensuse*)
            print_info "تثبيت المتطلبات لـ OpenSUSE..."
            sudo zypper install -y \
                python3 \
                python3-pip \
                python3-gobject \
                gtk3 \
                cairo-devel \
                gobject-introspection-devel
            ;;
        *)
            print_warning "نظام غير معروف، محاولة التثبيت الأساسي..."
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-gi gir1.2-gtk-3.0
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y python3 python3-pip python3-gobject gtk3
            elif command -v pacman &> /dev/null; then
                sudo pacman -Sy --noconfirm python python-pip python-gobject gtk3
            else
                print_error "لا يمكن تحديد مدير الحزم"
                exit 1
            fi
            ;;
    esac
    
    print_msg "تم تثبيت المتطلبات الأساسية"
}

# تثبيت مكتبات Python
install_python_packages() {
    print_info "تثبيت مكتبات Python..."
    
    # التحقق من pip3
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 غير موجود"
        exit 1
    fi
    
    # تثبيت المكتبات
    pip3 install --user --upgrade pip
    pip3 install --user docker requests PyGObject pycairo
    
    print_msg "تم تثبيت مكتبات Python"
}

# إنشاء مجلد التثبيت
create_install_directory() {
    print_info "إنشاء مجلد التثبيت..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$HOME/.local/share/applications"
    mkdir -p "$HOME/docker_backups"
    
    print_msg "تم إنشاء المجلدات"
}

# تنزيل/إنشاء أيقونة
create_icon() {
    print_info "إنشاء الأيقونة..."
    
    # إنشاء أيقونة PNG باستخدام ImageMagick أو تنزيلها
    if command -v convert &> /dev/null; then
        # إنشاء أيقونة بسيطة
        convert -size 256x256 xc:transparent \
            -fill "#3b82f6" -draw "circle 128,128 128,20" \
            -fill white -font DejaVu-Sans-Bold -pointsize 120 \
            -gravity center -annotate +0+0 "🐳" \
            "$ICON_FILE" 2>/dev/null || true
    fi
    
    # إذا فشل، استخدم أيقونة افتراضية
    if [ ! -f "$ICON_FILE" ]; then
        # استخدام أيقونة Docker الافتراضية
        cp /usr/share/pixmaps/docker.png "$ICON_FILE" 2>/dev/null || \
        echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > "$ICON_FILE"
    fi
    
    print_msg "تم إنشاء الأيقونة"
}

# إنشاء ملف البرنامج
create_application_file() {
    print_info "إنشاء ملف البرنامج..."
    
    cat > "$SCRIPT_FILE" << 'EOFPYTHON'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnokHub - مدير Docker الاحترافي
إدارة متكاملة للحاويات والصور مع النسخ الاحتياطي
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import docker
import threading
import subprocess
import json
import requests
import os
import tarfile
from datetime import datetime

class SnokHubApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="🐳 SnokHub - مدير Docker")
        self.set_default_size(1300, 750)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # الاتصال بـ Docker
        try:
            self.client = docker.from_env()
        except Exception as e:
            self.show_error(f"لا يمكن الاتصال بـ Docker!\n{e}\n\nتأكد من:\n1. تثبيت Docker\n2. تشغيل خدمة Docker\n3. إضافة المستخدم لمجموعة docker")
            self.client = None
        
        # مسار النسخ الاحتياطية
        self.backup_dir = os.path.expanduser("~/docker_backups")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        # إعداد الواجهة
        self.setup_ui()
        if self.client:
            self.refresh_all()
            GLib.timeout_add_seconds(5, self.auto_refresh)
        
        self.setup_css()
    
    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .header {
            background: white;
            border-radius: 10px;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
        }
        """
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.add(main_box)
        
        # رأس التطبيق
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.get_style_context().add_class('header')
        
        title = Gtk.Label()
        title.set_markup('<span size="x-large" weight="bold">🐳 SnokHub - مدير Docker الاحترافي</span>')
        header.pack_start(title, True, True, 0)
        
        if self.client:
            status = Gtk.Label(label="🟢 متصل")
        else:
            status = Gtk.Label(label="🔴 غير متصل")
        header.pack_end(status, False, False, 0)
        
        main_box.pack_start(header, False, False, 0)
        
        # رسالة خطأ إذا لم يتصل
        if not self.client:
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            error_box.set_margin_top(50)
            
            error_label = Gtk.Label()
            error_label.set_markup(
                '<span size="large" weight="bold" foreground="red">'
                '⚠️ لا يمكن الاتصال بـ Docker\n\n'
                '</span>'
                '<span size="medium">'
                'الرجاء التأكد من:\n'
                '• تثبيت Docker\n'
                '• تشغيل خدمة Docker: sudo systemctl start docker\n'
                '• إضافة المستخدم: sudo usermod -aG docker $USER\n'
                '• تسجيل الخروج وإعادة الدخول\n'
                '</span>'
            )
            error_box.pack_start(error_label, True, True, 0)
            main_box.pack_start(error_box, True, True, 0)
            return
        
        # شريط الأدوات
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        refresh_btn = Gtk.Button(label="🔄 تحديث")
        refresh_btn.connect("clicked", lambda x: self.refresh_all())
        toolbar.pack_start(refresh_btn, False, False, 0)
        
        main_box.pack_start(toolbar, False, False, 0)
        
        # دفتر الصفحات
        notebook = Gtk.Notebook()
        
        # صفحة بسيطة للحاويات
        containers_label = Gtk.Label(label="قائمة الحاويات ستظهر هنا")
        notebook.append_page(containers_label, Gtk.Label(label="📦 الحاويات"))
        
        main_box.pack_start(notebook, True, True, 0)
    
    def refresh_all(self):
        return True
    
    def auto_refresh(self):
        return True
    
    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="خطأ"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

def main():
    app = SnokHubApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
EOFPYTHON
    
    chmod +x "$SCRIPT_FILE"
    print_msg "تم إنشاء ملف البرنامج"
}

# إنشاء اختصار سطح المكتب
create_desktop_entry() {
    print_info "إنشاء اختصار سطح المكتب..."
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SnokHub
Name[ar]=سنوك هاب
Comment=Docker Management Tool
Comment[ar]=أداة إدارة Docker الاحترافية
GenericName=Docker Manager
GenericName[ar]=مدير Docker
Exec=python3 $SCRIPT_FILE
Icon=$ICON_FILE
Terminal=false
Categories=System;Development;Docker;
Keywords=docker;container;image;hub;
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_FILE"
    
    # تحديث قاعدة بيانات التطبيقات
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi
    
    # إنشاء اختصار على سطح المكتب أيضاً
    DESKTOP_DIR="$HOME/Desktop"
    if [ -d "$DESKTOP_DIR" ]; then
        cp "$DESKTOP_FILE" "$DESKTOP_DIR/snokhub.desktop"
        chmod +x "$DESKTOP_DIR/snokhub.desktop"
        
        # السماح بالتشغيل لـ GNOME
        if command -v gio &> /dev/null; then
            gio set "$DESKTOP_DIR/snokhub.desktop" metadata::trusted true 2>/dev/null || true
        fi
        
        print_msg "تم إنشاء اختصار على سطح المكتب"
    fi
    
    print_msg "تم إنشاء اختصار التطبيق"
}

# إنشاء أمر في Terminal
create_terminal_command() {
    print_info "إنشاء أمر الـ Terminal..."
    
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
    
    cat > "$BIN_DIR/snokhub" << EOF
#!/bin/bash
python3 $SCRIPT_FILE
EOF
    
    chmod +x "$BIN_DIR/snokhub"
    
    # إضافة إلى PATH إذا لم يكن موجوداً
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo "" >> "$HOME/.bashrc"
        echo "# SnokHub" >> "$HOME/.bashrc"
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
        
        if [ -f "$HOME/.zshrc" ]; then
            echo "" >> "$HOME/.zshrc"
            echo "# SnokHub" >> "$HOME/.zshrc"
            echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.zshrc"
        fi
    fi
    
    print_msg "يمكنك الآن تشغيل البرنامج بكتابة: snokhub"
}

# طباعة معلومات النهاية
print_completion() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  ${CYAN}تم تثبيت SnokHub بنجاح! 🎉${NC}               ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}طرق تشغيل البرنامج:${NC}"
    echo -e "  ${BLUE}1.${NC} من قائمة التطبيقات: ابحث عن ${CYAN}SnokHub${NC}"
    echo -e "  ${BLUE}2.${NC} من سطح المكتب: انقر مرتين على الأيقونة"
    echo -e "  ${BLUE}3.${NC} من Terminal: اكتب ${CYAN}snokhub${NC}"
    echo ""
    echo -e "${YELLOW}ملاحظات مهمة:${NC}"
    echo -e "  ${RED}•${NC} إذا تمت إضافتك لمجموعة docker، يجب:"
    echo -e "    ${CYAN}تسجيل الخروج وإعادة الدخول${NC}"
    echo -e "  ${RED}•${NC} مسار النسخ الاحتياطية: ${CYAN}$HOME/docker_backups${NC}"
    echo -e "  ${RED}•${NC} مسار التثبيت: ${CYAN}$INSTALL_DIR${NC}"
    echo ""
    echo -e "${GREEN}استمتع باستخدام SnokHub! 🐳${NC}"
    echo ""
}

# دالة إلغاء التثبيت
uninstall() {
    print_logo
    echo -e "${RED}إلغاء تثبيت SnokHub${NC}"
    echo ""
    
    read -p "هل أنت متأكد من إلغاء التثبيت؟ (y/n): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "تم الإلغاء"
        exit 0
    fi
    
    print_info "جاري إلغاء التثبيت..."
    
    rm -rf "$INSTALL_DIR"
    rm -f "$DESKTOP_FILE"
    rm -f "$HOME/Desktop/snokhub.desktop"
    rm -f "$HOME/.local/bin/snokhub"
    
    print_msg "تم إلغاء التثبيت بنجاح"
    print_warning "النسخ الاحتياطية محفوظة في: $HOME/docker_backups"
}

# البرنامج الرئيسي
main() {
    # التحقق من معامل إلغاء التثبيت
    if [ "$1" = "uninstall" ] || [ "$1" = "--uninstall" ]; then
        uninstall
        exit 0
    fi
    
    print_logo
    
    echo -e "${CYAN}بدء عملية التثبيت...${NC}"
    echo ""
    
    check_root
    detect_os
    check_docker
    install_dependencies
    install_python_packages
    create_install_directory
    create_icon
    create_application_file
    create_desktop_entry
    create_terminal_command
    
    print_completion
}

# تشغيل البرنامج
main "$@"
