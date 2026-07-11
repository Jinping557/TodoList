# impl/desktop/win_impl.py
from backend.platforms.interface.service import PlatformService
from backend.platforms.impl.desktop.win_firewall_manager import FirewallManager

import os
from pathlib import Path

class WindowsService(PlatformService):
    def shortcut_handler(self, shortcut, handler):
        try:
            import backend.globals
            from pynput import keyboard
            listener = keyboard.GlobalHotKeys({shortcut: handler})
            listener.start()
            self.backend_logger().info(f"【系统日志】快捷键监听成功挂载！当前在 Mac 下的标准热键为: {shortcut}")
            return None
        except Exception as e:
            self.backend_logger().error(f"【系统日志】快捷键挂载失败: {e}")

    def force_kill_process_tree(self, pid):
        """强制结束当前进程及其所有子进程的统一接口"""
        import subprocess
        import time
        # --- Windows ---
        # 优雅终止 (SIGTERM)
        subprocess.run(f'taskkill /PID {pid} /T', shell=True)
        time.sleep(2)
        # 强制终止 (SIGKILL)
        subprocess.run(f'taskkill /F /T /PID {pid}', shell=True, capture_output=True)

    def get_log_directory(self):
        """返回可写的日志目录的统一接口"""
        import sys
        # Windows: exe 同级目录（用户通常有写权限）
        exe_dir = Path(sys.executable).parent
        log_dir = exe_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def get_app_icon(self, base_path):
        """获取应用图标的统一接口"""
        return base_path / 'todo_icon.ico'

    def is_ssl_enable(self):
        """获取是否开启ssl的统一接口"""
        return True

    def is_default_hide(self):
        """获取是否隐藏快捷键窗口的统一接口"""
        return True

    def icon_exit(self):
        """图标注销消息的统一接口"""
        pass

    def start_prepare(self):
        """应用启动前准备工作的统一接口"""
        pass

    def start_keyboard(self):
        """应用启用快捷键的统一接口"""
        from backend.platforms.impl.desktop.common.smart_task import SmartTaskInput
        SmartTaskInput(self)

    def start_desktop_task_reminder(self, is_start, event=None):
        """应用桌面端消息提醒的统一接口"""
        from backend.platforms.impl.desktop.common.task_reminder import start_reminder, stop_reminder
        if is_start:
            start_reminder(platform_service=self,click_event=event)
        else:
            stop_reminder(self)

    def add_new_desktop_task_reminder(self):
        """应用桌面端新任务添加消息提醒的统一接口"""
        from backend.platforms.impl.desktop.common.task_reminder import get_reminder
        # 重置已提醒任务列表，确保新任务可以被提醒
        reminder = get_reminder(self)
        reminder.reset_notified_tasks()

    def check_calendar_permission(self):
        """校验日历使用权限的统一接口"""
        pass

    def add_task_reminder_to_calendar(self, title, desc, start_time_ms):
        """添加任务提醒到日历的统一接口"""
        pass

    def sync_reminder_to_calendar(self, sync_start_time, sync_end_time):
        """同步任务提醒到日历的统一接口"""
        pass

    def add_firewall_rule(self, port):
        """添加防火墙策略规则的统一接口"""
        firewall_manager = FirewallManager(service= self, port=port)
        return firewall_manager.add_rule()

    def remove_firewall_rule(self, port):
        """移除防火墙策略规则的统一接口"""
        firewall_manager = FirewallManager(service= self, port=port)
        return firewall_manager.remove_rule()

    def get_auto_start_status(self):
        """获取自动重启开关状态的统一接口"""
        from backend.database.operations import TodoDatabase
        auto_start_enabled = TodoDatabase().get_setting('auto_start_enabled', False)
        return {
            'enabled': auto_start_enabled,
            'platform': 'windows',
            'supported': True
        }

    def enable_windows_auto_start(self, app_name) -> bool:
        """启用开机自启动"""
        from backend.utils import utils
        app_path = utils.get_app_path(self)

        try:
            import winreg

            # 启动命令
            launch_cmd = utils.get_launch_command(self)

            # 注册表路径
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            # 打开注册表键
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                # 设置注册表值
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, launch_cmd)

            self.backend_logger().info(f"Windows开机自启动已启用: {launch_cmd}")
            return True

        except ImportError:
            # 备用方案：使用启动文件夹
            startup_folder = Path(
                os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            startup_folder.mkdir(parents=True, exist_ok=True)

            # 创建快捷方式
            shortcut_path = startup_folder / f"{app_name}.lnk"

            # 使用Python创建快捷方式
            import pythoncom
            from win32com.client import Dispatch

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.Targetpath = app_path
            shortcut.WorkingDirectory = str(Path(app_path).parent)

            shortcut.save()

            self.backend_logger().warning(f"Windows启动文件夹快捷方式已创建: {shortcut_path}")

            return True
        except Exception as e:
            self.backend_logger().error(f"启用开机自启动失败: {e}")
            return False

    def disable_windows_auto_start(self, app_name) -> bool:
        """禁用开机自启动"""
        try:
            import winreg

            # 注册表路径
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            # 尝试删除注册表项
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                # 注册表项不存在，继续检查启动文件夹
                pass

            # 删除启动文件夹中的快捷方式和批处理文件
            startup_folder = Path(
                os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'

            # 删除快捷方式
            shortcut_path = startup_folder / f"{app_name}.lnk"
            if shortcut_path.exists():
                shortcut_path.unlink()

            # 删除批处理文件
            bat_path = startup_folder / f"{app_name}.bat"
            if bat_path.exists():
                bat_path.unlink()

            self.backend_logger().info("Windows开机自启动已禁用")
            return True

        except Exception as e:
            self.backend_logger().error(f"Windows禁用自启动失败: {e}")
            return False

    def set_auto_start_enabled(self, enabled):
        """设置自动重启开关状态的统一接口"""
        self.backend_logger().info(f"设置开机自启动状态: {enabled}")
        try:
            # 保存配置
            from backend.database.operations import TodoDatabase
            TodoDatabase().set_setting('auto_start_enabled', enabled)

            app_name = "TodoList"

            # 根据状态设置或取消自启动
            if enabled:
                return self.enable_windows_auto_start(app_name)
            else:
                return self.disable_windows_auto_start(app_name)

        except Exception as e:
            self.backend_logger().error(f"设置开机自启动失败: {e}")
            return False

    def start_app(self):
        """启动应用的统一接口"""
        from backend.platforms.impl.desktop.common.system_tray import SystemTrayManager
        manager = SystemTrayManager(self)
        manager.start_app(True)

    def frontend_logger(self):
        """前端日志的统一接口"""
        from backend.utils.logger import setup_logger
        # 创建默认的logger实例
        return setup_logger(self, 'frontend')

    def backend_logger(self):
        """后端日志的统一接口"""
        from backend.utils.logger import setup_logger
        # 创建默认的logger实例
        return setup_logger(self, 'backend')

# 用于给工厂注册的导出变量
ExportService = WindowsService
