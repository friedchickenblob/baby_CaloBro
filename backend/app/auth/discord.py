import os
import httpx
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.db import SessionLocal
from app.models import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth/discord")

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")


def _allowed_frontends():
    raw = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return [u.strip().rstrip("/") for u in raw.split(",") if u.strip()]


def _pick_frontend(requested: str | None) -> str:
    """Return the requested frontend only if it is in the allow-list."""
    allowed = _allowed_frontends()
    if requested and requested.rstrip("/") in allowed:
        return requested.rstrip("/")
    return allowed[0]


@router.get("/login")
async def discord_login(frontend: str | None = None):
    # The frontend passes its own origin so we can send the user back to it.
    state = quote(_pick_frontend(frontend), safe="")
    url = (
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        "&scope=identify email"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )
    return RedirectResponse(url)






@router.get("/callback")
async def discord_callback(code: str, request: Request, state: str | None = None):
    async with httpx.AsyncClient() as client:
        # exchange code for token
        token_res = await client.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        token_json = token_res.json()
        access_token = token_json.get("access_token")

        if not access_token:
            raise HTTPException(400, "Failed to get token")

        # fetch user info
        user_res = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        discord_user = user_res.json()

    # --- save to database ---
    db: Session = SessionLocal()
    user = db.query(User).filter(User.discord_id == discord_user["id"]).first()

    if not user:
        user = User(
            discord_id=discord_user["id"],
            username=discord_user["username"],
            email=discord_user.get("email"),
            verified=discord_user.get("verified", False),
            avatar=discord_user.get("avatar"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    response = RedirectResponse(
    url=_pick_frontend(state) + "/",
    status_code=302,
)

    print("this is discord id", discord_user["id"])
    request.session["user_id"] = discord_user["id"]
    db.close()
    # return {"message": "User saved", "user": {"id": user.id, "username": user.username}}
    return response
