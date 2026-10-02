import os
import requests
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

# Load environment variables from .env file
load_dotenv()

# Fixed open-weight model required for DebugBuddy
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"

# Page configuration
st.set_page_config(
    page_title="DebugBuddy - AI Java DSA Coach",
    page_icon="🐞",
    layout="wide",
)

# App Header
st.title("🐞 DebugBuddy — AI Java DSA Coach")
st.caption(
    "A friendly peer debugging coach for students mastering Data Structures & Algorithms in Java. "
    "Hacktoberfest 2026 Project."
)

# Sidebar setup
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown(f"**Model:** `{MODEL_NAME}`")
    st.markdown("**Provider:** Hugging Face Inference API")
    st.divider()

    # Retrieve token securely from environment (.env)
    env_token = os.getenv("HF_TOKEN")

    # If not found in .env, offer sidebar input as fallback
    if not env_token:
        st.warning("⚠️ `HF_TOKEN` not found in `.env`")
        sidebar_token = st.text_input(
            "Enter HF Token (temporary):",
            type="password",
            help="Create a .env file with HF_TOKEN=... or paste it here.",
        )
        active_token = sidebar_token.strip() if sidebar_token else ""
    else:
        st.success("✅ `HF_TOKEN` loaded from `.env`")
        active_token = env_token.strip()

    st.divider()
    st.header("💡 Try a Sample Problem")
    if st.button("Load Two Sum Sample"):
        st.session_state["problem"] = (
            "Given an array of integers nums and an integer target, return indices of the two "
            "numbers such that they add up to target. You may assume that each input would have "
            "exactly one solution, and you may not use the same element twice."
        )
        st.session_state["code"] = (
            "class Solution {\n"
            "    public int[] twoSum(int[] nums, int target) {\n"
            "        for (int i = 0; i < nums.length; i++) {\n"
            "            for (int j = 0; j < nums.length; j++) {\n"
            "                if (nums[i] + nums[j] == target) {\n"
            "                    return new int[] { i, j };\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "        return new int[] {};\n"
            "    }\n"
            "}"
        )
        st.session_state["stuck"] = (
            "When nums = [3, 2, 4] and target = 6, my code returns [0, 0] instead of [1, 2] "
            "because it uses the element at index 0 twice. Also, how can I avoid O(n^2) time?"
        )
        st.rerun()

    if st.button("Clear All"):
        st.session_state["problem"] = ""
        st.session_state["code"] = ""
        st.session_state["stuck"] = ""
        st.rerun()

    st.divider()
    st.markdown("### 📌 About")
    st.markdown(
        "DebugBuddy is designed to help students understand *why* their Java code fails "
        "and guides them towards optimal DSA patterns without unnecessary complexity."
    )

# Initialize session state keys for inputs
if "problem" not in st.session_state:
    st.session_state["problem"] = ""
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "stuck" not in st.session_state:
    st.session_state["stuck"] = ""

# Main input layout (2 columns)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. DSA Problem")
    problem_input = st.text_area(
        "Paste the problem description & constraints:",
        value=st.session_state["problem"],
        height=180,
        placeholder="e.g., Given a binary tree, check whether it is a mirror of itself...",
    )

    st.subheader("3. What are you stuck with?")
    stuck_input = st.text_area(
        "Describe your difficulty, error message, or failing test case:",
        value=st.session_state["stuck"],
        height=140,
        placeholder="e.g., Getting NullPointerException when root.left is null, or failing on empty array...",
    )

with col2:
    st.subheader("2. Your Java Code")
    code_input = st.text_area(
        "Paste your Java attempt:",
        value=st.session_state["code"],
        height=390,
        placeholder="public class Solution {\n    // your code here\n}",
    )

debug_button = st.button("🚀 Debug with Buddy", type="primary", use_container_width=True)


def build_coach_prompt(problem: str, java_code: str, stuck: str) -> list[dict]:
    """Constructs the chat messages adhering strictly to the 8 required sections."""
    system_prompt = (
        "You are DebugBuddy, a technically rigorous, friendly, and patient AI DSA coach helping a classmate "
        "debug Data Structures and Algorithms problems in Java.\n\n"
        "Your mission is to provide 100% logically, mathematically, and technically precise feedback on the submitted Java code. "
        "Adhere strictly to the following debugging principles:\n"
        "1. Primary Bug Focus: Identify the PRIMARY bug that causes the wrong result for the exact input and scenario provided by the user. "
        "The 'What's Wrong' section and the corrected code must both address this exact primary bug.\n"
        "2. Do Not Substitute with Edge Cases: Never replace the primary bug with an unrelated edge case. Edge cases (such as negative numbers, "
        "empty arrays, or single elements) may be noted separately, but they must NEVER replace the primary bug. "
        "Do not claim the code has a failure merely because an edge case could fail unless that edge case is part of the supplied input/problem.\n"
        "3. Multi-Issue Distinction: If the submitted code contains both an initialization issue (e.g., initializing max to 0 vs Integer.MIN_VALUE or arr[0]) "
        "and a comparison/operator issue (e.g., using `<` instead of `>`), explicitly identify which one actually causes the supplied test case to fail, "
        "and explain both separately without confusing or conflating them.\n"
        "4. Mathematically Exact Dry Run: Before writing the dry run, evaluate every comparison using the exact operator and actual values from the submitted code. "
        "Never claim that a condition such as `2 < 0` or `5 < 2` is true when it is mathematically false. "
        "The dry run must follow the user's submitted code exactly and conclude with the exact output the submitted code actually produces.\n"
        "5. Explicit Fix Statement: After the dry run, explicitly state the exact line number, variable, or operator that must change to fix the primary bug.\n"
        "6. No Inventions or Contradictions: Do not invent bugs that are not present, and do not make contradictory claims about code execution, variable values, or return values.\n\n"
        "You MUST format your entire response using the following 8 sections with exact markdown headers:\n\n"
        "### 1. Problem Understanding\n"
        "Explain the problem statement, expected input/output, and key constraints in plain, easy-to-understand terms.\n\n"
        "### 2. Hint\n"
        "Provide a gentle conceptual hint or thought-provoking question to help the student think in the right direction before reading the solution.\n\n"
        "### 3. What's Wrong\n"
        "Pinpoint the PRIMARY bug causing the code to fail on the user's input. Cite the exact line, operator, or variable responsible. "
        "Ground your diagnosis strictly in the actual code logic without hallucinating flaws. "
        "If there are separate secondary issues or edge cases (e.g., negative numbers or empty arrays), explain them separately and explicitly distinguish them from the primary bug.\n\n"
        "### 4. Dry Run\n"
        "Trace the user's submitted code line-by-line on their supplied test case. "
        "For every comparison or condition, write out the literal values and exact operator (e.g., evaluating `arr[i] < max` with `2 < 0` is FALSE) to show the true variable states. "
        "Follow the submitted code's actual logic to its final output before explaining the fix. "
        "Conclude this section by explicitly stating the exact line and operator that must change to fix the primary bug.\n\n"
        "### 5. Correct Approach\n"
        "Explain the optimal algorithm/strategy, followed by clean, beginner-friendly, and well-commented Java code that directly fixes the primary bug identified above.\n\n"
        "### 6. Time Complexity\n"
        "State the Big-O time complexity of the correct approach and explain why based on operations/loops.\n\n"
        "### 7. Space Complexity\n"
        "State the Big-O auxiliary space complexity of the correct approach and explain what memory or data structures are allocated.\n\n"
        "### 8. Practice Question\n"
        "Suggest one similar DSA problem (with a short description) that tests the same core pattern to reinforce their understanding."
    )

    user_content = (
        f"**DSA Problem:**\n{problem}\n\n"
        f"**My Java Code:**\n```java\n{java_code}\n```\n\n"
        f"**What I am stuck with:**\n{stuck}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


def call_huggingface_api(token: str, messages: list[dict]) -> str:
    """Invokes Hugging Face InferenceClient with Qwen/Qwen2.5-Coder-7B-Instruct."""
    client = InferenceClient(model=MODEL_NAME, token=token)
    response = client.chat_completion(
        messages=messages,
        max_tokens=2048,
        temperature=0.3,
    )
    return response.choices[0].message.content


# Processing upon button click
if debug_button:
    # 1. Validation: check user inputs
    if not problem_input.strip():
        st.warning("⚠️ Please provide the DSA problem description.")
    elif not code_input.strip():
        st.warning("⚠️ Please provide your Java code.")
    elif not stuck_input.strip():
        st.warning("⚠️ Please explain what you are stuck with.")
    # 2. Validation: check Hugging Face token
    elif not active_token:
        st.error(
            "🔑 **Hugging Face API Token Missing!**\n\n"
            "To use DebugBuddy, please configure your API token:\n"
            "1. Create a `.env` file in the project folder with: `HF_TOKEN=your_huggingface_token_here`\n"
            "2. Or temporarily paste your token in the sidebar input.\n\n"
            "You can generate a free token at: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)"
        )
    else:
        # Build prompt messages
        messages = build_coach_prompt(problem_input, code_input, stuck_input)

        st.divider()
        st.subheader("📋 DebugBuddy Feedback")

        try:
            with st.spinner("🤖 DebugBuddy is analyzing your Java code and tracing the logic..."):
                feedback = call_huggingface_api(active_token, messages)

            st.markdown(feedback)

        except HfHubHTTPError as e:
            status_code = getattr(e.response, "status_code", None)
            if status_code in (401, 403):
                st.error(
                    "🔒 **Authentication Error (401/403):** Your Hugging Face API token is invalid or unauthorized.\n\n"
                    "- Please ensure your token has **Read** permission.\n"
                    "- Check `.env` or re-enter your token in the sidebar."
                )
            elif status_code == 429:
                st.error(
                    "⏳ **Rate Limit Exceeded (429):** The Hugging Face Inference API rate limit has been reached.\n\n"
                    "Please wait a minute and try again."
                )
            elif status_code == 503:
                st.warning(
                    "⏳ **Model Loading (503):** `Qwen/Qwen2.5-Coder-7B-Instruct` is currently spinning up on Hugging Face servers.\n\n"
                    "Please wait 30–60 seconds and click **Debug with Buddy** again."
                )
            else:
                st.error(f"❌ **Hugging Face API Error ({status_code}):** {e}")

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            st.error(
                "🌐 **Network Error:** Unable to reach Hugging Face Inference API servers.\n\n"
                "Please check your internet connection and try again."
            )

        except Exception as e:
            st.error(f"⚠️ **Unexpected Error:** {str(e)}")
