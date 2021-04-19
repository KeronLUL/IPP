<?php
    $testDir = "./";
	$parsePath = "./parse.php";
	$interpretPath = "./interpret.py";
	$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
    $jexamcfg = "/pub/courses/ipp/jexamxml/options";
    $recursive = false;
    $parseOnly = false;
    $intOnly = false;

    # Function that prints error and exits the program with value given by $val
    function errorExit($val, $string){
        print($string);
        exit($val);
    }

    # Argument check
    function argCheck(){
        global $testDir, $parsePath, $interpretPath, $jexamxml, 
                $jexamcfg, $recursive, $parseOnly, $intOnly, $argc;

        $number = $argc;
        $options = array("help", "directory:", "recursive", "parse-script:", "int-script:",
                            "parse-only", "int-only", "jexamxml:", "jexamcfg:");
        $usedOptions = getopt(null, $options);

        if($number == 1){
            errorExit(10, "Invalid arguments\n");
        }
        if(isset($usedOptions["help"])){
            if($argc == 2){
                print("Testing of parse.php and interpret.py\n");
                exit(0);
            }
            else errorExit(10, "Invalid arguments\n");
        }
        if(isset($usedOptions["directory"])){
            $testDir = $usedOptions["directory"];
            if(substr($testDir, -1) != "/"){
                $testDir = $testDir."/";
            }
            $number -= 1;
        } 
        if(isset($usedOptions["recursive"])){
            $recursive = true;
            $number -= 1;
        } 
        if(isset($usedOptions["parse-script"])){
            $parsePath = $usedOptions["parse-script"];
            $number -= 1;
        }
        if(isset($usedOptions["int-script"])){
            $interpretPath = $usedOptions["int-script"];
            $number -= 1;
        }
        if(isset($usedOptions["parse-only"])){
            $parseOnly = true;
            $number -= 1;
        }
        if(isset($usedOptions["int-only"])){
            $intOnly = true;
            $number -= 1;
        }
        if(isset($usedOptions["jexamxml"])){
            $jexamxml = $usedOptions["jexamxml"];
            $number -= 1;
        }
        if(isset($usedOptions["jexamcfg"])){
            $jexamcfg = $usedOptions["jexamcfg"];
            $number -= 1;
        }
        if($parseOnly){
            if ($intOnly || isset($usedOptions["int-script"])){
                errorExit(10, "Invalid arguments\n");
            }
        }
        if($intOnly){
            if ($parseOnly || isset($usedOptions["parse-script"])){
                errorExit(10, "Invalid arguments\n");
            }
        }
        if($number != 1){
            errorExit(10, "Invalid arguments\n");
        }
    }

    # Run test and compare return codes and output
    function runTests($src){
        global $parsePath, $interpretPath, $jexamxml, $jexamcfg, $parseOnly,
                $intOnly, $testPassedCount, $testFailedCount, $arrays;
       
        $path = str_replace(".src", "", $src);
        $name = explode("/", $path);
        $name = end($name);

        $inFile = $path . ".in";
        $outFile = $path . ".out";
        $rcFile = $path . ".rc";
        
        # Check if files exists, if not create them
        $array = [".in", ".out", ".rc"];
        $rc = 0;
        for ($i = 0; $i < 3; $i++){
            if (!file_exists($path . $array[$i])){
                try{
                    $file = fopen($path . $array[$i], "w");
                } catch ( Exception $e ){
                    errorExit(11, "Couldn't open file\n");
                }
                if ($array[$i] == ".rc"){
                    $rc = 0;
                    fwrite($file, $rc);
                }
                fclose($file);
            }else if ($array[$i] == ".rc"){
                try{
                    $file = fopen($rcFile, "r");
                } catch ( Exception $e ){
                    errorExit(11, "Couldn't open file\n");
                }
                $rc = intval(fread($file, filesize($rcFile)));
                fclose($file);
            }
        }
        
        # Execute parse.php if interpret-only argument is not set
        if (!$intOnly){
            exec("php7.4 " . $parsePath . " < " . $src, $parseOut, $parseRc);
            $parseOut = shell_exec("php7.4 " . $parsePath . " < " . $src);
            if ($parseRc != 0){
                if ($parseRc != $rc){
                    $testFailedCount++;
                    array_push($arrays, $path, "Failed");
                    return;
                }else {
                    $testPassedCount++;
                    array_push($arrays, $path, "Success");
                    return;
                }
            }
            try{
                $file = fopen($path . ".tmp", "w");
            } catch ( Exception $e ){
                errorExit(11, "Couldn't open file\n");
            }
            fwrite($file, $parseOut);
        
        
            # If argument parse-only is set compare output with jexamxml
            if ($parseOnly){
                if ($rc != $parseRc){
                    $testFailedCount++;
                    array_push($arrays, $path, "Failed");
                    return;
                }
                if ($parseRc == 0){
                    exec("java -jar " . $jexamxml ." ". $path .".tmp " . $outFile ." ". $path."delta.xml ". $jexamcfg, $trash, $xmlDiff);
                    unlink($path ."delta.xml");

                    if (!$xmlDiff){
                        $testPassedCount++;
                        array_push($arrays, $path, "Success");
                    }else {
                        $testFailedCount++;
                        array_push($arrays, $path, "Failed");
                    }
                    unlink($path .".tmp");
                    return;
                }
                $testPassedCount++;
                array_push($arrays, $path, "Success");
                return;
            }
        }
      
        # Choose which source file to give to interpret depending on set arguments
        if (!$intOnly){
            exec("python3.8 " . $interpretPath . " --source=". $path . ".tmp" . " --input=" . $inFile, $intOut, $intRC);
            $intOut = shell_exec("python3.8 " . $interpretPath . " --source=". $path . ".tmp" . " --input=" . $inFile);
            unlink($path .".tmp");
        }else {
            exec("python3.8 " . $interpretPath . " --source=" . $path.".src" . " --input=" . $inFile, $intOut, $intRC);
            $intOut = shell_exec("python3.8 " . $interpretPath . " --source=" . $path.".src" . " --input=" . $inFile);
        }
        
        if ($intRC != $rc){
            $testFailedCount++;
            array_push($arrays, $path, "Failed");
            return;
        }

        # Compare output of interpret with diff
        if ($intRC == 0){
            try{
                $file = fopen($path .".tmp", "w");
            } catch ( Exception $e ){
                errorExit(11, "Couldn't open file\n");
            }
            fwrite($file, $intOut);
            
            exec("diff ".$path .".tmp" ." ". $outFile, $output, $retcode);
            unlink($path .".tmp");
            if ($retcode == 0){
                $testPassedCount++;
                array_push($arrays, $path, "Success");
                return;
            }else{
                $testFailedCount++;
                array_push($arrays, $path, "Failed");
                return;
            }
        }else {
            $testPassedCount++;
            array_push($arrays, $path, "Success");
            return;
        }
        
    }

    argCheck();
    # Check if files exists
    $fileArray = [$jexamcfg, $jexamxml, $parsePath, $interpretPath];
    for ($i = 0; $i < 4; $i++){
        if (!file_exists($fileArray[$i])){
            errorExit(11, "File doesn't exists\n");
        }
    }
    if (!is_dir($testDir)){
        errorExit(11, "Directory doesn't exists\n");
    }

    # Find every test ending with .src
    if ($recursive) {
        exec("find " . $testDir . " -regex '.*\.src$'", $testPaths);
    }else exec("find " . $testDir . " -maxdepth 1 -regex '.*\.src$'", $testPaths);
    
    $testCount = 0;
    $testPassedCount = 0;
    $testFailedCount = 0;
    $arrays = [];
    foreach ($testPaths as $src) {   
        $testCount++;
        runTests($src);   
    }

    # Generating HTML
    $html = "<!DOCTYPE html>
    <html>
    <head>
        <title>IPP 2021 Výsledky testů</title>
        <meta charset='utf-8' />
        <style>
            * {
                margin: 0;
                padding: 0
            }
    
            html {
                background: whitesmoke;
            }
    
            body {
                font-family: 'Segoe UI', Arial, 'Noto Sans', sans-serif;
            }
    
            .summary-container {
                display: flex;
                justify-content: center;
                width: 100%;
                padding-top: 20px
            }
    
            .summary-table {
                width: 400px;
                height: 200px;
                box-shadow: 10px 10px 50px -20px  rgba(0, 0, 0, 0.4);
                border-radius: 15px;
            }
    
            .summary-header {
                text-align: center;
                padding-top: 20px;
            }
    
            .test-summary {
                display: flex;
                align-items: center;
                height: 125px;
                padding: 20px;
                padding-left: 100px;
                padding-top: 5px;
                font-size: 20px;
                font-weight: 400;
                width: 100%;
            }
    
            .test-number{
                padding-left: 60px;
            }
    
            .table-results {
                margin-left: auto;
                margin-right: auto;
                padding-top: 20px;
                width: 60%;
            }
    
            .table-results-container {
                box-shadow: 10px 10px 50px -20px rgba(0, 0, 0, 0.4);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
    
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }
    
            .test-result {
                display: flex;
                border-bottom: 1px solid rgba(81, 85, 90, 0.1);
                padding: 10px;
                align-items: center;
            }
    
            .test-result-order {
                font-size: 25px;
                width: 32px;
                height: 32px;
                font-weight: bold;
                display: flex;
                justify-content: center;
                align-items: center;
                margin-right: 25px;
                margin-left: 25px;
            }
    
            .test-result-columns {
                display: flex;
                width: 100%;
                align-items: center;
            }
    
            .test-result-columns div {
                padding: 0px 5px;
            }
    
            .test-result-columns div:first-child {
                width: 100%;
            }
    
            .test-result-columns table {
                width: 70%;
            }
    
            .test-result-columns table tr th {
                text-align: left;
            }
    
            .test-result-failed {
                color: #cf2900;
                padding-right: 20px;
            }
    
            .test-result-passed {
                color: #02ba1e;
                padding-right: 20px;
            }
    
            .test-dir{
                width: 150px;
            }
            
        </style>
    </head>
    
    <body>
        <section class='summary-container'>
            <div class='summary-table'>
                <h1 class='summary-header'>Výsledky testů</h1>
                <div class='test-summary'>
                    <table>
                        <tr>
                            <td>Úspěšných:</td>
                            <td class = 'test-number'>";
    $html = $html . $testPassedCount;
    $html = $html . "</td>
    </tr>
    <tr>
        <td>Neúspěšných:</td>
        <td class = 'test-number'>";
    $html = $html . $testFailedCount;
    $html = $html . "</td>
    </tr>
    <tr>
        <td>Celkem:</td>
        <td class = 'test-number'>";
    $html = $html . $testCount;
    $html = $html . "</td>
    </tr>
</table>
</div>
</div>
</section>

<section class='table-results'>
<div class='table-results-container'>";

    for($i = 0; $i < count($arrays); $i += 2){
        $html = $html . "<div class='test-result'>
        <div class='test-result-order'>";
        $html = $html . ($i/2+1);
        $html = $html . "</div>
        <div class='test-result-columns'>
            <div class='test-result-data'>
                <table>
                    <tr>
                        <th class = 'test-dir'>Složka:</th>
                        <td>";
        $html = $html . $arrays[$i];
        $html = $html . "</td>
        </tr>
        <tr>
            <th>Název testu:</th>
            <td>";
        $name = explode("/", $arrays[$i]);
        $name = end($name);
        $html = $html . $name;
        $html = $html . "</td>
        </tr>
    </table>
</div>";
        
        if ($arrays[$i+1] == "Success"){
            $html = $html . "<h2 class='test-result-passed'>Úspěch</h2>
            </div>
        </div>";
        }else {
            $html = $html . "<h2 class='test-result-failed'>Selhalo</h2>
            </div>
        </div>";
        }
    }
    $html = $html . "</div>
    </section>
</body>
</html>";
    
    echo $html;
    exit(0);
?>