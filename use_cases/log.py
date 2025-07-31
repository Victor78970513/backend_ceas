from infrastructure.log_repository import LogRepository
from schemas.log import LogSistemaResponse
from fastapi import HTTPException
from typing import List

class LogUseCase:
    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository

    def list_logs(self) -> List[LogSistemaResponse]:
        logs = self.log_repository.list_logs()
        return [LogSistemaResponse(**l.__dict__) for l in logs]

    def get_log(self, log_id: int) -> LogSistemaResponse:
        l = self.log_repository.get_log(log_id)
        if not l:
            raise HTTPException(status_code=404, detail="Log no encontrado")
        return LogSistemaResponse(**l.__dict__) 