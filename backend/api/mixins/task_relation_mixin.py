# backend/api/mixins/task_relation_mixin.py

class TaskRelationMixin:
    """任务关联核心操作 Mixin"""

    def get_children(self, task_id):
        """获取指定任务的直接子任务列表（完整任务信息）"""
        try:
            children = self.db.get_children(task_id)
            return {'success': True, 'children': children}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_parent(self, task_id):
        """获取指定任务的父任务（完整任务信息）"""
        try:
            parent = self.db.get_parent(task_id)
            return {'success': True, 'parent': parent}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def add_task_relation(self, sub_task_id, main_task_id):
        """为单个子任务设置父任务（若已存在则更新）"""
        try:
            sub = self.db.get_task(sub_task_id)
            if not sub:
                return {'success': False, 'error': '子任务不存在'}
            main = self.db.get_task(main_task_id)
            if not main:
                return {'success': False, 'error': '父任务不存在'}
            if sub_task_id == main_task_id:
                return {'success': False, 'error': '不能将自己设为父任务'}
            if sub.get('isRecurring'):
                return {'success': False, 'error': '周期性任务不允许添加父任务关联'}
            self.db.add_task_relation(sub_task_id, main_task_id)
            return {'success': True, 'message': '关联已建立'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def remove_task_relation(self, sub_task_id):
        """移除单个子任务的父任务关联"""
        try:
            sub = self.db.get_task(sub_task_id)
            if not sub:
                return {'success': False, 'error': '子任务不存在'}
            self.db.delete_relation_by_children(sub_task_id)
            return {'success': True, 'message': '关联已移除'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def batch_add_task_relations(self, sub_task_ids, main_task_id):
        """批量将多个子任务关联到同一个父任务"""
        try:
            if not sub_task_ids:
                return {'success': False, 'error': '子任务列表为空'}
            main = self.db.get_task(main_task_id)
            if not main:
                return {'success': False, 'error': '父任务不存在'}
            success_count = 0
            errors = []
            for sub_id in sub_task_ids:
                try:
                    if sub_id == main_task_id:
                        errors.append(f'{sub_id}: 不能将自己设为父任务')
                        continue
                    sub = self.db.get_task(sub_id)
                    if not sub:
                        errors.append(f'{sub_id}: 子任务不存在')
                        continue
                    if sub.get('isRecurring'):
                        errors.append(f'{sub_id}: 周期性任务不允许添加父任务关联')
                        continue
                    self.db.add_task_relation(sub_id, main_task_id)
                    success_count += 1
                except Exception as e:
                    errors.append(f'{sub_id}: {str(e)}')
            return {
                'success': True,
                'success_count': success_count,
                'errors': errors,
                'total': len(sub_task_ids)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def batch_remove_task_relations(self, sub_task_ids):
        """批量移除多个子任务的父任务关联"""
        try:
            if not sub_task_ids:
                return {'success': False, 'error': '子任务列表为空'}
            success_count = 0
            errors = []
            for sub_id in sub_task_ids:
                try:
                    sub = self.db.get_task(sub_id)
                    if not sub:
                        errors.append(f'{sub_id}: 子任务不存在')
                        continue
                    self.db.delete_relation_by_children(sub_id)
                    success_count += 1
                except Exception as e:
                    errors.append(f'{sub_id}: {str(e)}')
            return {
                'success': True,
                'success_count': success_count,
                'errors': errors,
                'total': len(sub_task_ids)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_subtasks_by_parent_name(self, parent_name, page=1, page_size=10,
                                       category_id=None, status=None, priority=None,
                                       due_date_filter=None):
        """通过父任务名称搜索其子任务（要求父任务名称完全匹配），并按当前筛选条件过滤。

        筛选参数与 get_todos 语义一致（参考 operations.get_tasks_paginated）：
        - category_id: 'all'|'uncategorized'|<具体分类ID>|None
        - status: all|completed|uncompleted|pending|overdue
        - priority: all|high|medium|low|none
        - due_date_filter: all|today|tomorrow|week|month|no-due-date
        """
        from datetime import datetime, timedelta
        try:
            # 先查找父任务
            parent_task = self.db.find_task_by_title_exact(parent_name)
            if not parent_task:
                return {'success': True, 'tasks': [], 'total': 0, 'page': page, 'page_size': page_size,
                        'total_pages': 0}

            # 获取该父任务的子任务
            children = self.db.get_children(parent_task['id'])

            # 应用筛选条件（与 get_tasks_paginated 语义对齐）
            def _iso_date(val):
                if not val:
                    return None
                try:
                    return datetime.fromisoformat(str(val)).date()
                except Exception:
                    return None

            today = datetime.now().date()

            def _pending_overdue(task):
                d = _iso_date(task.get('dueDate'))
                if task.get('completed'):
                    return {'pending': False, 'overdue': False}
                return {
                    'pending': d is None or d >= today,
                    'overdue': d is not None and d < today,
                }

            # 计算日期区间
            def _tomorrow():
                if today.day < 28:
                    return today.replace(day=today.day + 1)
                if today.month < 12:
                    return today.replace(day=1, month=today.month + 1)
                return today.replace(year=today.year + 1, month=1, day=1)

            week_start = today - timedelta(days=today.weekday())
            week_end_candidate = week_start + timedelta(days=7)
            week_end = week_end_candidate if today.day <= 21 else today.replace(day=28)
            month_start = today.replace(month=today.month, day=1)
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            month_end = next_month - timedelta(days=1)

            norm_status = status if status not in (None, 'all', '') else None
            norm_priority = priority if priority not in (None, 'all', '') else None
            norm_cat = category_id if category_id not in (None, 'all', '') else None
            norm_dd = due_date_filter if due_date_filter not in (None, 'all', '') else None

            filtered = []
            for t in children:
                # 状态筛选
                if norm_status:
                    if norm_status == 'completed' and not t.get('completed'):
                        continue
                    if norm_status == 'uncompleted' and t.get('completed'):
                        continue
                    po = _pending_overdue(t)
                    if norm_status == 'pending' and not po['pending']:
                        continue
                    if norm_status == 'overdue' and not po['overdue']:
                        continue
                # 优先级筛选
                if norm_priority and (t.get('priority') or 'none') != norm_priority:
                    continue
                # 分类筛选
                if norm_cat:
                    cid = t.get('categoryId')
                    if norm_cat == 'uncategorized':
                        if cid not in (None, ''):
                            continue
                    elif cid != norm_cat:
                        continue
                # 日期筛选
                if norm_dd:
                    d = _iso_date(t.get('dueDate'))
                    if norm_dd == 'today':
                        if d != today:
                            continue
                    elif norm_dd == 'tomorrow':
                        if d != _tomorrow():
                            continue
                    elif norm_dd == 'week':
                        if d is None or not (week_start <= d < week_end):
                            continue
                    elif norm_dd == 'month':
                        if d is None or not (month_start <= d <= month_end):
                            continue
                    elif norm_dd == 'no-due-date':
                        if d is not None:
                            continue
                filtered.append(t)

            # 分页处理
            total = len(filtered)
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_children = filtered[start_idx:end_idx]

            return {
                'success': True,
                'tasks': paginated_children,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'parent_task': {'id': parent_task['id'], 'title': parent_task['title']}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_tasks_with_subtasks(self, keyword='', limit=5):
        """搜索具有子任务的父任务（按标题模糊匹配），返回前 limit 条。

        供前端在搜索框输入 ">" 时调用，下拉展示有子任务的父任务建议。
        返回: {'success': True, 'tasks': [{id, title, priority, dueDate, completed, subtaskCount}, ...]}
        """
        try:
            tasks = self.db.search_tasks_with_subtasks(keyword=keyword or '', limit=limit)
            return {'success': True, 'tasks': tasks}
        except Exception as e:
            return {'success': False, 'error': str(e)}