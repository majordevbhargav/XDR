"""Unit tests for the local XDR example logic. These tests never contact external services."""
import os
import unittest
from unittest.mock import patch

from Automation.hello_xdr_api import classify_ip, hello_xdr, run_workflow


class IPClassificationTests(unittest.TestCase):
    def test_private_ipv4_ranges(self):
        for address in ("10.2.3.4", "172.16.0.1", "172.31.255.254", "192.168.1.2"):
            with self.subTest(address=address):
                self.assertEqual(classify_ip(address), "private")

    def test_public_ipv4(self):
        self.assertEqual(classify_ip("8.8.8.8"), "public")
        self.assertEqual(classify_ip("172.32.0.1"), "public")

    def test_special_addresses_are_not_called_public(self):
        self.assertEqual(classify_ip("127.0.0.1"), "non-public/reserved")
        self.assertEqual(classify_ip("169.254.1.2"), "non-public/reserved")

    def test_ipv6(self):
        self.assertEqual(classify_ip("2001:4860:4860::8888"), "public")
        self.assertEqual(classify_ip("fd00::1"), "private")

    def test_invalid_ip_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_ip("not-an-ip")

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            hello_xdr("  ", "10.0.0.1")

    def test_valid_message(self):
        self.assertEqual(
            hello_xdr("Asha", "10.1.2.3"),
            "Hello Asha, 10.1.2.3 is a private address",
        )


class WorkflowSafetyTests(unittest.TestCase):
    def test_workflow_start_is_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "disabled"):
                run_workflow("Asha", "10.1.2.3")


if __name__ == "__main__":
    unittest.main()
