# Настройки документов

Архитектура настроек для работы с документами построена по принципу разделения общих и специфичных параметров.

## Структура настроек

### CommonDocumentSettings (common.py)
Общие параметры для всех операций с документами:

- **max_document_size_mb**: Максимальный размер документа (200 МБ по умолчанию)
- **preferred_head_size**: Размер буфера для чтения заголовка (16 КБ по умолчанию)
- **default_timeout_seconds**: Базовый таймаут для операций (60 сек по умолчанию)
- **temp_base_dir**: Базовая директория для временных файлов
- **cleanup_interval_seconds**: Интервал очистки временных файлов (1 час по умолчанию)
- **max_concurrent_operations**: Лимит параллельных операций (10 по умолчанию)
- **buffer_size_bytes**: Размер буфера для I/O операций (8 КБ по умолчанию)
- **enable_metrics**: Включение сбора метрик (true по умолчанию)
- **quality_threshold**: Порог качества операций (0.7 по умолчанию)

### MagicDetectorSettings (detection/magic_detector.py)
Специфичные настройки Magic детектора:

- **use_libmagic**: Использование системной libmagic (true по умолчанию)
- **confidence_threshold**: Минимальный порог уверенности (0.7 по умолчанию)
- **mime_conflict_penalty**: Штраф за конфликт MIME (0.2 по умолчанию)
- **ooxml_confidence_cap**: Максимальная уверенность для OOXML (0.85 по умолчанию)
- **ole_confidence_cap**: Максимальная уверенность для OLE (0.8 по умолчанию)
- **scan_limit_multiplier**: Множитель лимита сканирования (4.0 по умолчанию)
- **enable_signature_cache**: Включение кеша сигнатур (true по умолчанию)
- **signature_cache_size**: Размер кеша сигнатур (1000 по умолчанию)

### LibreOfficeConverterSettings (conversion/libreoffice_converter.py)
Специфичные настройки LibreOffice конвертера:

- **min_processes** / **max_processes**: Размер пула процессов (2-10 по умолчанию)
- **process_idle_timeout_multiplier**: Множитель таймаута простоя (30.0 по умолчанию)
- **conversion_timeout_multiplier**: Множитель таймаута конвертации (5.0 по умолчанию)
- **libreoffice_path**: Путь к LibreOffice (автоопределение по умолчанию)
- **startup_timeout**: Таймаут запуска процесса (60 сек по умолчанию)
- **max_memory_mb**: Лимит памяти на процесс (512 МБ по умолчанию)
- **enable_headless**: Режим headless (true по умолчанию)
- **preserve_metadata**: Сохранение метаданных (true по умолчанию)
- **quality_level**: Уровень качества конвертации (8/10 по умолчанию)
- **enable_process_recycling**: Переработка процессов (true по умолчанию)
- **max_operations_per_process**: Операций на процесс (100 по умолчанию)
- **enable_conversion_cache**: Кеширование результатов (false по умолчанию)


### Общие настройки
```bash
DOCUMENTS_MAX_SIZE_MB=200
DOCUMENTS_PREFERRED_HEAD_SIZE=16384
DOCUMENTS_DEFAULT_TIMEOUT=60.0
DOCUMENTS_TEMP_BASE_DIR=/tmp/documents
DOCUMENTS_ENABLE_CLEANUP=true
DOCUMENTS_CLEANUP_INTERVAL=3600
DOCUMENTS_MAX_CONCURRENT_OPERATIONS=10
DOCUMENTS_BUFFER_SIZE=8192
DOCUMENTS_ENABLE_METRICS=true
DOCUMENTS_QUALITY_THRESHOLD=0.7
```

### Детектор
```bash
DETECTOR_MAGIC_USE_LIBMAGIC=true
DETECTOR_MAGIC_CONFIDENCE_THRESHOLD=0.7
DETECTOR_MAGIC_MIME_CONFLICT_PENALTY=0.2
DETECTOR_MAGIC_OOXML_CONFIDENCE_CAP=0.85
DETECTOR_MAGIC_OLE_CONFIDENCE_CAP=0.8
DETECTOR_MAGIC_SCAN_LIMIT_MULTIPLIER=4.0
DETECTOR_MAGIC_ENABLE_SIGNATURE_CACHE=true
DETECTOR_MAGIC_SIGNATURE_CACHE_SIZE=1000
```

### Конвертер
```bash
CONVERTER_LIBREOFFICE_MIN_PROCESSES=2
CONVERTER_LIBREOFFICE_MAX_PROCESSES=10
CONVERTER_LIBREOFFICE_PROCESS_IDLE_TIMEOUT_MULTIPLIER=30.0
CONVERTER_LIBREOFFICE_CONVERSION_TIMEOUT_MULTIPLIER=5.0
CONVERTER_LIBREOFFICE_PATH=/usr/bin/libreoffice
CONVERTER_LIBREOFFICE_STARTUP_TIMEOUT=60
CONVERTER_LIBREOFFICE_MAX_MEMORY_MB=512
CONVERTER_LIBREOFFICE_ENABLE_HEADLESS=true
CONVERTER_LIBREOFFICE_PRESERVE_METADATA=true
CONVERTER_LIBREOFFICE_QUALITY_LEVEL=8
CONVERTER_LIBREOFFICE_ENABLE_PROCESS_RECYCLING=true
CONVERTER_LIBREOFFICE_MAX_OPERATIONS_PER_PROCESS=100
CONVERTER_LIBREOFFICE_ENABLE_CONVERSION_CACHE=false
```
