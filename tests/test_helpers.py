import sys
import types
import importlib.util
from pathlib import Path


def load_biots_module():
    """Load src/biots.py as a module with minimal stubs."""
    src_path = Path(__file__).resolve().parents[1] / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # minimal pygame stub
    pygame_stub = types.ModuleType("pygame")
    pygame_stub.init = lambda: None
    pygame_stub.font = types.SimpleNamespace(
        Font=lambda *a, **k: None, match_font=lambda name: None
    )
    pygame_stub.Rect = lambda *a, **k: None
    sys.modules.setdefault("pygame", pygame_stub)

    # minimal Box2D stub
    Box2D_stub = types.ModuleType("Box2D")
    class B2Vec2:
        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y
        def __mul__(self, other):
            return B2Vec2(self.x * other, self.y * other)
        def __add__(self, other):
            return B2Vec2(self.x + other.x, self.y + other.y)
    Box2D_stub.b2Vec2 = B2Vec2
    sys.modules.setdefault("Box2D", Box2D_stub)

    spec = importlib.util.spec_from_file_location("biots_py3", src_path / "biots.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_addVectors_simple():
    biots = load_biots_module()
    angle, length = biots.addVectors((0, 1), (0, 1))
    assert angle == 0
    assert length == 2


def test_line_intersection():
    biots = load_biots_module()
    l1 = ((0, 0), (1, 1))
    l2 = ((0, 1), (1, 0))
    assert biots.line_intersection(l1, l2)

    l3 = ((0, 0), (1, 0))
    l4 = ((0, 1), (1, 1))
    assert not biots.line_intersection(l3, l4)


def test_caclulateEnergyGain():
    biots = load_biots_module()
    gene = {
        "num_levels": 3,
        "angle": 0.0,
        "segGenes": {
            0: {
                "branchfactor": 0,
                "color": (255, 0, 0),
                "length": 1,
                "energy": 5,
                "movecounter": 0,
                "seg_id": 0,
            },
            1: {
                "branchfactor": 0,
                "color": (255, 0, 0),
                "length": 1,
                "energy": 5,
                "movecounter": 0,
                "seg_id": 1,
            },
            2: {
                "branchfactor": 0,
                "color": (0, 255, 0),
                "length": 1,
                "energy": 12,
                "movecounter": 0,
                "seg_id": 2,
            },
        },
        "arm_id": 0,
    }
    arm = biots.BiotArm(0, 0, size=10, gene=gene)
    arm.caclulateEnergyGain()

    # root increases energy by 3
    assert arm.idBiot["r"]["energy"] == 15
    # children should be destroyed
    assert not arm.idBiot["rm"]["exists"]
    assert not arm.idBiot["rp"]["exists"]
