from pydantic import BaseModel

class RequestHeaders(BaseModel):
    authorization: str
    user_agent: str | None = None
    x_request_id: str | None = None
    x_client_version: str | None = None
    x_api_key: str | None = None

class AdminHeaders(BaseModel):
    authorization: str
    x_admin_key: str
    x_request_id: str | None = None