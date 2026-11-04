-- Local development/test privileges only. Executed on first volume initialization.
CREATE DATABASE IF NOT EXISTS test_littlelemon CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON test_littlelemon.* TO 'littlelemon'@'%';
