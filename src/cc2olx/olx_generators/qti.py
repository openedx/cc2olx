import functools
import urllib.parse
import xml.dom.minidom
from html import unescape
from typing import Callable, Collection, Dict, List, Tuple, Union

from lxml import etree, html

from cc2olx.constants import QTI_RESPROCESSING_TYPES
from cc2olx.enums import QtiQuestionType
from cc2olx.exceptions import QtiError
from cc2olx.olx_generators import AbstractOlxGenerator
from cc2olx.utils import element_builder


class QtiOlxGenerator(AbstractOlxGenerator):
    """
    Generate OLX for QTIs.
    """

    FIB_PROBLEM_TEXTLINE_SIZE_BUFFER = 10

    def create_nodes(self, content: List[dict]) -> List[xml.dom.minidom.Element]:
        problems = []

        for problem_data in content:
            cc_profile = problem_data["cc_profile"]
            create_problem = self._problem_creators_map.get(cc_profile)

            if create_problem is None:
                raise QtiError('Unknown cc_profile: "{}"'.format(problem_data["cc_profile"]))

            problem = create_problem(problem_data)

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
        Callable[[dict], Union[xml.dom.minidom.Element, Collection[xml.dom.minidom.Element]]],
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

    def _add_choice(self, parent: xml.dom.minidom.Element, is_correct: bool, text: str) -> None:
        """
        Append choices to given ``checkboxgroup`` or ``choicegroup`` parent.
        """
        choice = self._doc.createElement("choice")
        choice.setAttribute("correct", "true" if is_correct else "false")
        self._set_text(choice, text)
        parent.appendChild(choice)

    def _set_text(self, node: xml.dom.minidom.Element, new_text: str) -> None:
        """
        Set a node text.
        """
        text_node = self._doc.createTextNode(new_text)
        node.appendChild(text_node)

    def _create_multiple_choice_problem(self, problem_data: dict) -> xml.dom.minidom.Element:
        """
        Create multiple choice problem OLX.
        """
        problem = self._doc.createElement("problem")
        problem_content = self._doc.createElement("multiplechoiceresponse")

        problem_description = self._create_problem_description(problem_data["problem_description"])

        choice_group = self._doc.createElement("choicegroup")
        choice_group.setAttribute("type", "MultipleChoice")

        for choice_data in problem_data["choices"].values():
            self._add_choice(choice_group, choice_data["correct"], choice_data["text"])

        problem_content.appendChild(problem_description)
        problem_content.appendChild(choice_group)
        problem.appendChild(problem_content)

        return problem

    def _create_multiple_response_problem(self, problem_data: dict) -> xml.dom.minidom.Element:
        """
        Create multiple response problem OLX.

        Set partial_credit to EDC by default.
        """
        el = element_builder(self._doc)

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

    def _create_fib_problem(self, problem_data: dict) -> xml.dom.minidom.Element:
        """
        Create Fill-In-The-Blank problem OLX.
        """
        # Track maximum answer length for textline at the bottom
        max_answer_length = 0

        problem = self._doc.createElement("problem")

        # Set the primary answer on the stringresponse
        # and set the type to case insensitive
        problem_content = self._doc.createElement("stringresponse")
        problem_content.setAttribute("answer", problem_data["answer"])
        problem_content.setAttribute("type", self._build_fib_problem_type(problem_data))

        if len(problem_data["answer"]) > max_answer_length:
            max_answer_length = len(problem_data["answer"])

        problem_description = self._create_problem_description(problem_data["problem_description"])
        problem_content.appendChild(problem_description)

        # For any (optional) additional accepted answers, add an
        # additional_answer element with that answer
        for answer in problem_data.get("additional_answers", []):
            additional_answer = self._doc.createElement("additional_answer")
            additional_answer.setAttribute("answer", answer)
            problem_content.appendChild(additional_answer)

            if len(answer) > max_answer_length:
                max_answer_length = len(answer)

        # Add a textline element with the max answer length plus a buffer
        textline = self._doc.createElement("textline")
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
    ) -> Union[xml.dom.minidom.Element, Tuple[xml.dom.minidom.Element, xml.dom.minidom.Element]]:
        """
        Create an essay problem OLX.

        Given parsed essay problem data, returns a openassessment component. If a sample
        solution provided, returns that as a HTML block before openassessment.
        """
        el = element_builder(self._doc)

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
            child = el("html", self._doc.createCDATASection(problem_data["sample_solution"]))
            return child, ora

        return ora

    def _create_pattern_match_problem(self, problem_data: dict) -> xml.dom.minidom.Element:
        """
        Create pattern match problem OLX.
        """
        raise NotImplementedError
