import urllib.request
import urllib.error
import http.client
import json
from threading import Thread
from os import mkdir, listdir
from os.path import exists
import os.path
from time import sleep

ipinfo_io = 'https://ipinfo.io/{0}'

def whois(url, addr):
  url = url.format(addr)
  
  try:
    (path, msg) = urllib.request.urlretrieve(url)
  except urllib.error.HTTPError:
    return None
  
  with open(path) as F:
    parsed = json.loads(F.read())
    result = [
      parsed['ip'],
      parsed['country'] if 'country' in parsed else 'undefined',
      parsed['region'] if 'region' in parsed else 'undefined',
      parsed['org'] if 'org' in parsed else 'undefined'
    ]
    return ','.join(result)


class Loader(Thread):
  def __init__(self, url, addr):
    Thread.__init__(self)
    self.url = url
    self.addr = addr

  def run(self):
    data = whois(self.url, self.addr)
    with open('./csv/{0}.csv'.format(self.addr), 'w+') as F:
      if data is None:
        # i think that now they consider that I ddos them
        # and they refused connection for a while
        print('data is None for {0}'.format(self.addr))
      else:
        F.write(data)
    # it means that the job is over
    loaders.append(self.addr)

def concat(output, files):
  with open(output, 'a+') as out:
    for filename in files:
      with open(filename, 'r+') as F:
        out.write(F.read() + "\n")

loaders = []

with open('./ips.txt') as F:
  if not exists('./csv'):
    mkdir('./csv')

  ips = F.readlines()

  for ip in ips:
    if len(ip) > 4 and ip[-1] == '\n':
        ip = ip[0:-1]
    thread = Loader(ipinfo_io, ip)
    thread.start()
  
  while True:
    sleep(.1)
    if len(loaders) == len(ips):
      # concat('./result.csv', listdir('./csv'))
      for i in range(0, len(loaders)):
        loaders[i] = './csv/{0}.csv'.format(loaders[i])
      concat('./result.csv', loaders)
      break
  