<?php

$servername = "localhost";
$dbname = "icpkjhat_NodeImages";
$username = "icpkjhat_test";
$password = "TalkingToPlantsTeam3";

$NodeID = "";
$RunNumber = "";
$ImageNumber = "";
$SegmentNumber = "";
$ImageData = "";


$api_key = "";
$api_key_value = "CvcCKjGnBYAQoEAWtNGb6BFAdsWATKZwdNip8LVunjdsbQro1VDpVHnwXZAs8Sog";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    
    $api_key = $_POST["api_key"];
    
    if($api_key == $api_key_value) {
        
        $NodeID = $_POST["NodeID"];
        $RunNumber = $_POST["RunNumber"];
        $ImageNumber = $_POST["ImageNumber"];
        $SegmentNumber = $_POST["SegmentNumber"];
        $TotalSegmentNumber = $_POST["TotalSegmentNumber"];
        $ImageData = $_POST["Data"];
        
        // Create connection
        $conn = new mysqli($servername, $username, $password, $dbname);
        // Check connection
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }
        
        // ------------- CLEAR INPUT BUFFER -------------
        
        if($SegmentNumber == '0') {
            $sql = "TRUNCATE TABLE InputBuffer";
            $conn->query($sql);
        } 
        
        // ------------- INSERT DATA -------------
        
        $sql = "INSERT INTO InputBuffer (NodeID, RunNumber, ImageNumber, SegmentNumber, TotalSegmentNumber, Data) VALUES ('" . $NodeID . "', '" . $RunNumber . "', '" . $ImageNumber . "', '" . $SegmentNumber . "','" . $TotalSegmentNumber . "' ,'" . $ImageData . "')";
        
        if ($conn->query($sql) === TRUE) {
            echo "Image Data Received, " . $ImageData; 
        } 
        else {
            echo "Error: " . $sql . "<br>" . $conn->error;
        }
    
        // ------------- RUN CONCATENATION -------------
        // Change to run off of no. of rows rather than segment no.
    
        if ($TotalSegmentNumber == ($SegmentNumber + 1)) {
            include 'Concatenation.php';
        }
    
        $conn->close();
    }

}
else {
    	echo "No data posted with HTTP POST.";
}

?>