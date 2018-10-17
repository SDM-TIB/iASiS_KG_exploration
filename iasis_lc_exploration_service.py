#!/usr/bin/env python3
#
# Description: POST service for exploration of
# data of Lung Cancer in the iASiS KG.
#

import sys
import os
from flask import Flask, jsonify, abort, make_response, request, send_from_directory, send_file, make_response
import json
import shutil
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

LIMIT=3

#KG="http://194.95.157.198:11230/sparql"
KG = os.environ["IASISKG_ENDPOINT"]
#KG="http://node2.research.tib.eu:7171/sparql"
EMPTY_JSON = "{}"

app = Flask(__name__)

############################
#
# Query constants
#
############################

QUERY_PUBLICATIONS ="""
    SELECT DISTINCT  ?id ?title ?author ?year ?journal  WHERE {?s a <http://project-iasis.eu/vocab/Annotation>.
                            ?o <http://project-iasis.eu/vocab/hasAnnotation>  ?s.
                            ?o <http://project-iasis.eu/vocab/annotates> ?p.
                            ?p <http://project-iasis.eu/vocab/pubmedID> ?id.
                            ?p <http://project-iasis.eu/vocab/title> ?title.
                            ?p <http://project-iasis.eu/vocab/author> ?author.
                            ?p <http://project-iasis.eu/vocab/journal> ?journal.
                            ?p <http://project-iasis.eu/vocab/year> ?year.
"""

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
CLOSE_RANK= "} GROUP BY ?idf ORDER BY DESC (?C)"

QUERY_PUBLICATIONS_RANKED ="""
SELECT DISTINCT  ?idf COUNT(?c) as ?C WHERE {
                            ?s a <http://project-iasis.eu/vocab/Publication>.
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

def query_publications_ranked(lcuis):
    query = QUERY_PUBLICATIONS_RANKED + get_publications_filter(lcuis, "a") + NEWLINE + CLOSE_RANK
    print("Query publications ranked:")
    print(query)
    return query

def get_publications_filter(lcuis, variable):
    fstr = FILTER + OPENP + VAR + variable + SPC + IN + SPC + OPENP
    if len(lcuis) ==  1:
        fstr += ANNT + lcuis[0] + GT + CLOSEP + CLOSEP
        return fstr
    for cui in lcuis[:-1]:
        fstr += ANNT + cui + GT + COMA + SPC 
    fstr += ANNT + lcuis[-1] + GT + CLOSEP + CLOSEP 
    print(fstr)
    return fstr

def get_query_publication(lcuis):
    query = QUERY_PUBLICATIONS + get_publications_filter(lcuis, "s") + NEWLINE + CLOSE
    print("Query:")
    print(query)
    return query

def sendSPARQL(sparql_ins, origin_query, num_paging, len_max):
    cur_offset = 0
    num_paged_result = sys.maxsize
    list_result = []
    while (num_paged_result >= num_paging and cur_offset < len_max):
        cur_query = origin_query + "LIMIT"+ " " + str(num_paging) + " " + "OFFSET" + " " +  str(cur_offset)
        sparql_ins.setQuery(cur_query)
        sparql_ins.setReturnFormat(JSON)
        results = sparql_ins.query().convert()
        cur_list_result = results["results"]["bindings"]
        list_result = list_result + cur_list_result
        num_paged_result = len(cur_list_result)
        cur_offset = cur_offset + num_paging
    return list_result

def execute_query(query):
    logger.info("Query:" + str(query))
    logger.info("EndPoint:" + str(KG))
    sparql_ins = SPARQLWrapper(KG)
    logger.info("Waiting for the SPARQL Endpoint")
    qresults = sendSPARQL(sparql_ins=sparql_ins, origin_query=query, num_paging=10000, len_max=10000)
    #print(qresults)
    return qresults

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

def get_publication_data(lcuis):
    print("CUIS ",lcuis)
    query = get_query_publication(lcuis)
    qresults = execute_query(query)
    logger.info("Number of publications: " + str(len(qresults)))
    results = get_publications_results(qresults)
    #print(results)
    return results

def get_publications_ranked_result(qresults, n, limit):
    results = []
    cont = 0
    for cur_result in qresults:
        if (cont >= limit):
            return results
        pub_id = cur_result["idf"]["value"]
        pub_score = cur_result["C"]["value"]
        results.append((pub_id,  int(pub_score)/n)) 
        cont += 1
    return results

def get_publications_ranked_data(lcuis, limit):
    print("CUIS ", lcuis)
    query = query_publications_ranked(lcuis)
    qresults = execute_query(query)
    logger.info("Number of publications ranked: " + str(len(qresults)))
    results = get_publications_ranked_result(qresults, len(lcuis), limit)
    #print(results)
    return results

"""
def get_comorbidities_publications():
    codicc = {}
    codicc['parameter'] = 'comorbidities'
    codicc['links'] = {}
    pubs = []
    pub1 = {}
    pub1['title'] = "Spontaneous pulmonary hypertension in genetic mouse models of natural killer cell deficiency"  
    pub1['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/30234375"
    pub1['score'] = "0.65"
    pubs.append(pub1)

    pub2 = {}
    pub2['title'] = "Chronic Hepatitis B Virus Infection and Risk of Dyslipidemia: A Cohort Study"
    pub2['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/30267602"
    pub2['score'] = "0.42"
    pubs.append(pub2)
    codicc['links'] = pubs
    return codicc 

def get_biomarkers_publications():
    codicc = {}
    codicc['parameter'] = 'biomarkers'
    codicc['links'] = {}
    pubs = []
    pub1 = {}
    pub1['title'] = "EGFR and HER3 signaling blockade in invasive mucinous lung adenocarcinoma harboring an NRG1 fusion."  
    pub1['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/30268483"
    pub1['score'] = "0.90"
    pubs.append(pub1)

    pub2 = {}
    pub2['title'] = "High-throughput sequencing reveals distinct genetic features and clinical implications of NSCLC with de novo and acquired EGFR T790M mutation"
    pub2['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/30268462"
    pub2['score'] = "0.72"
    pubs.append(pub2)
    codicc['links'] = pubs
    return codicc 

def get_publications_tumorType():
    codicc = {}
    codicc['parameter'] = 'tumorType'
    codicc['links'] = {}
    pubs = []
    pub1 = {}
    pub1['title'] = "Extra cost of brain metastases (BM) in patients with non-squamous non-small cell lung cancer (NSCLC): a French national hospital database analysis."
    pub1['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/30233822" 
    #pub1['score'] = "0.60"
    pubs.append(pub1)

    pub2 = {}
    pub2['title'] = "Clinical Parameters for Predicting the Survival in Patients with Squamous and Non-squamous-cell NSCLC Receiving PD-1 Inhibitor Therapy."
    pub2['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/30232703"
    #pub2['score'] = "0.22"
    pubs.append(pub2)
    codicc['links'] = pubs
    return codicc 

def proccesing_publications_response(input_dicc):
    pubs = []
    if "comorbidities" in input_dicc:
        copub = get_comorbidities_publications()
        pubs.append(copub)

    if "biomarkers" in input_dicc:
        copub = get_biomarkers_publications()
        pubs.append(copub)

    if 'tumorType'  in input_dicc:
        copub = get_publications_tumorType()
        pubs.append(copub)
    
    return pubs
"""

def processing_biomarkers(lelems):
    cuiList = []
    for e in lelems:
        if e.upper() == "EGFR":
            cuiList.append("C0034802")
        elif e.upper() == "ALK":
            cuiList.append("C1332080")
        elif e.upper() == "ROS1":
            cuiList.append("C0812281")
        else:
            cuiList.append(e.replace(" ", ""))
    return cuiList

def procesing_oncologicalTreatments(lelems):
    cuiList = []
    for e in lelems:
        if e.lower() == "immunotherapy":
            cuiList.append("C0021083")
        elif e.lower() == "chemotherapy":
            cuiList.append("C3665472")
        elif e.lower() == "tki":
            cuiList.append("C3899317")
        elif e.lower() == "antiangiogenic":
            cuiList.append("C0596087")
        elif e.lower() == "radiationtherapy":
            cuiList.append("C0034619")
        elif e.lower() == "surgery":
            cuiList.append("C0543467")
        else:
            cuiList.append(e.replace(" ", ""))
    return cuiList

def proccesing_response(input_dicc, limit, ltypes):
    allpubs = []
    print("Linit: ", limit)
    for elem in input_dicc:
        print("")
        if elem == 'biomarkers':
            lcuis =  processing_biomarkers(input_dicc[elem])
        elif elem == 'oncologicalTreatments':
            lcuis = procesing_oncologicalTreatments(input_dicc[elem])
        else:
            lcuis = [ e.replace(" ", "") for e in input_dicc[elem] ]
        print("Processing: ", elem)
        print("CUIS ", lcuis)
        results_pub = get_publication_data(lcuis)
        results_pub_ranked = get_publications_ranked_data(lcuis, limit)
        codicc = {}
        codicc['parameter'] = elem

        if ('sideEffects' in ltypes):
            codicc['sideEffects'] = []
        
        if ('drugInteractions' in ltypes):
            codicc['drugInteractions'] = []

        if ('publications' in ltypes):
            pubs = []
            for (id_pub, score) in results_pub_ranked:
                pub1 = {}
                if  id_pub in results_pub:
                    pub1['title'] =  results_pub[id_pub]["title"] 
                    pub1['url'] = "https://www.ncbi.nlm.nih.gov/pubmed/"+id_pub
                    pub1['author'] = results_pub[id_pub]['author']
                    pub1['journal'] = results_pub[id_pub]['journal']
                    pub1['year'] = results_pub[id_pub]["year"]
                    pub1['score'] = str(score)    
                    pubs.append(pub1)
                
            codicc['publications'] = pubs
            allpubs.append(codicc)
    return allpubs

"""
def proccesing_side_effects_response(input_list):
    se = []
    drugs = {}
    drugs['parameter'] = 'drugs'
    omeprazol = {}
    omeprazol['omeprazol'] = 'Ritonavir' 
    drugs['sideEffects'] = [omeprazol]
    se.append(drugs)

    drugs = {}
    drugs['parameter'] = 'chemotherapyDrugs'
    omeprazol = {}
    omeprazol['Cisplatin'] = 'Reboxetine' 
    drugs['sideEffects'] = [omeprazol]
    se.append(drugs)
    
    drugs = {}
    drugs['parameter'] = 'tkiDrugs'
    omeprazol = {}
    omeprazol['Erlotinib'] = 'Ofloxacin' 
    drugs['sideEffects'] = [omeprazol]
    se.append(drugs)

    drugs = {}
    drugs['parameter'] = 'immunotherapyDrugs'
    omeprazol = {}
    omeprazol['nivolumab'] = 'Belimumab' 
    drugs['sideEffects'] = [omeprazol]
    se.append(drugs)
    
    return se
"""

def proccesing_list_types(ltype):
    ltype = ltype.replace("[", "")
    ltype = ltype.replace("]", "")
    ltype = ltype.replace(" ", "")
    ltype = ltype.split(",")
    return ltype 

@app.route('/lc_exploration', methods=['POST'])
def run_semep_drug_service():
    if (not request.json):
        abort(400)
    
    endpoint = KG
    print("Number of Arguments", len(request.args))
    print("Input type 1", request.args['type'])
    if 'limit' in request.args:
        limit = int(request.args['limit'])
    else:
        limit = LIMIT
    print("Limit of responses", limit)

    typed = request.args['type']
    ltypes = proccesing_list_types(typed)
    print("List of types ", ltypes)
    
    print("Proccesing input")
    #input_list = processing_input(request.json)
    input_list = request.json
    print(input_list)
    print("Proccesing input done ")
    logger.info("Number of terms analyze: "+ str(len(input_list)))
    logger.info("Hello, this is the IaSiS Lung Cancer Exploration Service")
    #result = get_drug_data(drug, endpoint)
    if len(input_list) == 0:
        logger.info("Error in the input format")
        r = EMPTY_JSON
    else:
        if len(ltypes) == 0:
            abort(400)
        if ('publications' not in ltypes) and ('sideEffects' not in ltypes) and ('drugInteractions' not in ltypes):
            abort(400)
        response = proccesing_response(input_list, limit, ltypes)
        #if typed == 'publications':
        #  print("running publications")
        #lcuis = ["C0001006", "C0001443"]
        #lcuis = ["C0004272", "C0010178", "C0013556", "C0162416"]
        #results_pub = get_publication_data(lcuis)
        #results_pub_ranked = get_publications_ranked_data(lcuis, limit)
            
        # elif typed == 'sideEffects':
        #     pubs = proccesing_side_effects_response(input_list)
        #     print(pubs)
        # else:
        #    EMPTY_JSON
        r = json.dumps(response, indent=4)
                   
    logger.info("Sending the results: ")
    response = make_response(r, 200)
    response.mimetype = "application/javascript"
    return response

def run_service():
    app.run(debug=True)

def main(*args):
    if len(args) == 1:
        myhost = args[0]
    else:
        myhost = "127.0.0.1"
    app.run(debug=True, host=myhost)
    
if __name__ == '__main__':
     main(*sys.argv[1:])
