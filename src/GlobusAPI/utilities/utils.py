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

from ..logging.logging import get_logger

logger = get_logger(stdout=True)


def time_string_to_integer_seconds(time_string: str = "00:00:30") -> int:
    """Time string conversion to seconds

    Args:
        time_string (str, optional): A string that specifies the period of time to wait. It should in a "ss" or "mm:ss"
                                    or "hh:mm:ss" format. Defaults to "00:00:30".

    Returns:
        int: wait period as a number of seconds

    Raises:
        ValueError: If wait_period is not in the correct time format or if time input is not valid

    """

    interval = time_string.split(":")
    if len(interval) > 3:
        logger.error(
            'Incorrect wait_period argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
        raise ValueError(
            'Incorrect wait_period argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
    for i in interval:
        if int(i) < 0 or int(i) > 59:
            logger.error(
                """Invalid wait_period argument. It should follow
                   the "ss" or "mm:ss" or "hh:mm:ss" time formats."""
            )
            raise ValueError(
                """Incorrect wait_period argument.
                   Use "ss" or "mm:ss" or "hh:mm:ss" time formats"""
            )

    if len(interval) == 1:
        interval = int(interval[0])
    elif len(interval) == 2:
        interval = int(interval[0]) * 60 + int(interval[1])
    else:
        interval = (int(interval[0]) * 60 + int(interval[1])) * 60 + int(interval[2])
    if interval < 0:
        logger.error("Invalid wait_period argument, as it is less than 0 seconds.")
        raise ValueError("Invalid wait_period argument, as it is less than 0 seconds.")

    return interval
