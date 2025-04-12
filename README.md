![silly mario banner that says "i am a placeholder: SUPER MARIO BANNER" and the picture is a bunch of fucked up marios in gm_construct](static/banners/placeholderbanner.png)
# tomochan

some type of imageboard (images not implemented yet) using python/flask, and sqlite

TODO:
- file uploads, 3 images by default maybe? also multiple images in the form, also videso and audio probably
- post formatting of some variety (im thinking markdown, and maybe a selector for classical formatting which apparently is bbcode), also greentext
- aesthetics
- \>\>1 replying
- show direct replies in post header (\>\>2 \>\>10)
- board page showing last 5 threads
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
- post archival
- stickies
- blotter
- flags
- captcha? probably with an audio one too
- placeholders of various varieties
- search
- (USER WAS BANNED FOR THIS POST) its a SA thing not originally an imageboard thing but its still just so iconic i gotta have it
- atom/rss???
- qol javascript stuff?
- boardlist/info in db maybe? maybe not?
- figure out what the fuck the checkbox is for on not current day 4chan (too much js shit to really get at the meat and potatoes i mean even the banner is js now its crazy)
- maybe setup a futaba board for reference
- job queueing?
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


markdown things:
- discord style newlines, its just better esp for this kinda thing
- no embedding images sorry you got the file uploader for that
- fancy links will DEFINITELY be toggleable for sure just imagine the abuse cases

image filename scheme:
(post id)_(image number (0-2)).whatever
validated by extension and then mime type
original filename ran through secure_filename before being put in db
