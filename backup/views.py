from django.shortcuts import render
import requests
import time

API_KEY = 'AIzaSyAzU7gIQjilPaew6gaOXAV7ngAZygf4KXY'
SEARCH_RADIUS = 50 * 1609.34  # 50 miles to meters
MIN_RATING = 4.3
MIN_REVIEWS = 30

def get_repair_shops(search_query, zip_code):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_query}+repair+shop+near+{zip_code}&radius={SEARCH_RADIUS}&key={API_KEY}"
    shops = []

    while url:
        response = requests.get(url)
        result = response.json()
        for shop in result['results']:
            if shop.get('rating', 0) >= MIN_RATING and shop.get('user_ratings_total', 0) > MIN_REVIEWS:
                place_id = shop['place_id']
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={API_KEY}"
                details_response = requests.get(details_url)
                details_result = details_response.json().get('result', {})
                phone_number = details_result.get('formatted_phone_number', 'N/A')
                website = details_result.get('website', 'N/A')
                shop['phone_number'] = phone_number
                shop['website'] = website
                shops.append(shop)
        url = None
        if 'next_page_token' in result:
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={result['next_page_token']}&key={API_KEY}"
            time.sleep(2)  # Delay to allow the next_page_token to become valid
    return shops

def shop_list(request):
    make = request.GET.get('make', '')  # Default to empty string if no make is provided
    category = request.GET.get('category', '')  # Default to empty string if no category is provided
    zip_code = request.GET.get('zip_code', '36301')  # Default to '36301'
    search_query = f"{make} {category}".strip()
    shops = get_repair_shops(search_query, zip_code)
    return render(request, 'shops/shop_list.html', {'shops': shops, 'make': make, 'category': category, 'zip_code': zip_code})
