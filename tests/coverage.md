# Карта покрытия автотестов TranslateText

Поверхность: desktop (CustomTkinter). Раннер: pytest. Прогон — команда `/use-tests`.

Срез S-01: подписи, пустые поля, блокировки, направление перевода (FT-051…FT-053). Срез S-02: опрос `GET /api/tags`, выбор модели, клик/фокус «Модель» в окне. Срез S-03: статус FT-024, восстановление по клику на «Модель», приоритет подсказки FT-050, оригинал не очищается. Срез S-04: «Перевести» одного короткого фрагмента (EN→RU / RU→EN), прогресс 0/100, снимок FT-011, замена поля. Срез S-05: пустая инструкция — диалог FT-029, согласие или отмена, базовый промпт текущего направления. Срез S-06: лимит 100 000 символов Unicode — поле держит >100k, отказ при «Перевести» без Ollama. Срез S-07: нарезка по абзацам, очередь перевода, прогресс по доле исходника, склейка. Срез S-07b: сверхдлинный абзац (FT-025). Срез S-07c: отмена очереди (FT-054) — unit `StartTranslation` / `TranslationBridge.cancel` и GUI-кнопка «Отменить перевод». Срез S-08: сбой фрагмента и таймаут 60 с (FT-028). Срез S-09: предупреждение о несохранённом переводе (FT-032, FT-033, UC-006). Срез S-10: ручное «Сохранить перевод» (FT-004, FT-043, FT-044, FT-046, UC-003). Срез S-11: открыть `.txt` / `.md` (FT-003, FT-047, UC-002). Срез S-12: `ExtractSource` для `.docx` / `.pdf` и `DocumentParseError` (FT-039, FT-042); диалог полного набора — `/frontend`. Живой Ollama в тестах не вызывается (MockTransport / фейк-порт). Окно в pytest — `HarnessWindow`: `after` из воркера очередится и выполняется в потоке Tk (`drain_worker_after` в `pump_until`). `event_generate` на `combo-model` доставляет `<Button-1>` / `<FocusIn>` в обработчики окна (CTkComboBox при `withdraw()` события не принимает).

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
| `test_should_keep_user_pick_when_refresh_started_with_old_model` | `tests/test_model_list.py` | FT-045; A0053 | edge | — | выбор во время опроса |
| `test_should_select_default_when_current_model_missing_after_refresh` | `tests/test_model_list.py` | FT-045; A0053 | edge | — | |
| `test_should_not_poll_models_when_window_gains_focus` | `tests/test_model_list.py` | A0079 | negative | — | не опрос при фокусе окна |
| `test_should_show_start_ollama_status_when_api_is_unavailable` | `tests/test_ollama_unavailable.py` | FT-024; NFT-011; US-007 AC1 | negative | error | `start_ollama.bat` и `F:\Docker\Ollama` в статусе |
| `test_should_keep_original_text_when_ollama_becomes_unavailable` | `tests/test_ollama_unavailable.py` | FT-024; US-007 AC1 | negative | error | оригинал не очищается |
| `test_should_enable_translate_when_models_return_after_unavailable` | `tests/test_ollama_unavailable.py` | FT-024; FT-048; A0079; US-007 AC1 | happy | — | клик по «Модель», статус снят |
| `test_should_show_ollama_hint_when_original_empty_and_api_unavailable` | `tests/test_ollama_unavailable.py` | FT-050; A0082; US-008 AC5 | edge | disabled | «Ollama не работает», не «Нет текста…» |
| `test_should_put_russian_translation_in_field_when_user_translates_en_ru` | `tests/test_translation.py` | FT-009; FT-010; FT-016; US-001 AC1 | happy | success | один фрагмент, снимок EN→RU |
| `test_should_put_english_translation_in_field_when_user_translates_ru_en` | `tests/test_translation.py` | FT-002; FT-010; US-009 AC1 | happy | success | подпись «Английский перевод» |
| `test_should_use_selected_model_when_user_translates` | `tests/test_translation.py` | FT-006 | happy | success | не умолчание qwen |
| `test_should_show_progress_zero_then_hundred_when_single_fragment_translates` | `tests/test_translation.py` | FT-022; A0039; NFT-002 | happy | loading | 0 % до ответа, 100 % после |
| `test_should_disable_translate_when_translation_is_in_progress` | `tests/test_translation.py` | FT-031; US-001 AC1 | negative | loading | оригинал не очищается |
| `test_should_show_in_progress_hint_when_pointer_hovers_during_translation` | `tests/test_translation.py` | FT-050; US-008 | negative | loading | не строка статуса |
| `test_should_enable_translate_when_translation_finishes` | `tests/test_translation.py` | FT-031 | happy | success | блокировка снята после ответа |
| `test_should_replace_previous_translation_when_user_translates_again` | `tests/test_translation.py` | FT-035; US-001 AC3 | happy | success | не конкатенация |
| `test_should_keep_request_snapshot_when_fields_change_during_translation` | `tests/test_translation.py` | FT-011; NFT-014; A0052 | edge | loading | клик «Модель» не убивает перевод |
| `test_should_post_chat_to_local_ollama_when_translating_fragment` | `tests/test_ollama_gateway.py` | FT-012; FT-013; A0145 | happy | — | POST /api/chat; `num_predict=-1`; хвост A0145 в user |
| `test_should_raise_empty_instruction_when_instruction_empty_and_not_confirmed` | `tests/test_start_translation.py` | FT-029; A0050 | negative | — | без GUI; Ollama не вызывается |
| `test_should_not_substitute_prompt_when_instruction_empty_even_if_confirmed` | `tests/test_start_translation.py` | FT-029 | negative | — | слой не подставляет промпт |
| `test_should_start_with_snapshot_when_instruction_already_nonempty` | `tests/test_start_translation.py` | FT-011; FT-029 | happy | — | снимок непустой инструкции |
| `test_should_use_en_ru_prompt_in_snapshot_when_start_after_consent` | `tests/test_start_translation.py` | FT-029; A0006; A0050 | happy | — | снимок после согласия EN→RU |
| `test_should_use_ru_en_prompt_in_snapshot_when_start_after_consent` | `tests/test_start_translation.py` | FT-029; A0122 | happy | — | снимок после согласия RU→EN |
| `test_should_raise_empty_instruction_when_bridge_starts_without_ready_prompt` | `tests/test_start_translation.py` | FT-029 | negative | — | клей не стартует воркер |
| `test_should_reject_empty_instruction_when_require_ready_is_called` | `tests/test_start_translation.py` | FT-029 | negative | — | общий гейт |
| `test_should_enable_translate_when_instruction_is_empty_but_original_has_text` | `tests/test_empty_instruction.py` | FT-029 | edge | — | кнопка доступна |
| `test_should_show_empty_instruction_dialog_when_user_translates_without_instruction` | `tests/test_empty_instruction.py` | FT-029; US-005 AC3 | negative | dialog | askokcancel с каноном |
| `test_should_not_start_translation_when_user_cancels_empty_instruction_dialog` | `tests/test_empty_instruction.py` | FT-029; US-005 AC4; A0050 | negative | dialog | отмена без Ollama |
| `test_should_fill_base_prompt_and_translate_when_user_confirms_en_ru` | `tests/test_empty_instruction.py` | FT-029; A0006; A0050 | happy | success | согласие EN→RU |
| `test_should_fill_ru_en_base_prompt_and_translate_when_user_confirms_ru_en` | `tests/test_empty_instruction.py` | FT-029; A0122 | happy | success | согласие RU→EN |
| `test_should_return_one_fragment_when_text_is_at_most_700_chars` | `tests/test_split_text.py` | FT-016; A0141 | happy | — | SplitText без GUI |
| `test_should_split_into_two_fragments_when_text_exceeds_700_with_paragraphs` | `tests/test_split_text.py` | FT-015; FT-018; A0141; A0142 | happy | — | два абзаца; `\n\n` у первого |
| `test_should_preserve_short_paragraphs_in_one_fragment_when_total_under_700` | `tests/test_split_text.py` | FT-018 | edge | — | упаковка в один фрагмент |
| `test_should_split_on_blank_line_when_text_uses_crlf` | `tests/test_split_text.py` | FT-018 | edge | — | Windows `\r\n\r\n` |
| `test_should_split_long_paragraph_on_sentence_boundaries_not_spaces` | `tests/test_split_text.py` | A0142; FT-025 | happy | — | резка по `.` / `?` / `!` |
| `test_should_keep_filename_extension_inside_sentence_when_splitting` | `tests/test_split_text.py` | A0142 | edge | — | `.md file` не граница |
| `test_should_split_after_period_when_numbered_list_follows_without_space` | `tests/test_split_text.py` | A0142 | edge | — | `it.1. What` |
| `test_should_split_after_question_when_next_sentence_has_no_space` | `tests/test_split_text.py` | A0142 | edge | — | `prompt?Only` |
| `test_should_attach_paragraph_break_to_previous_sentence` | `tests/test_split_text.py` | A0142 | edge | — | `\n\n` у предыдущего предложения |
| `test_should_keep_numbered_item_as_one_sentence` | `tests/test_split_text.py` | A0142 | edge | — | не рвать после `1.` |
| `test_should_split_user_en_text_on_real_sentences` | `tests/test_split_text.py` | A0142 | happy | — | образец EN со скрина |
| `test_should_glue_translation_when_long_text_splits_into_fragments` | `tests/test_fragment_queue.py` | FT-015; FT-020 | happy | success | UI + очередь; `\\n\\n` между фрагментами |
| `test_should_keep_blank_line_before_next_fragment_when_model_drops_it` | `tests/test_start_translation.py` | A0142; FT-020 | edge | — | модель съела `\\n\\n` — склейка восстанавливает |
| `test_should_raise_source_limit_when_text_exceeds_100000_chars` | `tests/test_split_text.py` | FT-023; A0036 | negative | — | SourceLimitExceededError |
| `test_should_allow_exactly_100000_chars` | `tests/test_split_text.py` | FT-023 | edge | — | ровно 100k |
| `test_should_translate_fragments_sequentially_when_text_exceeds_700` | `tests/test_start_translation.py` | FT-015; FT-019; FT-020 | happy | — | очередь, склейка |
| `test_should_emit_progress_after_each_fragment_when_queue_runs` | `tests/test_start_translation.py` | FT-022; NFT-005 | happy | — | processed_source_chars |
| `test_should_keep_over_limit_text_in_field_before_translate` | `tests/test_source_limit.py` | FT-014 | happy | — | поле >100k |
| `test_should_not_call_ollama_when_user_translates_over_limit_text` | `tests/test_source_limit.py` | FT-023; US-001 AC4 | negative | error | без Ollama |
| `test_should_keep_original_when_user_translates_over_limit_text` | `tests/test_source_limit.py` | FT-023; A0036 | negative | error | не урезать |
| `test_should_show_limit_message_when_user_translates_over_limit_text` | `tests/test_source_limit.py` | FT-023; A0007 | negative | error | строка статуса |
| `test_should_enable_translate_when_original_exceeds_limit` | `tests/test_source_limit.py` | FT-014 | edge | — | кнопка до «Перевести» |
| `test_should_translate_when_original_is_exactly_100000_chars` | `tests/test_source_limit.py` | FT-023 | edge | success | ровно 100k OK |
| `test_should_strip_russian_instruction_tail_when_model_echoes_it` | `tests/test_ollama_gateway.py` | A0145 | edge | — | хвост не в переводе |
| `test_should_strip_english_instruction_tail_when_model_translates_it` | `tests/test_ollama_gateway.py` | A0145 | edge | — | EN-перевод хвоста и обрывок |
| `test_should_split_text1_into_three_fragments_when_loaded` | `tests/test_text1_ru_en.py` | A0141; A0142 | happy | — | `test-data/Text1.txt`; Task в фрагменте 2 |
| `test_should_start_new_fragment_after_filled_paragraph_break` | `tests/test_split_text.py` | A0141; A0142 | edge | — | абзац ≥500 + `\\n\\n` — новый фрагмент |
| `test_should_translate_all_three_text1_fragments_when_ru_en` | `tests/test_text1_ru_en.py` | FT-015; FT-020; A0145 | happy | — | три вызова Ollama, склейка EN, без утечки хвоста |
| `test_should_copy_translation_when_ctrl_c_uses_cyrillic_es` | `tests/test_clipboard_copy.py` | B-001 | happy | — | RU Ctrl+C, VK_C=67 |
| `test_should_copy_translation_when_ctrl_c_uses_latin_c` | `tests/test_clipboard_copy.py` | B-001 | happy | — | EN Ctrl+C |
| `test_should_treat_cyrillic_es_as_copy_not_paste` | `tests/test_clipboard_copy.py` | B-001 | edge | — | keysym RU C ≠ paste |
| `test_should_add_russian_example_when_direction_is_en_ru` | `tests/test_ollama_gateway.py` | A0006 | edge | — | few-shot EN→RU, без китайского срыва |
| `test_should_add_english_example_when_direction_is_ru_en` | `tests/test_ollama_gateway.py` | A0122 | edge | — | few-shot RU→EN |
| `test_should_never_exceed_hard_cap_700_chars_per_fragment` | `tests/test_split_text.py` | A0159; A0160 | edge | — | потолок 700 |
| `test_should_split_unit_over_700_on_spaces_without_breaking_words` | `tests/test_split_text.py` | FT-025 | happy | — | S-07b, единица >700 |
| `test_should_keep_word_intact_when_sentence_exceeds_700` | `tests/test_split_text.py` | FT-025 | edge | — | слово 600 < 700 не рвать |
| `test_should_not_start_next_fragment_when_user_cancels_queue` | `tests/test_start_translation.py` | FT-054; A0149 | negative | — | без GUI; следующий фрагмент не уходит |
| `test_should_append_in_flight_success_when_user_cancels` | `tests/test_start_translation.py` | A0152 | happy | — | доживший успех в склейке |
| `test_should_keep_incomplete_when_single_fragment_succeeds_after_cancel` | `tests/test_start_translation.py` | A0150; UC-010 | edge | — | один фрагмент, incomplete |
| `test_should_emit_cancelled_not_ollama_when_in_flight_fails_after_cancel` | `tests/test_start_translation.py` | A0153 | negative | — | причина cancelled, не ollama |
| `test_should_not_fill_field_with_fragment_when_cancel_before_any_success` | `tests/test_start_translation.py` | A0148 | negative | — | пустая склейка |
| `test_should_keep_previous_glue_when_cancel_then_later_fragment_fails` | `tests/test_start_translation.py` | NFT-007; A0155 | edge | — | длина склейки не меньше |
| `test_should_not_emit_when_window_stop_is_set_during_queue` | `tests/test_start_translation.py` | FT-054 vs закрытие окна | negative | — | без incomplete |
| `test_should_request_cancel_when_bridge_cancel_is_called` | `tests/test_start_translation.py` | FT-054 | happy | — | `TranslationBridge.cancel` |
| `test_should_stop_queue_when_fragment_times_out` | `tests/test_start_translation.py` | FT-028; A0031 | negative | — | таймаут — incomplete, следующий не стартует |
| `test_should_keep_glue_when_later_fragment_fails` | `tests/test_start_translation.py` | FT-028; A0013 | negative | — | склейка успешных при ошибке модели |
| `test_should_keep_glue_length_when_queue_fails` | `tests/test_start_translation.py` | NFT-007 | edge | — | длина склейки не меньше |
| `test_should_raise_timeout_when_chat_exceeds_60_seconds` | `tests/test_ollama_gateway.py` | FT-028; A0031 | negative | — | ReadTimeout → OllamaTimeoutError |
| `test_should_raise_model_error_when_chat_returns_http_error` | `tests/test_ollama_gateway.py` | FT-028; A0044 | negative | — | HTTP 500 → OllamaModelError |
| `test_should_show_incomplete_status_when_ollama_times_out` | `tests/test_translation_incomplete.py` | FT-028; US-007 AC3 | negative | error | статус, пустое поле, оригинал на месте |
| `test_should_show_incomplete_status_when_model_returns_error` | `tests/test_translation_incomplete.py` | FT-028; A0044 | negative | error | ошибка модели, EN→RU |
| `test_should_keep_glued_translation_when_later_fragment_fails` | `tests/test_translation_incomplete.py` | FT-028; NFT-007 | negative | error | GUI: склейка первого, второй сорвался |
| `test_should_hide_cancel_when_translation_is_idle` | `tests/test_cancel_translation.py` | FT-054; A0147; US-010 AC1 | empty | empty | кнопка в дереве, не в геометрии |
| `test_should_show_cancel_when_translation_is_in_progress` | `tests/test_cancel_translation.py` | FT-054; A0147; US-010 AC1; FT-031; FT-050 | happy | loading | команда видна, Перевести серая |
| `test_should_hide_cancel_immediately_when_user_cancels` | `tests/test_cancel_translation.py` | FT-054; A0151 | negative | loading | скрыть сразу; повторный клик — нет операции |
| `test_should_keep_translate_disabled_when_cancel_waits_for_request` | `tests/test_cancel_translation.py` | FT-031; A0151 | negative | loading | клик не разблокирует Перевести |
| `test_should_show_cancelled_status_when_user_cancels` | `tests/test_cancel_translation.py` | FT-054; A0150; A0152 | negative | error | статус отмены, не FT-028; успех в поле |
| `test_should_not_start_next_fragment_when_user_cancels_from_window` | `tests/test_cancel_translation.py` | FT-054; A0149; FT-020 | negative | error | GUI: второй фрагмент не уходит; поле `first\\n\\n` |
| `test_should_enable_translate_when_cancelled_request_finishes` | `tests/test_cancel_translation.py` | FT-031; A0151 | happy | success | после конца запроса Перевести живая |
| `test_should_keep_cancelled_status_when_in_flight_fails_after_cancel` | `tests/test_cancel_translation.py` | A0153; A0148 | negative | error | сбой после отмены — FT-054, поле пусто |
| `test_should_show_cancelled_status_when_user_cancels_ru_en` | `tests/test_cancel_translation.py` | US-010 AC3 | negative | error | то же при RU→EN |
| `test_should_not_treat_empty_field_as_unsaved_when_saved_flag_is_false` | `tests/test_unsaved_translation.py` | FT-032; US-006 AC4 | edge | — | пустое поле — не несохранённый |
| `test_should_not_treat_nonempty_as_unsaved_when_export_succeeded` | `tests/test_unsaved_translation.py` | FT-033; FT-004 | happy | — | после сохранения |
| `test_should_treat_nonempty_as_unsaved_when_not_exported` | `tests/test_unsaved_translation.py` | FT-033; A0097 | negative | — | гейт без подтверждения |
| `test_should_raise_unsaved_when_queue_starts_without_confirmation` | `tests/test_unsaved_translation.py` | FT-032 | negative | — | Ollama не вызывается |
| `test_should_start_queue_when_unsaved_is_confirmed` | `tests/test_unsaved_translation.py` | FT-032; A0098 | happy | — | после подтверждения |
| `test_should_start_queue_when_incomplete_translation_is_confirmed` | `tests/test_unsaved_translation.py` | A0097 | edge | — | неполный текст |
| `test_should_raise_unsaved_when_bridge_starts_without_confirmation` | `tests/test_unsaved_translation.py` | FT-032 | negative | — | клей не стартует воркер |
| `test_should_mark_saved_when_translation_field_becomes_empty` | `tests/test_unsaved_translation.py` | FT-033 | edge | — | пустое = сохранённое |
| `test_should_mark_saved_when_export_succeeds` | `tests/test_unsaved_translation.py` | FT-004 | happy | — | сохранённость |
| `test_should_clear_translation_when_source_loaded_successfully` | `tests/test_unsaved_translation.py` | A0099 | happy | — | очистка после загрузки |
| `test_should_show_unsaved_dialog_when_user_translates_with_unsaved_text` | `tests/test_unsaved_warning.py` | FT-032; US-006 AC1 | negative | dialog | «Перевести» |
| `test_should_not_start_translation_when_user_cancels_unsaved_dialog` | `tests/test_unsaved_warning.py` | FT-032; A0098; NFT-008 | negative | dialog | отмена, поля на месте |
| `test_should_replace_translation_when_user_confirms_unsaved_and_translates` | `tests/test_unsaved_warning.py` | FT-032; FT-035; US-006 AC1 | happy | success | замена поля |
| `test_should_show_unsaved_dialog_when_user_opens_file_with_unsaved_text` | `tests/test_unsaved_warning.py` | FT-032; US-006 AC2 | negative | dialog | «Открыть файл» |
| `test_should_keep_fields_when_user_cancels_unsaved_dialog_before_open_file` | `tests/test_unsaved_warning.py` | FT-032; A0098; NFT-008 | negative | dialog | отмена открытия |
| `test_should_clear_translation_when_source_loaded_after_unsaved_confirm` | `tests/test_unsaved_warning.py` | A0099; US-006 AC2 | happy | — | загрузка очищает перевод |
| `test_should_not_show_unsaved_dialog_when_translation_is_empty` | `tests/test_unsaved_warning.py` | FT-032; US-006 AC4 | edge | empty | пустое поле |
| `test_should_not_show_unsaved_dialog_when_translation_was_saved` | `tests/test_unsaved_warning.py` | FT-032; FT-004; US-006 AC3 | happy | — | после «Сохранить перевод» |
| `test_should_show_unsaved_dialog_when_user_edits_after_save` | `tests/test_unsaved_warning.py` | FT-033; A0106 | negative | dialog | правка сбрасывает сохранённость |
| `test_should_not_show_unsaved_dialog_when_only_direction_changes` | `tests/test_unsaved_warning.py` | FT-053; A0124 | negative | — | не триггер FT-032 |
| `test_should_ask_empty_instruction_after_unsaved_confirm_when_both_apply` | `tests/test_unsaved_warning.py` | A0102 | edge | dialog | FT-032 затем FT-029 |
| `test_should_show_unsaved_dialog_when_incomplete_translation_is_not_saved` | `tests/test_unsaved_warning.py` | A0097; US-006 AC4 | negative | dialog | неполный перевод |
| `test_should_write_field_contents_to_txt_when_export_runs` | `tests/test_export_translation.py` | FT-004; US-003 AC1 | happy | — | UTF-8, без GUI |
| `test_should_write_field_contents_to_docx_when_export_runs` | `tests/test_export_translation.py` | FT-004; FT-046 | happy | — | python-docx |
| `test_should_overwrite_existing_file_when_export_is_invoked` | `tests/test_export_translation.py` | FT-043 | happy | — | после согласия ОС |
| `test_should_raise_write_error_when_translation_is_empty` | `tests/test_export_translation.py` | FT-027 | negative | — | файл не создаётся |
| `test_should_raise_write_error_when_format_is_not_txt_or_docx` | `tests/test_export_translation.py` | FT-046 | negative | — | .pdf не пишется |
| `test_should_raise_write_error_when_path_cannot_be_written` | `tests/test_export_translation.py` | FT-044 | negative | — | каталог вместо файла |
| `test_should_keep_unsaved_when_export_raises` | `tests/test_export_translation.py` | FT-044; FT-033 | negative | — | флаг не меняет сбой |
| `test_should_notify_success_when_export_bridge_writes` | `tests/test_export_translation.py` | FT-004 | happy | — | клей on_success |
| `test_should_notify_error_when_export_bridge_write_fails` | `tests/test_export_translation.py` | FT-044 | negative | — | клей on_error |
| `test_should_write_translation_field_to_txt_when_user_saves` | `tests/test_export_save.py` | FT-004; US-003 AC1 | happy | success | GUI .txt |
| `test_should_write_translation_field_to_docx_when_user_saves` | `tests/test_export_save.py` | FT-004; FT-046 | happy | success | GUI .docx |
| `test_should_offer_only_txt_and_docx_when_save_dialog_opens` | `tests/test_export_save.py` | FT-046 | happy | dialog | filetypes |
| `test_should_not_change_existing_file_when_user_cancels_save_dialog` | `tests/test_export_save.py` | FT-043; US-003 AC4 | negative | dialog | отмена |
| `test_should_keep_translation_and_enable_save_when_write_fails` | `tests/test_export_save.py` | FT-044; A0104 | negative | error | поле и кнопка |
| `test_should_return_utf8_text_when_txt_file_is_readable` | `tests/test_extract_source.py` | FT-003 | happy | — | UTF-8 |
| `test_should_return_text_when_file_has_utf8_bom` | `tests/test_extract_source.py` | FT-003 | edge | — | utf-8-sig |
| `test_should_fallback_to_cp1251_when_utf8_fails` | `tests/test_extract_source.py` | FT-003 | edge | — | Windows-1251 |
| `test_should_return_markdown_text_when_md_file_is_readable` | `tests/test_extract_source.py` | FT-003 | happy | — | `.md` |
| `test_should_raise_parse_error_when_file_is_empty` | `tests/test_extract_source.py` | FT-039; S-11 | negative | — | пустой файл |
| `test_should_raise_parse_error_when_file_is_only_whitespace` | `tests/test_extract_source.py` | FT-039; S-11 | negative | — | пробелы |
| `test_should_return_paragraphs_when_docx_has_text` | `tests/test_extract_source.py` | FT-003; FT-042; S-12 | happy | — | python-docx |
| `test_should_return_page_text_when_pdf_has_extractable_text` | `tests/test_extract_source.py` | FT-003; FT-042; S-12 | happy | — | pypdf |
| `test_should_raise_parse_error_when_docx_is_empty` | `tests/test_extract_source.py` | FT-039; S-12 | negative | — | пустой docx |
| `test_should_raise_parse_error_when_pdf_has_no_text_layer` | `tests/test_extract_source.py` | FT-039; S-12 | negative | — | скан без текста |
| `test_should_raise_parse_error_when_docx_is_corrupt` | `tests/test_extract_source.py` | FT-039; UC-002 E2 | negative | — | битый docx |
| `test_should_raise_parse_error_when_pdf_is_corrupt` | `tests/test_extract_source.py` | FT-039; UC-002 E2 | negative | — | битый pdf |
| `test_should_return_text_when_load_source_opens_docx` | `tests/test_extract_source.py` | FT-003; S-12 | happy | — | LoadSource |
| `test_should_raise_parse_error_when_file_cannot_be_read` | `tests/test_extract_source.py` | UC-002 E1 | negative | — | нет файла |
| `test_should_keep_text_longer_than_100k_when_extracted` | `tests/test_extract_source.py` | S-11; FT-030 | edge | — | лимит на перевод |
| `test_should_return_text_when_load_source_use_case_runs` | `tests/test_extract_source.py` | FT-003 | happy | — | LoadSource |
| `test_should_notify_success_when_load_bridge_reads` | `tests/test_extract_source.py` | FT-003 | happy | — | клей |
| `test_should_notify_error_when_load_bridge_parse_fails` | `tests/test_extract_source.py` | FT-039 | negative | — | клей |
| `test_should_put_txt_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | FT-003; US-002 AC1 | happy | success | GUI .txt |
| `test_should_put_md_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | FT-003 | happy | success | GUI .md |
| `test_should_offer_txt_md_docx_pdf_when_open_dialog_opens` | `tests/test_open_source.py` | FT-042; S-12 | happy | dialog | фильтр по умолчанию — все четыре |
| `test_should_keep_original_when_user_cancels_open_dialog` | `tests/test_open_source.py` | FT-047; US-002 AC4 | negative | dialog | отмена |
| `test_should_keep_original_and_show_message_when_txt_is_empty` | `tests/test_open_source.py` | FT-039; S-11 | negative | error | поле на месте |
| `test_should_clear_translation_when_open_file_succeeds` | `tests/test_open_source.py` | A0099 | happy | success | очистка перевода |
| `test_should_keep_translation_when_open_file_fails` | `tests/test_open_source.py` | UC-002 | negative | error | перевод на месте |
| `test_should_put_docx_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | FT-003; FT-042; S-12 | happy | success | GUI .docx |
| `test_should_put_pdf_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | FT-003; FT-042; S-12 | happy | success | GUI .pdf |
| `test_should_keep_original_and_show_message_when_pdf_has_no_text` | `tests/test_open_source.py` | FT-039; S-12 | negative | error | скан PDF |
| `test_should_not_open_other_format_when_path_is_not_allowed` | `tests/test_open_source.py` | FT-042; A0046 | negative | error | .xlsx не открывать |
