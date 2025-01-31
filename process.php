<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

use PHPMailer\PHPMailer\PHPMailer;

$host = 'localhost';
$username = 'u865696452_doubleoptin';
$password = '9Ahxdh=[';
$database = 'u865696452_finaldoubleopt';

// Create a connection to the database
$conn = new mysqli($host, $username, $password, $database);

// Check the connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to generate a unique token
function generateToken() {
    return bin2hex(random_bytes(16));
}

// Function to send a confirmation email using PHPMailer
function sendConfirmationEmail($email, $filename, $pdfPath,$content1,$content2,$btnOpenPdf) {
    require 'PHPMailer/Exception.php';
    require 'PHPMailer/PHPMailer.php';
    require 'PHPMailer/SMTP.php';

    $mail = new PHPMailer(true);

    try {
        // Server settings
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com';  // Replace with your SMTP server
        $mail->SMTPAuth = true;
        $mail->Username = 'lucy.smith@ittech-news.com'; // Replace with your SMTP username
        $mail->Password = 'vmxazdvtlnrrrvkm'; // Replace with your SMTP password
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; // Set the encryption method
        $mail->Port = 587; // Set the SMTP port

        // Recipients
        $mail->setFrom('lucy.smith@ittech-news.com');
        $mail->addAddress($email);

        // Content
        $mail->isHTML(true);
        $mail->CharSet = 'UTF-8';
        $mail->Subject = 'ittech-news.com';
        $mail->Body = $mail->Body = "<!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>Download PDF Button</title>
        </head>
        <body>
        
            <div style='text-align: center;'> 
                <p>$content1</p>
                <a name='click' style='display: inline-block; padding: 10px 20px; font-size: 16px; text-align: center; text-decoration: none; border: 2px solid #3498db; color: #3498db; border-radius: 5px; transition: background-color 0.3s; background-color: #fff;' href='https://ittech-news.com/landing_pages/Servicenow08112024/process.php?token=".$filename."' onclick='handleClick();' >".$btnOpenPdf."</a>
                <p>$content2</p>
            </div>
            <script>
function handleClick() {
    // Your click event handling code goes here

    // For example, you can log a message
    console.log('Link clicked!');

    // Prevent the default behavior (e.g., navigating to a new page)
    return false;
}
</script>
        </body>
        
        </html>";
        $mail->send();
        
      
    } catch (Exception $e) {
        echo "Message could not be sent. Mailer Error: {$mail->ErrorInfo}";
    }
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the submitted email
    if (!isset($_POST['email'])) {
        echo 'Email parameter is missing.';
        exit();
    }
    $pdfPath = $_POST['pdfValue'];
    $checkCountry = array('Switzerland','Germany','Austria','Greece','Luxembourg','Norway');
    $email = $conn->real_escape_string($_POST['email']);
    $token = generateToken();
    $filename = $token; // Set $filename to the generated token

    $firstName = $conn->real_escape_string($_POST['FirstName']);
    $lastName = $conn->real_escape_string($_POST['LastName']);
    $phone = $conn->real_escape_string($_POST['Phone']);
    $company = $conn->real_escape_string($_POST['Company']);
    $title = $conn->real_escape_string($_POST['Title']);
    $country = $conn->real_escape_string($_POST['Country']);
    $state = $conn->real_escape_string($_POST['State']);
    $address = $conn->real_escape_string($_POST['Address']);
    $zipcode = $conn->real_escape_string($_POST['ZipCode']);
    $fileUrl = $conn->real_escape_string($pdfPath);
  

    $privacy = "No";
    if(isset($_POST['privacy'])){
        $privacy = "Yes";
    }
    $germanCountry = array('Germany','Austria','Switzerland');

    $content1 = 'Thank you for downloading the asset and for your interest in receiving ServiceNow updates! Click on the link below to confirm that you want to receive communication from ServiceNow.';
    $content2 = 'If you are not interested in receiving email updates from ServiceNow, or you are not sure why you received this email, you can disregard it. You will only receive marketing communications from ServiceNow if you click the above link.';
    $btnOpenPdf = 'Confirm opt-in';

    if(in_array($_POST['Country'],$germanCountry)){
        $content1 = 'Vielen Dank, dass Sie das Asset heruntergeladen und Interesse an ServiceNow-Updates haben. Klicken Sie auf den Link unten, um zu bestätigen, dass Sie E-Mails von ServiceNow erhalten möchten.';
        $content2 = 'Falls Sie kein Interesse an E-Mail-Updates von ServiceNow haben, oder nicht sicher sind, warum Sie diese E-Mail erhalten haben, können Sie sie ignorieren. Sie erhalten nur Marketing-E-Mails von ServiceNow, wenn Sie auf den Link oben klicken.';
        $btnOpenPdf = 'Anmeldungsbestätigung';
    }
    
     // Create a new DateTime object
     $date = new DateTime();
    // Set the time zone to UTC
     $date->setTimezone(new DateTimeZone('UTC'));
     // Format the date and time (optional)
     $utcDateTime = $date->format('Y-m-d H:i:s');

    // Store user data in the database
    $sql = "INSERT INTO doubleoptin1 (`FirstName`, `LastName`, `email`, `Phone`, `Company`, `Title`, `Country`, `State`, `Address`, `ZipCode`,`fileUrl`,`privacy`, `filename`,`createdAt`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?)";
    $stmt = $conn->prepare($sql);

   if ($stmt) {
        $stmt->bind_param("ssssssssssssss", $firstName,$lastName,$email,$phone,$company,$title,$country,$state,$address,$zipcode,$fileUrl,$privacy, $filename,$utcDateTime); // Use "ss" for two string parameters
        $stmt->execute();

        if ($stmt->affected_rows > 0) {
            // Send confirmation email
            if(in_array($_POST['Country'],$checkCountry) && isset($_POST['privacy'])){
                sendConfirmationEmail($email, $filename, $pdfPath,$content1,$content2,$btnOpenPdf);
            } 
        
            $pdfFile = "original%20(1).pdf"; // You should replace this with the actual PDF file path
            header("Location: ".$_POST['pdfValue']);
            readfile($pdfFile);
            exit();
        } else {
            echo "Error: " . $stmt->error;
        }

        $stmt->close();
    } else {
        echo 'Error: ' . $conn->error;
    }

    $conn->close();
    exit();
} else {
    echo "Invalid request.";
}

// Handle form Mail get
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // Get the submitted email
    if (!isset($_GET['token'])) {
        echo 'Token parameter is missing.';
        exit();
    }
   
    $token = $conn->real_escape_string($_GET['token']);
    
     // Create a new DateTime object
     $date = new DateTime();
    // Set the time zone to UTC
     $date->setTimezone(new DateTimeZone('UTC'));
     // Format the date and time (optional)
     $utcDateTime = $date->format('Y-m-d H:i:s');

    // Store user data in the database
    $selectSql = "SELECT * FROM doubleoptin1 WHERE `filename` = ?";
    $selectStmt = $conn->prepare($selectSql);

   if ($selectStmt) {
        $selectStmt->bind_param("s", $token); // Use "ss" for two string parameters
        $selectStmt->execute();

        $result = $selectStmt->get_result();
        if ($result->num_rows > 0) {
            // Fetch the data
            while ($row = $result->fetch_assoc()) {
                // Process the data as needed
                $updateSql = "UPDATE doubleoptin1 SET mailpdf=? WHERE `filename`=?";
                $updateStmt = $conn->prepare($updateSql);
                // $headerurl =$row['fileUrl'];
                $headerurl = 'https://ittech-news.com/';
                if ($updateStmt) {
                    $updateStmt->bind_param("ss", $utcDateTime, $token); // Use "s" for a string parameter
                    $updateStmt->execute();
                    
                    if ($updateStmt->affected_rows > 0) {
                        // echo "Record updated successfully.";
                        header("Location: ".$headerurl);
                    } else {
                        echo "No records updated.";
                    }
                
                    $updateStmt->close();
                } else {
                    echo 'Error: ' . $conn->error;
                }
                // header("Location: ".$row['fileUrl']);
                header("Location: ".$headerurl);
                exit();
            }
        } else {
            echo "Error: " . $selectStmt->error;
        }

        $selectStmt->close();
    } else {
        echo 'Error: ' . $conn->error;
    }

    $conn->close();
    exit();
} else {
    echo "Invalid request.";
}

// Close the database connection
mysqli_close($conn);