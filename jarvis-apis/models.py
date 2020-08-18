from mongoengine import Document, StringField, EmailField, URLField, BinaryField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField


class TrelloCredentials(EmbeddedDocument):
    trelloAPIkey = StringField(required=True, default="")
    trelloAPISecret = StringField(required=True, default="")
    board = StringField(required=True, default="")


class GithubCredentials(EmbeddedDocument):
    git_username = StringField(required=True, default="")
    git_personal_token = StringField(required=True, default="")
    org_name = StringField(required=True, default="")


class User(Document):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    company_name = StringField(required=True)
    company_url =  URLField(required=True, unique=True)
    password =  BinaryField(required=True)
    github_creds = EmbeddedDocumentField(GithubCredentials)
    confluence_url = StringField(required=True, default="")
    travis_creds = StringField(required=True, default="")
    trello_creds = EmbeddedDocumentField(TrelloCredentials)