![silly mario banner that says "i am a placeholder: SUPER MARIO BANNER" and the picture is a bunch of fucked up marios in gm_construct](static/banners/placeholderbanner.png)
# tomochan

some type of imageboard (images not implemented yet) using python/flask, and sqlite
VERY WIP DO NOT USE

TODO URGENT:
- catalog
- start truncating post content in board view and in catalog view

- have image sizes display in MB for large images maybe
- separate logic for videos and audio
- truncate long original filenames



TODO less urgent:
- cycling image like the garfield calander on the homepage
- tacky gold theme called "tomo premium"
- sanitize ALL the inputs
- figure out error handling/logging
- beef up the security practices (prob already better than yotsuba tho lol)
- check thread ids in the post code
- figure out better way to render board links list (similar to 4chan) [ b / tomo / nottomo ] (remove trailing /)
- wordfilters (language enhancers)
- start truncating post content in board view and in catalog view
- move more shit to config file
- split into modules
- textboard mode with 2ch type templates
- refactor templates
- save and request name in cookie
- ctrl-enter to send
- better accessibility (deffo alt text on images at least) (DEFINITELY do a pass with a screen reader to test that)
- multiple file uploads
- file size limit
- videos/audio, with thumbnails for video so ffmpeg will probably be involved somehow there
- maybe even pdfs but NOT using ghostscript i do not want to get hacked like 4chan
- allowed filetypes and number of uploads configurable by board
- silly banner ads
- optimize sql queries
- markdown post formatting with discord newlines and also greentext
- aesthetics
- \>\>1 replying
- show direct replies in post header (\>\>2 \>\>10)
- maybe some other email easter eggs besides sage and nonoko? (like dice rolling? definitely #fortune), writing my own fortunes even tho i have all the 4chan ones now because tbh i can do better i can make sillier ones
- other pages, maybe an overboard (/ukko/) or homepage or rules/faq or whatever
- funny 404 pages
- board specific banners
- oekaki would be so epic just imagine
- caching rendered templates for extra performance maybe?
- r9k
- init scripts
- mod view/tools
- mobile, just mobile
- checkbox for post deleting and reporting
- post deletion using the password
- save password in cookie
- tripcodes and capcodes (prob "secure" tripcodes and maybe even tripkeys too)
- bump limits (configurable)
- post archival/falling off the board
- thread list pages
- fun polls?
- blotter
- localizations? at least the architecture for them
- flags
- flood detection, ill need it sooner or later
- proxy detection? Even if i dont use it
- captcha? probably with an audio one too (DEFINITELY NOT RECAPTCHA, a basic one is enough to stop unambitious bots and anything more complicated is never gonna be sufficent to block the ambitious ones)
- possibly altcha?
- placeholders of various varieties
- search (prob just ops by default)
- banning users (youve been banned for (timespan) - take a moment to reflect on your actions and (wait until (date/time) || send an appeal to (appeals email))
- (USER WAS BANNED FOR THIS POST) its a SA thing not originally an imageboard thing but its still just so iconic i gotta have it
- atom/rss???
- qol javascript stuff?
- boardlist/info in db maybe? maybe not?
- maybe setup a yotsuba board for reference (we need not settle for futaba anymore)
- job queueing?
- auto update/refresh js? also tomo ticker (ticker of recent posts/recently bumped threads/new threads MARQUEE IS BACK BAYBEEEEE)
- eventual postgres migration

DONE:
- posting
- displaying posts
- saving posts (NOT using pickle im using sqlite now)
- something better for timestamps
- swatch internet time
- sql db of some type
- threads
- replies
- post ids
- sage and nonoko (im going for modern 4ch behavior there its just actually better defaulting to noko)
- combined sage and nonoko, gotta add that but idk what the thing to combine them is because im at the library and i dont want to open 4chan at the library right now (its nonokosage btw)
- reply button on threads on the board view too
- bumping
- board page showing last 5 threads and replies ommitted
- file uploads
- displaying images on posts
- spoiler image
- add ips into posts table
- stickies
- config file
- hidden boards
- better tabbing on the post form
- REPLY COUNT FOR OPS IN DB REPLY COUNT FOR OPS IN DB!!!!
- FIGURE OUT WHY THE SWATCH TIMESTAMPS ARE FUCKED UP
- image thumbnails
- file size and dimentions in db, kinda goes hand in hand with thumbnails ~~actually i can prob use PIL for both~~ FRIENDSHIP ENDED WITH PIL NOW IMAGEMAGICK IS MY NEW BEST FRIEND

markdown things:
- discord style newlines, its just better esp for this kinda thing
- no embedding images sorry you got the file uploader for that
- fancy links will DEFINITELY be toggleable for sure just imagine the abuse cases

image filename scheme:
(post id)_(image number (0-2)).whatever
validated by extension and then mime type
original filename ran through secure_filename before being put in db


r9k notes:
- check content against content fields
- start hashing images (im pretty sure 4chan r9k checks images too) and check against those hashes (new column in db?)
