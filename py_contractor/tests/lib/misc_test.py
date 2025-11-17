# -*- coding: utf-8 -*-
"""
Created on Tue May 17 08:37:34 2022

@author: brendan

A collection of functions and classes used for performing software tests

"""
from collections.abc import Callable

import os
import pytest


# %% Functions
def compare_dictionary_items(result,
                             expected_response,
                             comparisons,
                             failed_comparisons):
    """!
    **Compare dictionary values against keys that may be string or non-string**

    Because items loaded from JSON files will always have keys as strings, and
    python doesn't have this enforcement, compare a dictionary based on its
    values - as long as its keys map across to same string type.

    @param[in] result [dict] The dictionary item returned from Python code
        under test. Keys may not be strings
    @param[in] expected_response [dict] The dictionary item loaded from either
        .py or .json - keys may be enforced as strings if from JSON
    @param [in] comparisons [list] holding booleans of comparisions performed
    @param [in] failed_comparisons [list] of failed key-value from result that
        failed comparison check

    @return comparisons [list]
    @return failed_comparisons [list]

    """
    for key in result.keys():
        if (isinstance(key, str) and key not in expected_response.keys()):
            comparisons.append(False)
            failed_comparisons.append({key: result[key]})
            continue
        elif str(key) not in expected_response.keys():
            comparisons.append(False)
            failed_comparisons.append({key: result[key]})
            continue

        if result.get(key) == expected_response.get(key):
            comparisons.append(True)
        elif (isinstance(result.get(key), dict)
              and isinstance(expected_response.get(str(key)), dict)):
            comparisons, failed_comparisons = compare_dictionary_items(
                result.get(key),
                expected_response.get(str(key)),
                comparisons,
                failed_comparisons)
        elif result.get(key) == expected_response.get(str(key)):
            comparisons.append(True)
        else:
            failed_comparisons.append({key: result[key]})
            comparisons.append(False)

    return comparisons, failed_comparisons


# %% Classes
class MiscTest:
    '''
    Misc functions involved with testing that aren't run through pyTest
    Note, use of lower case test avoids pyTest warning
    (although it would reject anyway due to __init__)
    '''

    #--------------------------------------------------------------------------
    def __init__(self):
        pass

    #--------------------------------------------------------------------------
    def demark_test():
        print("--------------------------------------------------------------")

    # -------------------------------------------------------------------------
    # def processReturns(testNo, result, expectedResponse, silent=False):
    def process_returns(*,
                        test_no: int,
                        result,
                        expected_response,
                        silent: bool = True,
                        ignore: list = [],
                        ):
        """!
        **Process a return within a test case and ensure expectations met**
        
        @param [in] test_no [int] The test number
        @param [in] result [undefined] the result from item under test
        @param [in] expected_response [undefined] the expected result within 
            the item under test
        @param
        """
        
        # If present, ignore will be a list of string keys that demark a dict
        # item to ignore        
        passed = False
        if not ignore and result == expected_response:
            passed = True

        elif ignore:
            # Need to remove the "ignore" entries from both sides and rerun the
            # logical comparison
            for item in ignore:
                keysA = item.split("][")
                keysA[0] = keysA[0].replace("[", "")
                keysA[-1] = keysA[-1].replace("]", "")

                # Then walk the keys and set the value equal to "" on both
                temp = result
                for key in keysA[:-1]:
                    temp = temp[key]
                temp[keysA[-1]] = ""
                # The above takes advantage of python's equivalence for vars
                # (i.e. whey we have to deepcopy to break links)

            if result == expected_response:
                passed = True
        elif isinstance(expected_response, dict) and isinstance(result, dict):
            # There is potential for an expected response loaded from a .json
            # file to have string keys (per its format), whereas the python
            # variable contains a none string key
            comparisons, fails = compare_dictionary_items(result,
                                                          expected_response,
                                                          [],
                                                          [])
            passed = min(comparisons)

        if passed:
            print("\n")
            print("T." + str(test_no) + " response as expected")
            print("")
            if not silent:
                print(result)

        if not passed:
            print("\n")
            print("***WARNING*** " + "T." + str(test_no)
                  + " response unexpected")
            if not silent:
                print("")
                print("Actual result:")
                print(result)
                print("")
                print("Expected result:")
                print("")
                print(expected_response)
                print("\n")

        # Note, place assert last in the subfunction, as a failed assert will
        # see the function exit back to parent
        if "PYTEST_CURRENT_TEST" in os.environ:
            # Currently running pyTest, so apply assertions for checking
            # (will cause error in normal execution)

            if not passed:
                pytest.fail("Unexpected response", False)

            # In above, the bool within pytest.fail has been set false to avoid
            # the traceback of python code associated with the fail - as the
            # python code is not what is under test - associated printout
            # should contain pertinent information

    # -------------------------------------------------------------------------
    def test_harness(*,
                     handle: Callable,
                     put: dict = None,
                     get: list = None,
                     ):
        """!
        **Enter the supplied instance and either add/manipulate or get**
        
        @param [in] handle [Callable] handle of object under test, not optional
        @param [in] [put] [dict] of class variable names and the data to
            populate them with
        @param [in] [get] [list] of class variable names which need data
            collected off them

        @return [dict]
        
        """
        data_rtn = {}
        
        if put:
            if not isinstance(put, dict):
                print("A 'put' argument should be a dictionary object")
            for var_name, var_val in put.items():
                setattr(handle, var_name, var_val)

        if get:
            for var_name in get:
                if hasattr(handle, var_name):
                    data_rtn[var_name] = getattr(handle, var_name)
                else:
                    data_rtn[var_name] = "Doesn't exist!"

        return data_rtn

    # -------------------------------------------------------------------------