import re
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ========================
# Compiler code
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

# Regex for all token types (order matters - string literals before identifiers)
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
        """Parse a statement (function call or return statement)."""
        current = self.get_current_token_type()
        
        if current == 'IDENTIFIER':
            # Function call: identifier(args);
            self.advance()  # consume identifier
            self.expect('LPAREN')
            self.parse_arguments()  # Parse function arguments
            self.expect('RPAREN')
            self.expect('SEMICOLON')
            print("  Syntax: Parsed function call statement")
        
        elif current == 'RETURN_KEYWORD':
            # Return statement: return value;
            self.expect('RETURN_KEYWORD')
            if self.get_current_token_type() == 'NUMBER':
                self.expect('NUMBER')
            self.expect('SEMICOLON')
            print("  Syntax: Parsed return statement")
        
        else:
            raise SyntaxError(f"Unexpected statement starting with '{current}'")
    
    def parse_arguments(self):
        """Parse function arguments (can be empty or multiple expressions)."""
        current = self.get_current_token_type()
        
        # Empty argument list
        if current == 'RPAREN':
            return
        
        # Parse first argument
        self.parse_expression()
        
        # Parse additional arguments separated by commas
        while self.get_current_token_type() == 'COMMA':
            self.expect('COMMA')
            self.parse_expression()
    
    def parse_expression(self):
        """Parse a simple expression (string literal or number)."""
        current = self.get_current_token_type()
        
        if current == 'STRING_LITERAL':
            self.expect('STRING_LITERAL')
            print("  Syntax: Parsed string literal expression")
        elif current == 'NUMBER':
            self.expect('NUMBER')
            print("  Syntax: Parsed number expression")
        elif current == 'IDENTIFIER':
            self.expect('IDENTIFIER')
            print("  Syntax: Parsed identifier expression")
        else:
            raise SyntaxError(f"Expected expression but got '{current}'")


def syntax_analyzer(tokens: list[tuple[str, str]]) -> bool:
    """FUNCTION 2: Syntax Analyzer (Parser). Validates token order."""
    print("\n--- Running Syntax Analyzer ---")
    parser = SimpleParser(tokens)
    
    try:
        # Expect: int main() { statements }
        parser.expect('INT_KEYWORD')
        parser.expect('IDENTIFIER')  # main
        parser.expect('LPAREN')
        parser.expect('RPAREN')
        parser.expect('LBRACE')
        
        # Parse zero or more statements inside the function body
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


# ========================
# GUI code (the "window")
# ========================

def run_compiler():
    # Get code from the text box
    code = code_input.get("1.0", tk.END)

    # Clear previous output
    output_box.delete("1.0", tk.END)

    # Run lexical analyzer
    tokens = lexical_analyzer(code)

    # Show tokens in the output box
    output_box.insert(tk.END, "Tokens:\n")
    for token_type, token_value in tokens:
        output_box.insert(tk.END, f"{token_type}: {token_value}\n")

    # Run syntax analyzer
    ok = syntax_analyzer(tokens)

    output_box.insert(tk.END, "\nSyntax Result:\n")
    if ok:
        output_box.insert(tk.END, "Syntax Analysis Successful! ✅\n")
        messagebox.showinfo("Compiler", "Syntax Analysis Successful!")
    else:
        output_box.insert(tk.END, "Syntax Analysis Failed. ❌\n(See console for details.)\n")
        messagebox.showerror("Compiler", "Syntax Analysis Failed.\nCheck console for details.")

# Create main window
root = tk.Tk()
root.title("Mini Compiler")
root.geometry('1000x680')
root.minsize(760, 520)

# Use a modern ttk theme and define some simple colors for a dark editor style
style = ttk.Style(root)
try:
    style.theme_use('clam')
except Exception:
    pass

# Fonts
mono_font = font.Font(family='Consolas' if 'Consolas' in font.families() else 'Courier', size=11)
heading_font = font.Font(family='Playfair', size=14) if 'Playfair' in font.families() else font.Font(size=13, weight='bold')

# Main layout frame
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main = ttk.Frame(root, padding=(14, 12, 14, 12))
main.grid(row=0, column=0, sticky='nsew')
main.columnconfigure(0, weight=1)
main.columnconfigure(1, weight=1)
main.rowconfigure(0, weight=1)

# Left column: Source code
left = ttk.Frame(main)
left.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=(0, 10))
left.columnconfigure(0, weight=1)
left.rowconfigure(1, weight=1)

lbl_src = ttk.Label(left, text='Source Code', font=heading_font)
lbl_src.grid(row=0, column=0, sticky='w')

code_input = scrolledtext.ScrolledText(left, wrap=tk.NONE, font=mono_font, width=60, height=18)
code_input.grid(row=1, column=0, sticky='nsew', pady=(6, 0))
code_input.configure(background='#0b1220', foreground='#e6eef6', insertbackground='#e6eef6', relief='flat', borderwidth=0)

code_input.insert(tk.END, 'int main() { return 0; }')

# Right column: Output / tokens
right = ttk.Frame(main)
right.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=(0, 10))
right.columnconfigure(0, weight=1)
right.rowconfigure(1, weight=1)

lbl_out = ttk.Label(right, text='Output', font=heading_font)
lbl_out.grid(row=0, column=0, sticky='w')

output_box = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=mono_font, width=60, height=18, state='normal')
output_box.grid(row=1, column=0, sticky='nsew', pady=(6, 0))
output_box.configure(background='#0b1220', foreground='#e6eef6', insertbackground='#e6eef6', relief='flat', borderwidth=0)

# Bottom controls
controls = ttk.Frame(main)
controls.grid(row=1, column=0, columnspan=2, sticky='ew')
controls.columnconfigure(0, weight=1)
controls.columnconfigure(1, weight=0)

# Add a run button on the right and a small status label on the left
status_label = ttk.Label(controls, text='Ready', anchor='w')
status_label.grid(row=0, column=0, sticky='ew', padx=(2, 8), pady=(10, 0))

run_button = ttk.Button(controls, text='Run Compiler', command=run_compiler)
run_button.grid(row=0, column=1, sticky='e', padx=(8, 0), pady=(10, 0))

# Keyboard shortcut: Ctrl+Return to run
root.bind('<Control-Return>', lambda e: run_compiler())

# Make the UI resize nicely
for w in (code_input, output_box):
    w.configure(font=mono_font)

# Start the GUI event loop
root.mainloop()
