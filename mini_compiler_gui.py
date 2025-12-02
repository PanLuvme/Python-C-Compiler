import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, font

# ========================
# 1. Compiler Logic (Lexer & Parser)
# ========================

TOKEN_TYPES = {
    'INT_KEYWORD': r'\bint\b',
    'RETURN_KEYWORD': r'\breturn\b',
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    'STRING_LITERAL': r'"[^"]*"',
    'NUMBER': r'\b\d+\b',
    'PLUS': r'\+',        
    'MINUS': r'-',        
    'EQUALS': r'=',       
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'LBRACE': r'{',
    'RBRACE': r'}',
    'SEMICOLON': r';',
    'COMMA': r',',
    'WHITESPACE': r'\s+',
    'UNKNOWN': r'.',
}

# Regex for all token types
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES.items())

def lexical_analyzer(code: str) -> tuple[list[tuple[str, str]], bool]:
    """FUNCTION 1: Lexical Analyzer (Lexer). Breaks code into tokens."""
    print("--- Running Lexical Analyzer ---")
    tokens = []
    has_error = False
    
    for match in re.finditer(token_regex, code):
        token_type = match.lastgroup
        token_value = match.group()
        
        if token_type == 'WHITESPACE':
            continue
        elif token_type == 'UNKNOWN':
            print(f"Lexical Error: Unknown character '{token_value}'")
            has_error = True
            continue
        
        tokens.append((token_type, token_value))
    
    print(f"Found {len(tokens)} tokens.")
    return tokens, has_error


class SimpleParser:
    """Helper class to manage parsing state."""
    
    def __init__(self, tokens: list[tuple[str, str]]):
        self.tokens = tokens
        self.current_token_index = 0
    
    def get_current_token_type(self):
        """Gets the current token's type, or None if at end."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index][0]
        return None
    
    def advance(self):
        """Move to the next token."""
        self.current_token_index += 1
    
    def expect(self, expected_type: str):
        """Consumes the current token if it matches, else raises SyntaxError."""
        current_type = self.get_current_token_type()
        if current_type == expected_type:
            print(f"  Syntax: Matched '{expected_type}'")
            self.advance()
        else:
            raise SyntaxError(
                f"Expected token type '{expected_type}' but got '{current_type}'"
            )
    
    def parse_statement(self):
        """Parse a statement (Variables, Return, Calls, Assignments)."""
        current = self.get_current_token_type()
        
        # --- 1. Variable Declaration (int x = 5;) ---
        if current == 'INT_KEYWORD':
            self.advance()  # consume 'int'
            self.expect('IDENTIFIER') # variable name
            
            # Check for initialization (= 5)
            if self.get_current_token_type() == 'EQUALS':
                self.advance() # consume '='
                self.parse_expression() # parse value
            
            self.expect('SEMICOLON')
            print("  Syntax: Parsed variable declaration")

        # --- 2. Return Statement (return 5;) ---
        elif current == 'RETURN_KEYWORD':
            self.advance()
            # Parse expression unless it's immediately a semicolon
            if self.get_current_token_type() != 'SEMICOLON':
                self.parse_expression()
            self.expect('SEMICOLON')
            print("  Syntax: Parsed return statement")

        # --- 3. Identifier Start (Assignment OR Function Call) ---
        elif current == 'IDENTIFIER':
            self.advance() # consume the identifier name
            
            # Check what comes next
            next_token = self.get_current_token_type()

            if next_token == 'LPAREN':
                # Function Call: name(...)
                self.advance() # consume '('
                self.parse_arguments()
                self.expect('RPAREN')
                self.expect('SEMICOLON')
                print("  Syntax: Parsed function call")

            elif next_token == 'EQUALS':
                # Assignment: name = ...
                self.advance() # consume '='
                self.parse_expression()
                self.expect('SEMICOLON')
                print("  Syntax: Parsed assignment")
                
            else:
                raise SyntaxError(f"Expected '(' or '=' after identifier, got '{next_token}'")
        
        else:
            raise SyntaxError(f"Unexpected statement starting with '{current}'")
    
    def parse_arguments(self):
        """Parse function arguments."""
        if self.get_current_token_type() == 'RPAREN':
            return
        
        self.parse_expression()
        while self.get_current_token_type() == 'COMMA':
            self.expect('COMMA')
            self.parse_expression()
    
    def parse_expression(self):
        """Parse expressions with Math support (left-to-right)."""
        # Parse the left-hand side
        self.parse_term()

        # Check for operators (+ or -)
        while self.get_current_token_type() in ['PLUS', 'MINUS']:
            op = self.get_current_token_type()
            self.advance() # consume operator
            print(f"  Syntax: Found operator '{op}'")
            self.parse_term() # Parse the right-hand side

    def parse_term(self):
        """Helper to parse a single unit (Number, String, or Variable)."""
        current = self.get_current_token_type()

        if current == 'NUMBER':
            self.expect('NUMBER')
        elif current == 'IDENTIFIER':
            self.expect('IDENTIFIER')
        elif current == 'STRING_LITERAL':
            self.expect('STRING_LITERAL')
        else:
            raise SyntaxError(f"Expected number or identifier, got '{current}'")


def syntax_analyzer(tokens: list[tuple[str, str]]) -> bool:
    """FUNCTION 2: Syntax Analyzer (Parser)."""
    print("\n--- Running Syntax Analyzer ---")
    parser = SimpleParser(tokens)
    
    try:
        # Expect: int main() { statements }
        parser.expect('INT_KEYWORD')
        parser.expect('IDENTIFIER')  # main
        parser.expect('LPAREN')
        parser.expect('RPAREN')
        parser.expect('LBRACE')
        
        # Parse statements until closing brace
        while parser.get_current_token_type() not in ['RBRACE', None]:
            parser.parse_statement()
        
        parser.expect('RBRACE')
        
        if parser.get_current_token_type() is not None:
            raise SyntaxError("Unexpected tokens at end of file.")
        
        print("Syntax Analysis Successful!")
        return True
    
    except SyntaxError as e:
        print(f"Syntax Analysis Failed: {e}")
        return False

def evaluate(tokens: list[tuple[str, str]]) -> str:
    """Simple interpreter: evaluates variable declarations, assignments,
    and printf() calls with numeric or string expressions."""
    
    symbols = {}    # variable storage
    output = []     # printed output lines
    
    # Simple expression evaluator (handles + and - only)
    def eval_expression(i):
        """Evaluate NUMBER or IDENTIFIER with + or -."""
        def get_value(tok):
            ttype, tval = tok
            if ttype == "NUMBER":
                return int(tval)
            if ttype == "STRING_LITERAL":
                return tval.strip('"')
            if ttype == "IDENTIFIER":
                return symbols.get(tval, 0)
            raise ValueError("Bad expression")
        
        value = get_value(tokens[i])
        i += 1
        
        while i < len(tokens) and tokens[i][0] in ("PLUS", "MINUS"):
            op = tokens[i][0]
            right = get_value(tokens[i+1])
            
            if op == "PLUS":
                value = value + right
            elif op == "MINUS":
                value = value - right
            
            i += 2
        
        return value
    
    i = 0
    while i < len(tokens):
        ttype, tval = tokens[i]
        
        # int x;
        if ttype == "INT_KEYWORD":
            name = tokens[i+1][1]
            symbols[name] = 0
            i += 3
            continue
        
        # int x = expr;
        if ttype == "INT_KEYWORD" and tokens[i+2][0] == "EQUALS":
            name = tokens[i+1][1]
            value = eval_expression(i+3)
            symbols[name] = value
            i += 5
            continue
        
        # x = expr;
        if ttype == "IDENTIFIER" and tokens[i+1][0] == "EQUALS":
            name = tval
            value = eval_expression(i+2)
            symbols[name] = value
            i += 4
            continue
        
        # printf(expr);
        if ttype == "IDENTIFIER" and tval == "printf":
            value = eval_expression(i+2)
            output.append(str(value))
            
            # skip until semicolon
            while tokens[i][0] != "SEMICOLON":
                i += 1
            i += 1
            continue
        
        i += 1
    
    return "\n".join(output)


# ========================
# 2. GUI Code (Updated)
# ========================

def run_compiler():
    # Get code from the text box
    code = code_input.get("1.0", tk.END)

    # Clear previous output
    output_box.delete("1.0", tk.END)

    # Run lexical analyzer
    # FIX: Unpack the tuple (tokens, error)
    tokens, lex_error = lexical_analyzer(code)

    # Show tokens in the output box
    output_box.insert(tk.END, "Tokens:\n")
    for token_type, token_value in tokens:
        output_box.insert(tk.END, f"{token_type}: {token_value}\n")

    if lex_error:
        output_box.insert(tk.END, "\n❌ Lexical Error Detected. Stopping.\n")
        return

        # Run syntax analyzer
    ok = syntax_analyzer(tokens)

    output_box.insert(tk.END, "\nSyntax Result:\n")
    if ok:
        output_box.insert(tk.END, "Syntax Analysis Successful! ✅\n")

        # NEW — evaluate program and print results
        result = evaluate(tokens)
        if result:
            output_box.insert(tk.END, "\nProgram Output:\n")
            output_box.insert(tk.END, result + "\n")
        else:
            output_box.insert(tk.END, "\nProgram Output:\n(No output)\n")

        messagebox.showinfo("Compiler", "Compilation complete.")
    else:
        output_box.insert(tk.END, "Syntax Analysis Failed. ❌\n(See console for details.)\n")
        messagebox.showerror("Compiler", "Compiler error.")


# Create main window
root = tk.Tk()
root.title("Mini Compiler")
root.geometry('1000x680')
root.minsize(760, 520)

# Styles
style = ttk.Style(root)
try:
    style.theme_use('clam')
except Exception:
    pass

# Fonts
mono_font = font.Font(family='Consolas' if 'Consolas' in font.families() else 'Courier', size=11)
heading_font = font.Font(family='Playfair', size=14) if 'Playfair' in font.families() else font.Font(size=13, weight='bold')

# Layout
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main = ttk.Frame(root, padding=(14, 12, 14, 12))
main.grid(row=0, column=0, sticky='nsew')
main.columnconfigure(0, weight=1)
main.columnconfigure(1, weight=1)
main.rowconfigure(0, weight=1)

# Left column
left = ttk.Frame(main)
left.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=(0, 10))
left.columnconfigure(0, weight=1)
left.rowconfigure(1, weight=1)

lbl_src = ttk.Label(left, text='Source Code', font=heading_font)
lbl_src.grid(row=0, column=0, sticky='w')

code_input = scrolledtext.ScrolledText(left, wrap=tk.NONE, font=mono_font, width=60, height=18)
code_input.grid(row=1, column=0, sticky='nsew', pady=(6, 0))
code_input.configure(background='#0b1220', foreground='#e6eef6', insertbackground='#e6eef6', relief='flat', borderwidth=0)

# Default Code Example
default_code = """int main() {
    int x = 10;
    int y;
    y = x + 5;
    return 0;
}"""
code_input.insert(tk.END, default_code)

# Right column
right = ttk.Frame(main)
right.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=(0, 10))
right.columnconfigure(0, weight=1)
right.rowconfigure(1, weight=1)

lbl_out = ttk.Label(right, text='Output', font=heading_font)
lbl_out.grid(row=0, column=0, sticky='w')

output_box = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=mono_font, width=60, height=18, state='normal')
output_box.grid(row=1, column=0, sticky='nsew', pady=(6, 0))
output_box.configure(background='#0b1220', foreground='#e6eef6', insertbackground='#e6eef6', relief='flat', borderwidth=0)

# Controls
controls = ttk.Frame(main)
controls.grid(row=1, column=0, columnspan=2, sticky='ew')
controls.columnconfigure(0, weight=1)
controls.columnconfigure(1, weight=0)

status_label = ttk.Label(controls, text='Ready', anchor='w')
status_label.grid(row=0, column=0, sticky='ew', padx=(2, 8), pady=(10, 0))

run_button = ttk.Button(controls, text='Run Compiler', command=run_compiler)
run_button.grid(row=0, column=1, sticky='e', padx=(8, 0), pady=(10, 0))

root.bind('<Control-Return>', lambda e: run_compiler())

root.mainloop()
