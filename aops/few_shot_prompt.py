
instruct_parse = """You are given an online Math QA forum where each user post in each topic is in the format "post i by user j: [post i text]". Each user may reply to other users by quoting their post. Your task is to identify the question asked by the first user and find all potential answers within the follow-up discussion, and output them in a structured json format.
Your output json must have a "question" key containing the question, and one "answers" key containing the list of answers. Each answer must have three keys: a "user" key to identify the user who posted the solution, a "post_number" to identify which post number the answer originates from, and a "content" key for the content of the solution. Make sure to reformat the answer content to make it a formal clean solution, without missing details. Do not include any irrelevant information in the answer. Do not add any additional information to the question or answers.
Ensure to handle different line breaks and spaces between posts accurately, and maintain the sequence of the dialogue. Always surround mathematical questions with $ symbols for LaTeX formatting. In case the dialogou does not contain any mathematical question, or there are no valid answers, leave the "question" or "answer" key empty. A few examples are proided below:\n\n{few_shot_examples}\nNow, your task is to provide JSON output for the following Topic:\n{query_topic}"""
    

instruct_classify_question_fewshot = """
Post: Prove that for all positive integers $n\\geq 4$ then $(1^2+1)(2^2+1)\\cdots(n^2+1)$ is not a perfect square.\nOutput:\\boxed{1}
Post: I use Kile and have Fedora 10(if that makes a difference). How can I get Asymptote?\nOutput:\\boxed{0}
Post: On a board the numbers $(n-1, n, n+1)$ are written where  $n$ is positive integer. On a move choose 2 numbers $a$ and $b$, delete them and write $2a-b$ and $2b-a$. After a succession of moves, on the board there are 2 zeros. Find all possible values for $n$.\nOutput:\\boxed{1}
Post: Does anyone know of resources on projective transformations (not just projective geometry) for olympiad problems?\nOutput:\\boxed{0}
Post: HI! This is just a guess my number game. You ask the number. No numbers bigger than 1000 and no negative numbers.\nOutput:\\boxed{0}
Post: Hi,\r\n\r\nI was working on my geometry homework and I stuck on this one construction problem. I'm not familiar with construction problem so you might find this easy but help!\r\n\r\nQuestion say:\r\n\r\nCreate an equiangular octagon that is not equiangular.\r\n\r\nHmm... I know there should be 8 angles (each with 135 degrees) but I still don't have idea on how am I going to put this on the paper.\r\n\r\nPlease help: \nOutput:\\boxed{1}
Post: Generally, what scores at nationals are necessary for countdown? What place (about) would 34 get usually?\nOutput:\\boxed{0}
Post: Hi. I'm a little confused with the definition of a saddle point. Is it a critical point (all first derivatives vanish) that is neither local maximum nor local minimum? Or is it a critical point that is a local minimum in one direction and a local maximum in another direction? Are these two definitions equivalent.\nOutput:\\boxed{0}
Post: While training for a marathon, Randi increased the distance she ran each day by 1 mile. She ran 120 miles in five days. How many miles did she run on the first of these five days?\nOutput:\\boxed{1}
Post: Can some one explain to me how to add and multiply letter exponents?\nOutput:\\boxed{0}
"""

instruct_classify_question = f"""
You are given an online Math QA post. Your task is to identify whether the post asked is a concrete mathmatical question, note that this means it shouldn't be a abstract general question related to math, output the result as \\boxed{{0}} for no and \\boxed{{1}} for yes.
A few examples are proided below:\n{instruct_classify_question_fewshot}\nNow, your task is to provide output for the following post:\nPost: 
"""


def get_instruct_formalize_answer(question, answer):
    instruct_formalize_answer = "You are given a solution to a mathematical question. Your task is to re-write the solution into a step-by-step solution. You should re-write the solution in a formal and clean way, without missing any details. Make sure to include all the necessary steps and explanations. Do not include any irrelevant information in the answer. Do not add any additional information to the solution. Enclose all mathematical expressions in $ symbols for LaTeX formatting. Number each step clearly, starting from 1. Use a new line for each step, and make sure to present the steps in order of how the solution progresses. If there's a final answer or expression, enclose it in \\boxed{} for LaTeX formatting. If the question only requires a proof, end your response with $\blacksquare$.\nQuestion: " + question + "\nSolution: " + answer + "\nNow provide the formalized re-written solution. DO NOT include the question in your response. Only respond with the re-written solution."
    return instruct_formalize_answer

def get_instruct_formalize_question(question, answer):
    if answer == "":
        instruct_formalize_question = "You are given a mathematical question. Your task is to re-write the question in a formal way. Make sure to include all the necessary details and information in the question. Do not include any irrelevant information in the question. Enclose all mathematical expressions in $ symbols for LaTeX formatting. You must never remove geometry figure tags (shown by [asy]).\nQuestion: " + question + "\nNow provide the formalized re-written question. Only respond with the re-written question."
    else:
        instruct_formalize_question = "You are given a mathematical question and its solution. Your task is to re-write the question in a formal way. Make sure to include all the necessary details and information in the question. Do not include any irrelevant information in the question. Enclose all mathematical expressions in $ symbols for LaTeX formatting. You must never remove geometry figure tags (shown by [asy]).\nQuestion: " + question + "\nAnswer: " + answer + "\nNow provide the formalized re-written question. Only respond with the re-written question."
    return instruct_formalize_question


# , a "answer_type" key which is the type of answer you get for questions, choose from (numeric, expression, equation, tuple, interval, prove)

parse_instruct_answer_only = """You are given an online Math QA forum where each user post in each topic is in the format "post i by user j: [post i text]". Each user may reply to other users by quoting their post. Your task is to find all potential answers within the follow-up discussion, and output them in a structured json format.
Your output json must have one "answers" key containing the list of answers. Each answer must have two keys: a "user" key to identify the user who posted the solution, a "post_number" to identify which post number the answer originates from. Do not add any additional information to the question or answers. In case the dialogou does not contain any mathematical question, or there are no valid answers, leave the "answer" key as an empty list. Before you output your JSON answer, provide a short summary of the discussion. A few examples are proided below:\n\n{few_shot_examples}\nNow, your task is to provide JSON output for the following Topic:\n{query_topic}"""


TOPIC_495607_ANS = r"""
Discussion summary:
Post 1: User metalari asks a mathematical question.
Post 2: User roza2010 provides a final answer without any explanation.
Post 3: User Pheonix asks for clarification on the solution provided by roza2010.
Post 4: User mavropnevma provides a complete solution.
Therefore, post 4 is the only solution.
```json
{
  "answers": [
    {
      "user": "mavropnevma",
      "post_number": 4
    }
  ]
}
```"""

TOPIC_1766376_ANS = r"""
Discussion summary:
Post 1: User Angelaangie asks a mathematical question.
Post 2: User Synthetic_Potato provides a complete solution.
Post 3: User Angelaangie asks for clarification on a step in the solution.
Post 4: User omriya200 provides a detailed explanation for the step in question.
Post 5: User Angelaangie thanks omriya200 for the explanation.
Post 6: User khanhnx provides an alternative complete solution.
Therefore, posts 2,6 are the only solutions.
```json
{
  "answers": [
    {
      "user": "Synthetic_Potato",
      "post_number": 2
    },
    {
      "user": "khanhnx",
      "post_number": 6
    }
  ]
}
```"""

TOPIC_3387088_ANS = r"""
Discussion summary:
Post 1: User Vulch asks a mathematical question.
Post 2: User SomeonecoolLovesMaths provides a final answer without any explanation.
Post 3: User Chenyang-Liu asks for clarification on the solution provided by SomeonecoolLovesMaths.
Post 4: User c_double_sharp provides a clarification on the base of the logarithm.
Post 5: User pingpongmerrily provides an alternative base for the logarithm.
Post 6: User Vulch confirms the base of the logarithm.
Therefore, there is no solution.
```json
{
  "answers": []
}
```"""
