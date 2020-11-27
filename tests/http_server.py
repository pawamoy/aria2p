from fastapi import FastAPI
from fastapi.responses import StreamingResponse


def translate_size(size):
    try:
        return int(size)
    except ValueError:
        pass
    size = size.lower()
    if size.endswith("k"):
        multiplier = 2 ** 10
    elif size.endswith("m"):
        multiplier = 2 ** 20
    elif size.endswith("g"):
        multiplier = 2 ** 30
    else:
        raise ValueError("size unit not supported:", size)
    return int(size.rstrip("kmg")) * multiplier


async def virtual_file(size, chunks=4096):
    while size > 0:
        yield b"1" * min(size, chunks)
        size -= chunks


app = FastAPI()


@app.get("/{size}")
async def get(size):
    return StreamingResponse(
        virtual_file(translate_size(size)),
        media_type="application/octet-stream",
    )
