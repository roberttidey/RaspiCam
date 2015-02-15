<!DOCTYPE html>
<?php
  define('BASE_DIR', dirname(__FILE__));
  require_once(BASE_DIR.'/config.php');
  
  //Search for matching thumb files within 4 seconds back
   function getThumb($vFile, $makeit) {
      $fType = substr($vFile,0,5);
      $fDate = substr($vFile,11,8);
      $fTime = substr($vFile,20,8);
      if ($fType == 'video') {
         for ($i = 0; $i < 4; $i++) {
            $thumb = 'vthumb_' . $fDate . '_' . sprintf('%06d', $fTime - $i) . '.jpg';
            if (file_exists("media/$thumb")) {
               return $thumb;
            }
         }
         //run command to generate video thumb
         if ($makeit) {
            $thumb = 'vthumb_' . $fDate . '_' . sprintf('%06d', $fTime) . '.jpg';
            exec("ffmpeg -i media/$vFile -vframes 1 -r 1 -s 162x122 -f image2 media/$thumb");
            return $thumb;
         }
      }
      else if ($fType == 'image') {
         $thumb = 'ithumb_' . $fDate . '_' . sprintf('%06d', $fTime - $i) . '.jpg';
         if (file_exists("media/$thumb")) {
            return $thumb;
         }
         else if ($makeit) {
            //run command for image
            exec("ffmpeg -i media/$vFile -vframes 1 -r 1 -s 162x122 -f image2 media/$thumb");
            return $thumb;
         }
      }
      return "";
   }
?>
<html>
   <head>
      <meta name="viewport" content="width=550, initial-scale=1">
      <title>RPi Cam Download</title>
      <link rel="stylesheet" href="css/style_minified.css" />
   </head>
   <body>
      <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
         <div class="container">
            <div class="navbar-header">
               <a class="navbar-brand" href="index.php"><span class="glyphicon glyphicon-chevron-left"></span>Back - <?php echo CAM_STRING; ?></a>
            </div>
         </div>
      </div>
    
      <div class="container-fluid">
      <?php
         if(isset($_GET["delete"])) {
            unlink("media/" . $_GET["delete"]);
            $tFile = getThumb($_GET["delete"], false);
            if ($tFile != "") {
               unlink("media/$tFile");
            }
         }
         if(isset($_GET["delete_all"])) {
            $files = scandir("media");
            foreach($files as $file) unlink("media/$file");
         }
         else if(isset($_GET["file"])) {
            $tFile = $_GET["file"];
            echo "<h1>Preview:  " . substr($tFile,0,10) . "</h1>";
            if(substr($tFile, -3) == "jpg") echo "<a href='media/$tFile' target='_blank'><img src='media/$tFile' width='640'></a>";
            else echo "<video width='640' controls><source src='media/$tFile' type='video/mp4'>Your browser does not support the video tag.</video>";
            echo "<p><br><input class='btn btn-primary' type='button' value='Download' onclick='window.open(\"download.php?file=$tFile\", \"_blank\");'> ";
            echo "<input class='btn btn-danger' type='button' value='Delete' onclick='window.location=\"preview.php?delete=$tFile\";'></p>";
         }
      ?>
      <h1>Files</h1>
      <?php
         $files = scandir("media");
         if(count($files) == 2) echo "<p>No videos/images saved</p>";
         else {
            echo "<table style='border-collapse:separate;border-spacing:2em 0.5em'>";
            echo "<tr><th>No:</th><th>Type</th><th>Thumb</th><th>Date</th><th>Time</th><th>MB</th><th>Del</th></tr>";
            foreach($files as $file) {
               if(($file != '.') && ($file != '..') && ((substr($file, 0, 5) == 'video') || (substr($file, 0, 5) == 'image'))) {
                  $fsz = round ((filesize("media/" . $file)) / (1024 * 1024));
                  $fType = substr($file,0,5);
                  $fNumber = substr($file,6,4);
                  $fDate = substr($file,11,8);
                  $fTime = substr($file,20,8);
                  echo "<tr>";
                  echo "<td><a href='preview.php?file=$file'>$fNumber</a></td>";
                  echo "<td><img src='" . $fType . ".png'/></td>";
                  $tFile = getThumb($file, true);
                  if ($tFile != "") {
                     echo "<td><img src='media/$tFile' style='width:64px'/></td>";
                  }
                  else { 
                     echo "<td>None</td>";
                  }
                  echo "<td>" . substr($fDate,0,4) . "-" . substr($fDate,4,2) . "-" . substr($fDate,6,2) . "</td>";
                  echo "<td>" . substr($fTime,0,2) . ":" . substr($fTime,2,2) . ":" . substr($fTime,4,2) . "</td>";
                  echo "<td>$fsz MB</td>";
                  echo "<td><input class='btn btn-danger' type='button' value='Delete' onclick='window.location=\"preview.php?delete=" . $file . "\";'></td>";
                  echo "</tr>";
               } 
            }
            echo "</table>";
            echo "<p><input class='btn btn-danger' type='button' value='Delete all' onclick='if(confirm(\"Delete all?\")) {window.location=\"preview.php?delete_all\";}'></p>";
         }
      ?>
      </div>
   </body>
</html>