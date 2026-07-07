"""
Spines & Starlight — scene framework.

The Scene protocol, the shared game Context, and the scene-stack transition
machine that replaces bookstore.py's single hardcoded loop. See
docs/spines-and-starlight/03-screen-flow.md.
"""

from dataclasses import dataclass, field

from . import content

# Scene ids (§1). DETAIL is a modal overlay over SHOP.
TITLE = "TITLE"
SHOP = "SHOP"
DETAIL = "DETAIL"
CART = "CART"
CHECKOUT = "CHECKOUT"


class Scene:
    """Base scene. Screens subclass and override what they need."""

    overlay = False   # True -> the scene below stays drawn underneath (DETAIL)

    def on_enter(self, ctx):
        pass

    def on_exit(self):
        pass

    def handle_event(self, e, ctx):
        pass

    def update(self, dt, ctx):
        pass

    def draw(self, surf, ctx):
        pass


# ----------------------------------------------------------------------
# Scene registry — id -> factory. Screens register themselves on import.
# ----------------------------------------------------------------------
_REGISTRY: dict = {}


def register(scene_id, factory):
    _REGISTRY[scene_id] = factory


def make_scene(scene_id, **params):
    return _REGISTRY[scene_id](**params)


# ----------------------------------------------------------------------
# Context — shared state every scene reads/writes (§4)
# ----------------------------------------------------------------------
@dataclass
class Context:
    profile: content.Profile
    wallet: content.Wallet
    cart: content.Cart
    quest: content.Quest
    catalog: list
    t: int = 0
    muted: bool = False
    mouse: tuple = (0, 0)   # cursor in LOGICAL coords, refreshed each frame
    _pending: tuple | None = field(default=None, repr=False)  # (op, scene_id, params)
    _quit: bool = field(default=False, repr=False)

    @property
    def ledger(self):
        return content.Ledger(self.cart)

    # navigation — scenes request a transition; the app applies it after draw
    def go(self, scene_id, **params):
        self._pending = ("go", scene_id, params)

    def push(self, scene_id, **params):
        self._pending = ("push", scene_id, params)

    def pop(self):
        self._pending = ("pop", None, {})

    def quit(self):
        self._quit = True


def new_context():
    return Context(
        profile=content.load_profile(),
        wallet=content.Wallet(),
        cart=content.Cart(),
        quest=content.DEFAULT_QUEST,
        catalog=content.CATALOG,
    )


# ----------------------------------------------------------------------
# Transition application (§5)
# ----------------------------------------------------------------------
def visible_slice(stack):
    """Scenes to draw, bottom-up. Overlay tops also draw the scene beneath."""
    top = stack[-1]
    if getattr(top, "overlay", False) and len(stack) > 1:
        return [stack[-2], top]
    return [top]


def commit_purchase(ctx):
    """The one money-spending transition (§6). Atomic; returns success."""
    ledger = content.Ledger(ctx.cart)
    if not ledger.affordable(ctx.wallet):
        return False
    ctx.wallet.coins -= ledger.total
    ctx.profile.collection += [b.id for b in ctx.cart.items]
    ctx.profile.coins = ctx.wallet.coins
    ctx.cart = content.Cart()
    content.save_profile(ctx.profile)
    return True


def apply_transitions(stack, ctx):
    """Consume ctx._pending and mutate the scene stack accordingly."""
    if ctx._pending is None:
        return
    op, scene_id, params = ctx._pending
    ctx._pending = None
    if op == "go":
        stack[-1].on_exit()
        stack[-1] = make_scene(scene_id, **params)
        stack[-1].on_enter(ctx)
    elif op == "push":
        new = make_scene(scene_id, **params)
        stack.append(new)
        new.on_enter(ctx)
    elif op == "pop":
        if len(stack) > 1:
            stack.pop().on_exit()
