# Документоскоп — API

## /api/upload/ [POST]

**Описание:**  
Загрузка файла для анализа.

**Параметры:**  
- file: UploadFile (pdf/docx/jpg/png)

**Ответ:**  
```json
{
  "task_id": "uuid",
  "status": "processing"
}
