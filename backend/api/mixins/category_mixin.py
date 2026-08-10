# backend/api/mixins/category_mixin.py

class CategoryMixin:
    """分类核心操作 Mixin"""

    def add_category(self, category_data):
        """添加新分类"""
        try:
            result = self.db.add_category(category_data)
            return {'success': True, 'category': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_categories(self):
        """获取所有分类"""
        try:
            categories = self.db.get_all_categories()
            return {'success': True, 'categories': categories}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_category(self, category_id):
        """删除分类"""
        try:
            result = self.db.delete_category(category_id)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_category(self, category_id, category_data):
        """更新分类"""
        try:
            result = self.db.update_category(category_id, category_data)
            return {'success': True, 'category': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}