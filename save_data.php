<?php
include 'config.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $timestamp = $_POST['timestamp'];
    $event = $_POST['event'];
    $object = $_POST['object'];
    $detected_count = $_POST['detected_count'];
    $total_bottle = $_POST['total_bottle'];
    $total_notebook = $_POST['total_notebook'];

    $sql = "INSERT INTO detections (timestamp, event, object, detected_count, total_bottle, total_notebook)
            VALUES ('$timestamp', '$event', '$object', '$detected_count', '$total_bottle', '$total_notebook')";

    if ($conn->query($sql) === TRUE) {
        echo "Success: Data inserted";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
}
$conn->close();
?>
