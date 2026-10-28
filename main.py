
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def explain_error(message):
    rules = [
        (
            r"expected .?;.* before",
            "A semicolon may be missing.",
            "Add ; at the end of the previous statement."
        ),
        (
            r"expected '\)'",
            "A closing parenthesis may be missing.",
            "Check the matching opening and closing parentheses."
        ),
        (
            r"expected '\}'",
            "A closing brace may be missing.",
            "Add } to close the appropriate block."
        ),
        (
            r"undeclared|was not declared",
            "A variable or identifier has not been declared.",
            "Declare the variable before using it and check its spelling."
        ),
        (
            r"expected expression before",
            "An expression is incomplete or incorrectly written.",
            "Check for missing operands or extra operators."
        ),
        (
            r"too few arguments|too many arguments",
            "The function call has an incorrect number of arguments.",
            "Compare the function call with its declaration."
        ),
    ]

    for pattern, explanation, suggestion in rules:
        if re.search(pattern, message, re.IGNORECASE):
            return explanation, suggestion

    return (
        "GCC found a compilation issue.",
        "Inspect the reported line and the lines immediately before it."
    )


def analyze_code(code):
    gcc = shutil.which("gcc")

    if gcc is None:
        print("\n[ERROR] GCC is not installed or not in PATH.")
        print("Check GCC installation with: gcc --version")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "input.c"
        source.write_text(code, encoding="utf-8")

        try:
            result = subprocess.run(
                [
                    gcc,
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-pedantic",
                    "-fsyntax-only",
                    str(source)
                ],
                capture_output=True,
                text=True,
                errors="replace",
                timeout=15,
                check=False
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            print(f"\n[ERROR] Could not complete analysis: {error}")
            return

        output = result.stderr.strip()

        pattern = re.compile(
            r"input\.c:(\d+):(\d+):\s*"
            r"(fatal error|error|warning|note):\s*(.*)"
        )

        diagnostics = []

        for line in output.splitlines():
            match = pattern.search(line)

            if match:
                line_no, column, severity, message = match.groups()
                diagnostics.append(
                    (int(line_no), int(column), severity, message)
                )

        errors = [
            item for item in diagnostics
            if item[2] in ("error", "fatal error")
        ]

        print("\n" + "=" * 55)
        print("          C CODE ERROR DETECTOR")
        print("=" * 55)

        if result.returncode == 0:
            print("\n[SUCCESS] No compilation errors found.")
        elif errors:
            print(f"\n[FAILED] Found {len(errors)} compilation error(s).")
        else:
            print("\n[FAILED] GCC could not compile the source.")
            if output:
                print(output)

        for index, (line_no, col, severity, message) in enumerate(
            diagnostics, start=1
        ):
            print("\n" + "-" * 55)
            print(
                f"{index}. {severity.upper()} "
                f"| Line {line_no}, Column {col}"
            )
            print(f"Message: {message}")

            if severity in ("error", "fatal error"):
                explanation, suggestion = explain_error(message)
                print(f"Explanation: {explanation}")
                print(f"Suggestion: {suggestion}")
            elif severity == "warning":
                print("Suggestion: Review this warning.")

        if output and not diagnostics:
            print("\nFull compiler output:")
            print(output)

        print("\nAnalysis complete.")


def main():
    while True:
        print("\n" + "=" * 55)
        print("C CODE DOCTOR")
        print("Paste or type C code below.")
        print("Type END on a separate line to analyze.")
        print("Type EXIT on the first line to quit.")
        print("=" * 55)

        lines = []

        while True:
            try:
                line = input()
            except EOFError:
                return

            if not lines and line.strip().upper() == "EXIT":
                print("Goodbye!")
                return

            if line.strip() == "END":
                break

            lines.append(line)

        code = "\n".join(lines)

        if not code.strip():
            print("No code entered. Try again.")
            continue

        analyze_code(code)


if __name__ == "__main__":
    main()
