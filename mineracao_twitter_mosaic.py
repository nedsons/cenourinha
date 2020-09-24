import tweepy
import pandas as pd
import pathlib
import sys
import jsonpickle
import logging
import unicodedata
import numpy
import re
from artchee_o import ArcheeO
from tqdm import tqdm
from owlready2 import sync_reasoner_pellet, base, reasoning
from unidecode import unidecode
import pickle

from pymongo import MongoClient
from processador_texto import processa_texto


sqlite3_filename = "/home/projeto/nedson/project-oc/ontologia/bd_ontology.sqlite3"
ontology_max_individuos = 500


def funcao1(artchee_o_type, count_aux, tweets_marcados, dboc):
    try:
        with artchee_o_type.onto:
            sync_reasoner_pellet(artchee_o_type.big_world,
                                 infer_property_values=True, infer_data_property_values=True, debug=0)
    except base.OwlReadyJavaError as e:
        print('\nNão foi possível aplicar o reasoner\nError: {}'.format(e))
        sys.exit()
    file_out = "/home/projeto/nedson/project-oc/ontologia/artchee-o_pop_{}.owl".format(count_aux)
    saved = artchee_o_type.save_and_close_new_world(file_out)
    if saved:
        print("\nTweets armazenados na ontologia com sucesso!\nAtualizando MongoDB com {} registros..."
              .format(tweets_marcados.__len__()))
        for tweet2 in tweets_marcados:
            dboc[tweet2.grupo_mosaic].update_one({"id_str": tweet2.id_str}, {"$set": {"in_mongodb": True}})
    return saved


def get_qtd_individuos(world):
    y = 0
    for x in world.individuals():
        y = y + 1
    return y, y + ontology_max_individuos


def conecta_tweepy():
    print("Conectando no Twitter...")
    API_KEY = 'wpbveqphO7MdHr5cBC9itioCv'
    API_SECRET = 'c5Bu4DhmSWEwPdPOzEqwAYSMKBsdXmEbMpMLIIxpsfLeHBH833'
    ACCESS_TOKEN = '1193893175607386114-raQQFNDazRTc9FKSPKzrvOa6WrhbbY'
    ACCESS_TOKEN_SECRET = 'aMQq4VIeqe9Rxtysy66vul8XJ9iL5sDlCzQ9GxjAfoQhY'

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET, ACCESS_TOKEN)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    if not api:
        print("Can't Authenticate")
        sys.exit(-1)
    else:
        print("Conexão estabelecida!")
        return api


def get_hastags_query(artchee_o_aux, iri):
    print("Extraindo hashtags da ontologia...")
    with artchee_o_aux.onto:
        lista_ind_keywords = artchee_o_aux.onto.search(
            is_a=artchee_o_aux.onto.Keyword,
            hasGroup=artchee_o_aux.onto.search(
                is_a=artchee_o_aux.onto.MosaicGroup,
                iri=iri))
    aux = []
    query = ''
    for individuo in tqdm(lista_ind_keywords):
        for palavra in individuo.hashtag:
            aux.append(('#' + palavra + ' OR ', individuo.hasWeight[0].weight_value[0]))
    df_aux = pd.DataFrame(aux, columns=["hashtag", "weight"]).sort_values("weight", ascending=False)
    aux1 = 0
    for index, row in df_aux.iterrows():
        if query.__len__() < 490:
            query = query + row.hashtag
        elif query.__len__() > 490:
            aux1 = 1
            while query.__len__() > 490:
                listinha = query.split('OR')
                listinha.pop()
                query = 'OR'.join(listinha)
            break
    if aux1 == 0:
        query = query[:-3]
    return query


def get_groups_query(artchee_o_aux):
    print("Extraindo grupos da ontologia...")
    aux = []
    with artchee_o_aux.onto:
        list_ind_mosaic_group = artchee_o_aux.onto.search(
            is_a=artchee_o_aux.onto.MosaicGroup)
    list_ind_mosaic_group.pop(0)
    for grupo in list_ind_mosaic_group:
        query1 = get_hastags_query(artchee_o_aux, grupo.iri)
        group_dict = {grupo.name: query1}
        aux.append(group_dict)
    return aux


def coleta_tweets(tweepy_api, searchQuery, grupo, max_tweets, mongo_client):
    dboc = mongo_client.dboc
    tweetsPerQry = 100  # this is the max the API permits
    # fName = '/home/projeto/nedson/project-oc/dados/estilos/twitter/tweets-' + grupo + '.txt'  # We'll store the tweets in a text file.
    colecao = dboc["coll_tweets-" + grupo]
    qnt_documentos_ini = colecao.count_documents({})
    # print("Existem {} documentos na coleção de tweets do grupo {}".format(qnt_documentos_ini, grupo))

    # If results from a specific ID onwards are reqd, set since_id to that ID.
    # else default to no lower limit, go as far back as API allows
    sinceId = None

    # If results only below a specific ID are, set max_id to that ID.
    # else default to no upper limit, start from the most recent tweet matching the search query.
    max_id = -1

    tweetCount = 0
    # print("Downloading max {0} tweets".format(maxTweets))
    while tweetCount < max_tweets:
        try:
            if max_id <= 0:
                if not sinceId:
                    new_tweets = tweepy_api.search(searchQuery, count=tweetsPerQry,
                                                   lang='pt', tweet_mode="extended")
                else:
                    new_tweets = tweepy_api.search(searchQuery, count=tweetsPerQry,
                                                   since_id=sinceId, lang='pt', tweet_mode="extended")
            else:
                if not sinceId:
                    new_tweets = tweepy_api.search(searchQuery, count=tweetsPerQry,
                                                   max_id=str(max_id - 1), lang='pt', tweet_mode="extended")
                else:
                    new_tweets = tweepy_api.search(searchQuery, count=tweetsPerQry,
                                                   max_id=str(max_id - 1),
                                                   since_id=sinceId, lang='pt', tweet_mode="extended")
            if not new_tweets:
                print("Não foi encontrado mais nenhum tweet")
                break
            for tweet in new_tweets:
                try:
                    # f.write(jsonpickle.encode(tweet._json, unpicklable=False) +
                    #         '\n')
                    colecao.insert_one(tweet._json)
                except(RuntimeError, TypeError, NameError, Exception) as e:
                    logging.error(e)
                    pass
            tweetCount += len(new_tweets)
            # print("Downloaded {} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            logging.error(e)
            # print("some error : " + str(e))
            break
    qnt_documentos_fim = colecao.count_documents({}) - qnt_documentos_ini
    print("\nForam adicionados {} documentos".format(qnt_documentos_fim))
    print("Downloaded {} tweets".format(tweetCount))


def get_estilos_tweets(mongo_client, tweepy_api, lista_master, quantidade):
    print("\nIniciando mineração dos tweets estilo de vida...")
    for row in tqdm(lista_master):
        grupo = row.keys().__str__().replace("dict_keys(['", '').replace("'])", '')
        query = row.get(grupo)
        coleta_tweets(tweepy_api, query, grupo, quantidade, mongo_client)


def post_tweet(mongo_client, artchee_o_type, df_tweets):
    dboc = mongo_client.dboc
    coll_ontology_state = mongo_client.ontology.state
    dict_ontology_count = coll_ontology_state.find()[0]
    count_aux = dict_ontology_count['actual_state_num']
    tweets_marcados = []
    qtd_individuos_my_world, qtd_individuos_my_world_max = get_qtd_individuos(artchee_o_type.my_world)
    save_state = 0

    print("Iniciando criação de um novo Mundo")
    onto_pop_path = "/home/projeto/nedson/project-oc/ontologia/artchee-o_pop_{}.owl".format(count_aux)
    if pathlib.Path(onto_pop_path).exists():
        sqlite_pop_path = "/home/projeto/nedson/project-oc/ontologia/bd_artchee-o_pop{}.sqlite3".format(count_aux)
        artchee_o_type.create_new_world(onto_pop_path, sqlite_pop_path)
        qtd_individuos_big_world, qtd_individuos_max_big_world = get_qtd_individuos(artchee_o_type.big_world)
    else:
        qtd_individuos_big_world = 0

    for index, tweet in tqdm(df_tweets.iterrows()):
        if qtd_individuos_big_world == 0:
            path_sqlite = "/home/projeto/nedson/project-oc/ontologia/bd_artchee-o_pop_{}.sqlite3".format(count_aux)
            artchee_o_type.create_new_world(artchee_o_type.path_onto, path_sqlite)
        elif qtd_individuos_big_world >= qtd_individuos_my_world:
            save_state = funcao1(artchee_o_type, count_aux, tweets_marcados, dboc)
            print("Iniciando criação de um novo Mundo")
            count_aux = count_aux + 1
            path_sqlite = "/home/projeto/nedson/project-oc/ontologia/bd_artchee-o_pop{}.sqlite3".format(count_aux)
            artchee_o_type.create_new_world(artchee_o_type.path_onto, path_sqlite)
            coll_ontology_state.update_one({}, {"$set": {"actual_state_num": count_aux}})
            tweets_marcados = []
            qtd_individuos_big_world = 0
        with artchee_o_type.onto:
            if tweet.full_text is not numpy.nan:
                tweet_text = tweet.full_text
                # user_id = tweet.user['id_str']
            else:
                tweet_text = tweet.text
                # user_id = tweet.user['id_str']
            nome_tweet = "tweet_" + tweet.id_str
            individuo_tweet = artchee_o_type.onto.Tweet(nome_tweet)
            individuo_tweet.id = [tweet.id_str]
            individuo_tweet.date = [tweet.created_at]
            individuo_tweet.favorite_count = [tweet.favorite_count]
            # individuo_tweet.user_id = [user_id]
            individuo_tweet.processed_text = [processa_texto(tweet_text)]
            individuo_tweet.hashtag = []
            hashtags = tweet.entities['hashtags']
            if hashtags.__len__() > 0:
                for tag in hashtags:
                    individuo_tweet.hashtag.append(unidecode(tag['text'].lower()))
            tweets_marcados.append(tweet)
            qtd_individuos_big_world = qtd_individuos_big_world + 1
    if save_state == 0:
        funcao1(artchee_o_type, count_aux, tweets_marcados, dboc)


def inicia_mineracao(mongo_client, artchee_o_aux):
    tweepy_api = conecta_tweepy()
    lt_queries = get_groups_query(artchee_o_aux)
    get_estilos_tweets(mongo_client, tweepy_api, lt_queries, 1000000)


def get_all_tweets_from_mongo(mongo_client):
    dboc = mongo_client.dboc
    df_tweets = pd.DataFrame()
    print("Pegando tweets do MongoDB...")
    for x in tqdm(dboc.list_collections()):
        colecao = dboc[x['name']]
        if df_tweets.__len__() == 0:
            df_tweets = pd.DataFrame(
                list(colecao.find({"in_mongodb": {"$exists": False}})))
            df_tweets.drop_duplicates(subset="full_text", keep="first")
            df_tweets['grupo_mosaic'] = x['name']
        else:
            df_tweets2 = pd.DataFrame(
                list(colecao.find({"in_mongodb": {"$exists": False}})))
            df_tweets2 = df_tweets2.drop_duplicates(subset="full_text", keep="first")
            df_tweets2['grupo_mosaic'] = x['name']
            df_tweets = df_tweets.append(df_tweets2)
    print("Foram extraídos {} tweets do MongoDB".format(df_tweets.__len__()))
    return df_tweets.sort_values("created_at")


def main():
    reasoning.JAVA_MEMORY = 10000
    logging.basicConfig(filename="logfile.log", level=logging.INFO)

    sqlite3_filename = "/home/projeto/nedson/project-oc/ontologia/bd_artchee-o_tx.sqlite3"
    onto = "/home/projeto/nedson/project-oc/ontologia/artchee-o_tx.owl"
    artchee_o = ArcheeO(sqlite3_filename, onto)

    cliente_mongo = MongoClient()
    # inicia_mineracao(cliente_mongo, artchee_o)
    df_tweets_mosaic = get_all_tweets_from_mongo(cliente_mongo)
    post_tweet(cliente_mongo, artchee_o, df_tweets_mosaic)
    artchee_o.close_base_world()


if __name__ == '__main__':
    main()
    # colecao.update_many({}, {"$unset": {"in_mongodb": True}})
    # post_tweet(ontologia, colecao, 10000, aux)
