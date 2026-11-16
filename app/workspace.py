from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from html import escape
import re

router = APIRouter()

SECTIONS = [
    ("Start Here", "/"),
    ("Data Review", "/data"),
    ("Find Problems", "/problems"),
    ("Build / Modify", "/review"),
    ("Test", "/test"),
    ("Walkthrough", "/walkthrough"),
    ("Submit", "/submit"),
    ("History", "/history"),
    ("Legacy", "/legacy"),
]

# The former placeholder pages now redirect to the real tabs.
REDIRECTS = {"start": "/", "data": "/data", "build": "/review", "test": "/test",
             "walkthrough": "/walkthrough", "submit": "/submit"}


@router.get("/workspace/{section}")
def workspace_page(section: str):
    from fastapi.responses import RedirectResponse
    if section not in REDIRECTS:
        return HTMLResponse("Page not found", status_code=404)
    return RedirectResponse(REDIRECTS[section])

class NavigationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if "text/html" not in response.headers.get("content-type", ""):
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        page = body.decode("utf-8", errors="replace")

        if 'id="bellhaven-navigation"' not in page:
            buttons = "".join(
                '<a href="{}" style="display:inline-block;'
                'padding:10px 13px;margin:3px;border-radius:8px;'
                'background:#263a57;color:#fff;text-decoration:none;'
                'font:14px Arial">{}</a>'.format(url, escape(name))
                for name, url in SECTIONS
            )
            nav = (
                '<nav id="bellhaven-navigation" style="'
                'padding:15px;background:#111c30;'
                'border-bottom:1px solid #405577">'
                '<strong style="color:white;font:16px Arial">'
                'Bellhaven Workspace</strong><div style="margin-top:8px">'
                + buttons +
                                '</div></nav>'
            )
            match = re.search(r"<body[^>]*>", page, re.I)
            if match:
                page = page[:match.end()] + nav + page[match.end():]
            else:
                page = nav + page

        headers = {
            k: v for k, v in response.headers.items()
            if k.lower() not in ("content-length", "content-encoding")
        }
        return Response(
            page,
            status_code=response.status_code,
            headers=headers,
            media_type="text/html"
        )

def install(app):
    app.include_router(router)
    app.add_middleware(NavigationMiddleware)
