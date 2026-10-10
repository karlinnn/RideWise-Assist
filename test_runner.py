import traceback
import sys

from tests.test_workflow import (
    test_malformed_llm_output,
    test_clarification,
    test_session_reset,
    test_cross_customer_booking_access,
    test_invalid_booking_id,
    test_missing_evidence,
    test_answer_llm_error
)

tests = [
    test_malformed_llm_output,
    test_clarification,
    test_session_reset,
    test_cross_customer_booking_access,
    test_invalid_booking_id,
    test_missing_evidence,
    test_answer_llm_error
]

failed = 0
for test in tests:
    try:
        test()
        print(f"PASSED: {test.__name__}")
    except Exception as e:
        print(f"FAILED: {test.__name__}")
        traceback.print_exc()
        failed += 1

sys.exit(failed)
