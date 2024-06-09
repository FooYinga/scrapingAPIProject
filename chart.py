from pprint import pprint
import requests
from bs4 import BeautifulSoup


class ChartScraper:
    def __init__(self):
        self.base_url = 'https://www.officialcharts.com/charts/singles-chart/'

    def get_chart_data(self, num_items=100):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        chart_items = soup.find_all("div", class_="description block")
        chart_imgs = soup.find_all("div", class_="chart-image")
        chart_data = []
        for i, item in enumerate(chart_items[:num_items], start=1):
            song_name = item.find('a', class_='chart-name font-bold inline-block').text.strip()
            if song_name.startswith(('New', 'RE')):
                song_name = song_name.replace('New', '', 1).replace('RE', '', 1)

            artist_name = item.find('a', class_='chart-artist text-lg inline-block').text.strip()
            song_img = chart_imgs[i - 1].find('img')['src']

            last_week_span = item.find(lambda tag: tag.name == 'span' and 'LW' in tag.text)
            last_week = None
            if last_week_span:
                found_span = last_week_span.find('span')
                if found_span:
                    last_week = found_span.text

            if song_name and artist_name and last_week:
                chart_data.append({'position': i, 'song': song_name, 'artist': artist_name, 'last_week': last_week,
                                   'song_image': song_img})


        return chart_data


scraper = ChartScraper()
chart_data = scraper.get_chart_data(num_items=100)
# pprint(chart_data)
# for data in chart_data:
#     print(data.get('artist'), '-', data.get('song'))
