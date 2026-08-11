# backend/api/mixins/datafile_mixin.py

import os
from backend.database.operations import TodoDatabase
from backend.database.data_export import DataExportManager

class DatafileMixin:
    """数据目录配置操作 Mixin"""

    def get_data_file_config(self):
        """获取数据文件配置"""
        try:
            from backend.config import get_current_data_file, get_default_data_file
            from backend.database.operations import get_app_data_file
            from backend.config_manager import get_config_manager

            current_file = get_current_data_file()
            default_file = get_default_data_file()
            actual_file = str(get_app_data_file())

            # 获取配置管理器中的配置信息
            config_manager = get_config_manager(self.service)
            external_config = config_manager.get('data_file')

            return {
                'success': True,
                'current_file': current_file,
                'default_file': default_file,
                'actual_file': actual_file,
                'external_config': external_config,
                'is_custom': current_file != default_file
            }
        except Exception as e:
            self.get_logger.error(f"获取数据文件配置失败: {e}")
            return {'success': False, 'error': str(e)}

    def set_data_file_config(self, file_path):
        """设置数据文件配置"""
        try:
            from backend.config import set_data_file

            # 验证并设置新文件
            if set_data_file(file_path):
                # 重新初始化数据库连接以使用新文件
                self.db = TodoDatabase()

                # 更新数据管理器
                if hasattr(self, '_data_manager'):
                    self._data_manager.switch_data_file(file_path)
                else:
                    self._data_manager = DataExportManager(self.service, file_path)

                self.get_logger.info(f"数据文件已设置为: {file_path}")
                return {
                    'success': True,
                    'message': '数据文件设置成功',
                    'new_file': file_path
                }
            else:
                return {'success': False, 'error': '设置数据文件失败'}

        except Exception as e:
            self.get_logger.error(f"设置数据文件配置失败: {e}")
            return {'success': False, 'error': str(e)}

    def validate_data_file(self, file_path):
        """验证数据文件路径的有效性"""
        try:
            from pathlib import Path

            if not file_path or not isinstance(file_path, str):
                return {'success': False, 'error': '文件路径不能为空'}

            path = Path(file_path)

            # 检查路径格式
            try:
                path.resolve()
            except Exception:
                return {'success': False, 'error': '文件路径格式无效'}

            # 检查扩展名
            if path.suffix.lower() not in ['.db']:
                return {'success': False, 'error': '仅支持 .db 文件'}

            # 检查权限
            if path.exists():
                if not os.access(path, os.R_OK | os.W_OK):
                    return {'success': False, 'error': '没有对该文件的读写权限'}
            else:
                # 检查父目录权限
                parent = path.parent
                if not parent.exists():
                    return {'success': False, 'error': '父目录不存在'}
                if not os.access(parent, os.W_OK):
                    return {'success': False, 'error': '没有在该目录创建文件的权限'}

            return {'success': True, 'message': '文件路径有效'}

        except Exception as e:
            return {'success': False, 'error': f'验证文件路径时出错: {str(e)}'}

    def select_file_dialog(self):
        """打开文件选择对话框"""
        try:
            import webview
            active_window = webview.active_window()
            file_types = ('All files (*.*)',)
            selected_path = active_window.create_file_dialog(
                webview.FileDialog.OPEN,
                file_types=file_types
            )

            if selected_path:
                return {
                    'success': True,
                    'selected_path': selected_path,
                    'message': '文件选择成功'
                }
            else:
                return {
                    'success': False,
                    'error': '用户取消了文件选择'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'文件选择对话框不可用: {str(e)}',
                'fallback': True
            }