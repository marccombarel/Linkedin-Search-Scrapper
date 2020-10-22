import random
import requests
import arrow
import argparse
import json
import csv
import flask
import os
from dotenv import load_dotenv
from fake_useragent import UserAgent


load_dotenv()
LI_AT = os.getenv('li_at')
JSESSIONID = os.getenv('JSESSIONID')
date_time_now = arrow.now("Europe/Paris").format("DD-MM-YYYY-hhmm")
FULL_NAMES = []


def generate_fake_user_agent():
	user_agent = UserAgent(verify_ssl=False, use_cache_server=False)
	browsers = ["edge", "google chrome", "firefox", "safari", "opera"]
	return user_agent[random.choice(browsers)]


headers = {"user-agent":"{0}".format(generate_fake_user_agent()),
	"accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
	"accept-encoding": "gzip, deflate, br",
	"accept": "application/vnd.linkedin.normalized+json+2.1",
	"referer": "https://www.linkedin.com/search/results/people/?keywords=WebScrapper&origin=SWITCH_SEARCH_VERTICAL&page=2",
}


def get_data(limit, search):
	start_index = 0
	if limit > 50:
		count = 50
	else: 
		count = limit

	csv_file = "final_results_{0}.csv".format(date_time_now)


	with open('./final_results/'+csv_file, 'w', newline='') as file:
		field_names = ['full_name', 'location', 'headline', 'lkdn_url']
		filewriter = csv.DictWriter(file, fieldnames = field_names)
		filewriter.writeheader()
	

		while limit > len(FULL_NAMES):
			linkedin_base_url =	'https://www.linkedin.com/voyager/api/search/blended?'
			params 	= {
				'count': count,
				'filters': 'List(resultType->PEOPLE)',
				'keywords': search,
				'origin': 'SWITCH_SEARCH_VERTICAL',
				'q': 'all',
				'queryContext': 'List(spellCorrectionEnabled->true,relatedSearchesEnabled->true)',
				'start': start_index,
			}
			start_index = len(FULL_NAMES)+1

			

			with requests.session() as session:

				session.cookies['li_at'] 	  = LI_AT
				session.cookies["JSESSIONID"] = JSESSIONID
				session.headers 			  = headers
				session.headers["csrf-token"] = session.cookies["JSESSIONID"].strip('"')
				response 	   				  = session.get(linkedin_base_url, params=params)
				response_dict  				  = response.json()
				response_array 				  = response_dict["data"]["elements"][0]["elements"]

				for profile in response_array:
					fullName = profile["title"]["text"]
					location = profile["subline"]["text"]
					lkdn_url = profile["navigationUrl"]
					headline = profile["headline"]["text"]

					FULL_NAMES.append(fullName)

					filewriter.writerow({'full_name': fullName, 'location': location, 'headline': headline, 'lkdn_url': lkdn_url,})





def main(limit=None, search=None, from_cli=False):

	if from_cli:
		parser = argparse.ArgumentParser()
		parser.add_argument("-l", "--limit", help="number of profile to scrap", type=int, default=50)
		parser.add_argument("-s", "--search", help="type your boolean search", type=str)
		args = parser.parse_args()
		limit = args.limit
		search = args.search

		if args.search is None:
			print("___________________________________________________________________________________")
			print(" ")
			print("	      Missing boolean search!                      command: -s") 
			print("	          i.e. 'something1' AND ('something2' OR 'something3')")
			print("___________________________________________________________________________________")

	get_data(limit, search)



if __name__ == '__main__':
	main(from_cli=True)