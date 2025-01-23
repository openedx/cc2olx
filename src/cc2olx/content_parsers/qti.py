import functools
import logging
import re
from collections import OrderedDict
from pathlib import Path
from typing import Callable, Dict, List, Optional, OrderedDict as OrderedDictType, Union

from cc2olx import filesystem
from cc2olx.constants import QTI_RESPROCESSING_TYPES
from cc2olx.content_parsers import AbstractContentParser
from cc2olx.dataclasses import FibProblemRawAnswers
from cc2olx.enums import CommonCartridgeResourceType, QtiQuestionType
from cc2olx.exceptions import QtiError
from cc2olx.xml import cc_xml

logger = logging.getLogger()


class QtiContentParser(AbstractContentParser):
    """
    QTI resource content parser.
    """

    def _parse_content(self, idref: Optional[str]) -> Optional[List[dict]]:
        if idref:
            if resource := self._cartridge.define_resource(idref):
                if re.match(CommonCartridgeResourceType.QTI_ASSESSMENT, resource["type"]):
                    resource_file = resource["children"][0]
                    resource_file_path = self._cartridge.build_resource_file_path(resource_file.href)
                    return self._parse_qti(resource_file_path)
        return None

    def _parse_qti(self, resource_file_path: Path) -> List[dict]:
        """
        Parse resource of ``imsqti_xmlv1p2/imscc_xmlv1p1/assessment`` type.
        """
        tree = filesystem.get_xml_tree(resource_file_path)
        root = tree.getroot()

        parsed_problems = []

        for index, problem in enumerate(root.items):
            parsed_problems.append(self._parse_problem(problem, index, resource_file_path))

        return parsed_problems

    def _parse_problem(self, problem: cc_xml.QtiItem, problem_index: int, resource_file_path: Path) -> dict:
        """
        Parse a QTI item.

        When the malformed course (due to a weird Canvas behaviour) with equal
        identifiers is gotten, a unique string is added to the raw identifier.
        LMS doesn't support blocks with the same identifiers.
        """
        data = {}

        attributes = problem.attrib

        data["ident"] = attributes["ident"] + str(problem_index)
        if title := attributes.get("title"):
            data["title"] = title

        cc_profile = problem.profile
        data["cc_profile"] = cc_profile

        parse_problem = self._problem_parsers_map.get(cc_profile)

        if parse_problem is None:
            raise QtiError(f'Unknown cc_profile: "{cc_profile}"')

        try:
            data.update(parse_problem(problem))
        except NotImplementedError:
            logger.info("Problem with ID %s can't be converted.", problem.attrib.get("ident"))
            logger.info("    Profile %s is not supported.", cc_profile)
            logger.info("    At file %s.", resource_file_path)

        return data

    @functools.cached_property
    def _problem_parsers_map(self) -> Dict[QtiQuestionType, Callable[[cc_xml.QtiItem], dict]]:
        """
        Provide mapping between CC profile value and problem node type parser.

        Note: Since True/False problems in QTI are constructed identically to
        QTI Multiple Choice problems, we reuse `_parse_multiple_choice_problem`
        for BOOLEAN type problems.
        """
        return {
            QtiQuestionType.MULTIPLE_CHOICE: self._parse_multiple_choice_problem,
            QtiQuestionType.MULTIPLE_RESPONSE: self._parse_multiple_response_problem,
            QtiQuestionType.FILL_IN_THE_BLANK: self._parse_fib_problem,
            QtiQuestionType.ESSAY: self._parse_essay_problem,
            QtiQuestionType.BOOLEAN: self._parse_multiple_choice_problem,
            QtiQuestionType.PATTERN_MATCH: self._parse_pattern_match_problem,
        }

    def _parse_fixed_answer_question_responses(
        self,
        presentation: cc_xml.QtiPresentation,
    ) -> OrderedDictType[str, Dict[str, Union[bool, str]]]:
        """
        Provide mapping with response IDs as keys and response data as values.

        Example of ``<response_lid/>`` structure for the following profiles:
            - ``cc.multiple_choice.v0p1``
            - ``cc.multiple_response.v0p1``
            - ``cc.true_false.v0p1``
        ```
        <response_lid ident="response1" rcardinality="Single">
          <render_choice>
            <response_label ident="8157">
              <material>
                <mattext texttype="text/plain">Response 1</mattext>
              </material>
            </response_label>
            <response_label ident="4226">
              <material>
                <mattext texttype="text/plain">Response 2</mattext>
              </material>
            </response_label>
          </render_choice>
        </response_lid>
        ```
        """
        responses = OrderedDict()

        for response in presentation.response_labels:
            response_id = response.attrib["ident"]
            responses[response_id] = {"text": response.mattext.text or "", "correct": False}

        return responses

    def _mark_correct_responses(self, resprocessing: cc_xml.QtiResprocessing, responses: OrderedDict) -> None:
        """
        Add the information about correctness to responses data.

        Example of ``<resprocessing/>`` structure for the following profiles:
            - ``cc.multiple_choice.v0p1``
            - ``cc.true_false.v0p1``
        ```
        <resprocessing>
          <outcomes>
            <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
          </outcomes>
          <respcondition continue="Yes">
            <conditionvar>
              <varequal respident="response1">8157</varequal>
            </conditionvar>
            <displayfeedback feedbacktype="Response" linkrefid="8157_fb"/>
          </respcondition>
          <respcondition continue="Yes">
            <conditionvar>
              <varequal respident="response1">5534</varequal>
            </conditionvar>
            <displayfeedback feedbacktype="Response" linkrefid="5534_fb"/>
          </respcondition>
          <respcondition continue="No">
            <conditionvar>
              <varequal respident="response1">4226</varequal>
            </conditionvar>
            <setvar action="Set" varname="SCORE">100</setvar>
            <displayfeedback feedbacktype="Response" linkrefid="correct_fb"/>
          </respcondition>
        </resprocessing>
        ```

        This XML is a sort of instruction about how responses should be evaluated. In this
        particular example we have three correct answers with ids: 8157, 5534, 4226.

        Example of ``<resprocessing/>`` structure for ``cc.multiple_response.v0p1``:
        ```
        <resprocessing>
          <outcomes>
            <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
          </outcomes>
          <respcondition continue="No">
            <conditionvar>
              <and>
                <varequal respident="response1">1759</varequal>
                <not>
                  <varequal respident="response1">5954</varequal>
                </not>
                <varequal respident="response1">8170</varequal>
                <varequal respident="response1">9303</varequal>
                <not>
                  <varequal respident="response1">15</varequal>
                </not>
              </and>
            </conditionvar>
          </respcondition>
        </resprocessing>
        ```
        Above example is for a multiple response type problem. In this example 1759, 8170 and
        9303 are correct answers while 15 and 5954 are not. Note that this code also support
        ``or`` opearator too.

        For now, we just consider these responses correct in OLX, but according specification,
        conditions can be arbitrarily nested, and score can be computed by some formula, so to
        implement 100% conversion we need to write new XBlock.
        """
        for respcondition in resprocessing.respconditions:
            correct_answers = respcondition.varequals

            if len(correct_answers) == 0:
                correct_answers = respcondition.and_varequals
                correct_answers += respcondition.or_varequals

            for answer in correct_answers:
                responses[answer.text]["correct"] = True

            if respcondition.attrib.get("continue", "No") == "No":
                break

    def _parse_multiple_choice_problem(self, problem: cc_xml.QtiItem) -> dict:
        """
        Provide the multiple choice problem data.
        """
        choices = self._parse_fixed_answer_question_responses(problem.presentation)
        self._mark_correct_responses(problem.resprocessing, choices)

        return {
            "problem_description": problem.description,
            "choices": choices,
        }

    def _parse_multiple_response_problem(self, problem: cc_xml.QtiItem) -> dict:
        """
        Provide the multiple response problem data.
        """
        return self._parse_multiple_choice_problem(problem)

    def _parse_fib_problem(self, problem: cc_xml.QtiItem) -> dict:
        """
        Provide the Fill-In-The-Blank problem data.
        """
        return {
            "problem_description": problem.description,
            **self._parse_fib_problem_answers(problem),
        }

    def _parse_fib_problem_answers(self, problem: cc_xml.QtiItem) -> dict:
        """
        Parse the Fill-In-The-Blank problem answers data.
        """
        raw_answers = self._parse_fib_problem_raw_answers(problem)

        data = {"is_regexp": bool(raw_answers.answer_patterns)}

        if data["is_regexp"]:
            data.update(self._build_fib_problem_regexp_answers(raw_answers))
        else:
            data.update(self._build_fib_problem_exact_answers(raw_answers))
        return data

    def _parse_fib_problem_raw_answers(self, problem: cc_xml.QtiItem) -> FibProblemRawAnswers:
        """
        Parse the Fill-In-The-Blank problem answers without processing.
        """
        exact_answers = []
        answer_patterns = []

        resprocessing = problem.resprocessing

        for respcondition in resprocessing.respconditions:
            for varequal in respcondition.varequals:
                exact_answers.append(varequal.text)

            for varsubstring in respcondition.varsubstrings:
                answer_patterns.append(varsubstring.text)

            if respcondition.attrib.get("continue", "No") == "No":
                break

        return FibProblemRawAnswers(exact_answers, answer_patterns)

    @staticmethod
    def _build_fib_problem_regexp_answers(raw_answers: FibProblemRawAnswers) -> dict:
        """
        Build the Fill-In-The-Blank problem regular expression answers data.
        """
        exact_answers = raw_answers.exact_answers.copy()
        answer_patterns = raw_answers.answer_patterns.copy()

        data = {"answer": answer_patterns.pop(0)}
        exact_answers = [re.escape(answer) for answer in exact_answers]
        data["additional_answers"] = [*answer_patterns, *exact_answers]

        return data

    @staticmethod
    def _build_fib_problem_exact_answers(raw_answers: FibProblemRawAnswers) -> dict:
        """
        Build the Fill-In-The-Blank problem exact answers data.
        """
        # Primary answer is the first one, additional answers are what is left
        exact_answers = raw_answers.exact_answers.copy()

        return {
            "answer": exact_answers.pop(0),
            "additional_answers": exact_answers,
        }

    def _parse_essay_problem(self, problem: cc_xml.QtiItem) -> dict:
        """
        Parse `cc.essay.v0p1` problem type.

        Provide a dictionary with presentation & sample solution if exists.
        """
        data = {"problem_description": problem.description, **self._parse_essay_feedback(problem)}

        if sample_solution := self._parse_essay_sample_solution(problem):
            data["sample_solution"] = sample_solution

        return data

    def _parse_essay_sample_solution(self, problem: cc_xml.QtiItem) -> Optional[str]:
        """
        Parse the essay sample solution.
        """
        if (solution := problem.solution) is not None:
            return solution.mattext.text
        return None

    def _parse_essay_feedback(self, problem: cc_xml.QtiItem) -> dict:
        """
        Parse the essay feedback.
        """
        data = {}

        if problem.get_itemfeedback() is not None:
            for resp_type in QTI_RESPROCESSING_TYPES:
                if response_text := self._parse_essay_response_text(problem, resp_type):
                    data[resp_type] = response_text

        return data

    def _parse_essay_response_text(self, problem: cc_xml.QtiItem, resp_type: str) -> Optional[str]:
        """
        Parse the essay response text.
        """
        respcondition = problem.resprocessing.respconditions[0]
        if respcondition.get_display_feedback(resp_type) is not None:
            return problem.get_itemfeedback(resp_type).flow_mat.material.mattext.text
        return None

    def _parse_pattern_match_problem(self, problem: cc_xml.QtiItem) -> dict:
        """
        Provide the pattern match problem data.
        """
        raise NotImplementedError
