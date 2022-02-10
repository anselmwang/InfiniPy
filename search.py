# %%
import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Text, Tuple

logger = logging.getLogger(os.path.basename(__file__))
# logger.setLevel(logging.INFO)
@dataclass
class Span:
    start: int
    end: int

@dataclass
class MatchResult:
    spans: List[Span]  

class TextMatcher:
    def __init__(self, docs: List[str], ignore_case: bool=False):
        self._docs = docs
        self._ignore_case = ignore_case
    
    def _search(self, query: str, ignore_case: bool=False) -> List[MatchResult]:
        return [self.match(query, doc, self._ignore_case) for doc in self._docs]
        
    def filter(self, query: str) -> Tuple[List[int], List[str], List[MatchResult]]:
        logger.debug(f"query: {query}")
        match_results = self._search(query)
        filtered_line_nos = []
        filtered_lines = []
        filtered_match_results = []
        for line_no, (line, match_result) in enumerate(zip(self._docs, match_results)):
            if match_result is not None:
                filtered_line_nos.append(line_no)
                filtered_lines.append(line)
                filtered_match_results.append(match_result)
        return filtered_line_nos, filtered_lines, filtered_match_results

    @staticmethod
    def match(query: str, doc: str, ignore_case: bool=False) -> Optional[MatchResult]:
        """Match query with doc. 
        Check whether segments in query appear in doc in order.

        Args:
            query (str): multiple segments splitted by whitepsace chars
            doc (str): 
            ignore_case (bool, optional): Defaults to False.

        Returns:
            Optional[MatchResult]: 
                return None is query doesn't match with doc
                return length 0 spans in case the query is empty
        """
        if ignore_case:
            query = query.lower()
            doc = doc.lower()

        match_result = MatchResult([])
        segments = query.split()
        start_pos = 0
        for segment in segments:
            found_pos = doc.find(segment, start_pos)
            if found_pos == -1:
                return None
            match_result.spans.append(Span(found_pos, found_pos+len(segment)))
            start_pos = found_pos + len(segment)
        return match_result

class ListSearcher:
    def __init__(self, objects, ignore_case=True):
        self._objects = objects
        _original_lines = [self._str_for_matcher(record) for record in objects]
        self._text_matcher = TextMatcher(_original_lines, ignore_case=ignore_case)

    def _str_for_matcher(self, record):
        raise NotImplementedError
    
    def _str_for_show(self, match_str: str, record):
        raise NotImplementedError

    def filter(self, query: str) -> Tuple[List, List[str], List[MatchResult]]:
        filtered_line_nos, filtered_lines, filtered_match_results = self._text_matcher.filter(query)
        filtered_records = [self._objects[line_no] for line_no in filtered_line_nos]
        rendered_filtered_lines = []
        for match_str, record in zip(filtered_lines, filtered_records):
            str_for_show = self._str_for_show(match_str, record)
            # to ensure the match results still valid for the str_for_show, the result must have `match_str` as prefix
            assert str_for_show.startswith(match_str)
            rendered_filtered_lines.append(self._str_for_show(match_str, record))
            
        return filtered_records, rendered_filtered_lines, filtered_match_results

class StrSearcher(ListSearcher):
    def _str_for_matcher(self, record):
        return record

    def _str_for_show(self, match_str: str, record):
        return record