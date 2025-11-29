from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from mcstatus import JavaServer, BedrockServer

app = FastAPI(title="Minecraft Status API")


@app.get("/java/status")
async def java_status(
    host: str = Query(..., description="Minecraft Java server hostname or IP"),
    port: int = Query(25565, description="Minecraft Java server port"),
):
    """
    Java版のサーバーに対して、いわゆる「ping」(status) を実行して返します。
    """
    try:
        server = JavaServer.lookup(f"{host}:{port}")
        status = server.status()

        # 必要そうな情報だけ抜粋。生データが欲しければ status.raw などを返してもよい
        version = None
        if getattr(status, "version", None):
            v = status.version
            version = {
                "name": getattr(v, "name", None),
                "protocol": getattr(v, "protocol", None),
            }

        data = {
            "online": True,
            "host": host,
            "port": port,
            "version": version,
            "latency_ms": status.latency,
            "players": {
                "online": status.players.online,
                "max": status.players.max,
                "sample": [
                    {"name": p.name, "id": p.id}
                    for p in (status.players.sample or [])
                ],
            },
            "motd": getattr(status.description, "to_mojangson", lambda: str(status.description))(),
        }
        return JSONResponse(content=data)

    except Exception as e:
        # サーバーが落ちている / 接続できないなど
        return JSONResponse(
            status_code=200,
            content={
                "online": False,
                "host": host,
                "port": port,
                "error": str(e),
            },
        )
