from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi import status
from fastapi.exceptions import RequestValidationError

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, OPTIONS, etc.
    allow_headers=["*"],
)

# Custom handler for 422 errors to print the request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body = await request.body()
        print("Unprocessable Entity (422) - Request body:", body.decode())
    except Exception as e:
        print("Unprocessable Entity (422) - Could not decode request body.")
    return PlainTextResponse(str(exc), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class RestaurantInfo(BaseModel):
    name: str
    address: str
    cuisine: str
    menu: list[str]
    rating: float
    reservation_required: bool
    opening_hours: str

class TwilloNumRequest(BaseModel):
    twillo_num: str

class ReservationRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    num_people: Optional[int] = None
    date: Optional[str] = None  # e.g., '2025-08-04'
    time: Optional[str] = None  # e.g., '19:00'
    special_requests: Optional[str] = None

@app.post("/restaurant_info")
def get_restaurant_info(request: TwilloNumRequest):
    # Dummy data
    data = RestaurantInfo(
        name="Sultans Dine",
        address="123 Main St, Dhaka",
        cuisine="Bangladeshi",
        menu=[
            "Kacchi Biryani",
            "Chicken Roast",
            "Mutton Rezala",
            "Borhani",
            "Firni"
        ],
        rating=4.7,
        reservation_required=True,
        opening_hours="11:00-23:00"
    )
    return JSONResponse(content=data.model_dump())

@app.post("/reserve")
def make_reservation(request: ReservationRequest):
    # Check if the reservation date is 9th August
    if request.date:
        # Accept both '9-08', '09-08', '2025-08-09', etc.
        if (
            request.date.strip().endswith("-08-09") or
            request.date.strip().endswith("-8-9") or
            request.date.strip() == "9-08" or
            request.date.strip() == "09-08" or
            request.date.strip() == "8-9" or
            request.date.strip() == "08-09"
        ):
            response = {
                "success": False,
                "message": "Sorry, reservations are not available on 9th August. Please choose another date.",
                "details": request.model_dump()
            }
            return JSONResponse(content=response)
    response = {
        "success": True,
        "message": f"Reservation confirmed for {request.name} on {request.date} at {request.time}.",
        "details": request.model_dump()
    }
    return JSONResponse(content=response)

# Call log through vapi webhook (parsed JSON will be saved here)
import os
PARSED_JSONL_FILE = os.path.join(os.path.dirname(__file__), "parsed_calls_log.jsonl")

@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    import json, openai
    from openai import OpenAI
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    payload = await request.json()
    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    artifact = message.get("artifact", {}) if isinstance(message, dict) else {}
    message_type = message.get("type")

    if message_type != "end-of-call-report":
        return {"status": "ignored", "reason": message_type}

    # --- Helpers (scoped inside endpoint to avoid changing rest of file) ---
    from datetime import datetime, timezone
    from typing import Any, Dict, Union

    def _parse_unix_numeric(value: Union[int, float]) -> Union[str, None]:
        ts_seconds = value / 1000 if value > 1e12 else value
        try:
            return datetime.fromtimestamp(ts_seconds, tz=timezone.utc).date().isoformat()
        except (OverflowError, OSError, ValueError):
            return None

    def _parse_iso8601(value: str) -> Union[str, None]:
        s = value.strip()
        if s.endswith('Z'):
            s = s[:-1]
        if ' ' in s and 'T' not in s:
            s = s.replace(' ', 'T')
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt.date().isoformat()
        except ValueError:
            return None

    def _parse_possible_numeric_string(value: str) -> Union[str, None]:
        s = value.strip()
        if s.isdigit():
            try:
                return _parse_unix_numeric(int(s))
            except Exception:
                return None
        if 'Date(' in s:
            import re
            m = re.search(r'Date\((\d{10,})\)', s)
            if m:
                try:
                    return _parse_unix_numeric(int(m.group(1)))
                except Exception:
                    return None
        return None

    def extract_call_date_utc(started_at):
        if started_at is None:
            return None
        if isinstance(started_at, (int, float)):
            return _parse_unix_numeric(started_at)
        if isinstance(started_at, str):
            iso = _parse_iso8601(started_at)
            if iso:
                return iso
            num = _parse_possible_numeric_string(started_at)
            if num:
                return num
        return None

    def _iter_candidates(msg: Dict[str, Any]):
        art = msg.get('artifact', {}) if isinstance(msg, dict) else {}
        keys = [
            ('artifact', 'startedAt'), ('artifact', 'started_at'),
            ('artifact', 'startTime'), ('artifact', 'started'),
            ('startedAt',), ('started_at',), ('startTime',), ('started',)
        ]
        for path in keys:
            cur = msg if path[0] != 'artifact' else art
            if len(path) == 2:
                cur = art.get(path[1])
            else:
                cur = msg.get(path[0])
            if cur is not None:
                yield cur

    def get_call_date(msg: Dict[str, Any]):
        for c in _iter_candidates(msg):
            d = extract_call_date_utc(c)
            if d:
                return d
        return None

    call_date = get_call_date(message)

    duration_seconds = (
        artifact.get("durationSeconds")
        or (artifact.get("durationMs", 0) / 1000 if artifact.get("durationMs") else None)
        or message.get("durationSeconds")
    )

    summary = (
        artifact.get("summary")
        or message.get("analysis", {}).get("summary")
    )

    recording_mono_combined_url = (
        (artifact.get("recording") or {})
        .get("mono", {})
        .get("combinedUrl")
    )

    # Extract the time portion from the call date
    if call_date:
        call_time = datetime.strptime(call_date, "%Y-%m-%d").time().strftime("%H:%M:%S")
    else:
        call_time = None

    def define_type(summary: str) -> str:
        try:
            response = client.responses.create(
                    model="gpt-5-nano",
                    input=f"""
                    Based on the following call summary, classify the call type into one of these categories: 'reservation', 'order', 'service'.\n
                    If user requests a reservation, classify as 'reservation'.\n
                    If user places an order, classify as 'order'.\n
                    If user asks for help or has a complaint or none of the above, classify as 'service'.\n\n
                    Call Summary: {summary}\n
                    Respond with only one word: 'reservation', 'order', or 'service'. No other text.
                    """
                )

            return response.output_text
        except Exception as e:
            raise RuntimeError(f"Failed to classify call type: {e}")

    assistant_id = message.get("assistant", {}).get("id")
    parsed = {
        "type": define_type(summary),
        "phone": message.get("customer", {}).get("number"),
        "call_date": call_date,
        "call time": call_time, 
        "duration_seconds": duration_seconds,
        "summary": summary,
        "recording": recording_mono_combined_url,
        "assistant_id": assistant_id
    }

    # try:
    #     with open(PARSED_JSONL_FILE, "a", encoding="utf-8") as f:
    #         f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
    # except Exception as e:
    #     parsed["file_write_error"] = str(e)
    # return parsed
    
    stored_parsed = parsed
    print("Parsed call log:", stored_parsed)
    return stored_parsed