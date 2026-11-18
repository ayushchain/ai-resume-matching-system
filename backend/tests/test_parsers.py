"""Unit tests for experience parsing (app/parsers.py)."""
from datetime import date

from app.parsers import extract_experience_years


def _months(y1, m1, y2, m2):
    return (y2 * 12 + (m2 - 1)) - (y1 * 12 + (m1 - 1))


def test_explicit_years():
    assert extract_experience_years("I have 5 years of experience in backend development.") == 5.0
    assert extract_experience_years("Experience: 3.5 years") == 3.5
    assert extract_experience_years("7+ years of experience") == 7.0


def test_explicit_takes_priority_over_date_ranges():
    text = "2 years of experience. Earlier role: Jan 2015 - Jan 2025 at a large firm."
    assert extract_experience_years(text) == 2.0


def test_year_only_ranges():
    assert extract_experience_years("Worked at X, 2019 - 2022.") == 3.0
    assert extract_experience_years("2019 – 2022") == 3.0  # en dash


def test_month_year_ranges():
    # Jan 2020 -> Mar 2023 is 38 months = 3.2 years.
    assert extract_experience_years("Jan 2020 – Mar 2023") == 3.2
    assert extract_experience_years("January 2020 - March 2023") == 3.2


def test_present_ranges_count_up_to_today():
    today = date.today()
    expected = round(_months(2019, 1, today.year, today.month) / 12, 1)
    assert extract_experience_years("January 2019 - Present") == expected
    expected = round(_months(2021, 6, today.year, today.month) / 12, 1)
    assert extract_experience_years("Jun 2021 to Present") == expected


def test_overlapping_ranges_are_merged_not_double_counted():
    # Jan 2020 - Dec 2021 and Jun 2021 - Jun 2022 overlap; the merged span
    # Jan 2020 - Jun 2022 is 29 months = 2.4 years (not 23 + 12 months).
    text = "Role A: Jan 2020 - Dec 2021. Role B: Jun 2021 - Jun 2022."
    assert extract_experience_years(text) == 2.4


def test_separate_ranges_sum():
    text = "Role A: 2015 - 2017. Role B: 2019 - 2021."
    assert extract_experience_years(text) == 4.0


def test_no_experience_information():
    assert extract_experience_years("Fresh graduate looking for a first role.") == 0.0
