import math

# Code is overall the same as TP3, with a few changes mainly in the first 3 functions.


symbol_table = {}
# reads a script file, validate and parses its lines so they can be processed
def SCRIPT(file_path):
    with open(file_path, "r") as file:

        lines = []
        for line in file.readlines():
            stripped = line.strip()
            if not stripped:
                continue

            # serves to recognize end of loop.
            if stripped == '}' :
                lines.append(stripped)
                continue

            # this statement serves to recognize loops, an exception to the semicolon "rule"
            if stripped.startswith('boucle') and stripped.endswith('{'):
                lines.append(stripped)
            elif stripped.endswith(';'):
                # Remove semicolon
                lines.append(stripped[:-1].strip())
            else:
                return 'Error: Line(s) did not end with ";"'

    parsed = []
    LISTINSTR(lines, parsed)

    # Filters out lines that are empty
    cleaned = []
    for item in parsed:
        if item is not None:
            cleaned.append(item)

    return cleaned


def LISTINSTR(lines, parsed):
    if not lines:
        return parsed

    next_line = lines.pop(0)

    if next_line == '}':
        return parsed # 

    instr_res = INSTR(next_line, lines)
    if isinstance(instr_res, str) and instr_res.startswith("Error"):
        return instr_res # serves to propagate the error in the recursion
    
   # this section handles multiple instructions e.g loops.
   # (because in the descending recursion, INSTR → boucle nb { LISTINSTR } )
    if isinstance(instr_res, list):
        for item in instr_res:
            parsed.append(item)
    else:
        parsed.append(instr_res)

    return LISTINSTR(lines, parsed)


def INSTR(cmd, lines):
    for ch in "()+=*":
        cmd = cmd.replace(ch, f" {ch} ")
    tokens = cmd.split()


    # INSTR → aff_ral
    if tokens[0] == 'aff_ral':
        return '\n'

    # INSTR → boucle nb { LISTINSTR }
    if tokens[0] == 'boucle':
        if len(tokens) != 3 or not tokens[1].isdigit() or tokens[-1] != '{':
            return "Error: Incorrect boucle syntax. Expected format: 'boucle nb {'"
        n_loop = int(tokens[1])

        # here, we collect the instructions inside the loop
        loop_instr = []
        while lines:
            curr_line = lines[0].strip()
            if curr_line == '}':
                lines.pop(0) 
                break
            loop_instr.append(lines.pop(0))

        # the purpose of this section is to re-execute the same instructions within the loop(for n_loop time) 
        results = []
        for _ in range(n_loop):
            parsed_instructions = []
            result = LISTINSTR(loop_instr.copy(), parsed_instructions)
            
            if isinstance(result, str):
                return result
            
            for i in parsed_instructions:
                results.append(i)

        return results


   # INSTR → id = PD_AFF ; same logic as last tp3 
    if len(tokens) >= 2 and tokens[1] == '=' and tokens[0][0].isalpha():
        var = tokens[0]
        val = PDF_AFF(tokens[2:])
            
        if isinstance(val, (int, float)): 
            symbol_table[var] = val
            return None
        return 'Assigned value must be a float/int'

    # INSTR → afficher E
    if tokens[0] == 'afficher':
        return E(tokens[1:])


    return "Error: Invalid instruction"




# PDF_AFF evaluates the expression
# the same logic as last tp, but with root
def PDF_AFF(tokens):
    if tokens[0] == 'inv':
        value = E(tokens[1:])
        if isinstance(value, str):
            return value
        return 1 / value
    elif tokens[0] == 'racine':
        value = E(tokens[1:])
        if isinstance(value, str):
            return value
        return math.sqrt(value)
    else:
        return E(tokens)


# E handles expressions with +
def E(tokens):
    in_prts = False  # parentesis tracking
    for i in range(len(tokens)):
        if tokens[i] == '(':
            in_prts = True
        elif tokens[i] == ')':
            in_prts = False
        elif tokens[i] == '+' and not in_prts:
            # Split T and D in case of + encounter and check for type coherence on both sides.
            # This follows the standard recursive descent parsing approach seen in class
            t = T(tokens[:i])
            if isinstance(t, str):
                return t

            d = D(tokens[i:])
            if isinstance(d, str):
                return d

            return t + d  # E → T D

    return T(tokens)  # E → T

# D handles + operator
def D(tokens):
    if tokens[0] == '+':
        return E(tokens[1:])  # D → + E
    return 0  # D → ε

# T handles * operator
def T(tokens):
    parens = 0  
    for i in range(len(tokens)):
        if tokens[i] == '(':
            parens += 1
        elif tokens[i] == ')':
            parens -= 1
        elif tokens[i] == '*' and parens == 0:
            # same logic as E
            f = F(tokens[:i])
            if isinstance(f, str):
                return f

            g = G(tokens[i:])
            if isinstance(g, str):
                return g

            return f * g  # T → FG

    return F(tokens)  # T → F

# G handles * operator 
def G(tokens):
    if tokens[0] == '*':
        return T(tokens[1:])  # G → * T
    return 1  # G → ε

# F evaluates numbers(terminal), variables(terminal) and parentheses.
def F(tokens):
    if not tokens:
        return 'Invalid instruction'

    # Parentheses handling 
    if tokens[0][0] == '(' and tokens[-1][-1] == ')':
        return E(tokens[1:-1])  # F → ( E )
    
    # var handling
    if len(tokens) == 1:
        token = tokens[0]
         # Check if token is a used variable
        if token in symbol_table:
            return symbol_table[token]  # F → id

        # numbers
        if token.lstrip('-').replace('.', '', 1).isdigit():
            return float(token)  # F → nb

    return 'Invalid instruction'

def display_results(results):
    if isinstance(results, str):
        # error
        print(results)
        return

    print("\nExecution Results:")
    for result in results:
        if result == "\n":
            print(result, end="")
        else:
            print(result)



file_name = input("Enter the script file name: ").strip()
results = SCRIPT(file_name)
display_results(results)
