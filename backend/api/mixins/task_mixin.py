# backend/api/mixins/task_mixin.py
from datetime import datetime
from backend.platforms.core.factory import get_platform_service
service = get_platform_service()
backend_logger = service.backend_logger()

class TaskMixin:
    """任务核心操作 Mixin"""

    # ---------- 辅助校验 ----------
    def validate_due_date(self, task_data):
        """校验截止时间（完全拷贝原方法）"""
        if isinstance(task_data, dict):
            due_date_str = task_data.get('dueDate')
            if not due_date_str:
                return {'valid': True, 'message': ''}
        else:
            due_date_str = task_data

        if not due_date_str:
            return {'valid': True, 'message': ''}

        try:
            due_date = datetime.fromisoformat(due_date_str)
            now = datetime.now()

            if due_date < now:
                return {
                    'valid': False,
                    'message': '截止时间不能早于当前时间'
                }

            return {'valid': True, 'message': ''}

        except ValueError:
            return {
                'valid': False,
                'message': '截止时间格式无效'
            }

    # ---------- 任务 CRUD ----------
    def add_todo(self, task_data):
        """添加新任务"""
        # 校验截止时间
        validation_result = self.validate_due_date(task_data)
        if not validation_result['valid']:
            return {'success': False, 'error': validation_result['message']}

        try:
            if task_data['dueDate'] and self.is_android:
                target_time = datetime.fromisoformat(task_data['dueDate']).timestamp() * 1000
                service.add_task_reminder_to_calendar(task_data['title'], task_data['description'], target_time)
            result = self.db.add_task(task_data)
            return {'success': True, 'task': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_todos(self, page=1, page_size=10, category_id=None, status=None,
                  priority=None, due_date_filter=None, year=None, month=None,
                  search_query=None, custom_date=None, custom_start_date=None, custom_end_date=None):
        """分页获取任务，支持多种筛选条件

        参数:
            page: 页码，从1开始
            page_size: 每页数量，支持10/20/50/100
            category_id: 分类ID，'all'表示所有分类，'uncategorized'表示未分类
            status: 状态筛选，可选值: all/completed/uncompleted/pending/overdue
            priority: 优先级筛选，可选值: all/high/medium/low/none
            due_date_filter: 日期筛选，可选值: all/today/tomorrow/week/month/no-due-date
            year: 年份筛选
            month: 月份筛选
            search_query: 搜索关键词
            custom_date: 自定义具体日期筛选，格式YYYY-MM-DD
            custom_start_date: 自定义开始日期筛选，格式YYYY-MM-DD
            custom_end_date: 自定义结束日期筛选，格式YYYY-MM-DD
        """
        try:
            result = self.db.get_tasks_paginated(
                page=page,
                page_size=page_size,
                category_id=category_id,
                status=status,
                priority=priority,
                due_date_filter=due_date_filter,
                year=year,
                month=month,
                search_query=search_query,
                custom_date=custom_date,
                custom_start_date=custom_start_date,
                custom_end_date=custom_end_date
            )
            return {'success': True, **result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_todo(self, task_id):
        """获取单个任务"""
        try:
            task = self.db.get_task(task_id)
            return {'success': True, 'task': task}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_todo(self, task_id, task_data):
        """更新任务"""
        # 校验截止时间
        validation_result = self.validate_due_date(task_data)
        if not validation_result['valid']:
            return {'success': False, 'error': validation_result['message']}

        try:
            result = self.db.update_task(task_id, task_data)
            return {'success': True, 'task': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_todo_due_date(self, task_id, due_date):
        """更新任务"""
        # 校验截止时间
        validation_result = self.validate_due_date(due_date)
        if not validation_result['valid']:
            return {'success': False, 'error': validation_result['message']}

        try:
            result = self.db.update_task_due_date(task_id, due_date)
            return {'success': True, 'task': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_todo(self, task_id, delete_all=False):
        """删除任务"""
        try:
            # 先检查是否为周期性任务
            task = self.db.get_task(task_id)
            if task and (task.get('isRecurring') or task.get('parentTaskId')):
                result = self.db.delete_recurring_task(task_id, delete_all)
            else:
                result = self.db.delete_task(task_id)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def add_recurring_todo(self, task_data):
        """添加周期性任务"""
        # 校验截止时间
        validation_result = self.validate_due_date(task_data)
        if not validation_result['valid']:
            return {'success': False, 'error': validation_result['message']}

        # 校验周期性任务参数
        if task_data.get('isRecurring'):
            if not task_data.get('recurrenceType'):
                return {'success': False, 'error': '周期类型不能为空'}
            if not task_data.get('dueDate'):
                return {'success': False, 'error': '周期性任务必须设置截止时间'}

        try:
            result = self.db.create_recurring_tasks(task_data)
            for task in result:
                if task.get('dueDate') and self.is_android:
                    target_time = datetime.fromisoformat(task['dueDate']).timestamp() * 1000
                    service.add_task_reminder_to_calendar(task['title'], task['description'], target_time)
            return {'success': True, 'task': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def toggle_todo(self, task_id):
        """切换任务完成状态"""
        try:
            task = self.db.get_task(task_id)
            if task:
                task['completed'] = not task['completed']
                result = self.db.update_task(task_id, task, False)
                return {'success': True, 'task': result}
            return {'success': False, 'error': 'Task not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_stats(self):
        """任务统计"""
        try:
            from datetime import timedelta

            tasks = self.db.get_all_tasks()
            now = datetime.now()

            # 总未完成
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task['completed'])
            uncompleted_tasks = total_tasks - completed_tasks

            # 今日已完成
            today_completed_tasks = sum([1 for task in tasks if task['completed'] and task['updatedAt'] and
                              datetime.fromisoformat(task['updatedAt']).date() == now.date()])
            # 已逾期
            over_due_tasks = sum([1 for task in tasks if not task['completed'] and task['dueDate'] and
                              datetime.fromisoformat(task['dueDate']) < now])

            return {
                'success': True,
                'stats': {
                    'uncompleted': uncompleted_tasks,
                    'today_completed': today_completed_tasks,
                    'over_due': over_due_tasks,
                    'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}