# Abodo.com python scraping application

**Author**: Farbod G, farbodg@gmail.com

**Description**: This is my submission for a coding assignment which scrapes abodo.com.

**Instructions**: Download chromedriver [here](https://chromedriver.chromium.org/downloads). Set your *PATH* to location of the chromedriver. Navigate to location of the project and do a *pip install -r requirements* to install all necessary libraries. *python app.py* to run the application. You should see the following in your prompt:
```
MacBook-Pro$ python app.py 
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
**Endpoint access**: You can access the endpoint by sending a GET request to ```http://127.0.0.1:5000/properties``` to retrieve properties and their related attributes. To add bedroom and bathroom parameters, pass in the attributes to the URL. For example: . Example: ```http://127.0.0.1:5000/properties?bedrooms=2&bathrooms=1```

**Further notes**: This application utilizes the selenium driver and the requests library to scrape results from Adobo. This means the API call could take a long time (longer than standard API calls) as Selenium will need to traverse Adobo to obtain the initial results, then an individual HTTP request needs to be made for each property to obtain its attributes. In the *services/scraper.py* file, there is a global variable called *result_limit*. It's currently set to 1 to retrieve less properties (quicker api results), but for the assignment, the requirement was to restrict to 200 results so you will need to set to 10 (Adobo lists 20 properties per page) if you want 200 properties. You can also update the zip codes that the scraping tool searches for in the same file.
