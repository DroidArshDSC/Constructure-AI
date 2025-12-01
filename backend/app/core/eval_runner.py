from app.core.vectorstore import search_chunks
from app.core.llm import generate_answer, extract_schedule


class EvalRunner:

    def __init__(self):
        self.tests = [
            {
                "name": "RAG – Find wage rate (text-only doc)",
                "query": "What is the wage rate for an Electrician (Low Voltage Wiring)?",
                "expected_substring": "34.50",
            },
            {
                "name": "RAG – Abbreviation meaning (drawings)",
                "query": "What does ETR mean?",
                "expected_substring": "Existing",
            },
            {
                "name": "Extraction – Door schedule contains rows",
                "extract": True,
                "expected_min_rows": 5,
            }
        ]


    # -------------------------------------------------------
    # Run the entire evaluation suite
    # -------------------------------------------------------
    def run_all(self):
        results = []

        for test in self.tests:
            if test.get("extract"):
                result = self.run_extraction_test(test)
            else:
                result = self.run_rag_test(test)

            results.append(result)

        summary = self.summarize(results)

        return {
            "summary": summary,
            "results": results
        }


    # -------------------------------------------------------
    # Test RAG chat behavior using generate_answer()
    # -------------------------------------------------------
    def run_rag_test(self, test):
        query = test["query"]

        # Retrieve chunks
        chunks = search_chunks(query, k=5)

        # Generate answer
        answer, citations = generate_answer(query, chunks)

        expected = test["expected_substring"]
        passed = expected.lower() in answer.lower()

        return {
            "name": test["name"],
            "type": "rag",
            "query": query,
            "expected": expected,
            "answer": answer,
            "citations": citations,
            "passed": passed
        }


    # -------------------------------------------------------
    # Test extraction pipeline (door schedule)
    # -------------------------------------------------------
    def run_extraction_test(self, test):

        # Pull door-schedule-relevant chunks
        chunks = search_chunks("door schedule", k=8)

        # Extract structured schedule
        result = extract_schedule(chunks)

        data = result["data"]
        citations = result["citations"]

        min_rows = test["expected_min_rows"]
        passed = len(data) >= min_rows

        return {
            "name": test["name"],
            "type": "extract",
            "rows_found": len(data),
            "expected_min_rows": min_rows,
            "citations": citations,
            "sample": data[:3],
            "passed": passed
        }


    # -------------------------------------------------------
    # Compute final summary of all tests
    # -------------------------------------------------------
    def summarize(self, results):
        total = len(results)
        passed = len([r for r in results if r["passed"]])
        failed = total - passed

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "score_percent": round((passed / total) * 100, 1)
        }
