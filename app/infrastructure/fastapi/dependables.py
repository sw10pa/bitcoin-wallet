from starlette.requests import Request

from app.core.facade import Service


def get_core(request: Request) -> Service:
    core: Service = request.app.state.core
    return core
