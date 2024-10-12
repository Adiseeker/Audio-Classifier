<?php
header('Content-Type: application/json');

// Connect to SQLite database
$db = new SQLite3('audycje.db');

// Retrieve the search term from the query parameter
$searchTerm = isset($_GET['q']) ? $_GET['q'] : '';

// Prepare and execute the query
$stmt = $db->prepare('
    SELECT * FROM audycje
    WHERE filename LIKE :search OR content LIKE :search OR keyphrases_spacy LIKE :search OR keyphrases_rake LIKE :search
');
$searchTermWildcard = '%' . $searchTerm . '%';
$stmt->bindValue(':search', $searchTermWildcard, SQLITE3_TEXT);
$result = $stmt->execute();

// Fetch results
$results = [];
while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
    $results[] = $row;
}

// Return results as JSON
echo json_encode($results);
?>
