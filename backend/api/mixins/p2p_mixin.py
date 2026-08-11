# backend/api/mixins/p2p_mixin.py

class P2PMixin:
    """P2P服务核心操作 Mixin"""

    def p2p_start_server(self):
        """启动P2P服务器"""
        try:
            def data_received_callback(data, address):
                """数据接收回调"""
                # 存储接收到的数据供前端获取
                self._received_data = data
                self.get_logger.info(f"接收到来自 {address[0]} 的数据")

            def data_request_callback():
                """数据请求回调 - 返回要共享的数据"""
                if hasattr(self, '_exported_data') and self._exported_data:
                    return self._exported_data
                return None

            self._p2p_server.set_data_request_callback(data_request_callback)

            success, message = self._p2p_server.start(data_received_callback)

            if success:
                local_ip = self._p2p_server.get_local_ip()
                return {
                    'success': True,
                    'ip': local_ip,
                    'port': self._p2p_server.port,
                    'message': message or f'服务器已启动，IP: {local_ip}, 端口: {self._p2p_server.port}'
                }
            else:
                return {'success': False, 'error': message or '服务器启动失败'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_get_shared_data(self):
        """获取要共享的数据（供服务器使用）"""
        try:
            if hasattr(self, '_exported_data'):
                return self._exported_data
            return None
        except:
            return None

    def p2p_stop_server(self):
        """停止P2P服务器"""
        try:
            if hasattr(self, '_p2p_server'):
                success, message = self._p2p_server.stop()
                return {'success': success, 'message': message or '服务器已停止'}
            return {'success': True, 'message': '服务器未运行'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_scan_devices(self):
        """扫描局域网内的设备"""
        try:
            devices = self._p2p_client.scan_devices()
            return {'success': True, 'devices': devices}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_receive_data(self, ip):
        """从指定设备接收数据"""
        try:
            data = self._p2p_client.receive_data(ip)
            if data:
                # 存储接收到的数据供前端确认后导入
                self._received_data = data
                return {'success': True, 'data': data}
            else:
                return {'success': False, 'error': '接收数据失败'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_get_received_data(self):
        """获取接收到的数据"""
        try:
            if hasattr(self, '_received_data'):
                return {'success': True, 'data': self._received_data}
            return {'success': False, 'error': '暂无接收到的数据'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_export_data(self):
        """导出当前数据"""
        try:
            self._exported_data = self._data_manager.export_data()
            if self._exported_data:
                # 存储导出的数据供服务器使用
                return {'success': True, 'data': self._exported_data}
            else:
                return {'success': False, 'error': '导出数据失败'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_get_exported_data(self):
        """获取导出的数据"""
        try:
            if hasattr(self, '_exported_data'):
                return {'success': True, 'data': self._exported_data}
            return {'success': False, 'error': '暂无导出的数据'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_get_data_summary(self):
        """获取当前数据摘要"""
        try:
            summary = self._data_manager.get_data_summary()
            if summary:
                return {'success': True, 'summary': summary}
            else:
                return {'success': False, 'error': '获取数据摘要失败'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_has_data(self):
        """检查是否有数据"""
        try:
            has_data = self._data_manager.has_data()
            return {'success': True, 'has_data': has_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def p2p_import_data(self, data):
        """导入数据"""
        try:
            # 在安卓设备上由于可能存在权限问题，因而不做备份操作
            success = self._data_manager.import_data(data, backup=(not self.is_android))
            if success:
                # 导入成功后刷新前端缓存
                self._received_data = None
                self.get_logger.info("数据导入成功")
                return {'success': True, 'message': '数据导入成功'}
            else:
                self.get_logger.error("数据导入失败")
                return {'success': False, 'error': '数据导入失败'}
        except Exception as e:
            self.get_logger.error(f"导入数据异常: {e}")
            return {'success': False, 'error': str(e)}