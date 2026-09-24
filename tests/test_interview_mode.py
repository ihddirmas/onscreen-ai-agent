from oncue.interview_mode import INTERVIEW_CONFIRMATION, InterviewSession


def test_interview_lock_phrase():
    s = InterviewSession()
    assert s.wants_lock("switch to Interview & Meeting Mode permanent lock")
    msg = s.lock()
    assert msg == INTERVIEW_CONFIRMATION


def test_question_detection():
    s = InterviewSession()
    assert s.is_question("What is the latest React version?")
    assert not s.is_question("I'm stuck on the deployment pipeline again.")


def test_should_invoke_for_stuck_statement():
    s = InterviewSession()
    s.lock()
    assert s.should_invoke_agent("I'm stuck on the deployment pipeline again.")


def test_skip_filler():
    s = InterviewSession()
    s.lock()
    assert not s.should_invoke_agent("okay")
