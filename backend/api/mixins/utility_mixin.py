# backend/api/mixins/utility_mixin.py
import webbrowser
from backend.platforms.core.factory import get_platform_service
service = get_platform_service()

class UtilityMixin:
    """工具方法 Mixin"""

    # 日历写入权限校验
    def check_calendar_permission(self):
        """检查权限"""
        service.check_calendar_permission()

    def log(self, level, message, source='frontend'):
        """从前端记录日志

        Args:
            level: 日志级别（debug, info, warning, error, critical）
            message: 日志消息
            source: 日志来源
        """
        log = service.frontend_logger()
        level_map = {
            'debug': log.debug,
            'info': log.info,
            'warning': log.warning,
            'error': log.error,
            'critical': log.critical
        }

        log_func = level_map.get(level.lower(), log.info)
        log_func(f"[{source}] {message}")

    def open_in_browser(self, url):
        webbrowser.open(url)

    def export_tasks_excel(self, priority=None, status=None, year=None, month=None,
                           category_id=None, tag_ids=None):
        return service.export_tasks_excel(self.db, priority, status, year, month, category_id, tag_ids)