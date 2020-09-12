import requests
import json


class riotData:

    def __init__(self, RIOT_API_CREDENCIAL, RIOT_API_URL_RANK, RIOT_API_URL_SUMMONER, RIOT_API_URL_MATCHES, RIOT_API_URL_MATCHES_DETAIL ):        
        self.RIOT_API_CREDENCIAL = RIOT_API_CREDENCIAL
        self.RIOT_API_URL_RANK = RIOT_API_URL_RANK
        self.RIOT_API_URL_SUMMONER = RIOT_API_URL_SUMMONER 
        self.RIOT_API_URL_MATCHES = RIOT_API_URL_MATCHES
        self.RIOT_API_URL_MATCHES_DETAIL = RIOT_API_URL_MATCHES_DETAIL

    def getSummonerAccountDetail(self, item):        
        response = requests.get("{}{}".format(self.RIOT_API_URL_SUMMONER, item['summonerId']) , headers={ "X-Riot-Token": self.RIOT_API_CREDENCIAL } )
        if (response.status_code == 200):            
            return response.json()
        else:
            print(f"Error Message: " + response.raise_for_status())
            getSummonerAccountDetail(item)

    def getAllSummoners(self):        
        return json.loads(requests.get(self.RIOT_API_URL_RANK, headers={ "X-Riot-Token": self.RIOT_API_CREDENCIAL }).text)

    def getMatchesOfSummoner(self, accountId, begin = 0, end = 100, listResult = []):
        response = requests.get(f"{self.RIOT_API_URL_MATCHES}{accountId}?endIndex={end}&beginIndex={begin}" , headers={ "X-Riot-Token": self.RIOT_API_CREDENCIAL } )

        try:
            if (response.status_code == 200): 
                temp =  response.json()

                matches = temp['totalGames']
                begin = temp['startIndex']
                end = temp['endIndex']
                listResult.extend(temp['matches'])

                if end == matches:
                    return listResult[0]
        
                else:
                    matches = temp['totalGames']
                    begin = temp['endIndex']
                    end = temp['totalGames'] if (end + 100) > temp['totalGames'] else end + 100            

                    return self.getMatchesOfSummoner(accountId, begin, end,listResult)
            else:
                print(f"Error Message: " + response.raise_for_status())
                self.getMatchesOfSummoner(accountId, begin, end, listResult)
        except NameError:
            print(f"Error Message: " + NameError)
            self.getMatchesOfSummoner(accountId, begin, end, listResult)

    def getDetailMatches(self, item): 
        response = requests.get(self.RIOT_API_URL_MATCHES_DETAIL + str(item['gameId']) , headers={ "X-Riot-Token": self.RIOT_API_CREDENCIAL } )
        if (response.status_code == 200): 
            temp = response.json()

            retorno = {}
            retorno['teams'] = temp['teams']

            temp['teams'][0]['bans'].extend(temp['teams'][1]['bans'])
            retorno['bans'] = temp['teams'][0]['bans']
            
                
            retorno['picks'] = {**temp['participants'][0], **temp['participants'][1]}
            retorno['stats'] = {**temp['participants'][0]['stats'], **temp['participants'][1]['stats']}

            item['teams'] = retorno['teams']
            item['bans'] = retorno['bans']
            item['picks'] = retorno['picks']
            item['stats'] = retorno['stats']


            return item
        else:
            print(f"Error Message: " + response.raise_for_status())
            getDetailMatches(item)
        
