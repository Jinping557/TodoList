# backend/api/mixins/tag_mixin.py

class TagMixin:
    """标签核心操作 Mixin"""

    def get_all_tags(self):
        """获取所有标签"""
        try:
            tags = self.db.get_all_tags()
            return {'success': True, 'tags': tags}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_task_tags(self, task_id):
        """获取任务的标签"""
        try:
            tags = self.db.get_task_tags(task_id)
            return {'success': True, 'tags': tags}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_tag(self, tag_id):
        """删除标签"""
        try:
            self.db.delete_tag(tag_id)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}