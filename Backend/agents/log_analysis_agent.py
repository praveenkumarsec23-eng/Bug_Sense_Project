# =========================================================
# BUGSENSE - LOG ANALYSIS AGENT
# =========================================================

import re


class LogAnalysisAgent:

    def __init__(self):
        self.name = "Log Analysis Agent"

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        error_message="",
        stack_trace="",
        code="",
        language=""
    ):
        error_message = error_message or ""
        stack_trace = stack_trace or ""
        code = code or ""
        language = language or ""

        combined_text = "\n".join([
            error_message,
            stack_trace
        ])

        exception = self._detect_exception(combined_text)

        inferred_failure = None

        if not exception and code.strip():
            inferred_failure = self._infer_exception_from_source(
                code=code,
                language=language
            )

            if inferred_failure:
                exception = inferred_failure.get("exception")

        file_name = self._detect_file(stack_trace)
        line_number = self._detect_line(stack_trace)

        function_name = self._detect_function(
            stack_trace=stack_trace,
            language=language
        )

        failure_code = self._detect_failure_code(
            code=code,
            stack_trace=stack_trace,
            line_number=line_number,
            language=language
        )

        if inferred_failure:

            inferred_code = inferred_failure.get("failure_code")
            inferred_line = inferred_failure.get("line")
            inferred_function = inferred_failure.get("function")

            if inferred_code:
                failure_code = inferred_code

            if line_number is None and inferred_line is not None:
                line_number = inferred_line

            if not function_name and inferred_function:
                function_name = inferred_function

        return {
            "agent": self.name,
            "exception": exception,
            "file": file_name,
            "line": line_number,
            "function": function_name,
            "failure_code": failure_code,
            "language": language
        }

       # =====================================================
    # SOURCE-CODE EXCEPTION INFERENCE
    # =====================================================

    def _infer_exception_from_source(
        self,
        code,
        language=""
    ):
        if not code.strip():
            return None

        language_value = (
            language or ""
        ).strip().lower()

        # -------------------------------------------------
        # PYTHON
        # -------------------------------------------------

        if language_value == "python":

            result = self._infer_python_exception(
                code
            )

            if result:
                return result

        # -------------------------------------------------
        # JAVA
        # -------------------------------------------------

        if language_value == "java":

            result = self._infer_java_exception(
                code
            )

            if result:
                return result

        # -------------------------------------------------
        # JAVASCRIPT / TYPESCRIPT
        # -------------------------------------------------

        if language_value in [
            "javascript",
            "js",
            "typescript",
            "ts"
        ]:

            result = self._infer_javascript_exception(
                code,
                is_typescript=language_value in [
                    "typescript",
                    "ts"
                ]
            )

            if result:
                return result

        # -------------------------------------------------
        # C / C++
        # -------------------------------------------------

        if language_value in [
            "c",
            "c++",
            "cpp",
            "cc",
            "cxx"
        ]:

            result = self._infer_c_cpp_exception(
                code
            )

            if result:
                return result

        # -------------------------------------------------
        # C#
        # -------------------------------------------------

        if language_value in [
            "c#",
            "csharp",
            "cs"
        ]:

            result = self._infer_csharp_exception(
                code
            )

            if result:
                return result

        # -------------------------------------------------
        # PHP
        # -------------------------------------------------

        if language_value == "php":

            result = self._infer_php_exception(
                code
            )

            if result:
                return result

        # -------------------------------------------------
        # NO SOURCE-ONLY EXCEPTION FOUND
        # -------------------------------------------------

        return None
        # =====================================================
    # C / C++ SOURCE INFERENCE
    # =====================================================

    def _infer_c_cpp_exception(
        self,
        code
    ):
        lines = code.splitlines()

        null_variables = set()

        # Detect variables explicitly assigned NULL or nullptr.
        #
        # Examples:
        # int *ptr = NULL;
        # User *user = nullptr;
        # ptr = NULL;

        declaration_pattern = re.compile(
            r'^\s*'
            r'(?:const\s+)?'
            r'(?:struct\s+)?'
            r'[A-Za-z_]\w*'
            r'(?:\s+[A-Za-z_]\w*)*'
            r'\s*\*+\s*'
            r'([A-Za-z_]\w*)'
            r'\s*=\s*'
            r'(?:NULL|nullptr)'
            r'\s*;'
        )

        assignment_pattern = re.compile(
            r'^\s*'
            r'([A-Za-z_]\w*)'
            r'\s*=\s*'
            r'(?:NULL|nullptr)'
            r'\s*;'
        )

        for line in lines:

            match = declaration_pattern.match(
                line
            )

            if not match:
                match = assignment_pattern.match(
                    line
                )

            if match:
                null_variables.add(
                    match.group(1)
                )

        if not null_variables:
            return None

               # -----------------------------------------------
        # DIRECT NULL POINTER DEREFERENCE
        # -----------------------------------------------
        #
        # Example:
        # int *ptr = NULL;
        # printf("%d", *ptr);

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            for variable_name in null_variables:

                # Ignore pointer declarations and function parameters.
                #
                # int *ptr = NULL;
                # void printValue(int *ptr) {
                #
                # "*ptr" here declares a pointer.
                # It is NOT a pointer dereference.

                pointer_declaration = re.search(
                    rf'\b[A-Za-z_]\w*'
                    rf'(?:\s+[A-Za-z_]\w*)*'
                    rf'\s*\*+\s*'
                    rf'{re.escape(variable_name)}'
                    rf'\b',
                    stripped
                )

                if pointer_declaration:
                    continue

                # Detect:
                # *ptr

                direct_dereference = re.compile(
                    rf'(?<![A-Za-z0-9_])'
                    rf'\*\s*{re.escape(variable_name)}'
                    rf'\b'
                )

                # Detect:
                # ptr->value

                arrow_dereference = re.compile(
                    rf'\b{re.escape(variable_name)}'
                    r'\s*->\s*'
                    r'[A-Za-z_]\w*'
                )

                if (
                    direct_dereference.search(stripped)
                    or arrow_dereference.search(stripped)
                ):
                    return {
                        "exception":
                            "Segmentation fault",

                        "failure_code":
                            stripped,

                        "line":
                            index + 1,

                        "function":
                            self._find_c_cpp_function_for_line(
                                lines,
                                index
                            ),

                        "evidence":
                            (
                                f"{variable_name} is assigned "
                                "NULL/nullptr and is later "
                                "dereferenced"
                            )
                    }

        # -----------------------------------------------
        # NULL POINTER PASSED INTO FUNCTION
        # -----------------------------------------------

        function_pattern = re.compile(
            r'^\s*'
            r'(?:[A-Za-z_]\w*'
            r'(?:\s*\*+)?\s+)+'
            r'([A-Za-z_]\w*)'
            r'\s*\(([^)]*)\)'
            r'\s*\{'
        )

        functions = []

        for function_index, line in enumerate(
            lines
        ):

            match = function_pattern.match(
                line
            )

            if not match:
                continue

            function_name = match.group(1)

            parameters = [
                parameter.strip()
                for parameter
                in match.group(2).split(",")
                if parameter.strip()
            ]

            parameter_names = []

            for parameter in parameters:

                parameter_match = re.search(
                    r'\*+\s*'
                    r'([A-Za-z_]\w*)'
                    r'\s*$',
                    parameter
                )

                if parameter_match:
                    parameter_names.append(
                        parameter_match.group(1)
                    )
                else:
                    normal_match = re.search(
                        r'([A-Za-z_]\w*)'
                        r'\s*$',
                        parameter
                    )

                    parameter_names.append(
                        normal_match.group(1)
                        if normal_match
                        else None
                    )

            brace_depth = (
                line.count("{")
                - line.count("}")
            )

            end_index = function_index

            for body_index in range(
                function_index + 1,
                len(lines)
            ):

                brace_depth += (
                    lines[body_index].count("{")
                    - lines[body_index].count("}")
                )

                end_index = body_index

                if brace_depth <= 0:
                    break

            functions.append({
                "name": function_name,
                "parameters": parameter_names,
                "start": function_index,
                "end": end_index
            })

        for function in functions:

            for parameter_index, parameter in enumerate(
                function["parameters"]
            ):

                if not parameter:
                    continue

                failure = None

                for body_index in range(
                    function["start"] + 1,
                    function["end"]
                ):

                    stripped = lines[
                        body_index
                    ].strip()

                    if not self._is_meaningful_code_line(
                        stripped
                    ):
                        continue

                    pointer_dereference = re.compile(
                        rf'(?<![A-Za-z0-9_])'
                        rf'\*\s*{re.escape(parameter)}'
                        rf'\b'
                    )

                    arrow_dereference = re.compile(
                        rf'\b{re.escape(parameter)}'
                        r'\s*->\s*'
                        r'[A-Za-z_]\w*'
                    )

                    if (
                        pointer_dereference.search(stripped)
                        or arrow_dereference.search(stripped)
                    ):
                        failure = {
                            "code": stripped,
                            "line": body_index + 1
                        }
                        break

                if not failure:
                    continue

                call_pattern = re.compile(
                    rf'\b{re.escape(function["name"])}'
                    r'\s*\(([^)]*)\)'
                )

                for call_index, call_line in enumerate(
                    lines
                ):

                    if (
                        function["start"]
                        <= call_index
                        <= function["end"]
                    ):
                        continue

                    for call_match in call_pattern.finditer(
                        call_line
                    ):

                        arguments = [
                            argument.strip()
                            for argument
                            in call_match.group(1).split(",")
                        ]

                        if parameter_index >= len(arguments):
                            continue

                        argument = arguments[
                            parameter_index
                        ]

                        if (
                            argument in [
                                "NULL",
                                "nullptr"
                            ]
                            or argument in null_variables
                        ):
                            return {
                                "exception":
                                    "Segmentation fault",

                                "failure_code":
                                    failure["code"],

                                "line":
                                    failure["line"],

                                "function":
                                    function["name"],

                                "evidence":
                                    (
                                        f"{function['name']}() "
                                        f"receives a null pointer "
                                        f"for {parameter} and "
                                        "dereferences it"
                                    )
                            }

        return None

    # =====================================================
    # FIND C / C++ FUNCTION
    # =====================================================

    def _find_c_cpp_function_for_line(
        self,
        lines,
        target_index
    ):
        function_pattern = re.compile(
            r'^\s*'
            r'(?:[A-Za-z_]\w*'
            r'(?:\s*\*+)?\s+)+'
            r'([A-Za-z_]\w*)'
            r'\s*\([^;]*\)'
            r'\s*\{'
        )

        for index in range(
            target_index,
            -1,
            -1
        ):

            match = function_pattern.match(
                lines[index]
            )

            if match:
                return match.group(1)

        return None
    # =====================================================
    # JAVASCRIPT / TYPESCRIPT SOURCE INFERENCE
    # =====================================================

    def _infer_javascript_exception(
        self,
        code,
        is_typescript=False
    ):
        lines = code.splitlines()

        invalid_variables = set()

        # -------------------------------------------------
        # NULL / UNDEFINED VARIABLE ASSIGNMENTS
        # -------------------------------------------------
        #
        # JavaScript:
        # let user = null;
        #
        # TypeScript:
        # let user: User | null = null;
        # const data: Profile | undefined = undefined;

        assignment_pattern = re.compile(
            r'^\s*'
            r'(?:let|const|var)\s+'
            r'([A-Za-z_$][\w$]*)'
            r'(?:\s*:\s*[^=;]+)?'
            r'\s*=\s*'
            r'(null|undefined)'
            r'\s*;?\s*$'
        )

        for line in lines:
            match = assignment_pattern.match(line)

            if match:
                invalid_variables.add(
                    match.group(1)
                )

        # -------------------------------------------------
        # DIRECT NULL / UNDEFINED DEREFERENCE
        # -------------------------------------------------

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            for variable_name in invalid_variables:

                # Do not treat optional chaining as an error.
                optional_pattern = re.compile(
                    rf'\b{re.escape(variable_name)}'
                    r'\s*\?\.\s*'
                )

                if optional_pattern.search(stripped):
                    continue

                property_pattern = re.compile(
                    rf'\b{re.escape(variable_name)}'
                    r'\s*\.\s*'
                    r'[A-Za-z_$][\w$]*'
                )

                if property_pattern.search(stripped):

                    # Ignore the assignment itself.
                    if re.search(
                        rf'\b{re.escape(variable_name)}'
                        r'(?:\s*:\s*[^=;]+)?'
                        r'\s*=\s*'
                        r'(?:null|undefined)',
                        stripped
                    ):
                        continue

                    return {
                        "exception": "TypeError",
                        "failure_code": stripped,
                        "line": index + 1,
                        "function":
                            self._find_javascript_function_for_line(
                                lines,
                                index
                            ),
                        "evidence":
                            (
                                f"{variable_name} is assigned "
                                "null or undefined and is later "
                                "dereferenced"
                            )
                    }

        # -------------------------------------------------
        # FUNCTION DECLARATIONS
        # -------------------------------------------------
        #
        # JavaScript:
        # function printUserName(user) {
        #
        # TypeScript:
        # function printUserName(user: User | null) {

        function_pattern = re.compile(
            r'^\s*function\s+'
            r'([A-Za-z_$][\w$]*)'
            r'\s*\(([^)]*)\)'
            r'(?:\s*:\s*[^{]+)?'
            r'\s*\{'
        )

        functions = []

        for function_index, line in enumerate(lines):

            function_match = function_pattern.match(line)

            if not function_match:
                continue

            function_name = function_match.group(1)

            raw_parameters = self._split_js_parameters(
                function_match.group(2)
            )

            parameters = []

            for parameter in raw_parameters:

                parameter_name = (
                    self._extract_js_parameter_name(
                        parameter
                    )
                )

                if parameter_name:
                    parameters.append(parameter_name)

            brace_depth = (
                line.count("{")
                - line.count("}")
            )

            end_index = function_index

            for body_index in range(
                function_index + 1,
                len(lines)
            ):

                brace_depth += (
                    lines[body_index].count("{")
                    - lines[body_index].count("}")
                )

                end_index = body_index

                if brace_depth <= 0:
                    break

            functions.append({
                "name": function_name,
                "parameters": parameters,
                "start": function_index,
                "end": end_index
            })

        # -------------------------------------------------
        # FUNCTION PARAMETER DEREFERENCE
        # -------------------------------------------------

        for function in functions:

            function_name = function["name"]
            parameters = function["parameters"]

            if not parameters:
                continue

            for body_index in range(
                function["start"] + 1,
                function["end"]
            ):

                stripped = lines[
                    body_index
                ].strip()

                if not self._is_meaningful_code_line(
                    stripped
                ):
                    continue

                for parameter_index, parameter in enumerate(
                    parameters
                ):

                    # Optional chaining is safe.
                    optional_pattern = re.compile(
                        rf'\b{re.escape(parameter)}'
                        r'\s*\?\.\s*'
                    )

                    if optional_pattern.search(stripped):
                        continue

                    property_pattern = re.compile(
                        rf'\b{re.escape(parameter)}'
                        r'\s*\.\s*'
                        r'[A-Za-z_$][\w$]*'
                    )

                    if not property_pattern.search(
                        stripped
                    ):
                        continue

                    call_pattern = re.compile(
                        rf'\b{re.escape(function_name)}'
                        r'\s*\(([^)]*)\)'
                    )

                    for call_index, call_line in enumerate(
                        lines
                    ):

                        if (
                            function["start"]
                            <= call_index
                            <= function["end"]
                        ):
                            continue

                        for call_match in call_pattern.finditer(
                            call_line
                        ):

                            arguments = self._split_js_parameters(
                                call_match.group(1)
                            )

                            if (
                                parameter_index
                                >= len(arguments)
                            ):
                                continue

                            argument = arguments[
                                parameter_index
                            ].strip()

                            # Direct null/undefined argument.
                            if argument in [
                                "null",
                                "undefined"
                            ]:
                                return {
                                    "exception": "TypeError",
                                    "failure_code": stripped,
                                    "line": body_index + 1,
                                    "function": function_name,
                                    "evidence":
                                        (
                                            f"{function_name}() "
                                            f"receives {argument} "
                                            f"for {parameter}"
                                        )
                                }

                            # Variable known to contain null/undefined.
                            if argument in invalid_variables:
                                return {
                                    "exception": "TypeError",
                                    "failure_code": stripped,
                                    "line": body_index + 1,
                                    "function": function_name,
                                    "evidence":
                                        (
                                            f"{function_name}() "
                                            f"receives {argument}, "
                                            "which is null or undefined"
                                        )
                                }

        return None

    # =====================================================
    # JAVASCRIPT / TYPESCRIPT PARAMETER SPLITTER
    # =====================================================

    def _split_js_parameters(
        self,
        value
    ):
        if not value.strip():
            return []

        result = []
        current = []

        angle_depth = 0
        square_depth = 0
        brace_depth = 0
        parenthesis_depth = 0

        for character in value:

            if character == "<":
                angle_depth += 1

            elif character == ">":
                angle_depth = max(
                    0,
                    angle_depth - 1
                )

            elif character == "[":
                square_depth += 1

            elif character == "]":
                square_depth = max(
                    0,
                    square_depth - 1
                )

            elif character == "{":
                brace_depth += 1

            elif character == "}":
                brace_depth = max(
                    0,
                    brace_depth - 1
                )

            elif character == "(":
                parenthesis_depth += 1

            elif character == ")":
                parenthesis_depth = max(
                    0,
                    parenthesis_depth - 1
                )

            if (
                character == ","
                and angle_depth == 0
                and square_depth == 0
                and brace_depth == 0
                and parenthesis_depth == 0
            ):
                result.append(
                    "".join(current).strip()
                )

                current = []
                continue

            current.append(character)

        if current:
            result.append(
                "".join(current).strip()
            )

        return [
            item
            for item in result
            if item
        ]

    # =====================================================
    # TYPESCRIPT PARAMETER NAME EXTRACTION
    # =====================================================

    def _extract_js_parameter_name(
        self,
        parameter
    ):
        parameter = (
            parameter or ""
        ).strip()

        if not parameter:
            return None

        # Remove rest parameter marker.
        if parameter.startswith("..."):
            parameter = parameter[3:].strip()

        # Remove default value.
        if "=" in parameter:
            parameter = parameter.split(
                "=",
                1
            )[0].strip()

        # Remove TypeScript type annotation.
        if ":" in parameter:
            parameter = parameter.split(
                ":",
                1
            )[0].strip()

        # Optional TypeScript parameter:
        # user?: User
        parameter = parameter.rstrip("?").strip()

        match = re.fullmatch(
            r'[A-Za-z_$][\w$]*',
            parameter
        )

        if match:
            return parameter

        return None

    # =====================================================
    # FIND JAVASCRIPT / TYPESCRIPT FUNCTION
    # =====================================================

    def _find_javascript_function_for_line(
        self,
        lines,
        target_index
    ):
        function_pattern = re.compile(
            r'^\s*function\s+'
            r'([A-Za-z_$][\w$]*)'
            r'\s*\('
        )

        for index in range(
            target_index,
            -1,
            -1
        ):

            match = function_pattern.match(
                lines[index]
            )

            if match:
                return match.group(1)

        return None

    # =====================================================
    # JAVA SOURCE INFERENCE
    # =====================================================

    def _infer_java_exception(
        self,
        code
    ):
        lines = code.splitlines()

        null_assignment_pattern = re.compile(
            r'^\s*'
            r'(?:final\s+)?'
            r'(?:[A-Za-z_$][\w$<>\[\],.?]*\s+)+'
            r'([A-Za-z_$][\w$]*)'
            r'\s*=\s*null\s*;'
        )

        simple_null_assignment_pattern = re.compile(
            r'^\s*'
            r'([A-Za-z_$][\w$]*)'
            r'\s*=\s*null\s*;'
        )

        null_variables = {}

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            match = null_assignment_pattern.match(
                line
            )

            if not match:
                match = (
                    simple_null_assignment_pattern.match(
                        line
                    )
                )

            if match:

                variable_name = match.group(1)

                null_variables[
                    variable_name
                ] = {
                    "assignment_line": index + 1
                }

        if not null_variables:
            return None

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            for variable_name in null_variables:

                dereference_pattern = re.compile(
                    rf'\b{re.escape(variable_name)}'
                    r'\s*\.\s*'
                    r'[A-Za-z_$][\w$]*'
                )

                if not dereference_pattern.search(
                    stripped
                ):
                    continue

                if re.fullmatch(
                    rf'.*\b{re.escape(variable_name)}'
                    r'\s*=\s*null\s*;?\s*',
                    stripped
                ):
                    continue

                return {
                    "exception":
                        "NullPointerException",

                    "failure_code":
                        stripped,

                    "line":
                        index + 1,

                    "function":
                        self._find_java_method_for_line(
                            lines,
                            index
                        ),

                    "evidence":
                        (
                            f"{variable_name} is explicitly "
                            "assigned null and is later "
                            "dereferenced"
                        )
                }

        return None

    # =====================================================
    # FIND JAVA METHOD
    # =====================================================

    def _find_java_method_for_line(
        self,
        lines,
        target_index
    ):
        method_pattern = re.compile(
            r'^\s*'
            r'(?:public|protected|private)?\s*'
            r'(?:static\s+)?'
            r'(?:final\s+)?'
            r'(?:synchronized\s+)?'
            r'(?:[A-Za-z_$][\w$<>\[\],.?]*\s+)'
            r'([A-Za-z_$][\w$]*)'
            r'\s*\([^;{}]*\)'
            r'(?:\s+throws\s+[^{]+)?'
            r'\s*\{?\s*$'
        )

        control_words = {
            "if",
            "for",
            "while",
            "switch",
            "catch",
            "return",
            "new"
        }

        for index in range(
            target_index,
            -1,
            -1
        ):

            match = method_pattern.match(
                lines[index]
            )

            if not match:
                continue

            method_name = match.group(1)

            if method_name not in control_words:
                return method_name

        return None

    # =====================================================
    # PYTHON SOURCE INFERENCE
    # =====================================================

    def _infer_python_exception(
        self,
        code
    ):
        lines = code.splitlines()

        # =====================================================
        # 1. TRACK VARIABLES ASSIGNED A LITERAL ZERO
        # =====================================================
        #
        # Example:
        #
        # a = 10
        # b = 0
        # print(a / b)
        #
        # Here "b" is known to contain zero. If it is later
        # used as a divisor, infer ZeroDivisionError.

        zero_variables = set()

        zero_assignment_pattern = re.compile(
            r'^\s*'
            r'([A-Za-z_]\w*)'
            r'\s*=\s*'
            r'([+-]?0+(?:\.0*)?)'
            r'\s*$'
        )

        general_assignment_pattern = re.compile(
            r'^\s*'
            r'([A-Za-z_]\w*)'
            r'\s*=\s*'
            r'(.+?)'
            r'\s*$'
        )

        division_by_variable_pattern = re.compile(
            r'/\s*'
            r'([A-Za-z_]\w*)'
        )

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            # ---------------------------------------------
            # Check whether a known-zero variable is used
            # as a divisor.
            # ---------------------------------------------

            for division_match in (
                division_by_variable_pattern.finditer(
                    stripped
                )
            ):

                divisor = (
                    division_match.group(1)
                )

                if divisor in zero_variables:

                    return {
                        "exception":
                            "ZeroDivisionError",

                        "failure_code":
                            stripped,

                        "line":
                            index + 1,

                        "function":
                            self._find_python_function_for_line(
                                lines,
                                index
                            ),

                        "evidence":
                            (
                                f"{divisor} is assigned a "
                                "literal zero value and is "
                                "later used as a divisor"
                            )
                    }

            # ---------------------------------------------
            # Detect zero assignment.
            # ---------------------------------------------

            zero_assignment_match = (
                zero_assignment_pattern.match(
                    stripped
                )
            )

            if zero_assignment_match:

                variable_name = (
                    zero_assignment_match.group(1)
                )

                zero_variables.add(
                    variable_name
                )

                continue

            # ---------------------------------------------
            # If the variable is reassigned to another
            # value, it is no longer definitely zero.
            #
            # Example:
            #
            # b = 0
            # b = 5
            # print(a / b)
            #
            # This should NOT be reported as zero division.
            # ---------------------------------------------

            general_assignment_match = (
                general_assignment_pattern.match(
                    stripped
                )
            )

            if general_assignment_match:

                variable_name = (
                    general_assignment_match.group(1)
                )

                zero_variables.discard(
                    variable_name
                )

        # =====================================================
        # 2. ZERO DIVISION THROUGH FUNCTION CALL
        # =====================================================
        #
        # Example:
        #
        # def divide(a, b):
        #     return a / b
        #
        # print(divide(10, 0))
        #
        # Detect that parameter "b" is used as the divisor,
        # then check whether the function receives literal 0
        # for that parameter.

        function_pattern = re.compile(
            r'^\s*def\s+'
            r'([A-Za-z_]\w*)'
            r'\s*\(([^)]*)\)\s*:'
        )

        for function_index, line in enumerate(
            lines
        ):

            function_match = (
                function_pattern.match(
                    line
                )
            )

            if not function_match:
                continue

            function_name = (
                function_match.group(1)
            )

            parameters = [
                parameter.strip()
                for parameter
                in function_match.group(2).split(",")
                if parameter.strip()
            ]

            if not parameters:
                continue

            function_indent = (
                len(line)
                - len(line.lstrip())
            )

            division_info = None

            for body_index in range(
                function_index + 1,
                len(lines)
            ):

                body_line = lines[
                    body_index
                ]

                stripped = (
                    body_line.strip()
                )

                if not stripped:
                    continue

                body_indent = (
                    len(body_line)
                    - len(body_line.lstrip())
                )

                if body_indent <= function_indent:
                    break

                division_match = re.search(
                    r'/\s*'
                    r'([A-Za-z_]\w*)',
                    stripped
                )

                if not division_match:
                    continue

                divisor = (
                    division_match.group(1)
                )

                if divisor not in parameters:
                    continue

                division_info = {
                    "divisor":
                        divisor,

                    "failure_code":
                        stripped,

                    "line":
                        body_index + 1
                }

                break

            if not division_info:
                continue

            divisor = (
                division_info["divisor"]
            )

            try:
                divisor_position = (
                    parameters.index(
                        divisor
                    )
                )

            except ValueError:
                continue

            call_pattern = re.compile(
                rf'\b{re.escape(function_name)}'
                r'\s*\(([^)]*)\)'
            )

            for call_index, call_line in enumerate(
                lines
            ):

                if call_index == function_index:
                    continue

                for call_match in (
                    call_pattern.finditer(
                        call_line
                    )
                ):

                    arguments = [
                        argument.strip()
                        for argument
                        in call_match.group(1).split(",")
                    ]

                    if (
                        divisor_position
                        >= len(arguments)
                    ):
                        continue

                    divisor_argument = (
                        arguments[
                            divisor_position
                        ]
                    )

                    if self._is_python_zero_literal(
                        divisor_argument
                    ):

                        return {
                            "exception":
                                "ZeroDivisionError",

                            "failure_code":
                                division_info[
                                    "failure_code"
                                ],

                            "line":
                                division_info[
                                    "line"
                                ],

                            "function":
                                function_name,

                            "evidence":
                                (
                                    f"{function_name}() "
                                    f"receives 0 for "
                                    f"{divisor}"
                                )
                        }

        # =====================================================
        # 3. DIRECT DIVISION BY LITERAL ZERO
        # =====================================================
        #
        # Examples:
        #
        # result = 10 / 0
        #
        # result = value / 0.0

        direct_zero_pattern = re.compile(
            r'/\s*'
            r'(?:0+(?:\.0*)?)'
            r'(?![\d.])'
        )

        for index, line in enumerate(
            lines
        ):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            if direct_zero_pattern.search(
                stripped
            ):

                return {
                    "exception":
                        "ZeroDivisionError",

                    "failure_code":
                        stripped,

                    "line":
                        index + 1,

                    "function":
                        self._find_python_function_for_line(
                            lines,
                            index
                        ),

                    "evidence":
                        "Division by a literal zero value"
                }

        return None

    # =====================================================
    # PYTHON ZERO-LITERAL CHECK
    # =====================================================

    def _is_python_zero_literal(
        self,
        value
    ):
        value = (
            value or ""
        ).strip()

        return bool(
            re.fullmatch(
                r'[+-]?0+(?:\.0*)?',
                value
            )
        )

    # =====================================================
    # FIND PYTHON FUNCTION
    # =====================================================

    def _find_python_function_for_line(
        self,
        lines,
        target_index
    ):
        function_pattern = re.compile(
            r'^(\s*)def\s+'
            r'([A-Za-z_]\w*)'
            r'\s*\('
        )

        for index in range(
            target_index,
            -1,
            -1
        ):

            match = function_pattern.match(
                lines[index]
            )

            if not match:
                continue

            function_indent = len(
                match.group(1)
            )

            target_line = lines[
                target_index
            ]

            target_indent = (
                len(target_line)
                - len(target_line.lstrip())
            )

            if target_indent > function_indent:
                return match.group(2)

        return None

    # =====================================================
    # EXCEPTION DETECTION
    # =====================================================

    def _detect_exception(
        self,
        text
    ):
        if not text.strip():
            return None

        php_patterns = [
            r'PHP\s+Fatal\s+error:\s+Uncaught\s+'
            r'([A-Za-z_\\][A-Za-z0-9_\\]*(?:Error|Exception))',

            r'PHP\s+Fatal\s+error:\s+Uncaught\s+'
            r'(Error|Exception)\b',

            r'Uncaught\s+'
            r'([A-Za-z_\\][A-Za-z0-9_\\]*(?:Error|Exception))',

            r'Uncaught\s+(Error|Exception)\b',

            r'PHP\s+(?:Fatal\s+)?error:\s+'
            r'([A-Za-z_\\][A-Za-z0-9_\\]*(?:Error|Exception))'
        ]

        for pattern in php_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = match.group(1)

                if "\\" in value:
                    value = value.split("\\")[-1]

                return value

        if re.search(
            r'PHP\s+Fatal\s+error:.*?\bUncaught\s+Error\b',
            text,
            re.IGNORECASE | re.DOTALL
        ):
            return "Error"

        patterns = [
            r'\b([A-Za-z0-9_]+Exception)\b',
            r'\b([A-Za-z0-9_]+Error)\b',
            r'\b(Segmentation\s+[Ff]ault)\b',
            r'\b(SIGSEGV)\b'
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = match.group(1)

                if value.upper() == "SIGSEGV":
                    return "Segmentation fault"

                if re.fullmatch(
                    r"Segmentation\s+Fault",
                    value,
                    re.IGNORECASE
                ):
                    return "Segmentation fault"

                return value

        return None

    # =====================================================
    # FILE DETECTION
    # =====================================================

    def _detect_file(
        self,
        stack_trace
    ):
        if not stack_trace.strip():
            return None

        patterns = [
            r'\bin\s+'
            r'([A-Za-z0-9_./\\\-]+\.php)'
            r':(?:line\s+)?(\d+)',

            r'#\d+\s+'
            r'([A-Za-z0-9_./\\\-]+\.php)'
            r'\((\d+)\)',

            r'([A-Za-z0-9_./\\\-]+\.'
            r'(?:java|py|js|ts|cpp|cc|cxx|cs|c|h|hpp|php|go|rb))'
            r':(?:line\s+)?(\d+)',

            r'at\s+'
            r'([A-Za-z0-9_./\\\-]+\.'
            r'(?:cpp|cc|cxx|cs|c|h|hpp))'
            r':(\d+)',

            r'([A-Za-z0-9_./\\\-]+\.'
            r'(?:java|py|js|ts|cpp|cc|cxx|cs|c|h|hpp|php|go|rb))'
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                stack_trace,
                re.IGNORECASE
            )

            if match:
                return match.group(1)

        return None

       # =====================================================
    # LINE NUMBER DETECTION
    # =====================================================

    def _detect_line(
        self,
        stack_trace
    ):
        if not stack_trace.strip():
            return None

        # -------------------------------------------------
        # PYTHON TRACEBACK
        # Use the deepest / last traceback frame because
        # that is normally where the exception occurred.
        # -------------------------------------------------

        python_matches = list(
            re.finditer(
                r'File\s+["\'][^"\']+["\']'
                r',\s*line\s+(\d+)'
                r'(?:,\s*in\s+[A-Za-z_][A-Za-z0-9_]*)?',
                stack_trace,
                re.IGNORECASE
            )
        )

        if python_matches:
            try:
                return int(
                    python_matches[-1].group(1)
                )
            except ValueError:
                return None

        # -------------------------------------------------
        # OTHER SUPPORTED STACK TRACE FORMATS
        # -------------------------------------------------

        patterns = [
            r'\bin\s+'
            r'[A-Za-z0-9_./\\\-]+\.php'
            r':(?:line\s+)?(\d+)',

            r'#\d+\s+'
            r'[A-Za-z0-9_./\\\-]+\.php'
            r'\((\d+)\)',

            r'\.(?:java|py|js|ts|cpp|cc|cxx|cs|c|h|hpp|php|go|rb)'
            r':(?:line\s+)?(\d+)',

            r'\bline\s+(\d+)',

            r'\bat\s+'
            r'[A-Za-z0-9_./\\\-]+\.'
            r'(?:cpp|cc|cxx|cs|c|h|hpp)'
            r':(\d+)',

            r':(\d+)\)?'
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                stack_trace,
                re.IGNORECASE
            )

            if match:

                try:
                    return int(
                        match.group(1)
                    )
                except ValueError:
                    return None

        return None

    # =====================================================
    # FUNCTION / METHOD DETECTION
    # =====================================================

    def _detect_function(
        self,
        stack_trace,
        language=""
    ):
        if not stack_trace.strip():
            return None

        language_value = (
            language or ""
        ).strip().lower()

        # -------------------------------------------------
        # PHP
        # -------------------------------------------------

        if language_value == "php":

            php_function = self._detect_php_function(
                stack_trace
            )

            if php_function:
                return php_function

        # -------------------------------------------------
        # PYTHON
        #
        # A Python traceback can contain multiple frames.
        # Use the deepest / last frame.
        # -------------------------------------------------

        if language_value == "python":

            python_matches = list(
                re.finditer(
                    r'line\s+\d+,\s+in\s+'
                    r'([A-Za-z_][A-Za-z0-9_]*)',
                    stack_trace,
                    re.IGNORECASE
                )
            )

            if python_matches:
                return python_matches[-1].group(1)

        # -------------------------------------------------
        # C / C++ / GDB
        # -------------------------------------------------

        gdb_in_match = re.search(
            r'\bin\s+'
            r'([A-Za-z_~][A-Za-z0-9_:~<>]*)'
            r'\s*\(',
            stack_trace
        )

        if gdb_in_match:
            return gdb_in_match.group(1)

        gdb_frame_match = re.search(
            r'#\d+\s+'
            r'(?:0x[0-9A-Fa-f]+\s+in\s+)?'
            r'([A-Za-z_~][A-Za-z0-9_:~<>]*)'
            r'\s*\(',
            stack_trace
        )

        if gdb_frame_match:
            return gdb_frame_match.group(1)

        # -------------------------------------------------
        # JAVASCRIPT / TYPESCRIPT
        # -------------------------------------------------

        javascript_match = re.search(
            r'at\s+'
            r'([A-Za-z_$][A-Za-z0-9_$]*)'
            r'\s+\(',
            stack_trace
        )

        if javascript_match:
            return javascript_match.group(1)

        # -------------------------------------------------
        # C# / .NET
        # -------------------------------------------------

        dotnet_match = re.search(
            r'at\s+'
            r'(?:[\w`]+\.)*'
            r'([A-Za-z_][A-Za-z0-9_]*)'
            r'\s*\(',
            stack_trace
        )

        if dotnet_match:
            return dotnet_match.group(1)

        # -------------------------------------------------
        # JAVA
        # -------------------------------------------------

        java_match = re.search(
            r'at\s+'
            r'(?:[\w$]+\.)*'
            r'([\w$]+)'
            r'\s*\(',
            stack_trace
        )

        if java_match:
            return java_match.group(1)

        # -------------------------------------------------
        # PHP FALLBACK
        # -------------------------------------------------

        php_function = self._detect_php_function(
            stack_trace
        )

        if php_function:
            return php_function

        return None
    # =====================================================
    # PHP FUNCTION DETECTION
    # =====================================================

    def _detect_php_function(
        self,
        stack_trace
    ):
        if not stack_trace.strip():
            return None

        method_match = re.search(
            r'#\d+\s+'
            r'[A-Za-z0-9_./\\\-]+\.php'
            r'\(\d+\):\s*'
            r'(?:[A-Za-z_\\][A-Za-z0-9_\\]*'
            r'(?:::|->))?'
            r'([A-Za-z_][A-Za-z0-9_]*)'
            r'\s*\(',
            stack_trace,
            re.IGNORECASE
        )

        if method_match:
            return method_match.group(1)

        function_match = re.search(
            r'#\d+\s+'
            r'[A-Za-z0-9_./\\\-]+\.php'
            r'\(\d+\):\s*'
            r'([A-Za-z_][A-Za-z0-9_]*)'
            r'\s*\(',
            stack_trace,
            re.IGNORECASE
        )

        if function_match:
            return function_match.group(1)

        object_method_match = re.search(
            r'(?:[A-Za-z_\\][A-Za-z0-9_\\]*)'
            r'->'
            r'([A-Za-z_][A-Za-z0-9_]*)'
            r'\s*\(',
            stack_trace
        )

        if object_method_match:
            return object_method_match.group(1)

        static_method_match = re.search(
            r'(?:[A-Za-z_\\][A-Za-z0-9_\\]*)'
            r'::'
            r'([A-Za-z_][A-Za-z0-9_]*)'
            r'\s*\(',
            stack_trace
        )

        if static_method_match:
            return static_method_match.group(1)

        return None

    # =====================================================
    # FAILURE CODE DETECTION
    # =====================================================

    def _detect_failure_code(
        self,
        code,
        stack_trace,
        line_number,
        language
    ):
        if not code.strip():
            return None

        lines = code.splitlines()

        if not lines:
            return None

        language_value = (
            language or ""
        ).strip().lower()

        stack_statement = self._extract_stack_statement(
            stack_trace
        )

        if stack_statement:

            matching_source = self._find_matching_source_line(
                lines,
                stack_statement
            )

            if matching_source:
                return matching_source

            return stack_statement

        if language_value == "php":

            php_failure = self._detect_php_failure_code(
                lines=lines,
                line_number=line_number
            )

            if php_failure:
                return php_failure

        if language_value in [
            "c",
            "c++",
            "cpp"
        ]:

            c_failure = self._detect_c_failure_code(
                lines
            )

            if c_failure:
                return c_failure

        if language_value in [
            "c#",
            "csharp",
            "cs"
        ]:

            csharp_failure = (
                self._detect_csharp_failure_code(
                    lines
                )
            )

            if csharp_failure:
                return csharp_failure

        if (
            line_number is not None
            and 1 <= line_number <= len(lines)
        ):

            candidate = lines[
                line_number - 1
            ].strip()

            if self._is_meaningful_code_line(
                candidate
            ):
                return candidate

        risky_patterns = [
            r'->',
            r'\*\s*[A-Za-z_]\w*',
            r'\.\w+\(',
            r'\[[^\]]+\]',
            r'\bnull\b',
            r'\bNULL\b',
            r'\bNone\b',
            r'\bundefined\b',
            r'\bthrow\b',
            r'\braise\b'
        ]

        for line in lines:

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            for pattern in risky_patterns:

                if re.search(
                    pattern,
                    stripped
                ):
                    return stripped

        for line in lines:

            stripped = line.strip()

            if self._is_meaningful_code_line(
                stripped
            ):
                return stripped

        return None
    # =====================================================
    # PHP SOURCE INFERENCE
    # =====================================================

    def _infer_php_exception(
        self,
        code
    ):
        lines = code.splitlines()

        # -------------------------------------------------
        # FIND VARIABLES ASSIGNED NULL
        # -------------------------------------------------
        #
        # Examples:
        #
        # $user = null;
        # $data = NULL;

        null_variables = set()

        null_assignment_pattern = re.compile(
            r'^\s*'
            r'\$([A-Za-z_]\w*)'
            r'\s*=\s*'
            r'(?:null|NULL)'
            r'\s*;'
        )

        for line in lines:

            match = null_assignment_pattern.match(
                line
            )

            if match:
                null_variables.add(
                    match.group(1)
                )

        if not null_variables:
            return None

        # -------------------------------------------------
        # FIND PHP FUNCTIONS
        # -------------------------------------------------
        #
        # Example:
        #
        # function printUserName($user) {
        #     echo $user->name;
        # }

        function_pattern = re.compile(
            r'^\s*'
            r'function\s+'
            r'([A-Za-z_]\w*)'
            r'\s*\(([^)]*)\)'
            r'\s*\{'
        )

        functions = []

        for function_index, line in enumerate(
            lines
        ):

            match = function_pattern.match(
                line
            )

            if not match:
                continue

            function_name = match.group(1)

            parameters = [
                parameter.strip()
                for parameter
                in match.group(2).split(",")
                if parameter.strip()
            ]

            parameter_names = []

            for parameter in parameters:

                parameter_match = re.search(
                    r'\$([A-Za-z_]\w*)',
                    parameter
                )

                parameter_names.append(
                    parameter_match.group(1)
                    if parameter_match
                    else None
                )

            # ---------------------------------------------
            # FIND END OF FUNCTION
            # ---------------------------------------------

            brace_depth = (
                line.count("{")
                - line.count("}")
            )

            end_index = function_index

            for body_index in range(
                function_index + 1,
                len(lines)
            ):

                brace_depth += (
                    lines[body_index].count("{")
                    - lines[body_index].count("}")
                )

                end_index = body_index

                if brace_depth <= 0:
                    break

            functions.append({
                "name": function_name,
                "parameters": parameter_names,
                "start": function_index,
                "end": end_index
            })

        # -------------------------------------------------
        # NULL VALUE PASSED INTO FUNCTION
        # -------------------------------------------------

        for function in functions:

            for parameter_index, parameter in enumerate(
                function["parameters"]
            ):

                if not parameter:
                    continue

                # -----------------------------------------
                # FIND PARAMETER DEREFERENCE
                # -----------------------------------------
                #
                # $user->name
                # $user->getName()

                member_pattern = re.compile(
                    rf'\${re.escape(parameter)}'
                    r'\s*->\s*'
                    r'[A-Za-z_]\w*'
                )

                failure = None

                for body_index in range(
                    function["start"] + 1,
                    function["end"]
                ):

                    stripped = lines[
                        body_index
                    ].strip()

                    if not self._is_meaningful_code_line(
                        stripped
                    ):
                        continue

                    if member_pattern.search(
                        stripped
                    ):
                        failure = {
                            "code": stripped,
                            "line": body_index + 1
                        }

                        break

                if not failure:
                    continue

                # -----------------------------------------
                # FIND FUNCTION CALL
                # -----------------------------------------

                call_pattern = re.compile(
                    rf'\b{re.escape(function["name"])}'
                    r'\s*\(([^)]*)\)'
                )

                for call_index, call_line in enumerate(
                    lines
                ):

                    # Ignore function declaration/body.
                    if (
                        function["start"]
                        <= call_index
                        <= function["end"]
                    ):
                        continue

                    for call_match in call_pattern.finditer(
                        call_line
                    ):

                        arguments = [
                            argument.strip()
                            for argument
                            in call_match.group(1).split(",")
                        ]

                        if (
                            parameter_index
                            >= len(arguments)
                        ):
                            continue

                        argument = arguments[
                            parameter_index
                        ]

                        # Direct null:
                        #
                        # printUserName(null);

                        if argument.lower() == "null":

                            return {
                                "exception":
                                    "Error",

                                "failure_code":
                                    failure["code"],

                                "line":
                                    failure["line"],

                                "function":
                                    function["name"],

                                "evidence":
                                    (
                                        f"{function['name']}() "
                                        f"receives null for "
                                        f"${parameter} and "
                                        "dereferences it"
                                    )
                            }

                        # Variable known to contain null:
                        #
                        # $user = null;
                        # printUserName($user);

                        variable_match = re.fullmatch(
                            r'\$([A-Za-z_]\w*)',
                            argument
                        )

                        if variable_match:

                            argument_name = (
                                variable_match.group(1)
                            )

                            if (
                                argument_name
                                in null_variables
                            ):

                                return {
                                    "exception":
                                        "Error",

                                    "failure_code":
                                        failure["code"],

                                    "line":
                                        failure["line"],

                                    "function":
                                        function["name"],

                                    "evidence":
                                        (
                                            f"{function['name']}() "
                                            f"receives ${argument_name}, "
                                            "which is null, and "
                                            f"dereferences "
                                            f"${parameter}"
                                        )
                                }

        # -------------------------------------------------
        # DIRECT NULL DEREFERENCE
        # -------------------------------------------------
        #
        # $user = null;
        # echo $user->name;

        for index, line in enumerate(
            lines
        ):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            for variable_name in null_variables:

                member_pattern = re.compile(
                    rf'\${re.escape(variable_name)}'
                    r'\s*->\s*'
                    r'[A-Za-z_]\w*'
                )

                if member_pattern.search(
                    stripped
                ):

                    return {
                        "exception":
                            "Error",

                        "failure_code":
                            stripped,

                        "line":
                            index + 1,

                        "function":
                            self._find_php_function_for_line(
                                lines,
                                index
                            ),

                        "evidence":
                            (
                                f"${variable_name} is assigned "
                                "null and is later dereferenced"
                            )
                    }

        return None

    # =====================================================
    # FIND PHP FUNCTION
    # =====================================================

    def _find_php_function_for_line(
        self,
        lines,
        target_index
    ):
        function_pattern = re.compile(
            r'^\s*'
            r'function\s+'
            r'([A-Za-z_]\w*)'
            r'\s*\('
        )

        for index in range(
            target_index,
            -1,
            -1
        ):

            match = function_pattern.match(
                lines[index]
            )

            if match:
                return match.group(1)

        return None
    # =====================================================
    # PHP FAILURE STATEMENT
    # =====================================================

    def _detect_php_failure_code(
        self,
        lines,
        line_number=None
    ):
        if (
            line_number is not None
            and 1 <= line_number <= len(lines)
        ):

            candidate = (
                lines[line_number - 1]
                .strip()
            )

            if (
                self._is_meaningful_code_line(
                    candidate
                )
                and (
                    "->" in candidate
                    or "::" in candidate
                )
            ):
                return candidate

        php_member_pattern = re.compile(
            r'\$[A-Za-z_]\w*'
            r'\s*->\s*'
            r'[A-Za-z_]\w*'
            r'(?:\s*\(|\b)'
        )

        for line in lines:

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            if php_member_pattern.search(
                stripped
            ):
                return stripped

        php_static_pattern = re.compile(
            r'\b[A-Za-z_\\][A-Za-z0-9_\\]*'
            r'\s*::\s*'
            r'[A-Za-z_]\w*'
        )

        for line in lines:

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            if php_static_pattern.search(
                stripped
            ):
                return stripped

        return None
    # =====================================================
    # STACK TRACE SOURCE STATEMENT
    # =====================================================

    def _extract_stack_statement(
        self,
        stack_trace
    ):
        if not stack_trace.strip():
            return None

        lines = stack_trace.splitlines()

        # -------------------------------------------------
        # PYTHON TRACEBACK
        #
        # Python traceback frames normally look like:
        #
        # File "example.py", line 6, in function_name
        #     failing_statement()
        #
        # The source statement immediately after the LAST
        # "File ..." frame is the deepest failure statement.
        # -------------------------------------------------

        python_statement = None

        for index, line in enumerate(lines):

            stripped = line.strip()

            python_frame = re.match(
                r'^File\s+["\'][^"\']+["\']'
                r',\s*line\s+\d+'
                r'(?:,\s*in\s+.+)?$',
                stripped,
                re.IGNORECASE
            )

            if not python_frame:
                continue

            if index + 1 >= len(lines):
                continue

            candidate = lines[index + 1].strip()

            if not candidate:
                continue

            # Do not accidentally use the exception message
            # itself as source code.
            if re.match(
                r'^[A-Za-z_][A-Za-z0-9_]*(?:Error|Exception)\s*:',
                candidate
            ):
                continue

            if self._is_meaningful_code_line(
                candidate
            ):
                python_statement = candidate

        if python_statement:
            return python_statement

        # -------------------------------------------------
        # NUMBERED STACK / SOURCE FORMATS
        # -------------------------------------------------

        for line in lines:

            stripped = line.strip()

            match = re.match(
                r'^\d+\s+(.+)$',
                stripped
            )

            if not match:
                continue

            statement = match.group(1).strip()

            if self._is_meaningful_code_line(
                statement
            ):
                return statement

        return None

    # =====================================================
    # C / C++ FAILURE STATEMENT
    # =====================================================

    def _detect_c_failure_code(
        self,
        lines
    ):
        pointer_patterns = [
            r'\b[A-Za-z_]\w*\s*->\s*[A-Za-z_]\w*',
            r'\*\s*[A-Za-z_]\w*',
            r'\bfree\s*\(',
            r'\bmemcpy\s*\(',
            r'\bmemmove\s*\(',
            r'\bstrcpy\s*\(',
            r'\bstrcat\s*\('
        ]

        for line in lines:

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            for pattern in pointer_patterns:

                if re.search(
                    pattern,
                    stripped
                ):
                    return stripped

        return None
    # =====================================================
    # C# SOURCE INFERENCE
    # =====================================================

    def _infer_csharp_exception(
        self,
        code
    ):
        lines = code.splitlines()

        # -------------------------------------------------
        # FIND VARIABLES ASSIGNED NULL
        # -------------------------------------------------
        #
        # Examples:
        # User user = null;
        # string name = null;
        # user = null;

        null_variables = set()

        declaration_pattern = re.compile(
            r'^\s*'
            r'(?:var|[A-Za-z_][\w<>\[\],.?]*)'
            r'\s+'
            r'([A-Za-z_]\w*)'
            r'\s*=\s*null\s*;'
        )

        assignment_pattern = re.compile(
            r'^\s*'
            r'([A-Za-z_]\w*)'
            r'\s*=\s*null\s*;'
        )

        for line in lines:

            match = declaration_pattern.match(line)

            if not match:
                match = assignment_pattern.match(line)

            if match:
                null_variables.add(
                    match.group(1)
                )

        if not null_variables:
            return None

        # -------------------------------------------------
        # FIND C# METHODS
        # -------------------------------------------------

        method_pattern = re.compile(
            r'^\s*'
            r'(?:(?:public|private|protected|internal|static|'
            r'virtual|override|async|sealed|new)\s+)*'
            r'[A-Za-z_][\w<>\[\],.?]*'
            r'\s+'
            r'([A-Za-z_]\w*)'
            r'\s*\(([^)]*)\)'
            r'\s*\{?\s*$'
        )

        methods = []

        for method_index, line in enumerate(lines):

            match = method_pattern.match(line)

            if not match:
                continue

            method_name = match.group(1)

            parameters = [
                parameter.strip()
                for parameter in match.group(2).split(",")
                if parameter.strip()
            ]

            parameter_names = []

            for parameter in parameters:

                parameter_match = re.search(
                    r'([A-Za-z_]\w*)'
                    r'\s*$',
                    parameter
                )

                parameter_names.append(
                    parameter_match.group(1)
                    if parameter_match
                    else None
                )

            # Find opening brace.
            opening_index = method_index

            while (
                opening_index < len(lines)
                and "{"
                not in lines[opening_index]
            ):
                opening_index += 1

            if opening_index >= len(lines):
                continue

            brace_depth = 0
            end_index = opening_index

            for body_index in range(
                opening_index,
                len(lines)
            ):

                brace_depth += (
                    lines[body_index].count("{")
                    - lines[body_index].count("}")
                )

                end_index = body_index

                if (
                    body_index > opening_index
                    and brace_depth <= 0
                ):
                    break

            methods.append({
                "name": method_name,
                "parameters": parameter_names,
                "start": method_index,
                "body_start": opening_index,
                "end": end_index
            })

        # -------------------------------------------------
        # NULL PASSED INTO METHOD PARAMETER
        # -------------------------------------------------

        for method in methods:

            for parameter_index, parameter in enumerate(
                method["parameters"]
            ):

                if not parameter:
                    continue

                failure = None

                # Look for:
                # user.Name
                # user.Method()

                property_pattern = re.compile(
                    rf'\b{re.escape(parameter)}'
                    r'\s*\.\s*'
                    r'[A-Za-z_]\w*'
                )

                for body_index in range(
                    method["body_start"] + 1,
                    method["end"]
                ):

                    stripped = lines[
                        body_index
                    ].strip()

                    if not self._is_meaningful_code_line(
                        stripped
                    ):
                        continue

                    if property_pattern.search(stripped):

                        # Ignore null-safe access:
                        # user?.Name

                        null_safe_pattern = re.compile(
                            rf'\b{re.escape(parameter)}'
                            r'\s*\?\.\s*'
                        )

                        if null_safe_pattern.search(
                            stripped
                        ):
                            continue

                        failure = {
                            "code": stripped,
                            "line": body_index + 1
                        }

                        break

                if not failure:
                    continue

                # Find calls to this method.
                call_pattern = re.compile(
                    rf'\b{re.escape(method["name"])}'
                    r'\s*\(([^)]*)\)'
                )

                for call_index, call_line in enumerate(
                    lines
                ):

                    if (
                        method["start"]
                        <= call_index
                        <= method["end"]
                    ):
                        continue

                    for call_match in call_pattern.finditer(
                        call_line
                    ):

                        arguments = [
                            argument.strip()
                            for argument
                            in call_match.group(1).split(",")
                        ]

                        if parameter_index >= len(arguments):
                            continue

                        argument = arguments[
                            parameter_index
                        ]

                        if (
                            argument == "null"
                            or argument in null_variables
                        ):
                            return {
                                "exception":
                                    "NullReferenceException",

                                "failure_code":
                                    failure["code"],

                                "line":
                                    failure["line"],

                                "function":
                                    method["name"],

                                "evidence":
                                    (
                                        f"{method['name']}() "
                                        f"receives a null value "
                                        f"for {parameter} and "
                                        "dereferences it"
                                    )
                            }

        # -------------------------------------------------
        # DIRECT NULL DEREFERENCE
        # -------------------------------------------------
        #
        # User user = null;
        # Console.WriteLine(user.Name);

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            for variable_name in null_variables:

                null_safe_pattern = re.compile(
                    rf'\b{re.escape(variable_name)}'
                    r'\s*\?\.\s*'
                )

                if null_safe_pattern.search(stripped):
                    continue

                dereference_pattern = re.compile(
                    rf'\b{re.escape(variable_name)}'
                    r'\s*\.\s*'
                    r'[A-Za-z_]\w*'
                )

                if dereference_pattern.search(stripped):

                    return {
                        "exception":
                            "NullReferenceException",

                        "failure_code":
                            stripped,

                        "line":
                            index + 1,

                        "function":
                            self._find_csharp_method_for_line(
                                lines,
                                index
                            ),

                        "evidence":
                            (
                                f"{variable_name} is assigned "
                                "null and is later dereferenced"
                            )
                    }

        return None

    # =====================================================
    # FIND C# METHOD
    # =====================================================

    def _find_csharp_method_for_line(
        self,
        lines,
        target_index
    ):
        method_pattern = re.compile(
            r'^\s*'
            r'(?:(?:public|private|protected|internal|static|'
            r'virtual|override|async|sealed|new)\s+)*'
            r'[A-Za-z_][\w<>\[\],.?]*'
            r'\s+'
            r'([A-Za-z_]\w*)'
            r'\s*\([^;]*\)'
            r'\s*\{?\s*$'
        )

        for index in range(
            target_index,
            -1,
            -1
        ):

            match = method_pattern.match(
                lines[index]
            )

            if match:
                return match.group(1)

        return None
    # =====================================================
    # C# FAILURE STATEMENT
    # =====================================================

    def _detect_csharp_failure_code(
        self,
        lines
    ):
        ignored_objects = {
            "Console",
            "System",
            "Math",
            "String",
            "Convert",
            "DateTime"
        }

        property_pattern = re.compile(
            r'\b([A-Za-z_]\w*)\s*\.\s*'
            r'([A-Za-z_]\w*)'
        )

        for line in lines:

            stripped = line.strip()

            if not self._is_meaningful_code_line(
                stripped
            ):
                continue

            matches = list(
                property_pattern.finditer(
                    stripped
                )
            )

            for match in reversed(matches):

                object_name = match.group(1)

                if object_name in ignored_objects:
                    continue

                return stripped

        return None

    # =====================================================
    # SOURCE LINE MATCHING
    # =====================================================

    def _find_matching_source_line(
        self,
        lines,
        stack_statement
    ):
        normalized_stack = self._normalize_code(
            stack_statement
        )

        for line in lines:

            stripped = line.strip()

            if not stripped:
                continue

            if (
                self._normalize_code(stripped)
                == normalized_stack
            ):
                return stripped

        return None

    def _normalize_code(
        self,
        value
    ):
        return re.sub(
            r'\s+',
            '',
            value or ''
        )

    # =====================================================
    # MEANINGFUL SOURCE CHECK
    # =====================================================

    def _is_meaningful_code_line(
        self,
        line
    ):
        if not line:
            return False

        ignored = {
            "{",
            "}",
            "};",
            ";",
            "<?php",
            "<?",
            "?>"
        }

        if line in ignored:
            return False

        if line.startswith("#include"):
            return False

        if line.startswith("//"):
            return False

        return True


# =========================================================
# SIMPLE FUNCTION INTERFACE
# =====================================================

def run_log_analysis_agent(
    error_message="",
    stack_trace="",
    code="",
    language=""
):
    agent = LogAnalysisAgent()

    return agent.analyze(
        error_message=error_message,
        stack_trace=stack_trace,
        code=code,
        language=language
    )