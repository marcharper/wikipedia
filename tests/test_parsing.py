import unittest

from mediawiki.helpers import (extract_templates,
    normalize_link, normalize_title, parse_category_link, parse_link)


class TestHelpers(unittest.TestCase):

    def test_normalize_title(self):
        self.assertEqual(normalize_title("a b"), 'A_b')
        self.assertEqual(normalize_title(" a b "), 'A_b')
        self.assertEqual(normalize_title(" a   b "), 'A_b')
        self.assertEqual(normalize_title("R O C"), "R_O_C")
        self.assertEqual(normalize_title("r o c"), "R_o_c")
        self.assertEqual(normalize_title(''), '')

    def test_normalize_link(self):
        self.assertEqual(normalize_link('[[a b]]'), '[[a b]]')
        self.assertEqual(normalize_link('[[ a b ]]'), '[[a b]]')
        self.assertEqual(normalize_link('[[a (b)|]]'), '[[a (b)|a]]')
        self.assertEqual(normalize_link('[[a, b|]]'), '[[a, b|a]]')
        self.assertEqual(normalize_link('[[C:a (b)|]]'), '[[C:a (b)|a]]')
        self.assertEqual(normalize_link('[[C:a, b|]]'), '[[C:a, b|a]]')
        self.assertEqual(normalize_link('[[|b]]', 'a, c'), '[[b, c|b]]')
        self.assertEqual(normalize_link('[[|b]]', 'a (c)'), '[[b (c)|b]]')
        self.assertEqual(normalize_link('[[#b]]', 'a'), '[[a#b]]')

        self.assertEqual(normalize_link('[[Boston, Massachusetts|]]'),
                         '[[Boston, Massachusetts|Boston]]')
        self.assertEqual(normalize_link('[[|Agonizer]]', 'Agonist (disambiguation)'),
                         '[[Agonizer (disambiguation)|Agonizer]]')
        self.assertEqual(normalize_link('[[:Category:Continents|]]'),
                         '[[:Category:Continents|Continents]]')
        self.assertEqual(normalize_link('[[Wikipedia:Help|]]'),
                         '[[Wikipedia:Help|Help]]')


    def test_extract_templates(self):
        self.assertEqual(extract_templates('{{a}}'), ['{{a}}'])
        self.assertEqual(extract_templates('{{ {{a}} b }}'), ['{{ {{a}} b }}'])
        self.assertEqual(extract_templates('{{b}} {{a}}'), ['{{b}}', '{{a}}'])
        self.assertEqual(extract_templates('{{ a b {{a}} {{ a b}} }}'),
                         ['{{ a b {{a}} {{ a b}} }}'])
        self.assertEqual(extract_templates('{{ a b {{a}} }} {{ {{ a b}} }}'),
                         ['{{ a b {{a}} }}', '{{ {{ a b}} }}'])

    def test_parse_category_link(self):
        self.assertEqual(parse_category_link("[[a:b|c]]"), "[[a:b]]")
        self.assertEqual(parse_category_link("[[a:b]]"), "[[a:b]]")
        self.assertEqual(parse_category_link("[[a]]"), "[[a]]")

    def test_parse_link(self):
        # Need namespace and languages tests
        self.assertEqual(parse_link("[[a]]"),
                         {'language': 'en',
                          'target': 'a',
                          'display': 'a',
                          'interwiki': '',
                          'namespace': ''})
        self.assertEqual(parse_link("[[a|b]]"),
                         {'language': 'en',
                          'target': 'a',
                          'display': 'b',
                          'interwiki': '',
                          'namespace': ''})
        self.assertEqual(parse_link("[[n:a|b]]"),
                         {'language': 'en',
                          'target': 'n:a',
                          'display': 'b',
                          'interwiki': 'n',
                          'namespace': ''})

