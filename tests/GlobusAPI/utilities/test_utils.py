"""
   Copyright [2026] [Rosalind Franklin Institute]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import unittest

from GlobusAPI.utilities.utils import time_string_to_integer_seconds


class TestTimeStringToIntegerSeconds(unittest.TestCase):
    def test_seconds_only(self):
        self.assertEqual(time_string_to_integer_seconds("30"), 30)

    def test_minutes_and_seconds(self):
        self.assertEqual(time_string_to_integer_seconds("01:30"), 90)

    def test_minutes_and_seconds_asymmetric(self):
        self.assertEqual(time_string_to_integer_seconds("02:05"), 125)

    def test_hours_minutes_and_seconds(self):
        self.assertEqual(time_string_to_integer_seconds("01:02:03"), 3723)

    def test_default_value(self):
        self.assertEqual(time_string_to_integer_seconds(), 30)

    def test_too_many_segments_raises(self):
        with self.assertRaises(ValueError):
            time_string_to_integer_seconds("00:00:00:00")

    def test_out_of_range_segment_raises(self):
        with self.assertRaises(ValueError):
            time_string_to_integer_seconds("00:60")
