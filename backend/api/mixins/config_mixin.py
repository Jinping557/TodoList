# backend/api/mixins/config_mixin.py

from backend.utils import utils

class ConfigMixin:
    """配置操作 Mixin"""

    # ==================== 开机自启动相关API ====================

    def get_auto_start_config(self):
        """获取开机自启动配置"""
        try:
            status = self.service.get_auto_start_status()
            return {
                'success': True,
                'config': {
                    'enabled': utils.str_to_bool(status['enabled']),
                    'platform': status['platform'],
                    'supported': status['supported']
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def set_auto_start_config(self, enabled):
        """设置开机自启动配置"""
        try:
            success = self.service.set_auto_start_enabled(enabled)
            if success:
                return {
                    'success': True,
                    'message': '开机自启动设置已保存'
                }
            else:
                return {
                    'success': False,
                    'error': '设置开机自启动失败'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 窗口置顶相关API ====================

    def set_window_on_top_config(self, enabled):
        """设置窗口置顶配置"""
        try:
            import backend.globals
            self.db.set_setting('window_on_top', enabled)
            backend.globals.window.on_top = utils.str_to_bool(self.db.get_setting('window_on_top', False))
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_window_on_top_config(self):
        """获取窗口置顶配置"""
        try:
            enabled = utils.str_to_bool(self.db.get_setting('window_on_top', False))
            return {
                'success': True,
                'enabled': enabled
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 快捷键相关API ====================

    def set_shortcut_config(self, shortcut):
        """设置快捷键配置"""
        try:
            self.db.set_setting('shortcut', shortcut)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_shortcut_config(self):
        """获取快捷键配置"""
        try:
            shortcut = self.db.get_setting('shortcut', '<ctrl>+<space>')
            return {
                'success': True,
                'config': shortcut
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def set_shortcut_enabled(self, enabled):
        """设置快捷操作开关"""
        try:
            self.db.set_setting('shortcut_enabled', enabled)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_shortcut_enabled(self):
        """获取快捷操作开关状态"""
        try:
            enabled = utils.str_to_bool(self.db.get_setting('shortcut_enabled', True))
            return {
                'success': True,
                'enabled': enabled
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 快捷键相关API ====================

    def set_theme_config(self, theme):
        """设置快捷键配置"""
        try:
            self.db.set_setting('theme', theme)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_theme_config(self):
        """获取快捷键配置"""
        try:
            theme = self.db.get_setting('theme', 'light')
            return {
                'success': True,
                'config': theme
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def set_language_config(self, language):
        """设置快捷键配置"""
        try:
            self.db.set_setting('language', language)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_language_config(self):
        """获取快捷键配置"""
        try:
            language = self.db.get_setting('language', 'zh')
            return {
                'success': True,
                'config': language
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }