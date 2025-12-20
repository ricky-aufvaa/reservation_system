"""
Generate realistic restaurant data for GoodFoods chain (Delhi)
Creates 50-100 restaurants with diverse attributes
"""

import json
import random
from datetime import datetime
import uuid

# Restaurant name components
CUISINE_NAMES = {
    'Italian': ["Giovanni's", 'Bella Italia', 'Trattoria Romana', 'La Cucina', 'Pasta Palazzo'],
    'Chinese': ['Golden Dragon', 'Jade Garden', 'Szechuan Palace', 'Ming Dynasty', 'Red Lantern'],
    'Indian': ['Spice Route', 'Taj Mahal', 'Mumbai Masala', 'Curry House', 'Namaste Kitchen'],
    'Japanese': ['Sakura Gardens', 'Tokyo Express', 'Sushi Zen', 'Ramen House', 'Izakaya Kobo'],
    'Mexican': ['Casa Verde', 'El Mariachi', 'Taco Fiesta', 'Azteca Grill', 'La Cantina'],
    'French': ['La Belle Vue', 'Bistro Provence', 'Le Jardin', 'Chez Pierre', 'Maison Rouge'],
    'American': ['The Grill House', 'Liberty Diner', 'Oak & Barrel', 'The Rooftop', 'Main Street Bistro'],
    'Thai': ['Bangkok Nights', 'Thai Orchid', 'Golden Temple', 'Sukhothai', 'Pad Thai Palace'],
    'Mediterranean': ['Olive Branch', 'Aegean Sea', 'Cyprus Garden', 'Mediterranean Breeze', 'Santorini'],
    'Korean': ['Seoul Kitchen', 'K-BBQ House', 'Kimchi Garden', 'Gangnam Grill', 'Hanok Table']
}

# Real-world Delhi locations
DELHI_LOCATIONS = [
    'Connaught Place',
    'Hauz Khas Village',
    'Greater Kailash I',
    'Greater Kailash II',
    'Saket',
    'Vasant Kunj',
    'Chanakyapuri',
    'Karol Bagh',
    'Rajouri Garden',
    'Punjabi Bagh',
    'Lajpat Nagar',
    'South Extension',
    'Defence Colony',
    'Dwarka Sector 21',
    'Aerocity',
    'Janpath',
    'Nehru Place',
    'Malviya Nagar',
    'Khan Market',
    'Civil Lines'
]

FEATURES = [
    'outdoor seating', 'private dining', 'bar area', 'live music',
    'vegan options', 'gluten-free menu', 'kids menu', 'parking available',
    'wheelchair accessible', 'romantic ambiance', 'group friendly',
    'business casual', 'pet friendly patio', 'craft cocktails'
]

DELHI_PIN_CODES = ['110001', '110016', '110019', '110021', '110024', '110027', '110029', '110048', '110057', '110070']


def generate_operating_hours():
    """Generate realistic operating hours"""
    lunch_start = random.choice(['11:00', '11:30', '12:00'])
    dinner_close = random.choice(['21:30', '22:30', '23:00', '23:30'])
    
    return {
        'monday_friday': f'{lunch_start}-{dinner_close}',
        'saturday_sunday': f'10:00-{dinner_close}',
        'closed_days': random.choice([[], ['monday'], []])
    }


def generate_restaurants(num_restaurants=75):
    restaurants = []
    used_names = set()

    for _ in range(num_restaurants):
        cuisine = random.choice(list(CUISINE_NAMES.keys()))

        available_names = [n for n in CUISINE_NAMES[cuisine] if n not in used_names]
        if not available_names:
            continue

        name = random.choice(available_names)
        used_names.add(name)

        location = random.choice(DELHI_LOCATIONS)
        capacity = random.choice([20, 30, 40, 50, 60, 75, 100, 120, 150])
        price_range = random.choices(['₹', '₹₹', '₹₹₹', '₹₹₹₹'], weights=[0.15, 0.4, 0.3, 0.15])[0]
        rating = round(random.uniform(3.6, 4.9), 1)

        features = random.sample(FEATURES, random.randint(3, 7))

        restaurant = {
            'restaurant_id': str(uuid.uuid4()),
            'name': name,
            'cuisine': cuisine,
            'location': location,
            'address': f'{random.randint(1, 200)} {random.choice(["Market Road", "Ring Road", "Main Road", "Block A", "Block C"])}, {location}, New Delhi - {random.choice(DELHI_PIN_CODES)}',
            'capacity': capacity,
            'price_range': price_range,
            'rating': rating,
            'features': features,
            'operating_hours': generate_operating_hours(),
            'phone': f'+91-11-{random.randint(2000, 9999)}-{random.randint(1000, 9999)}',
            'description': f'Authentic {cuisine} dining experience located in {location}, New Delhi'
        }

        restaurants.append(restaurant)

    return restaurants


def save_restaurants(restaurants, filename='restaurants.json'):
    with open(filename, 'w') as f:
        json.dump(restaurants, f, indent=2)
    print(f'Generated {len(restaurants)} restaurants and saved to {filename}')




if __name__ == '__main__':
    restaurants = generate_restaurants(75)
    save_restaurants(restaurants)

    print('\n=== Delhi Restaurant Statistics ===')
    print(f'Total restaurants: {len(restaurants)}')
    print(f'Cuisines: {len(set(r["cuisine"] for r in restaurants))}')
    print(f'Locations: {len(set(r["location"] for r in restaurants))}')
    print(f'Avg capacity: {sum(r["capacity"] for r in restaurants) / len(restaurants):.0f}')
    print(f'Avg rating: {sum(r["rating"] for r in restaurants) / len(restaurants):.1f}')
