<?php

main($argv, $argc);
exit(0);

function main($argv, $argc)
{
    hmtl_head();
    $dir = "./";
    $parse_file = "parse.php";
    $int_file = "interpret.py";
    $jexamxml_file = "/pub/courses/ipp/jexamxml/jexamxml.jar";
    $parse_int_only = 0; //-1 -> parse 1 -> int 0 -> both
    $recursive = parse_args($argv, $argc, $dir, $parse_file, $int_file, $jexamxml_file, $parse_int_only);
    check_file($dir);




    if($parse_int_only == -1)
    {
        check_file($jexamxml_file);
        check_file($parse_file);
        test_parser($dir, $parse_file, $jexamxml_file, $recursive);
    }

    elseif ($parse_int_only == 1)
    {
        check_file($int_file);
        test_interpret($dir, $int_file, $recursive);
    }

    else
    {
        check_file($parse_file);
        check_file($int_file);
        test_both($dir, $parse_file, $int_file, $jexamxml_file, $recursive);
    }

}


function parse_args($argv, $argc, &$dir, &$parse_file, &$int_file, &$jexamxml_file, &$parse_int_only)
{
    $directory = false;
    $recursive = false;
    $parse_script = false;
    $int_script = false;
    $parse_only = false;
    $int_only = false;
    $jexamxml = false;

    if(strcmp($argv[1], "--help") == 0 && $argc == 2)
    {
        echo "Skript (test.phpv jazyce PHP 7.4) bude sloužit pro automatické testování postupné aplikaceparse.phpainterpret.py";
        exit(0);
    }


    else
    {
        for($i = 1; $i < $argc; $i++)
        {
            if(preg_match("/^--directory=.+$/", $argv[$i]) == 1)
            {

                if($directory)
                    exit(10);
                else
                {
                    $dir = get_filename($argv[$i]);
                    if(strcmp(substr($dir, -1), "/") != 0)
                        $dir = $dir . "/";
                    $directory = true;
                }

            }
            elseif(strcmp($argv[$i], "--recursive") == 0)
            {
                if($recursive)

                    exit(10);
                else
                    $recursive = true;
            }
            elseif(preg_match("/^--parse-script=.+$/", $argv[$i]) == 1)
            {
                if($parse_script || $int_only)
                    exit(10);
                else
                {
                    $parse_file = get_filename($argv[$i]);
                    $parse_script = true;
                }
            }
            elseif(preg_match("/^--int-script=.+$/", $argv[$i]) == 1)
            {
                if($int_script || $parse_only)
                    exit(10);
                else
                {
                    $int_file = get_filename($argv[$i]);
                    $int_script = true;
                }
            }
            elseif(strcmp($argv[$i], "--parse-only") == 0)
            {
                if($parse_only || $int_only || $int_script)
                    exit(10);
                else
                {
                    $parse_only = true;
                    $parse_int_only = -1;
                }


            }
            elseif(strcmp($argv[$i], "--int-only") == 0)
            {
                if($int_only || $parse_only || $parse_script)
                    exit(10);
                else
                {
                    $int_only = true;
                    $parse_int_only = 1;
                }

            }
            elseif(preg_match("/^--jexamxml=.+$/", $argv[$i]) == 1)
            {
                if($jexamxml)
                    exit(10);
                else
                {
                    $jexamxml_file = get_filename($argv[$i]);
                    $jexamxml = true;
                }
            }
            else
                exit(10);
        }
    }
    return $recursive;
}

function check_file($filename)
{
    if(!file_exists($filename))
    {
        echo "FILE DOESNT EXISTS" . $filename;
        exit(11);
    }

}

function get_filename($arg)
{
    $temp = preg_split("/=/", $arg, $limit = 2);
    return $temp[1];
}

function test_parser($dir, $parser, $jexam, $recursive)
{
    $test_number = 0;
    $test_success = 0;
    if($recursive)
    {
        $tmp = tempnam(".", "tmp");
        $di = new RecursiveDirectoryIterator($dir);
        foreach (new RecursiveIteratorIterator($di) as $filename)
        {
            if(preg_match("/^.+\.src$/", $filename))
            {
                if(strcmp(basename($filename),".src") != 0)
                {
                    $success = exec_parser($parser, $jexam, $tmp, $filename, true, $test_number);
                    if($success)
                        $test_success++;
                    $test_number++;
                }
            }

        }
        clean($tmp);

    }
    else
    {
        $tmp = tempnam(".", "tmp");
        $src = find_src($dir);
        foreach ($src as $s)
        {
            $success = exec_parser($parser, $jexam, $tmp, $s, true, $test_number++);
            if($success)
                $test_success++;
            $test_number++;
        }

        clean($tmp);
    }

    html_end($test_success, $test_number);
}

function test_interpret($dir, $interpret, $recursive)
{
    $test_success = 0;
    $test_number = 0;
    if($recursive)
    {
        $tmp = tempnam(".", "tmp");
        $di = new RecursiveDirectoryIterator($dir);
        foreach (new RecursiveIteratorIterator($di) as $filename)
        {
            if(preg_match("/^.+\.src$/", $filename))
            {
                if(strcmp(basename($filename),".src") != 0)
                {
                    $success = exec_interpret($interpret, $tmp, $filename, true, $test_number);
                    if($success)
                        $test_success++;
                    $test_number++;
                }

            }

        }
        clean($tmp);
    }
    else
    {

        $tmp = tempnam(".", "tmp");
        $src = find_src($dir);
        foreach ($src as $s)
        {
            $success = exec_interpret($interpret, $tmp, $s, true, $test_number);
            if($success)
                $test_success++;

            $test_number++;
        }
        clean($tmp);
    }
    html_end($test_success, $test_number);
}

function test_both($dir, $parser, $interpret, $jexamxml, $recursive)
{
    $test_success = 0;
    $test_number = 0;
    if($recursive)
    {
        $tmp = tempnam(".", "tmp");
        $di = new RecursiveDirectoryIterator($dir);
        foreach (new RecursiveIteratorIterator($di) as $filename)
        {
            if(preg_match("/^.+\.src$/", $filename))
            {
                if(strcmp(basename($filename),".src") != 0)
                {
                    $success = exec_parser($parser, $jexamxml, $tmp, $filename,false, $test_number);
                    if($success)
                    {
                        $success = exec_interpret($interpret, $tmp, $filename, false, $test_number);
                        if($success)
                            $test_success++;
                        /*else
                        {
                            fopen($filename . "_debug", "w+");
                            copy($tmp, $filename . "_debug");
                        }*/
                    }
                    $test_number++;
                }
            }
        }
        clean($tmp);
    }
    else
    {
        $tmp = tempnam(".", "tmp");
        $src = find_src($dir);
        foreach ($src as $s)
        {
            $success = exec_parser($parser, $jexamxml, $tmp, $s,false, $test_number);
            if($success)
            {
                $success = exec_interpret($interpret, $tmp, $s, false, $test_number);
                if($success)
                    $test_success++;
            }


            $test_number++;
        }
        clean($tmp);
    }
    html_end($test_success, $test_number);
}

function exec_parser($parser, $jexam, &$tmp, $src, $parse_only, $test_number)
{
    $src_name = substr($src, 0, -4);
    $jexam_options = dirname($jexam);


    $rc = check_in_out_rc($src_name);

    $out_path = $src_name .".out";

    $arguments = " <" . $src . " >" . $tmp;

    exec("php7.4 " . $parser . $arguments, $output, $rc_my);

    $your_rc = fgets($rc);
    if($your_rc == 0)
    {
        if($rc_my == $your_rc)
        {
            if($parse_only)
            {
                exec("java -jar " . $jexam . " " . $out_path ." " . $tmp . " " . $jexam_options ."/options", $output, $return);
                if($return == 0)
                {
                    html_row($src, true, $test_number, -1);
                    return true;
                }

                else
                {
                    html_row($src, false, $test_number, -1);
                    return false;
                }
            }
            else
                return true;
        }
        else
        {
            html_row($src, false, $test_number, -1);
            return false;
        }
    }
    else
    {
        if($rc_my == $your_rc)
        {
            html_row($src, true, $test_number, -1);
            return false;
        }
        else
            return true;
    }
}

function exec_interpret($interpret, $tmp, $src, $int_only, $test_number)
{
    $src_name = substr($src, 0, -4);
    $rc = check_in_out_rc($src_name);

    if($int_only)
    {
        $src_path = $src;
        $my_out = $tmp;
    }
    else
    {
        $src_path = $tmp;
        $my_out = tempnam(".", "int");
    }

    $in_path = $src_name . ".in";
    $out_path = $src_name . ".out";
    $arguments = " --source=" . $src_path . " --input=" . $in_path . " >" . $my_out;

    exec("python3.8 " . $interpret . $arguments, $output, $rc_my);
    if($rc_my == fgets($rc))
    {
        if($rc_my == 0)
        {
            exec("diff " . $out_path . " " . $my_out, $output, $return);
            if($return == 0)
            {
                if($int_only)
                {
                    html_row($src, true, $test_number, 1);
                    $suc = true;
                }
                else
                {
                    html_row($src, true, $test_number, 0);
                    $suc = true;
                }

            }
            else
            {
                if($int_only)
                {

                    html_row($src, false, $test_number, 1);
                    $suc = false;
                }
                else
                {
                    html_row($src, false, $test_number, 0);
                    $suc = false;
                }

            }
        }
        else
        {
            if($int_only)
            {
                html_row($src, true, $test_number, 1);
                $suc = true;
            }
            else
            {
                html_row($src, true, $test_number, 0);
                $suc = true;
            }
        }
    }
    else
    {
        if($int_only)
        {
            html_row($src, false, $test_number, 1);
            $suc = false;
        }
        else
        {
            html_row($src, false, $test_number, 0);
            $suc = false;
        }

    }

    if(!$int_only)
        unlink($my_out);
    return $suc;
}

function find_src($dir)
{
    $src_files = glob($dir . "*.src");
    $src_sorted = [];
    foreach ($src_files as $s)
    {
        if(!is_dir($s))
            $src_sorted[] = $s;
    }
    return $src_sorted;
}

function check_in_out_rc($src_name)
{
    if(!file_exists( $src_name . ".in"))
        fopen($src_name . ".in", "w+");
    if(!file_exists($src_name . ".out"))
        fopen($src_name . ".out", "w+");
    if(file_exists( $src_name .".rc"))
        return fopen($src_name . ".rc", "r");
    else
        $rc = fopen($src_name .".rc", "w+");
    fwrite($rc, "0");
    return $rc;
}


function clean($tmp)
{
    unlink($tmp);
}

function hmtl_head()
{
    echo "<!DOCTYPE html>
        <html lang = \"cs-CZ\">
            <head>
            <style type=\"text/css\">
                table, th, td {
                    padding: 10px;
                    border-collapse: collapse;
                }
                table, th{border: 3px solid black;}
                td {border: 1px solid black;}
                
               </style>
                <meta charset = \"UTF-8\">
                <title>Výsledky testů</title>
            </head>
            <body>
                <h1>Výsledky testů</h1> 
                
                <table style=\"width:100%\">
                    <tr>
                        <th>Jméno testu</th>
                        <th>Umístění</th>
                        <th>Testováno</th>
                        <th>Výsledek</th>
                    </tr>";
}

function html_row($test_path_with_filename, $passed, $test_number, $tested)
{
    $id = "R" . $test_number;
    $test_name = basename($test_path_with_filename);
    $dir = dirname($test_path_with_filename);

    if($passed)
        echo "<style>table tr#$id {background-color: chartreuse}</style>";
    else
        echo "<style>table tr#$id {background-color: crimson }</style>";

    echo "
                    <tr id=$id>
                        <td>$test_name</td>
                        <td>$dir</td>";
    if($tested == -1)
        echo "<td>parser.php</td>";
    elseif ($tested == 1)
        echo "<td>interpret.py</td>";
    else
        echo "<td>parser.php a interpret.py</td>";
    if($passed)
        echo "<td>Úspěšný</td>";
    else
        echo "<td>Neúspěšný</td>";

    echo "</tr>";
}

function html_end($succes, $sum)
{
    echo "</table> ";

    if($succes == $sum)
        echo "<p style=\"font-size: large; font-weight: bold; text-align: right \">Testů splňěno: $succes/$sum</p>";
    else
        echo "<p style=\"color: crimson; font-size: large;font-weight: bold; text-align: right\">Testů splňěno: $succes/$sum</p>";
        echo"    </body>
        </html>";
}
