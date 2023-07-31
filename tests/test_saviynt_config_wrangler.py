"""Tests key library functions.

Copyright 2023 Oregon State University.  All Rights Reserved.

Requests for more information can be directed to iamteam@oregonstate.edu |
advantage@oregonstate.edu 
"""

import datetime
import json
import logging

import pytest

import groovy_samples
import json_samples
import saviynt_config_wrangler as wrangler

logger = logging.getLogger(__name__)


@pytest.fixture(name="bad_json")
def fixture_bad_json():
    return json_samples.BAD_JSON


@pytest.fixture(name="json_with_sql")
def fixture_json_with_sql():
    return json_samples.JSON_WITH_SQL


@pytest.fixture(name="groovy_sample_1")
def fixture_groovy_sample_1():
    return groovy_samples.CREATEACCOUNTJSON


@pytest.fixture(name="groovy_sample_2")
def fixture_groovy_sample_2():
    return groovy_samples.UPDATEACCOUNTJSON


@pytest.fixture(name="simple_json")
def fixture_simple_json():
    return """{
        "a": 1,
        "b": 2,
        "c": {
            "c1": 3,
            "c2": 3
        },
        "d": 4
    }"""


@pytest.fixture(name="simple_deep_json")
def fixture_simple_deep_json():
    return """{
        "a": 1,
        "b": 2,
        "c": {
            "c1": 3,
            "c2": 3,
            "c3": {
                "e": 5,
                "f": 6
            }
        },
        "d": 4
    }"""


@pytest.fixture(name="simple_dict")
def fixture_simple_dict():
    return {
        "a": 1,
        "b": 2,
        "c": {
            "c1": 3,
            "c2": 3,
        },
        "d": 4,
    }


def test_loading_bad_json(bad_json):
    """This test pokes at some problematic JSON."""

    # Ensure the problem exists
    with pytest.raises(json.decoder.JSONDecodeError) as e:
        loaded = json.loads(bad_json)
        logger.warning(e)

    # See what info can be gleaned from the exception
    try:
        loaded = json.loads(bad_json)
    except json.decoder.JSONDecodeError as e:
        logger.warning("JSONDEcodeError was: %s", e)
        logger.warning("Offending line # was: %d", e.lineno)
        logger.warning("Offending column # was: %d", e.colno)
        line = bad_json.split("\n")[e.lineno - 1]
        logger.warning("Offending line was: '%s'", line)
        logger.warning("Line length is %d", len(line))
        with pytest.raises(IndexError):
            char = line[e.colno]
            logger.warning("Offending char is '%s'", char)

    # Strip out \n - a solution?
    joined = bad_json.replace("\n", "")
    loaded = json.loads(joined)
    assert loaded


def test_json_decoder_options(simple_dict):
    def echo(_input):
        logger.debug("object pairs hook echo: %s", _input)

        for pair in _input:
            logger.debug("object pair element 0: '%s'", pair[0])
            logger.debug("object pair element 1: '%s'", pair[1])

    json.loads(json.dumps(simple_dict), object_pairs_hook=echo)


def test_recursive_breadcrumbing(simple_json, simple_deep_json):
    logger.debug(simple_json)
    sample = json.loads(simple_deep_json)
    assert isinstance(sample, dict)

    def breadcrumbs(_input, location=None):
        result = {}
        if location is None:
            location = []

        for k, v in _input.items():
            current_location = location.copy()
            current_location.append(k)
            if isinstance(v, dict):
                value, new_location = breadcrumbs(v, current_location)
                current_location.extend(new_location)
                result.update(value)
            else:
                result["->".join(current_location)] = v

        return result, location

    logger.debug(breadcrumbs(sample))


def test_extract_code_snippets_from_json(json_with_sql):
    """Test the recursive method on real-world input.

    Ensure that the function correctly identifies and extracts a SQL snippet
    and that it associates the snippet with the correct path through the json
    tree.
    """
    extract = wrangler.extract_code_snippets_from_json(
        json_with_sql, ["MODIFYUSERDATAJSON"], path_sep="->"
    )
    assert (
        extract["MODIFYUSERDATAJSON->ADDITIONALTABLES->USERS"]
        == """SELECT username,
       firstname,
       lastname,
       systemusername,
       customproperty28,
       customproperty41,
       customproperty42,
       customproperty38,
       customproperty20,
       customproperty19,
       customproperty35,
       customproperty21,
       email
FROM USERS"""
    )
    # Test path_sep param
    extract = wrangler.extract_code_snippets_from_json(
        json_with_sql, ["MODIFYUSERDATAJSON"], path_sep="--"
    )
    assert "MODIFYUSERDATAJSON--ADDITIONALTABLES--USERS" in extract
