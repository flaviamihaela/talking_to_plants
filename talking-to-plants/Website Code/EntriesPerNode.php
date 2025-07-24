<html>
<head>
    <title> Node Info </title>
    <style>
        body{
            background-color: rgb(191, 173, 230);
        }
        </style>
</head>

<?php
//connect to database
$user2 = 'icpkjhat_website';
$pass2 = 'TalkingToPlantsTeam3';
$db2 = 'icpkjhat_NodeImages';

$conn = mysqli_connect('localhost', $user2, $pass2, $db2);

if (!$conn){
    echo "Error - Could not Connect";
}
else { 
    echo "Connected to Database Successfully";
    echo "<br></br>";
} 

?>

<body>
    <centre>
     
            <table width="100%" border="1" cellpadding="20">
                <thead>
                    <tr>
                        <th> Node Number </th>
                        <th> Total Runs </th>
</tr>
</thead>


<?php

$sql = "SELECT a.Node, a.RunNumber
  FROM (SELECT Node, RunNumber,
               ROW_NUMBER() OVER (PARTITION BY Node ORDER BY RunNumber DESC) ranked_order
          FROM WebsiteTest) a
 WHERE a.ranked_order = 1 ";
    

//make query and get result
$result = mysqli_query($conn, $sql);

while($row = mysqli_fetch_array($result))
{
    ?>
    <tr>
        <td style ="text-align: center;"> <?php echo $row['Node']   ?></td>
        <td style ="text-align: center;"> <?php echo $row['RunNumber']   ?></td>
</tr>
<?php
}

?>
</table>
</centre>

</body>