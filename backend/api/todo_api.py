"""
TodoList应用的前后端通信API
"""
import sys
from pathlib import Path
from backend.database.operations import TodoDatabase
from backend.database.data_export import DataExportManager
from backend.features.p2p.p2p_server import P2PServer
from backend.features.p2p.p2p_client import P2PClient
from backend.api.mixins.category_mixin import CategoryMixin
from backend.api.mixins.config_mixin import ConfigMixin
from backend.api.mixins.datafile_mixin import DatafileMixin
from backend.api.mixins.p2p_mixin import P2PMixin
from backend.api.mixins.settings_mixin import SettingsMixin
from backend.api.mixins.tag_mixin import TagMixin
from backend.api.mixins.task_mixin import TaskMixin
from backend.api.mixins.task_relation_mixin import TaskRelationMixin
from backend.api.mixins.utility_mixin import UtilityMixin
from backend.api.mixins.webdav_mixin import WebDAVMixin
from backend.platforms.core.factory import get_platform_service

# 确保能找到database模块
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

class TodoApi(
    CategoryMixin, ConfigMixin, DatafileMixin, P2PMixin,
    SettingsMixin, TagMixin, TaskMixin, TaskRelationMixin,
    UtilityMixin, WebDAVMixin
):
    """TodoList应用的API类，提供前后端通信接口"""
    
    def __init__(self, is_android, sync_manager):
        self.db = TodoDatabase()
        self.is_android = is_android
        self.sync_manager = sync_manager
        self._received_data = None
        self._exported_data = None
        self.service = get_platform_service()
        self.get_logger = self.service.backend_logger()
        self._p2p_server = P2PServer(self.service)
        self._p2p_client = P2PClient(self.service)
        self._data_manager = DataExportManager(self.service)
        try:
            self.service.add_new_desktop_task_reminder()
            self.get_logger.info("任务提醒器已重置")
        except Exception as e:
            self.get_logger.warning(f"重置任务提醒器失败: {e}")