bl_info = {
    "name": "Addon_v1 Auto‑Updater",
    "author": "FeelDiference",
    "version": (0, 6),
    "blender": (4, 3, 0),
    "description": "Automatically poll GitHub for updates, reload addon and Blender scripts",
    "category": "Development",
}

import bpy, os, io, json, zipfile, importlib, urllib.request
from bpy.app.handlers import persistent
from bpy.props import IntProperty

# === Настройки под ваш репо ===
GITHUB_API_COMMITS = "https://api.github.com/repos/FeelDiference/addon_v1/commits/main"
GITHUB_ZIP_ARCHIVE  = "https://github.com/FeelDiference/addon_v1/archive/refs/heads/main.zip"

# === Пути внутри аддона ===
ADDONS_PATH = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons')
ADDON_NAME  = "addon_v1"
ADDON_DIR   = os.path.join(ADDONS_PATH, ADDON_NAME)
STATE_FILE  = os.path.join(ADDON_DIR, ".last_sha")

# --- Получаем и ставим SHA ---

def get_last_local_sha():
    if os.path.exists(STATE_FILE):
        return open(STATE_FILE, "r").read().strip()
    return None


def set_last_local_sha(sha):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(sha)

# --- Работа с GitHub ---

def fetch_remote_sha():
    with urllib.request.urlopen(GITHUB_API_COMMITS) as r:
        data = json.load(r)
        return data.get("sha")


def download_and_extract_zip():
    with urllib.request.urlopen(GITHUB_ZIP_ARCHIVE) as r:
        buf = io.BytesIO(r.read())
    with zipfile.ZipFile(buf) as z:
        root = z.namelist()[0]
        for member in z.namelist():
            if member.endswith("/"):
                continue
            rel_path = member[len(root):]
            target = os.path.join(ADDON_DIR, rel_path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as out:
                out.write(z.read(member))

# --- Перезагрузка модулей и скриптов ---

def reload_addon_modules():
    module_name = f"{ADDON_NAME}.test"
    if module_name in locals():
        importlib.reload(locals()[module_name])
    else:
        locals()[module_name] = importlib.import_module(module_name)
    # Перезагрузить все скрипты Blender
    bpy.ops.script.reload()

# --- Основная функция обновления ---

def auto_update():
    prefs = bpy.context.preferences.addons[__name__].preferences
    try:
        remote = fetch_remote_sha()
        local  = get_last_local_sha()
        if local != remote:
            print(f"[AutoUpdater] New SHA {remote}, updating…")
            download_and_extract_zip()
            set_last_local_sha(remote)
            # Авто‑включение скачанного аддона, если ещё не активирован
            if ADDON_NAME not in bpy.context.preferences.addons:
                bpy.ops.preferences.addon_enable(module=ADDON_NAME)
                print(f"[AutoUpdater] Addon '{ADDON_NAME}' enabled.")
            # Перезагрузить скрипты Blender, чтобы изменения вступили в силу
            bpy.ops.script.reload()
            print(f"[AutoUpdater] Scripts reloaded for '{ADDON_NAME}'.")
        else:
            print("[AutoUpdater] No changes.")
    except Exception as e:
        print(f"[AutoUpdater] Error: {e}")
    # возвращаем интервал для следующего вызова
    return prefs.poll_interval

# --- Operator для ручного обновления ---
class ADDON_OT_manual_update(bpy.types.Operator):
    bl_idname = "addon_v1.manual_update"
    bl_label = "Обновить"
    bl_description = "Pull latest from GitHub and reload addon and scripts"

    def execute(self, context):
        auto_update()
        self.report({'INFO'}, "Addon enabled and scripts reloaded")
        return {'FINISHED'}

# --- Аддон настройки ---
class ADDONPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    poll_interval: IntProperty(
        name="Poll Interval (s)",
        description="Seconds between checking GitHub for updates",
        default=60,
        min=5,
        max=3600,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "poll_interval")
        layout.operator(ADDON_OT_manual_update.bl_idname, icon='FILE_REFRESH')

# --- Регистрация ---
def register():
    bpy.utils.register_class(ADDON_OT_manual_update)
    bpy.utils.register_class(ADDONPreferences)
    # Запуск таймера при активации аддона
    prefs = bpy.context.preferences.addons[__name__].preferences
    bpy.app.timers.register(auto_update, first_interval=prefs.poll_interval)


def unregister():
    bpy.utils.unregister_class(ADDONPreferences)
    bpy.utils.unregister_class(ADDON_OT_manual_update)

if __name__ == "__main__":
    register()
