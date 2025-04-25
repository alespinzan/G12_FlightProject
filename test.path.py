from path import Path

def test_path():
    path = Path("A")
    path.AddNodeToPath("B", 5)
    path.AddNodeToPath("C", 10)

    assert path.ContainsNode("B") == True
    assert path.ContainsNode("D") == False
    assert path.CostToNode("C") == 15
    assert path.CostToNode("D") == -1

    print("All tests passed!")

test_path()