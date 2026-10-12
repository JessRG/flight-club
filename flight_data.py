class FlightData:

    def __init__(self, price, origin_airport, destination_airport, out_date, return_date, stops):
        self.price = price
        self.origin_airport = origin_airport
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date
        self.stops = stops

def find_cheapest_flight(data, return_date):
    # Handle empty data if no flight data is returned
    if data is None or (not data.get("best_flights") and not data.get("other_flights")):
        print("No flight data")
        return FlightData("N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

    # Combine best_flights and other_flights into one list
    all_flights = data.get("best_flights", []) + data.get("other_flights", [])

    # Set lowest price variable
    lowest_price = float('inf')

    # Initialize FlightData
    cheapest_flight = FlightData("N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

    for flight in all_flights:
        # Exception handling - json has data but flight is missing 'price'. Skip.
        price = flight.get("price", -1)
        if price == -1:
            print("--- No price available for flight. ---")
            continue
        if price < lowest_price:
            lowest_price = price
            origin = flight["flights"][0]["departure_airport"]["id"]
            destination = flight["flights"][-1]["arrival_airport"]["id"]
            out_date = flight["flights"][0]["departure_airport"]["time"].split(" ")[0]
            nr_stops = len(flight["flights"]) - 1
            cheapest_flight = FlightData(lowest_price, origin, destination, out_date, return_date, nr_stops)
            print(f"Lowest price to {destination} is USD {lowest_price}")

    return cheapest_flight
