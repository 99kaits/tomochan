![silly mario banner that says "i am a placeholder: SUPER MARIO BANNER" and the picture is a bunch of fucked up marios in gm_construct](static/banners/placeholderbanner.png)
# tomochan

some type of imageboard (images not implemented yet) using python/flask, and sqlite

TODO:
- refactor templates
- multiple file uploads
- image thumbnails
- file size and dimentions in db
- videos/audio
- allowed filetypes and number of uploads configurable by board
- optimize sql queries
- post formatting of some variety (im thinking markdown, and maybe a selector for classical formatting which apparently is bbcode), also greentext
- aesthetics
- \>\>1 replying
- show direct replies in post header (\>\>2 \>\>10)
- maybe some other email easter eggs besides sage and nonoko? (like dice rolling? deffo #fortune)
- other pages, maybe an /ukko/ or homepage or rules/faq or whatever
- funny 404 pages
- board specific banners
- oekaki would be so epic just imagine
- caching rendered templates for extra performance maybe?
- config file
- init scripts
- mod view/tools
- mobile, just mobile
- password for delete
- tripcodes and capcodes
- bump limits (configurable)
- catalog
- post archival
- fun polls?
- blotter
- localizations? at least the architecture for them
- flags
- flood detection, ill need it sooner or later
- proxy detection? Even if i dont use it
- captcha? probably with an audio one too (DEFINITELY NOT RECAPTCHA, a basic one is enough to stop unambitious bots and anything more complicated is never gonna be sufficent to block the ambitious ones)
- placeholders of various varieties
- search (prob just ops by default)
- banning users (youve been banned for (timespan) - take a moment to reflect on your actions and (wait until (date/time) || send an appeal to (appeals email))
- (USER WAS BANNED FOR THIS POST) its a SA thing not originally an imageboard thing but its still just so iconic i gotta have it
- atom/rss???
- qol javascript stuff?
- boardlist/info in db maybe? maybe not?
- checkbox for post deleting and reporting
- maybe setup a futaba board for reference
- job queueing?
- auto update/refresh js? also tomo ticker (ticker of recent posts/recently bumped threads/new threads)
- if i make my own futaba/yotsuba esque theme call it mitsuba
- maybe an eventual rewrite with kotlin/postgres?????? idk?????????

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



markdown things:
- discord style newlines, its just better esp for this kinda thing
- no embedding images sorry you got the file uploader for that
- fancy links will DEFINITELY be toggleable for sure just imagine the abuse cases

image filename scheme:
(post id)_(image number (0-2)).whatever
validated by extension and then mime type
original filename ran through secure_filename before being put in db
