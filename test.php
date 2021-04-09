<?php
    $testDir = "./";
	$parsePath = "./parse.php";
	$interpretPath = "./interpret.py";
	$jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
    $jexamcfg = "/pub/courses/ipp/jexamxml/options";
    $recursive = false;
    $parseOnly = false;
    $intOnly = false;

    function errorExit($val, $string){
        print($string);
        exit($val);
    }

    function arg_check(){
        global $testDir;
        global $parsePath;
        global $interpretPath;
        global $jexamxml;
        global $jexamcfg;
        global $recursive;
        global $parseOnly;
        global $intOnly;
        global $argc;
        $number = $argc;
        $options = array("help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:", "jexamcfg:");
        $usedOptions = getopt(null, $options);
        
        if(isset($usedOptions["help"])){
            if($argc == 2){
                print("Testing of parse.php and interpret.py\n");
                exit(0);
            }
            else errorExit(1, "Invalid arguments\n");
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
                exit(1);
            }
        }
        if($intOnly){
            if ($parseOnly || isset($usedOptions["parse-script"])){
                exit(1);
            }
        }
        if($number != 1){
            errorExit(1, "Invalid arguments\n");
        }
    }

    function parse_test($src, $testDirPassedCount, $testCount){
        global $parsePath;
        global $interpretPath;
        global $parseOnly;
        global $intOnly;
        global $jexamxml;
        global $jexamcfg;
        global $html;
        $path = str_replace(".src", "", $src);
        $name = explode("/", $path);
        $name = end($name);


        $html = $html."<td>".$name."</td>\n";

        $inFile = $path . ".in";
        $outFile = $path . ".out";
        $rcFile = $path . ".rc";

        $array = [".in", ".out", ".rc"];
        $rc = 0;
        for ($i = 0; $i < 3; $i++){
            if (!file_exists($path . $array[$i])){
                $file = fopen($path . $array[$i], "w");
                if ($array[$i] == ".rc"){
                    $rc = 0;
                    fwrite($file, $rc);
                }
                fclose($file);
            }else if ($array[$i] == ".rc"){
                $file = fopen($rcFile, "r");
                $rc = intval(fread($file, filesize($rcFile)));
                fclose($file);
            }
        }
        
        if (!$intOnly){
            exec("php7.4 " . $parsePath . " < " . $src, $parseOut, $parseRc);
        }
        
        if ($parseOnly){
            if ($rc != $parseRc){
                echo "debilku\n";
            }
            if ($rc == 0){
                $file = fopen($name .".tmp", "w");
                foreach($parseOut as $line){ 
                    fwrite($file, $line);
                }
                exec("java -jar " . $jexamxml ." ". $name .".tmp " . $outFile . " ". $name ."delta.xml ". $jexamcfg, $trash, $xmlDiff);
                unlink($name ."delta.xml");

                if (!$xmlDiff){
                    $html = $html . "<td class='passed'>Passed</td>\n";
                    $testDirPassedCount += 1;
                }
                unlink($name .".tmp");
            }
            
            

            return;
        }

        if(!$parseOnly){
            exec("python3.8 " . $interpretPath . " --source=" . $parseOut . " --input=" . $inFile);
        }

        
        
    }

    arg_check();
    if ($recursive) {
        exec("find " . $testDir . " -regex '.*\.src$'", $testPaths);
    }else exec("find " . $testDir . " -maxdepth 1 -regex '.*\.src$'", $testPaths);
    
    $html = $html =
    '<!doctype html>
    <html lang=\"cz\">
    <head>
        <meta charset=\"utf-8\">
        <title>IPPcode21 Test</title>
        <meta name=\"Testování scriptů parse.php a interpret.py\">
        <meta name=\"Karel Norek\">
        
        <style>
            h1 {
                text-align: center;
                color: #676d6a;
            }
            #main {
                width: 70%;
                margin: auto;
            }
            
            table {
                width: 100%;
                box-shadow: 1px 1px 5px 0px rgba(0,0,0,0.47);
                font-family: Helvetica;
                border-collapse: collapse;
            }
            
            table td, table th {
                padding: 8px;
            }
            
            table tbody tr {
                border: 2px solid white;
            }
            
            table tr:nth-child(even){background-color: #f2f2f2;}
            
            table tr:hover {background-color: #ddd;}
            
            table th {
                padding-top: 12px;
                padding-bottom: 12px;
                text-align: left;
                background-color: #878784;
                color: white;
                text-align: center;
            }
            .dir-heading {
                text-align: left;
                padding: 5px 15px;    
                background-color: #626363;
                color: white;;          
            }
            .background-gray{
                background: #dcdcd9;
            }
            .failed {
                color: #e30e0e;
            }
            .passed {
                color: #00b31d;
            }
            .center {
                text-align: center;
            }
        </style>
    </head>
    
    <body>
            <div id="main">
                <table class="center">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Test name</th>
                            <th>Result</th>
                        </tr>
                    </thead>';

    
    $testCount = 0;
    $testDirPassedCount = 0;
    $testDirCodesPassedCount = 0;
    foreach ($testPaths as $src) {   
        $html = $html."<tr>";
        $testCount++;
        $html = $html."<td class='center'>".$testCount."</td>\n";
        parse_test($src, $testDirPassedCount, $testCount);   
    }
    echo $html;
?>