# Xsolla School 2021. Backend

Есть возможность протестировать API на удаленном общем сервере: http://xsolla.jelastic.regruhosting.ru/

Докер сразу поддерживает SSL протокол, но требуется отключать верификацию SSL при запросе. 

## Установка

### Рекомендуемый способ

```shell
$ sudo docker pull k0per/xsolla-school-backend-2021
$ sudo docker run -v /path/to/data/dir:/var/lib/postgresql/data -p 80:80 -p 443:443 k0per/xsolla-school-backend-2021
```

### Ручная сборка образа

```shell
$ git clone https://github.com/k0perX-X/xsolla-backend-test.git
$ sudo docker build -t xsolla .
$ sudo docker run -v /path/to/data/dir:/var/lib/postgresql/data -p 80:80 -p 443:443 xsolla
```

### Установка без Docker (не рекомендуется)

1. Установить PostgreSQL (можно на удаленный сервер).

2. ```shell 
   $ git clone https://github.com/k0perX-X/xsolla-backend-test.git
   ```

3. Ввести настройки PostgreSQL в settings.ini:
   ```
   dbname=goods   - имя базы данных
   user=postgres  - имя пользователя для подключения к базе
   password=      - пароль пользователя
   host=localhost - хост сервера
   ```
   Желательно также указать свой `log_file_path`.

4. ```shell 
   $ python3 app.py
   ```

## OpenAPI

Посмотреть API можно по ссылке: https://app.swaggerhub.com/apis-docs/k0per/Xsolla/