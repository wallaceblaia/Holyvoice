from fastapi import WebSocket
from typing import Dict, Optional
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, monitoring_id: int, websocket: WebSocket):
        """Conecta um novo cliente websocket"""
        await websocket.accept()
        self.active_connections[monitoring_id] = websocket

    def disconnect(self, monitoring_id: int):
        """Desconecta um cliente websocket"""
        if monitoring_id in self.active_connections:
            del self.active_connections[monitoring_id]

    async def send_progress(self, monitoring_id: int, data: dict):
        """Envia atualização de progresso para um cliente específico"""
        if websocket := self.active_connections.get(monitoring_id):
            try:
                await websocket.send_json(data)
            except Exception:
                self.disconnect(monitoring_id)

    async def broadcast(self, data: dict):
        """Envia mensagem para todos os clientes conectados"""
        for monitoring_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(data)
            except Exception:
                self.disconnect(monitoring_id)

# Instância global do gerenciador de conexões
manager = ConnectionManager() 