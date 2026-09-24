from __future__ import annotations

import pytest

from domain.errors import OllamaUnavailableError
from domain.models import RefreshModelsCommand
from use_cases.refresh_models import RefreshModels, select_model


class FakeOllama:
    def __init__(self, models: tuple[str, ...]) -> None:
        self._models = models

    def list_models(self) -> tuple[str, ...]:
        return self._models

    def translate_fragment(
        self, *, model: str, instruction: str, source: str, direction: str = ""
    ) -> str:
        raise NotImplementedError

    def close(self) -> None:
        return


def test_should_select_qwen_when_preferred_model_is_in_response() -> None:
    """FT-041, happy: при старте без выбора — qwen2.5:7b, если есть в ответе."""
    models = ("llama3.2", "qwen2.5:3b", "qwen2.5:7b")
    event = RefreshModels(FakeOllama(models)).run(
        RefreshModelsCommand(request_id=1, current_model="")
    )
    assert event.models == models
    assert event.selected_model == "qwen2.5:7b"
    assert event.request_id == 1


def test_should_select_first_model_when_qwen_is_absent() -> None:
    """FT-041, edge: нет qwen2.5:7b — первая модель ответа, даже если есть qwen2.5:3b."""
    models = ("llama3.2", "qwen2.5:3b")
    assert select_model(models, "") == "llama3.2"


def test_should_keep_current_model_when_it_remains_in_response() -> None:
    """FT-045, A0053, happy: выбранную не сбрасывать, пока имя есть в ответе."""
    models = ("llama3.2", "qwen2.5:3b")
    event = RefreshModels(FakeOllama(models)).run(
        RefreshModelsCommand(request_id=2, current_model="llama3.2")
    )
    assert event.selected_model == "llama3.2"


def test_should_apply_default_rule_when_current_model_disappeared() -> None:
    """FT-045, A0053, edge: имени нет в новом ответе — снова FT-041."""
    models = ("qwen2.5:3b", "qwen2.5:7b")
    event = RefreshModels(FakeOllama(models)).run(
        RefreshModelsCommand(request_id=3, current_model="gone:7b")
    )
    assert event.selected_model == "qwen2.5:7b"


def test_should_keep_all_api_names_when_list_includes_non_qwen() -> None:
    """FT-005, NFT-013: без отсечения по имени."""
    models = ("custom-finetune:latest", "llama3.2")
    event = RefreshModels(FakeOllama(models)).run(
        RefreshModelsCommand(request_id=4, current_model="")
    )
    assert event.models == models


def test_should_raise_unavailable_when_port_returns_empty_list() -> None:
    """Пустой список моделей — OllamaUnavailableError, не первая «пустая»."""
    with pytest.raises(OllamaUnavailableError):
        RefreshModels(FakeOllama(())).run(
            RefreshModelsCommand(request_id=5, current_model="")
        )
