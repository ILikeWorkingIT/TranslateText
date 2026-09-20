# Прогон автотестов TranslateText

Дата: 2026-09-20 09:56  
Команда: `python -m pytest tests -v --tb=short`  
OS: Windows 10 (win32), Python 3.12.0, pytest-9.1.1  
Каталог: `e:\Cursor\TranslateText`  
Итог: 201 passed, 0 failed, 0 error, 0 skipped  
Длительность: 27.78 с  
Режим: прогон  
Попыток фикса: 0 / 2; полных прогонов: 1 / 4

## Кратко

Полный набор pytest по поверхности desktop/customtkinter зелёный. Живой Ollama не вызывался (MockTransport / фейк-порт). Очередь исправления пуста. Ниже — сводка по файлам и статус каждого из 201 тестов этого прогона.

## Очередь исправления

| ID | Тест | Файл теста | Тип | Воспроизведение | Ожидание | Факт | Требования | Где чинить | Доказательство | Статус |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | — | — | — | — | — | — | — | — | — | пусто |

## Как чинить

Правок не требуется: падений нет.

## Сводка по файлам

| Файл | Тестов | Итог |
| --- | --- | --- |
| `tests/test_blocking.py` | 10 | passed |
| `tests/test_cancel_translation.py` | 9 | passed |
| `tests/test_clipboard_copy.py` | 3 | passed |
| `tests/test_direction.py` | 7 | passed |
| `tests/test_empty_instruction.py` | 5 | passed |
| `tests/test_export_save.py` | 5 | passed |
| `tests/test_export_translation.py` | 9 | passed |
| `tests/test_extract_source.py` | 18 | passed |
| `tests/test_fragment_queue.py` | 1 | passed |
| `tests/test_main_screen.py` | 10 | passed |
| `tests/test_model_list.py` | 9 | passed |
| `tests/test_ollama_gateway.py` | 11 | passed |
| `tests/test_ollama_unavailable.py` | 4 | passed |
| `tests/test_open_source.py` | 11 | passed |
| `tests/test_refresh_models.py` | 6 | passed |
| `tests/test_source_limit.py` | 6 | passed |
| `tests/test_split_text.py` | 19 | passed |
| `tests/test_start_translation.py` | 21 | passed |
| `tests/test_text1_ru_en.py` | 2 | passed |
| `tests/test_translation.py` | 9 | passed |
| `tests/test_translation_incomplete.py` | 3 | passed |
| `tests/test_unsaved_translation.py` | 10 | passed |
| `tests/test_unsaved_warning.py` | 12 | passed |
| `tests/test_user_ru_en_texts.py` | 1 | passed |

## Результаты тестов

| Тест | Файл | Статус |
| --- | --- | --- |
| `test_should_disable_translate_when_original_is_empty` | `tests/test_blocking.py` | passed |
| `test_should_enable_translate_when_original_has_text` | `tests/test_blocking.py` | passed |
| `test_should_enable_translate_when_original_is_only_spaces` | `tests/test_blocking.py` | passed |
| `test_should_disable_save_when_translation_is_empty` | `tests/test_blocking.py` | passed |
| `test_should_enable_save_when_translation_has_text` | `tests/test_blocking.py` | passed |
| `test_should_disable_translate_when_model_list_is_empty` | `tests/test_blocking.py` | passed |
| `test_should_keep_model_list_enabled_when_model_list_is_empty` | `tests/test_blocking.py` | passed |
| `test_should_show_no_text_hint_when_pointer_hovers_blocked_translate` | `tests/test_blocking.py` | passed |
| `test_should_not_show_no_text_hint_when_pointer_is_not_on_translate` | `tests/test_blocking.py` | passed |
| `test_should_hide_blocking_hints_when_translate_is_enabled` | `tests/test_blocking.py` | passed |
| `test_should_hide_cancel_when_translation_is_idle` | `tests/test_cancel_translation.py` | passed |
| `test_should_show_cancel_when_translation_is_in_progress` | `tests/test_cancel_translation.py` | passed |
| `test_should_hide_cancel_immediately_when_user_cancels` | `tests/test_cancel_translation.py` | passed |
| `test_should_keep_translate_disabled_when_cancel_waits_for_request` | `tests/test_cancel_translation.py` | passed |
| `test_should_show_cancelled_status_when_user_cancels` | `tests/test_cancel_translation.py` | passed |
| `test_should_not_start_next_fragment_when_user_cancels_from_window` | `tests/test_cancel_translation.py` | passed |
| `test_should_enable_translate_when_cancelled_request_finishes` | `tests/test_cancel_translation.py` | passed |
| `test_should_keep_cancelled_status_when_in_flight_fails_after_cancel` | `tests/test_cancel_translation.py` | passed |
| `test_should_show_cancelled_status_when_user_cancels_ru_en` | `tests/test_cancel_translation.py` | passed |
| `test_should_treat_cyrillic_es_as_copy_not_paste` | `tests/test_clipboard_copy.py` | passed |
| `test_should_copy_translation_when_ctrl_c_uses_cyrillic_es` | `tests/test_clipboard_copy.py` | passed |
| `test_should_copy_translation_when_ctrl_c_uses_latin_c` | `tests/test_clipboard_copy.py` | passed |
| `test_should_select_en_ru_when_window_opens` | `tests/test_direction.py` | passed |
| `test_should_offer_only_en_ru_and_ru_en_when_window_opens` | `tests/test_direction.py` | passed |
| `test_should_show_ru_en_base_prompt_when_direction_changes_and_instruction_is_base` | `tests/test_direction.py` | passed |
| `test_should_keep_custom_instruction_when_direction_changes` | `tests/test_direction.py` | passed |
| `test_should_show_english_translation_label_when_direction_is_ru_en` | `tests/test_direction.py` | passed |
| `test_should_keep_translation_text_when_direction_changes` | `tests/test_direction.py` | passed |
| `test_should_not_show_ollama_status_when_only_direction_changes` | `tests/test_direction.py` | passed |
| `test_should_enable_translate_when_instruction_is_empty_but_original_has_text` | `tests/test_empty_instruction.py` | passed |
| `test_should_show_empty_instruction_dialog_when_user_translates_without_instruction` | `tests/test_empty_instruction.py` | passed |
| `test_should_not_start_translation_when_user_cancels_empty_instruction_dialog` | `tests/test_empty_instruction.py` | passed |
| `test_should_fill_base_prompt_and_translate_when_user_confirms_en_ru` | `tests/test_empty_instruction.py` | passed |
| `test_should_fill_ru_en_base_prompt_and_translate_when_user_confirms_ru_en` | `tests/test_empty_instruction.py` | passed |
| `test_should_write_translation_field_to_txt_when_user_saves` | `tests/test_export_save.py` | passed |
| `test_should_write_translation_field_to_docx_when_user_saves` | `tests/test_export_save.py` | passed |
| `test_should_offer_only_txt_and_docx_when_save_dialog_opens` | `tests/test_export_save.py` | passed |
| `test_should_not_change_existing_file_when_user_cancels_save_dialog` | `tests/test_export_save.py` | passed |
| `test_should_keep_translation_and_enable_save_when_write_fails` | `tests/test_export_save.py` | passed |
| `test_should_write_field_contents_to_txt_when_export_runs` | `tests/test_export_translation.py` | passed |
| `test_should_write_field_contents_to_docx_when_export_runs` | `tests/test_export_translation.py` | passed |
| `test_should_overwrite_existing_file_when_export_is_invoked` | `tests/test_export_translation.py` | passed |
| `test_should_raise_write_error_when_translation_is_empty` | `tests/test_export_translation.py` | passed |
| `test_should_raise_write_error_when_format_is_not_txt_or_docx` | `tests/test_export_translation.py` | passed |
| `test_should_raise_write_error_when_path_cannot_be_written` | `tests/test_export_translation.py` | passed |
| `test_should_keep_unsaved_when_export_raises` | `tests/test_export_translation.py` | passed |
| `test_should_notify_success_when_export_bridge_writes` | `tests/test_export_translation.py` | passed |
| `test_should_notify_error_when_export_bridge_write_fails` | `tests/test_export_translation.py` | passed |
| `test_should_return_utf8_text_when_txt_file_is_readable` | `tests/test_extract_source.py` | passed |
| `test_should_return_text_when_file_has_utf8_bom` | `tests/test_extract_source.py` | passed |
| `test_should_fallback_to_cp1251_when_utf8_fails` | `tests/test_extract_source.py` | passed |
| `test_should_return_markdown_text_when_md_file_is_readable` | `tests/test_extract_source.py` | passed |
| `test_should_raise_parse_error_when_file_is_empty` | `tests/test_extract_source.py` | passed |
| `test_should_raise_parse_error_when_file_is_only_whitespace` | `tests/test_extract_source.py` | passed |
| `test_should_return_paragraphs_when_docx_has_text` | `tests/test_extract_source.py` | passed |
| `test_should_return_page_text_when_pdf_has_extractable_text` | `tests/test_extract_source.py` | passed |
| `test_should_raise_parse_error_when_docx_is_empty` | `tests/test_extract_source.py` | passed |
| `test_should_raise_parse_error_when_pdf_has_no_text_layer` | `tests/test_extract_source.py` | passed |
| `test_should_raise_parse_error_when_docx_is_corrupt` | `tests/test_extract_source.py` | passed |
| `test_should_raise_parse_error_when_pdf_is_corrupt` | `tests/test_extract_source.py` | passed |
| `test_should_return_text_when_load_source_opens_docx` | `tests/test_extract_source.py` | passed |
| `test_should_raise_parse_error_when_file_cannot_be_read` | `tests/test_extract_source.py` | passed |
| `test_should_keep_text_longer_than_100k_when_extracted` | `tests/test_extract_source.py` | passed |
| `test_should_return_text_when_load_source_use_case_runs` | `tests/test_extract_source.py` | passed |
| `test_should_notify_success_when_load_bridge_reads` | `tests/test_extract_source.py` | passed |
| `test_should_notify_error_when_load_bridge_parse_fails` | `tests/test_extract_source.py` | passed |
| `test_should_glue_translation_when_long_text_splits_into_fragments` | `tests/test_fragment_queue.py` | passed |
| `test_should_show_all_glossary_labels_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_show_original_text_field_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_show_translation_field_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_show_custom_instruction_field_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_show_base_prompt_when_user_has_not_replaced_instruction` | `tests/test_main_screen.py` | passed |
| `test_should_show_model_list_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_show_progress_indicator_at_zero_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_show_empty_original_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_show_empty_translation_when_window_opens` | `tests/test_main_screen.py` | passed |
| `test_should_keep_replaced_instruction_when_user_edits_field` | `tests/test_main_screen.py` | passed |
| `test_should_select_qwen_when_window_opens_and_preferred_is_available` | `tests/test_model_list.py` | passed |
| `test_should_select_first_model_when_window_opens_without_qwen` | `tests/test_model_list.py` | passed |
| `test_should_show_all_api_names_when_list_includes_non_qwen` | `tests/test_model_list.py` | passed |
| `test_should_update_model_list_when_user_clicks_model` | `tests/test_model_list.py` | passed |
| `test_should_update_model_list_when_model_receives_focus` | `tests/test_model_list.py` | passed |
| `test_should_keep_selected_model_when_it_remains_in_new_response` | `tests/test_model_list.py` | passed |
| `test_should_keep_user_pick_when_refresh_started_with_old_model` | `tests/test_model_list.py` | passed |
| `test_should_select_default_when_current_model_missing_after_refresh` | `tests/test_model_list.py` | passed |
| `test_should_not_poll_models_when_window_gains_focus` | `tests/test_model_list.py` | passed |
| `test_should_return_all_model_names_when_tags_response_has_several` | `tests/test_ollama_gateway.py` | passed |
| `test_should_raise_unavailable_when_model_list_is_empty` | `tests/test_ollama_gateway.py` | passed |
| `test_should_raise_unavailable_when_tags_request_fails` | `tests/test_ollama_gateway.py` | passed |
| `test_should_close_httpx_client_when_gateway_closes` | `tests/test_ollama_gateway.py` | passed |
| `test_should_post_chat_to_local_ollama_when_translating_fragment` | `tests/test_ollama_gateway.py` | passed |
| `test_should_strip_russian_instruction_tail_when_model_echoes_it` | `tests/test_ollama_gateway.py` | passed |
| `test_should_strip_english_instruction_tail_when_model_translates_it` | `tests/test_ollama_gateway.py` | passed |
| `test_should_add_russian_example_when_direction_is_en_ru` | `tests/test_ollama_gateway.py` | passed |
| `test_should_add_english_example_when_direction_is_ru_en` | `tests/test_ollama_gateway.py` | passed |
| `test_should_raise_timeout_when_chat_exceeds_60_seconds` | `tests/test_ollama_gateway.py` | passed |
| `test_should_raise_model_error_when_chat_returns_http_error` | `tests/test_ollama_gateway.py` | passed |
| `test_should_show_start_ollama_status_when_api_is_unavailable` | `tests/test_ollama_unavailable.py` | passed |
| `test_should_keep_original_text_when_ollama_becomes_unavailable` | `tests/test_ollama_unavailable.py` | passed |
| `test_should_enable_translate_when_models_return_after_unavailable` | `tests/test_ollama_unavailable.py` | passed |
| `test_should_show_ollama_hint_when_original_empty_and_api_unavailable` | `tests/test_ollama_unavailable.py` | passed |
| `test_should_put_txt_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | passed |
| `test_should_put_md_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | passed |
| `test_should_offer_txt_md_docx_pdf_when_open_dialog_opens` | `tests/test_open_source.py` | passed |
| `test_should_keep_original_when_user_cancels_open_dialog` | `tests/test_open_source.py` | passed |
| `test_should_keep_original_and_show_message_when_txt_is_empty` | `tests/test_open_source.py` | passed |
| `test_should_clear_translation_when_open_file_succeeds` | `tests/test_open_source.py` | passed |
| `test_should_keep_translation_when_open_file_fails` | `tests/test_open_source.py` | passed |
| `test_should_put_docx_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | passed |
| `test_should_put_pdf_contents_in_original_when_user_opens_file` | `tests/test_open_source.py` | passed |
| `test_should_keep_original_and_show_message_when_pdf_has_no_text` | `tests/test_open_source.py` | passed |
| `test_should_not_open_other_format_when_path_is_not_allowed` | `tests/test_open_source.py` | passed |
| `test_should_select_qwen_when_preferred_model_is_in_response` | `tests/test_refresh_models.py` | passed |
| `test_should_select_first_model_when_qwen_is_absent` | `tests/test_refresh_models.py` | passed |
| `test_should_keep_current_model_when_it_remains_in_response` | `tests/test_refresh_models.py` | passed |
| `test_should_apply_default_rule_when_current_model_disappeared` | `tests/test_refresh_models.py` | passed |
| `test_should_keep_all_api_names_when_list_includes_non_qwen` | `tests/test_refresh_models.py` | passed |
| `test_should_raise_unavailable_when_port_returns_empty_list` | `tests/test_refresh_models.py` | passed |
| `test_should_keep_over_limit_text_in_field_before_translate` | `tests/test_source_limit.py` | passed |
| `test_should_not_call_ollama_when_user_translates_over_limit_text` | `tests/test_source_limit.py` | passed |
| `test_should_keep_original_when_user_translates_over_limit_text` | `tests/test_source_limit.py` | passed |
| `test_should_show_limit_message_when_user_translates_over_limit_text` | `tests/test_source_limit.py` | passed |
| `test_should_enable_translate_when_original_exceeds_limit` | `tests/test_source_limit.py` | passed |
| `test_should_translate_when_original_is_exactly_100000_chars` | `tests/test_source_limit.py` | passed |
| `test_should_return_one_fragment_when_text_is_at_most_700_chars` | `tests/test_split_text.py` | passed |
| `test_should_split_into_two_fragments_when_text_exceeds_700_with_paragraphs` | `tests/test_split_text.py` | passed |
| `test_should_split_long_paragraph_into_700_char_chunks` | `tests/test_split_text.py` | passed |
| `test_should_preserve_short_paragraphs_in_one_fragment_when_total_under_700` | `tests/test_split_text.py` | passed |
| `test_should_split_on_single_newline_when_no_blank_line` | `tests/test_split_text.py` | passed |
| `test_should_split_on_blank_line_when_text_uses_crlf` | `tests/test_split_text.py` | passed |
| `test_should_split_100000_chars_into_many_fragments` | `tests/test_split_text.py` | passed |
| `test_should_raise_source_limit_when_text_exceeds_100000_chars` | `tests/test_split_text.py` | passed |
| `test_should_split_long_paragraph_on_sentence_boundaries_not_spaces` | `tests/test_split_text.py` | passed |
| `test_should_keep_filename_extension_inside_sentence_when_splitting` | `tests/test_split_text.py` | passed |
| `test_should_split_after_period_when_numbered_list_follows_without_space` | `tests/test_split_text.py` | passed |
| `test_should_split_after_question_when_next_sentence_has_no_space` | `tests/test_split_text.py` | passed |
| `test_should_attach_paragraph_break_to_previous_sentence` | `tests/test_split_text.py` | passed |
| `test_should_keep_numbered_item_as_one_sentence` | `tests/test_split_text.py` | passed |
| `test_should_start_new_fragment_after_filled_paragraph_break` | `tests/test_split_text.py` | passed |
| `test_should_split_user_en_text_on_real_sentences` | `tests/test_split_text.py` | passed |
| `test_should_never_exceed_hard_cap_700_chars_per_fragment` | `tests/test_split_text.py` | passed |
| `test_should_split_unit_over_700_on_spaces_without_breaking_words` | `tests/test_split_text.py` | passed |
| `test_should_keep_word_intact_when_sentence_exceeds_700` | `tests/test_split_text.py` | passed |
| `test_should_raise_empty_instruction_when_instruction_empty_and_not_confirmed` | `tests/test_start_translation.py` | passed |
| `test_should_not_substitute_prompt_when_instruction_empty_even_if_confirmed` | `tests/test_start_translation.py` | passed |
| `test_should_start_with_snapshot_when_instruction_already_nonempty` | `tests/test_start_translation.py` | passed |
| `test_should_use_en_ru_prompt_in_snapshot_when_start_after_consent` | `tests/test_start_translation.py` | passed |
| `test_should_use_ru_en_prompt_in_snapshot_when_start_after_consent` | `tests/test_start_translation.py` | passed |
| `test_should_raise_empty_instruction_when_bridge_starts_without_ready_prompt` | `tests/test_start_translation.py` | passed |
| `test_should_reject_empty_instruction_when_require_ready_is_called` | `tests/test_start_translation.py` | passed |
| `test_should_translate_fragments_sequentially_when_text_exceeds_700` | `tests/test_start_translation.py` | passed |
| `test_should_emit_progress_after_each_fragment_when_queue_runs` | `tests/test_start_translation.py` | passed |
| `test_should_keep_blank_line_before_next_fragment_when_model_drops_it` | `tests/test_start_translation.py` | passed |
| `test_should_not_start_next_fragment_when_user_cancels_queue` | `tests/test_start_translation.py` | passed |
| `test_should_append_in_flight_success_when_user_cancels` | `tests/test_start_translation.py` | passed |
| `test_should_keep_incomplete_when_single_fragment_succeeds_after_cancel` | `tests/test_start_translation.py` | passed |
| `test_should_emit_cancelled_not_ollama_when_in_flight_fails_after_cancel` | `tests/test_start_translation.py` | passed |
| `test_should_not_fill_field_with_fragment_when_cancel_before_any_success` | `tests/test_start_translation.py` | passed |
| `test_should_keep_previous_glue_when_cancel_then_later_fragment_fails` | `tests/test_start_translation.py` | passed |
| `test_should_not_emit_when_window_stop_is_set_during_queue` | `tests/test_start_translation.py` | passed |
| `test_should_request_cancel_when_bridge_cancel_is_called` | `tests/test_start_translation.py` | passed |
| `test_should_stop_queue_when_fragment_times_out` | `tests/test_start_translation.py` | passed |
| `test_should_keep_glue_when_later_fragment_fails` | `tests/test_start_translation.py` | passed |
| `test_should_keep_glue_length_when_queue_fails` | `tests/test_start_translation.py` | passed |
| `test_should_split_text1_into_three_fragments_when_loaded` | `tests/test_text1_ru_en.py` | passed |
| `test_should_translate_all_three_text1_fragments_when_ru_en` | `tests/test_text1_ru_en.py` | passed |
| `test_should_put_russian_translation_in_field_when_user_translates_en_ru` | `tests/test_translation.py` | passed |
| `test_should_put_english_translation_in_field_when_user_translates_ru_en` | `tests/test_translation.py` | passed |
| `test_should_use_selected_model_when_user_translates` | `tests/test_translation.py` | passed |
| `test_should_show_progress_zero_then_hundred_when_single_fragment_translates` | `tests/test_translation.py` | passed |
| `test_should_disable_translate_when_translation_is_in_progress` | `tests/test_translation.py` | passed |
| `test_should_show_in_progress_hint_when_pointer_hovers_during_translation` | `tests/test_translation.py` | passed |
| `test_should_enable_translate_when_translation_finishes` | `tests/test_translation.py` | passed |
| `test_should_replace_previous_translation_when_user_translates_again` | `tests/test_translation.py` | passed |
| `test_should_keep_request_snapshot_when_fields_change_during_translation` | `tests/test_translation.py` | passed |
| `test_should_show_incomplete_status_when_ollama_times_out` | `tests/test_translation_incomplete.py` | passed |
| `test_should_show_incomplete_status_when_model_returns_error` | `tests/test_translation_incomplete.py` | passed |
| `test_should_keep_glued_translation_when_later_fragment_fails` | `tests/test_translation_incomplete.py` | passed |
| `test_should_not_treat_empty_field_as_unsaved_when_saved_flag_is_false` | `tests/test_unsaved_translation.py` | passed |
| `test_should_not_treat_nonempty_as_unsaved_when_export_succeeded` | `tests/test_unsaved_translation.py` | passed |
| `test_should_treat_nonempty_as_unsaved_when_not_exported` | `tests/test_unsaved_translation.py` | passed |
| `test_should_raise_unsaved_when_queue_starts_without_confirmation` | `tests/test_unsaved_translation.py` | passed |
| `test_should_start_queue_when_unsaved_is_confirmed` | `tests/test_unsaved_translation.py` | passed |
| `test_should_start_queue_when_incomplete_translation_is_confirmed` | `tests/test_unsaved_translation.py` | passed |
| `test_should_raise_unsaved_when_bridge_starts_without_confirmation` | `tests/test_unsaved_translation.py` | passed |
| `test_should_mark_saved_when_translation_field_becomes_empty` | `tests/test_unsaved_translation.py` | passed |
| `test_should_mark_saved_when_export_succeeds` | `tests/test_unsaved_translation.py` | passed |
| `test_should_clear_translation_when_source_loaded_successfully` | `tests/test_unsaved_translation.py` | passed |
| `test_should_show_unsaved_dialog_when_user_translates_with_unsaved_text` | `tests/test_unsaved_warning.py` | passed |
| `test_should_not_start_translation_when_user_cancels_unsaved_dialog` | `tests/test_unsaved_warning.py` | passed |
| `test_should_replace_translation_when_user_confirms_unsaved_and_translates` | `tests/test_unsaved_warning.py` | passed |
| `test_should_show_unsaved_dialog_when_user_opens_file_with_unsaved_text` | `tests/test_unsaved_warning.py` | passed |
| `test_should_keep_fields_when_user_cancels_unsaved_dialog_before_open_file` | `tests/test_unsaved_warning.py` | passed |
| `test_should_clear_translation_when_source_loaded_after_unsaved_confirm` | `tests/test_unsaved_warning.py` | passed |
| `test_should_not_show_unsaved_dialog_when_translation_is_empty` | `tests/test_unsaved_warning.py` | passed |
| `test_should_not_show_unsaved_dialog_when_translation_was_saved` | `tests/test_unsaved_warning.py` | passed |
| `test_should_show_unsaved_dialog_when_user_edits_after_save` | `tests/test_unsaved_warning.py` | passed |
| `test_should_not_show_unsaved_dialog_when_only_direction_changes` | `tests/test_unsaved_warning.py` | passed |
| `test_should_ask_empty_instruction_after_unsaved_confirm_when_both_apply` | `tests/test_unsaved_warning.py` | passed |
| `test_should_show_unsaved_dialog_when_incomplete_translation_is_not_saved` | `tests/test_unsaved_warning.py` | passed |
| `test_should_translate_user_short_ru_text_then_longer_ru_text` | `tests/test_user_ru_en_texts.py` | passed |
