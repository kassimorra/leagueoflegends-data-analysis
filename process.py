##import all libraries

import requests
from neo4j import GraphDatabase
import json 
from time import sleep 
from riot import riotData


##setup
RIOT_API_CREDENCIAL = open('riotCredential', 'r') .readlines()[0]
RIOT_API_URL_RANK = "https://br1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
RIOT_API_URL_SUMMONER = "https://br1.api.riotgames.com/lol/summoner/v4/summoners/"
RIOT_API_URL_MATCHES = "https://br1.api.riotgames.com/lol/match/v4/matchlists/by-account/"
RIOT_API_URL_MATCHES_DETAIL = "https://br1.api.riotgames.com/lol/match/v4/matches/"

#inicializa a abstração da interface da Riot
rData = riotData(RIOT_API_CREDENCIAL = RIOT_API_CREDENCIAL, RIOT_API_URL_RANK = RIOT_API_URL_RANK, RIOT_API_URL_SUMMONER = RIOT_API_URL_SUMMONER, RIOT_API_URL_MATCHES = RIOT_API_URL_MATCHES)

#conecta no Neo4J
uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))


##apaga todo o conteúdo do Neo4J
with driver.session() as session:
    session.run("match (n) detach delete n")


##processa a informação
summoners = rData.getAllSummoners()

##pega todos os invocadores
for summoner in summoners['entries']:    
    with driver.session() as session:        
        session.run("create (:summoner{{id:'{}', name:'{}', vpl:{}, wins:{}, losses:{}}})".format( summoner['summonerId'], summoner['summonerName'], summoner['leaguePoints'], summoner['wins'], summoner['losses']))

    ##atualiza com as informações dos ID´s das contas
    resultAccountDetail = rData.getSummonerAccountDetail(summoner)
    print("{} - {}".format(summoner['summonerId'], summoner['summonerName']))
    with driver.session() as session:
        session.run("match (a:summoner) where a.id = '{}'  set a.puuid = '{}', a.accountId = '{}', a.summonerLevel = {}".format(summoner['summonerId'], resultAccountDetail['puuid'], resultAccountDetail['accountId'], resultAccountDetail['summonerLevel']))

    ##captura os dados das partidas que eles participaram
    resultMatches = rData.getMatchesOfSummoner(accountId = resultAccountDetail['accountId'], begin = 0, end = 100, listResult=[])

    for match in resultMatches:
        with driver.session() as session:

            session.run(f"merge (m:Match {{id: {match['gameId']}}}) ")    

            session.run(f"merge (s:Season {{name: {match['season']}}}) ")            

            session.run(f"match (m:Match {{ id = {match['gameId']} }}), (s:Season {{ name = '{match['season']}') create (m)-[:TEMPORADA]->(s)")            
  

##Encerra a conexão com o banco
driver.close()