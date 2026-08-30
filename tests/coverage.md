# Карта покрытия автотестов TranslateText

Поверхность: desktop (CustomTkinter). Раннер: pytest. Прогон — команда `/use-tests`.

Срез S-01: подписи, пустые поля, блокировки, направление перевода (FT-051…FT-053). Срез S-02: опрос `GET /api/tags`, выбор модели, клик/фокус «Модель» в окне. Срез S-03: статус FT-024, восстановление по клику на «Модель», приоритет подсказки FT-050, оригинал не очищается. Срез S-04: «Перевести» одного короткого фрагмента (EN→RU / RU→EN), прогресс 0/100, снимок FT-011, замена поля. Срез S-05: пустая инструкция — диалог FT-029, согласие или отмена, базовый промпт текущего направления. Срез S-06: лимит 100 000 символов Unicode — поле держит >100k, отказ при «Перевести» без Ollama. Срез S-07: нарезка по абзацам, очередь перевода, прогресс по доле исходника, склейка. Срез S-07b: сверхдлинный абзац (FT-025). Срез S-07c: отмена очереди (FT-054) — unit `StartTranslation` / `TranslationBridge.cancel` без GUI. Живой Ollama в тестах не вызывается (MockTransport / фейк-порт). Окно в pytest — `HarnessWindow`: `after` из воркера очередится и выполняется в потоке Tk (`drain_worker_after` в `pump_until`). `event_generate` на `combo-model` доставляет `<Button-1>` / `<FocusIn>` в обработчики окна (CTkComboBox при `withdraw()` события не принимает).

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
| `test_should_split_paragraph_over_5000_on_sentences_without_breaking_words` | `tests/test_split_text.py` | FT-025 | happy | — | S-07b, абзац >5000 |
| `test_should_keep_word_intact_when_sentence_exceeds_5000` | `tests/test_split_text.py` | FT-025 | edge | — | слово 800 < 5000 не рвать |
| `test_should_not_start_next_fragment_when_user_cancels_queue` | `tests/test_start_translation.py` | FT-054; A0149 | negative | — | без GUI; следующий фрагмент не уходит |
| `test_should_append_in_flight_success_when_user_cancels` | `tests/test_start_translation.py` | A0152 | happy | — | доживший успех в склейке |
| `test_should_keep_incomplete_when_single_fragment_succeeds_after_cancel` | `tests/test_start_translation.py` | A0150; UC-010 | edge | — | один фрагмент, incomplete |
| `test_should_emit_cancelled_not_ollama_when_in_flight_fails_after_cancel` | `tests/test_start_translation.py` | A0153 | negative | — | причина cancelled, не ollama |
| `test_should_not_fill_field_with_fragment_when_cancel_before_any_success` | `tests/test_start_translation.py` | A0148 | negative | — | пустая склейка |
| `test_should_keep_previous_glue_when_cancel_then_later_fragment_fails` | `tests/test_start_translation.py` | NFT-007; A0155 | edge | — | длина склейки не меньше |
| `test_should_not_emit_when_window_stop_is_set_during_queue` | `tests/test_start_translation.py` | FT-054 vs закрытие окна | negative | — | без incomplete |
| `test_should_request_cancel_when_bridge_cancel_is_called` | `tests/test_start_translation.py` | FT-054 | happy | — | `TranslationBridge.cancel` |
