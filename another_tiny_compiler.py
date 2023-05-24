from typing import Any, Dict, List, Tuple

from pprint import pprint
import re


Token = Dict[str, str]
Ast = Dict[str, Any]
Code = List[str]


def tokenize(program_text: str) -> List[Token]:
    """
    Convert a string of program text into a list of tokens.

    Each token is a dictionary with a 'type' and 'value'. The 'type' can be
    'lparen', 'rparen', 'number', or 'name'. The 'value' is the actual string
    from the program text.

    Whitespace is ignored. Raises a ValueError if an invalid character is encountered.
    """

    token_seq = []  # The sequence of tokens extracted from the program text

    program_text_len = len(program_text)

    pos = 0  # The position in the program_text where the next token should be extracted from
    while pos < program_text_len:
        text = program_text[pos:]

        if (m := re.match(r'\s+', text)):
            eat = len(m.group(0))
        elif text[0] == '(':
            token_seq.append({
                'type': 'lparen',
                'value': '('
            })
            eat = 1
        elif text[0] == ')':
            token_seq.append({
                'type': 'rparen',
                'value': ')'
            })
            eat = 1
        elif (m := re.match(r"[0-9]+", text)):
            token_seq.append({
                'type': 'number',
                'value': m.group(0),
            })
            eat = len(m.group(0))
        elif (m := re.match(r"[A-Za-z]+", text)):
            token_seq.append({
                'type': 'name',
                'value': m.group(0),
            })
            eat = len(m.group(0))
        else:
            raise ValueError(f"Invalid char: {program_text[pos]}")

        pos += eat

    return token_seq


def parse(token_seq: List[Token]) -> Ast:
    """
    Convert a list of tokens into an Abstract Syntax Tree (AST).

    Each node in the AST is a dictionary with a 'type' and possibly other properties.
    The 'type' can be 'NumberLiteral' or 'CallExpression'. The 'value' or 'name' and 'params'
    properties are taken from the tokens.

    Raises a ValueError if an invalid token is encountered.
    """

    pos = 0  # The position of token that currently investigated

    def walk():
        """
        Recursively walk through the list of tokens and generate the corresponding AST.

        This function is called recursively to handle nested expressions.
        """

        nonlocal pos

        if pos >= len(token_seq):
            raise IndexError(f"Unexpected EOF")

        token = token_seq[pos]
        token_type = token['type']
        if token_type == 'number':
            # Generate a leaf node for the number
            pos += 1
            node = {
                'type': 'NumberLiteral',
                'value': token['value'],
            }
            return node
        elif token_type == 'lparen':
            # Generate a intermediate node for the function call
            pos += 1
            token = token_seq[pos]
            node = {
                'type': 'CallExpression',
                'name': token['value'],
                'params': [],
            }

            pos += 1
            token = token_seq[pos]
            while token['type'] != 'rparen':
                node['params'].append(walk())  # Node for the arguments goes `param` attribute of this node
                token = token_seq[pos]
            pos += 1

            return node
        else:
            raise ValueError(f"Invalid token at position {pos}: {repr(token)}")

    ast = walk()
    return ast, pos


def compile(node: Ast, used_vars: List[str]) -> Tuple[str, Code]:
    """
    Recursively compile an Abstract Syntax Tree (AST) node into code.

    This function is called recursively to handle nested expressions. The 'used_vars' argument is a list
    that keeps track of the names of the variables that are used in the code and need to be declared. 
    New variable names are appended to this list as they are used.

    Raises a ValueError if an invalid node is encountered.
    """

    node_type = node['type']
    if node_type == 'CallExpression':
        code = []  # The generated code for the node

        # Prepare a variable to store the return value of the function call
        ret_var = f"v{len(used_vars)}"
        used_vars.append(ret_var)

        # Generate code for each of the arguments
        args = []
        for param_node in node['params']:
            r, c = compile(param_node, used_vars)
            args.append(r)
            code.extend(c)

        # Generate code of calling the function for the given arguments
        node_name = node['name']
        code.append(f"{ret_var} = {node_name}({', '.join(args)});")
        return ret_var, code
    elif node_type == 'NumberLiteral':
        return node['value'], []
    else:
        raise ValueError(f"Invalid node: {repr(node)}")


def main():
    program_text = "(print (add (subtract 1 2) 3))"  # Source code of the program

    token_seq = tokenize(program_text)
    # pprint(token_seq)

    ast, _ = parse(token_seq)
    # pprint(ast)

    used_vars = []  # The names of the variables that are used in the code and need to be declared
    _, code = compile(ast, used_vars)
    code.insert(0, f"int {', '.join(used_vars)};")

    print('\n'.join(code))


if __name__ == '__main__':
    main()

