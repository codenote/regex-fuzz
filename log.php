<?php
/**
 * Basic logger for fuzzer
 */

$data = $_GET['req'];
$hash = md5($_SERVER['HTTP_USER_AGENT']);
file_put_contents(
    "logs/$hash-log.txt",
    $_SERVER['HTTP_USER_AGENT'] . PHP_EOL . $data
);
