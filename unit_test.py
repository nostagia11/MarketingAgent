
def query_and_validate(question: str, expected_response: str):
    EVAL_PROMPT = """
    Expected Response: {expected_response}
    Actual Response: {actual_response}
    ---
    (Answer with 'true' or 'false') Does the actual response match the expected response?
    """
    response_text = query_rag(question)
    prompt = EVAL_PROMPT.format(
        expected_response=expected_response,
        actual_response=response_text)

    model = Ollama(model="mistral")
    evaluation_results_str = model.invoke(prompt)
    final_result = evaluation_results_str.strip().lower()

    print(prompt)

    if "true" in final_result:
        return True
    #print("\033[92m") + f"Response: {final_result}" + "\033[0m")
    elif "false" in final_result:
        return False
    # print("\033[92m") + f"Response: {final_result}" + "\033[0m")
    else:
        raise ValueError(f"Cannot determine if true or false Invalid evaluation result. Cannot determine if 'true' or 'false'.")


def test_assistant_rules():
    assert query_and_validate(
        question="",
        expected_response="",
    )