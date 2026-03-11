class Route:
    def __init__(self, covered_route, route, duration_until_decision_point):
        self.covered_route = covered_route
        self.route = route
        self.duration_until_decision_point = duration_until_decision_point

    def copy(self):
        """Create a deep copy of this Route object."""
        return Route(
            covered_route=self.covered_route.copy(),
            route=self.route.copy(),
            duration_until_decision_point=self.duration_until_decision_point
        )

    def start(self):
        if self.covered_route:
            return self.covered_route[-1]
        return 0
    
    def full_route(self):
        return self.covered_route + self.route
