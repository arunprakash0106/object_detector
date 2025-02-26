<?php
include 'config.php';

$sql = "SELECT * FROM detections ORDER BY timestamp DESC";
$result = $conn->query($sql);

echo "<h2>Object Detection Data</h2>";
echo "<table border='1'><tr><th>ID</th><th>Timestamp</th><th>Event</th><th>Object</th><th>Detected Count</th><th>Total Bottle</th><th>Total Notebook</th></tr>";

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        echo "<tr>
                <td>{$row['id']}</td>
                <td>{$row['timestamp']}</td>
                <td>{$row['event']}</td>
                <td>{$row['object']}</td>
                <td>{$row['detected_count']}</td>
                <td>{$row['total_bottle']}</td>
                <td>{$row['total_notebook']}</td>
              </tr>";
    }
} else {
    echo "<tr><td colspan='7'>No data available</td></tr>";
}

echo "</table>";
$conn->close();
?>
