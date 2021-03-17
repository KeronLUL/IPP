<?php
    /*
        IPP project 2021
        parse.php
        Author: Karel Norek, xnorek01
    */
    const badParam = 10;
    const badHeader = 21;
    const wrongOpcode = 22;
    const other = 23;

    $instructions = array(
        "MOVE" => array("var", "symb"),
        "CREATEFRAME" => array(),
        "PUSHFRAME" => array(),
        "POPFRAME" => array(),
        "DEFVAR" => array("var"),
        "CALL" => array("label"),
        "RETURN" => array(),
        "PUSHS" => array("symb"),
        "POPS" => array("var"),
        "ADD" => array("var", "symb", "symb"),
        "SUB" => array("var", "symb", "symb"),
        "MUL" => array("var", "symb", "symb"),
        "IDIV" => array("var", "symb", "symb"),
        "LT" => array("var", "symb", "symb"),
        "GT" => array("var", "symb", "symb"),
        "EQ" => array("var", "symb", "symb"),
        "AND" => array("var", "symb", "symb"),
        "OR" => array("var", "symb", "symb"),
        "NOT" => array("var", "symb"),
        "INT2CHAR" => array("var", "symb"),
        "STRI2INT" => array("var", "symb", "symb"),
        "READ" => array("var", "type"),
        "WRITE" => array("symb"),
        "CONCAT" => array("var", "symb", "symb"),
        "STRLEN" => array("var", "symb"),
        "GETCHAR" => array("var", "symb", "symb"),
        "SETCHAR" => array("var", "symb", "symb"),
        "TYPE" => array("var", "symb"),
        "LABEL" => array("label"),
        "JUMP" => array("label"),
        "JUMPIFEQ" => array("label", "symb", "symb"),
        "JUMPIFNEQ" => array("label", "symb", "symb"),
        "EXIT" => array("symb"),
        "DPRINT" => array("symb"),
        "BREAK" => array(),
    );

    # Read lines and skip empty lines or lines with only comments
    function read_line() {
        $STDIN = STDIN;
        while(true) {
            if (($line = fgets($STDIN)) == false) {
                return 0;
            }
            if (preg_match("~^\s*#~", $line) || preg_match("~^\s*$~", $line)){
                continue;
            }
            $splitLine = explode("#", $line);
            $words = preg_split("~\s+~", $splitLine[0]);
           
            if (end($words) == ""){ 
                array_pop($words);
            }
            if ($words[0] == ""){
                array_shift($words);
            } 
            break;
        }
        return $words;
    }

    # Check arguments of instructions with regular expressions
    function arg_check($word, $argument){
        if ($argument == "var"){
            
            if (!preg_match("~^(LF|TF|GF)@[a-zA-Z_\-$&%!?*][a-zA-Z0-9_\-$&%!?*]*$~", $word)){
                exit(other);
            }
            return "var";
        }else if ($argument == "label"){
            if (!preg_match( "~^[a-zA-Z_\-$&%!?*][a-zA-Z0-9_\-$&%!?*]*$~", $word)) {
                exit(other);
            }
            return "label";
        }else if ($argument == "type"){
            if (!preg_match("~^(int|string|bool)$~", $word)){
                exit(other);
            }
            return "type";
        }else if ($argument == "symb"){
            $match = explode("@", $word, 2);
           
            if ($match[0] == "string"){
                if (preg_match("~\s~", $match[1])) {
                    exit(other);
                }if (preg_match("~\\\\~", $match[1])){
                    $test_slash= explode("\\", $match[1]);
                    for ($i = 1; $i <= count($test_slash); $i++){
                        if (!preg_match("~^[0-9]{3,}~", $test_slash[1])){
                            exit(other);
                        }
                    }
                }
                return "string";
            }else if($match[0] == "int"){
                if (!preg_match("~^[+-]?[0-9]+$~", $match[1])){
                    exit(other);
                }
                return "int";
            }else if($match[0] == "bool"){
                if (!preg_match("~^(true|false)$~", $match[1])){
                    exit(other);
                }
                return "bool";
            }else if(preg_match("~^(LF|TF|GF)~", $match[0])){
                if (!preg_match("~^[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$~", $match[1])){
                    exit(other);
                }
                return "var";
            }else if($match[0] == "nil"){
                if (!preg_match("~^nil$~", $match[1])){
                    exit(other);
                }
                return "nil";
            }else exit(other);
        }else exit(other);
    }

    # Split symbol into 2 string for easier work with XML
    function convert_string($type, $line){
        if (preg_match("~^(string|bool|int|nil)~", $type)){
            $string = explode("@", $line, 2);
            return $string[1];
        }else return $line;
    }

    # Check if instruction is correct and write it into XML
    function parse_instruction(){
        global $instructions;
        $counter = 0;

        $domtree = new DOMDocument('1.0', 'UTF-8');
        $domtree->formatOutput = true;
        $xmlRoot = $domtree->createElement("program");
        $xmlRoot->setAttribute("language", "IPPcode21");
        $xmlRoot = $domtree->appendChild($xmlRoot);

        while ($line = read_line()){
            $line[0] = strtoupper($line[0]);
            $foo = array_key_exists($line[0], $instructions);

            if(!$foo){
                exit(wrongOpcode);
            }
            $instruction = $instructions[$line[0]];
          
            if (count($instruction) + 1 != (count($line))){
                exit(other);
            }
            $counter += 1;
           
            $xmlInstruction = $domtree->createElement("instruction");
            $xmlInstruction->setAttribute("order", $counter);
            $xmlInstruction->setAttribute("opcode", $line[0]);

            if (count($instruction) == 1){
                
                $type = arg_check($line[1], $instruction[0]);
                $line[1] = convert_string($type, htmlspecialchars($line[1]));
                $xmlArg1 = $domtree->createElement("arg1", $line[1]);
                $xmlArg1->setAttribute("type", $type);
                $xmlInstruction->appendChild($xmlArg1);
            }

            if (count($instruction) == 2){
                for ($i = 1; $i <= 2; $i++) {
                    $type = arg_check($line[$i], $instruction[$i-1]);
                    $line[$i] = convert_string($type, $line[$i]);
                    $xmlArg = $domtree->createElement("arg{$i}", htmlspecialchars($line[$i]));
                    $xmlArg->setAttribute("type", $type);
                    $xmlInstruction->appendChild($xmlArg);
                }
            }
            if (count($instruction) == 3){
                for ($i = 1; $i <= 3; $i++) {
                    $type = arg_check($line[$i], $instruction[$i-1]);
                    $line[$i] = convert_string($type, $line[$i]);
                    $xmlArg = $domtree->createElement("arg{$i}", htmlspecialchars($line[$i]));
                    $xmlArg->setAttribute("type", $type);
                    $xmlInstruction->appendChild($xmlArg);
                }
            }
            $xmlRoot->appendChild($xmlInstruction);
        }
        echo $domtree->saveXML();
    }

    # Argument check
    if ($argc > 1) {
        if ($argv[1] == "--help" && $argc == 2) {
            echo "Parser that parses\nUsage: No arguments or --help: prints this help\nScript takes stdin as input and stdout as output\n";
            exit(0);
        }else{ 
            exit(badParam);
        }
    }

    # Check if input contains correct header
    $line = read_line();
    if(!preg_match("~^\.ippcode21$~i", $line[0])) {
        exit(badHeader);
    }

    parse_instruction();
    exit(0);
?>