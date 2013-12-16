import requests
from urllib import urlencode


class APIError(Exception):
    pass


class AuthError(APIError):
    pass


class Client(object):
    BASE_URI = 'https://api.put.io/v2'

    def __init__(self, client_id=None, client_token=None, client_secret=None,
        redirect_uri=None, oauth_token=None):
        self.client_id = client_id
        self.client_token = client_token
        self.client_secret = client_secret 
        self.redirect_uri = redirect_uri
        self.oauth_token = oauth_token

    def get_authenticate_url(self):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri
        }

        return '%s/oauth2/authenticate?%s' % (self.BASE_URI,
            urlencode(params))

    def get_access_token(self, code, grant_type='authorization_code'):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': grant_type,
            'code': code
        }

        resp = requests.get('%s/oauth2/access_token' % self.BASE_URI,
            params=params)

        if resp.status_code == requests.codes.ok:
            data = resp.json()
            return data['access_token']
        else:
            raise AuthError("Error granting %s on code %s. (#%s)" % (
                grant_type, code, resp.status_code))

    def list_files(self, parent_id=0):
        params = {
            'parent_id': parent_id,
            'oauth_token': self.oauth_token
        }

        resp = requests.get('%s/files/list' % self.BASE_URI, params=params,
            headers={'Accept': 'application/json'})
        if resp.status_code == requests.codes.ok:
            return resp.json()
        else:
            raise APIError("Could not list files in %s. (#%s)" % (parent_id,
                resp.status_code))

    def search_files(self, keyword, query=0, page_no=0, shared_from='me',
        file_type='all', file_ext='all', timeframe='all'):
        uri = '%s/files/search/%s/page/%s' % (self.BASE_URI, query, page_no)
        params = {
            'keyword': keyword,
            'from': shared_from,
            'type': file_type,
            'ext': file_ext,
            'time': timeframe,
            'oauth_token': self.oauth_token
        }

        resp = requests.get(uri, params=params)
        if resp.status_code == requests.codes.ok:
            return resp.json()
        else:
            raise APIError("Could not find files. (#%s)" % resp.status_code)

    def upload_file(self, path_to_file, filename=None, parent_id=0):
        resp = requests.post('%s/files/upload' % self.BASE_URI,
            files={'file': open(path_to_file, 'rb')},
            params={'oauth_token': self.oauth_token})

        if resp.status_code == requests.codes.ok:
            return resp.json()
        else:
            raise APIError("Could not upload %s. (#%s)" % (path_to_file,
                resp.status_code))
