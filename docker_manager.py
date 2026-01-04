#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق إدارة Docker المتقدم لسطح المكتب - Linux
مع تصفح Docker Hub والنسخ الاحتياطي
يتطلب: PyGObject, docker, requests
التثبيت: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
           pip3 install docker requests
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, Pango, GdkPixbuf
import docker
import threading
import subprocess
import json
import requests
import os
import tarfile
from datetime import datetime

# Translation dictionaries
TRANSLATIONS = {
    "en": {
        "app_title": "SnokHub - Docker Manager",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "refresh": "Refresh",
        "new_container": "New Container",
        "quick_backup": "Quick Backup",
        "cleanup": "Cleanup",
        "containers": "Containers",
        "images": "Images",
        "docker_hub": "Docker Hub",
        "backup": "Backup",
        "networks": "Networks",
        "volumes": "Volumes",
        "stats": "Statistics",
        "no_containers": "No containers",
        "no_images": "No images",
        "no_volumes": "No volumes",
        "image": "Image",
        "stop": "Stop",
        "restart": "Restart",
        "start": "Start",
        "logs": "Logs",
        "delete": "Delete",
        "size": "Size",
        "search": "Search",
        "popular_images": "Popular Images",
        "download_latest": "Download latest",
        "choose_version": "Choose version",
        "backup_info": "Backup Information",
        "backup_path": "Backup path",
        "backup_all_images": "Backup all images",
        "export_containers": "Export containers",
        "open_backup_folder": "Open backup folder",
        "available_backups": "Available backups",
        "total_containers": "Total Containers",
        "running": "Running",
        "total_images": "Total Images",
        "docker_version": "Docker version",
        "os": "Operating System",
        "architecture": "Architecture",
        "cpus": "CPUs",
        "total_memory": "Total Memory",
        "error": "Error",
        "success": "Success",
        "cancel": "Cancel",
        "close": "Close",
        "yes": "Yes",
        "no": "No",
        "no_images_backup": "No images to backup!",
        "no_containers_export": "No containers to export!",
        "no_backups": "No backups found",
        "no_results": "No results found",
        "no_description": "No description",
        "official": "Official",
        "search_error": "Search failed",
        "export_error": "Export failed",
        "backup_success_msg": "Backup created for {count} images!",
        "export_success_msg": "Exported {count} containers to:\n{path}",
        "about": "About",
        "update_app": "Update App",
        "developer": "Developer",
        "company": "Company",
        "phone": "Phone",
        "website": "Website",
        "update_success": "Update successful! Please restart the application.",
        "update_failed": "Update failed",
        "checking_updates": "Checking for updates...",
        "no_updates": "You have the latest version.",
        "update_confirm": "New version available. Update now?",
    },
    "fr": {
        "app_title": "SnokHub - Gestionnaire Docker",
        "connected": "Connecté",
        "disconnected": "Déconnecté",
        "refresh": "Actualiser",
        "new_container": "Nouveau conteneur",
        "quick_backup": "Sauvegarde rapide",
        "cleanup": "Nettoyer",
        "containers": "Conteneurs",
        "images": "Images",
        "docker_hub": "Docker Hub",
        "backup": "Sauvegarde",
        "networks": "Réseaux",
        "volumes": "Volumes",
        "stats": "Statistiques",
        "no_containers": "Aucun conteneur",
        "no_images": "Aucune image",
        "no_volumes": "Aucun volume",
        "image": "Image",
        "stop": "Arrêter",
        "restart": "Redémarrer",
        "start": "Démarrer",
        "logs": "Journaux",
        "delete": "Supprimer",
        "size": "Taille",
        "search": "Rechercher",
        "popular_images": "Images populaires",
        "download_latest": "Télécharger latest",
        "choose_version": "Choisir version",
        "backup_info": "Informations de sauvegarde",
        "backup_path": "Chemin de sauvegarde",
        "backup_all_images": "Sauvegarder toutes les images",
        "export_containers": "Exporter les conteneurs",
        "open_backup_folder": "Ouvrir dossier de sauvegarde",
        "available_backups": "Sauvegardes disponibles",
        "total_containers": "Total des conteneurs",
        "running": "En cours",
        "total_images": "Total des images",
        "docker_version": "Version Docker",
        "os": "Système d'exploitation",
        "architecture": "Architecture",
        "cpus": "CPUs",
        "total_memory": "Mémoire totale",
        "error": "Erreur",
        "success": "Succès",
        "cancel": "Annuler",
        "close": "Fermer",
        "yes": "Oui",
        "no": "Non",
        "no_images_backup": "Aucune image à sauvegarder!",
        "no_containers_export": "Aucun conteneur à exporter!",
        "no_backups": "Aucune sauvegarde trouvée",
        "no_results": "Aucun résultat trouvé",
        "no_description": "Pas de description",
        "official": "Officiel",
        "search_error": "Échec de la recherche",
        "export_error": "Échec de l'exportation",
        "backup_success_msg": "Sauvegarde créée pour {count} images!",
        "export_success_msg": "{count} conteneurs exportés vers:\n{path}",
        "about": "À propos",
        "update_app": "Mettre à jour",
        "developer": "Développeur",
        "company": "Société",
        "phone": "Téléphone",
        "website": "Site Web",
        "update_success": "Mise à jour réussie! Veuillez redémarrer l'application.",
        "update_failed": "Échec de la mise à jour",
        "checking_updates": "Recherche de mises à jour...",
        "no_updates": "Vous avez la dernière version.",
        "update_confirm": "Nouvelle version disponible. Mettre à jour maintenant?",
        "docker_not_running": "Impossible de se connecter à Docker. Assurez-vous qu'il fonctionne!",
        "feature_in_development": "Cette fonctionnalité est en développement",
        "cleanup_confirm": "Voulez-vous nettoyer les ressources inutilisées?\n(Conteneurs arrêtés, images inutilisées, réseaux, volumes)",
        "cleanup_success": "Nettoyage réussi!",
        "delete_container_confirm": "Voulez-vous supprimer le conteneur",
        "delete_image_confirm": "Voulez-vous supprimer l'image",
        "container_deleted": "Conteneur supprimé",
        "image_deleted": "Image supprimée",
        "enter_version": "Entrez la version (Tag):",
        "example": "Exemple",
        "download": "Télécharger",
        "theme": "Thème",
        "language": "Langue",
    },
    "ar": {
        "app_title": "SnokHub - مدير Docker",
        "connected": "متصل",
        "disconnected": "غير متصل",
        "refresh": "تحديث",
        "new_container": "حاوية جديدة",
        "quick_backup": "نسخ احتياطي سريع",
        "cleanup": "تنظيف",
        "containers": "الحاويات",
        "images": "الصور",
        "docker_hub": "Docker Hub",
        "backup": "النسخ الاحتياطي",
        "networks": "الشبكات",
        "volumes": "الأحجام",
        "stats": "الإحصائيات",
        "no_containers": "لا توجد حاويات",
        "no_images": "لا توجد صور",
        "no_volumes": "لا توجد أحجام",
        "image": "الصورة",
        "stop": "إيقاف",
        "restart": "إعادة تشغيل",
        "start": "تشغيل",
        "logs": "السجلات",
        "delete": "حذف",
        "size": "الحجم",
        "search": "بحث",
        "popular_images": "الصور الشائعة",
        "download_latest": "تحميل latest",
        "choose_version": "اختيار إصدار",
        "backup_info": "معلومات النسخ الاحتياطي",
        "backup_path": "مسار النسخ الاحتياطي",
        "backup_all_images": "نسخ احتياطي لجميع الصور",
        "export_containers": "تصدير الحاويات",
        "open_backup_folder": "فتح مجلد النسخ",
        "available_backups": "النسخ الاحتياطية المتوفرة",
        "total_containers": "إجمالي الحاويات",
        "running": "قيد التشغيل",
        "total_images": "إجمالي الصور",
        "docker_version": "إصدار Docker",
        "os": "نظام التشغيل",
        "architecture": "المعمارية",
        "cpus": "المعالجات",
        "total_memory": "الذاكرة الكلية",
        "error": "خطأ",
        "success": "نجاح",
        "cancel": "إلغاء",
        "close": "إغلاق",
        "yes": "نعم",
        "no": "لا",
        "no_images_backup": "لا توجد صور للنسخ الاحتياطي!",
        "no_containers_export": "لا توجد حاويات للتصدير!",
        "no_backups": "لا توجد نسخ احتياطية",
        "no_results": "لا توجد نتائج",
        "no_description": "لا يوجد وصف",
        "official": "رسمي",
        "search_error": "فشل البحث",
        "export_error": "فشل التصدير",
        "backup_success_msg": "تم إنشاء نسخة احتياطية لـ {count} صورة!",
        "export_success_msg": "تم تصدير {count} حاوية إلى:\n{path}",
        "about": "حول",
        "update_app": "تحديث البرنامج",
        "developer": "المطور",
        "company": "الشركة",
        "phone": "الهاتف",
        "website": "الموقع",
        "update_success": "تم التحديث بنجاح! الرجاء إعادة تشغيل البرنامج.",
        "update_failed": "فشل التحديث",
        "checking_updates": "جاري التحقق من التحديثات...",
        "no_updates": "لديك أحدث إصدار.",
        "update_confirm": "توجد نسخة جديدة. هل تريد التحديث الآن؟",
        "docker_not_running": "لا يمكن الاتصال بـ Docker. تأكد من تشغيله!",
        "feature_in_development": "هذه الميزة قيد التطوير",
        "cleanup_confirm": "هل تريد تنظيف الموارد غير المستخدمة؟\n(الحاويات المتوقفة، الصور غير المستخدمة، الشبكات، الأحجام)",
        "cleanup_success": "تم التنظيف بنجاح!",
        "delete_container_confirm": "هل تريد حذف الحاوية",
        "delete_image_confirm": "هل تريد حذف الصورة",
        "container_deleted": "تم حذف الحاوية",
        "image_deleted": "تم حذف الصورة",
        "enter_version": "أدخل الإصدار (Tag):",
        "example": "مثال",
        "download": "تحميل",
        "theme": "السمة",
        "language": "اللغة",
    }
}

class DockerManagerApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="SnokHub - Docker Manager")
        #self.set_default_size(1300, 750)
        self.set_default_size(700, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Configuration
        self.config_dir = os.path.expanduser("~/.config/snokhub")
        self.config_file = os.path.join(self.config_dir, "config.json")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Load configuration (defaults: dark theme, English language)
        self.config = self.load_config()
        self.current_theme = self.config.get("theme", "dark")
        self.current_language = self.config.get("language", "en")
        
        # مسار الشعار
        self.logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snokhub_logo.png")
        
        # الاتصال بـ Docker
        try:
            self.client = docker.from_env()
        except:
            self.client = None
        
        # مسار النسخ الاحتياطية
        self.backup_dir = os.path.expanduser("~/docker_backups")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        # إعداد الواجهة
        self.setup_ui()
        self.refresh_all()
        
        # تحديث تلقائي كل 5 ثواني
        GLib.timeout_add_seconds(5, self.auto_refresh)
        
        # إعداد CSS للتصميم الجميل
        self.setup_css()
    
    def setup_css(self):
        """Setup CSS with theme support"""
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme):
        self.current_theme = theme
        css_provider = Gtk.CssProvider()
        
        # Base CSS with Nova Round font
        base_css = """
        * {
            font-family: 'Nova Round', sans-serif;
        }
        """
        
        if theme == "dark":
            css = base_css + """
            window {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            }
            .header {
                background: #1e293b;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
                color: #f1f5f9;
            }
            .card {
                background: #334155;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                color: #f1f5f9;
            }
            .hub-card {
                background: linear-gradient(135deg, #334155, #475569);
                border-radius: 8px;
                padding: 12px;
                margin: 5px;
                border: 2px solid #64748b;
                color: #f1f5f9;
            }
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            .btn-success {
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
            }
            .btn-danger {
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
            }
            .btn-warning {
                background: linear-gradient(135deg, #f59e0b, #d97706);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
            }
            .status-running {
                background: #10b981;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
            }
            .status-stopped {
                background: #ef4444;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
            }
            label {
                color: #f1f5f9;
            }
            """
        else:  # light theme
            css = b"""
            window {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            }
            .header {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .card {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .hub-card {
                background: linear-gradient(135deg, #f8fafc, #e0e7ff);
                border-radius: 8px;
                padding: 12px;
                margin: 5px;
                border: 2px solid #818cf8;
            }
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            .btn-success {
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
            }
            .btn-danger {
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
            }
            .btn-warning {
                background: linear-gradient(135deg, #f59e0b, #d97706);
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
            }
            .status-running {
                background: #10b981;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
            }
            .status-stopped {
                background: #ef4444;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
            }
            """
        
        css_provider.load_from_data(css.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Save theme preference
        self.save_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"theme": "dark", "language": "en"}
    
    def save_config(self):
        """Save configuration to file"""
        self.config["theme"] = self.current_theme
        self.config["language"] = self.current_language
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def t(self, key):
        """Get translated text for current language"""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS["en"]).get(key, key)
    
    def set_language(self, language):
        """Change application language"""
        self.current_language = language
        self.save_config()
        # Rebuild UI with new language
        for child in self.get_children():
            self.remove(child)
        self.setup_ui()
        self.refresh_all()
        self.show_all()
    
    def setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.add(main_box)
        
        # رأس التطبيق
        header = self.create_header()
        main_box.pack_start(header, False, False, 0)
        
        # شريط الأدوات
        toolbar = self.create_toolbar()
        main_box.pack_start(toolbar, False, False, 0)
        
        # دفتر الصفحات
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        main_box.pack_start(self.notebook, True, True, 0)
        
        # صفحة الحاويات
        containers_page = self.create_containers_page()
        self.notebook.append_page(containers_page, Gtk.Label(label=f"📦 {self.t('containers')}"))
        
        # صفحة الصور
        images_page = self.create_images_page()
        self.notebook.append_page(images_page, Gtk.Label(label=f"💿 {self.t('images')}"))
        
        # صفحة Docker Hub (جديد!)
        hub_page = self.create_hub_page()
        self.notebook.append_page(hub_page, Gtk.Label(label=f"🌐 {self.t('docker_hub')}"))
        
        # صفحة النسخ الاحتياطي (جديد!)
        backup_page = self.create_backup_page()
        self.notebook.append_page(backup_page, Gtk.Label(label=f"💾 {self.t('backups')}"))
        
        # صفحة الشبكات
        networks_page = self.create_networks_page()
        self.notebook.append_page(networks_page, Gtk.Label(label=f"🌐 {self.t('networks')}"))
        
        # صفحة الأحجام
        volumes_page = self.create_volumes_page()
        self.notebook.append_page(volumes_page, Gtk.Label(label=f"💾 {self.t('volumes')}"))
        
        # صفحة الإحصائيات
        stats_page = self.create_stats_page()
        self.notebook.append_page(stats_page, Gtk.Label(label=f"📊 {self.t('stats')}"))
    
    def create_header(self):
        box = dialog.get_content_area()
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_spacing(10)
        
        box.pack_start(Gtk.Label(label="الإصدار (Tag):", xalign=0), False, False, 0)
        
        tag_entry = Gtk.Entry()
        tag_entry.set_text("latest")
        box.pack_start(tag_entry, False, False, 0)
        
        # إصدارات شائعة
        common_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        common_box.pack_start(Gtk.Label(label="شائع:"), False, False, 0)
        
        for tag in ["latest", "stable", "alpine", "slim"]:
            btn = Gtk.Button(label=tag)
            btn.connect("clicked", lambda x, t=tag: tag_entry.set_text(t))
            common_box.pack_start(btn, False, False, 0)
        
        box.pack_start(common_box, False, False, 0)
        
        dialog.add_button("إلغاء", Gtk.ResponseType.CANCEL)
        dialog.add_button("تحميل", Gtk.ResponseType.OK)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            tag = tag_entry.get_text().strip() or "latest"
            self.quick_pull_image(image_name, tag)
        
        dialog.destroy()
    
    def backup_all_images(self):
        """نسخ احتياطي لجميع الصور"""
        if not self.client:
            return
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="جاري إنشاء نسخة احتياطية..."
        )
        
        progress = Gtk.ProgressBar()
        progress.set_show_text(True)
        dialog.get_content_area().pack_start(progress, True, True, 10)
        dialog.show_all()
        
        def backup_thread():
            try:
                images = self.client.images.list()
                total = len(images)
                
                if total == 0:
                    GLib.idle_add(dialog.destroy)
                    GLib.idle_add(self.show_error, self.t("no_images_backup"))
                    return
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_folder = os.path.join(self.backup_dir, f"backup_{timestamp}")
                os.makedirs(backup_folder, exist_ok=True)
                
                for idx, image in enumerate(images):
                    # Update progress
                    percent = (idx + 1) / total
                    GLib.idle_add(progress.set_fraction, percent)
                    GLib.idle_add(progress.set_text, f"{self.t('backup')} {idx+1}/{total}")
                    
                    # Save image
                    tag = image.tags[0] if image.tags else image.short_id
                    safe_name = tag.replace('/', '_').replace(':', '_')
                    filepath = os.path.join(backup_folder, f"{safe_name}.tar")
                    
                    with open(filepath, 'wb') as f:
                        for chunk in image.save():
                            f.write(chunk)
                
                # Save backup info
                info_file = os.path.join(backup_folder, "backup_info.json")
                info = {
                    "timestamp": timestamp,
                    "total_images": total,
                    "images": [{"tags": img.tags, "id": img.short_id} for img in images]
                }
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(info, f, indent=2, ensure_ascii=False)
                
                GLib.idle_add(dialog.destroy)
                success_msg = self.t("backup_success_msg").replace("{count}", str(total))
                GLib.idle_add(self.show_success, success_msg)
                GLib.idle_add(self.refresh_backups)
                
            except Exception as e:
                GLib.idle_add(dialog.destroy)
                GLib.idle_add(self.show_error, f"{self.t('error')}: {e}")
        
        thread = threading.Thread(target=backup_thread)
        thread.daemon = True
        thread.start()
    
    def quick_backup_all(self):
        """Quick backup"""
        self.backup_all_images()
    
    def export_containers(self):
        """Export all containers configurations"""
        if not self.client:
            return
        
        try:
            containers = self.client.containers.list(all=True)
            if not containers:
                self.show_error(self.t("no_containers_export"))
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(self.backup_dir, f"containers_export_{timestamp}.json")
            
            containers_data = []
            for container in containers:
                containers_data.append({
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                    "status": container.status,
                    "ports": container.ports,
                    "environment": container.attrs.get('Config', {}).get('Env', []),
                    "volumes": container.attrs.get('Mounts', []),
                    "command": container.attrs.get('Config', {}).get('Cmd', [])
                })
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(containers_data, f, indent=2, ensure_ascii=False)
            
            success_msg = self.t("export_success_msg").replace("{count}", str(len(containers))).replace("{path}", export_file)
            self.show_success(success_msg)
            self.refresh_backups()
            
        except Exception as e:
            self.show_error(f"{self.t('export_error')}: {e}")
    
    def refresh_backups(self):
        """Refresh backups list"""
        for child in self.backups_box.get_children():
            self.backups_box.remove(child)
        
        try:
            backups = []
            
            # Find backup folders
            for item in os.listdir(self.backup_dir):
                item_path = os.path.join(self.backup_dir, item)
                if os.path.isdir(item_path) and item.startswith('backup_'):
                    info_file = os.path.join(item_path, 'backup_info.json')
                    if os.path.exists(info_file):
                        with open(info_file, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                            info['path'] = item_path
                            info['folder_name'] = item
                            backups.append(info)
                
                # Export files
                elif item.startswith('containers_export_') and item.endswith('.json'):
                    stat = os.stat(item_path)
                    backups.append({
                        "type": "containers",
                        "path": item_path,
                        "filename": item,
                        "timestamp": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "size": stat.st_size
                    })
            
            # Sort by date
            backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            if not backups:
                label = Gtk.Label(label=self.t("no_backups"))
                label.set_margin_top(50)
                self.backups_box.pack_start(label, False, False, 0)
            else:
                for backup in backups:
                    card = self.create_backup_card(backup)
                    self.backups_box.pack_start(card, False, False, 0)
            
            self.backups_box.show_all()
            
        except Exception as e:
            print(f"خطأ في تحديث النسخ الاحتياطية: {e}")
        
        return False
    
    def create_backup_card(self, backup_info):
        """إنشاء بطاقة للنسخة الاحتياطية"""
        frame = Gtk.Frame()
        frame.get_style_context().add_class('card')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        # العنوان
        if backup_info.get('type') == 'containers':
            title = f"📋 تصدير الحاويات - {backup_info['filename']}"
            info_text = f"التاريخ: {backup_info['timestamp']}\nالحجم: {backup_info['size']/1024:.2f} KB"
        else:
            title = f"💾 نسخة احتياطية - {backup_info.get('folder_name', 'N/A')}"
            info_text = f"التاريخ: {backup_info['timestamp']}\nعدد الصور: {backup_info.get('total_images', 0)}"
        
        title_label = Gtk.Label()
        title_label.set_markup(f'<span weight="bold">{title}</span>')
        title_label.set_halign(Gtk.Align.START)
        box.pack_start(title_label, False, False, 0)
        
        info_label = Gtk.Label(label=info_text)
        info_label.set_halign(Gtk.Align.START)
        box.pack_start(info_label, False, False, 0)
        
        # الأزرار
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_margin_top(10)
        
        if backup_info.get('type') != 'containers':
            restore_btn = Gtk.Button(label="♻️ استعادة")
            restore_btn.get_style_context().add_class('btn-success')
            restore_btn.connect("clicked", lambda x: self.restore_backup(backup_info))
            button_box.pack_start(restore_btn, True, True, 0)
        
        open_btn = Gtk.Button(label="📂 فتح")
        open_btn.connect("clicked", lambda x: subprocess.run(['xdg-open', backup_info['path']]))
        button_box.pack_start(open_btn, True, True, 0)
        
        delete_btn = Gtk.Button(label="🗑️ حذف")
        delete_btn.get_style_context().add_class('btn-danger')
        delete_btn.connect("clicked", lambda x: self.delete_backup(backup_info))
        button_box.pack_start(delete_btn, True, True, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        frame.add(box)
        return frame
    
    def restore_backup(self, backup_info):
        """استعادة نسخة احتياطية"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="هل تريد استعادة هذه النسخة الاحتياطية؟"
        )
        dialog.format_secondary_text("سيتم تحميل جميع الصور من النسخة الاحتياطية")
        
        response = dialog.run()
        dialog.destroy()
        
        if response != Gtk.ResponseType.YES:
            return
        
        # نافذة التقدم
        progress_dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="جاري الاستعادة..."
        )
        
        progress = Gtk.ProgressBar()
        progress.set_show_text(True)
        progress_dialog.get_content_area().pack_start(progress, True, True, 10)
        progress_dialog.show_all()
        
        def restore_thread():
            try:
                backup_path = backup_info['path']
                tar_files = [f for f in os.listdir(backup_path) if f.endswith('.tar')]
                total = len(tar_files)
                
                for idx, tar_file in enumerate(tar_files):
                    percent = (idx + 1) / total
                    GLib.idle_add(progress.set_fraction, percent)
                    GLib.idle_add(progress.set_text, f"استعادة {idx+1}/{total}")
                    
                    tar_path = os.path.join(backup_path, tar_file)
                    with open(tar_path, 'rb') as f:
                        self.client.images.load(f.read())
                
                GLib.idle_add(progress_dialog.destroy)
                GLib.idle_add(self.show_success, f"تمت استعادة {total} صورة بنجاح!")
                GLib.idle_add(self.refresh_images)
                
            except Exception as e:
                GLib.idle_add(progress_dialog.destroy)
                GLib.idle_add(self.show_error, f"فشلت الاستعادة: {e}")
        
        thread = threading.Thread(target=restore_thread)
        thread.daemon = True
        thread.start()
    
    def delete_backup(self, backup_info):
        """حذف نسخة احتياطية"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="هل تريد حذف هذه النسخة الاحتياطية؟"
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            try:
                import shutil
                path = backup_info['path']
                
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                
                self.show_success("تم حذف النسخة الاحتياطية")
                self.refresh_backups()
                
            except Exception as e:
                self.show_error(f"فشل الحذف: {e}")
    
    def refresh_all(self):
        if not self.client:
            return False
        
        try:
            self.refresh_containers()
            self.refresh_images()
            self.refresh_networks()
            self.refresh_volumes()
            self.refresh_stats()
        except Exception as e:
            print(f"خطأ في التحديث: {e}")
        
        return True
    
    def refresh_containers(self):
        for child in self.containers_box.get_children():
            self.containers_box.remove(child)
        
        try:
            containers = self.client.containers.list(all=True)
            
            if not containers:
                label = Gtk.Label(label=self.t("no_containers"))
                label.set_margin_top(50)
                self.containers_box.pack_start(label, False, False, 0)
            else:
                for container in containers:
                    card = self.create_container_card(container)
                    self.containers_box.pack_start(card, False, False, 0)
            
            self.containers_box.show_all()
        except Exception as e:
            print(f"{self.t('error')}: {e}")
    
    def create_container_card(self, container):
        frame = Gtk.Frame()
        frame.get_style_context().add_class('card')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        name_label = Gtk.Label()
        name_label.set_markup(f'<span weight="bold" size="large">{container.name}</span>')
        name_label.set_halign(Gtk.Align.START)
        header.pack_start(name_label, True, True, 0)
        
        status = "running" if container.status == "running" else "stopped"
        status_label = Gtk.Label(label=container.status)
        status_label.get_style_context().add_class(f'status-{status}')
        header.pack_end(status_label, False, False, 0)
        
        box.pack_start(header, False, False, 0)
        
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        info_box.set_margin_top(5)
        
        info_box.pack_start(Gtk.Label(label=f"{self.t('image')}: {container.image.tags[0] if container.image.tags else container.image.short_id}", xalign=0), False, False, 0)
        info_box.pack_start(Gtk.Label(label=f"ID: {container.short_id}", xalign=0), False, False, 0)
        
        box.pack_start(info_box, False, False, 0)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_margin_top(10)
        
        if container.status == "running":
            stop_btn = Gtk.Button(label=f"⏸️ {self.t('stop')}")
            stop_btn.get_style_context().add_class('btn-warning')
            stop_btn.connect("clicked", lambda x: self.stop_container(container))
            button_box.pack_start(stop_btn, True, True, 0)
            
            restart_btn = Gtk.Button(label=f"🔄 {self.t('restart')}")
            restart_btn.get_style_context().add_class('btn-primary')
            restart_btn.connect("clicked", lambda x: self.restart_container(container))
            button_box.pack_start(restart_btn, True, True, 0)
            
            logs_btn = Gtk.Button(label=f"📜 {self.t('logs')}")
            logs_btn.connect("clicked", lambda x: self.show_logs(container))
            button_box.pack_start(logs_btn, True, True, 0)
        else:
            start_btn = Gtk.Button(label=f"▶️ {self.t('start')}")
            start_btn.get_style_context().add_class('btn-success')
            start_btn.connect("clicked", lambda x: self.start_container(container))
            button_box.pack_start(start_btn, True, True, 0)
            
            delete_btn = Gtk.Button(label=f"🗑️ {self.t('delete')}")
            delete_btn.get_style_context().add_class('btn-danger')
            delete_btn.connect("clicked", lambda x: self.delete_container(container))
            button_box.pack_start(delete_btn, True, True, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        frame.add(box)
        return frame
    
    def refresh_images(self):
        for child in self.images_box.get_children():
            self.images_box.remove(child)
        
        try:
            images = self.client.images.list()
            
            if not images:
                label = Gtk.Label(label=self.t("no_images"))
                label.set_margin_top(50)
                self.images_box.pack_start(label, False, False, 0)
            else:
                for image in images:
                    card = self.create_image_card(image)
                    self.images_box.pack_start(card, False, False, 0)
            
            self.images_box.show_all()
        except Exception as e:
            print(f"{self.t('error')}: {e}")
    
    def create_image_card(self, image):
        frame = Gtk.Frame()
        frame.get_style_context().add_class('card')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        tags = image.tags[0] if image.tags else image.short_id
        name_label = Gtk.Label()
        name_label.set_markup(f'<span weight="bold">{tags}</span>')
        name_label.set_halign(Gtk.Align.START)
        box.pack_start(name_label, False, False, 0)
        
        size = round(image.attrs['Size'] / (1024 * 1024), 2)
        box.pack_start(Gtk.Label(label=f"{self.t('size')}: {size} MB", xalign=0), False, False, 0)
        box.pack_start(Gtk.Label(label=f"ID: {image.short_id}", xalign=0), False, False, 0)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_margin_top(10)
        
        backup_btn = Gtk.Button(label=f"💾 {self.t('backup')}")
        backup_btn.get_style_context().add_class('btn-warning')
        backup_btn.connect("clicked", lambda x: self.backup_single_image(image))
        button_box.pack_start(backup_btn, True, True, 0)
        
        delete_btn = Gtk.Button(label=f"🗑️ {self.t('delete')}")
        delete_btn.get_style_context().add_class('btn-danger')
        delete_btn.connect("clicked", lambda x: self.delete_image(image))
        button_box.pack_start(delete_btn, True, True, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        frame.add(box)
        return frame
    
    def backup_single_image(self, image):
        """نسخ احتياطي لصورة واحدة"""
        def backup_thread():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tag = image.tags[0] if image.tags else image.short_id
                safe_name = tag.replace('/', '_').replace(':', '_')
                filepath = os.path.join(self.backup_dir, f"{safe_name}_{timestamp}.tar")
                
                with open(filepath, 'wb') as f:
                    for chunk in image.save():
                        f.write(chunk)
                
                GLib.idle_add(self.show_success, f"{self.t('success')}:\n{filepath}")
                GLib.idle_add(self.refresh_backups)
                
            except Exception as e:
                GLib.idle_add(self.show_error, f"{self.t('error')}: {e}")
        
        thread = threading.Thread(target=backup_thread)
        thread.daemon = True
        thread.start()
    
    def refresh_networks(self):
        for child in self.networks_box.get_children():
            self.networks_box.remove(child)
        
        try:
            networks = self.client.networks.list()
            
            for network in networks:
                card = self.create_network_card(network)
                self.networks_box.pack_start(card, False, False, 0)
            
            self.networks_box.show_all()
        except Exception as e:
            print(f"{self.t('error')}: {e}")
    
    def create_network_card(self, network):
        frame = Gtk.Frame()
        frame.get_style_context().add_class('card')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        name_label = Gtk.Label()
        name_label.set_markup(f'<span weight="bold">{network.name}</span>')
        name_label.set_halign(Gtk.Align.START)
        box.pack_start(name_label, False, False, 0)
        
        box.pack_start(Gtk.Label(label=f"Driver: {network.attrs.get('Driver', 'N/A')}", xalign=0), False, False, 0)
        
        frame.add(box)
        return frame
    
    def refresh_volumes(self):
        for child in self.volumes_box.get_children():
            self.volumes_box.remove(child)
        
        try:
            volumes = self.client.volumes.list()
            
            if not volumes:
                label = Gtk.Label(label=self.t("no_volumes"))
                label.set_margin_top(50)
                self.volumes_box.pack_start(label, False, False, 0)
            else:
                for volume in volumes:
                    card = self.create_volume_card(volume)
                    self.volumes_box.pack_start(card, False, False, 0)
            
            self.volumes_box.show_all()
        except Exception as e:
            print(f"{self.t('error')}: {e}")
    
    def create_volume_card(self, volume):
        frame = Gtk.Frame()
        frame.get_style_context().add_class('card')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        name_label = Gtk.Label()
        name_label.set_markup(f'<span weight="bold">{volume.name}</span>')
        name_label.set_halign(Gtk.Align.START)
        box.pack_start(name_label, False, False, 0)
        
        frame.add(box)
        return frame
    
    def refresh_stats(self):
        try:
            containers = self.client.containers.list(all=True)
            running = len([c for c in containers if c.status == "running"])
            images = self.client.images.list()
            volumes = self.client.volumes.list()
            
            self.total_containers_label.value_label.set_markup(
                f'<span size="xx-large" weight="bold" foreground="#3b82f6">{len(containers)}</span>'
            )
            self.running_containers_label.value_label.set_markup(
                f'<span size="xx-large" weight="bold" foreground="#10b981">{running}</span>'
            )
            self.total_images_label.value_label.set_markup(
                f'<span size="xx-large" weight="bold" foreground="#f59e0b">{len(images)}</span>'
            )
            self.total_volumes_label.value_label.set_markup(
                f'<span size="xx-large" weight="bold" foreground="#ef4444">{len(volumes)}</span>'
            )
            
            info = self.client.info()
            buffer = self.system_info.get_buffer()
            buffer.set_text("")
            
            iter = buffer.get_end_iter()
            buffer.insert(iter, f"{self.t('docker_version')}: {info.get('ServerVersion', 'N/A')}\n")
            buffer.insert(iter, f"{self.t('os')}: {info.get('OperatingSystem', 'N/A')}\n")
            buffer.insert(iter, f"{self.t('architecture')}: {info.get('Architecture', 'N/A')}\n")
            buffer.insert(iter, f"{self.t('cpus')}: {info.get('NCPU', 'N/A')}\n")
            mem_total = round(info.get('MemTotal', 0) / (1024**3), 2)
            buffer.insert(iter, f"{self.t('total_memory')}: {mem_total} GB\n")
            
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")
    
    def start_container(self, container):
        try:
            container.start()
            self.show_success(f"تم تشغيل الحاوية {container.name}")
            self.refresh_containers()
        except Exception as e:
            self.show_error(f"فشل تشغيل الحاوية: {e}")
    
    def stop_container(self, container):
        try:
            container.stop()
            self.show_success(f"تم إيقاف الحاوية {container.name}")
            self.refresh_containers()
        except Exception as e:
            self.show_error(f"فشل إيقاف الحاوية: {e}")
    
    def restart_container(self, container):
        try:
            container.restart()
            self.show_success(f"تمت إعادة تشغيل الحاوية {container.name}")
            self.refresh_containers()
        except Exception as e:
            self.show_error(f"فشل إعادة تشغيل الحاوية: {e}")
    
    def create_header(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        box.get_style_context().add_class('header')
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        # Logo
        if os.path.exists(self.logo_path):
            try:
                logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.logo_path, 50, 50, True)
                logo_image = Gtk.Image.new_from_pixbuf(logo_pixbuf)
                logo_image.set_margin_end(10)
                box.pack_start(logo_image, False, False, 0)
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Title and subtitle
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title = Gtk.Label()
        title.set_markup('<span size="x-large" weight="bold">SnokHub</span>')
        title.set_halign(Gtk.Align.START)
        title_box.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label()
        subtitle.set_markup('<span foreground="#64748b">Docker Manager</span>')
        subtitle.set_halign(Gtk.Align.START)
        title_box.pack_start(subtitle, False, False, 0)
        box.pack_start(title_box, False, False, 0)
        
        # Right aligned items (Packed from end)
        
        # Language selector (Far right)
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lang_icon = Gtk.Label()
        lang_icon.set_markup('<span size="large">🌐</span>')
        lang_box.pack_start(lang_icon, False, False, 0)
        
        self.lang_combo = Gtk.ComboBoxText()
        self.lang_combo.append("en", "EN")
        self.lang_combo.append("fr", "FR")
        self.lang_combo.append("ar", "AR")
        self.lang_combo.set_active_id(self.current_language)
        self.lang_combo.connect("changed", self.on_language_changed)
        lang_box.pack_start(self.lang_combo, False, False, 0)
        box.pack_end(lang_box, False, False, 0)
        
        # About button
        self.about_btn = Gtk.Button()
        self.about_btn.set_label("ℹ️")
        self.about_btn.set_tooltip_text(self.t("about"))
        self.about_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.about_btn.connect("clicked", self.show_about_dialog)
        box.pack_end(self.about_btn, False, False, 5)
        
        # Update button
        self.update_btn = Gtk.Button()
        self.update_btn.set_label("⬇️")  # Or ↻ for update
        self.update_btn.set_tooltip_text(self.t("update_app"))
        self.update_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.update_btn.connect("clicked", self.update_application)
        box.pack_end(self.update_btn, False, False, 5)
        
        # Theme toggle button
        self.theme_btn = Gtk.Button()
        theme_icon = "☀️" if self.current_theme == "dark" else "🌙"
        self.theme_label = Gtk.Label()
        self.theme_label.set_markup(f'<span size="large">{theme_icon}</span>')
        self.theme_btn.add(self.theme_label)
        self.theme_btn.set_tooltip_text(self.t("theme"))
        self.theme_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.theme_btn.connect("clicked", self.toggle_theme)
        box.pack_end(self.theme_btn, False, False, 5)
        
        # Status label
        status_text = "🟢 " + self.t("connected") if self.client else "🔴 " + self.t("disconnected")
        self.status_label = Gtk.Label(label=status_text)
        self.status_label.set_margin_end(15)
        box.pack_end(self.status_label, False, False, 10)
        
        return box
    
    def toggle_theme(self, button):
        """Toggle between dark and light theme"""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        # Update button icon
        theme_icon = "☀️" if new_theme == "dark" else "🌙"
        self.theme_label.set_markup(f'<span size="large">{theme_icon}</span>')
    
    def on_language_changed(self, combo):
        """Handle language change"""
        new_lang = combo.get_active_id()
        if new_lang and new_lang != self.current_language:
            self.set_language(new_lang)
    
    def create_toolbar(self):
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        toolbar.set_margin_top(5)
        toolbar.set_margin_bottom(5)
        
        refresh_btn = Gtk.Button(label=f"🔄 {self.t('refresh')}")
        refresh_btn.get_style_context().add_class('btn-primary')
        refresh_btn.connect("clicked", lambda x: self.refresh_all())
        toolbar.pack_start(refresh_btn, False, False, 0)
        
        create_btn = Gtk.Button(label=f"➕ {self.t('new_container')}")
        create_btn.get_style_context().add_class('btn-success')
        create_btn.connect("clicked", self.on_create_container)
        toolbar.pack_start(create_btn, False, False, 0)
        
        backup_btn = Gtk.Button(label=f"💾 {self.t('backup_all')}")
        backup_btn.get_style_context().add_class('btn-warning')
        backup_btn.connect("clicked", lambda x: self.quick_backup_all())
        toolbar.pack_start(backup_btn, False, False, 0)
        
        clean_btn = Gtk.Button(label=f"🧹 {self.t('cleanup')}")
        clean_btn.get_style_context().add_class('btn-danger')
        clean_btn.connect("clicked", self.on_cleanup)
        toolbar.pack_start(clean_btn, False, False, 0)
        
        return toolbar
    
    def create_containers_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.containers_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.containers_box.set_margin_top(10)
        self.containers_box.set_margin_bottom(10)
        self.containers_box.set_margin_start(10)
        self.containers_box.set_margin_end(10)
        
        scrolled.add(self.containers_box)
        return scrolled
    
    def create_images_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.images_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.images_box.set_margin_top(10)
        self.images_box.set_margin_bottom(10)
        self.images_box.set_margin_start(10)
        self.images_box.set_margin_end(10)
        
        scrolled.add(self.images_box)
        return scrolled
    
    def create_hub_page(self):
        """صفحة تصفح وتحميل الصور من Docker Hub"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        
        # شريط البحث
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        search_label = Gtk.Label(label=f"🔍 {self.t('search')}:")
        search_box.pack_start(search_label, False, False, 0)
        
        self.hub_search_entry = Gtk.Entry()
        self.hub_search_entry.set_placeholder_text(f"{self.t('search')}... (Example: nginx, mysql)")
        search_box.pack_start(self.hub_search_entry, True, True, 0)
        
        search_btn = Gtk.Button(label=self.t("search"))
        search_btn.get_style_context().add_class('btn-primary')
        search_btn.connect("clicked", self.search_dockerhub)
        search_box.pack_start(search_btn, False, False, 0)
        
        popular_btn = Gtk.Button(label=f"⭐ {self.t('popular_images')}")
        popular_btn.get_style_context().add_class('btn-success')
        popular_btn.connect("clicked", lambda x: self.load_popular_images())
        search_box.pack_start(popular_btn, False, False, 0)
        
        main_box.pack_start(search_box, False, False, 0)
        
        # منطقة النتائج
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.hub_results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled.add(self.hub_results_box)
        
        main_box.pack_start(scrolled, True, True, 0)
        
        # تحميل الصور الشائعة تلقائياً
        GLib.timeout_add(500, self.load_popular_images)
        
        return main_box
    
    def create_backup_page(self):
        """صفحة النسخ الاحتياطي والاستعادة"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        main_box.set_margin_top(15)
        main_box.set_margin_bottom(15)
        main_box.set_margin_start(15)
        main_box.set_margin_end(15)
        
        # معلومات النسخ الاحتياطي
        info_frame = Gtk.Frame(label=f"📁 {self.t('backup_info')}")
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        info_box.set_margin_top(10)
        info_box.set_margin_bottom(10)
        info_box.set_margin_start(10)
        info_box.set_margin_end(10)
        
        self.backup_path_label = Gtk.Label()
        self.backup_path_label.set_markup(f'<b>{self.t("backup_path")}:</b> {self.backup_dir}')
        self.backup_path_label.set_halign(Gtk.Align.START)
        info_box.pack_start(self.backup_path_label, False, False, 0)
        
        info_frame.add(info_box)
        main_box.pack_start(info_frame, False, False, 0)
        
        # أزرار النسخ الاحتياطي
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        backup_all_btn = Gtk.Button(label=f"💾 {self.t('backup_all_images')}")
        backup_all_btn.get_style_context().add_class('btn-primary')
        backup_all_btn.connect("clicked", lambda x: self.backup_all_images())
        buttons_box.pack_start(backup_all_btn, True, True, 0)
        
        export_btn = Gtk.Button(label=f"📤 {self.t('export_containers')}")
        export_btn.get_style_context().add_class('btn-success')
        export_btn.connect("clicked", lambda x: self.export_containers())
        buttons_box.pack_start(export_btn, True, True, 0)
        
        open_folder_btn = Gtk.Button(label=f"📂 {self.t('open_backup_folder')}")
        open_folder_btn.connect("clicked", lambda x: subprocess.run(['xdg-open', self.backup_dir]))
        buttons_box.pack_start(open_folder_btn, True, True, 0)
        
        main_box.pack_start(buttons_box, False, False, 0)
        
        # قائمة النسخ الاحتياطية
        backups_frame = Gtk.Frame(label=f"📋 {self.t('available_backups')}")
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(300)
        
        self.backups_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.backups_box.set_margin_top(10)
        self.backups_box.set_margin_bottom(10)
        self.backups_box.set_margin_start(10)
        self.backups_box.set_margin_end(10)
        
        scrolled.add(self.backups_box)
        backups_frame.add(scrolled)
        main_box.pack_start(backups_frame, True, True, 0)
        
        # تحميل النسخ الاحتياطية
        GLib.timeout_add(500, self.refresh_backups)
        
        return main_box
    
    def create_networks_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.networks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.networks_box.set_margin_top(10)
        self.networks_box.set_margin_bottom(10)
        self.networks_box.set_margin_start(10)
        self.networks_box.set_margin_end(10)
        
        scrolled.add(self.networks_box)
        return scrolled
    
    def create_volumes_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.volumes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.volumes_box.set_margin_top(10)
        self.volumes_box.set_margin_bottom(10)
        self.volumes_box.set_margin_start(10)
        self.volumes_box.set_margin_end(10)
        
        scrolled.add(self.volumes_box)
        return scrolled
    
    def create_stats_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        stats_grid = Gtk.Grid()
        stats_grid.set_column_spacing(10)
        stats_grid.set_row_spacing(10)
        
        self.total_containers_label = self.create_stat_card(self.t("total_containers"), "0", "#3b82f6")
        stats_grid.attach(self.total_containers_label, 0, 0, 1, 1)
        
        self.running_containers_label = self.create_stat_card(self.t("running"), "0", "#10b981")
        stats_grid.attach(self.running_containers_label, 1, 0, 1, 1)
        
        self.total_images_label = self.create_stat_card(self.t("total_images"), "0", "#f59e0b")
        stats_grid.attach(self.total_images_label, 0, 1, 1, 1)
        
        self.total_volumes_label = self.create_stat_card(self.t("volumes"), "0", "#ef4444")
        stats_grid.attach(self.total_volumes_label, 1, 1, 1, 1)
        
        box.pack_start(stats_grid, False, False, 0)
        
        self.system_info = Gtk.TextView()
        self.system_info.set_editable(False)
        self.system_info.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer = self.system_info.get_buffer()
        buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.system_info)
        box.pack_start(scrolled, True, True, 0)
        
        return box
    
    def create_stat_card(self, label, value, color):
        frame = Gtk.Frame()
        frame.set_size_request(200, 100)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(15)
        box.set_margin_bottom(15)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        value_label = Gtk.Label()
        value_label.set_markup(f'<span size="xx-large" weight="bold" foreground="{color}">{value}</span>')
        box.pack_start(value_label, False, False, 0)
        
        text_label = Gtk.Label(label=label)
        box.pack_start(text_label, False, False, 0)
        
        frame.add(box)
        frame.value_label = value_label
        return frame
    
    def load_popular_images(self):
        """تحميل الصور الشائعة من Docker Hub"""
        popular_images = [
            {"name": "nginx", "description": "خادم ويب عالي الأداء ومعكوس", "pulls": "1B+", "official": True},
            {"name": "mysql", "description": "قاعدة بيانات MySQL", "pulls": "500M+", "official": True},
            {"name": "postgres", "description": "قاعدة بيانات PostgreSQL", "pulls": "500M+", "official": True},
            {"name": "redis", "description": "قاعدة بيانات في الذاكرة", "pulls": "500M+", "official": True},
            {"name": "mongo", "description": "قاعدة بيانات MongoDB", "pulls": "500M+", "official": True},
            {"name": "python", "description": "بيئة تشغيل Python", "pulls": "500M+", "official": True},
            {"name": "node", "description": "بيئة تشغيل Node.js", "pulls": "500M+", "official": True},
            {"name": "ubuntu", "description": "نظام Ubuntu", "pulls": "1B+", "official": True},
            {"name": "alpine", "description": "نظام Alpine Linux خفيف", "pulls": "500M+", "official": True},
            {"name": "wordpress", "description": "نظام إدارة محتوى", "pulls": "100M+", "official": True},
        ]
        
        self.display_hub_results(popular_images)
        return False
    
    def search_dockerhub(self, button):
        """البحث في Docker Hub"""
        query = self.hub_search_entry.get_text().strip()
        if not query:
            self.show_error("الرجاء إدخال كلمة بحث!")
            return
        
        def search_thread():
            try:
                url = f"https://hub.docker.com/v2/search/repositories/?query={query}&page_size=20"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                results = []
                for item in data.get('results', []):
                    results.append({

                        "name": item.get('repo_name', 'N/A'),
                        "description": item.get('short_description', self.t('no_description'))[:100],
                        "pulls": item.get('pull_count', '0'),
                        "stars": item.get('star_count', 0),
                        "official": item.get('is_official', False)
                    })
                
                GLib.idle_add(self.display_hub_results, results)
                
            except Exception as e:
                GLib.idle_add(self.show_error, f"{self.t('search_error')}: {e}")
        
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
    
    def display_hub_results(self, results):
        """Show search results"""
        for child in self.hub_results_box.get_children():
            self.hub_results_box.remove(child)
        
        if not results:
            label = Gtk.Label(label=self.t("no_results"))
            label.set_margin_top(50)
            self.hub_results_box.pack_start(label, False, False, 0)
        else:
            for image in results:
                card = self.create_hub_card(image)
                self.hub_results_box.pack_start(card, False, False, 0)
        
        self.hub_results_box.show_all()
    
    def create_hub_card(self, image_info):
        """Create Hub image card"""
        frame = Gtk.Frame()
        frame.get_style_context().add_class('hub-card')
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        name_label = Gtk.Label()
        name_markup = f'<span weight="bold" size="large">{image_info["name"]}</span>'
        if image_info.get("official"):
            name_markup += f' <span foreground="#3b82f6">✓ {self.t("official")}</span>'
        name_label.set_markup(name_markup)
        name_label.set_halign(Gtk.Align.START)
        name_box.pack_start(name_label, False, False, 0)
        
        header.pack_start(name_box, True, True, 0)
        
        # عدد التحميلات
        if "pulls" in image_info:
            pulls_label = Gtk.Label()
            pulls_text = str(image_info["pulls"])
            if isinstance(image_info["pulls"], int):
                if image_info["pulls"] >= 1000000:
                    pulls_text = f"{image_info['pulls']/1000000:.1f}M"
                elif image_info["pulls"] >= 1000:
                    pulls_text = f"{image_info['pulls']/1000:.1f}K"
            pulls_label.set_markup(f'<span foreground="#64748b">⬇️ {pulls_text}</span>')
            header.pack_end(pulls_label, False, False, 0)
        
        box.pack_start(header, False, False, 0)
        
        # الوصف
        desc_label = Gtk.Label(label=image_info["description"])
        desc_label.set_halign(Gtk.Align.START)
        desc_label.set_line_wrap(True)
        desc_label.set_max_width_chars(60)
        box.pack_start(desc_label, False, False, 0)
        
        # أزرار التحكم
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_margin_top(10)
        
        # زر التحميل السريع
        quick_pull_btn = Gtk.Button(label="⬇️ تحميل latest")
        quick_pull_btn.get_style_context().add_class('btn-success')
        quick_pull_btn.connect("clicked", lambda x: self.quick_pull_image(image_info["name"], "latest"))
        button_box.pack_start(quick_pull_btn, True, True, 0)
        
        # زر اختيار الإصدار
        version_btn = Gtk.Button(label="🏷️ اختيار إصدار")
        version_btn.get_style_context().add_class('btn-primary')
        version_btn.connect("clicked", lambda x: self.show_version_dialog(image_info["name"]))
        button_box.pack_start(version_btn, True, True, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        frame.add(box)
        return frame
    
    def quick_pull_image(self, image_name, tag):
        """تحميل صورة بسرعة"""
        full_name = f"{image_name}:{tag}"
        
        # نافذة التقدم
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text=f"جاري تحميل {full_name}..."
        )
        
        progress = Gtk.ProgressBar()
        progress.set_show_text(True)
        progress.set_text("جاري التحميل...")
        dialog.get_content_area().pack_start(progress, True, True, 10)
        
        dialog.show_all()
        
        def pull_thread():
            try:
                for line in self.client.api.pull(image_name, tag=tag, stream=True, decode=True):
                    GLib.idle_add(progress.pulse)
                
                GLib.idle_add(dialog.destroy)
                GLib.idle_add(self.show_success, f"تم تحميل {full_name} بنجاح!")
                GLib.idle_add(self.refresh_images)
                
            except Exception as e:
                GLib.idle_add(dialog.destroy)
                GLib.idle_add(self.show_error, f"فشل التحميل: {e}")
        
        thread = threading.Thread(target=pull_thread)
        thread.daemon = True
        thread.start()
    
    def show_version_dialog(self, image_name):
        """عرض نافذة لاختيار إصدار الصورة"""
        dialog = Gtk.Dialog(
            title=f"اختيار إصدار {image_name}",
            transient_for=self,
            flags=0
        )
        dialog.set_default_size(400, 200)
        
        box = dialog.get_content_area()
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        
        label = Gtk.Label(label="أدخل الإصدار (Tag):")
        box.pack_start(label, False, False, 5)
        
        entry = Gtk.Entry()
        entry.set_text("latest")
        entry.set_placeholder_text("مثال: latest, 1.0, alpine")
        box.pack_start(entry, False, False, 5)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_margin_top(10)
        
        cancel_btn = Gtk.Button(label="إلغاء")
        cancel_btn.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.CANCEL))
        button_box.pack_start(cancel_btn, True, True, 0)
        
        pull_btn = Gtk.Button(label="تحميل")
        pull_btn.get_style_context().add_class('btn-success')
        pull_btn.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.OK))
        button_box.pack_start(pull_btn, True, True, 0)
        
        box.pack_start(button_box, False, False, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            tag = entry.get_text().strip()
            if tag:
                dialog.destroy()
                self.quick_pull_image(image_name, tag)
            else:
                dialog.destroy()
                self.show_error("الرجاء إدخال إصدار صحيح!")
        else:
            dialog.destroy()
    
    def show_error(self, message):
        """عرض رسالة خطأ"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
    
    def show_success(self, message):
        """عرض رسالة نجاح"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
    
    def auto_refresh(self):
        """تحديث تلقائي"""
        if self.client:
            try:
                self.refresh_stats()
            except:
                pass
        return True
    
    def on_create_container(self, button):
        """إنشاء حاوية جديدة"""
        self.show_error("هذه الميزة قيد التطوير")
    
    def on_cleanup(self, widget):
        """Clean up unused resources"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=self.t("cleanup_confirm")
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            try:
                self.client.containers.prune()
                self.client.images.prune()
                self.client.networks.prune()
                self.client.volumes.prune()
                
                self.show_success(self.t("cleanup_success"))
                self.refresh_all()
            except Exception as e:
                self.show_error(f"{self.t('error')}: {e}")
    
    def delete_container(self, container):
        """Delete container"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"{self.t('delete_container_confirm')} {container.name}?"
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            try:
                container.remove(force=True)
                self.show_success(f"{self.t('container_deleted')} {container.name}")
                self.refresh_containers()
            except Exception as e:
                self.show_error(f"{self.t('error')}: {e}")
    
    def delete_image(self, image):
        """Delete image"""
        tag = image.tags[0] if image.tags else image.short_id
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"{self.t('delete_image_confirm')} {tag}?"
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            try:
                self.client.images.remove(image.id, force=True)
                self.show_success(f"{self.t('image_deleted')} {tag}")
                self.refresh_images()
            except Exception as e:
                self.show_error(f"{self.t('error')}: {e}")
    
    def show_logs(self, container):
        """Show container logs"""
        dialog = Gtk.Dialog(
            title=f"{self.t('logs')} {container.name}",
            transient_for=self,
            flags=0
        )
        dialog.set_default_size(700, 500)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_monospace(True)
        
        try:
            logs = container.logs(tail=200).decode('utf-8', errors='ignore')
            textview.get_buffer().set_text(logs)
        except Exception as e:
            textview.get_buffer().set_text(f"{self.t('error')}: {e}")
        
        scrolled.add(textview)
        dialog.get_content_area().pack_start(scrolled, True, True, 0)
        
        close_btn = Gtk.Button(label=self.t("close"))
        close_btn.connect("clicked", lambda x: dialog.destroy())
        dialog.get_content_area().pack_start(close_btn, False, False, 10)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def show_about_dialog(self, button):
        """Show About dialog"""
        about = Gtk.AboutDialog()
        about.set_program_name("SnokHub")
        about.set_version("1.0.0")
        about.set_copyright("© 2026 SnokOS")
        about.set_comments(f"{self.t('app_title')}\n\n{self.t('company')}: SnokOS\n{self.t('developer')}: Mahrez Ben Mohammed\n{self.t('phone')}: +216 26 360 802")
        about.set_website("https://snokos.github.io/SnokOS/")
        about.set_website_label(self.t("website"))
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_scale(self.logo_path, 100, 100, True))
        about.set_transient_for(self)
        about.run()
        about.destroy()

    def update_application(self, button):
        """Update application from GitHub"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=self.t("update_confirm")
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            try:
                # Run git pull
                process = subprocess.Popen(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(os.path.abspath(__file__)))
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    self.show_success(self.t("update_success"))
                else:
                    self.show_error(f"{self.t('update_failed')}: {stderr.decode()}")
            except Exception as e:
                self.show_error(f"{self.t('update_failed')}: {e}")

if __name__ == "__main__":
    app = DockerManagerApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
