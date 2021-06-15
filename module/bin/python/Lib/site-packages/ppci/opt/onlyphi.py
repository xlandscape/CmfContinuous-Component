
from .. import ir
from .transform import FunctionPass


def only_used_by_phis(phi):
    return


class OnlyPhiPass(FunctionPass):
    """ Remove phi's used only by other phis.

    It can occur that after multiple optimizations, only phi nodes
    are left in a circle. This pass gets rid of these.
    """
    def on_function(self, function):
        raise NotImplementedError()
        # Gather all phi nodes:
        phis = set()
        for block in function:
            for instruction in block:
                if isinstance(instruction, ir.Phi):
                    phis.add(instruction)

        while phis:
            # Pick a phi:
            phi = phis.pop()

            if all(isinstance(p, ir.Phi) for p in phi.used_by):
                pass
