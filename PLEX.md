Plex

I recently started looking at switching from my current PVR solution (Tvheadend) to Plex.  The problem with that is that, because Plex is a fully featured media server, there is no way to tell it to dump all the recordings in to a single folder, so my current script doesn't work.

To fix that, and as I was a little curious, I decided to see if ChatGPT (https://chat.openai.com/) could do the job.  The answer is obviously yes but it was a mildly painful process as, at least with the free tier, ChatGPT apparently has Alzheimer's and regularly forgot changes I had asked it to make previously.  This meant a lot of repeating myself and then copying the code I wanted it to use so it hopefully wouldn't keep breaking one thing when it fixed another.

Anway, I have been using this script for a few months now and it seems to be working.  I did have to add a VIDEOS constant at the top and change a couple of hard-coded paths in the final section as they were pointing to my Videos folder, and I hadn't noticed before.  I have only briefly tested but my changes seem to work there.

So, in case you had a Plex setup, or wanted to use folders, there is now a plex.py script.  You can run it on its own or make both scripts run one after the other in a cron job just by separating the two paths with a semicolon something like:

*/5 * * * * /home/$USER/VRD-Watcher/vrdwatch.py; /home/$USER/VRD-Watcher/plex.py 2>&1 /home/$USER/Videos/vrdwatch_cron.log

The above should also ouptut an error if there's something wrong with the cron job.

Enjoy!
