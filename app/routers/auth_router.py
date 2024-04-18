from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from app.auth_handler import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_reset_password_token,
    decode_reset_password_token,
    get_password_hash,
)
from app.crud import get_user
from app.models import ForgetPasswordRequest, ResetPasswordRequest
from app.settings import settings
from fastapi_mail import FastMail, MessageSchema, MessageType


# Initialize the APIRouter with a prefix of "/auth" and a tag of "auth"
router = APIRouter(prefix="/api", tags=["login"])


# Route for user login
@router.post("/login")
async def login_user_route(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticates a user using the provided email and password, and returns a new access token.
    :param form_data: The UserLogin data containing the user's email and password.
    :return: The access token and token type if the authentication is successful, an HTTPException otherwise.
    """
    user_info = await authenticate_user(form_data.username, form_data.password)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=user_info, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# forget password route
# @router.post("/forget-password")
@router.post("/password-recovery/{email}", tags=["forget_password"])
async def forget_password_route(
    background_tasks: BackgroundTasks, fpr: ForgetPasswordRequest
):
    try:
        user = await get_user(email=fpr.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid email address",
            )

        secret_token = create_reset_password_token(email=user["email"])
        forget_url_link = (
            f"{settings.APP_BASE_URL}{settings.FORGET_PASSWORD_URL}/{secret_token}"
        )

        email_body = {
            "company": settings.MAIL_FROM_NAME,
            "link_expiry_min": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
            "reset_link": forget_url_link,
        }

        message = MessageSchema(
            subject="Password Reset Instructions",
            recipients=[fpr.email],
            template_body=email_body,
            subtype=MessageType.html,
        )
        template_name = "mail/password_reset.html"

        fm = FastMail(settings.conf)
        background_tasks.add_task(fm.send_message, message, template_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Email has been sent",
                "success": True,
                "status_code": status.HTTP_200_OK,
            },
        )

    except Exception as e:
        print(e)


# reset password route
@router.post("/reset-password")
async def reset_password_route(reset_password_request: ResetPasswordRequest):

    try:

        info = decode_reset_password_token(reset_password_request.token)
        if info is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Password Reset Payload or Reset Link Expired",
            )

        if info["email"] != reset_password_request.email:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid email address",
            )

        hashed_password = get_password_hash(reset_password_request.new_password)
        user = get_user(info)
        user.password = hashed_password
        # add user to mongodb database
        await user.save()

        return {'success': True, 'status_code': status.HTTP_200_OK,
                 'message': 'Password Reset Successfull!'}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something Unexpected, Server Error",
        )


# @router.post("/reset-password")
# async def reset_password_route(reset_password_request: ResetPasswordRequest):
#     try:
#         user = await get_user(email=reset_password_request.email)
#         if user is None:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Invalid email address",
#             )

#         user["password"] = get_password_hash(
#             password=reset_password_request.new_password
#         )
#         await user.save()
#         return "Password reset successful"

#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Something Unexpected, Server Error",
#         )
