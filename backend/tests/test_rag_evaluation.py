from app.agents.rag_agent import rag_agent


TEST_CASES = [
    {
        "name": "Annual leave entitlement",
        "question": "How many days of annual leave are employees entitled to?",
        "expected_answer": "20 days",
    },
    {
        "name": "Leave request location",
        "question": "Where do employees submit leave requests?",
        "expected_answer": "HR portal",
    },
]


def run_rag(question: str, user_id: int = 4):
    return rag_agent.invoke(
        {
            "question": question,
            "user_id": user_id,
            "context": "",
            "answer": "",
            "sources": [],
        }
    )


def test_rag_evaluation():
    passed = 0

    print("\nRAG Evaluation")
    print("-" * 60)

    for test_case in TEST_CASES:
        result = run_rag(test_case["question"])

        answer = result["answer"]
        expected = test_case["expected_answer"]

        success = expected.lower() in answer.lower()

        if success:
            passed += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"\nTest: {test_case['name']}")
        print(f"Question: {test_case['question']}")
        print(f"Expected: {expected}")
        print(f"Answer:   {answer}")
        print(f"Result:   {status}")

    accuracy = (passed / len(TEST_CASES)) * 100

    print("\n" + "-" * 60)
    print(f"Evaluation Accuracy: {accuracy:.2f}%")
    print("-" * 60)

    assert passed == len(TEST_CASES)


def test_unknown_question_does_not_hallucinate():
    question = "What is the company's policy for international space travel?"

    result = run_rag(question)

    answer = result["answer"]
    sources = result["sources"]

    print("\nUnknown Question Test")
    print("-" * 60)
    print(f"Question: {question}")
    print(f"Answer:   {answer}")
    print(f"Sources:  {len(sources)}")

    hallucination_phrases = [
        "international space travel policy",
        "space travel policy states",
        "employees can travel to space",
    ]

    hallucinated = any(
        phrase in answer.lower()
        for phrase in hallucination_phrases
    )

    assert not hallucinated


def test_rag_answer_has_supporting_sources():
    question = "How many days of annual leave are employees entitled to?"

    result = run_rag(question)

    answer = result["answer"]
    sources = result["sources"]

    print("\nSource Grounding Test")
    print("-" * 60)
    print(f"Question: {question}")
    print(f"Answer:   {answer}")
    print(f"Sources:  {len(sources)}")

    assert answer
    assert len(sources) > 0

    for source in sources:
        assert source["document_id"] is not None
        assert source["filename"]
        assert source["text"]
        assert source["score"] >= 0.50


def test_user_document_isolation():
    question = "How many days of annual leave are employees entitled to?"

    user_without_document = 99999

    result = run_rag(
        question,
        user_id=user_without_document,
    )

    answer = result["answer"]
    sources = result["sources"]

    print("\nUser Isolation Test")
    print("-" * 60)
    print(f"Question: {question}")
    print(f"Answer:   {answer}")
    print(f"Sources:  {len(sources)}")

    assert len(sources) == 0