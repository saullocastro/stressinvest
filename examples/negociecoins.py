import base64, hashlib, hmac, md5, random, time, urllib, urllib2, requests

def amx_authorization_header(id, key, url, method='GET', body=None):
    encoded_url = urllib.quote_plus(url).lower()
    method = method.upper()
    content = '' if body == None else base64.b64encode(md5.new(body).digest())
    timestamp = str(int(time.time()))
    nonce = str(random.randint(0, 100000000))
    data = ''.join([id, method, encoded_url, timestamp, nonce, content])
    secret = base64.b64decode(key)
    signature = base64.b64encode(hmac.new(secret, msg=data, digestmod=hashlib.sha256).digest())

    return 'amx %s' % ':'.join([id, signature, nonce, timestamp])


def exchange2(url, result):
    return requests.get(url, headers={'Authorization': result}).text

def exchange(url, result):

    req = urllib2.Request(url, headers={'Authorization': result, 'User-Agent': ''})

    webpage = urllib2.urlopen(req).read()

    return webpage

id1 = 'b316434cb3614165a9aab0234d0ec02f'
key = 'zRR/bYjtBxPEUckHi95iV72fgsUtmtKi6XqTP7j4MlY='
url1 = 'https://broker.negociecoins.com.br/tradeapi/v1/'
method = 'GET'
function = 'user/balance'

urlFinal = ''.join([url1, function])

result2 = amx_authorization_header(id1, key, urlFinal, method, body=None)
print(result2)

print(exchange(str(urlFinal), result2))
