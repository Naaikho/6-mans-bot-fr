import os, sys
from os import path
import requests

# trn tracker api:
#  link: https://api.tracker.gg/api/v2/rocket-league/standard/profile/{platform}/{id}
#   !!! need javascript !!! 

RANK_URL = "http://api.yannismate.de/rank/{}/{}?playlists=ranked_3v3&hideDiv=true"

while 1:
    PF = input("Platform: ")
    ID = input("account id: ")

    r = requests.get(RANK_URL.format(PF, ID))

    print(r.text)