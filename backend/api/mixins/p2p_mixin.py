# backend/api/mixins/p2p_mixin.py
from backend.utils.response_wrapper import api_handler

class P2PMixin:
    """P2P服务核心操作 Mixin"""

    @api_handler
    def p2p_start_server(self):
        """启动P2P服务器"""
        def data_received_callback(data, address):
            """数据接收回调"""
            # 存储接收到的数据供前端获取
            self._received_data = data
            self.get_logger.info(f"接收到来自 {address[0]} 的数据")

        def data_request_callback():
            """数据请求回调 - 返回要共享的数据"""
            return self._exported_data if self._exported_data else None

        self._p2p_server.set_data_request_callback(data_request_callback)
        success, message = self._p2p_server.start(data_received_callback)

        if not success:
            raise Exception(message or f'服务器启动失败')

        local_ip = self._p2p_server.get_local_ip()
        return {
            'ip': local_ip,
            'port': self._p2p_server.port,
            'message': message or f'服务器已启动，IP: {local_ip}, 端口: {self._p2p_server.port}'
        }

    @api_handler
    def p2p_stop_server(self):
        """停止P2P服务器"""
        self._p2p_server.stop()
        return None

    @api_handler
    def p2p_scan_devices(self):
        """扫描局域网内的设备"""
        return self._p2p_client.scan_devices()

    @api_handler
    def p2p_receive_data(self, ip):
        """从指定设备接收数据"""
        self._received_data = self._p2p_client.receive_data(ip)
        if not self._received_data:
            raise Exception(f'接收数据失败')
        return self._received_data

    @api_handler
    def p2p_get_received_data(self):
        """获取接收到的数据"""
        return self._received_data

    @api_handler
    def p2p_export_data(self):
        """导出当前数据"""
        self._exported_data = self._data_manager.export_data()
        if not self._exported_data:
            raise Exception(f'导出数据失败')
        return self._exported_data

    @api_handler
    def p2p_get_data_summary(self):
        """获取当前数据摘要"""
        summary = self._data_manager.get_data_summary()
        if not summary:
            raise Exception(f'获取数据摘要失败')
        return summary

    @api_handler
    def p2p_has_data(self):
        """检查是否有数据"""
        return self._data_manager.has_data()

    @api_handler
    def p2p_import_data(self, data):
        """导入数据"""
        # 在安卓设备上由于可能存在权限问题，因而不做备份操作
        success = self._data_manager.import_data(data, backup=(not self.is_android))
        if not success:
            raise Exception(f'数据导入失败')
        # 导入成功后刷新前端缓存
        self._received_data = None
        return None