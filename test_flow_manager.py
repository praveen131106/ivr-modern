from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def flow_manager():
    from backend.utils.flow_manager import FlowManager

    return FlowManager()


def test_flows_are_loaded(flow_manager):
    train_main = flow_manager.get_flow("train_main")
    assert train_main
    assert "states" in train_main
    assert "main_menu" in train_main["states"]


def test_keypad_transition_to_booking(flow_manager):
    session = {"data": {}}
    flow = flow_manager.get_flow("train_main")
    next_state, message, options, is_end = flow_manager.process_input(
        flow,
        current_state="main_menu",
        user_input="1",
        is_keypad=True,
        session=session,
    )
    assert next_state.startswith("flow:booking")
    assert not is_end


def test_invalid_input_recovers(flow_manager):
    session = {"data": {}}
    flow = flow_manager.get_flow("train_main")
    next_state, message, options, is_end = flow_manager.process_input(
        flow,
        current_state="main_menu",
        user_input="invalid utterance",
        is_keypad=False,
        session=session,
    )
    assert next_state == "main_menu"
    assert "didn't quite catch" in message.lower()
    assert not is_end

