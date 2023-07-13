import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)
#Build the URL
def build_URL(job_title, work_arrangement, location):
    job_title_ = job_title.replace(" ", "&20") #for job title
    work_arrangement_ = 1
    match work_arrangement:
        case "on-site":
            work_arrangement_ = 1
        case "hybrid":
            work_arrangement_ = 2
        case "remote":
            work_arrangement_ = 3
        case _:
            work_arrangement_ = 1
    location_ = location.replace(" ", "&20")
    webpage = (f'https://www.linkedin.com/jobs/search/?keywords={job_title_}&location={location_}&f_TPR=r86400&f_WT={work_arrangement_}&position=1&pageNum=0')
    return webpage

#Web Scrapper Logic
def linkedin_scraper(webpage, page_number):
    jobs_list = []
    next_page = webpage + str(page_number)
    response = requests.get(next_page)
    soup = BeautifulSoup(response.content, 'html.parser')

    jobs = soup.find_all('div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
    for job in jobs:
        job_title = job.find('h3', class_='base-search-card__title').text.strip()
        job_company = job.find('h4', class_='base-search-card__subtitle').text.strip()
        job_location = job.find('span', class_='job-search-card__location').text.strip()
        job_link = job.find('a', class_='base-card__full-link')['href']

        job_data = {
            'Title': job_title,
            'Company': job_company,
            'Location': job_location,
            'Apply': job_link
        }
        jobs_list.append(job_data)

    if page_number < 25:
        page_number += 25
        linkedin_scraper(webpage, page_number)

    return jobs_list

#API CODE
@app.route('/', methods=['GET'])
def get_jobs():
    job_title = request.args.get('job_title')
    work_arrangement = request.args.get('work_arrangement')
    location = request.args.get('location')

    webpage = build_URL(job_title,work_arrangement,location)
    page_number = 0
    jobs_list = linkedin_scraper(webpage, page_number)
    if(len(jobs_list)>0):
        return jsonify(jobs_list)
    else:
        'No Jobs Found', 404

if __name__ == '__main__':
    app.run(debug=True)
