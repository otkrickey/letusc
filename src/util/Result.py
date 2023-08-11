class Result:
    scope: str
    status: str
    message: str
    method: str

    def __init__(self, scope: str, status: str, message: str, method: str) -> None:
        self.scope = scope
        self.status = status
        self.message = message
        self.method = method

    def addScope(self, scope: str):
        self.scope = f'{self.scope}:{scope}'

    def changeScope(self, scope: str):
        self.scope = scope

    def __str__(self) -> str:
        document = {
            'scope': self.scope,
            'status': self.status,
            'message': self.message,
            'method': self.method
        }
        json = str(document).replace("'", '"')
        return json
