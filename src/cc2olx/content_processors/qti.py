import functools
import logging
import re
import urllib.parse
import xml.dom.minidom
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from html import unescape
from pathlib import Path
from typing import Callable, Collection, Dict, List, Optional, OrderedDict as OrderedDictType, Tuple, Union

from lxml import etree, html

from cc2olx import filesystem
from cc2olx.content_processors import AbstractContentProcessor
from cc2olx.enums import CommonCartridgeResourceType
from cc2olx.utils import element_builder
from cc2olx.xml import cc_xml

QTI_RESPROCESSING_TYPES = ["general_fb", "correct_fb", "general_incorrect_fb"]

logger = logging.getLogger()


class QtiError(Exception):
    """
    Exception type for QTI parsing/conversion errors.
    """


class QtiQuestionType(str, Enum):
    """
    Enumerate QTI question types.
    """

    MULTIPLE_CHOICE = "cc.multiple_choice.v0p1"
    MULTIPLE_RESPONSE = "cc.multiple_response.v0p1"
    FILL_IN_THE_BLANK = "cc.fib.v0p1"
    ESSAY = "cc.essay.v0p1"
    BOOLEAN = "cc.true_false.v0p1"
    PATTERN_MATCH = "cc.pattern_match.v0p1"


@dataclass
class FibProblemRawAnswers:
    """
    Encapsulate answers data for a Fill-In-The-Blank problem.
    """

    exact_answers: List[str]
    answer_patterns: List[str]


class QtiContentProcessor(AbstractContentProcessor):
    """
    QTI content processor.
    """

    FIB_PROBLEM_TEXTLINE_SIZE_BUFFER = 10

    def process(self, resource: dict, idref: str) -> Optional[List[xml.dom.minidom.Element]]:
        if content := self._parse(resource):
            return self._create_nodes(content)
        return None

    def _parse(self, resource: dict) -> Optional[List[dict]]:
        """
        Parse the resource content.
        """
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

    @staticmethod
    def _parse_fixed_answer_question_responses(
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

    @staticmethod
    def _mark_correct_responses(resprocessing: cc_xml.QtiResprocessing, responses: OrderedDict) -> None:
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

    @staticmethod
    def _parse_fib_problem_raw_answers(problem: cc_xml.QtiItem) -> FibProblemRawAnswers:
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

    def _create_nodes(self, content: List[dict]) -> List[xml.dom.minidom.Element]:
        """
        Give out <problem> or <openassessment> OLX nodes.
        """
        problems = []

        for problem_data in content:
            cc_profile = problem_data["cc_profile"]
            create_problem = self._problem_creators_map.get(cc_profile)

            if create_problem is None:
                raise QtiError('Unknown cc_profile: "{}"'.format(problem_data["cc_profile"]))

            doc = xml.dom.minidom.Document()
            problem = create_problem(problem_data, doc)

            # sometimes we might want to have additional items from one CC item
            if isinstance(problem, list) or isinstance(problem, tuple):
                problems += problem
            else:
                problems.append(problem)

        return problems

    @functools.cached_property
    def _problem_creators_map(
        self,
    ) -> Dict[
        QtiQuestionType,
        Callable[[dict, xml.dom.minidom.Document], Union[xml.dom.minidom.Element, Collection[xml.dom.minidom.Element]]],
    ]:
        """
        Provide CC profile value to actual problem node creators mapping.

        Note: Since True/False problems in OLX are constructed identically to
        OLX Multiple Choice problems, we reuse `_create_multiple_choice_problem`
        for BOOLEAN type problems
        """
        return {
            QtiQuestionType.MULTIPLE_CHOICE: self._create_multiple_choice_problem,
            QtiQuestionType.MULTIPLE_RESPONSE: self._create_multiple_response_problem,
            QtiQuestionType.FILL_IN_THE_BLANK: self._create_fib_problem,
            QtiQuestionType.ESSAY: self._create_essay_problem,
            QtiQuestionType.BOOLEAN: self._create_multiple_choice_problem,
            QtiQuestionType.PATTERN_MATCH: self._create_pattern_match_problem,
        }

    @staticmethod
    def _create_problem_description(description_html_str: str) -> xml.dom.minidom.Element:
        """
        Create a problem description node.

        Material texts can come in form of escaped HTML markup, which
        can't be considered as valid XML. ``xml.dom.minidom`` has no
        features to convert HTML to XML, so we use lxml parser here.
        """
        description_html_str = unescape(description_html_str)

        description_html_str = urllib.parse.unquote(description_html_str)

        element = html.fromstring(description_html_str)
        xml_string = etree.tostring(element)
        return xml.dom.minidom.parseString(xml_string).firstChild

    def _add_choice(
        self,
        parent: xml.dom.minidom.Element,
        is_correct: bool,
        text: str,
        doc: xml.dom.minidom.Document,
    ) -> None:
        """
        Append choices to given ``checkboxgroup`` or ``choicegroup`` parent.
        """
        choice = doc.createElement("choice")
        choice.setAttribute("correct", "true" if is_correct else "false")
        self._set_text(choice, text, doc)
        parent.appendChild(choice)

    @staticmethod
    def _set_text(node: xml.dom.minidom.Element, new_text: str, doc: xml.dom.minidom.Document) -> None:
        """
        Set a node text.
        """
        text_node = doc.createTextNode(new_text)
        node.appendChild(text_node)

    def _create_multiple_choice_problem(
        self,
        problem_data: dict,
        doc: xml.dom.minidom.Document,
    ) -> xml.dom.minidom.Element:
        """
        Create multiple choice problem OLX.
        """
        problem = doc.createElement("problem")
        problem_content = doc.createElement("multiplechoiceresponse")

        problem_description = self._create_problem_description(problem_data["problem_description"])

        choice_group = doc.createElement("choicegroup")
        choice_group.setAttribute("type", "MultipleChoice")

        for choice_data in problem_data["choices"].values():
            self._add_choice(choice_group, choice_data["correct"], choice_data["text"], doc)

        problem_content.appendChild(problem_description)
        problem_content.appendChild(choice_group)
        problem.appendChild(problem_content)

        return problem

    def _create_multiple_response_problem(
        self,
        problem_data: dict,
        doc: xml.dom.minidom.Document,
    ) -> xml.dom.minidom.Element:
        """
        Create multiple response problem OLX.

        Set partial_credit to EDC by default.
        """
        el = element_builder(doc)

        problem_description = self._create_problem_description(problem_data["problem_description"])

        problem = el(
            "problem",
            [
                el(
                    "choiceresponse",
                    [
                        problem_description,
                        el(
                            "checkboxgroup",
                            [
                                el(
                                    "choice",
                                    choice["text"],
                                    {"correct": "true" if choice["correct"] else "false"},
                                )
                                for choice in problem_data["choices"].values()
                            ],
                            {"type": "MultipleChoice"},
                        ),
                    ],
                    {"partial_credit": "EDC"},
                ),
            ],
        )
        return problem

    def _create_fib_problem(self, problem_data: dict, doc: xml.dom.minidom.Document) -> xml.dom.minidom.Element:
        """
        Create Fill-In-The-Blank problem OLX.
        """
        # Track maximum answer length for textline at the bottom
        max_answer_length = 0

        problem = doc.createElement("problem")

        # Set the primary answer on the stringresponse
        # and set the type to case insensitive
        problem_content = doc.createElement("stringresponse")
        problem_content.setAttribute("answer", problem_data["answer"])
        problem_content.setAttribute("type", self._build_fib_problem_type(problem_data))

        if len(problem_data["answer"]) > max_answer_length:
            max_answer_length = len(problem_data["answer"])

        problem_description = self._create_problem_description(problem_data["problem_description"])
        problem_content.appendChild(problem_description)

        # For any (optional) additional accepted answers, add an
        # additional_answer element with that answer
        for answer in problem_data.get("additional_answers", []):
            additional_answer = doc.createElement("additional_answer")
            additional_answer.setAttribute("answer", answer)
            problem_content.appendChild(additional_answer)

            if len(answer) > max_answer_length:
                max_answer_length = len(answer)

        # Add a textline element with the max answer length plus a buffer
        textline = doc.createElement("textline")
        textline.setAttribute("size", str(max_answer_length + self.FIB_PROBLEM_TEXTLINE_SIZE_BUFFER))
        problem_content.appendChild(textline)

        problem.appendChild(problem_content)

        return problem

    @staticmethod
    def _build_fib_problem_type(problem_data: dict) -> str:
        """
        Build `stringresponse` OLX type for a Fill-In-The-Blank problem.
        """
        problem_types = ["ci"]

        if problem_data["is_regexp"]:
            problem_types.append("regexp")

        return " ".join(problem_types)

    def _create_essay_problem(
        self,
        problem_data: dict,
        doc: xml.dom.minidom.Document,
    ) -> Union[xml.dom.minidom.Element, Tuple[xml.dom.minidom.Element, xml.dom.minidom.Element]]:
        """
        Create an essay problem OLX.

        Given parsed essay problem data, returns a openassessment component. If a sample
        solution provided, returns that as a HTML block before openassessment.
        """
        el = element_builder(doc)

        if any(key in QTI_RESPROCESSING_TYPES for key in problem_data.keys()):
            resp_samples = [
                el("name", "Feedback"),
                el("label", "Feedback"),
                el("prompt", "Example Feedback"),
            ]

            for desc, key in zip(["General", "Correct", "Incorrect"], QTI_RESPROCESSING_TYPES):
                resp_samples.append(
                    el(
                        "option",
                        [el("name", desc), el("label", desc), el("explanation", problem_data.get(key, desc))],
                        {"points": "0"},
                    )
                )
            criterion = el("criterion", resp_samples, {"feedback": "optional"})
        else:
            criterion = el(
                "criterion",
                [
                    el("name", "Ideas"),
                    el("label", "Ideas"),
                    el("prompt", "Example criterion"),
                    el(
                        "option",
                        [el("name", "Poor"), el("label", "Poor"), el("explanation", "Explanation")],
                        {"points": "0"},
                    ),
                    el(
                        "option",
                        [el("name", "Good"), el("label", "Good"), el("explanation", "Explanation")],
                        {"points": "1"},
                    ),
                ],
                {"feedback": "optional"},
            )

        description = problem_data["problem_description"]
        ora = el(
            "openassessment",
            [
                el("title", "Open Response Assessment"),
                el(
                    "assessments",
                    [
                        el("assessment", None, attributes={"name": "staff-assessment", "required": "True"}),
                    ],
                ),
                el(
                    "prompts",
                    [
                        el(
                            "prompt",
                            [el("description", description)],
                        ),
                    ],
                ),
                el(
                    "rubric",
                    [
                        criterion,
                        el("feedbackprompt", "Feedback prompt text"),
                        el("feedback_default_text", "Feedback prompt default text"),
                    ],
                ),
            ],
            {
                "url_name": problem_data["ident"],
                "text_response": "required",
                "prompts_type": "html",
            },
        )

        # if a sample solution exists add on top of ora, because
        # olx doesn't have a sample solution equivalent.
        if problem_data.get("sample_solution"):
            child = el("html", doc.createCDATASection(problem_data["sample_solution"]))
            return child, ora

        return ora

    def _create_pattern_match_problem(
        self,
        problem_data: dict,
        doc: xml.dom.minidom.Document,
    ) -> xml.dom.minidom.Element:
        """
        Create pattern match problem OLX.
        """
        raise NotImplementedError
