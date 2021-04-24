
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
public_session = requests.Session()

def calculate_content_lentgh(body):
    return len(body)

def get_url_port(url):
    scheme = get_scheme_from_url(url)
    splited_host = get_host_from_url(url).split(":")
    port = ""

    if "https://" == scheme:
        port = "443"
    elif "http://" == scheme:
        port = "80"

    if len(splited_host) > 1:
        port = splited_host[1]

    return port

def get_path_from_url(url):
    host = get_host_from_url(url)
    scheme = get_scheme_from_url(url)

    url_base = scheme + host
    path = "/"
    splited_url = url.split(url_base)
    if len(splited_url) > 1:
        path = splited_url[1]
    if path == "":
        path = "/"
    return path

def get_host_from_url(url):
    try:
        host = url.split("://")[1].split("/")[0].split("?")[0]

        return host
    except Exception as error:
        print(str(error) + " ==> " + url)
        return "www.google.com"

def calculate_encoded_data(data):
    data = data.replace("\r\n", "rc")
    return str(hex(len(data)))[2:]

def make_request_public_session(url, method, headers, body):
    try:
        if len(body) > 0:
            prepped = requests.Request(method, url, data=body, headers=headers).prepare()
        else:
            prepped = requests.Request(method, url, headers=headers).prepare()

        req = public_session.send(prepped, verify=False, timeout=5, allow_redirects=False)

        return req
    except Exception as error:
        if Configurations.General.debug:
            exception(error)

def get_scheme_from_url(url):
    try:
        return url.split("://")[0] + "://"
    except Exception as error:
        pass

def make_request_unique_session(url, method, headers, body):
    try:
        private_session = requests.Session()
        if len(body) > 0:
            prepped = requests.Request(method, url, data=body, headers=headers).prepare()
        else:
            prepped = requests.Request(method, url, headers=headers).prepare()

        prepped.headers["Content-length"] = headers["Content-Length"]
        req = private_session.send(prepped, verify=False, timeout=10, allow_redirects=False)

        return req
    except Exception as error:
        pass

def create_raw_request(url, method, headers, body):
    has_host = False
    raw_request = method + " " + get_path_from_url(url) + " HTTP/1.1\r\n"
    for key, value in headers.items():
        if key.lower() == "host":
            has_host = True
        raw_request += key + ": " + value + "\r\n"

    if not has_host:
        raw_request += "Host: " + get_host_from_url(url) + "\r\n"

    raw_request += "\r\n"

    raw_request += body

    return raw_request