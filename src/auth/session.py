from flask import request

COOKIE_NAME = "guest_uid"

def get_uid_from_cookie():
    return request.cookies.get(COOKIE_NAME)

def set_uid_cookie(response, uid: str):
    response.set_cookie(
        COOKIE_NAME,
        value=uid,
        max_age=60 * 60 * 24 * 30, 
        httponly=True,
        secure=True,
        samesite="Lax"
    )

def clear_uid_cookie(response):
    response.set_cookie(COOKIE_NAME, '', expires=0)
