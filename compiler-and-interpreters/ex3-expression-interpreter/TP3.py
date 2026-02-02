
# reads a script file, validate and parses its lines so they can be processed
def SCRIPT(file_path):
    with open(file_path, "r") as file:
        lines = []
        
        
        for line in file.readlines():
            stripped = line.strip()
            if stripped:
                
                # semicolon check
                if not stripped.endswith(';'):
                    return 'Error: Line(s) did not end with ";"'
                # Remove semicolon
                stripped = stripped[:-1].strip()
                lines.append(stripped)

    parsed = []  # Stores parsed instructions
    LISTINSTR(lines, parsed)

    # Filters out lines that are empty
    cleaned = []
    for item in parsed:
        if item is not None:
            cleaned.append(item)

    return cleaned


# LISTINSTR processes each instruction and parses into an instruction
# If there's > 1 instrs. it will recursively call itself
def LISTINSTR(lines, parsed):
    
    if lines:
        parsed.append(INSTR(lines.pop(0)))
        LISTINSTR(lines, parsed)



symbol_table = {}  # symbol table 




# INSTR processes and execute each instruction
def INSTR(cmd):
    for ch in "()+=*":
        cmd = cmd.replace(ch, f" {ch} ")
    tokens = cmd.split()


    # Handle newline
    if tokens[0] == 'aff_ral' and tokens[1:] == []:
        return '\n'  # INSTR → aff_ral ;

    # all inst. must be of len >= 2 unless its a newline
    if len(tokens) >= 2:
        # Handle id = PD_AFF
        if tokens[1] == '=' and tokens[0][0].isalpha():  # INSTR → id = PD_AFF ;
            var = tokens[0]
            val = PDF_AFF(tokens[2:])
            
            if isinstance(val, (int, float)): 
                symbol_table[var] = val
                return None
            return 'Assigned value must be a float/int'

        # Handle display function
        if tokens[0] == 'afficher':  # INSTR → afficher E ;
            return E(tokens[1:])

    return 'Invalid instruction'


# PDF_AFF evaluates the expression
def PDF_AFF(tokens):
    if tokens[0] == 'inv':
        value = E(tokens[1:])
        if isinstance(value, str):
            return value  # in case of an error
        return 1 / value  # PDF_AFF → inv E
    return E(tokens)  # PDF_AFF → E


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
        if token.isalpha():
            return symbol_table.get(token, 'Undefined variable')  # F → id

        # numbers
        if token.lstrip('-').replace('.', '', 1).isdigit():
            return float(token)  # F → nb

    return 'Invalid instruction'


def display_results(results):
    # Displays results 
    if isinstance(results, str):  # Handle errors 
        print(results)
        return

    print("\n Execution Results:")
    for result in results:
        if result == "\n":
            print(result, end="")
        else:
            print(result)

    # Print symbol table 
    print("\n Table State:")
    for key, value in symbol_table.items():
        print(key + ": " + str(value))


# Get script file name 
file_name = input("Enter the script file name: ").strip()
results = SCRIPT(file_name)
display_results(results)
