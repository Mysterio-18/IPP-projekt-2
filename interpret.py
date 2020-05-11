import sys
import xml.etree.ElementTree as ET
import re
import argparse


global_frame = dict()
local_frame = list()
lf_pointer = -1
temporary_frame = None

stack = list()


def main():
    source_file = None
    args = None
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--help', action='store_true')
    parser.add_argument('--source')
    parser.add_argument('--input')
    try:
        args = parser.parse_args()
    except SystemExit:
        print("Chybějící parametr skriptu nebo použití zakázané kombinace parametrů", file=sys.stderr)
        exit(10)

    if args.help:
        if len(sys.argv) == 2:
            print("Program načte XML reprezentaci programu a tento program s využitím vstupu "
                  "dle parametrů příkazové řádky interpretuje a generuje výstup.")
            exit(0)
        else:
            print("Chybějící parametr skriptu nebo použití zakázané kombinace parametrů", file=sys.stderr)
            exit(10)
    elif args.source or args.input:
        if args.source and args.input:
            try:
                source_file = open(args.source, "r")
                sys.stdin = open(args.input, "r")
            except FileNotFoundError:
                print("FileNotFoundError", file=sys.stderr)
                exit(11)
            except PermissionError:
                print("PermissionError", file=sys.stderr)
                exit(11)
        elif args.source:
            try:
                source_file = open(args.source, "r")
            except FileNotFoundError:
                print("FileNotFoundError", file=sys.stderr)
                exit(11)
            except PermissionError:
                print("PermissionError", file=sys.stderr)
                exit(11)
        else:
            source_file = sys.stdin
            try:
                sys.stdin = open(args.input, "r")
            except FileNotFoundError:
                print("FileNotFoundError", file=sys.stderr)
                exit(11)
            except PermissionError:
                print("PermissionError", file=sys.stderr)
                exit(11)
    else:
        print("Chybějící parametr skriptu nebo použití zakázané kombinace parametrů", file=sys.stderr)
        exit(10)

    root = None
    try:
        root = ET.parse(source_file).getroot()
    except ET.ParseError:
        print("XML není \"well-formed\"", file=sys.stderr)
        exit(31)
    if "language" in root.attrib:
        if root.attrib['language'] != "IPPcode20":
            print("Chybný text atributu language", file=sys.stderr)
            exit(32)
    else:
        print("Chybí atribut language", file=sys.stderr)
        exit(32)

    instructions = dict()
    labels = dict()
    for elem_instr in root:
        if elem_instr.tag == "instruction":
            if 'order' in elem_instr.attrib and 'opcode' in elem_instr.attrib:
                cur_order = elem_instr.attrib['order']
                cur_instr = elem_instr.attrib['opcode']
                try:
                    int(cur_order)
                except ValueError:
                    print("ValueError", file=sys.stderr)
                    exit(32)
                if cur_order in instructions or int(cur_order) < 1:
                    print("Opakovaný order nebo order menší než 1")
                    exit(32)
                else:
                    cur_instr = cur_instr.upper()
                    instructions[cur_order] = dict()
                    instructions[cur_order][cur_instr] = dict()
                    parse_instr(cur_instr, elem_instr, instructions[cur_order][cur_instr], labels, cur_order)

            else:
                print("Chybí atribut order nebo opcode")
                exit(32)
        else:
            print("Chybný tag(není instruction)")
            exit(32)
    interpret_instr(instructions, labels)
    

def parse_instr(instr, elem, cur_instr, labels, cur_order):

    if instr == "MOVE":
        return var_symb(elem, cur_instr)
    elif instr == "NOT":
        return var_symb(elem, cur_instr)
    elif instr == "INT2CHAR":
        return var_symb(elem, cur_instr)
    elif instr == "STRLEN":
        return var_symb(elem, cur_instr)
    elif instr == "TYPE":
        return var_symb(elem, cur_instr)

    elif instr == "CREATEFRAME":
        return empty(elem)
    elif instr == "PUSHFRAME":
        return empty(elem)
    elif instr == "POPFRAME":
        return empty(elem)
    elif instr == "RETURN":
        return empty(elem)
    elif instr == "BREAK":
        return empty(elem)

    elif instr == "DEFVAR":
        return var(elem, cur_instr)
    elif instr == "POPS":
        return var(elem, cur_instr)

    elif instr == "CALL":
        return label(elem, cur_instr, labels, False, cur_order)
    elif instr == "LABEL":
        return label(elem, cur_instr, labels, True, cur_order)
    elif instr == "JUMP":
        return label(elem, cur_instr, labels, False, cur_order)

    elif instr == "PUSHS":
        return symb(elem, cur_instr)
    elif instr == "WRITE":
        return symb(elem, cur_instr)
    elif instr == "EXIT":
        return symb(elem, cur_instr)
    elif instr == "DPRINT":
        return symb(elem, cur_instr)

    elif instr == "ADD":
        return var_symb_symb(elem, cur_instr)
    elif instr == "SUB":
        return var_symb_symb(elem, cur_instr)
    elif instr == "MUL":
        return var_symb_symb(elem, cur_instr)
    elif instr == "IDIV":
        return var_symb_symb(elem, cur_instr)
    elif instr == "LT":
        return var_symb_symb(elem, cur_instr)
    elif instr == "GT":
        return var_symb_symb(elem, cur_instr)
    elif instr == "EQ":
        return var_symb_symb(elem, cur_instr)
    elif instr == "AND":
        return var_symb_symb(elem, cur_instr)
    elif instr == "OR":
        return var_symb_symb(elem, cur_instr)
    elif instr == "STRI2INT":
        return var_symb_symb(elem, cur_instr)
    elif instr == "CONCAT":
        return var_symb_symb(elem, cur_instr)
    elif instr == "GETCHAR":
        return var_symb_symb(elem, cur_instr)
    elif instr == "SETCHAR":
        return var_symb_symb(elem, cur_instr)

    elif instr == "READ":
        return var_type(elem, cur_instr)

    elif instr == "JUMPIFEQ":
        return label_symb_symb(elem, cur_instr)
    elif instr == "JUMPIFNEQ":
        return label_symb_symb(elem, cur_instr)
    else:
        print("Neznámá instrukce", file=sys.stderr)
        exit(32)


def var_symb(elem, cur_instr):
    done_1 = False
    done_2 = False
    if len(elem) != 2:
        print("Chybný počet argumentů", file=sys.stderr)
        exit(32)
    for arg in elem:
        if arg.tag == "arg1" and not done_1:
            check_var(arg, cur_instr, arg.tag)
            done_1 = True
        elif arg.tag == "arg2" and not done_2:
            check_symb(arg, cur_instr, arg.tag)
            done_2 = True
        else:
            print("Chybný počet argumentů", file=sys.stderr)
            exit(32)
    return 0


def var_type(elem, cur_instr):
    done_1 = False
    done_2 = False
    if len(elem) != 2:
        print("Chybný počet argumentů", file=sys.stderr)
        exit(32)
    for arg in elem:
        if arg.tag == "arg1" and not done_1:
            check_var(arg, cur_instr, arg.tag)
            done_1 = True
        elif arg.tag == "arg2" and not done_2:
            check_type(arg, cur_instr, arg.tag)
            done_2 = True
        else:
            print("Neznámý element v xml souboru", file=sys.stderr)
            exit(32)
    return 0


def var_symb_symb(elem, cur_instr):
    done_1 = False
    done_2 = False
    done_3 = False
    if len(elem) != 3:
        print("Neznámý element v xml souboru", file=sys.stderr)
        exit(32)
    for arg in elem:
        if arg.tag == "arg1" and not done_1:
            check_var(arg, cur_instr, arg.tag)
            done_1 = True
        elif arg.tag == "arg2" and not done_2:
            check_symb(arg, cur_instr, arg.tag)
            done_2 = True
        elif arg.tag == "arg3" and not done_3:
            check_symb(arg, cur_instr, arg.tag)
            done_3 = True
        else:
            print("Neznámý element v xml souboru", file=sys.stderr)
            exit(32)
    return 0


def label_symb_symb(elem, cur_instr):
    done_1 = False
    done_2 = False
    done_3 = False
    if len(elem) != 3:
        print("Chybný počet argumentů", file=sys.stderr)
        exit(32)
    for arg in elem:
        if arg.tag == "arg1" and not done_1:
            check_label(arg, cur_instr, arg.tag)
            done_1 = True
        elif arg.tag == "arg2" and not done_2:
            check_symb(arg, cur_instr, arg.tag)
            done_2 = True
        elif arg.tag == "arg3" and not done_3:
            check_symb(arg, cur_instr, arg.tag)
            done_3 = True
        else:
            print("Neznámý element v xml souboru", file=sys.stderr)
            exit(32)
    return 0


def var(elem, cur_instr):
    if len(elem) != 1:
        print("Chybný počet argumentů", file=sys.stderr)
        exit(32)
    for arg in elem:
        if arg.tag == "arg1":
            check_var(arg, cur_instr, arg.tag)
        else:
            print("Neznámý element v xml souboru", file=sys.stderr)
            exit(32)
    return 0


def symb(elem, cur_instr):
    if len(elem) != 1:
        print("Chybný počet argumentů", file=sys.stderr)
        exit(32)
    for arg in elem:
        if arg.tag == "arg1":
            check_symb(arg, cur_instr, arg.tag)
        else:
            print("Neznámý element v xml souboru", file=sys.stderr)
            exit(32)
    return 0


def label(elem, cur_instr, labels, check, cur_order):
    if len(elem) != 1:
        print("Chybný počet argumentů", file=sys.stderr)
        exit(32)
    for arg in elem:
        if arg.tag == "arg1":
            check_label(arg, cur_instr, arg.tag)
            if check:
                for order in labels:
                    if labels[order] == arg.text:
                        print("Redefinice návěští", file=sys.stderr)
                        exit(52)
                labels[cur_order] = arg.text
        else:
            print("Neznámý element v xml souboru", file=sys.stderr)
            exit(32)
    return 0


def empty(elem):
    if len(elem) != 0:
        print("Chybný počet argumentů", file=sys.stderr)
        exit(32)
    else:
        return 0


def check_var(arg, cur_arg, arg_tag):
    if 'type' in arg.attrib:
        if arg.attrib['type'] == "var" and arg.text is not None:
            if re.search(r"^[GLT]F@[a-zA-Z_\-$&%*!?][\da-zA-Z_\-$&%*!?]*$", arg.text) is None:
                print("Nepovolený tvar proměnné", file=sys.stderr)
                exit(32)
            else:
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
        else:
            print("Nepovolený tvar proměnné", file=sys.stderr)
            exit(32)
    else:
        print("Chybějící atribut", file=sys.stderr)
        exit(32)


def check_symb(arg, cur_arg, arg_tag):
    if 'type' in arg.attrib:
        if arg.attrib['type'] == "var" and arg.text is not None:
            if re.search(r"^[GLT]F@[a-zA-Z_\-$&%*!?][\da-zA-Z_\-$&%*!?]*$", arg.text) is None:
                print("Nepovolený tvar proměnné", file=sys.stderr)
                exit(32)
            else:
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
        elif arg.attrib['type'] == "string":
            if arg.text is None:
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
            elif re.search(r"^([^\s#\\]|(\\\d\d\d))*$", arg.text) is None:
                print("Nepovolený tvar řetězce", file=sys.stderr)
                exit(32)
            else:
                while True:
                    escape = re.search(r"\\\d\d\d", arg.text)
                    if escape is None:
                        break
                    else:
                        escape = escape.group()[1:]
                        char = chr(int(escape))
                        arg.text = re.sub(r"\\\d\d\d", char, arg.text, count=1)

                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
        elif arg.attrib['type'] == "int" and arg.text is not None:
            if re.search(r"^(0|[+-]?[1-9]\d*)$", arg.text) is None:
                print("Nepovolený tvar čísla", file=sys.stderr)
                exit(32)
            else:
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
        elif arg.attrib['type'] == "bool" and arg.text is not None:
            if arg.text == "true" or arg.text == "false":
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
        elif arg.attrib['type'] == "nil":
            if arg.text == "nil":
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
            else:
                print("Nepovolený tvar nil", file=sys.stderr)
                exit(32)
        else:
            print("Nepovolený tvar symb", file=sys.stderr)
            exit(32)
    else:
        print("Chybějící atribut", file=sys.stderr)
        exit(32)


def check_label(arg, cur_arg, arg_tag):
    if 'type' in arg.attrib:
        if arg.attrib['type'] == "label" and arg.text is not None:
            if re.search(r"^[a-zA-Z_\-$&%*!?][\da-zA-Z_\-$&%*!?]*$", arg.text) is None:
                print("Nepovolený tvar návěští", file=sys.stderr)
                exit(32)
            else:
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
        else:
            print("Nepovolený tvar návěští", file=sys.stderr)
            exit(32)
    else:
        print("Chybějící atribut", file=sys.stderr)
        exit(32)


def check_type(arg, cur_arg, arg_tag):
    if 'type' in arg.attrib:
        if arg.attrib['type'] == "type" and arg.text is not None:
            if arg.text == "int" or arg.text == "string" or arg.text == "bool":
                cur_arg[arg_tag] = [arg.attrib['type'], arg.text]
                return 0
            else:
                print("Nepovolený tvar type", file=sys.stderr)
                exit(32)
        else:
            print("Nepovolený tvar type", file=sys.stderr)
            exit(32)
    else:
        print("Chybějící atribut", file=sys.stderr)
        exit(32)


def interpret_instr(instructions, labels):
    last = 0
    order_for_return = list()
    while True:
        order = find_next(instructions, last)
        if order == 0:
            break
        new_order = find_instr(instructions[str(order)], labels, order, order_for_return)
        if new_order is not None:
            last = new_order
        else:
            last = order


def find_next(instructions, last_ord):
    next_ord = float('inf')

    for order in instructions:
        checked = int(order)
        if int(last_ord) < checked < next_ord:
            next_ord = checked

    if next_ord == float('inf'):
        exit(0)
    else:
        return next_ord


def find_instr(cur_instr, labels, order, order_for_return):
    if 'MOVE' in cur_instr:
        interpret_move(cur_instr['MOVE'])
    elif "CREATEFRAME" in cur_instr:
        interpret_createframe()
    elif "PUSHFRAME" in cur_instr:
        interpret_pushframe()
    elif "POPFRAME" in cur_instr:
        interpret_popframe()
    elif "DEFVAR" in cur_instr:
        interpret_defvar(cur_instr['DEFVAR'])
    elif "CALL" in cur_instr:
        return interpret_call(cur_instr['CALL'], labels, order, order_for_return)
    elif "RETURN" in cur_instr:
        return interpret_return(order_for_return)

    elif "POPS" in cur_instr:
        interpret_pops(cur_instr['POPS'])
    elif "PUSHS" in cur_instr:
        interpret_pushs(cur_instr['PUSHS'])

    elif "ADD" in cur_instr:
        interpret_add(cur_instr['ADD'])
    elif "SUB" in cur_instr:
        interpret_sub(cur_instr['SUB'])
    elif "MUL" in cur_instr:
        interpret_mul(cur_instr['MUL'])
    elif "IDIV" in cur_instr:
        interpret_idiv(cur_instr['IDIV'])
    elif "LT" in cur_instr:
        interpret_lt(cur_instr['LT'])
    elif "GT" in cur_instr:
        interpret_gt(cur_instr['GT'])
    elif "EQ" in cur_instr:
        interpret_eq(cur_instr['EQ'])
    elif "AND" in cur_instr:
        interpret_and(cur_instr['AND'])
    elif "OR" in cur_instr:
        interpret_or(cur_instr['OR'])
    elif "NOT" in cur_instr:
        interpret_not(cur_instr['NOT'])
    elif "INT2CHAR" in cur_instr:
        interpret_int2char(cur_instr['INT2CHAR'])
    elif "STRI2INT" in cur_instr:
        interpret_stri2int(cur_instr['STRI2INT'])

    elif "READ" in cur_instr:
        interpret_read(cur_instr['READ'])
    elif "WRITE" in cur_instr:
        interpret_write(cur_instr['WRITE'])

    elif "CONCAT" in cur_instr:
        interpret_concat(cur_instr['CONCAT'])
    elif "STRLEN" in cur_instr:
        interpret_strlen(cur_instr['STRLEN'])
    elif "GETCHAR" in cur_instr:
        interpret_getchar(cur_instr['GETCHAR'])
    elif "SETCHAR" in cur_instr:
        interpret_setchar(cur_instr['SETCHAR'])

    elif "TYPE" in cur_instr:
        interpret_type(cur_instr['TYPE'])

    elif "LABEL" in cur_instr:
        return None
    elif "JUMP" in cur_instr:
        return interpret_jump(cur_instr['JUMP'], labels)
    elif "JUMPIFEQ" in cur_instr:
        return interpret_jumpifeq(cur_instr['JUMPIFEQ'], labels)
    elif "JUMPIFNEQ" in cur_instr:
        return interpret_jumpifneq(cur_instr['JUMPIFNEQ'], labels)
    elif "EXIT" in cur_instr:
        interpret_exit(cur_instr['EXIT'])

    elif "DPRINT" in cur_instr:
        return None
    elif "BREAK" in cur_instr:
        return None

    return None


def interpret_defvar(args):
    frame, name = split_var_arg(args, "arg1")
    if frame == "GF":
        if name in global_frame:
            print("Redefinice proměnné", file=sys.stderr)
            exit(52)
        else:
            global_frame[name] = [None, None]
    elif frame == "LF":
        if lf_pointer >= 0:
            if name in local_frame[lf_pointer]:
                print("Redefinice proměnné", file=sys.stderr)
                exit(52)
            else:
                local_frame[lf_pointer][name] = [None, None]
        else:
            print("Rámec neexistuje", file=sys.stderr)
            exit(55)
    else:
        if temporary_frame is not None:
            if name in temporary_frame:
                print("Redefinice proměnné", file=sys.stderr)
                exit(52)
            else:
                temporary_frame[name] = [None, None]
        else:
            print("Rámec neexistuje", file=sys.stderr)
            exit(55)


def interpret_move(args):
    var_value = get_var_value(args, 'arg1')
    symb_value = get_symb_value(args, 'arg2')
    if symb_value[0] is None:
        exit(56)
    var_value[0] = symb_value[0]
    var_value[1] = symb_value[1]


def interpret_createframe():
    global temporary_frame
    temporary_frame = dict()


def interpret_pushframe():
    global temporary_frame
    global lf_pointer

    if temporary_frame is not None:
        lf_pointer += 1
        local_frame.append(temporary_frame.copy())
        temporary_frame = None
    else:
        print("Rámec neexistuje", file=sys.stderr)
        exit(55)


def interpret_popframe():
    global temporary_frame
    global lf_pointer

    if lf_pointer >= 0:
        temporary_frame = local_frame[lf_pointer].copy()
        local_frame.pop()
        lf_pointer -= 1
    else:
        print("Rámec neexistuje", file=sys.stderr)
        exit(55)


def interpret_call(args, labels, order, order_for_return):
    label_value = get_label_value(args, 'arg1')
    order_for_return.append(order)
    return find_label(labels, label_value)


def interpret_return(order_for_return):
    if len(order_for_return) > 0:
        new_order = order_for_return[len(order_for_return)-1]
        order_for_return.pop()
        return new_order
    else:
        print("Chybějící hodnota", file=sys.stderr)
        exit(56)


def interpret_pushs(args):
    symb_value = get_symb_value(args, 'arg1')
    if symb_value[0] is None:
        exit(56)
    else:
        stack.append(symb_value)


def interpret_pops(args):
    var_value = get_var_value(args, 'arg1')
    if len(stack) == 0:
        print("Chybějící hodnota", file=sys.stderr)
        exit(56)
    stack_value = stack[len(stack)-1]
    var_value[0] = stack_value[0]
    var_value[1] = stack_value[1]
    stack.pop()


def interpret_add(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    check_ints(symb_value1[0], symb_value2[0])
    s = int(symb_value1[1]) + int(symb_value2[1])
    var_value[0] = symb_value1[0]
    var_value[1] = str(s)


def interpret_sub(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    check_ints(symb_value1[0], symb_value2[0])
    s = int(symb_value1[1]) - int(symb_value2[1])
    var_value[0] = symb_value1[0]
    var_value[1] = str(s)


def interpret_mul(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    check_ints(symb_value1[0], symb_value2[0])
    s = int(symb_value1[1]) * int(symb_value2[1])
    var_value[0] = symb_value1[0]
    var_value[1] = str(s)


def interpret_idiv(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    check_ints(symb_value1[0], symb_value2[0])
    if int(symb_value2[1]) == 0:
        print("Špatná hodnota operandu", file=sys.stderr)
        exit(57)
    else:
        s = int(symb_value1[1]) // int(symb_value2[1])
        var_value[0] = symb_value1[0]
        var_value[1] = str(s)


def interpret_lt(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    elif symb_value1[0] == symb_value2[0]:
        var_value[0] = "bool"
        if symb_value1[0] == "int":
            var_value[1] = str(int(symb_value1[1]) < int(symb_value2[1]))
        elif symb_value1[0] == "string":
            if symb_value1[1] is None:
                symb_value1[1] = ""
            if symb_value2[1] is None:
                symb_value2[1] = ""
            var_value[1] = str(symb_value1[1] < symb_value2[1])
        elif symb_value1[0] == "bool":
            value1 = get_value(symb_value1[1])
            value2 = get_value(symb_value2[1])
            var_value[1] = str(value1 < value2)
        else:
            print("Špatné typy operandů", file=sys.stderr)
            exit(53)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_gt(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    elif symb_value1[0] == symb_value2[0]:
        var_value[0] = "bool"
        if symb_value1[0] == "int":
            var_value[1] = str(int(symb_value1[1]) > int(symb_value2[1]))
        elif symb_value1[0] == "string":
            if symb_value1[1] is None:
                symb_value1[1] = ""
            if symb_value2[1] is None:
                symb_value2[1] = ""
            var_value[1] = str(symb_value1[1] > symb_value2[1])
        elif symb_value1[0] == "bool":
            value1 = get_value(symb_value1[1])
            value2 = get_value(symb_value2[1])
            var_value[1] = str(value1 > value2)
        else:
            print("Špatné typy operandů", file=sys.stderr)
            exit(53)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_eq(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    elif symb_value1[0] == symb_value2[0]:
        var_value[0] = "bool"
        if symb_value1[0] == "int":
            var_value[1] = str(int(symb_value1[1]) == int(symb_value2[1]))
        elif symb_value1[0] == "string":
            if symb_value1[1] is None:
                symb_value1[1] = ""
            if symb_value2[1] is None:
                symb_value2[1] = ""
            var_value[1] = str(symb_value1[1] == symb_value2[1])
        elif symb_value1[0] == "bool":
            value1 = get_value(symb_value1[1])
            value2 = get_value(symb_value2[1])
            var_value[1] = str(value1 == value2)
        else:
            var_value[1] = "True"
    elif symb_value1[0] == "nil" or symb_value2[0] == "nil":
        var_value[1] = "False"
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_and(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    elif symb_value1[0] == symb_value2[0] and symb_value1[0] == "bool":
        var_value[0] = symb_value1[0]
        value1 = get_value(symb_value1[1])
        value2 = get_value(symb_value2[1])
        var_value[1] = str(value1 and value2)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_or(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    elif symb_value1[0] == symb_value2[0] and symb_value1[0] == "bool":
        var_value[0] = symb_value1[0]
        value1 = get_value(symb_value1[1])
        value2 = get_value(symb_value2[1])
        var_value[1] = str(value1 or value2)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_not(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')

    if symb_value1[0] is None:
        exit(56)
    elif symb_value1[0] == "bool":
        var_value[0] = symb_value1[0]
        value1 = get_value(symb_value1[1])
        var_value[1] = str(not value1)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_int2char(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')

    if symb_value1[0] is None:
        exit(56)
    elif symb_value1[0] == "int":
        var_value[0] = "string"
        try:
            var_value[1] = str(chr(int(symb_value1[1])))
        except UnicodeEncodeError:
            print("Chybná práce s řetězcem", file=sys.stderr)
            exit(58)
        except ValueError:
            print("Chybná práce s řetězcem", file=sys.stderr)
            exit(58)
    else:
        exit(53)


def interpret_stri2int(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    if symb_value1[0] == "string" and symb_value2[0] == "int":
        if int(symb_value2[1]) < 0:
            exit(58)
        else:
            var_value[0] = "int"
            try:
                var_value[1] = str(ord(symb_value1[1][int(symb_value2[1])]))
            except IndexError:
                print("Chybná práce s řetězcem", file=sys.stderr)
                exit(58)
            except ValueError:
                print("Chybná práce s řetězcem", file=sys.stderr)
                exit(58)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_read(args):
    var_value = get_var_value(args, 'arg1')
    type_value = get_type_value(args, 'arg2')

    var_value[0] = type_value
    try:
        entry = input()
    except EOFError:
        entry = "nil"
        var_value[0] = "nil"

    if var_value[0] == "bool":
        if entry.lower() == "true":
            var_value[1] = "true"
        else:
            var_value[1] = "false"
    elif var_value[0] == "int":
        try:
            int(entry)
            var_value[1] = entry
        except ValueError:
            var_value[0] = "nil"
            var_value[1] = "nil"

    else:
        var_value[1] = str(entry)


def interpret_write(args):
    symb_value = get_symb_value(args, 'arg1')

    if symb_value[0] is None:
        exit(56)
    elif symb_value[0] == "bool":
        out = symb_value[1].lower()
        print(out, end='')
    elif symb_value[0] == "nil":
        print("", end='')
    else:
        if symb_value[1] is None:
            print("", end='')
        else:
            print(symb_value[1], end='')


def interpret_concat(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    elif symb_value1[0] == symb_value2[0] == "string":
        var_value[0] = symb_value1[0]
        if symb_value1[1] is None:
            var_value[1] = symb_value2[1]
        elif symb_value2[1] is None:
            var_value[1] = symb_value1[1]
        else:
            var_value[1] = symb_value1[1] + symb_value2[1]
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_strlen(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    if symb_value1[0] is None:
        exit(56)
    elif symb_value1[0] == "string":
        var_value[0] = "int"
        if symb_value1[1] is None:
            var_value[1] = "0"
        else:
            var_value[1] = str(len(symb_value1[1]))
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_getchar(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if symb_value2[0] is None or symb_value1[0] is None:
        exit(56)
    elif symb_value1[0] == "string" and symb_value2[0] == "int":
        var_value[0] = symb_value1[0]
        if symb_value1[1] is None or int(symb_value2[1]) < 0:
            print("Chybná práce s řetězcem", file=sys.stderr)
            exit(58)
        else:
            try:
                var_value[1] = symb_value1[1][int(symb_value2[1])]
            except IndexError:
                print("Chybná práce s řetězcem", file=sys.stderr)
                exit(58)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_setchar(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    if var_value[0] is None or symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    elif var_value[0] == symb_value2[0] == "string" and symb_value1[0] == "int":
        if var_value[1] is None or symb_value2[1] is None:
            print("Chybějící hodnota", file=sys.stderr)
            exit(58)
        elif len(var_value[1]) <= int(symb_value1[1]) or int(symb_value1[1]) < 0 or len(var_value[1]) == 0:
            exit(58)
        else:
            try:
                new_char = symb_value2[1][0]
                new_string = list(var_value[1])
                new_string[int(symb_value1[1])] = new_char
                new_string = "".join(new_string)
                var_value[1] = new_string
            except IndexError:
                print("Chybná práce s řetězcem", file=sys.stderr)
                exit(58)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def interpret_type(args):
    var_value = get_var_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')

    var_value[0] = "string"
    var_value[1] = symb_value1[0]


def interpret_jump(args, labels):
    label_value = get_label_value(args, 'arg1')
    return find_label(labels, label_value)


def interpret_jumpifeq(args, labels):
    label_value = get_label_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    new_order = find_label(labels, label_value)
    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    if label_eq_check(symb_value1, symb_value2):
        return new_order
    else:
        return None


def interpret_jumpifneq(args, labels):
    label_value = get_label_value(args, 'arg1')
    symb_value1 = get_symb_value(args, 'arg2')
    symb_value2 = get_symb_value(args, 'arg3')

    new_order = find_label(labels, label_value)
    if symb_value1[0] is None or symb_value2[0] is None:
        exit(56)
    if label_eq_check(symb_value1, symb_value2):
        return None
    else:
        return new_order


def interpret_exit(args):
    symb_value = get_symb_value(args, 'arg1')

    if symb_value[0] is None:
        exit(56)
    elif symb_value[0] == "int":
        if 0 <= int(symb_value[1]) <= 49:
            exit(int(symb_value[1]))
        else:
            print("Špatná hodnota operandů", file=sys.stderr)
            exit(57)
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def split_var_arg(args, arg_number):
    arg = args[arg_number][1]
    arg = re.split("@", arg)
    return arg[0], arg[1]


def get_symb_value(args, arg_number):

    if 'var' in args[arg_number]:
        temp = get_var_value(args, arg_number)
        value = [None, None]
        value[0] = temp[0]
        value[1] = temp[1]
        return value
    else:
        return args[arg_number]


# returns value of variable
def get_var_value(args, arg_number):
    frame, name = split_var_arg(args, arg_number)
    if frame == "GF":
        if name in global_frame:
            return global_frame[name]
        else:
            print("Přístup k neexistující proměnné", file=sys.stderr)
            exit(54)
    elif frame == "LF":
        if lf_pointer >= 0:
            if name in local_frame[lf_pointer]:
                return local_frame[lf_pointer][name]
            else:
                print("Přístup k neexistující proměnné", file=sys.stderr)
                exit(54)
        else:
            print("Rámec neexistuje", file=sys.stderr)
            exit(55)
    else:
        if temporary_frame is not None:
            if name in temporary_frame:
                return temporary_frame[name]
            else:
                print("Přístup k neexistující proměnné", file=sys.stderr)
                exit(54)
        else:
            print("Rámec neexistuje", file=sys.stderr)
            exit(55)


def get_label_value(args, arg_number):
    arg = args[arg_number][1]
    return arg


def get_type_value(args, arg_number):
    arg = args[arg_number][1]
    if arg == "int" or arg == "string" or arg == "bool":
        return arg
    else:
        print("Špatná hodnota operandů", file=sys.stderr)
        exit(57)


def check_ints(value1, value2):
    if value1 is None or value2 is None:
        exit(56)
    elif value1 != "int" or value2 != "int":
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


def get_value(value):
    if value == "false" or value == "False":
        return False
    else:
        return True


def find_label(labels, label_value):
    new_order = None
    for order in labels:
        if labels[order] == label_value:
            new_order = order
            break

    if new_order is None:
        print("Návěští nenalezeno", file=sys.stderr)
        exit(52)
    else:
        return new_order


def label_eq_check(symb_value1, symb_value2):
    if symb_value1[0] == symb_value2[0]:
        if symb_value1[0] == "int":
            return int(symb_value1[1]) == int(symb_value2[1])
        elif symb_value1[0] == "string":
            return symb_value1[1] == symb_value2[1]
        elif symb_value1[0] == "bool":
            value1 = get_value(symb_value1[1])
            value2 = get_value(symb_value2[1])
            return value1 == value2
        else:
            return True
    elif symb_value1[0] == "nil" or symb_value2[0] == "nil":
        return False
    else:
        print("Špatné typy operandů", file=sys.stderr)
        exit(53)


main()
