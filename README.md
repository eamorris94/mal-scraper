# mal-scraper
Web scrapes information from My Anime List in python, then outputs the results into Excel

===WORK STILL IN PROGRESS===

Program works by using MALTopScrape(), or by calling MALPageScrape(url) for a single page.


TODO:

*Edit MALTopScrape to accept custom ranges, but with defaults
*Add SQL functionality
*Visualize results of pivot tables
  Optional: use Tableau or Jupyter
*Get data into R
*Perform machine learning / regression analysis on data in R
  *KNN, OLS for predicting score + popularity without using the other
  *Multiple Least Squares for predicting both at the same time
*Put results Tableau for visualization
*multi-thread the scraping process (file takes ~8 hrs to run)
*clean everything. This will always be a thing to do.
 
