from __future__ import annotations

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.config import settings

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets',
]


def _creds():
    return service_account.Credentials.from_service_account_file(settings.google_service_account_file, scopes=SCOPES)


def upload_to_drive(local_file: str, mime_type: str = 'video/mp4') -> str:
    drive = build('drive', 'v3', credentials=_creds())
    metadata = {'name': local_file.split('/')[-1], 'parents': [settings.google_drive_folder_id]}
    media = MediaFileUpload(local_file, mimetype=mime_type)
    uploaded = drive.files().create(body=metadata, media_body=media, fields='id').execute()
    return uploaded['id']


def append_sheet_row(values: list[str]) -> None:
    sheets = build('sheets', 'v4', credentials=_creds())
    sheets.spreadsheets().values().append(
        spreadsheetId=settings.google_sheets_id,
        range='A1',
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': [values]},
    ).execute()
