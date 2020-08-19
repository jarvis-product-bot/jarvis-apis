from models import TrelloCredentials, GithubCredentials
from config import validateToken
import json
import jwt
from time import time
from config import CLIENT_KEY, CLIENT_SECRET


def generate_jwt():
    return {
        "statusCode": 200,
        "token": "Bearer "+jwt.encode(
            {
                "aud": None,
                "iss": CLIENT_KEY,
                "exp": int(time()) + 90 * 86400,
                "iat": int(time())
            }, CLIENT_SECRET
        ).decode('utf-8')
    }


def listIntegrations(token):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    data = {
        "trello_creds": data["trello_creds"],
        "travis_creds": data["travis_creds"],
        "github_creds": data["github_creds"],
        "confluence_url": data["confluence_url"],
        "email": data["email"],
        "zoom": generate_jwt()
    }
    return {
        "statusCode": 200,
        "data": data
    }


def createIntegrations(token, data):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    if data.get("trello", False):
        trello = TrelloCredentials(
            trelloAPIkey=data["trello"]["apikey"],
            trelloAPISecret=data["trello"]["apisecret"],
            board=data["trello"]["board"]
        )
        tokenValidator[1].update(set__trello_creds=trello)
    if data.get("github", False):
        github = GithubCredentials(
            git_username=data["github"]["username"],
            git_personal_token=data["github"]["personal_token"],
            org_name=data["github"]["orgname"]
        )
        tokenValidator[1].update(set__github_creds=github)
    if data.get("confluence", False):
        pass
    if data.get("travis", False):
        tokenValidator[1].update(set__travis_creds=data["travis"]["apikey"])
    return {
        "statusCode": 200,
        "messages": "Integrations Created/Updated Successfully"
    }


def updateIntegrations(token, data):
    return createIntegrations(token, data)
