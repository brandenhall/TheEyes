<?php
header('Content-disposition: attachment; filename=' . $_REQUEST["filename"]);
header('Content-type: application/json');
echo $_REQUEST["json"];
?>
