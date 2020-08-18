
import jwt
from datetime import datetime, timedelta
import bcrypt
from models import User


def signup(data):
    user = User(
        name=data["username"],
        email=data["email"],
        company_name=data["company_name"],
        company_url=data["company_url"],
        password=bcrypt.hashpw(
            data["password"].encode('utf-8'),
            bcrypt.gensalt()
        )
    )
    try:
        user.save()
        return {
            "statusCode": 200,
            "message": "SignupSuccessful",
            "auth_token": jwt.encode({
                'email': data["email"],
                'expiry_date': (
                    datetime.now() +
                    timedelta(hours=24) -
                    datetime(1970, 1, 1)
                ).total_seconds()
            }, "YOUR-KEY-GOES-HERE").decode('utf-8')
        }
    except Exception:
        return {
            'statusCode': 301,
            "message": "SignupFailed"
        }


def login(data):
    try:
        userexists = User.objects.get(email=data["email"])
        if bcrypt.checkpw(
            data["password"].encode('utf-8'),
            userexists.password
        ):
            return {
                "statusCode": 200,
                "message": "LoginSuccessful",
                "auth_token": jwt.encode({
                    'email': data["email"],
                    'expiry_date': (
                        datetime.now() +
                        timedelta(hours=24) -
                        datetime(1970, 1, 1)
                    ).total_seconds()
                }, "YOUR-KEY-GOES-HERE").decode('utf-8')
            }
        else:
            return {
                "statusCode": 301,
                "message": "LoginFailed"
            }
    except Exception:
        return {
            "statusCode": 301,
            "message": "LoginFailed"
        }
