from fastapi import Depends, HTTPException, status  # type: ignore
from app.auth_handler import decode_token, oauth2_scheme
from app.models import TokenData
from jose import JWTError
from app.crud import get_user


# Dependency function to retrieve the current user from the provided access token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user from the provided access token.
    :param token: The access token to extract the user information from.
    :return: The user data if the token is valid, an HTTPException otherwise.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception

        token_data = TokenData(email=email)
    except JWTError:
        raise credential_exception

    user = await get_user(email=token_data.email)
    if user is None:
        raise credential_exception

    return user
