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
    'STRING_LITERAL': r'"[^"]*"',  # NEW: String literals like "Hello World"
    'NUMBER': r'\b\d+\b',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'LBRACE': r'{',
    'RBRACE': r'}',
    'SEMICOLON': r';',
    'COMMA': r',',  # NEW: For multiple function arguments
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
# GUI code
# ========================

def run_compiler():
    # Get code from the text box
    code = code_input.get("1.0", tk.END)
    
    # Clear previous output
    output_box.delete("1.0", tk.END)
    
    # Run lexical analyzer
    tokens, lexical_error = lexical_analyzer(code)
    
    # Show tokens in the output box
    output_box.insert(tk.END, "Tokens:\n")
    for token_type, token_value in tokens:
        output_box.insert(tk.END, f"{token_type}: {token_value}\n")
    
    # Check for lexical errors first
    if lexical_error:
        output_box.insert(tk.END, "\n COMPILATION FAILED \n")
        output_box.insert(tk.END, "Lexical errors detected. Cannot proceed to syntax analysis.\n")
        messagebox.showerror("Compiler", "Compilation Failed!\nLexical errors found.")
        return  # Stop here - do not compile
    
    output_box.insert(tk.END, "\nLexical Analysis: PASSED\n")
    
    # Run syntax analyzer only if no lexical errors
    ok = syntax_analyzer(tokens)
    output_box.insert(tk.END, "\nSyntax Result:\n")
    
    if ok:
        output_box.insert(tk.END, "Syntax Analysis: PASSED\n")
        output_box.insert(tk.END, "\n COMPILATION SUCCESSFUL! \n")
        messagebox.showinfo("Compiler", "Compilation Successful!\nCode is valid.")
    else:
        output_box.insert(tk.END, "Syntax Analysis: FAILED\n")
        output_box.insert(tk.END, "\n COMPILATION FAILED \n")
        messagebox.showerror("Compiler", "Compilation Failed!\nSyntax errors found.")


# Create main window
root = tk.Tk()
root.title("Mini Compiler")

# Code input label + text box
label_input = tk.Label(root, text="Source Code:")
label_input.pack(anchor="w", padx=10, pady=(10, 0))

code_input = scrolledtext.ScrolledText(root, width=80, height=15)
code_input.pack(padx=10, pady=5)

# Put a default example in the box
code_input.insert(tk.END, 'int main()\n{\n    printf("Hello World");\n    return 0;\n}')

# Run button
run_button = tk.Button(root, text="Run Compiler", command=run_compiler)
run_button.pack(pady=5)

# Output label + text box
label_output = tk.Label(root, text="Output:")
label_output.pack(anchor="w", padx=10, pady=(10, 0))

output_box = scrolledtext.ScrolledText(root, width=80, height=15, state="normal")
output_box.pack(padx=10, pady=(0, 10))

# Start the GUI event loop
root.mainloop()
