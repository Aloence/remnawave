## Запуск проекта
Создать .env по примеру

Добавить в hosts 127.0.0.1 remnawave.local
```bash
docker compose -f remnawave/compose.yaml up -d && \
docker compose -f caddy/compose.yaml up -d && \
docker compose -f compose.yaml up -d
```
--- 
## Возвращаемые сущности

В некоторых эндпоинтах не уверен, что надо возвращать, а еще интеграция с внешним API тоже не всегда отдавала полезные данные - в таких случаях ответ 204 No Content

---

## DELETE /clients/{id} — поведение

**DELETE /clients/{id}** выполняет полное удаление пользователя в RemnaWave (`DELETE /api/users/{uuid}`): клиент и подписка удаляются, восстановление невозможно.

Альтернатива - **POST /clients/{id}/block** (деактивация в RemnaWave).

---

## Формат GET /clients/{id}/config
Ответ от RemnaWave `GET /api/subscriptions/by-uuid/{client_id}`:
```python
class SubInfoUserSchema(BaseSchemaModel):
    short_uuid: str
    username: str
    expires_at: datetime
    is_active: bool
    user_status: ClientStatus
    traffic_used: str
    traffic_limit: str

class ConfigSchema(BaseSchemaModel):
    is_found: bool
    user: SubInfoUserSchema
    links: list[str]
    ss_conf_links: dict[str, str]
    subscription_url: str
```

---

## Аудит операций
**GET /operations?clientId=...** — список операций по клиенту (пагинация: `limit`, `page`).

`src.utils.operation_logging`: пишет запись в таблицу `operations`, если при запросе указаны`log_request, client_id`

Пример:

```python
await rw_request(
    Method.POST,
    f"/api/users/{client_id}/actions/disable",
    None,
    
    #log operation
    log_request=True,
    client_id=client_id,
    
    has_response=False,
    client=self.client,
)
```


