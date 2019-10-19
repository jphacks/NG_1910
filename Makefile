sql:
	./cloud_sql_proxy -instances=jphacks-2019-nfc:us-central1:ng-1910=tcp:13306
login:
	mysql -u root -p --host 127.0.0.1 --port 13306