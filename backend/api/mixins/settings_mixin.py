# backend/api/mixins/settings_mixin.py

class SettingsMixin:
    """读写数据库中的settings表操作 Mixin"""

    def get_settings(self):
        """获取所有设置"""
        try:
            from backend.database.operations import TodoDatabase
            settings_db = TodoDatabase()
            settings = settings_db.get_all_settings()
            return {'success': True, 'settings': settings}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_setting(self, key, default_value=None):
        """获取单个设置"""
        try:
            from backend.database.operations import TodoDatabase
            settings_db = TodoDatabase()
            value = settings_db.get_setting(key, default_value)
            return {'success': True, 'value': value}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def set_setting(self, key, value):
        """保存单个设置"""
        try:
            from backend.database.operations import TodoDatabase
            settings_db = TodoDatabase()
            settings_db.set_setting(key, value)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_setting(self, key):
        """删除单个设置"""
        try:
            from backend.database.operations import TodoDatabase
            settings_db = TodoDatabase()
            settings_db.delete_setting(key)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def reset_settings(self):
        """重置所有设置为默认值"""
        try:
            from backend.database.operations import TodoDatabase
            settings_db = TodoDatabase()
            settings_db.reset_settings()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}