<?php
    function preserve_qs() {
        if (empty($_SERVER['QUERY_STRING']) && strpos($_SERVER['REQUEST_URI'], "?") === false) {
            return "";
        }
        return "?" . $_SERVER['QUERY_STRING'];
    }

    header("Location: /app/signup/" . preserve_qs());
    die();
?>
