# mal-scraper
Web scrapes information from My Anime List in python, then stores the data in SQL (and Excel), then performs analysis in SQL, Excel, and R

===WORK STILL IN PROGRESS===

TODO:
*Investigate sporadic failures
  *With no changes to the code, it sometimes fails to get the URL. MAL might be onto this being a bot.

*Rescrape everything, but without the arbitrary bounds
  *Before doing this, see if any additional data fields are desired
  *Optional: get score of prequel series for use in the regresion

*Edit MALTopScrape to accept custom ranges, but with defaults

*Get data into SQL

*Visualize results of pivot tables
  Optional: use Tableau or Jupyter

*Get data into R
*Perform machine learning / regression analysis on data in R
  *KNN, OLS for predicting score + popularity without using the other
  *Multiple Least Squares for predicting both at the same time
  
*Put results into PPT of no more than 7 slides
  (Any more counts as death by PPT)
 
