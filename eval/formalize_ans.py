import re
import os
import json
import sympy
from fractions import Fraction
from sympy import sympify, latex, S
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.latex import parse_latex
from latex2sympy2 import latex2sympy
from sympy.parsing.latex import parse_latex
from collections import defaultdict, Counter
from tqdm import tqdm
from func_timeout import func_timeout
# from latex2sympy2 import latex2sympy

def identify_corner_cases(answer):
    answer = answer.strip()
    
    # Check for yes/no
    if answer.lower() in ['yes', 'no', 'true', 'false']:
        return 'yes_no'
    
    # Check for phrases indicating 'no solution'
    if answer.lower() in ['no solution', 'no solutions', 'no answer', 'does not exist', 'no such n', 'no such function', 'no such f exists.', 'no angles', 'no bounded function', 'no solution for this equation', 'no']:
        return 'no_solution'

    # Check for 'infinite' or 'infinity'
    if answer.lower() in ['infinite', '\\infty', 'inf', 'infinity', 'infinitely many', 'diverge', 'diverges', 'divergent']:
        return 'infinite'

    # Check for number with unit or currency (e.g., '112 slices', '14.34$', '67.833654°')
    if re.match(r'^-?\d+(\.\d+)?\s*[a-zA-Z%°$]+', answer):
        return 'number_with_unit'
    
    # Check for numbers with commas (e.g., '20,250,001')
    if re.match(r'^-?\d{1,3}(,\d{3})*(\.\d+)?$', answer):
        return 'number_with_commas'
    
    # Check for ratios (e.g., '2:1', '3 : 2', '9:5', '1:5000000')
    if re.match(r'^\d+\s*:\s*\d+$', answer):
        return 'ratio'

    # Check for expressions with variables or exponents (e.g., '1002^2', '2^{2024}', 'n!')
    if re.search(r'[a-zA-Z_\\]', answer) and re.search(r'\^|!|\\', answer):
        return 'expression'

    # Check for fraction in LaTeX format or without backslashes (e.g., '$\\dfrac{5}{12}$', 'sqrt{71}')
    if re.search(r'(\\frac|\\dfrac|\\tfrac)\{.*?\}\{.*?\}', answer) or re.search(r'^\d+/\d+$', answer):
        return 'fraction'

    # Check for missing backslashes in functions (e.g., 'sqrt{71}', 'tan1')
    if re.search(r'^(sqrt|tan|cos|sin|ln|log)\s*\{?.*?\}?$', answer):
        return 'expression'

    # Check for mathematical constants (e.g., 'e', 'pi')
    if answer.strip() in ['e', '\\pi']:
        return 'constant'

    # Check for list of numbers or variables separated by commas
    if ',' in answer:
        items = split_items(answer)
        if all(re.match(r'^-?\d+(\.\d+)?$', item.strip()) or re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', item.strip()) for item in items):
            return 'list'

    # Check for single variable (e.g., 'p', 't', 'x', 'n')
    if re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', answer):
        return 'variable'

    # Check for phrases or words
    if re.fullmatch(r'[A-Za-z\s,.\-!?]+', answer):
        return 'phrase'

    # Check for numbers
    if re.match(r'^-?\d+(\.\d+)?$', answer):
        return 'number'

    # Default to string
    return 'string'

def identify_answer_type(answer):
    answer = answer.strip()
    # remove leading and trailing $
    while answer.startswith('$'):
        answer = answer[1:].strip()
    while answer.endswith('$'):
        answer = answer[:-1].strip()

    # Check for yes/no
    if answer.lower() in ['yes', 'no']:
        return 'yes_no'
    
    # make sure is [] instead of [],[]
    if ((answer.startswith('[') and answer.endswith(']')) or (answer.startswith('{') and answer.endswith('}'))) and split_items(answer)[0] == answer:
        return 'set_list'
    
    # make sure is () instead of (),()
    if answer.startswith('(') and answer.endswith(')') and split_items(answer)[0] == answer:
        return 'tuple'

    if any(op in answer for op in ['=', '≥', '≤', '\\ge', '\\le', '>', '<']) and len(split_items(answer)) == 1:        
        return 'equation'

    # Check for list at the top level
    if (',' in answer or ';' in answer) and len(split_items(answer)) > 1:
        return 'list'

    if re.fullmatch(r'-?\d+', answer):
        return 'integer'

    if re.fullmatch(r'-?\d+/\d+', answer) or re.search(r'\\frac\{.*?\}\{.*?\}', answer):
        return 'fraction'

    if re.fullmatch(r'-?\d+\.\d+', answer):
        return 'decimal'

    if 'pi' in answer or '\\sqrt' in answer or '√' in answer:
        return 'irrational'

    if re.search(r'[a-zA-Z]', answer) and re.search(r'[\+\-\*/^]', answer):
        return 'expression'


    return identify_corner_cases(answer)

def split_items_robust(answer):
    if split_items(answer)[0] == answer:
        if not (answer[0] in '([{' and answer[-1] in ')]}'):
            raise Exception('Invalid set or list format')
        answer = answer[1:-1]
    return split_items(answer)

def split_items(answer):
    items = []
    current = ''
    depth = 0
    for i, char in enumerate(answer):
        if char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
        if (char == ',' or char == ';') and depth == 0:
            items.append(current.strip())
            current = ''
        else:
            current += char
    if current:
        items.append(current.strip())
    return items

def correct_latex_symbols(answer):
    # Replace inequality symbols with LaTeX commands
    answer = answer.replace('≥', '\\ge ')
    answer = answer.replace('≤', '\\le ')
    answer = answer.replace('>', '\\gt ')
    answer = answer.replace('<', '\\lt ')
    answer = answer.replace('≠', '\\ne ')
    answer = answer.replace('=', '= ')
    
    # Ensure proper formatting for \sqrt
    answer = re.sub(r'\\sqrt\s*(\d+)', r'\\sqrt{\1}', answer)
    answer = re.sub(r'\\sqrt\s*\{?', r'\\sqrt{', answer)
    
    # Close any unclosed braces for \sqrt (fixed version)
    answer = re.sub(r'(\\sqrt\{[^\}]*(?:\{[^\}]*\})*[^\}]*})(?!})|'
                    r'(\\sqrt\{[^\}]*(?:\{[^\}]*\})*[^\}]*)(?!})',
                    lambda m: m.group(1) or m.group(2) + '}', answer)
    
    # Correct \frac without braces
    answer = re.sub(r'\\frac\s*(\d+)\s*(\d+)', r'\\frac{\1}{\2}', answer)
    
    # Ensure proper spacing
    answer = re.sub(r'\s+', ' ', answer)
    
    return answer.strip()

def standardize_yes_no(answer):
    return answer.strip().lower()

def standardize_integer(answer):
    return str(int(answer.strip()))

def standardize_fraction(answer):
    # Handle LaTeX fractions
    latex_frac = re.search(r'\\frac\{(.*?)\}\{(.*?)\}', answer)
    if latex_frac:
        numerator = latex_frac.group(1)
        denominator = latex_frac.group(2)
    else:
        numerator, denominator = answer.strip().split('/')
    # Simplify the fraction
    try:
        frac = Fraction(int(numerator), int(denominator))
        return f'\\frac{{{frac.numerator}}}{{{frac.denominator}}}'
    except ValueError:
        # If numerator or denominator is not an integer, return as is
        return f'\\frac{{{numerator}}}{{{denominator}}}'

def standardize_decimal(answer):
    num = float(re.findall(r'-?\d+\.\d+', answer)[0])
    return f'{num:.5f}'

def standardize_irrational(answer):
    answer = answer.replace(' ', '').replace('√', '\\sqrt')
    # Ensure \sqrt{...}
    answer = re.sub(r'\\sqrt(\d+)', r'\\sqrt{\1}', answer)
    answer = re.sub(r'\\sqrt\{([^\}]+)\}(?!\})', r'\\sqrt{\1}', answer)
    # Correct \pi spacing
    answer = answer.replace(' \\pi', '\\pi')
    answer = answer.replace('\\pi', '\\pi ')
    return correct_latex_symbols(answer)

def standardize_equation(answer):
    # Replace 'forall' with LaTeX command
    answer = answer.replace('\\forall', '\\forall ')
    answer = re.sub(r'(?<!\\)forall', '\\forall ', answer)
    # Correct LaTeX symbols
    answer = correct_latex_symbols(answer)
    return answer

def standardize_expression(answer):
    answer = correct_latex_symbols(answer)
    return answer

def standardize_set_list(answer):
    items = split_items_robust(answer)
    standardized_items = [standardize_answer(item) for item in items]
    bracket_type = '[' if answer.startswith('[') else '{'
    closing_bracket = ']' if bracket_type == '[' else '}'
    return standardized_items

def standardize_tuple(answer):
    items = split_items_robust(answer)
    standardized_items = [standardize_answer(item) for item in items]
    return standardized_items

def standardize_list(answer):
    items = split_items_robust(answer)
    standardized_items = [standardize_answer(item) for item in items]
    return standardized_items

def standardize_string(answer):
    return answer.strip()

# Corner cases
def standardize_number_with_unit(answer):
    # Extract the number part
    match = re.match(r'^(-?\d+(\.\d+)?)(\s*[a-zA-Z%°$]+)', answer)
    if match:
        number = match.group(1)
        return number
    else:
        # If no match, return as is
        return answer
    
def standardize_number_with_commas(answer):
    # Remove commas to get the number
    number = answer.replace(',', '')
    return number

def standardize_ratio(answer):
    # Remove spaces around ':'
    ratio = re.sub(r'\s*:\s*', ':', answer)
    return ratio

def standardize_no_solution(answer):
    return 'no solution'

def standardize_infinite(answer):
    return '\\infty'

def standardize_variable(answer):
    return answer.strip()

def standardize_phrase(answer):
    return answer.strip()

def standardize_expression(answer):
    # Correct LaTeX symbols
    answer = correct_latex_symbols(answer)
    # Add missing backslashes for common functions
    functions = ['sqrt', 'sin', 'cos', 'tan', 'ln', 'log', 'arcsin', 'arccos', 'arctan', 'sec', 'csc', 'cot']
    for func in functions:
        answer = re.sub(r'\b' + func, r'\\' + func, answer)
    return answer


def _parse_latex(s):
    for f in [parse_latex, parse_expr, latex2sympy]:
        try:
            return func_timeout(5, f, args=(s.replace("\\\\", "\\"),))
        except:
            try:
                return func_timeout(5, f, args=(s,))
            except:
                pass
    return None

def sympy_convert(answer, answer_type):
    if answer_type in ['integer', 'fraction', 'decimal', 'irrational', 'equation', 'expression']:
        try:
            # Parse the LaTeX expression into a SymPy expression
            expr = _parse_latex(answer)
            # expr = func_timeout(timeout_duration, parse_latex, args=(answer,))
            return expr
        except Exception as e:
            # If parsing fails, return the standardized answer
            return answer
    else:
        # For other types, return the standardized answer
        return answer

def preprocess_answer(answer):
    answer = answer.replace('\\left(', '(')
    answer = answer.replace('\\right)', ')')
    answer = answer.replace('\\left[', '[')
    answer = answer.replace('\\right]', ']')
    answer = answer.replace('\\left{', '{')
    answer = answer.replace('\\right}', '}')
    answer = answer.replace('\\left\\{', '{')
    answer = answer.replace('\\right\\}', '}')
    answer = answer.replace('\\{', '{')
    answer = answer.replace('\\}', '}')
    answer = answer.replace('\\(', '(')
    answer = answer.replace('\\)', ')')
    answer = answer.replace('\\[', '[')
    answer = answer.replace('\\]', ']')
    answer = answer.replace('≥', '\\ge ')
    answer = answer.replace('≤', '\\le ')
    answer = answer.replace('>', '\\gt ')
    answer = answer.replace('<', '\\lt ')
    answer = answer.replace('≠', '\\ne ')
    answer = answer.replace('=', '= ')
    return answer

DIRECT_PARSE_FAIL = 0
def standardize_answer(answer):
    answer = preprocess_answer(answer)
    answer_type = identify_answer_type(answer)
    ans = _parse_latex(answer)
    if ans is not None:
        return ans
    global DIRECT_PARSE_FAIL
    DIRECT_PARSE_FAIL += 1
    if answer_type == 'yes_no':
        standardized = standardize_yes_no(answer)
    elif answer_type == 'no_solution':
        standardized = standardize_no_solution(answer)
    elif answer_type == 'infinite':
        standardized = standardize_infinite(answer)
    elif answer_type == 'number_with_unit':
        standardized = standardize_number_with_unit(answer)
    elif answer_type == 'number_with_commas':
        standardized = standardize_number_with_commas(answer)
    elif answer_type == 'ratio':
        standardized = standardize_ratio(answer)
    elif answer_type == 'variable':
        standardized = standardize_variable(answer)
    elif answer_type == 'phrase':
        standardized = standardize_phrase(answer)
    elif answer_type == 'integer':
        standardized = standardize_integer(answer)
    elif answer_type == 'fraction':
        standardized = standardize_fraction(answer)
    elif answer_type == 'decimal':
        standardized = standardize_decimal(answer)
    elif answer_type == 'irrational':
        standardized = standardize_irrational(answer)
    elif answer_type == 'equation':
        standardized = standardize_equation(answer)
    elif answer_type == 'expression':
        standardized = standardize_expression(answer)
    elif answer_type == 'set_list':
        standardized = standardize_set_list(answer)
    elif answer_type == 'tuple':
        standardized = standardize_tuple(answer)
    elif answer_type == 'list':
        standardized = standardize_list(answer)
    else:
        standardized = standardize_string(answer)
    
    # Attempt to convert to SymPy expression if applicable
    standardized = sympy_convert(standardized, answer_type)
    return standardized

def format_output(answer):
    if isinstance(answer, list):
        return [format_output(item) for item in answer]
    else:
        # String or other type
        return sympy.latex(answer)

# Examples
# example1 = 'f(x)=1\\forall x, f(x)=-\\frac 12\\forall x, f(x)=\\cos\\frac{2\\pi}Tx\\quad\\forall x\\in\\mathbb R'
# standardized_example1 = standardize_answer(example1)
# print('Original Example 1:', example1)
# print('Standardized Example 1:', standardized_example1)

# example2 = '[(5\\sqrt{2})/2,(5\\sqrt{2})/2],[(5\\sqrt{2})/2,-(5\\sqrt{2})/2],[-(5\\sqrt{2})/2,(5\\sqrt{2})/2],[-(5\\sqrt{2})/2,-(5\\sqrt{2})/2]'
# standardized_example2 = standardize_answer(example2)
# print('\nOriginal Example 2:', example2)
# print('Standardized Example 2:', standardized_example2
if __name__ == '__main__':
    # add argparser, specify which jsonl to read
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--jsonl', type=str, default='data/aops/70b_rewritten/AOPS/gemini_eval.jsonl')
    args = parser.parse_args()
    examples = [
        '112 slices',
        '16, 64',
        '$\\dfrac{5}{12}$',
        '1002^2',
        '14.34$',
        '67.833654°',
        'sqrt{71}',
        'cos 1',
        'tan1',
        'No solution',
        'WAYYY MORE THAN 1,000,000!!!',
        '20,250,001',
        '2:1',
        '3 : 2',
        '9:5',
        'e',
        'p',
        'infinite',
        'No such n',
        'All positive integer n'
    ]

    for example in examples:
        standardized_example = standardize_answer(example)
        formatted_output = format_output(standardized_example)
        print(f'Original: {example}\nStandardized: {formatted_output}\nAnswer type: {identify_answer_type(example)}\n')

    example1 = '(x, y, z) = (0, 0, 0); (1, 1, 1)'
    standardized_example1 = standardize_answer(example1)
    print('Original Example 1:', example1)
    print('Standardized Example 1:', standardized_example1)


    # Initialize a dictionary to keep counts of answer types
    answer_type_counts = defaultdict(int)
    failed_to_convert_cnt = 0

    data = [json.loads(line) for line in open(args.jsonl).readlines()]

    type2ans = defaultdict(list)
    for d in tqdm(data):
        standard_answers = []
        failed_to_convert = []
        for ans in d['answers']:
            # Process 'answer'
            # print("Answer: ", ans['answer'])
            # answer_type = identify_answer_type(ans['answer'])
            # print("Answer type: ", answer_type)
            # type2ans[answer_type].append(ans['answer'])
            # answer_type_counts[answer_type] += 1  # Gather answer type information

            # if answer_type != 'phrase':
            #     try:
            #         standardized = standardize_answer(ans['answer'])
            #         standard_answers.append(standardized)
            #     except Exception as e:
            #         print("Error: ", e)
            #         print("Failed to convert: ", ans['answer'])
            #         failed_to_convert.append(ans['answer'])
            # else:
            #     print("Ignoring 'phrase' type answer for 'answer' field")

            # Process 'rewritten_answer'
            print("Rewritten Answer: ", ans['rewritten_answer'])
            rewritten_answer_type = identify_answer_type(ans['rewritten_answer'])
            print("Rewritten Answer type: ", rewritten_answer_type)
            type2ans[rewritten_answer_type].append(ans['rewritten_answer'])
            answer_type_counts[rewritten_answer_type] += 1  # Gather answer type information

            if rewritten_answer_type != 'phrase':
                try:
                    standardized_rewritten = standardize_answer(ans['rewritten_answer'])
                    standard_answers.append(standardized_rewritten)
                except Exception as e:
                    print("Error: ", e)
                    print("Failed to convert: ", ans['rewritten_answer'])
                    failed_to_convert.append(ans['rewritten_answer'])
            else:
                print("Ignoring 'phrase' type answer for 'rewritten_answer' field")

        # Convert standardized answers to strings for comparison
        standard_answers_str = [format_output(ans) for ans in standard_answers]
        standard_answers_str = [
            ans if isinstance(ans, str) else 'json:'+json.dumps(ans) for ans in standard_answers_str
        ]

        # Use majority voting to decide the most common standardized answer
        if standard_answers_str:
            answer_counts = Counter(standard_answers_str)
            most_common = answer_counts.most_common()
            max_count = most_common[0][1]
            top_answers = [ans for ans, cnt in most_common if cnt == max_count]
            # In case of a tie, select the first one
            d['voted_answer'] = top_answers[0]
        else:
            d['voted_answer'] = None  # No valid answers after filtering

        d['standard_answers'] = standard_answers_str
        d['dtype'] = rewritten_answer_type
        failed_to_convert_cnt += len(failed_to_convert)

    # After processing all data, print the answer type counts
    print("\nAnswer Type Counts:")
    for answer_type, count in answer_type_counts.items():
        print(f"{answer_type}: {count}")
    outout_jsonl = os.path.basename(args.jsonl).replace('.jsonl', '_standardized.jsonl')
    with open(f'./{outout_jsonl}', 'w') as f:
        for d in data:
            f.write(json.dumps(d) + '\n')
    
    print(f"Failed to Directly convert {DIRECT_PARSE_FAIL} answers")