# Карта покрытия автотестов TranslateText

Поверхность: desktop (CustomTkinter). Раннер: pytest. Прогон — команда `/use-tests`.

Макет UI без пайплайна перевода: покрыты подписи, стартовое состояние и Must-блокировки, которые можно наблюдать на виджетах. Живой Ollama, диалоги файлов и очередь фрагментов в набор не входят.

| Тест | Файл | Требования | Слой | Состояние UI | Примечание |
| --- | --- | --- | --- | --- | --- |
| `test_should_show_all_glossary_labels_when_window_opens` | `tests/test_main_screen.py` | NFT-006 | happy | — | 8 подписей глоссария |
| `test_should_show_original_text_field_when_window_opens` | `tests/test_main_screen.py` | FT-001 | happy | — | поле есть |
| `test_should_show_translation_field_when_window_opens` | `tests/test_main_screen.py` | FT-002 | happy | — | поле есть |
| `test_should_show_custom_instruction_field_when_window_opens` | `tests/test_main_screen.py` | FT-007 | happy | — | поле есть |
| `test_should_show_base_prompt_when_user_has_not_replaced_instruction` | `tests/test_main_screen.py` | FT-008; US-005 AC1 | happy | — | текст из глоссария |
| `test_should_show_model_list_when_window_opens` | `tests/test_main_screen.py` | FT-005 | happy | — | виджет списка; не опрос API |
| `test_should_show_autosave_control_when_window_opens` | `tests/test_main_screen.py` | FT-032 | happy | — | |
| `test_should_enable_autosave_when_window_opens` | `tests/test_main_screen.py` | FT-033; US-006 AC1 | happy | — | включена при старте |
| `test_should_show_progress_indicator_at_zero_when_window_opens` | `tests/test_main_screen.py` | FT-022 | empty | empty | 0 % до запуска перевода |
| `test_should_disable_translate_when_original_is_empty` | `tests/test_blocking.py` | FT-026; US-001 AC4 | negative | disabled | правило в макете не реализовано |
| `test_should_disable_save_when_translation_is_empty` | `tests/test_blocking.py` | FT-027; US-003 AC3 | negative | disabled | правило в макете не реализовано |
| `test_should_keep_autosave_enabled_when_translation_is_empty` | `tests/test_blocking.py` | FT-027; US-003 AC3 | edge | — | пустой перевод не блокирует галочку |
| `test_should_disable_translate_when_model_list_is_empty` | `tests/test_blocking.py` | FT-048; US-001 AC4 | negative | disabled | пустой список виджета; шва API нет |
| `test_should_keep_model_list_enabled_when_model_list_is_empty` | `tests/test_blocking.py` | FT-049; US-007 AC1 | happy | — | список остаётся доступным |
| `test_should_show_no_text_hint_when_pointer_hovers_blocked_translate` | `tests/test_blocking.py` | FT-050; US-008 AC1 | negative | disabled | подсказка в макете не реализована |
