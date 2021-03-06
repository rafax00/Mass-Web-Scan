import queue
import requests
import argparse
import urllib3
from ZeroXRequests import RequestUtils
import sys
import threading
from ZeroXRequests import RawRequests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Options():
    url = queue.Queue()
    headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
    proxy = {}
    stop_threads = False
    body = ""
    to_scan = 0
    scanned = 0

parser = argparse.ArgumentParser()
parser.add_argument("urls_file")
parser.add_argument("-t", dest="threads", default=5, help="Set threads number")
parser.add_argument("-v", dest="verify", action="store_true", help="Verify SSL")
parser.add_argument("-r", dest="redirect", action="store_true", help="Allow redirects")
parser.add_argument("-proxy", dest="proxy", default={}, help="Set proxy")
parser.add_argument("-method", dest="method", default="GET", help="Set request method")
parser.add_argument("-body", dest="body", default="", help="Set request body (file)")
parser.add_argument("-add-url", dest="end_of_url", default="", help="Add string to the end of the url")
parser.add_argument("-headers", nargs="+", dest="headers", default={}, help="Set request headers")
parser.add_argument("-timeout", dest="timeout", default=8, help="Set request timeout")
args = parser.parse_args()

str_proxy = args.proxy
urls_file = args.urls_file
threads = int(args.threads)
verify = args.verify
redirect = args.redirect
end_of_url = args.end_of_url
timeout = int(args.timeout)
method = str(args.method)
body = args.body
headers = args.headers

def load_vars():
    Options.proxy = {"http": str_proxy, "https": str_proxy}

    final_headers = {}
    for header in headers:
        splited_header = header.split(": ")
        var = splited_header[0]
        value = ""
        for i in range(1, len(splited_header)):
            if i == len(splited_header)-1:
                value += splited_header[i]
            else:
                value += splited_header[i] + ": "

            final_headers.update({var: value})

    Options.headers.update(final_headers)

    if body != "":
        Options.body = read_file(body, "string")

def read_file(name, type):
    try:
        final = []
        file = open(name, "r", encoding="latin1")
        if type == "list":
            data = file.readlines()
        else:
            data = file.read()

        file.close()

        if type == "list":
            for line in data:
                final.append(line.replace("\n", ""))

            return final
        else:
            return data
    except Exception as error:
        print(error)
        exit(0)

def make_request(url, headers):
    try:
        private_session = requests.Session()

        if len(body) > 0:
            prepped = requests.Request(method, url, data=Options.body, headers=Options.headers).prepare()
        else:
            prepped = requests.Request(method, url, headers=headers).prepare()

        for key, value in headers.items():
            prepped.headers[key] = value

        req = private_session.send(prepped, verify=verify, timeout=timeout, allow_redirects=redirect, proxies=Options.proxy)

        return req
    except Exception as error:
        error = str(error)
        #print(error)

def progressBar():
    try:
        Options.scanned += 1
        sys.stdout.flush()
        sys.stdout.write("[")
        sys.stdout.write(str(Options.scanned) + "/" + str(Options.to_scan))
        sys.stdout.write("]\r")
    except Exception as error:
        print(error)

def get_domain_from_subdomain(subdomain):
    splited = subdomain.split(".")
    rest = ""
    for i in range(0, len(splited)):
        if i >= len(splited)-2:
            if i == len(splited)-1:
                rest += splited[i]
            else:
                rest += splited[i] + "."

    return rest

def load_urls():
    urls = read_file(urls_file, "list")
    Options.to_scan = len(urls)
    for url in urls:
        if (not url.startswith("http://")) and (not url.startswith("https://")):
            url = "https://" + url
        Options.url.put(url + end_of_url)
    Options.url.put("exit")

def main():
    load_vars()
    load_urls()

    for i in range(0, threads):
        thread = threading.Thread(target=start)
        thread.start()

def RequestProxy(url):
    #### ADD Your code Here
    req = make_request(url, Options.headers)
    if req != None:  
        for key, value in req.headers.items():
            if key.lower() == "content-type" and "html" in value.lower():
                if '<"1337' in req.text:
                    print('[*][XSS] ' + url)
       
def start():
    while True:
        if Options.stop_threads:
            exit(0)
        url = Options.url.get()
        if url == "exit":
            Options.stop_threads = True
            exit(0)

        RequestProxy(url)

        progressBar()


main()
