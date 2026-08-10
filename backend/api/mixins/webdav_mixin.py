# backend/api/mixins/webdav_mixin.py

class WebDAVMixin:
    """WebDAV同步核心操作 Mixin"""

    def _call_manager_method(self, method_name, *args, **kwargs):
        """通用调用 sync_manager 的方法，自动处理异常和不支持的情况"""
        if self.sync_manager and hasattr(self.sync_manager, method_name):
            try:
                return getattr(self.sync_manager, method_name)(*args, **kwargs)
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': '当前系统不支持'}

    def get_webdav_config(self):
        """获取WebDAV配置"""
        return self._call_manager_method('get_webdav_config')

    def set_webdav_config(self, config):
        """设置WebDAV配置"""
        return self._call_manager_method('set_webdav_config', config)

    def test_webdav_connection(self, url, username, password, remote_path):
        """测试WebDAV连接"""
        return self._call_manager_method('test_webdav_connection', url, username, password, remote_path)

    def sync_from_cloud(self, is_overwrite=False):
        """从云端同步数据到本地"""
        return self._call_manager_method('sync_from_cloud', is_overwrite)

    def sync_to_cloud(self):
        """将本地数据同步到云端"""
        return self._call_manager_method('sync_to_cloud')

    def get_sync_status(self):
        """获取同步状态"""
        return self._call_manager_method('get_sync_status')

    def trigger_upload_on_change(self):
        """在数据变更时触发上传"""
        return self._call_manager_method('trigger_upload_on_change')