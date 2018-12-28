# -*- coding: utf-8 -*-

import csv
import logging
import os
import re
import scrapy
import yaml

from bs4 import BeautifulSoup

from scrapy import Request

from slugify import slugify

from urllib.parse import urlparse

logger = logging.getLogger(__file__)

ENTITY_CHARS = {
  '&#32;': ' ',
  '&#33;': '!',
  '&#34;': '"',
  '&quot;': '"',
  '&#35;': '#',
  '&#36;': '$',
  '&#37;': '%',
  '&#38;': '&',
  '&amp;': '&',
  '&#39;': "'",
  '&#40;': '(',
  '&#41;': ')',
  '&#42;': '*',
  '&#43;': '+',
  '&#44;': ',',
  '&#45;': '-',
  '&#46;': '.',
  '&#47;': '/',
	'&#58;': ':',
	'&#59;': ';',
	'&#60;': '<',
  '&lt;': '<',
	'&#61;': '=',
	'&#62;': '>',
  '&#gt;': '>',
	'&#63;': '?',
}
URL_MATCHER = re.compile('(http|https):\/\/(.*)')
SPACE_MATCHER = re.compile('\s+')
EMAIL_MATCHER = re.compile('[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+')
HANDLE_MATCHER = re.compile('\s(@[a-zA-Z0-9-_.]+)')

def is_uri_match(url_one, url_two):
  parts_one = urlparse(url_one)
  parts_two = urlparse(url_two)

  # ld, logical domain
  ld_one = '.'.join(parts_one.netloc.rsplit('.', 2)[:2])
  ld_two = '.'.join(parts_two.netloc.rsplit('.', 2)[:2])
  if ld_one != ld_two:
    return False

  if parts_one.path != parts_two.path:
    return False

  if parts_one.query != parts_two.query:
    return False

  if parts_one.fragment != parts_two.fragment:
    return False

  if parts_one.params != parts_two.params:
    return False

  return True

class CsvhunterSpider(scrapy.Spider):
    # handle_httpstatus_list = [416]
    name = 'csvhunter'
    # allowed_domains = ['jbcurtin.io']
    start_urls = []

    def __init__(self, input_file=None, config_path=None, output_path=None):
      csv_headers = None
      csv_data = {}
      start_urls = []

      if input_file is None:
        raise AttributeError('Missing input_file')

      self.input_file = os.path.join(os.getcwd(), input_file)
      if not os.path.exists(self.input_file):
        raise IOError(self.input_file)

      self.model_keys = []
      self.sources = []
      with open(input_file, 'r') as stream:
        try:
          rows = [row for row in csv.reader(stream)]
        except UnicodeDecodeError as err:
          raise ValueError('Unicode error in %s' % input_file)

        for row in rows:
          if csv_headers is None:
            csv_headers = row
            continue

          datum = {}
          datum.update((item for item in zip(csv_headers, row)))
          for key in datum.keys():
            if key not in self.model_keys:
              self.model_keys.append(key)

          self.sources.append(datum.copy())
          self.start_urls.extend([url for url in filter(lambda x: URL_MATCHER.search(x) != None, row)])

      self.start_urls = list({url for url in self.start_urls})
      self.start_urls = [url for url in filter(lambda x: '.'.join(urlparse(x).netloc.rsplit('.', 2)[1:]) not in ['linkedin.com', 'crunchbase.com'], self.start_urls)]
      # self.start_urls = self.start_urls[:200]

      if config_path is None:
        raise AttributeError('Missing config_path')

      self.config_path = os.path.join(os.getcwd(), config_path)
      if not os.path.exists(self.config_path):
        raise IOError(self.config_path)

      self.keywords = []
      with open(self.config_path, 'r') as stream:
        datum_config = yaml.load(stream.read())
        self.keywords.extend(list({keyword.lower() for keyword in datum_config['index']['keywords']}))
        self.keywords.extend(list({keyword.lower() for keyword in datum_config['index']['phrases']}))

      if output_path is None:
        raise AttributeError('Missing output_path')

      self.output_path = os.path.join(os.getcwd(), output_path)
      output_path_dir = os.path.dirname(self.output_path)
      if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)

    def cleanup_document(self, selector):
      text_soup = ' '.join(selector.xpath("//*[not(contains(local-name(), 'script')) or not(contains(local-name(), 'style'))]//text()").extract())
      text_soup = ''.join([c for c in map(lambda x: ENTITY_CHARS.get(x, x), text_soup)])
      text_soup = ' '.join(SPACE_MATCHER.split(text_soup))
      return text_soup.lower()

    def _extract_valid_anchors(self, response):
      for anchor in response.xpath('//a'):
        attrs = BeautifulSoup(anchor.extract(), 'html.parser').find('a').attrs
        try:
          attrs = {key: attrs[key] for key in ['href']}
        except KeyError as err:
          logger.debug(err)
          continue

        # https://en.wikipedia.org/wiki/Truth_table
        if attrs['href'] == '/':
          continue

        if attrs['href'].startswith('#'):
          continue

        if attrs['href'] == '':
          continue

        if attrs['href'].startswith('http'):
          yield attrs['href']

        url_parts = urlparse(response.url)
        if attrs['href'].startswith('/'):
          yield ''.join([
            url_parts.scheme, '://',
            url_parts.netloc,
            attrs['href']])

    def _build_context(self, lexigraph_sequence, cleaned_document, bounds=35):
      cursor = 0
      index = 0
      while True:
        index = index + cleaned_document[cursor:].find(lexigraph_sequence)
        if index < 0:
          break

        lower_bound = index - bounds
        upper_bound = index + len(lexigraph_sequence) + bounds
        yield {
          'lower_bound': cleaned_document[lower_bound: lower_bound + bounds],
          'lexigraph_sequence': lexigraph_sequence,
          'upper_bound': cleaned_document[upper_bound - bounds: upper_bound],
          'context': cleaned_document[lower_bound: upper_bound],
        }
        step = index + len(lexigraph_sequence)
        if step != cursor:
          cursor = step
        else:
          break

    def _detect_keywords(self, cleaned_document):
      for keyword in self.keywords:
        match = ' %s ' % keyword
        if match in cleaned_document:
          yield keyword, self._build_context(keyword, cleaned_document)

    def find_matched_sources(self, item):
      matched_sources = []
      for source in self.sources:
        found_urls = [url for url in filter(lambda x: URL_MATCHER.search(x) != None, source.values())]
        for url in found_urls:
          if is_uri_match(item['href'], url):
            matched_sources.append(source.copy())

      return matched_sources

    def parse(self, response):
      for anchor in self._extract_valid_anchors(response):
        yield Request(anchor, callback=self.parse)

      cleaned_document = self.cleanup_document(response)
      keywords_found = [keyword for keyword in self._detect_keywords(cleaned_document)]
      for keyword, context in keywords_found:
        item = {
          'domain': urlparse(response.url).netloc,
          'href': response.url,
          'catch_all': ':'.join([kw for kw, context in keywords_found]),
          'lexigraph_sequence': keyword,
          'context': ':::'.join(['-'.join([str(idx), c['context']]) for idx, c in enumerate([awe for awe in context])]),
          'emails-detected': [email for email in EMAIL_MATCHER.findall(cleaned_document) if email],
          'at-handle': [handle for handle in HANDLE_MATCHER.findall(cleaned_document) if handle]
        }
        matched_sources = self.find_matched_sources(item)
        if len(matched_sources) > 1:
          # import ipdb;ipdb.set_trace()
          logger.exception('matched_sources > 1')
          import sys; sys.exit(1)

        item.update({slugify(key): '' for key in self.model_keys})
        if len(matched_sources) is 1:
          item.update({slugify(key): value for key, value in matched_sources[0].items()})

        yield item

