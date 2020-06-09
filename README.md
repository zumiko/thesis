
# Giving By the Numbers 

This thesis investigates the size and nature of peer effects using data collected from the online crowdfunding platform GoFundMe. On a campaign page, the previous five or ten donations are visible to potential donors. This allows for investigation into how the knowledge of these previous donations affects one's own decision to give as well as the size of the donation. I find that people are strongly influenced by the donations that are displayed to them prior to their own donation but the size of the effect is significantly different for men and women. Moreover, the distribution of the displayed donations is important in influencing how people decide to act. 

### rcode 

* `import.Rmd` - importing the scraped csvs 
* `summarystats.Rmd` - summary stats
* `clean.Rmd` - data cleaning and tidying and adding predictors 
* `regs.Rmd` - includes regression models
* `trees.Rmd` - includes tree and boosted tree models

### scraper
* `completemergefixed.py` = pulls campaign desc, organizer, goal amount, amount raised, donor names, donor amounts, nonprofit status from GoFundMe

walking on a tightrope to the sun
