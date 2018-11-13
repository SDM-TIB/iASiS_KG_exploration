#!/usr/bin/env python3
#
# Description: POST service for exploration of
# data of Lung Cancer in the iASiS KG.
#

import sys
import os
from flask import Flask, abort, request, make_response
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#handler = logging.StreamHandler()
#handler.setLevel(logging.INFO)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
#logger.addHandler(handler)

LIMIT=10

KG="http://lxz15234:4141/sparql"
#KG = os.environ["IASISKG_ENDPOINT"]
#KG="http://10.114.113.14:7171/sparql"
EMPTY_JSON = "{}"

app = Flask(__name__)

############################
#
# Query constants
#
############################



OPENP = "("
CLOSEP = ")"
FILTER = 'FILTER'
CLOSE = "}"
NEWLINE = "\n"
DOT = '.'
SPC = " "
COMA = ","
IN = "in"
VAR = "?"
ANNT = "<http://project-iasis.eu/Annotation/"
GT = ">"
CLOSE_RANK= "} GROUP BY ?idf ORDER BY DESC (?score)"

QUERY_PUBLICATIONS_RANKED ="""
SELECT DISTINCT  ?idf COUNT(?c) as ?score SAMPLE(?title) as ?title SAMPLE(?author) as ?author SAMPLE(?journal) as ?journal SAMPLE(?year) as ?year  WHERE {
                            ?s a <http://project-iasis.eu/vocab/Publication>.
                            ?s <http://project-iasis.eu/vocab/title> ?title.
                            ?s <http://project-iasis.eu/vocab/author> ?author.
                            ?s <http://project-iasis.eu/vocab/journal> ?journal.
                            ?s <http://project-iasis.eu/vocab/year> ?year.
                            ?o <http://project-iasis.eu/vocab/annotates>  ?s.
                            ?o <http://project-iasis.eu/vocab/hasAnnotation> ?a.
                            ?o <http://project-iasis.eu/vocab/confidence>  ?c.
                            ?o a <http://project-iasis.eu/vocab/HAS_TOPIC> .
                            ?s <http://project-iasis.eu/vocab/pubmedID> ?idf.
"""

############################
#
# Query generation
#
############################


def execute_query(query):
    #logger.info("Query:" + str(query))
    #logger.info("EndPoint:" + str(KG))
    sparql_ins = SPARQLWrapper(KG)
    sparql_ins.setQuery(query)
    #logger.info("Waiting for the SPARQL Endpoint")
    sparql_ins.setReturnFormat(JSON)
    #print(qresults)
    return sparql_ins.query().convert()['results']['bindings']

def build_query_with_cuis(cuis):
    query=QUERY_PUBLICATIONS_RANKED
    #print(cuis)
    query+="FILTER(?a in ("
    for cui in cuis:
        #print(cui)
        query+="<http://project-iasis.eu/Annotation/"+cui+">,"
    query=query[:-1]
    query+="))} GROUP BY ?idf ORDER BY DESC (?score) LIMIT "+str(LIMIT)
    return query
    

############################
#
# Processing results
#
############################

def get_publications_results(qresults):
    result = {}
    for cur_result in qresults:
        pub_dicc = {}
        pub_id = cur_result["id"]["value"]
        pub_dicc["title"] = cur_result["title"]["value"]
        pub_dicc["author"] = cur_result["author"]["value"]
        pub_dicc["year"] = cur_result["year"]["value"]
        pub_dicc["journal"] = cur_result["journal"]["value"]
        result[pub_id] = pub_dicc
        #print((pub_title, pub_author, pub_year, pub_journal))
    return result 



def get_publications_ranked_result(qresults, n, limit):
    results = []
    cont = 0
    for cur_result in qresults:
        if (cont >= limit):
            return results
        pub_id = cur_result["idf"]["value"]
        pub_score = cur_result["score"]["value"]
        results.append((pub_id,  int(pub_score)/n)) 
        cont += 1
    return results

def get_publications_ranked_data(lcuis, limit):
    #print("CUIS ", lcuis)
    query = build_query_with_cuis(lcuis)
    qresults = execute_query(query)
    #logger.info("Number of publications ranked: " + str(len(qresults)))
    #results = get_publications_ranked_result(qresults, len(lcuis), limit)
    #print(results)
    return qresults


def proccesing_response(input_dicc, limit, ltypes):
    allpubs = []
    for elem in input_dicc:
        lcuis = input_dicc[elem]
        number_cuis=len(lcuis)
        #results_pub = get_publication_data(lcuis)
        results_pub_ranked = get_publications_ranked_data(lcuis, limit)
        codicc = {}
        codicc['parameter'] = elem

        if ('sideEffects' in ltypes):
            codicc['sideEffects'] = []
        
        if ('drugInteractions' in ltypes):
            codicc['drugInteractions'] = []

        if ('publications' in ltypes):
            pubs = []
            for result in results_pub_ranked:
                pub1 = {}
                pub1['title'] =  result["title"]["value"]
                pub1['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/"+result["idf"]["value"]
                pub1['author'] = result['author']["value"]
                pub1['journal'] = result['journal']["value"]
                pub1['year'] = result["year"]["value"]
                pub1['score'] = int(result["score"]["value"])/number_cuis
                pubs.append(pub1)
                
            codicc['publications'] = pubs
            allpubs.append(codicc)
    return allpubs



def proccesing_list_types(ltype):
    ltype = ltype.replace("[", "")
    ltype = ltype.replace("]", "")
    ltype = ltype.replace(" ", "")
    ltype = ltype.split(",")
    return ltype 

@app.route('/lc_exploration', methods=['POST'])
def run_exploration_api():
    if (not request.json):
        abort(400)
    if 'limit' in request.args:
        limit = int(request.args['limit'])
    else:
        limit = LIMIT
    typed = request.args['type']
    ltypes = proccesing_list_types(typed)
    input_list = request.json
    if len(input_list) == 0:
        logger.info("Error in the input format")
        r = "{results: 'Error in the input format'}"
    else:
        if len(ltypes) == 0:
            abort(400)
        if ('publications' not in ltypes) and ('sideEffects' not in ltypes) and ('drugInteractions' not in ltypes) and ('drugs' not in ltypes) and ('genes' not in ltypes) and ('mutations' not in ltypes):
            abort(400)
        response = proccesing_response(input_list, limit, ltypes)
        r = json.dumps(response, indent=4)            
    logger.info("Sending the results: ")
    response = make_response(r, 200)
    response.mimetype = "application/json"
    return response

#def run_service():
    #app.run(debug=True)

def main(*args):
    if len(args) == 1:
        myhost = args[0]
    else:
        myhost = "0.0.0.0"
    app.run(debug=False, host=myhost)
    
if __name__ == '__main__':
     main(*sys.argv[1:])
