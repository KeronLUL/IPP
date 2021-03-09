<?php
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
        "NOT" => array("var", "symb", "symb"),
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

    function arg_check($word, $argument){
        if ($argument == "var"){
            if (!preg_match("~^(LF|TF|GF)@[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$~", $word)){
                exit(other);
            }
            return "var";
        }else if ($argument == "label"){
            if (!preg_match( "~^[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$~", $word)) {
                exit(other);
            }
            return "label";
        }else if ($argument == "symb"){
            $match = explode("@", $word, 2);
           
            if ($match[0] == "string"){
            #    if (!preg_match("~^[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$~", $match[1])) {
            #        exit(other);
            #    }
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
            }else return "nil";
        }
    }

    function convert_string($type, $line){
        if (preg_match("~^(string|bool|int)~", $type)){
            $string = explode("@", $line, 2);
            return $string[1];
        }else return $line;
    }

    function parse_instruction(){
        global $instructions;
        $counter = 0;

        $domtree = new DOMDocument('1.0', 'UTF-8');
        $domtree->formatOutput = true;
        $xmlRoot = $domtree->createElement("program");
        $xmlRoot->setAttribute("language", "IPPcode21");
        $xmlRoot = $domtree->appendChild($xmlRoot);

        while ($line = read_line()){
            $foo = array_key_exists($line[0], $instructions);

            if(!$foo){
                exit(other);
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
                $line[1] = convert_string($type, $line[1]);
                $xmlArg1 = $domtree->createElement("arg1", $line[1]);
                $xmlArg1->setAttribute("type", $type);
                $xmlInstruction->appendChild($xmlArg1);
            }

            if (count($instruction) == 2){
                $type1 = arg_check($line[1], $instruction[0]);
                $line[1] = convert_string($type1, $line[1]);
                $xmlArg1 = $domtree->createElement("arg1", $line[1]);
                $xmlArg1->setAttribute("type", $type1);
                
                
                $type2 = arg_check($line[2], $instruction[1]);
                $line[2] = convert_string($type2, $line[2]);
                $xmlArg2 = $domtree->createElement("arg2", $line[2]);
                $xmlArg2->setAttribute("type", $type2);

                $xmlInstruction->appendChild($xmlArg1);
                $xmlInstruction->appendChild($xmlArg2);
            }

            if (count($instruction) == 3){
                $type1 = arg_check($line[1], $instruction[0]);
                $line[1] = convert_string($type1, $line[1]);
                $xmlArg1 = $domtree->createElement("arg1", $line[1]);
                $xmlArg1->setAttribute("type", $type1);
                
                $type2 = arg_check($line[2], $instruction[1]);
                $line[2] = convert_string($type2, $line[2]);
                $xmlArg2 = $domtree->createElement("arg2", $line[2]);
                $xmlArg2->setAttribute("type", $type2);

                $type3 = arg_check($line[3], $instruction[2]);
                $line[3] = convert_string($type3, $line[3]);
                $xmlArg3 = $domtree->createElement("arg2", $line[3]);
                $xmlArg3->setAttribute("type", $type3);

                $xmlInstruction->appendChild($xmlArg1);
                $xmlInstruction->appendChild($xmlArg2);
                $xmlInstruction->appendChild($xmlArg3);
            }


            $xmlRoot->appendChild($xmlInstruction);
        }

        echo $domtree->saveXML();
    }

    if ($argc > 1) {
        if ($argv[1] == "--help" && $argc == 2) {
            echo "help\n";
        }else{ 
            exit(badParam);
        }
    }

    $line = read_line();
    if(!preg_match("~^\.ippcode21$~i", $line[0])) {
        exit(badHeader);
    }

    parse_instruction();
    exit(0);
?>