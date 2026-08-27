# Карта покрытия автотестов TranslateText

Поверхность: desktop (CustomTkinter). Раннер: pytest. Прогон — команда `/use-tests`.

Срез S-01: подписи, пустые поля, блокировки, направление перевода (FT-051…FT-053). Срез S-02: опрос `GET /api/tags`, выбор модели, клик/фокус «Модель» в окне. Срез S-03: статус FT-024, восстановление по клику на «Модель», приоритет подсказки FT-050, оригинал не очищается. Живой Ollama в тестах не вызывается (MockTransport / фейк-порт). Окно в pytest — `HarnessWindow`: `after` из воркера очередится и выполняется в потоке Tk (`drain_worker_after` в `pump_until`). `event_generate` на `combo-model` доставляет `<Button-1>` / `<FocusIn>` в обработчики окна (CTkComboBox при `withdraw()` события не принимает).

| Тест | Файл | Требования | Слой | Состояние UI | Примечание |
| --- | --- | --- | --- | --- | --- |
| `test_should_show_all_glossary_labels_when_window_opens` | `tests/test_main_screen.py` | NFT-006; A0120; A0121 | happy | — | 8 подписей, в т.ч. «Направление перевода»; при EN→RU видна «Русский перевод» |
| `test_should_show_original_text_field_when_window_opens` | `tests/test_main_screen.py` | FT-001 | happy | — | поле есть |
| `test_should_show_translation_field_when_window_opens` | `tests/test_main_screen.py` | FT-002 | happy | — | поле есть |
| `test_should_show_custom_instruction_field_when_window_opens` | `tests/test_main_screen.py` | FT-007 | happy | — | поле есть |
| `test_should_show_base_prompt_when_user_has_not_replaced_instruction` | `tests/test_main_screen.py` | FT-008; US-005 AC1 | happy | — | текст A0006 при EN→RU |
| `test_should_show_model_list_when_window_opens` | `tests/test_main_screen.py` | FT-005; FT-045 | happy | — | старт: список = ответ фейк-API |
| `test_should_show_progress_indicator_at_zero_when_window_opens` | `tests/test_main_screen.py` | FT-022 | empty | empty | 0 % до запуска перевода |
| `test_should_show_empty_original_when_window_opens` | `tests/test_main_screen.py` | FT-001 | empty | empty | длина 0 при старте |
| `test_should_show_empty_translation_when_window_opens` | `tests/test_main_screen.py` | FT-002 | empty | empty | длина 0 при старте |
| `test_should_keep_replaced_instruction_when_user_edits_field` | `tests/test_main_screen.py` | FT-008 | happy | — | замена базового промпта |
| `test_should_select_en_ru_when_window_opens` | `tests/test_direction.py` | FT-051; A0120 | happy | — | умолчание EN→RU |
| `test_should_offer_only_en_ru_and_ru_en_when_window_opens` | `tests/test_direction.py` | FT-051; A0120 | happy | — | значения списка |
| `test_should_show_ru_en_base_prompt_when_direction_changes_and_instruction_is_base` | `tests/test_direction.py` | FT-052; A0123 | happy | — | подстановка A0122 |
| `test_should_keep_custom_instruction_when_direction_changes` | `tests/test_direction.py` | FT-052; A0123 | edge | — | своя инструкция не затирается |
| `test_should_show_english_translation_label_when_direction_is_ru_en` | `tests/test_direction.py` | FT-002; FT-053; A0121 | happy | — | одна подпись «Английский перевод» |
| `test_should_keep_translation_text_when_direction_changes` | `tests/test_direction.py` | FT-053; A0124 | happy | — | текст поля не очищается |
| `test_should_not_show_ollama_status_when_only_direction_changes` | `tests/test_direction.py` | FT-053; A0124 | negative | — | нет предупреждения FT-032 в статусе |
| `test_should_disable_translate_when_original_is_empty` | `tests/test_blocking.py` | FT-026; US-001 AC4 | negative | disabled | |
| `test_should_enable_translate_when_original_has_text` | `tests/test_blocking.py` | FT-026 | happy | — | до FT-048 / S-03 |
| `test_should_enable_translate_when_original_is_only_spaces` | `tests/test_blocking.py` | FT-026 | edge | — | пусто = длина 0 |
| `test_should_disable_save_when_translation_is_empty` | `tests/test_blocking.py` | FT-027; US-003 AC3 | negative | disabled | A0100 |
| `test_should_enable_save_when_translation_has_text` | `tests/test_blocking.py` | FT-027; A0100 | happy | — | |
| `test_should_disable_translate_when_model_list_is_empty` | `tests/test_blocking.py` | FT-048; US-001 AC4 | negative | disabled | пустой `values` виджета |
| `test_should_keep_model_list_enabled_when_model_list_is_empty` | `tests/test_blocking.py` | FT-049; US-007 AC1 | happy | — | список остаётся доступным |
| `test_should_show_no_text_hint_when_pointer_hovers_blocked_translate` | `tests/test_blocking.py` | FT-050; US-008 AC1; A0092 | negative | disabled | не строка статуса |
| `test_should_not_show_no_text_hint_when_pointer_is_not_on_translate` | `tests/test_blocking.py` | FT-050; A0092 | empty | empty | без наведения трёх фраз нет |
| `test_should_hide_blocking_hints_when_translate_is_enabled` | `tests/test_blocking.py` | FT-050; US-008 AC4 | happy | — | у доступной кнопки трёх подсказок нет |
| `test_should_return_all_model_names_when_tags_response_has_several` | `tests/test_ollama_gateway.py` | FT-005; FT-012 | happy | — | MockTransport, без GUI |
| `test_should_raise_unavailable_when_model_list_is_empty` | `tests/test_ollama_gateway.py` | FT-024 | negative | — | пустой JSON; текст bat не в исключении |
| `test_should_raise_unavailable_when_tags_request_fails` | `tests/test_ollama_gateway.py` | FT-012 | negative | — | ConnectError |
| `test_should_close_httpx_client_when_gateway_closes` | `tests/test_ollama_gateway.py` | — | happy | — | `Client.close()` |
| `test_should_select_qwen_when_preferred_model_is_in_response` | `tests/test_refresh_models.py` | FT-041; A0045 | happy | — | фейк `OllamaPort` |
| `test_should_select_first_model_when_qwen_is_absent` | `tests/test_refresh_models.py` | FT-041; A0045 | edge | — | |
| `test_should_keep_current_model_when_it_remains_in_response` | `tests/test_refresh_models.py` | FT-045; A0053 | happy | — | |
| `test_should_apply_default_rule_when_current_model_disappeared` | `tests/test_refresh_models.py` | FT-045; A0053 | edge | — | |
| `test_should_keep_all_api_names_when_list_includes_non_qwen` | `tests/test_refresh_models.py` | FT-005; NFT-013 | happy | — | без фильтра |
| `test_should_raise_unavailable_when_port_returns_empty_list` | `tests/test_refresh_models.py` | FT-024 | negative | — | |
| `test_should_select_qwen_when_window_opens_and_preferred_is_available` | `tests/test_model_list.py` | FT-041; A0045 | happy | — | комбо после старта |
| `test_should_select_first_model_when_window_opens_without_qwen` | `tests/test_model_list.py` | FT-041; A0045 | edge | — | |
| `test_should_show_all_api_names_when_list_includes_non_qwen` | `tests/test_model_list.py` | FT-005; NFT-013 | happy | — | без фильтра в комбо |
| `test_should_update_model_list_when_user_clicks_model` | `tests/test_model_list.py` | FT-045; NFT-013 | happy | — | клик, без пересборки окна |
| `test_should_update_model_list_when_model_receives_focus` | `tests/test_model_list.py` | FT-045; A0055 | happy | — | |
| `test_should_keep_selected_model_when_it_remains_in_new_response` | `tests/test_model_list.py` | FT-045; A0053 | happy | — | |
| `test_should_select_default_when_current_model_missing_after_refresh` | `tests/test_model_list.py` | FT-045; A0053 | edge | — | |
| `test_should_not_poll_models_when_window_gains_focus` | `tests/test_model_list.py` | A0079 | negative | — | не опрос при фокусе окна |
| `test_should_show_start_ollama_status_when_api_is_unavailable` | `tests/test_ollama_unavailable.py` | FT-024; NFT-011; US-007 AC1 | negative | error | `start_ollama.bat` и `F:\Docker\Ollama` в статусе |
| `test_should_keep_original_text_when_ollama_becomes_unavailable` | `tests/test_ollama_unavailable.py` | FT-024; US-007 AC1 | negative | error | оригинал не очищается |
| `test_should_enable_translate_when_models_return_after_unavailable` | `tests/test_ollama_unavailable.py` | FT-024; FT-048; A0079; US-007 AC1 | happy | — | клик по «Модель», статус снят |
| `test_should_show_ollama_hint_when_original_empty_and_api_unavailable` | `tests/test_ollama_unavailable.py` | FT-050; A0082; US-008 AC5 | edge | disabled | «Ollama не работает», не «Нет текста…» |
