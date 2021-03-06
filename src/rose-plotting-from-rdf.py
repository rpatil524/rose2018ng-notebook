from rdflib import Graph, RDF
from IPython.core.display import display, HTML
import os
import json
import csv
import uuid

from SPARQLWrapper import SPARQLWrapper, SPARQLWrapper2, JSON, JSONLD, CSV, TSV, N3, RDF, RDFXML, TURTLE
import pandas as pds
import itertools

import numpy as np
from plotnine import *


__author__ = 'proccaserra (Philippe Rocca-Serra)'

# author: philippe rocca-serra (philippe.rocca-serra@oerc.ox.ac.uk)
# ontology: http://www.stato-ontology.org


def queryResultToHTMLTable(queryResult):

    HTMLResult = '<table><tr style="color:white;background-color:#43BFC7;font-weight:bold">'
    # print variable names
    for varName in queryResult.vars:
        HTMLResult = HTMLResult + '<td>' + varName + '</td>'
    HTMLResult = HTMLResult + '</tr>'
    # print values from each row
    for row in queryResult:
        HTMLResult = HTMLResult + '<tr>'
        for column in row:
             if column is not "":
                HTMLResult = HTMLResult + '<td>' + str(column) + '</td>'
             else:
                 HTMLResult = HTMLResult + '<td>' + "N/A" + '</td>'

        HTMLResult = HTMLResult + '</tr>'

    HTMLResult = HTMLResult + '</table>'
    display(HTML(HTMLResult))


def get_sparql_variables(results, sparql_wrapper="SPARQLWrapper2"):
    # return results.vars if ("sparqlwrapper2" == sparql_wrapper.lower()) else results['head']['vars']
    return results.vars if ("sparqlwrapper2" == sparql_wrapper.lower()) else results.vars
    # print(results.vars)


def get_sparql_bindings(results, sparql_wrapper="SPARQLWrapper2"):
    return results.bindings if ("sparqlwrapper2" == sparql_wrapper.lower()) else results['results']['bindings']
   

def get_sparql_binding_variable_value(binding, variable, sparql_wrapper="SPARQLWrapper2"):
    return binding[variable] if ("sparqlwrapper2" == sparql_wrapper.lower()) else binding[variable]['value']
   

def make_sparql_dict_list(bindings, variables, sparql_wrapper="SPARQLWrapper2"):
    def binding_value(binding, var): # helper function for returning values
        return get_sparql_binding_variable_value(binding, var, sparql_wrapper) if (var in binding) else None

    dict_list = []  # list to contain dictionaries
    for binding in itertools.chain(bindings):
        values = [binding_value(binding, var) for var in itertools.chain(variables)]
        dict_list.append(dict(zip(variables, values)))

    return dict_list


def make_sparql_df(results, sparql_wrapper="SPARQLWrapper2"):

    # modified from https://github.com/RDFLib/sparqlwrapper/issues/125
  
    variables = get_sparql_variables(results, sparql_wrapper)

    cleaned_variables=[str(var.replace('\\n','')) for var in variables] 

    # print(cleaned_variables)
    bindings = get_sparql_bindings(results, sparql_wrapper)

    # create a list of dictionaries to use as data for dataframe
    data_list = make_sparql_dict_list(bindings, cleaned_variables, sparql_wrapper)
    
    # print(data_list)

    df = pds.DataFrame(data_list) # create dataframe from data list
    df["sample_mean"] = df["sample_mean"].astype("float")

    return df[cleaned_variables] # return dataframe with columns reordered


g = Graph()

g.parse("/Users/philippe/Documents/git/rose2018ng-notebook/data/processed/denovo/rdf/rose-aroma-ng-06-2018-full.ttl", format="n3")
# g.parse("./data/processed/denovo/rdf/rose-aroma-ng-06-2018-full.ttl", format="n3")

print(g)

get_idv_and_levels = g.query(
"""
PREFIX stato: <http://purl.obolibrary.org/obo/STATO_>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ncbitax: <http://purl.obolibrary.org/obo/NCBITaxon_>
PREFIX has_part: <http://purl.obolibrary.org/obo/BFO_0000051>
SELECT DISTINCT
             ?Predictor
             ?PredictorLevel
             WHERE {
                ?var a stato:0000087 ;
                     rdfs:label ?Predictor ;
                     has_part: ?value .
                ?value rdfs:label ?PredictorLevel .
                 }
"""
)

# for row in get_idv_and_levels:
#     print("%s knows %s" % row)

queryResultToHTMLTable(get_idv_and_levels)


get_replication_info = g.query("""
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix chmo:   <http://purl.obolibrary.org/obo/CHMO_>
prefix msio:   <http://purl.obolibrary.org/obo/MSIO_>
prefix stato: <http://purl.obolibrary.org/obo/STATO_>
prefix obi: <http://purl.obolibrary.org/obo/OBI_>
prefix ro: <http://purl.obolibrary.org/obo/RO_>
prefix po: <http://purl.obolibrary.org/obo/PO_>
prefix has_member: <http://purl.obolibrary.org/obo/RO_0002351>
prefix has_value: <http://purl.obolibrary.org/obo/STATO_0000129>
prefix computed_from: <http://purl.obolibrary.org/obo/STATO_0000557>
prefix has_specified_input: <http://purl.obolibrary.org/obo/OBI_0000293>
prefix has_specified_output: <http://purl.obolibrary.org/obo/OBI_0000299>
prefix is_about: <http://purl.obolibrary.org/obo/IAO_0000136>
prefix is_specified_output_of: <http://purl.obolibrary.org/obo/OBI_0000295>

SELECT
      ?TreatmentGroup
      (count(distinct ?member) as ?NbTechnicalReplicate)
      (count(distinct ?input) as ?NbBiologicalReplicate)
      WHERE {
            ?population a stato:0000193 ;
                rdfs:label ?TreatmentGroup ;
                has_member: ?member .
            ?member has_specified_input: ?input .
            ?mean a stato:0000402 ;
                computed_from: ?population ;
                has_value: ?MeanConcentration ;
                is_about: ?ChemicalCompound .
            ?concentration a stato:0000072;
                is_specified_output_of: ?assay ;
                is_about: ?ChemicalCompound .
            }
      GROUP BY ?population
""")

queryResultToHTMLTable(get_replication_info)

# get_all_data = g.query("""
# prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# prefix chmo:   <http://purl.obolibrary.org/obo/CHMO_>
# prefix msio:   <http://purl.obolibrary.org/obo/MSIO_>
# prefix stato: <http://purl.obolibrary.org/obo/STATO_>
# prefix obi: <http://purl.obolibrary.org/obo/OBI_>
# prefix ro: <http://purl.obolibrary.org/obo/RO_>
# prefix po: <http://purl.obolibrary.org/obo/PO_>
# prefix has_value: <http://purl.obolibrary.org/obo/STATO_0000129>
# prefix computed_from: <http://purl.obolibrary.org/obo/STATO_0000557>
# prefix is_about: <http://purl.obolibrary.org/obo/IAO_0000136>
# prefix is_denoted_by: <http://purl.obolibrary.org/obo/STATO_0000205>
# prefix derives_from: <http://purl.obolibrary.org/obo/RO_0001000>
# prefix located_in: <http://purl.obolibrary.org/obo/RO_0001025>
# prefix denotes: <http://purl.obolibrary.org/obo/IAO_0000219>
# prefix measured_in: <http://purl.obolibrary.org/obo/STATO_0000XYZ>
#
#
# SELECT DISTINCT  ?chemical_name ?chebi_identifier  ?inchi ?sample_mean ?sem ?treatment ?genotype ?organism_part
# WHERE {
#     ?pop_mean a stato:0000402 ;
#         is_about: ?chebi_identifier ;
#         computed_from: ?population ;
#         has_value: ?sample_mean .
#     ?chem a ?chebi_identifier ;
#         rdfs:label ?chemical_name ;
#         is_denoted_by: ?inchi .
#     ?semv a stato:0000037 ;
#         denotes: ?pop_mean ;
#         has_value: ?sem.
#     ?population a stato:0000193 ;
#         rdfs:label ?treatment .
#     ?sub_conc a stato:0000072 ;
#         derives_from: ?genotype ;
#         located_in: ?organism_part;
#         measured_in: ?population .
#
# }
# """)
#
# queryResultToHTMLTable(get_all_data)
#
# data = make_sparql_df(get_all_data)


# width = figure_size[0]
# height = figure_size[0] * aspect_ratio
# gray = '#666666'
# orange = '#FF8000'
# blue = '#3333FF'
#
# p1 = (ggplot(data)
#  + aes('chemical_name','sample_mean',fill='factor(treatment)')
#  + geom_col()
#  + facet_wrap('~treatment', dir='v',ncol=1)
#  + scale_y_continuous(expand = (0,0))
#  + theme(axis_text_x=element_text(rotation=90, hjust=1, fontsize=6, color=blue))
#  + theme(axis_text_y=element_text(rotation=0, hjust=2, fontsize=6, color=orange))
#          + theme(figure_size = (8, 16))
# )
#
# p1 + theme(panel_background=element_rect(fill=blue)
#        )
#
# p1
#
#
# ggsave(plot=p1, filename='./figures/denovo/Fig_3c-rose-aroma-naturegenetics2018-from-RDF.png', dpi=100)
#
