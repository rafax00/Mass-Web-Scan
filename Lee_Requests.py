import socket
import RequestUtils
import ssl

line_separator = "\r\n"

def check_ssl(scheme):
    if scheme == "https://":
        return True
    else:
        return False

def send(url, method, headers, body, timeout):
    try:
        host = RequestUtils.get_host_from_url(url)
        port = RequestUtils.get_url_port(url)
        raw_request = build_request(url, method, headers, body, host)
        use_ssl = check_ssl(RequestUtils.get_scheme_from_url(url))

        response = send_raw(raw_request, port, host, timeout, use_ssl)

        if response is not None:
            res = make_object(response)
            if res.status_code == 0:
                res = None
        else:
            res = None

        return res
    except Exception as error:
        print(error)

def send_raw(raw_request, port, host, timeout, use_ssl):
    try:
        if use_ssl:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_default_certs()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            w_socket = context.wrap_socket(s, server_hostname=host)
            w_socket.settimeout(timeout)
            w_socket.connect((host, port))
        else:
            w_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            w_socket.settimeout(timeout)
            w_socket.connect((host, port))

        w_socket.send(bytes(raw_request.encode()))
        data = w_socket.recv(4096).decode("latin1")
        w_socket.close()

        return data
    except Exception as error:
        return None

def make_object(raw_response):
    class response():
        status_code = 0
        text = ""
        header = ""
        raw = ""

    splited_response = raw_response.split(line_separator + line_separator)

    headers = splited_response[0]
    if len(splited_response) > 1:
        text = splited_response[1]
    else:
        text = ""
    splited_headers = headers.split(" ")

    status_code = 0
    if len(splited_headers) > 1:
        status_code = int(splited_headers[1])

    response.status_code = status_code
    response.raw = raw_response
    response.text = text
    response.header = headers

    return response


def build_request(url, method, headers, body, host):
    has_host = False
    has_content_length = False

    path = RequestUtils.get_path_from_url(url)

    raw_request = method.upper() + " " + path + " HTTP/1.1" + line_separator

    for key, value in headers.items():
        if key.lower() == "host":
            has_host = True
        if "content-length" in key.lower():
            has_content_length = True
        raw_request += key + ": " + value + line_separator

    if not has_host:
        raw_request += "Host: " + host + line_separator

    if len(body) > 0:
        if not has_content_length:
            raw_request += "Content-Length: " + str(RequestUtils.calculate_content_lentgh(body)) + line_separator
        raw_request += line_separator
        raw_request += body
    else:
        raw_request += line_separator

    return raw_request