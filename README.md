# Instabot
Takes a random hashtag from your latest posts and using selenium, likes up to 9 photos from the top of explore page.

Is designed to work on a Raspberry PI without a display. 

### Instalation
```bash
sudo apt-get update
sudo apt-get install iceweasel xvfb

sudo pip install selenium PyVirtualDisplay xvfbwrapper
```

### Running
Update the variables in `instabotrunner` and then add a cron job to run this file. Ex:
```bash
0 * * * * bash /path/to/repo/instarunner
```
