#!/usr/bin/env python3
#
# Description: POST service for SemEP with drugs
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

KG="http://194.95.157.198:11230/sparql"
#KG = os.environ["IASISKG_ENDPOINT"]

DBPEDIA_ENDPOINT="http://dbpedia.org/sparql"
BIO2RDF_ENDPOINT="http://bio2rdf.org/sparql"
EMPTY_JSON = "{}"

app = Flask(__name__)


#def get_iasis_kg_query(drug):
#    return """SELECT DISTINCT ?o10 WHERE {
#       ?s <http://project-iasis.eu/vocab/mutation_isLocatedIn_transcript> ?o7 .
#       ?s <http://project-iasis.eu/vocab/mutation_somatic_status> 'Confirmed somatic variant' .
#       ?s <http://project-iasis.eu/vocab/mutation_isLocatedIn_gene> <http://project-iasis.eu/Gene/EGFR>.
#       ?s <http://project-iasis.eu/vocab/mutationDescription> 'Substitution - Missense' .
#       ?s <http://project-iasis.eu/vocab/mutation_isLocatedIn_tumor> ?o11 .
#       ?o11 <http://project-iasis.eu/vocab/tumor_origin> 'metastasis' .
#       ?o7 <http://project-iasis.eu/vocab/translates_as> ?o1 .
#       ?s  <http://project-iasis.eu/vocab/mutation_aa> ?o10 .
#       ?o4  <http://project-iasis.eu/vocab/drug_interactsWith_protein> ?o1 . 
#       ?o4 <http://project-iasis.eu/vocab/label> '"""+drug+"""'
#}"""

"""
# Example of proccesing queries

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

def get_iasis_results(qresults, results):
    for cur_result in qresults:
        mutation = cur_result["o10"]["value"]
        #print(mutation)
        dic_add(EFGR, mutation, results)
        
def execute_query(query, end_point):
    logger.info("Query:" + str(query))
    logger.info("EndPoint:" + str(end_point))
    sparql_ins = SPARQLWrapper(end_point)
    logger.info("Waiting for the SPARQL Endpoint")
    qresults = sendSPARQL(sparql_ins=sparql_ins, origin_query=query, num_paging=50000000, len_max=sys.maxsize)
    #print(qresults)
    return qresults
    
def get_drug_data(drug, endpoint):
    results = {}
    # Quering DBpedia
    query = get_dbpedia_query(drug.title())
    qresults = execute_query(query, DBPEDIA_ENDPOINT)
    logger.info("Resutls DBpesia 1"  + str(len(qresults)))
    if len(qresults) != 1:
        logger.info("First query to  DBpedia failed")
        query = get_dbpedia2_query(drug.title())
        qresults = execute_query(query, DBPEDIA_ENDPOINT)
    get_dbpedia_results(qresults, results)
    logger.info("Number of triples DBpedia: " + str(len(qresults)))
    #print(results)

    # Quering Bio2RDF
    if "drugbankID" in results:
        drugbankId = results["drugbankID"]
        if drugbankId != None and drugbankId != "" and drugbankId[:2] == "DB":
            query = get_bio2rdf_query(drugbankId)
            qresults = execute_query(query, BIO2RDF_ENDPOINT)
            logger.info("Number of triples Bio2RDF: " + str(len(qresults)))
            get_bio2df_results(qresults, results)

    # Quering iASiS KG
    query = get_iasis_kg_query(drug.lower())
    #qresults = execute_query(query, IASIS_ENDPOINT)
    qresults = execute_query(query, endpoint)
    logger.info("Number of triples iASiS: " + str(len(qresults)))
    get_iasis_results(qresults, results)

    # Checking the results
    check_results(results)
    print(len(results))
    assert(len(results) == 10)
    print(results)
    return results
"""

def processing_input(json_input):
    result = {}
    
    if 'comorbidities' in json_input:
        comorbidities_list = json_input['comorbidities']
        print("List of comorbidities", comorbidities_list)
        result['comorbidities'] = comorbidities_list
        
    if 'biomarkers' in json_input:
        biomarkers_list = json_input['biomarkers']
        print("List of biomarkers", biomarkers_list)
        result['biomarkers'] = biomarkers_list

    if 'tumorType' in json_input:
        tumorType_list = json_input['tumorType']
        print("tumorType", tumorType_list)
        result['tumorType'] = tumorType_list
        
    if 'drugsGroups' in json_input:
        drugsGroups_list = json_input['drugsGroups']
        print("drugsGroups", drugsGroups_list)
        result['drugsGroups']  = drugsGroups_list
        
    if 'drugs' in json_input:
        drugs_list = json_input['drugs']
        print("List of drugs", drugs_list)
        result['drugs'] =  drugs_list
        
    if 'oncologicalTreatments' in json_input:
        oncologicalTreatments_list = json_input['oncologicalTreatments']
        print("List of oncologicalTreatments", oncologicalTreatments_list)
        result['oncologicalTreatments'] = oncologicalTreatments_list
        
    if "immunotherapyDrugs" in json_input:
        immunotherapy_list = json_input['immunotherapyDrugs']
        print("List of immunotherapyDrugs", immunotherapy_list)
        result["immunotherapyDrugs"] = immunotherapy_list

    if "tkiDrugs" in json_input:
        tki_list = json_input['tkiDrugs']
        print("List of tkiDrugs", tki_list)
        result['tkiDrugs'] = tki_list

    if "chemotherapyDrugs" in json_input:
        chemotherapy_list = json_input['chemotherapyDrugs']
        print("List of chemotherapyDrugs", chemotherapy_list)
        result["chemotherapyDrugs"] = chemotherapy_list
    return result

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
    
@app.route('/iasiskgexploration', methods=['POST'])
def run_semep_drug_service():
    if (not request.json):
        abort(400)
    
    endpoint = KG
    print("Number of Arguments", len(request.args))
    print("Input type 1", request.args['type'])
    print("Limit of responses", request.args['limit'])

    typed = request.args['type']
    limit = request.args['limit']

    print("Proccesing input")
    input_list = processing_input(request.json)
    print(input_list)
    print("Proccesing input done ")
    logger.info("Number of terms analyze: "+ str(len(input_list)))
    logger.info("Hello, this is the IaSiS KG exploration Service")
    #result = get_drug_data(drug, endpoint)
    if len(input_list) == 0:
        logger.info("Error in the input format")
        r = EMPTY_JSON
    else:
        if typed == 'publications':
            pubs = proccesing_publications_response(input_list)
        elif typed == 'sideEffects':
            pubs = proccesing_side_effects_response(input_list)
            print(pubs)
        else:
            EMPTY_JSON
        r = json.dumps(pubs, indent=4)
            
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
