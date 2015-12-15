__author__ = 'Erik Sommer'

import datetime
import requests
import json
import re

namespace_mapping = {"Article": 0,
                     "Diskussion": 1,
                     "Benutzer": 2,
                     "Benutzer Diskussion": 3,
                     "Wikisource": 4,
                     "Wikisource Diskussion": 5,
                     "Wikipedia": 4,
                     "Wikipedia Diskussion": 5,
                     "Wikibooks": 4,
                     "Wikibooks Diskussion": 5,
                     "Wikiquote": 4,
                     "Wikiquote Diskussion": 5,
                     "Wikispecies": 4,
                     "Wikispecies Diskussion": 5,
                     "Wikinews": 4,
                     "Wikinews Diskussion": 5,
                     "Wikionary": 4,
                     "Wikionary Diskussion": 5,
                     "Datei": 6,
                     "Datei Diskussion": 7,
                     "MediaWiki": 8,
                     "MediaWiki Diskussion": 9,
                     "Vorlage": 10,
                     "Vorlage Diskussion": 11,
                     "Hilfe": 12,
                     "Hilfe Diskussion": 13,
                     "Kategorie": 14,
                     "Kategorie Diskussion": 15,
                     "Portal": 100,
                     "Portal Diskussion": 101,
                     "Seite": 102,
                     "Seite Diskussion": 103,
                     "Wahl": 102,
                     "Wahl Diskussion": 103,
                     "Meinungen": 102,
                     "Meinungen Diskussion": 103,
                     "Verzeichnis": 102,
                     "Verzeichnis Diskussion": 103,
                     "Index": 104,
                     "Index Diskussion": 105,
                     "Thesaurus": 104,
                     "Thesaurus Diskussion": 105,
                     "Kurs": 106,
                     "Kurs Diskussion": 107,
                     "Reim": 106,
                     "Reim Diskussion": 107,
                     "Projekt": 108,
                     "Projekt Diskussion": 109,
                     "Flexion": 108,
                     "Flexion Diskussion": 109,
                     "Education Program": 446,
                     "Education Program Diskussion": 447,
                     "Modul": 828,
                     "Modul Diskussion": 829,
                     "Gadget ": 2300,
                     "Gadget  Diskussion": 2301,
                     "Gadget-Definition": 2302,
                     "Gadget-Definition Diskussion": 2303,
                     "Thema": 2600}


def listify(x):
    """
    If given a non-list, encapsulate in a single-element list.

    @rtype: list
    """
    return x if isinstance(x, list) else [x]


class CatScan:
    """
    Encapsulate the catscan service, written by Markus Manske (http://tools.wmflabs.org/catscan2/catscan2.php).
    It is possible to access all parameters by different setter functions. The function 'run' execute the server inquiry
    with the set parameters. The answer is a list with the matching pages. The inquiry have a timeout by 30 seconds.
    """
    def __init__(self):
        self.header = {'User-Agent': 'Python-urllib/3.1'}
        self.base_address = "http://tools.wmflabs.org/catscan2/catscan2.php"
        self.timeout = 30
        self.options = {}
        self.categories = {"positive": [], "negative": []}
        self.templates = {'yes': [], 'any': [], 'no': []}
        self.outlinks = {'yes': [], 'any': [], 'no': []}
        self.language = "de"
        self.project = "wikisource"

    def __str__(self):
        """
        Returns the ready constructed Searchstring for the catscan query.

        @return: Searchstring
        @rtype: str
        """
        return self._construct_string()

    def set_language(self, lang):
        """
        Set the language of the wiki.
        @param lang: language
        @type lang: str
        """
        self.language = lang

    def set_project(self, proj):
        """
        Set the project of the wiki (examples: wikisource, wikipedia).
        @param proj: project
        @type proj: str
        """
        self.project = proj

    def set_timeout(self, sec):
        """
        Set the timeout of the query.
        @param sec: seconds
        @type sec: int
        """
        self.timeout = sec

    def set_logic(self, log_and = None, log_or = None):
        """
        Set the logic connection between the categories.
        @param log_and: connects (True) the categories with an and statement or not (False)
        @type log_and: bool
        @param log_or: connects (True) the categories with an or statement or not (False)
        @type log_or: bool
        """
        if log_and and log_or:
            self.add_options({"comb[subset]": "1", "comb[union]": "1"})
        elif log_or:
            self.add_options({"comb[union]": "1"})

    def add_options(self, dict_options):
        """
        Add new options to self._options.
        @param dict_options: dictionary with new options
        @type dict_options: dict
        """
        self.options.update(dict_options)

    def set_depth(self, depth):
        """
        Defines the search depth for the query.
        @param depth: Count of subcategories that will be searched
        @type depth: int
        """
        self.add_options({"depth":depth})

    def add_positive_category(self, category):
        """
        Add category to the positive list.
        @param category: string with the category name
        @type category: str
        """
        self.categories["positive"].append(category)

    def add_negative_category(self, category):
        """
        Add category to the negative list.
        @param category: string with the category name
        @type category: str
        """
        self.categories["negative"].append(category)

    def add_namespace(self, namespace):
        """
        Add (a) namespace(s) to the options.
        @param namespace: string or integer with a new namespace (a list of namespaces is possible).
                          Only german namespaces are supported yet.
        @type namespace: str|int|list
        """
        # is there a list to process or only a single instance
        namespace = listify(namespace)
        for i in namespace:
            # is there a given integer or the string of a namespace
            if type(i) is int:
                self.add_options({"ns[" + str(i) + "]": "1"})
            else:
                self.add_options({"ns[" + str(namespace_mapping[i]) + "]": "1"})

    def activate_redirects(self):
        """
        Activate redirects in the result.
        """
        self.add_options({"show_redirects": "yes"})

    def deactivate_redirects(self):
        """
        Deactivate redirects in the result.
        """
        self.add_options({"show_redirects": "no"})

    def add_yes_template(self, template):
        """
        Add template to the yes list.
        @param template: string with the template name
        @type template: str
        """
        self.templates['yes'].append(template)

    def add_any_template(self, template):
        """
        Add template to the any list.
        @param template: string with the template name
        @type template: str
        """
        self.templates['any'].append(template)

    def add_no_template(self, template):
        """
        Add template to the no list.
        @param template: string with the template name
        @type template: str
        """
        self.templates['no'].append(template)

    def add_yes_outlink(self, outlink):
        """
        Add an outlink to the yes list.
        @param outlink: string with the outlink name
        @type outlink: str
        """
        self.outlinks['yes'].append(outlink)

    def add_any_outlink(self, outlink):
        """
        Add an outlink to the any list.
        @param outlink: string with the outlink name
        @type outlink: str
        """
        self.outlinks['any'].append(outlink)

    def add_no_outlink(self, outlink):
        """
        Add an outlink to the no list.
        @param outlink: string with the outlink name
        @type outlink: str
        """
        self.outlinks['no'].append(outlink)

    def last_change_before(self, year, month=1, day=1, hour=0, minute=0, second=0):
        """
        Specify lower boundry of the period, where the last change occured.
        @param year:
        @param month:
        @param day:
        @param hour:
        @param minute:
        @param second:
        @type year: int
        @type month: int
        @type day: int
        @type hour: int
        @type minute: int
        @type second: int
        """
        last_change = datetime.datetime(year, month, day, hour, minute, second)
        self.add_options({"before": last_change.strftime("%Y%m%d%H%M%S")})

    def last_change_after(self, year, month=1, day=1, hour=0, minute=0, second=0):
        """
        Specify higher boundry of the period, where the last change occured.
        @param year:
        @param month:
        @param day:
        @param hour:
        @param minute:
        @param second:
        @type year: int
        @type month: int
        @type day: int
        @type hour: int
        @type minute: int
        @type second: int
        """
        last_change = datetime.datetime(year, month, day, hour, minute, second)
        self.add_options({"after": last_change.strftime("%Y%m%d%H%M%S")})

    def max_age(self, hours):
        """
        The maximum age of the site.
        @param hours:
        @type hours: int
        """
        self.add_options({"max_age": str(hours)})

    def only_new(self):
        """
        show only items, which were created in the given period.
        """
        self.add_options({"only_new": "1"})

    def smaller_then(self, page_size):
        """
        The maximum page_size.
        @param page_size: Size in Bytes
        @type page_size: int
        """
        self.add_options({"smaller": str(page_size)})

    def larger_then(self, page_size):
        """
        The minimum page_size.
        @param page_size: Size in Bytes
        @type page_size: int
        """
        self.add_options({"larger": str(page_size)})

    def get_wikidata(self):
        """
        Get the wikidata items number of the results.
        """
        self.add_options({"get_q": "1"})

    def _construct_cat_string(self, cat_list):
        cat_string = ""
        i = 0
        for cat in cat_list:
            if i > 0:
                cat_string += "%0D%0A"
            string_item = cat
            string_item = re.sub(' ', '+', string_item)
            cat_string += string_item
            i += 1
        return cat_string

    def _construct_options(self):
        opt_string = ""
        for key in self.options:
            opt_string += ("&" + key + "=" + str(self.options[key]))
        return opt_string

    def _construct_string(self):
        question_string = self.base_address
        question_string += ("?language=" + self.language)
        question_string += ("&project=" + self.project)
        #categories
        if len(self.categories["positive"]) != 0:
            question_string += ("&categories=" + (self._construct_cat_string(self.categories["positive"])))
        if len(self.categories["negative"]) != 0:
            question_string += ("&negcats=" + (self._construct_cat_string(self.categories["negative"])))
        #templates
        if len(self.templates["yes"]) != 0:
            question_string += ("&templates_yes=" + (self._construct_cat_string(self.templates["yes"])))
        if len(self.templates["any"]) != 0:
            question_string += ("&templates_any=" + (self._construct_cat_string(self.templates["any"])))
        if len(self.templates["no"]) != 0:
            question_string += ("&templates_no=" + (self._construct_cat_string(self.templates["no"])))
        #outlinks
        if len(self.outlinks["yes"]) != 0:
            question_string += ("&outlinks_yes=" + (self._construct_cat_string(self.outlinks["yes"])))
        if len(self.outlinks["any"]) != 0:
            question_string += ("&outlinks_any=" + (self._construct_cat_string(self.outlinks["any"])))
        if len(self.outlinks["no"]) != 0:
            question_string += ("&outlinks_no=" + (self._construct_cat_string(self.outlinks["no"])))
        #rest of the options
        if len(self.options) != 0:
            question_string += (self._construct_options())
        question_string += "&format=json&doit=1"
        return question_string

    def run(self):
        """
        Execute the search query und returns the results as a list.
        @return: list of result dicionaries.
        @rtype: list
        """
        try:
            response = requests.get(url=self._construct_string(),
                                    headers=self.header, timeout=self.timeout)
            response_byte = response.content
            response_dict = json.loads(response_byte.decode("utf8"))
            return response_dict['*'][0]['a']['*']
        except Exception:
            raise ConnectionError