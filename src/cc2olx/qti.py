import logging
import urllib.parse
import xml.dom.minidom
from collections import OrderedDict
from html import unescape

from lxml import etree, html

from cc2olx import filesystem

from .utils import element_builder

logger = logging.getLogger()

# problem types
MULTIPLE_CHOICE = "cc.multiple_choice.v0p1"
MULTIPLE_RESPONSE = "cc.multiple_response.v0p1"
FILL_IN_THE_BLANK = "cc.fib.v0p1"
ESSAY = "cc.essay.v0p1"
BOOLEAN = "cc.true_false.v0p1"
PATTERN_MATCH = "cc.pattern_match.v0p1"
RESPROCESSING_TYPES = ["general_fb", "correct_fb", "general_incorrect_fb"]


class QtiError(Exception):
    """
    Exception type for Qti parsing/conversion errors.
    """


class QtiExport:
    """
    Contains methods for processing and conversion
    IMS Question & Test Interoperability (QTI) <= v1.2 into OLX markup
    """

    FIB_PROBLEM_TEXTLINE_SIZE_BUFFER = 10

    def __init__(self, root_xml_doc):
        self.doc = root_xml_doc

    def create_qti_node(self, details):
        """
        Creates OLX xml node, that represents content of unit with problems.

        Args:
            details: list of dictionaries, where each contains data to
                render problem.
        """

        problems = []

        for problem_data in details:
            cc_profile = problem_data["cc_profile"]
            create_problem = self._problem_creators_map.get(cc_profile)

            if create_problem is None:
                raise QtiError('Unknown cc_profile: "{}"'.format(problem_data["cc_profile"]))

            problem = create_problem(problem_data)

            # sometimes we might want to have additional items from one cc item
            if isinstance(problem, list) or isinstance(problem, tuple):
                problems += problem
            else:
                problems.append(problem)

        return problems

    @property
    def _problem_creators_map(self):
        """
        Returns: mapping between Common Cartridge profile value and function
            that creates actual problem node.

        Note: Since True/False problems in OLX are constructed identically to
            OLX Multiple Choice problems, we reuse `_create_multiple_choice_problem`
            for BOOLEAN type problems
        """
        return {
            MULTIPLE_CHOICE: self._create_multiple_choice_problem,
            MULTIPLE_RESPONSE: self._create_multiple_response_problem,
            FILL_IN_THE_BLANK: self._create_fib_problem,
            ESSAY: self._create_essay_problem,
            BOOLEAN: self._create_multiple_choice_problem,
            PATTERN_MATCH: self._create_pattern_match_problem,
        }

    def _create_problem_description(self, description_html_str):
        """
        Material texts can come in form of escaped HTML markup, which
        can't be considered as valid XML. ``xml.dom.minidom`` has no
        features to convert HTML to XML, so we use lxml parser here.

        Args:
            description_html_str: escaped HTML string

        Returns: instance of ``xml.dom.minidom.Node``
        """
        description_html_str = unescape(description_html_str)

        description_html_str = urllib.parse.unquote(description_html_str)

        element = html.fromstring(description_html_str)
        xml_string = etree.tostring(element)
        description = xml.dom.minidom.parseString(xml_string).firstChild

        return description

    def _add_choice(self, parent, is_correct, text):
        """
        Appends choices to given ``checkboxgroup`` or ``choicegroup`` parent.
        """
        choice = self.doc.createElement("choice")
        choice.setAttribute("correct", "true" if is_correct else "false")
        self._set_text(choice, text)
        parent.appendChild(choice)

    def _set_text(self, node, new_text):
        text_node = self.doc.createTextNode(new_text)
        node.appendChild(text_node)

    def _create_multiple_choice_problem(self, problem_data):
        """
        Creates XML node of problem.
        """

        problem = self.doc.createElement("problem")
        problem_content = self.doc.createElement("multiplechoiceresponse")

        problem_description = self._create_problem_description(problem_data["problem_description"])

        choice_group = self.doc.createElement("choicegroup")
        choice_group.setAttribute("type", "MultipleChoice")

        for choice_data in problem_data["choices"].values():
            self._add_choice(choice_group, choice_data["correct"], choice_data["text"])

        problem_content.appendChild(problem_description)
        problem_content.appendChild(choice_group)
        problem.appendChild(problem_content)

        return problem

    def _create_multiple_response_problem(self, problem_data):
        """
        Create XML node for multiple response problem. Sets partial_credit to EDC by default.
        """

        el = element_builder(self.doc)

        problem_description = self._create_problem_description(problem_data["problem_description"])

        # fmt: off
        problem = el('problem', [
            el('choiceresponse', [

                problem_description,

                el('checkboxgroup', [
                    el('choice',
                        choice['text'],
                        {'correct': 'true' if choice['correct'] else 'false'}
                       )
                    for choice in problem_data['choices'].values()
                ], {'type': 'MultipleChoice'})

            ], {'partial_credit': 'EDC'})
        ])
        # fmt: on
        return problem

    def _create_fib_problem(self, problem_data):
        """
        Creates XML node of fill in the blank problems
        """

        # Track maximum answer length for textline at the bottom
        max_answer_length = 0

        problem = self.doc.createElement("problem")

        # Set the primary answer on the stringresponse
        # and set the type to case insensitive
        problem_content = self.doc.createElement("stringresponse")
        problem_content.setAttribute("answer", problem_data["answer"])
        problem_content.setAttribute("type", "ci")

        if len(problem_data["answer"]) > max_answer_length:
            max_answer_length = len(problem_data["answer"])

        problem_description = self._create_problem_description(problem_data["problem_description"])
        problem_content.appendChild(problem_description)

        # For any (optional) additional accepted answers, add an
        # additional_answer element with that answer
        for answer in problem_data.get("additional_answers", []):
            additional_answer = self.doc.createElement("additional_answer")
            additional_answer.setAttribute("answer", answer)
            problem_content.appendChild(additional_answer)

            if len(answer) > max_answer_length:
                max_answer_length = len(answer)

        # Add a textline element with the max answer length plus a buffer
        textline = self.doc.createElement("textline")
        textline.setAttribute("size", str(max_answer_length + self.FIB_PROBLEM_TEXTLINE_SIZE_BUFFER))
        problem_content.appendChild(textline)

        problem.appendChild(problem_content)

        return problem

    def _create_essay_problem(self, problem_data):
        """
        Given parsed essay problem data, returns a openassessment component. If a sample
        solution provided, returns that as a HTML block before openassessment.
        """

        description = problem_data["problem_description"]

        el = element_builder(self.doc)

        if any(key in RESPROCESSING_TYPES for key in problem_data.keys()):
            resp_samples = [
                el("name", "Feedback"),
                el("label", "Feedback"),
                el("prompt", "Example Feedback"),
            ]

            for desc, key in zip(["General", "Correct", "Incorrect"], RESPROCESSING_TYPES):
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

        # fmt: off
        ora = el(
            'openassessment',
            [
                el('title', 'Open Response Assessment'),
                el('assessments', [
                    el(
                        'assessment',
                        None,
                        attributes={'name': 'staff-assessment', 'required': 'True'}
                    )
                ]),
                el('prompts', [
                    el('prompt', [
                        el('description', description)
                    ])
                ]),
                el('rubric', [
                    criterion,
                    el('feedbackprompt', 'Feedback prompt text'),
                    el('feedback_default_text', 'Feedback prompt default text'),
                ])
            ],
            {
                'url_name': problem_data['ident'],
                'text_response': 'required',
                'prompts_type': 'html'
            }
        )
        # fmt: on

        # if a sample solution exists add on top of ora, because
        # olx doesn't have a sample solution equivalent.
        if problem_data.get("sample_solution"):
            child = el("html", self.doc.createCDATASection(problem_data["sample_solution"]))
            return child, ora

        return ora

    def _create_pattern_match_problem(self, problem_data):
        raise NotImplementedError


class QtiParser:
    """
    Used to parse Qti xml resource.
    """

    # Xml namespaces
    NS = {"qti": "http://www.imsglobal.org/xsd/ims_qtiasiv1p2"}

    def __init__(self, resource_filename):
        self.resource_filename = resource_filename

    def parse_qti(self):
        """
        Parses resource of ``imsqti_xmlv1p2/imscc_xmlv1p1/assessment`` type.
        """

        tree = filesystem.get_xml_tree(self.resource_filename)
        root = tree.getroot()

        # qti xml can contain multiple problems represented by <item/> elements
        problems = root.findall(".//qti:section[@ident='root_section']/qti:item", self.NS)

        parsed_problems = []

        for i, problem in enumerate(problems):
            data = {}

            attributes = problem.attrib

            # We're adding unique string to identifier here to handle cases,
            # when we're getting malformed course (due to a weird Canvas behaviour)
            # with equal identifiers. LMS doesn't support blocks with the same identifiers.
            data["ident"] = attributes["ident"] + str(i)
            data["title"] = attributes.get("title", "")

            cc_profile = self._parse_problem_profile(problem)
            data["cc_profile"] = cc_profile

            parse_problem = self._problem_parsers_map.get(cc_profile)

            if parse_problem is None:
                raise QtiError(f'Unknown cc_profile: "{cc_profile}"')

            try:
                data.update(parse_problem(problem))
                parsed_problems.append(data)
            except NotImplementedError:
                logger.info("Problem with ID %s can't be converted.", problem.attrib.get("ident"))
                logger.info("    Profile %s is not supported.", cc_profile)
                logger.info("    At file %s.", self.resource_filename)

        return parsed_problems

    def _parse_problem_profile(self, problem):
        """
        Returns ``cc_profile`` value from problem metadata. This field is mandatory for problem,
        so we throw exception if it's not present.

        Example of metadata structure:
        ```
        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>cc_profile</fieldlabel>
              <fieldentry>cc.true_false.v0p1</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
        ```
        """

        metadata = problem.findall("qti:itemmetadata/qti:qtimetadata/qti:qtimetadatafield", self.NS)

        for field in metadata:
            label = field.find("qti:fieldlabel", self.NS).text
            entry = field.find("qti:fieldentry", self.NS).text

            if label == "cc_profile":
                return entry

        raise ValueError('Problem metadata must contain "cc_profile" field.')

    @property
    def _problem_parsers_map(self):
        """
        Returns: mapping between Common Cartridge profile value and function
            that parses actual problem node.

        Note: Since True/False problems in QTI are constructed identically to
            QTI Multiple Choice problems, we reuse `_parse_multiple_choice_problem`
            for BOOLEAN type problems
        """
        return {
            MULTIPLE_CHOICE: self._parse_multiple_choice_problem,
            MULTIPLE_RESPONSE: self._parse_multiple_response_problem,
            FILL_IN_THE_BLANK: self._parse_fib_problem,
            ESSAY: self._parse_essay_problem,
            BOOLEAN: self._parse_multiple_choice_problem,
            PATTERN_MATCH: self._parse_pattern_match_problem,
        }

    def _parse_fixed_answer_question_responses(self, presentation):
        """
        Returns dictionary where keys are response identifiers and values are
        response data.

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

        for response in presentation.findall("qti:response_lid/qti:render_choice/qti:response_label", self.NS):
            response_id = response.attrib["ident"]
            responses[response_id] = {
                "text": response.find("qti:material/qti:mattext", self.NS).text or "",
                "correct": False,
            }

        return responses

    def _mark_correct_responses(self, resprocessing, responses):
        """
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

        for respcondition in resprocessing.findall("qti:respcondition", self.NS):
            correct_answers = respcondition.findall("qti:conditionvar/qti:varequal", self.NS)

            if len(correct_answers) == 0:
                correct_answers = respcondition.findall("qti:conditionvar/qti:and/qti:varequal", self.NS)
                correct_answers += respcondition.findall("qti:conditionvar/qti:or/qti:varequal", self.NS)

            for ans in correct_answers:
                responses[ans.text]["correct"] = True

            if respcondition.attrib["continue"] == "No":
                break

    def _parse_multiple_choice_problem(self, problem):
        """
        Returns ``problem_description``, ``choices`` and marks the correct answer
        """
        data = {}

        presentation = problem.find("qti:presentation", self.NS)
        resprocessing = problem.find("qti:resprocessing", self.NS)

        data["problem_description"] = presentation.find("qti:material/qti:mattext", self.NS).text

        data["choices"] = self._parse_fixed_answer_question_responses(presentation)
        self._mark_correct_responses(resprocessing, data["choices"])

        return data

    def _parse_multiple_response_problem(self, problem):
        """
        Returns ``problem_description``, ``choices`` and marks all the correct answers.
        """
        return self._parse_multiple_choice_problem(problem)

    def _parse_fib_problem(self, problem):
        """
        Returns ``problem_description``, ``answer``, and ``additional_answers``
        """
        data = {}

        presentation = problem.find("qti:presentation", self.NS)
        resprocessing = problem.find("qti:resprocessing", self.NS)

        data["problem_description"] = presentation.find("qti:material/qti:mattext", self.NS).text

        answers = []
        for respcondition in resprocessing.findall("qti:respcondition", self.NS):
            for varequal in respcondition.findall("qti:conditionvar/qti:varequal", self.NS):
                answers.append(varequal.text)

            if respcondition.attrib["continue"] == "No":
                break

        # Primary answer is the first one, additional answers are what is left
        data["answer"] = answers.pop(0)
        data["additional_answers"] = answers

        return data

    def _parse_essay_problem(self, problem):
        """
        Parses `cc.essay.v0p1` problem type and returns dictionary with
        presentation & sample solution if exists.
        """

        data = {}
        presentation = problem.find("qti:presentation", self.NS)
        itemfeedback = problem.find("qti:itemfeedback", self.NS)
        solution = problem.find("qti:itemfeedback/qti:solution", self.NS)

        data["problem_description"] = presentation.find("qti:material/qti:mattext", self.NS).text

        if solution is not None:
            sample_solution_selector = "qti:solutionmaterial/qti:material/qti:mattext"
            data["sample_solution"] = solution.find(sample_solution_selector, self.NS).text

        if itemfeedback is not None:
            for resp_type in RESPROCESSING_TYPES:
                response_text = self._essay_response_processing(problem, resp_type)
                if response_text:
                    data[resp_type] = response_text
        return data

    def _essay_response_processing(self, problem, resp_type):
        respconditions = problem.find("qti:resprocessing/qti:respcondition", self.NS)
        if respconditions.find(f"qti:displayfeedback[@linkrefid='{resp_type}']", self.NS) is not None:
            text_selector = f"qti:itemfeedback[@ident='{resp_type}']/qti:flow_mat/qti:material/qti:mattext"
            return problem.find(text_selector, self.NS).text

    def _parse_pattern_match_problem(self, problem):
        raise NotImplementedError
