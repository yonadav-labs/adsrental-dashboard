<?php

    function GenerateRandomHexString($length)
    {
    	$decimalToHex = array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f");
        $result = "";
        
        for ($i = 0; $i < $length; $i++)
        {
            $randomIndex = mt_rand(0, 15);
            
            $result .= $decimalToHex[$randomIndex];
        }
        
        return $result;
    }

?>
