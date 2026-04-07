class Route:
    def __init__(self, covered_route, route, processing_time):
        self.covered_route = covered_route
        self.route = route
        self.processing_time = processing_time

    def copy(self):
        """Create a deep copy of this Route object."""
        return Route(
            covered_route=self.covered_route.copy(),
            route=self.route.copy(),
            processing_time=self.processing_time
        )

    def start(self):
        if self.covered_route:
            return self.covered_route[-1]
        return 0
    
    def full_route(self):
        return self.covered_route + self.route
