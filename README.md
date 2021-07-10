# Xsolla School 2021. Backend

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

## OpenAPI

Посмотреть API можно по ссылке: https://app.swaggerhub.com/apis/k0per/Xsolla/0.2.2