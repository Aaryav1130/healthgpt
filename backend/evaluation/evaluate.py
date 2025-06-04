"""
RAG Evaluation Pipeline using RAGAS framework.
Run: python evaluation/evaluate.py
"""
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from datasets import Dataset
import json

def run_evaluation(test_file: str = "evaluation/test_queries.json"):
    with open(test_file) as f:
        test_data = json.load(f)

    dataset = Dataset.from_dict({
        "question": [d["question"] for d in test_data],
        "answer": [d["generated_answer"] for d in test_data],
        "contexts": [d["contexts"] for d in test_data],
        "ground_truth": [d["ground_truth"] for d in test_data],
    })

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    )

    print("\n=== HealthGPT RAG Evaluation Results ===")
    print(result)
    result.to_pandas().to_csv("evaluation/results.csv", index=False)
    return result

if __name__ == "__main__":
    run_evaluation()