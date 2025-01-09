import os
import re


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename, encoding="utf-8").read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string. ")


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    That is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return bool(line) and not line.startswith(("-r", "#", "-e", "git+", "-c"))


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Requirements will include any constraints from files specified
    with -c in the requirements files.
    Returns a list of requirement strings.
    """
    def check_name_consistent(package):
        """
        Raise exception if package is named different ways.

        This ensures that packages are named consistently so we can match
        constraints to packages. It also ensures that if we require a package
        with extras we don't constrain it without mentioning the extras (since
        that too would interfere with matching constraints.)
        """
        canonical = package.lower().replace("_", "-").split("[")[0]
        seen_spelling = by_canonical_name.get(canonical)
        if seen_spelling is None:
            by_canonical_name[canonical] = package
        elif seen_spelling != package:
            raise Exception(
                f'Encountered both "{seen_spelling}" and "{package}" in requirements '
                "and constraints files; please use just one or the other."
            )

    def add_version_constraint_or_raise(current_line, current_requirements, add_if_not_present):
        if regex_match := requirement_line_regex.match(current_line):
            package = regex_match.group(1)
            version_constraints = regex_match.group(2)
            check_name_consistent(package)
            existing_version_constraints = current_requirements.get(package, None)
            # It's fine to add constraints to an unconstrained package,
            # but raise an error if there are already constraints in place.
            if existing_version_constraints and existing_version_constraints != version_constraints:
                raise Exception(
                    f"Multiple constraint definitions found for {package}:"
                    f' "{existing_version_constraints}" and "{version_constraints}".'
                    f"Combine constraints into one location with {package}"
                    f"{existing_version_constraints},{version_constraints}."
                )
            if add_if_not_present or package in current_requirements:
                current_requirements[package] = version_constraints

    by_canonical_name = {}  # e.g. {"django": "Django", "confluent-kafka": "confluent_kafka[avro]"}
    requirements = {}
    constraint_files = set()

    # groups "pkg<=x.y.z,..." into ("pkg", "<=x.y.z,...")
    re_package_name_base_chars = r"a-zA-Z0-9\-_."  # chars allowed in base package name
    # Two groups: name[maybe,extras], and optionally a constraint
    requirement_line_regex = re.compile(
        rf"([{re_package_name_base_chars}]+(?:\[[{re_package_name_base_chars},\s]+\])?)([<>=][^#\s]+)?"
    )

    # Read requirements from .in files and store the path to any
    # constraint files that are pulled in.
    for path in requirements_paths:
        with open(path) as reqs:
            for line in reqs:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, True)
                if line and line.startswith("-c") and not line.startswith("-c http"):
                    constraint_files.add(os.path.dirname(path) + "/" + line.split("#")[0].replace("-c", "").strip())

    # process constraint files: add constraints to existing requirements
    for constraint_file in constraint_files:
        with open(constraint_file) as reader:
            for line in reader:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, False)

    # process back into list of pkg><=constraints strings
    return [f'{pkg}{version or ""}' for (pkg, version) in sorted(requirements.items())]
