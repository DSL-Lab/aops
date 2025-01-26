import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import re
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
from grader import math_equal, call_with_timeout

# add current path to sys.path
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

    # Check for numbers
    if re.match(r'^-?\d+(\.\d+)?$', answer):
        return 'number'

    # Check for phrases or words
    if re.fullmatch(r'[A-Za-z\s,.\-!?]+', answer):
        return 'string'

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

    if answer.count('=') == 1 or answer.count('\\ge') == 1 or answer.count('\\le') == 1 or answer.count('\\gt') == 1 or answer.count('\\lt') == 1 or answer.count('\\ne') == 1:
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


def _parse_latex(s):
    for f in [latex2sympy, parse_latex, parse_expr]:
        try:
            return func_timeout(2, f, args=(s.replace("\\\\", "\\"),))
        except:
            try:
                return func_timeout(2, f, args=(s,))
            except:
                pass
    return None

def sympy_convert(answer):
    try:
        # Parse the LaTeX expression into a SymPy expression
        expr = _parse_latex(answer)
        if expr is None:
            raise Exception('Failed to parse LaTeX expression')
        # expr = func_timeout(timeout_duration, parse_latex, args=(answer,))
        return expr
    except Exception as e:
        # If parsing fails, return the standardized answer
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
    
    # Ensure proper formatting for \sqrt
    answer = re.sub(r'\\sqrt\s*(\d+)', r'\\sqrt{\1}', answer)
    answer = re.sub(r'\\sqrt\s*\{?', r'\\sqrt{', answer)
    
    # Correct \frac without braces
    answer = re.sub(r'\\frac\s*(\d+)\s*(\d+)', r'\\frac{\1}{\2}', answer)
    
    # Ensure proper spacing
    answer = re.sub(r'\s+', ' ', answer)
    
    functions = ['sqrt', 'sin', 'cos', 'tan', 'ln', 'log', 'arcsin', 'arccos', 'arctan', 'sec', 'csc', 'cot']
    for func in functions:
        answer = re.sub(r'\b' + func, r'\\' + func, answer)
    
    return answer


def format_output(answer):
    if isinstance(answer, list):
        return [format_output(item) for item in answer]
    elif isinstance(answer, str):
        return answer
    else:
        # String or other type
        try:
            str_answer = sympy.latex(answer)
        except Exception as e:
            try:
                str_answer = str(answer)
            except Exception as e:
                str_answer = "none"
        return str_answer


# Examples
# example1 = 'f(x)=1\\forall x, f(x)=-\\frac 12\\forall x, f(x)=\\cos\\frac{2\\pi}Tx\\quad\\forall x\\in\\mathbb R'
# standardized_example1 = standardize_answer(example1)
# print('Original Example 1:', example1)
# print('Standardized Example 1:', standardized_example1)

# example2 = '[(5\\sqrt{2})/2,(5\\sqrt{2})/2],[(5\\sqrt{2})/2,-(5\\sqrt{2})/2],[-(5\\sqrt{2})/2,(5\\sqrt{2})/2],[-(5\\sqrt{2})/2,-(5\\sqrt{2})/2]'
# standardized_example2 = standardize_answer(example2)
# print('\nOriginal Example 2:', example2)
# print('Standardized Example 2:', standardized_example2
# def math_equal_with_timeout(a, b):
#     if a is None or b is None:
#         return False
#     try:
#         print("call with timeout", a, b)
#         return call_with_timeout(math_equal, a, b, timeout=5)
#     except:
#         return False

def check_consistent_with_original_boxed(l1, l2):
    for ans1, ans2 in zip(l1, l2):
        if ans2 is None or ans1 is None:
            continue
        if not math_equal(ans1, ans2, timeout=True):
            if not ans1 in ans2:
                return False
    return True

def list_not_all_none(l):
    for item in l:
        if item is not None:
            return True
    return False

def accept_ans_w_ref(ans_l, ref_ans_l):
    accepted_ans_l = []
    for ans in ans_l:
        if ans is None:
            continue
        for ref_ans in ref_ans_l:
            if ref_ans is None:
                continue
            if math_equal(ans, ref_ans, timeout=True):
                accepted_ans_l.append(ans)
            elif ans in ref_ans:
                accepted_ans_l.append(ans)
    return accepted_ans_l

def get_diff_labels():
    diff_labels = {}
    
    data_2024_diff = [json.loads(line) for line in open('/data/datasets/QED/aops/aops_24_dif/1_2_test_dif.jl', 'r').readlines()] +\
                        [json.loads(line) for line in open('/data/datasets/QED/aops/aops_24_dif/3_5_test_dif.jl', 'r').readlines()] +\
                        [json.loads(line) for line in open('/data/datasets/QED/aops/aops_24_dif/6_8_test_dif.jl', 'r').readlines()] 
    data_2023_diff = [json.loads(line) for line in open('/data/datasets/QED/aops/aops_24_dif/2023_to_annotate_gemini_eval_dif.jsonl', 'r').readlines()] 
    data_2020_diff = [json.loads(line) for line in open('/data/datasets/QED/aops/aops_24_dif/2020_2021_2022_to_annotate_dif.jsonl', 'r').readlines()]
    data = data_2023_diff + data_2020_diff + data_2024_diff
    for d in data: 
        topic_id = d['topic_id']
        diff_labels[topic_id] = d['difficulty']
        
    return diff_labels

if __name__ == '__main__':
    # add argparser, specify which jsonl to read
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--jsonl1', type=str, default='/data/muchenli/QED/data/aops/70b_rewritten_qwen/AOPS_v0.3.2_qwen_eval/2024_1-8_to_annotate.jsonl')
    parser.add_argument('--jsonl1_name', type=str, default='qwen')
    parser.add_argument('--jsonl2', type=str, default='/data/muchenli/QED/data/aops/70b_rewritten/AOPS_v0.2_eval/2024_1-8_to_annotate.jsonl')
    parser.add_argument('--jsonl2_name', type=str, default='llama')


    args = parser.parse_args()

    data1 = [json.loads(line) for line in open(args.jsonl1).readlines()]
    data1 = {d['topic_id']: d for d in data1}
    data2 = [json.loads(line) for line in open(args.jsonl2).readlines()]
    data2 = {d['topic_id']: d for d in data2}
    
    f_inconsistent_w_original = open('out/inconsistent_w_original.jsonl', 'w')
    f_no_answer = open('out/no_answer.jsonl', 'w')
    f_has_text = open('out/has_text.jsonl', 'w')
    # outout_jsonl = os.path.basename(args.jsonl1).replace('.jsonl', '_standardized.jsonl')
    outout_jsonl = "aops_2024.jsonl"
    f_output_jsonl = open(os.path.join('out', outout_jsonl), 'w')
    diff_d = get_diff_labels()
    for topic_id in tqdm(data1.keys()):
        print('Processing topic', topic_id)
        d_to_save = {
            "topic_id": topic_id,
            "question": data1[topic_id]['rewritten_question'],
            "link": data1[topic_id]['link'],
            "post_time": data1[topic_id]['post_time'],
            "solution": "\n\n\n\n".join(data1[topic_id]['rewritten_answers']),
        }
        # if there is > 2 ? in the question, skip
        if data1[topic_id]['rewritten_question'].count('?') > 2:
            print('Skipping topic', topic_id, 'because of too many ?')
            continue
        d1 = data1[topic_id]
        if topic_id not in data2:
            continue
        d2 = data2[topic_id]
        jump_flag = False

        if not check_consistent_with_original_boxed(d1['boxed_answers'], d1['boxed_answers_original']):
            print('Original boxed answers inconsistent with the rewritten boxed answers', end=' : ')
            print(d1['boxed_answers'], " vs ", d1['boxed_answers_original'])
            f_inconsistent_w_original.write(args.jsonl1_name + '\n')
            f_inconsistent_w_original.write(json.dumps(d1) + '\n')
            jump_flag = True
        if not check_consistent_with_original_boxed(d2['boxed_answers'], d2['boxed_answers_original']):
            print('Original boxed answers inconsistent with the rewritten boxed answers', end=' : ')
            print(d2['boxed_answers'], " vs ", d2['boxed_answers_original'])
            f_inconsistent_w_original.write(args.jsonl2_name + '\n')
            f_inconsistent_w_original.write(json.dumps(d2) + '\n')
            jump_flag = True
        if jump_flag:
            continue
        
        d1_id2ans = {}
        for ori_sol, ans in zip(d1['original_answers'], d1['boxed_answers']):
            d1_id2ans[ori_sol['post_number']] = ans
        d2_id2ans = {}
        for ori_sol, ans in zip(d2['original_answers'], d2['boxed_answers']):
            d2_id2ans[ori_sol['post_number']] = ans
        
        # if original answer is found, use it  
        if list_not_all_none(d1['boxed_answers_original']):
            answers = accept_ans_w_ref(d1['boxed_answers'], d1['boxed_answers_original'])
            answers = answers + accept_ans_w_ref(d2['boxed_answers'], d1['boxed_answers_original'])
            answers = answers + [x for x in d1['boxed_answers_original'] if x is not None]
            print('Original answer found, accepted answer cnt:', len(answers))
        # if original answer is not found, use all consistent answers
        else:
            answers = []
            for post_number in d1_id2ans.keys():
                if post_number not in d2_id2ans:
                    print(f'Post number {post_number} not found in d2 for topic {topic_id}')
                    continue
                if d1_id2ans[post_number] is not None and d2_id2ans[post_number] is not None:
                    if math_equal(d1_id2ans[post_number], d2_id2ans[post_number], timeout=True):
                        answers.append(d1_id2ans[post_number])
                        answers.append(d2_id2ans[post_number])
        
        # summerize ans save
        answers = list(set(answers))
        if len(answers) == 0:
            print('No answer found for topic', topic_id)
            f_no_answer.write(json.dumps(d1) + '\n')
            f_no_answer.write(json.dumps(d2) + '\n')
            f_no_answer.write('\n')
        else:
            answers = sorted(answers, key=lambda x: len(x))
            d_to_save['voted_answer'] = answers
            # remove anything that have \\text{}
            has_text = ["\\text{" in ans for ans in answers]
            if sum(has_text) > 0:
                print(f"Jumping over {topic_id} because of ans with text")
                f_has_text.write(json.dumps(d1) + '\n')
                continue
            d_to_save['rewrite'] = {
                args.jsonl1_name: d1_id2ans,
                args.jsonl2_name: d2_id2ans,
                "raw": d1['original_answers']
            }
            is_zero_one = 'zero_one' if str(answers[0]).lower() in ['0', '1', 'yes', 'no'] else 'not_zero_one'
            d_to_save['type'] = [
                f"{d1['post_time']['year']}-{d1['post_time']['month']}",
                str(diff_d.get(topic_id, -1)),
                identify_answer_type(answers[0]),
                is_zero_one
            ]
            f_output_jsonl.write(json.dumps(d_to_save) + '\n')
            
