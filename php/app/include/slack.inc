<?php
    function post($url, $params)
    {
        $curl = curl_init($url);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_POST, true);
        curl_setopt($curl, CURLOPT_POSTFIELDS, $params);
        $json_response = curl_exec($curl);
        return $json_response;
    }
    function sendSlackMessage($url, $text)
    {
        $message = array("text" => $text, "link_names" => "1");
        return post($url, "payload=" . json_encode($message));
    }
?>
