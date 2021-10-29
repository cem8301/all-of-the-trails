# all-of-the-trails
This repo creates an interactive Strava activity tracker, which can be used [here](https://www.giraffesinaboat.com/)! Use the tool to plot your Strava activities, track your travels, and ride/run/paddle/etc all of the trails in your area. The tool is interactive and can further split/ plot your data by type, gear, and year. 

I created this tool as a sandbox to work with the [Strava API](https://developers.strava.com/) as well as learn how to host a website using Digital Ocean's [app platform](https://www.digitalocean.com/products/app-platform/). Here is the result! 

![All my activities from 2016-2021](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/all_zoom2.png)
## How to create your own sandbox
I wanted to open source this code to aid others in their own projects. Feel free to propose ideas here via issues or pull requests. This code is a work and progress and I'm slowly implementing new features. But first, here are the basic steps to replicate my tool, so you can play on your own:

The basic steps:
1) Fork this repo
2) Create your own Strava App
3) Buy a domain name and set it up
4) Create a Digital Ocean account
5) Create a new app and link everything up!
6) See if it worked
 
### In a little more detail (also wip):
#### 1) Fork this repo:
Forking this repo gives you your own copy and allows for experimentation. Follow the [guide](https://docs.github.com/en/get-started/quickstart/fork-a-repo) on github.

#### 2) Create your own Strava App
Here is a link to the Strava developers [getting-started guide](https://developers.strava.com/docs/getting-started/#:~:text=If%20you%20have%20not%20already,api%20and%20create%20an%20app.). It will point you towards creating your own API App and describe what all the pieces mean. 

Once you have your own App, a good place to start is the [API Playground](https://developers.strava.com/playground/). Here you can test out different http requests and see what the responses look like. In order for this to work, read the instructions at the top of the page. The important piece is to set the 'Authorization Callback Domain' on your new strava API to 'developers.strava.com'. Later you  will change this to your own domain. Example here: 
![Setting up strava api to use the playground](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/strava_api.png).

Back to the playground site, click on the 'Authorize` button on the right hand side to enter your newly made 'client_id' and 'client_secret'. Set your scope. I found that all scopes may not work.

If you choose to experiment outside of the playground, please note the verification needed to make the request. The 'client_id' and 'client_secret' are specific to the your new app. When making a request you will specify a scope. These are used to ask the user for authorization for your app to read their data. If the user accepts, then an authorization code is generated and will be used to make requests. 

#### 3) Buy a domain name and set it up
Now that you are familiar with the Strava API, its time to setup your own domain. I bought my domain from https://www.namecheap.com/. But there are many options. I chose to name my site 'giraffesinaboat.com'. 

#### 4) Create a Digital Ocean account
I started by hosting my tool on my laptop, then experimented with options on Digital Ocean. Regardless, you will need a host for all the requests to run from. You can setup an account [here](https://www.digitalocean.com/).

#### 5) Create a new app and link everything up!
Now its time to link everything up. The pieces we need to link up are the domain name, the host, and the code.

In order to link up the domain follow these [instructions](https://www.digitalocean.com/community/tutorials/how-to-point-to-digitalocean-nameservers-from-common-domain-registrars). It is importnat to note that example.com does not equal www.example.com. When following these steps just add the three generated 'ns*.digitalocean.com' values as NS options as desrcibed in the link. In order to save the values without the www, type in '@'. My entries look like this: ![DNS entries on digital ocean networking tab](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/do_dns.png)
Also note, that these steps all take time to propagate. Allow several hours to multiple days for these to take affect. 

You will also need to setup security for your site. You can create an SSL certificate on the digital ocean website. (I need to look into this further).

Next create a new app. Instructions can be found [here](https://docs.digitalocean.com/products/app-platform/). This setup phase, will connect your forked all-of-the-trails repo to be part of app platform. App platform will run automatic builds every time you make a new PR and be made avaliable on your site. On step 2, add your 'STRAVA_CLIENT_ID' and 'STRAVA_CLIENT_SECRET' to the 'Environment Variables' so your code can run queries. Shown here: ![setting up app platform environment variables](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/do_env.png)

Once your app has been created go to the settings page to finish linking up your domain. Make sure to add example.com AND www.example.com. The www is an alias to the first and a CNAME entry will be created in the DNS records. Mine looks like this: ![setting up app platform domains](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/do_domains.png)

I found this piece to be very tricky. Again you must wait for propogation time before you know if it was done correctly.

#### 6) See if it worked
Now everything is connected and should be live! Try navigating to your website. You can review build logs and run time logs on app platform for trouble shooting purposes.


## Some more screen shots from the tool (Just for fun)
I live full time in a van (since spring 2020) so it is fun to see where I have gone each year.

My travels from 2020:
![All my activities from 2020](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/2020.png)

My travels from 2021:
![All my activities from 2021](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/2021.png)

Where I kayaked in New England:
![kayaking new england](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/kayak_ct.png)

Where I have Mountain Biked around Summit County Colorado. Working on getting all of the trails and OHV roads in the area:
![Mountain biking Colorado](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/mtb_co.png)

Zoom into Missoula, MT:
![Missoula MT](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/missoula.png)

Some other fun. Kayaking in the Bob Marshall Wilderness, MT:
![bob marshall trip](https://github.com/cem8301/all-of-the-trails/blob/main/readme_support/bob.png)

That's it. Hope my write-up is somewhat helpful. Still a work in progress with writing code/ sharing it. 
