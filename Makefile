sql:
	./cloud_sql_proxy -instances=jphacks-2019-nfc:asia-northeast1:ng19102=tcp:3306
login:
	mysql -u root -p --host 127.0.0.1 --port 3306