import argparse
import re

from cc2olx.utils import is_valid_ipv6_address


class LinkSourceValidator:
    """
    Validate a link source.
    """

    UL = "\u00a1-\uffff"  # Unicode letters range (must not be a raw string).

    # IP patterns
    IPV4_REGEX = (
        r"(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)"
        r"(?:\.(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)){3}"
    )
    IPV6_REGEX = r"\[[0-9a-f:.]+\]"  # (simple regex, validated later)

    # Host patterns
    HOSTNAME_REGEX = rf"[a-z{UL}0-9](?:[a-z{UL}0-9-]{{0,61}}[a-z{UL}0-9])?"
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    DOMAIN_REGEX = rf"(?:\.(?!-)[a-z{UL}0-9-]{{1,63}}(?<!-))*"
    TLD_REGEX = (
        r"\."  # dot
        r"(?!-)"  # can't start with a dash
        rf"(?:[a-z{UL}-]{{2,63}}"  # domain label
        r"|xn--[a-z0-9]{1,59})"  # or punycode label
        r"(?<!-)"  # can't end with a dash
        r"\.?"  # may have a trailing dot
    )
    HOST_REGEX = "(" + HOSTNAME_REGEX + DOMAIN_REGEX + TLD_REGEX + "|localhost)"

    LINK_SOURCE_REGEX = (
        r"^https?://"  # scheme is validated separately
        r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"  # user:pass authentication
        rf"(?P<netloc>{IPV4_REGEX}|{IPV6_REGEX}|{HOST_REGEX})"
        r"(?::[0-9]{1,5})?"  # port
        r"/?"  # trailing slash
        r"\Z"
    )

    message = "Enter a valid URL."

    def __call__(self, value: str) -> str:
        if not (link_source_match := re.fullmatch(self.LINK_SOURCE_REGEX, value, re.IGNORECASE)):
            raise argparse.ArgumentTypeError(self.message)

        self._validate_ipv6_address(link_source_match.group("netloc"))

        return value

    def _validate_ipv6_address(self, netloc: str) -> None:
        """
        Check netloc correctness if it's an IPv6 address.
        """
        potential_ipv6_regex = r"^\[(.+)\](?::[0-9]{1,5})?$"
        if netloc_match := re.search(potential_ipv6_regex, netloc):
            potential_ip = netloc_match[1]
            if not is_valid_ipv6_address(potential_ip):
                raise argparse.ArgumentTypeError(self.message)
