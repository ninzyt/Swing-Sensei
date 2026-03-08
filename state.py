from dataclasses import dataclass, field
import collections
import time

import phases

@dataclass
class SwingState:
    current_phase: phases.Phase = phases.Phase.REST
    prev_phase: phases.Phase = phases.Phase.REST

 
    velocity_history: collections.deque = field(
        default_factory=lambda: collections.deque(maxlen=10)
    )
    prev_velocity_history: collections.deque = field(
        default_factory=lambda: collections.deque(maxlen=10)
    )


    prev_wrist: any = None
    prev_time: float = field(default_factory=time.time)
    prev_velocity: tuple | None = None

 
    prev_smoothed_cvy: float = 0.0


    contact_fired: bool = False