import requests
import json


def get_docker_auth_token(auth_url, image_name):
    get_auth_token_payload = {
        'service': 'registry.docker.io',
        'scope': 'repository:library/{}:pull'.format(image_name)
    }

    token_resp = requests.get(auth_url + '/token', params=get_auth_token_payload)
    if not r.status_code == 200:
        print("Error status code: {} returned when trying to get token".format(r.status_code))
        raise Exception("Error: Could not get an auth token!")

    resp_json = token_resp.json()
    return resp_json['token']


def fetch_versions(index_url, token, image_name):
    h = {'Authorization': "Bearer {}".format(token)}
    resp_tags = requests.get('{}/v2/library/{}/tags/list'.format(index_url,
                                                                 image_name),
                     headers=h)
    return resp_tags.json()


def fetch_catalog(index_url, token):
    h = {'Authorization': "Bearer {}".format(token)}
    resp = requests.get('{}/v2/_catalog'.format(index_url),
                     headers=h)
    return resp.json()


if __name__ == "__main__":
    name = "alpine"
    index_url = 'https://index.docker.io'
    auth_url = 'https://auth.docker.io'

    token = get_docker_auth_token(auth_url=auth_url, image_name=name)
    print(token)

    print("Get versions")
    versions = fetch_versions(index_url, token, name)
    print(json.dumps(versions, indent=2))
    print("----")

    print("Get catalog")
    catalog = fetch_catalog(index_url, token)
    print(json.dumps(catalog, indent=2))
