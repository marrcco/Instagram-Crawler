# Instagram-Crawler
Instagram Followers Crawler

Crawler pulls the data from Google Sheets. Sheet is configured as follows:
Name -> Name of the user/account (optional)
Link -> URL to the IG profile to keep track of followers (required)
type_of_media -> instagram. In the future I'll add twitter, so you can choose between instagram and twitter
type_of_account -> if you want to separate different types of accounts(influencers,singers,athletes,etc.)

After pulling required data Crawler loops through all accounts and scrape followers count. This data will be automatically appended to specified sheet.

# How to use it?

First you'd have to specify type_of_media, type_of_account and sheet_to_update(this is name of the tab where you want to append Crawler results)
crawler = Crawler(type_of_media="instagram",
                  type_of_account="athletes",
                  sheet_to_update="athletes_sheet")

By calling function crawl() Crawler will pull the athletes Instagram accounts from your sheet and scrape followers count.
followers_df = crawler.crawl()

By calling function update_spreadsheet() Crawler will append dataframe to specified sheet_to_update
crawler.update_spreadsheet(followers_df)
                  
