# C Code Doctor

A command-line tool that detects programming errors in C code and explains them in plain English, with a suggested fix for each one.

C Code Doctor wraps the GCC compiler. It runs a syntax-only check on the code you paste in, parses GCC's diagnostics, and translates the cryptic compiler messages into clear explanations and corrections.

## Features

- Paste or type C code directly in the terminal
- Detects errors and warnings using GCC (`-std=c11 -Wall -Wextra -pedantic`)
- Reports the exact line, column and severity of every issue
- Explains common errors and suggests a correction
- Safe to run: the code is only syntax-checked (`-fsyntax-only`), never executed, and is written to a temporary file that is deleted afterwards
- 15-second timeout so the tool never hangs
- Checks that GCC is installed and tells you if it is not

## Requirements

- Python 3.8 or newer
- GCC available in your `PATH`

Check your setup:

```bash
python --version
gcc --version
```

Installing GCC:

| OS | Command |
|----|---------|
| Ubuntu / Debian | `sudo apt install gcc` |
| macOS | `xcode-select --install` |
| Windows | Install [MinGW-w64](https://www.mingw-w64.org/) or MSYS2, then add its `bin` folder to `PATH` |

No third-party Python packages are needed. The tool uses only the standard library (`re`, `shutil`, `subprocess`, `tempfile`, `pathlib`).

## Usage

Save the script (for example as `c_code_doctor.py`) and run:

```bash
python c_code_doctor.py
```

Then:

1. Paste or type your C code.
2. Type `END` on a separate line to analyze it.
3. Type `EXIT` on the first line to quit.

### Example

Input:

```c
#include <stdio.h>

int main(void) {
    printf("Hello")
    return 0;
}
```

Output:

```text
=======================================================
          C CODE ERROR DETECTOR
=======================================================

[FAILED] Found 1 compilation error(s).

-------------------------------------------------------
1. ERROR | Line 5, Column 18
Message: expected ';' before 'return'
Explanation: A semicolon may be missing.
Suggestion: Add ; at the end of the previous statement.

Analysis complete.
```

The exact line and column come from GCC, so they may differ slightly from the example.

## How It Works

```text
Paste C code
     |
     v
Save to temporary input.c
     |
     v
Run gcc -fsyntax-only -Wall -Wextra -pedantic
     |
     v
Parse stderr with a regex (line, column, severity, message)
     |
     v
Errors found? --No--> [SUCCESS] No compilation errors found.
     |
    Yes
     v
explain_error() matches the message against a rule table
     |
     v
Print explanation and suggestion, then wait for the next input
```

## Project Structure

| Function | Purpose |
|----------|---------|
| `main()` | Interactive loop: reads input until `END`, handles `EXIT` and empty input |
| `analyze_code(code)` | Writes the temp file, runs GCC, parses diagnostics and prints the report |
| `explain_error(message)` | Matches an error message against regex rules and returns an explanation and suggestion |

## Supported Error Explanations

| Pattern in GCC message | Explanation given |
|------------------------|-------------------|
| `expected ';' before ...` | A semicolon may be missing |
| `expected ')'` | A closing parenthesis may be missing |
| `expected '}'` | A closing brace may be missing |
| `undeclared` / `was not declared` | A variable or identifier has not been declared |
| `expected expression before` | An expression is incomplete or incorrectly written |
| `too few arguments` / `too many arguments` | A function call has the wrong number of arguments |

Any other error gets a generic hint to inspect the reported line and the lines just before it. Warnings are reported with a suggestion to review them.

## Limitations

- Only syntax-level checks: runtime and logic errors are not detected
- Explanations are rule-based, so only the six patterns above get specific advice
- The semicolon rule matches `expected ';' before ...` but not GCC's `expected ',' or ';' before ...` variant, which falls back to the generic hint
- Requires GCC to be installed locally
- Command-line interface only

## Future Improvements

- LLM-powered, context-aware explanations
- Automatic application of suggested fixes
- Web or GUI front end with highlighted error lines
- Support for more languages (C++, Java, Python)
- Static analysis and sanitizers for logic and runtime bugs
- A larger rule base covering more GCC messages

## License

Add your preferred license here (for example MIT).
