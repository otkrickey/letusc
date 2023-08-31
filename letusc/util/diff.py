import difflib


def diff_texts(text1, text2) -> list[str]:
    d = difflib.Differ()
    diff = list(d.compare(text1.splitlines(), text2.splitlines()))

    # GitHubのDiff表示にフォーマット
    formatted_diff = []
    line_number_1 = 1
    line_number_2 = 1

    for line in diff:
        if line.startswith("  "):
            formatted_diff.append(f"~{line_number_1:02} {line[2:]}")
            line_number_1 += 1
            line_number_2 += 1
        elif line.startswith("- "):
            formatted_diff.append(f"-{line_number_1:02} {line[2:]}")
            line_number_1 += 1
        elif line.startswith("+ "):
            formatted_diff.append(f"+{line_number_2:02} {line[2:]}")
            line_number_2 += 1

    return formatted_diff
