example1 = """
Question: 
Write $\\\frac{1}{1} + \\\frac{1}{2} + \\\frac{1}{3} + \\cdots + \\\frac{1}{19} = \\\frac{A}{B}$, where A is an integer and B is the least common multiple of the numbers 1, 2, 3, ..., 19. Find the remainder of A when divided by 19.

Solution Raw:
2^4 \u00d7 3^2 \u00d7 5 \u00d7 7 \u00d7 11 \u00d7 13 \u00d7 17      \n= (4 \u00d7 5) \u00d7 (3 \u00d7 7) \u00d7 (2 \u00d7 11) \u00d7 (3 \u00d7 13) \u00d7 17 \u00d7 2    \n= 20 \u00d7 21 \u00d7 22 \u00d7 39 \u00d7 17 \u00d7 2    \n= 1 \u00d7 2 \u00d7 3 \u00d7 1 \u00d7 (\u20132) \u00d7 2  \n= \u201324 mod 19  \n= 14 mod 19

Solution Rewrite: 
## Step 1:  The problem asks us to find the remainder of A when divided by 19, where A is an integer and B is the least common multiple of the numbers 1, 2, 3, ..., 19 in the expression $\\\frac{1}{1} + \\\frac{1}{2} + \\\frac{1}{3} + \\cdots + \\\frac{1}{19} = \\\frac{A}{B}$.\n## Step 2:  To approach this problem, we first need to calculate the least common multiple (LCM) of the numbers 1 through 19, which is $2^4 \\times 3^2 \\times 5 \\times 7 \\times 11 \\times 13 \\times 17$.\n## Step 3:  Next, we can simplify the expression by grouping certain terms together to make the calculation easier.\n## Step 4:  We can rewrite the LCM as $(4 \\times 5) \\times (3 \\times 7) \\times (2 \\times 11) \\times (3 \\times 13) \\times 17 \\times 2$.\n## Step 5:  Further simplifying, we get $20 \\times 21 \\times 22 \\times 39 \\times 17 \\times 2$.\n## Step 6:  Now, we can reduce each term modulo 19 to simplify the expression.\n## Step 7:  After reducing each term modulo 19, we get $1 \\times 2 \\times 3 \\times 1 \\times (-2) \\times 2$.\n## Step 8:  Finally, we calculate the product of these terms to find the remainder of A when divided by 19.\n## Step 9:  The product is $-24$, and when reduced modulo 19, we get $14$.\n## Step 10:  Therefore, the remainder of A when divided by 19 is $\\boxed{14}$.\n\nThe final answer is: $\\boxed{14}$

1 Whether Solution rewrite has consistent answer with solution raw
2 The formalized answer from original solution

Let's think step by step:
The final result from solution is 14 mod 19 so it is 14 which is consistent with the rewritten solution $\\boxed{14}$.
```json
{
    "is_consistent": true,
    "answer_raw_propose": "14",
}
```
"""

example2 = """
Question: 
Let $$A=\\begin{pmatrix} a & b& c\ b& c & a\ c& a&b\end{pmatrix},$$ in which $a,b,c$ are all roots of $P(x)=x^3+5x^2+8x-2023.$ Compute det$A$.

Solution Raw:
Using $a^3+b^3+c^3-3abc=(a+b+c)(a^2+b^2+c^2-ab-bc-ca)$,the answer is 5

Solution Rewrite:
## Step 1: Recall the formula for the determinant of a 3x3 matrix
The determinant of a 3x3 matrix can be calculated using the formula:
\[
\det A = a(ei - fh) - b(di - fg) + c(dh - eg)
\]
where the letters represent the corresponding entries of the matrix.

## Step 2: Apply the formula to the given matrix
Using the given matrix $A$, we can substitute the entries into the formula:
\[
\det A = a(c^2 - a^2) - b(ac - bc) + c(ab - ac)
\]

## Step 3: Simplify the expression
Simplifying the expression, we get:
\[
\det A = a(c^2 - a^2) - b(ac - bc) + c(ab - ac)
\]
\[
\det A = a(c^2 - a^2) - abc + b^2c + abc - ac^2
\]
\[
\det A = a(c^2 - a^2) + b^2c - ac^2
\]
\[
\det A = ac^2 - a^3 + b^2c - ac^2
\]
\[
\det A = b^2c - a^3
\]

## Step 4: Use the given polynomial equation
We are given that $a, b, c$ are roots of the polynomial $P(x) = x^3 + 5x^2 + 8x - 2023$.

1 Whether Solution rewrite has consistent answer with solution raw
2 The formalized answer from original solution

Let's think step by step:
The original solution provides the answer as 5, but the rewrriten solution is incomplete, so not consistent and the answer is 5.
```json
{
    "is_consistent": false,
    "answer_raw_propose": "5",
}
```
"""


example3 = """
Question:
Can we find four sequences of real numbers $\\{a_n\\}_{n=1}^{\\infty}$, $\\{b_n\\}_{n=1}^{\\infty}$, $\\{c_n\\}_{n=1}^{\\infty}$ and $\\{d_n\\}_{n=1}^{\\infty}$, such that sequence of functions $f_n(x)=\frac{e^{a_nx+b_n}}{{e^{a_nx+b_n}+e^{c_nx+d_n}}}$ uniformly converges to $f(x)=x$ on $[0,1]$.

Solution Raw:
We will show that we can't have pointwise convergence, let alone uniform convergence. Write $\\alpha_ n:=e^{a_nx+b_n}, \\beta_n:=e^{c_nx+d_n}k_n:=c_n-a_n, l_n:=d_n-b_n$. On $(0,1)$ we have ${{\\alpha_n}\\over {\\alpha_n+\\beta_n}}\\rightarrow x$.\nHence $1+{{\\beta_n}\\over {\\alpha_n}}\\rightarrow 1/x$ and $e^{k_nx+l_n}\\rightarrow {{1-x}\\over x}$. Then also $\\theta_n(x):=k_nx+l_n\\rightarrow \\ln ({{1-x}\\over x})=:\\phi(x)$.\nFix $0<a<b<1$ then $k_n={{\\theta_n(b)-\\theta_n(a)}\\over {b-a}}\\rightarrow {{\\phi(b)-\\phi(a)}\\over {b-a}}$.\nThe sequence $k_n$ can have only limit, call it $k$, then ${{\\phi(b)-\\phi(a)}\\over {b-a}}=k$ whenever $0<a<b<1$.\nHence $\\phi$ is a linear (affine) function on $(0,1)$ and $\\phi'(x)$ is constant on $(0,1)$, contradiction."

Solution Rewrite:
## Step 1: Define the sequences and functions\nWe are given sequences of real numbers $\\{a_n\\}_{n=1}^{\\infty}$, $\\{b_n\\}_{n=1}^{\\infty}$, $\\{c_n\\}_{n=1}^{\\infty}$, and $\\{d_n\\}_{n=1}^{\\infty}$, and a sequence of functions $f_n(x)=\\frac{e^{a_nx+b_n}}{e^{a_nx+b_n}+e^{c_nx+d_n}}$.\n\n## Step 2: Introduce new variables\nLet $\\alpha_n := e^{a_nx+b_n}$, $\\beta_n := e^{c_nx+d_n}$, $k_n := c_n - a_n$, and $l_n := d_n - b_n$.\n\n## Step 3: Analyze pointwise convergence\nOn the interval $(0,1)$, we have $\\frac{\\alpha_n}{\\alpha_n + \\beta_n} \\rightarrow x$.\n\n## Step 4: Derive a relationship between $\\alpha_n$ and $\\beta_n$\nFrom the previous step, we have $1 + \\frac{\\beta_n}{\\alpha_n} \\rightarrow \\frac{1}{x}$.\n\n## Step 5: Derive a relationship between $k_n$ and $l_n$\nWe also have $e^{k_nx + l_n} \\rightarrow \\frac{1-x}{x}$.\n\n## Step 6: Define a new function $\\theta_n(x)$\nLet $\\theta_n(x) := k_nx + l_n$.\n\n## Step 7: Analyze the limit of $\\theta_n(x)$\nThen $\\theta_n(x) \\rightarrow \\ln\\left(\\frac{1-x}{x}\\right) =: \\phi(x)$.\n\n## Step 8: Fix a subinterval and analyze the limit of $k_n$\nFix $0 < a < b < 1$, then $k_n = \\frac{\\theta_n(b) - \\theta_n(a)}{b-a} \\rightarrow \\frac{\\phi(b) - \\phi(a)}{b-a}$.\n\n## Step 9: Derive a contradiction\nThe sequence $k_n$ can have only one limit, call it $k$, then $\\frac{\\phi(b) - \\phi(a)}{b-a} = k$ whenever $0 < a < b < 1$.\n\n## Step 10: Analyze the properties of $\\phi(x)$\nHence $\\phi$ is a linear (affine) function on $(0,1)$ and $\\phi'(x)$ is constant on $(0,1)$, which is a contradiction.\n\nThe final answer is: $\\boxed{0}

1 Whether Solution rewrite has consistent answer with solution raw
2 The formalized answer from original solution

Let's think step by step:
The original solution reach to a contradiction so the final answer is no. The rewritten solution is consistent with the original solution. Since it's a yes not question, the answer should be no.
```json
{
    "is_consistent": true,
    "answer_raw_propose": "no",
}
```
"""

example4 = """
Question:
(1) Determine with proof if for any irrational real $x$, $\\{px\\}$ is dense on $[0,1]$, where $p$ run over primes. (2) Determine with proof if for any irrational real $x$ and non-constant polynomial $f\\in\\mathbb{Z}[x]$, $\\{f(n)x\\}$ is dense on $[0,1]$, where $n$ run over integers.

Solution Raw:
(1) was determined by Vinogradov, a proof for this result can be found [url=https://archive.org/details/vinogradov-the-method-of-trigonometric-sums-in-the-theory-of-numbers/page/70/mode/2up]here[/url], alternatively one might search for [url=https://www.cambridge.org/core/journals/mathematika/article/abs/on-the-distribution-of-p-modulo-1/98751083E04CE57F16D94FCF4D3B94E2]this[/url] article instead. \n(2) proof can be found [url=http://www.fuchs-braun.com/media/3ed54b58b68a224cffff80dffffffff1.pdf]here [/url]where it has shown a broader generalization where $f$ is a polynomial with at least one coeff irrational, then $f(n)$ is equidistributed.\n\nEdit. For (2) there's a proof given in PFTB, but it involves a somewhat technical lemma.

Solution Rewrite:
## Step 1: Understand the problem statement\nThe problem consists of two parts: (1) determining if for any irrational real $x$, the set $\\{px\\}$ is dense on $[0,1]$, where $p$ runs over primes, and (2) determining if for any irrational real $x$ and non-constant polynomial $f\\in\\mathbb{Z}[x]$, the set $\\{f(n)x\\}$ is dense on $[0,1]$, where $n$ runs over integers.\n\n## Step 2: Recall the result for part (1)\nThe result for part (1) was determined by Vinogradov, and a proof can be found in the provided references.\n\n## Step 3: Recall the result for part (2)\nThe result for part (2) can be found in the provided references, which show a broader generalization where $f$ is a polynomial with at least one coefficient irrational, then $f(n)$ is equidistributed.\n\n## Step 4: Note the alternative proof for part (2)\nAn alternative proof for part (2) can be found in PFTB, but it involves a somewhat technical lemma.\n\nThe final answer is: $\\boxed{1}$

1 Whether Solution rewrite has consistent answer with solution raw
2 The formalized answer from original solution

Let's think step by step:
The original solution gives reference to find the proof so it's incomplete. 
```json
{
    "is_consistent": no,
    "answer_raw_propose": "None",
}
```
"""

example5 = """
Question:
  How many solutions, depending on the value of the parameter $a$, has the equation $$\\sqrt{x^2-4}+\\sqrt{2x^2-7x+5}=a ?$$

Solution Raw:
For\n$\\sqrt{(x-2)(x+2)} + \\sqrt{(x-1)(2x-5)}$\nto be real, we need\n$x \\leq -2$ or $x \\geq 2$\nfrom the first term and\n$x \\leq 1$ or $x \\geq \\frac{5}{2}$\nfrom the second term.\nSo we must have \n$x \\leq -2$ or $x \\geq \\frac{5}{2}$\nNow, if $x = -2$, then the sum of the two radicals is\n$0 + \\sqrt{27} = 3\\sqrt{3} = a$.\nIf $x = \\frac{5}{2}$, then the sum is $\\frac{3}{2} = a$\nFor $a = \\frac{3}{2}$, there is one solution for $x$, that is, $x = \\frac{5}{2}$.\nFor $a = 3\\sqrt{3}$, we have two solutions for $x$, that is $x = -2$ or $x \\approx 3.5$.\nTherefore, there are:\nNo solutions for $a < \\frac{3}{2}$,\nOne solution for $\\frac{3}{2} \\leq a < 3\\sqrt{3}$,\nTwo solutions for $a \\geq 3\\sqrt{3}$

Solution Rewrite:
## Step 1: Determine the conditions for the radicals to be real\nFor the expression $\\sqrt{x^2-4}+\\sqrt{2x^2-7x+5}$ to be real, we need to ensure that the terms inside each square root are non-negative. This leads to the conditions $x \\leq -2$ or $x \\geq 2$ from the first term and $x \\leq 1$ or $x \\geq \\frac{5}{2}$ from the second term.\n\n## Step 2: Combine the conditions to find the valid range of x\nCombining the conditions from both terms, we find that we must have $x \\leq -2$ or $x \\geq \\frac{5}{2}$ for the expression to be real.\n\n## Step 3: Evaluate the expression at the boundary values of x\nIf $x = -2$, then the sum of the two radicals is $0 + \\sqrt{27} = 3\\sqrt{3} = a$. If $x = \\frac{5}{2}$, then the sum is $\\frac{3}{2} = a$.\n\n## Step 4: Determine the number of solutions for different ranges of a\nFor $a = \\frac{3}{2}$, there is one solution for $x$, that is, $x = \\frac{5}{2}$. For $a = 3\\sqrt{3}$, we have two solutions for $x$, that is $x = -2$ or $x \\approx 3.5$.\n\n## Step 5: Summarize the number of solutions for different ranges of a\nTherefore, there are:\n- No solutions for $a < \\frac{3}{2}$,\n- One solution for $\\frac{3}{2} \\leq a < 3\\sqrt{3}$,\n- Two solutions for $a \\geq 3\\sqrt{3}$.\n\nThe final answer is: $\\boxed{2}$

1 Whether Solution rewrite has consistent answer with solution raw
2 The formalized answer from original solution

Let's think step by step:
The original solution comes to a conclution that there is two solutions for $a \\geq 3\\sqrt{3}$  which is consistent with \\boxed{2} in the rewritten solution. 
```json
{
    "is_consistent": true,
    "answer_raw_propose": "2",
}
```
"""

example6 = """
Question: Pasha and Vova play the game crossing out the cells of the $3\times 101$ board by turns. At the start, the central cell is crossed out. By one move the player chooses the diagonal (there can be $1, 2$ or $3$ cells in the diagonal) and crosses out cells of this diagonal which are still uncrossed. At least one new cell must be crossed out b
y any player's move. Pasha begins, the one who can not make any move loses. Who has a winning strategy?                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                              
Solution Raw: Im not sure but if first player crosses a 2 cell diagonal. And then if 2nd  crosses 1 cell 1st crosses 2 cell, if 1 then 2, if 3 then 3 to make the number divisible by 3                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                                              
Solution Rewrite: ## Step 1: Understand the game setup and rules                                                                                                                                                                                                                                                                                              
The game is played on a $3\times 101$ board, with the central cell initially crossed out. Players take turns crossing out cells on the board, with each move consisting of choosing a diagonal (containing 1, 2, or 3 cells) and crossing out the uncrossed cells on that diagonal. At least one new cell must be crossed out in each move.                   
                                                                                                                                                                                                                                                                                                                                                              
## Step 2: Determine the winning strategy                                                                                                                                                                                                                                                                                                                     
To develop a winning strategy, we need to consider the possible moves and their outcomes. The first player, Pasha, can start by crossing out a 2-cell diagonal.                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                              
## Step 3: Analyze the response of the second player                                                                                                                                                                                                                                                                                                          
The second player, Vova, can respond by crossing out either a 1-cell, 2-cell, or 3-cell diagonal. We need to consider each of these possibilities and determine the optimal response for Pasha.                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                              
## Step 4: Develop a pattern for Pasha's moves                                                                                                                                                                                                                                                                                                                
If Vova crosses out a 1-cell diagonal, Pasha should respond by crossing out a 2-cell diagonal. If Vova crosses out a 2-cell diagonal, Pasha should respond by crossing out a 1-cell diagonal. If Vova crosses out a 3-cell diagonal, Pasha should respond by crossing out a 3-cell diagonal. This pattern ensures that the total number of crossed-out cells r
emains divisible by 3.                                                                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                              
## Step 5: Determine the winning player                                                                                                                                                                                                                                                                                                                       
By following this pattern, Pasha can maintain control of the game and ensure that Vova is left with no valid moves. Therefore, Pasha has a winning strategy.                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                                                                              
The final answer is: $\boxed{1}$                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                                                              
1 Whether Solution rewrite has consistent answer with solution raw                                                                                                                                                                                                                                                                                            
2 The formalized answer from original solution\Let's think step by step:                                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                                              
Response:  Let's think step by step:                                                                                                                                                                                                                                                                                                                          
The original solution has the idea of making the number of crossed-out cells divisible by 3, but it's not a complete and didn't explicitly specify the answer. So we cannot check whether they are consistent, is_consisent is false and the answer is None.                                                                                                                                                                                                     
```json                                                                                                                                                                                                                                                                                                                                                       
{                                                                                                                                                                                                                                                                                                                                                             
    "is_consistent": false,                                                                                                                                                                                                                                                                                                                                    
    "answer": "None",                                                                                                                                                                                                                                                                                                                                        
}                                                                                                                                                                                                                                                                                                                                                             
```
"""



instruction = """
You are given:
- A **Question**.
- A **Solution Raw** (the original solution).
- A **Solution Rewrite** (the rewritten solution) where the answer is in \\boxed{}.

**Your tasks are:**
1. **Check Consistency:**
   - Determine if the final answer in the **Solution Raw** is consistent with the final answer in the **Solution Rewrite**.
   - If they are consistent, output:
     ```
        {"is_consistent": true}
     ```
   - If they are not consistent or if the **Solution Raw** is incomplete, output:
     ```
        {"is_consistent": false}
     ```
2. **Extract Answer:**
   - Extract the final answer from the **Solution Raw**.
   - If an answer is present, output it in the format:
     ```
        {"answer_raw_propose": [Answer Raw Propose]}
     ```
   - If no answer is present explicitly or the solution is incomplete, output:
     ```
        {"answer_raw_propose": "None"}
     ```

**Note:**
- Please thing step by step and reason carefully, first output your thouhts and then output the result in json format.
- Replace `[Answer Raw Propose]` with the actual final answer extracted from Solution Raw if answer is explicitly specified, otherwise put "None". 
- It's possible that the **Solution Raw** and **Solution Rewrite** is consistent but have different format of writting the answer. In this case, consider them as consistent and output the formalized answer from the **Solution Raw**
- Note that for corner cases like it's not a math question or question not complete, output false for consistency and None for answer.
"""

instruction_few_shot = instruction + \
"\nExample 1:\n" + example1 + \
"\nExample 2:\n" + example2 + \
"\nExample 3:\n" + example3 + \
"\nExample 4:\n" + example4 + \
"\nExample 5:\n" + example5 + \
"\nExample 6:\n" + example6


def get_prompt_format(question, solution_raw, solution_rewrite):
    return f"""\nQuestion: {question}\n\nSolution Raw: {solution_raw}\n\nSolution Rewrite: {solution_rewrite}\n\n1 Whether Solution rewrite has consistent answer with solution raw\n2 The formalized answer from original solution\Let's think step by step:\n"""
    