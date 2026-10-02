# DebugBuddy — Your Local AI DSA Coach

DebugBuddy is a beginner-friendly, peer-learning AI debugging assistant designed to help students and classmates master Data Structures & Algorithms (DSA) in Java. 

Instead of just handing out answers or spitting out generic code, DebugBuddy analyzes the student's actual attempt, diagnoses the specific logic bug, walks through a line-by-line dry run, and provides structured hints and explanations.

---

## Overview

Learning DSA in Java can be overwhelming. Beginners often get stuck on index bounds, off-by-one errors, loop conditions, or suboptimal complexity without understanding *why* their code fails. 

DebugBuddy provides a local Streamlit interface while using Hugging Face hosted inference for the AI model. The application communicates directly with Hugging Face's hosted Inference API to provide real-time, structured coaching without requiring heavy local hardware or complex setups.

---

## Features

- **Grounded Bug Diagnosis:** Pinpoints the exact bug in the submitted code without hallucinating or making contradictory claims.
- **Detailed Step-by-Step Dry Run:** Traces code execution with concrete values and evaluates comparisons mathematically before explaining the fix.
- **Conceptual Hints First:** Offers gentle nudges and guiding questions so students can think critically before jumping to the solution.
- **Separation of Primary Bugs vs. Edge Cases:** Addresses the root logic issue directly while noting edge cases (e.g., negative numbers, empty arrays) separately.
- **Complexity Analysis:** Breaks down Big-O time and space complexity with clear justifications.
- **Reinforcement Practice:** Recommends a similar practice question to solidify learned patterns.
- **Zero-Bloat Architecture:** No heavy orchestration frameworks, vector databases, or local LLM servers required.

---

## How It Works

The workflow is simple and intuitive:

1. **User Provides:**
   - **DSA Problem:** The problem statement and constraints.
   - **Java Code:** The student's current implementation attempt.
   - **What They Are Stuck With:** The failing test case, error message, or confusion (e.g., TLE, incorrect return value).

2. **AI Generates Structured Coaching:**
   - `### 1. Problem Understanding`
   - `### 2. Hint`
   - `### 3. What’s Wrong`
   - `### 4. Dry Run`
   - `### 5. Correct Approach` (Clean, commented Java code)
   - `### 6. Time Complexity`
   - `### 7. Space Complexity`
   - `### 8. Practice Question`

---

## Tech Stack

- **Frontend / UI:** [Streamlit](https://streamlit.io/)
- **AI Model:** `Qwen/Qwen2.5-Coder-7B-Instruct`
- **Model Provider:** [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index) (hosted inference)
- **API Client:** `huggingface_hub` (`InferenceClient`)
- **Environment Management:** `python-dotenv`
- **Language:** Python 3.10+

> **Important Technical Note:**
> - DebugBuddy uses **Hugging Face hosted inference**—the model weights are not hosted or run on local GPU/CPU hardware.
> - DebugBuddy does **NOT** use Ollama.
> - DebugBuddy does **NOT** use LangChain, LangGraph, FAISS, vector stores, or databases.

---

## Project Structure

```text
DebugBuddy/
├── app.py              # Streamlit application UI & Hugging Face inference logic
├── requirements.txt    # Project Python dependencies
├── .env.example        # Template for environment variables
├── .gitignore          # Git exclusion rules (ignores .env, venv, cache)
└── README.md           # Project documentation
```

---

## Environment Variables

DebugBuddy expects a free Hugging Face User Access Token to communicate with the Inference API. 

Create a `.env` file in the root directory (based on `.env.example`):

```env
HF_TOKEN=your_huggingface_token_here
```

| Variable | Description | Required |
| :--- | :--- | :---: |
| `HF_TOKEN` | Hugging Face User Access Token with permission to make calls to Inference Providers | Yes |

*Note: Never commit your `.env` file to version control. The repository's `.gitignore` is pre-configured to keep your token secure.*

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/ChikkalaSukrutiNaidu/DebugBuddy.git
cd DebugBuddy
```

### 2. Create a virtual environment
```powershell
python -m venv venv
```

### 3. Activate the virtual environment (Windows)
```powershell
.\venv\Scripts\activate
```
*(On macOS/Linux: `source venv/bin/activate`)*

### 4. Install dependencies
```powershell
pip install -r requirements.txt
```

### 5. Create your `.env` file
Copy the `.env.example` template:
```powershell
copy .env.example .env
```
*(On macOS/Linux: `cp .env.example .env`)*

### 6. Add your Hugging Face API token
Open `.env` in any text editor and paste your token:
```env
HF_TOKEN=your_huggingface_token_here
```
> You can create a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (enable the permission to make calls to Inference Providers).

---

## How to Run

With your virtual environment activated and `.env` configured, start the app:

```powershell
streamlit run app.py
```

Streamlit will launch the web application in your default browser at `http://localhost:8501`.

---

## Example Use Case

- **Problem:** Two Sum (Find indices of two numbers that add up to a target).
- **Submitted Code:** Nested `for` loop where inner loop starts at `j = 0` instead of `j = i + 1`.
- **Student Difficulty:** Testing with `nums = [3, 2, 4]` and `target = 6` returns `[0, 0]` because element `3` is used twice.
- **DebugBuddy Output:**
  - Identifies that `j` begins at index `0`, allowing the same element to pair with itself.
  - Traces the dry run for `i = 0, j = 0`, demonstrating `nums[0] + nums[0] == 6` (`3 + 3 == 6`) returning `[0, 0]`.
  - Explains the fix (`j = i + 1`) and shows the optimal $O(N)$ solution using a `HashMap`.
  - Analyzes time and space complexity and suggests a follow-up problem (e.g., *Two Sum II - Input Array Is Sorted*).

---

## Why Open-Weight AI?

DebugBuddy is built around `Qwen/Qwen2.5-Coder-7B-Instruct`. Qwen2.5-Coder-7B-Instruct is an open-weight code-focused language model. Open-weight models offer:
- **Transparency & Reproducibility:** Accessible to students, educators, and open-source contributors without proprietary lock-in.
- **High Code Quality:** Specially trained on diverse coding tasks, syntax, and algorithmic logic.
- **Accessible Learning:** Hosted inference makes it possible to experiment with the model without requiring students to own local GPU hardware.

---

## Future Improvements

- [ ] Support for additional programming languages (Python, C++).
- [ ] Automated JUnit test case generation for edge-case validation.
- [ ] Interactive multi-turn chat to ask follow-up questions on the dry run.
- [ ] Visual tree/graph diagrams for recursion and pointer problems.

---

## Author

Created as a Hacktoberfest 2026 project to make Java DSA learning accessible, supportive, and beginner-friendly.
