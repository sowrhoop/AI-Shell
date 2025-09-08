import os
import tempfile

from ai_shell.history import Message, SessionRecord, list_sessions, load_session, new_session_id, save_session


def test_history_save_and_load():
    with tempfile.TemporaryDirectory() as td:
        os.environ["AI_SHELL_DATA_DIR"] = td
        try:
            sid = new_session_id()
            rec = SessionRecord(
                id=sid,
                created_at="",
                model="gpt-test",
                system_prompt="sys",
                messages=[Message(role="user", content="hi"), Message(role="assistant", content="hello")],
            )
            path = save_session(rec)
            assert os.path.exists(path)
            files = list_sessions()
            assert any(sid in f for f in files)
            back = load_session(sid)
            assert back is not None
            assert back.model == "gpt-test"
            assert len(back.messages) == 2
        finally:
            del os.environ["AI_SHELL_DATA_DIR"]

