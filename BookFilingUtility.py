"""
:mod: 'BookFilingUtility'
~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:module:: BookFilingUtility
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: Filing and Fact class definitions, and utility functions for working with facts and filings
    :description: Contains the following classes:

        Filing - represents a single filing, as a list of business facts
        Fact - represents a single business fact
        MyHTMLParser - custom class of HTMLParser (from html.parser) used to parse and store HTML

                  Contains the following functions:

        isXbrlInstance - determines whether a file is an XBRL instance or not
        isAlphaOrHtml - determines whether a Fact is a textual or numerical business fact
        getFilingInfo - analyzes a Filing object and returns information relevant for display and database storage
        isImportable - determines whether a fact file can be imported into a XBRLStudio sqlite database
        parseFactFile - converts a fact file (produced by an Arelle controller) into a Filing object
        decodeHtml - converts a text block (string) into formatted html (string)
"""

try:
    import os, sys, datetime, logging
    filing_utility_logger = logging.getLogger()
    import xml.etree.ElementTree as etree
    # from lxml import etree
    from html.parser import HTMLParser
    from html.entities import name2codepoint
except Exception as err:
    filing_utility_logger.error("{0}:BookFilingUtility import error:{1}".format(str(datetime.datetime.now()), str(err)))

class Filing():
    """
    Filing
    ~~~~~~
    Custom class providing structure and operations for the storage and comparison of business facts

    Functions
    ~~~~~~~~~
    __key(self) - key function used, e.g., by set()
    __eq__(self, other) - equals function used, e.g., by set()
    __ne__(self, other) - not-equals function used, e.g., by set()
    __hash__(self) - hash function used, e.g., by set()

    Attributes
    ~~~~~~~~~~
    facts (list type); list of Fact objects, each representing a business fact from a parsed fact file
    """

    def __init__(self, facts):
        filing_utility_logger.info("{0}:Initializing Filing".format(str(datetime.datetime.now())))
        self.facts = facts

    def __key(self):
        try:
            return self.facts
        except Exception as err:
            filing_utility_logger.error("{0}:Filing.__key():{1}".format(str(datetime.datetime.now()), str(err)))

    def __eq__(self, other):
        try:
            return self.__key() == other.__key()
        except Exception as err:
            filing_utility_logger.error("{0}:Filing.__eq__():{1}".format(str(datetime.datetime.now()), str(err)))

    def __ne__(self, other):
        try:
            if self.__eq__(self, other):
                return False
            else:
                return True
        except Exception as err:
            filing_utility_logger.error("{0}:Filing.__ne__():{1}".format(str(datetime.datetime.now()), str(err)))

    def __hash__(self):
        try:
            return hash(self.__key())
        except Exception as err:
            filing_utility_logger.error("{0}:Filing.__hash__():{1}".format(str(datetime.datetime.now()), str(err)))

class Fact():
    """
    Fact
    ~~~~
    Custom class providing structure for the storage of a single business fact

    Functions
    ~~~~~~~~~
    __key(self) - key function used, e.g., by set()
    __eq__(self, other) - equals function used, e.g., by set()
    __ne__(self, other) - not-equals function used, e.g., by set()
    __hash__(self) - hash function used, e.g., by set()

    Attributes
    ~~~~~~~~~~
    label (string type); fact label
    name (string type); fact name
    context_ref (string type); fact context
    unit_ref (string type); fact units
    dec (int type); fact decimals (stored in table model items but only conditionally displayed)
    prec (int type); fact precision (stored in table model items but not displayed; derivable from dec; see XBRL documentation)
    lang (string type); fact language (not used by XBRLStudio)
    value (string or int or float type); fact value
    entity_scheme (string type); fact entity scheme (not used by XBRLStudio)
    entity_identifier (string type); fact entity identifier (not used by XBRLStudio)
    period (string type); fact period (not used by XBRLStudio)
    dimensions (string type); fact dimensions (not used by XBRLStudio)
    """

    def __init__(self, label = None, name = None, context_ref = None, unit_ref = None,
                 dec = None, prec = None, lang = None, value = None, entity_scheme = None,
                 entity_identifier = None, period = None, dimensions = None):
        self.label = label
        self.name = name
        self.context_ref = context_ref
        self.unit_ref = unit_ref
        self.dec = dec
        self.prec = prec
        self.lang = lang
        self.value = value
        self.entity_scheme = entity_scheme
        self.entity_identifier = entity_identifier
        self.period = period
        self.dimensions = dimensions

    def __key(self):
        try:
            return(self.label, self.name, self.context_ref, self.unit_ref, self.dec, self.prec,
               self.lang, self.value, self.entity_scheme, self.entity_identifier, self.period, self.dimensions)
        except Exception as err:
            filing_utility_logger.error("{0}:Fact.__key():{1}".format(str(datetime.datetime.now()), str(err)))

    def __eq__(self, other):
        try:
            return self.__key() == other.__key()
        except Exception as err:
            filing_utility_logger.error("{0}:Fact.__eq__():{1}".format(str(datetime.datetime.now()), str(err)))

    def __ne__(self, other):
        try:
            if self.__eq__(self, other):
                return False
            else:
                return True
        except Exception as err:
            filing_utility_logger.error("{0}:Fact.__ne__():{1}".format(str(datetime.datetime.now()), str(err)))

    def __hash__(self):
        try:
            return hash(self.__key())
        except Exception as err:
            filing_utility_logger.error("{0}:Fact.__hash__():{1}".format(str(datetime.datetime.now()), str(err)))

class MyHTMLParser(HTMLParser):
    """
    MyHTMLParser
    ~~~~~~~~~~~~
    Custom class providing HTML parsing, storage, and retrival functionality

    Functions
    ~~~~~~~~~
    handle_starttag - incorporate the start tag and any attributes
    handle_endtag - incorporate the end tag
    handle_data - incorporate data
    handle_comment - incorporate comment
    handle_entityref - incorporate entity reference
    handle_charref - incorporate character reference
    handle_decl - incorporate decl
    retrieveElement - return the element

    Attributes
    ~~~~~~~~~~
    element - main string containing the html to be delivered
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.element = ""

    def handle_starttag(self, tag, attrs):
        self.element += str(tag)
        for attr in attrs:
            self.element += str(attr)

    def handle_endtag(self, tag):
        self.element += str(tag)

    def handle_data(self, data):
        self.element += str(data)

    def handle_comment(self, data):
        self.element += str(data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        self.element += str(c)

    def handle_charref(self, name):
        self.element += str(name)

    def handle_decl(self, data):
        self.element += str(data)

    def retrieveElement(self):
        return self.element

def isXbrlInstance(uri):
    try:
        uri_tree = etree.parse(uri)
        uri_tree_root = uri_tree.getroot()
        if "instance" in uri_tree_root.tag:
            return True
        else:
            return False
    except Exception as err:
        filing_utility_logger.error("{0}:isXbrlInstance():{1}".format(str(datetime.datetime.now()), str(err)))

def isAlphaOrHtml(target_fact):
    try:
        try:
            temp = None
            temp = float(target_fact.value.replace(",", ""))
            return False
        except ValueError: #fact value is non-integer (i.e., string)
            return True
        except TypeError: #fact value is NoneType - group with html facts
            return True
    except Exception as err:
        filing_utility_logger.error("{0}:isAlphaOrHtml():{1}".format(str(datetime.datetime.now()), str(err)))

def getFilingInfo(filing):
    try:
        entity_name = None
        filing_year = None
        filing_period = None
        entity_cik = None
        entity_parent_cik = None
        filing_end_date = None
        entity_cik_list = []
        for fact in filing.facts:
            if fact.name == "dei:EntityRegistrantName": #entity name
                try:
                    entity_name = str(fact.value)
                except Exception as err:
                    pass
            if fact.name == "dei:DocumentFiscalYearFocus": #filing year
                try:
                    filing_year = str(fact.value)
                except Exception as err:
                    pass
            if fact.name == "dei:DocumentFiscalPeriodFocus": #filing quarter/fy
                try:
                    filing_period = str(fact.value).lower()
                except Exception as err:
                    pass
            if fact.name == "dei:EntityCentralIndexKey": #cik
                try:
                    entity_cik_list.append(int(fact.value))
                except Exception as err:
                    pass
            if fact.name == "dei:DocumentPeriodEndDate": #document end date (more prevalent)
                try:
                    filing_end_date = str(fact.value)
                except Exception as err:
                    pass
        if filing_period is not None and filing_year is not None:
            if filing_period == "fy":
                filing_period = "q4"
            filing_period = filing_period + filing_year
        elif filing_period is None or filing_year is None:
            if filing_end_date is not None:
                filing_year = filing_end_date[0:4]
                if filing_end_date[5:7] == "03": #Q1
                    filing_period = "q1" + filing_year
                elif filing_end_date[5:7] == "06": #Q2
                    filing_period = "q2" + filing_year
                elif filing_end_date[5:7] == "09": #Q3
                    filing_period = "q3" + filing_year
                elif filing_end_date[5:7] == "12": #Q4
                    filing_period = "q4" + filing_year
                else:
                    filing_period = None
            else:
                pass

        for entity_cik in entity_cik_list:
            entity_cik = "{0:010d}".format(entity_cik)

        return entity_cik_list, entity_parent_cik, entity_name, filing_period
    except Exception as err:
        filing_utility_logger.error("{0}:getFilingInfo():{1}".format(str(datetime.datetime.now()), str(err)))

def isImportable(target_fact_uri):
    try:
        target_filing = parseFactFile(target_fact_uri)
        target_cik_list, target_parent_cik, target_name, target_period = getFilingInfo(target_filing)

        if len(target_cik_list) == 0 or None in (target_name, target_period):
            return False
        else:
            return True
    except Exception as err:
        filing_utility_logger.error("{0}:isImportable():{1}".format(str(datetime.datetime.now()), str(err)))

def parseFactFile(target_fact_uri):
    try:
        fact_object_list = []
        uri_tree = etree.parse(target_fact_uri)
        fact_list = uri_tree.getroot()

        for item in fact_list:
            new_fact = Fact(name = item.attrib["name"])
            for child in item:
                if child.tag == "label":
                    new_fact.label = child.text
                if child.tag == "contextRef":
                    new_fact.context_ref = child.text
                if child.tag == "unitRef":
                    new_fact.unit_ref = child.text
                if child.tag == "dec":
                    new_fact.dec = child.text
                if child.tag == "prec":
                    new_fact.prec = child.text
                if child.tag == "lang":
                    new_fact.lang = child.text
                if child.tag == "value":
                    new_fact.value = child.text
                if child.tag == "entityScheme":
                    new_fact.entity_scheme = child.text
                if child.tag == "entityIdentifier":
                    new_fact.entity_identifier = child.text
                if child.tag == "period":
                    new_fact.period = child.text
                if child.tag == "dimensions":
                    new_fact.dimensions = child.text
            fact_object_list.append(new_fact)

        return Filing(fact_object_list)
    except Exception as err:
        filing_utility_logger.error("{0}:parseFactFile():{1}".format(str(datetime.datetime.now()), str(err)))

def decodeHtml(text_block):
    try:
        parser = MyHTMLParser()
        parser.feed(text_block)
        return parser.retrieveElement()
    except Exception as err:
        filing_utility_logger.error("{0}:decodeHtml():{1}".format(str(datetime.datetime.now()), str(err)))
