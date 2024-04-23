from typing import Dict, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import httpx

app = FastAPI()


class StockData(BaseModel):
    exchange: str
    symbol: str


@app.get("/")
async def read_root() -> Dict[str, str]:
    return {"Message": "Hello World"}


@app.post("/fetch/")
async def fetch(stock_data: StockData) -> Dict[str, Union[str, Dict[str, str]]]:
    exchange = stock_data.exchange
    symbol = stock_data.symbol

    urls = {
        "NSE": f"http://python-fastapi-nse:8000/nse/{symbol}",
        "INDEX": f"http://python-fastapi-nse:8000/index/{symbol}",
    }

    if exchange not in urls:
        raise HTTPException(status_code=400, detail="Invalid exchange")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(urls[exchange])
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Symbol not found or HTML structure changed",
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Error fetching data"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Error parsing response"
            )

    return {
        "msg": "Data fetched successfully",
        "exchange": exchange,
        "symbol": symbol,
        "name": data.get("name"),
        "price": data.get("price"),
    }


if __name__ == "__main__":
    uvicorn.run(app, port=8001, host="0.0.0.0")