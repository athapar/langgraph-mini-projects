from __future__ import annotations
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph,START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

prompt = "Explain the concept of compound interest to a high-school student."
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

# -----------------------
# 1) Define State Schema
# -----------------------
class LoopState(TypedDict):
    question: str
    answer: str
    feedback: str
    score: int
    iteration: int




# -----------------------
# 2) Initialize LLM
# -----------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",   # cheap + good enough for this demo
    temperature=0.2,
    api_key=OPENAI_API_KEY,
)

# -----------------------
# 3) Node A: Generate/Refine answer
# -----------------------
def answer_node(state: LoopState) -> LoopState:
    question = state["question"]
    prev_answer = state.get("answer", "")
    feedback = state.get("feedback", "")

    prompt = f"""You are a clear explainer.
Question: {question}

Current answer (may be empty):
{prev_answer}

Critique feedback (may be empty):
{feedback}

Write an improved answer for a high-school student.
Keep it under 140 words. Include ONE simple numeric example.
Include exactly one sentence that explicitly lists compounding frequencies: yearly, monthly, daily
"""
    msg = llm.invoke(prompt)
    new_answer = msg.content.strip()

    return {
        **state,
        "answer": new_answer,
        "iteration": state.get("iteration", 0) + 1,
    }



# -----------------------
# 4) Node B: Critique + score
# -----------------------
def critique_node(state: LoopState) -> LoopState:
    answer = state["answer"]
    question = state["question"]

    prompt = f"""You are a strict but consistent grader.

Check ONLY these criteria (no other suggestions):
1) Under 140 words
2) Includes exactly one numeric example
3) Explicitly lists compounding frequencies: yearly, monthly, daily
4) Has a separate sentence that says more frequent compounding grows faster

Score 0-10 based on how many criteria are met:
- 10 if all 4 met
- 8 if 3 met
- 6 if 2 met
- 4 if 1 met
- 2 if 0 met

Return exactly this format (no extra text):
SCORE: <integer>
FEEDBACK: <which criteria failed, in 1 sentence>
Answer:
{state["answer"]}
"""
    msg = llm.invoke(prompt)
    text = msg.content.strip()

    # Very simple parsing
    score_line = next((l for l in text.splitlines() if l.startswith("SCORE:")), "SCORE: 0")
    feedback_line = next((l for l in text.splitlines() if l.startswith("FEEDBACK:")), "FEEDBACK: Improve clarity.")
    score = int(score_line.split("SCORE:")[1].strip() or 0)
    feedback = feedback_line.split("FEEDBACK:")[1].strip()

    return {**state, "score": score, "feedback": feedback}



# -----------------------
# 5) Loop condition
# -----------------------
THRESHOLD = 9
MAX_ITERS = 4

def should_continue(state: LoopState) -> Literal["answer", END]:
    if state["score"] >= THRESHOLD:
        return END
    if state["iteration"] >= MAX_ITERS:
        return END
    return "answer"


# -----------------------
# 6) Build the graph
# -----------------------



if __name__ == "__main__":

    initial: LoopState = {
        "question": "Explain compound interest to a high-school student.",
        "answer": "",
        "feedback": "",
        "score": 0,
        "iteration": 0,
    }

    graph = StateGraph(LoopState)

    graph.add_node("answer", answer_node)
    graph.add_node("critique", critique_node)

    graph.add_edge(START, "answer")
    graph.add_edge("answer", "critique")

    # Conditional edge from critique -> either answer (loop) or END
    graph.add_conditional_edges("critique", should_continue, {"answer": "answer", END: END})

    app = graph.compile()




    final_state = app.invoke(initial)

    print("\n--- FINAL ANSWER ---\n", final_state["answer"])
    print("\n--- FINAL SCORE ---\n", final_state["score"])
    print("\n--- FINAL FEEDBACK ---\n", final_state["feedback"])
    print("\n--- ITERS ---\n", final_state["iteration"])