# xsolla-backend-test

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


