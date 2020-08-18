from models import User
import jwt
import json

def validateToken(token):
    try:
        decoded_token = jwt.decode(
            token,
            "YOUR-KEY-GOES-HERE"
        )["email"]
        user = User.objects.get(email=decoded_token)
        return True, user
    except:
        return False, {
            'statusCode': 401,
            "message": "InvalidCredentials"
        }

def timebuilder(val):
    val = int(val)
    if val < 100:
        return val, "seconds"
    elif val < 3600:
        return val//60, "minutes"
    elif val < 86400:
        return val//3600, "hours"
    else:
        val = val//86400
    if val < 60:
        return val, "days"
    else:
        return val//30, "months"