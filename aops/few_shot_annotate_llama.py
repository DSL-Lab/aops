example1 = """
Question: 
Write $\\\frac{1}{1} + \\\frac{1}{2} + \\\frac{1}{3} + \\cdots + \\\frac{1}{19} = \\\frac{A}{B}$, where A is an integer and B is the least common multiple of the numbers 1, 2, 3, ..., 19. Find the remainder of A when divided by 19.

Solution Raw:
2^4 \u00d7 3^2 \u00d7 5 \u00d7 7 \u00d7 11 \u00d7 13 \u00d7 17      \n= (4 \u00d7 5) \u00d7 (3 \u00d7 7) \u00d7 (2 \u00d7 11) \u00d7 (3 \u00d7 13) \u00d7 17 \u00d7 2    \n= 20 \u00d7 21 \u00d7 22 \u00d7 39 \u00d7 17 \u00d7 2    \n= 1 \u00d7 2 \u00d7 3 \u00d7 1 \u00d7 (\u20132) \u00d7 2  \n= \u201324 mod 19  \n= 14 mod 19

Solution Rewrite: 
## Step 1:  The problem asks us to find the remainder of A when divided by 19, where A is an integer and B is the least common multiple of the numbers 1, 2, 3, ..., 19 in the expression $\\\frac{1}{1} + \\\frac{1}{2} + \\\frac{1}{3} + \\cdots + \\\frac{1}{19} = \\\frac{A}{B}$.\n## Step 2:  To approach this problem, we first need to calculate the least common multiple (LCM) of the numbers 1 through 19, which is $2^4 \\times 3^2 \\times 5 \\times 7 \\times 11 \\times 13 \\times 17$.\n## Step 3:  Next, we can simplify the expression by grouping certain terms together to make the calculation easier.\n## Step 4:  We can rewrite the LCM as $(4 \\times 5) \\times (3 \\times 7) \\times (2 \\times 11) \\times (3 \\times 13) \\times 17 \\times 2$.\n## Step 5:  Further simplifying, we get $20 \\times 21 \\times 22 \\times 39 \\times 17 \\times 2$.\n## Step 6:  Now, we can reduce each term modulo 19 to simplify the expression.\n## Step 7:  After reducing each term modulo 19, we get $1 \\times 2 \\times 3 \\times 1 \\times (-2) \\times 2$.\n## Step 8:  Finally, we calculate the product of these terms to find the remainder of A when divided by 19.\n## Step 9:  The product is $-24$, and when reduced modulo 19, we get $14$.\n## Step 10:  Therefore, the remainder of A when divided by 19 is $\\boxed{14}$.\n\nThe final answer is: $\\boxed{14}$

Results:
```json
{
    "is_consistent": 1
}
```
"""

example2 = """
Question:
Can we find four sequences of real numbers $\\{a_n\\}_{n=1}^{\\infty}$, $\\{b_n\\}_{n=1}^{\\infty}$, $\\{c_n\\}_{n=1}^{\\infty}$ and $\\{d_n\\}_{n=1}^{\\infty}$, such that sequence of functions $f_n(x)=\frac{e^{a_nx+b_n}}{{e^{a_nx+b_n}+e^{c_nx+d_n}}}$ uniformly converges to $f(x)=x$ on $[0,1]$.

Solution Raw:
We will show that we can't have pointwise convergence, let alone uniform convergence. Write $\\alpha_ n:=e^{a_nx+b_n}, \\beta_n:=e^{c_nx+d_n}k_n:=c_n-a_n, l_n:=d_n-b_n$. On $(0,1)$ we have ${{\\alpha_n}\\over {\\alpha_n+\\beta_n}}\\rightarrow x$.\nHence $1+{{\\beta_n}\\over {\\alpha_n}}\\rightarrow 1/x$ and $e^{k_nx+l_n}\\rightarrow {{1-x}\\over x}$. Then also $\\theta_n(x):=k_nx+l_n\\rightarrow \\ln ({{1-x}\\over x})=:\\phi(x)$.\nFix $0<a<b<1$ then $k_n={{\\theta_n(b)-\\theta_n(a)}\\over {b-a}}\\rightarrow {{\\phi(b)-\\phi(a)}\\over {b-a}}$.\nThe sequence $k_n$ can have only limit, call it $k$, then ${{\\phi(b)-\\phi(a)}\\over {b-a}}=k$ whenever $0<a<b<1$.\nHence $\\phi$ is a linear (affine) function on $(0,1)$ and $\\phi'(x)$ is constant on $(0,1)$, contradiction."

Solution Rewrite:
## Step 1: Define the sequences and functions\nWe are given sequences of real numbers $\\{a_n\\}_{n=1}^{\\infty}$, $\\{b_n\\}_{n=1}^{\\infty}$, $\\{c_n\\}_{n=1}^{\\infty}$, and $\\{d_n\\}_{n=1}^{\\infty}$, and a sequence of functions $f_n(x)=\\frac{e^{a_nx+b_n}}{e^{a_nx+b_n}+e^{c_nx+d_n}}$.\n\n## Step 2: Introduce new variables\nLet $\\alpha_n := e^{a_nx+b_n}$, $\\beta_n := e^{c_nx+d_n}$, $k_n := c_n - a_n$, and $l_n := d_n - b_n$.\n\n## Step 3: Analyze pointwise convergence\nOn the interval $(0,1)$, we have $\\frac{\\alpha_n}{\\alpha_n + \\beta_n} \\rightarrow x$.\n\n## Step 4: Derive a relationship between $\\alpha_n$ and $\\beta_n$\nFrom the previous step, we have $1 + \\frac{\\beta_n}{\\alpha_n} \\rightarrow \\frac{1}{x}$.\n\n## Step 5: Derive a relationship between $k_n$ and $l_n$\nWe also have $e^{k_nx + l_n} \\rightarrow \\frac{1-x}{x}$.\n\n## Step 6: Define a new function $\\theta_n(x)$\nLet $\\theta_n(x) := k_nx + l_n$.\n\n## Step 7: Analyze the limit of $\\theta_n(x)$\nThen $\\theta_n(x) \\rightarrow \\ln\\left(\\frac{1-x}{x}\\right) =: \\phi(x)$.\n\n## Step 8: Fix a subinterval and analyze the limit of $k_n$\nFix $0 < a < b < 1$, then $k_n = \\frac{\\theta_n(b) - \\theta_n(a)}{b-a} \\rightarrow \\frac{\\phi(b) - \\phi(a)}{b-a}$.\n\n## Step 9: Derive a contradiction\nThe sequence $k_n$ can have only one limit, call it $k$, then $\\frac{\\phi(b) - \\phi(a)}{b-a} = k$ whenever $0 < a < b < 1$.\n\n## Step 10: Analyze the properties of $\\phi(x)$\nHence $\\phi$ is a linear (affine) function on $(0,1)$ and $\\phi'(x)$ is constant on $(0,1)$, which is a contradiction.\n\nThe final answer is: $\\boxed{0}

Results:
```json
{
    "is_consistent": 0
}
```
"""

example3 = """
Question
(1) Determine with proof if for any irrational real $x$, $\\{px\\}$ is dense on $[0,1]$, where $p$ run over primes. (2) Determine with proof if for any irrational real $x$ and non-constant polynomial $f\\in\\mathbb{Z}[x]$, $\\{f(n)x\\}$ is dense on $[0,1]$, where $n$ run over integers.

Solution Raw:
(1) was determined by Vinogradov, a proof for this result can be found [url=https://archive.org/details/vinogradov-the-method-of-trigonometric-sums-in-the-theory-of-numbers/page/70/mode/2up]here[/url], alternatively one might search for [url=https://www.cambridge.org/core/journals/mathematika/article/abs/on-the-distribution-of-p-modulo-1/98751083E04CE57F16D94FCF4D3B94E2]this[/url] article instead. \n(2) proof can be found [url=http://www.fuchs-braun.com/media/3ed54b58b68a224cffff80dffffffff1.pdf]here [/url]where it has shown a broader generalization where $f$ is a polynomial with at least one coeff irrational, then $f(n)$ is equidistributed.\n\nEdit. For (2) there's a proof given in PFTB, but it involves a somewhat technical lemma.

Solution Rewrite:
## Step 1: Understand the problem statement\nThe problem consists of two parts: (1) determining if for any irrational real $x$, the set $\\{px\\}$ is dense on $[0,1]$, where $p$ runs over primes, and (2) determining if for any irrational real $x$ and non-constant polynomial $f\\in\\mathbb{Z}[x]$, the set $\\{f(n)x\\}$ is dense on $[0,1]$, where $n$ runs over integers.\n\n## Step 2: Recall the result for part (1)\nThe result for part (1) was determined by Vinogradov, and a proof can be found in the provided references.\n\n## Step 3: Recall the result for part (2)\nThe result for part (2) can be found in the provided references, which show a broader generalization where $f$ is a polynomial with at least one coefficient irrational, then $f(n)$ is equidistributed.\n\n## Step 4: Note the alternative proof for part (2)\nAn alternative proof for part (2) can be found in PFTB, but it involves a somewhat technical lemma.\n\nThe final answer is: $\\boxed{1}$

Result:
```json
{
    "is_consistent": -1
}
```
"""

instruction = """
You are given:
- A Question.
- A Solution Raw (the original solution).
- A Solution Rewrite (the rewritten solution) where the answer is in \\boxed{}.

**Your tasks are to check the consistency between Solution Raw ans Solution Rewrite.
   - Determine if the final answer in the **Solution Raw** is consistent with the final answer in the **Solution Rewrite**.
   - If they are consistent, output:
     ```
        {"is_consistent": 1}
     ```
   - If they are not consistent, output:
     ```
        {"is_consistent": 0}
     ```
   - if the Solution Raw is incomplete (the solution did not contain an final answer or prove not complete), output:
    ```
        {"is_consistent": -1}
    ```

**Note:**
- Do not include any additional explanation or reasoning in your output.
- It's possible that the **Solution Raw** and **Solution Rewrite** is consistent but have different format of writting the answer.
"""

instruction_few_shot = instruction + \
"\nExample 1:\n" + example1 + \
"\nExample 2:\n" + example2 + \
"\nExample 5:\n" + example3


def get_prompt_format(question, solution_raw, solution_rewrite):
    return f"""\nQuestion: {question}\n\nSolution Raw: {solution_raw}\n\nSolution Rewrite: {solution_rewrite}\n\n1 Whether Solution rewrite has consistent answer with solution raw\n2 The formalized answer from original solution\nResult:\n"""
    