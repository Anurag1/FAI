from fai import FAI, Memory


def test_memory_retrieval():
    m = Memory()
    m.add("graphs connect entities", "cats are animals")
    assert m.retrieve("entity graph") == ["graphs connect entities"]


def test_reasoning_pipeline():
    engine = FAI(model=lambda prompt: "answer with assumptions and test")
    engine.memory.add("graphs expose relationships")
    result = engine.reason("improve AI discovery with graphs")
    assert result["answer"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["hypothesis"].counterquestions


def test_empty_memory_is_valid():
    result = FAI(model=lambda _: "ok").reason("hello")
    assert result["observation"]["text"] == "hello"
