from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from markdown.tools.html import HTMLParserTools
from markdown.tools.html.errors import (
    EmptyHtmlProvidedForParsing,
    InvalidAttributeProvided,
    InvalidContentProvided,
    InvalidHtmlProvidedForParsing,
    NoFirstTagFound,
    TagNotFoundInHTML,
)


class TestHTMLParserTools:
    def test_parse_html_properly(self):
        html = "<h1>Test</h1>"
        expected = BeautifulSoup(html, "html.parser")

        result = HTMLParserTools(html)

        assert result.tree == expected

    def test_parse_empty_html(self):
        html = ""

        with pytest.raises(EmptyHtmlProvidedForParsing):
            HTMLParserTools(html)

    @patch("markdown.tools.html.parser.BeautifulSoup", side_effect=Exception)
    def test_parse_(self, *_):
        html = "Something wrong"

        with pytest.raises(InvalidHtmlProvidedForParsing):
            HTMLParserTools(html)


class TestHTMLParserToolsFindFirstTag:
    def test_return_first_tag(self):
        html = "<h1>Test</h1>"
        html_tree = BeautifulSoup(html, "html.parser")
        expected = list(html_tree.children)[0]

        result = HTMLParserTools(html).find_first_tag()

        assert result == expected

    def test_no_first_tag_included(self):
        html = "Test"

        with pytest.raises(NoFirstTagFound):
            HTMLParserTools(html).find_first_tag()


class TestHTMLParserToolsAddAttributeToTag:
    def test_add_content_properly(self):
        html = "<h1>Test</h1><a>Test</a>"
        service = HTMLParserTools(html)
        tag = list(service.tree.children)[0]
        expected = '<h1 md_content="content">Test</h1><a>Test</a>'

        service.add_attribute_to_tag(tag, "md_content", "content")

        assert str(service.tree) == expected

    def test_invalid_tag_included(self):
        html = "Test"
        other_html_tree = BeautifulSoup("<h1>Test</h1>", "html.parser")
        fake_tag = list(other_html_tree.children)[0]

        with pytest.raises(TagNotFoundInHTML):
            HTMLParserTools(html).add_attribute_to_tag(
                fake_tag, "md_content", "content"
            )

    def test_fail_with_empty_attribute(self):
        html = "<h1>Test</h1><a>Test</a>"
        service = HTMLParserTools(html)
        tag = list(service.tree.children)[0]

        with pytest.raises(InvalidAttributeProvided):
            service.add_attribute_to_tag(tag, "", "content")

    def test_fail_with_none_attribute(self):
        html = "<h1>Test</h1><a>Test</a>"
        service = HTMLParserTools(html)
        tag = list(service.tree.children)[0]

        with pytest.raises(InvalidAttributeProvided):
            service.add_attribute_to_tag(tag, None, "content")

    def test_with_none_content(self):
        html = "<h1>Test</h1><a>Test</a>"
        service = HTMLParserTools(html)
        tag = list(service.tree.children)[0]

        with pytest.raises(InvalidContentProvided):
            service.add_attribute_to_tag(tag, "md_content", None)

    def test_with_empty_content(self):
        html = "<h1>Test</h1><a>Test</a>"
        service = HTMLParserTools(html)
        tag = list(service.tree.children)[0]
        expected = '<h1 md_content="">Test</h1><a>Test</a>'

        service.add_attribute_to_tag(tag, "md_content", "")

        assert str(service.tree) == expected

    def test_with_none_tag(self):
        html = "<h1>Test</h1><a>Test</a>"

        with pytest.raises(TagNotFoundInHTML):
            HTMLParserTools(html).add_attribute_to_tag(None, "md_content", "content")


class TestHTMLParserToolsGetString:
    def test_working_properly(self):
        html = "<h1>Test</h1><a>Test</a>"
        service = HTMLParserTools(html)

        result = service.get_html()

        assert result == html
