# Lab session #3: Use of cloud services programmatically through their API

In this lab session, you’ll learn how to extract data from web pages and analyze images and videos using **AWS Rekognition** to uncover insightful information.

### Tools you'll use:

- **[Scrapy](https://scrapy.org/):** A powerful Python framework for scalable web scraping. It provides the necessary tools to extract data efficiently, process it as needed, and [store it in various formats](https://doc.scrapy.org/en/latest/topics/feed-exports.html).
- **[AWS Rekognition](https://aws.amazon.com/rekognition/):** A cloud-based image analysis service that can detect objects, scenes, faces, landmarks, and inappropriate content. It can also extract text, identify celebrities, and assess image quality and dominant colors.

## Pre-lab task

Using what you have learned from the AWS Academy Module 4 - AWS Cloud Security - create a new **programmatic user** named **lab3_user** that will have access to the AWS Rekognition service and any additional assets necessary to execute this lab session. The user will only be used inside the application.

1. At the AWS IAM console create a new user.
2. Attach policies directly (not through a group or copying permissions) setting "Rekognition full access".
3. Once the user is created, edit its "Security credentials" and add an "access key" of type "Application running outside AWS".
4. You can either "Download .csv file" or copy the "Access key" and "Secret access key" in your password manager. Please, if you decide to download the .csv file put it on a very safe place since anybody may use the credentials to consume the services that you will end up paying for.

> [!Important]
> Don't forget to use the *"principle of least privilege"* when creating and managing the programmatic user.


## Lab Tasks Overview
- [**Task 3.1: Expand Your AWS Cloud Knowledge**](#Task31)
- [**Task 3.2: Extract images from a website**](#Task32)
- [**Task 3.3: Obtain insights about an image using AWS Rekognition**](#Task33)
- [**Task 3.4: Get Insights From Website Images Using AWS Rekognition**](#Task34)

<a id="Task31" />

## Task 3.1: Expand Your AWS Cloud Knowledge

Study the following AWS Academy modules and complete the associated labs:

> [!Important]
> Each student must **individually** complete the AWS Academy knowledge checks as part of the course requirements.
> 
> :bangbang: Complete only the laboratories specified below.


- **Module 8 – Databases**

  > :question: **Question 1:** Include screenshots of key steps and briefly explain what you learned or observed.

  > :test_tube: **Laboratory 5:** *Build a Database Server*

- **Module 9 – Cloud Architecture**  

  > :question: **Question 2:** Include screenshots of key steps and briefly explain what you learned or observed.

- **Module 10 – Auto Scaling and Monitoring**  

  > :question: **Question 3:** Include screenshots of key steps and briefly explain what you learned or observed.

  > :test_tube: **Laboratory 6:** *Scale & Load Balance your Architecture*

<a id="Task32" />

## Task 3.2: Extract Images from a Website


Read the official [Scrapy tutorial](https://doc.scrapy.org/en/latest/intro/tutorial.html) and [documentation](https://doc.scrapy.org/en/latest/) to get started.

### Installing Scrapy

Install Scrapy using pip:

```bash
pip install scrapy
```

### Scrapy shell

Once the Scrapy package is installed, you can use the Scrapy shell to do some testing before programming your web data extraction. 

In the following example, we download the home page
of ["Universitat Politècnica de Catalunya"](https://www.upc.edu/). Please, inspect the structure of the HTML, and extract the images included in each page. As you can see we can use a CSS syntax to select the HTML elements of the page.

```python
fetch("https://www.upc.edu/")
print(response.text)
response.css("img").extract_first()
response.css("a").extract_first()
```

> [!Tip]
> Use Chrome DevTools to inspect page structure and find CSS selectors.

### Creating a Custom Scrapy Spider

Start a new Scrapy project:

```bash
_$ scrapy startproject imageScraper
```

This will generate a project folder like this:

 <img src="images/Lab03-imageScraper.png"  width="30%">

### Limit Crawl Depth

The most important components are the file `imageScraper/settings.py` containing the settings for the project and the directory `imageScraper/spiders/` that keeps all the custom spiders.

The [crawl depth](https://www.wordstream.com/crawl-depth) is referred to the distance between the first page visited and the page in question. To restrict crawling depth, set the following in `settings.py`:

```python
DEPTH_LIMIT = 1
```

If you begin by crawling the home page of a website, pages with low depth limit are more important than pages with high
depth limit because users are not going to be reaching them as easily.

<img src="images/Lab03-crawl-depth-tree.jpg" width="50%"/>

### Create and Edit the Spider

Navigate into your project and generate the spider:

```bash
cd imageScraper
scrapy genspider images www.upc.edu
```

The execution creates a file named `imageScraper/spiders/images.py` inside the project directory. The file contains the following basic code:

```python
import scrapy

class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['www.upc.edu']
    start_urls = ['http://www.upc.edu/en/']

    def parse(self, response):
        pass
```

Few things to note here:

- **name**: Name of the spider, in this case, it is “images”. Naming spiders properly is essential when you have to
  maintain hundreds of spiders.
- **allowed_domains**: An optional list of strings containing domains that this spider is allowed to crawl. Requests for
  URLs not belonging to the domain names specified in this list won’t be followed.
- **parse(self, response)**: This function is called whenever the crawler successfully crawls a URL. Remember the
  response object from earlier?.

After every successful crawl the *parse(..)* method is called, and so that’s where you write your extraction logic.

Now update `parse()` to extract images:

```python
import scrapy
from urllib.parse import urljoin

class ImagesSpider(scrapy.Spider):
    name = "images"
    allowed_domains = ["www.upc.edu"]
    start_urls = ["https://www.upc.edu/en/"]

    def parse(self, response):
        # Extract image URLs
        for img in response.css("img").getall():
            image_src = img.attrib.get('src') or img.attrib.get('data-src')  # Fallback to 'data-src'
            if image_src is not None:
                full_image_url = urljoin(response.url, image_src)
                yield {
                    'img_url': full_image_url,
                    'appears_url': response.url,
                    'depth': response.meta.get('depth', 0)
                }
```

Once the homepage has been crawled we can continue crawling the rest of the URLs that appear in the page by selecting
the tag **a** (anchor) with the attribute **href**.

```python
# Extract and follow hyperlinks
for link in response.css('a::attr(href)').getall():
    # Ensure the link is absolute
    absolute_link = urljoin(response.url, link)
    # Follow the link and call the parse method recursively
    if absolute_link and absolute_link.startswith('https://'):  # Validating full link
        yield scrapy.Request(url=absolute_link, callback=self.parse)
```

We can feed the crawler with all the URLs found. The only URLs that will be crawled will be the ones matching the
allowed_domains and the DEPTH_LIMIT defined.

```python
    allowed_domains = ["www.upc.edu"]
```

We need to get the list of unique images found. It is possible to define `unique_images` inside the `ImagesSpider`
class.

```python
    unique_images = []
```

We'll add the images to the list only if it is not already present.

```python
if full_image_url not in self.unique_images:
    self.unique_images.append(full_image_url)
```

`closed` is a method that can be defined in class `ImagesSpider` and it is invoked once all the URLs have been crawled.

```python

def closed(self, cause):
    self.unique_images.sort()
    print(self.unique_images)
```

The above code yields a JSON record containing something like the following example:

```json
{
  "img_url": "https://www.upc.edu/++theme++homeupc/assets/images/Logo.svg",
  "appears_url": "https://www.upc.edu/ca",
  "depth": 0
}
```

### Export Results

To export extracted images to a JSON file:

```bash
scrapy crawl images -o images.json
```

### Debug in PyCharm

To debug via PyCharm, create a `main.py` file, in the same directory containing `scrapy.cnf`, with:

```python
from scrapy import cmdline

cmdline.execute("scrapy crawl images -o images.json".split())
```

 <img src="images/Lab03-pycharmConfig.png" width="50%">


> :question: **Question 4**: Reflect on the tasks above. What did you find interesting or challenging? Share your thoughts.

<a id="Task33" />

## Task 3.3: Obtain Insights About an Image Using AWS Rekognition

To get hands-on with **Amazon Rekognition**, you'll begin by using the AWS Console Rekognition demo, followed by writing a Python script that interacts with Rekognition through the AWS API.


### Step 1: Try the Rekognition Demo

1. Log into your AWS console.
2. Search for **Amazon Rekognition** and open the service.
3. Use the demo interface to experiment with:
   - The sample image provided in the demo.
   - Any images you collected using Scrapy in the previous task.

<img src="images/Lab03-sampleImage.jpeg" width="50%"/>
<img src="images/Lab03-RekognitionDemo.png" width="50%"/>


> :question: **Question 5**: Share your thoughts about the Rekognition demo.
> What did you observe? Was anything surprising or particularly useful?

### Step 2: Analyze an Image Programmatically Using Python

#### Create a configuration file

Idenfify the values for the variables below and write its value on a ".env" file that will be **excluded** to be synchronized using git.

- AWS_REGION
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

> [!Caution]
> Any git repo containing credentials will automatically be evaluated with a zero, and there is no exception to this. Beware that the git repo contains the values of the credentials even if you make the mistake and then delete the .env file. Hackers (and anybody else) may access any git repo history. Configure your **.gitignore** to prevent that from happening.

#### Write a Python Script to Call Rekognition

Use the script provided in [`Recognize_1.py`](Lab03/Recognize_1.py) as a template. This script uses the [`boto3` library](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) to interact with the [Rekognition API](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html) and returns detected features from the image.

> [!Warning]
> Please make sure that you are not analyzing the same image over and over again since that is going to cause a huge expense on your AWS account. Implement a mechanism to prevent that from happening.


```python
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

with open('./images/Lab03-sampleImage.jpeg', 'rb') as fd:
    image = fd.read()

recognize = boto3.client('rekognition',
                         region_name=os.getenv('AWS_REGION'),
                         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         )
labels_list = recognize.detect_labels(Image={'Bytes': image}, MaxLabels=10, MinConfidence=70)
print(json.dumps(labels_list, indent=4))
```

```json
{
  "Labels": [
    {
      "Name": "Crowd",
      "Confidence": 99.99995422363281,
      "Instances": [],
      "Parents": [
        {
          "Name": "Person"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Person Description"
        }
      ]
    },
    {
      "Name": "Person",
      "Confidence": 99.99995422363281,
      "Instances": [
        {
          "BoundingBox": {
            "Width": 0.12894393503665924,
            "Height": 0.35750454664230347,
            "Left": 0.4808120131492615,
            "Top": 0.3740279972553253
          },
          "Confidence": 99.70088958740234
        },
        {
          "BoundingBox": {
            "Width": 0.11610560119152069,
            "Height": 0.4229159355163574,
            "Left": 0.0818672701716423,
            "Top": 0.2698194086551666
          },
          "Confidence": 99.66973876953125
        },
        {
          "BoundingBox": {
            "Width": 0.21254201233386993,
            "Height": 0.37966635823249817,
            "Left": 0.7135862112045288,
            "Top": 0.40775251388549805
          },
          "Confidence": 99.6224136352539
        },
        {
          "BoundingBox": {
            "Width": 0.1125546246767044,
            "Height": 0.32264119386672974,
            "Left": 0.27944132685661316,
            "Top": 0.3795841634273529
          },
          "Confidence": 99.5901870727539
        },
        {
          "BoundingBox": {
            "Width": 0.1910828799009323,
            "Height": 0.30100688338279724,
            "Left": 0.20694220066070557,
            "Top": 0.6622647047042847
          },
          "Confidence": 99.55730438232422
        },
        {
          "BoundingBox": {
            "Width": 0.18923720717430115,
            "Height": 0.3014851212501526,
            "Left": 0.39241740107536316,
            "Top": 0.6974440217018127
          },
          "Confidence": 98.555419921875
        },
        {
          "BoundingBox": {
            "Width": 0.22100703418254852,
            "Height": 0.281598836183548,
            "Left": 0.5547536611557007,
            "Top": 0.7183756232261658
          },
          "Confidence": 98.39226531982422
        },
        {
          "BoundingBox": {
            "Width": 0.2582959532737732,
            "Height": 0.2904464602470398,
            "Left": 0.6936929821968079,
            "Top": 0.7093237042427063
          },
          "Confidence": 98.30375671386719
        },
        {
          "BoundingBox": {
            "Width": 0.15318384766578674,
            "Height": 0.30458614230155945,
            "Left": 0.7919331192970276,
            "Top": 0.6382029056549072
          },
          "Confidence": 97.72750091552734
        },
        {
          "BoundingBox": {
            "Width": 0.13399796187877655,
            "Height": 0.2561280429363251,
            "Left": 0.6102837324142456,
            "Top": 0.611282229423523
          },
          "Confidence": 97.62276458740234
        },
        {
          "BoundingBox": {
            "Width": 0.14009936153888702,
            "Height": 0.15651848912239075,
            "Left": 0.17773200571537018,
            "Top": 0.618211567401886
          },
          "Confidence": 95.98444366455078
        },
        {
          "BoundingBox": {
            "Width": 0.14211870729923248,
            "Height": 0.179799884557724,
            "Left": 0.03909475356340408,
            "Top": 0.5740248560905457
          },
          "Confidence": 95.24139404296875
        },
        {
          "BoundingBox": {
            "Width": 0.1584833562374115,
            "Height": 0.29877763986587524,
            "Left": 0.0796993225812912,
            "Top": 0.700888454914093
          },
          "Confidence": 95.08063507080078
        },
        {
          "BoundingBox": {
            "Width": 0.16035592555999756,
            "Height": 0.2708810567855835,
            "Left": 0.0003941879840567708,
            "Top": 0.7290992140769958
          },
          "Confidence": 92.44922637939453
        },
        {
          "BoundingBox": {
            "Width": 0.035537686198949814,
            "Height": 0.07679184526205063,
            "Left": 0.01201602816581726,
            "Top": 0.6788983941078186
          },
          "Confidence": 84.72416687011719
        }
      ],
      "Parents": [],
      "Aliases": [
        {
          "Name": "Human"
        }
      ],
      "Categories": [
        {
          "Name": "Person Description"
        }
      ]
    },
    {
      "Name": "Audience",
      "Confidence": 99.96797943115234,
      "Instances": [],
      "Parents": [
        {
          "Name": "Crowd"
        },
        {
          "Name": "Person"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Performing Arts"
        }
      ]
    },
    {
      "Name": "Chair",
      "Confidence": 99.93281555175781,
      "Instances": [
        {
          "BoundingBox": {
            "Width": 0.14681798219680786,
            "Height": 0.2093701958656311,
            "Left": 0.4752836525440216,
            "Top": 0.5199379920959473
          },
          "Confidence": 99.93281555175781
        },
        {
          "BoundingBox": {
            "Width": 0.153163880109787,
            "Height": 0.17988941073417664,
            "Left": 0.24217256903648376,
            "Top": 0.55253666639328
          },
          "Confidence": 99.77008819580078
        },
        {
          "BoundingBox": {
            "Width": 0.14017456769943237,
            "Height": 0.08491340279579163,
            "Left": 0.7451263666152954,
            "Top": 0.9150865077972412
          },
          "Confidence": 97.67218780517578
        },
        {
          "BoundingBox": {
            "Width": 0.15577459335327148,
            "Height": 0.2323492467403412,
            "Left": 0.7789000868797302,
            "Top": 0.5389119982719421
          },
          "Confidence": 97.0833740234375
        },
        {
          "BoundingBox": {
            "Width": 0.06615076959133148,
            "Height": 0.08635266125202179,
            "Left": 0.6475703716278076,
            "Top": 0.8072365522384644
          },
          "Confidence": 75.36813354492188
        }
      ],
      "Parents": [
        {
          "Name": "Furniture"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Furniture and Furnishings"
        }
      ]
    },
    {
      "Name": "Microphone",
      "Confidence": 99.73712921142578,
      "Instances": [
        {
          "BoundingBox": {
            "Width": 0.04608222842216492,
            "Height": 0.05529649555683136,
            "Left": 0.07135389000177383,
            "Top": 0.3253592550754547
          },
          "Confidence": 99.73712921142578
        }
      ],
      "Parents": [
        {
          "Name": "Electrical Device"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Technology and Computing"
        }
      ]
    },
    {
      "Name": "Adult",
      "Confidence": 99.70088958740234,
      "Instances": [
        {
          "BoundingBox": {
            "Width": 0.12894393503665924,
            "Height": 0.35750454664230347,
            "Left": 0.4808120131492615,
            "Top": 0.3740279972553253
          },
          "Confidence": 99.70088958740234
        },
        {
          "BoundingBox": {
            "Width": 0.11610560119152069,
            "Height": 0.4229159355163574,
            "Left": 0.0818672701716423,
            "Top": 0.2698194086551666
          },
          "Confidence": 99.66973876953125
        },
        {
          "BoundingBox": {
            "Width": 0.21254201233386993,
            "Height": 0.37966635823249817,
            "Left": 0.7135862112045288,
            "Top": 0.40775251388549805
          },
          "Confidence": 99.6224136352539
        },
        {
          "BoundingBox": {
            "Width": 0.1910828799009323,
            "Height": 0.30100688338279724,
            "Left": 0.20694220066070557,
            "Top": 0.6622647047042847
          },
          "Confidence": 99.55730438232422
        },
        {
          "BoundingBox": {
            "Width": 0.2582959532737732,
            "Height": 0.2904464602470398,
            "Left": 0.6936929821968079,
            "Top": 0.7093237042427063
          },
          "Confidence": 98.30375671386719
        },
        {
          "BoundingBox": {
            "Width": 0.15318384766578674,
            "Height": 0.30458614230155945,
            "Left": 0.7919331192970276,
            "Top": 0.6382029056549072
          },
          "Confidence": 97.72750091552734
        }
      ],
      "Parents": [
        {
          "Name": "Person"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Person Description"
        }
      ]
    },
    {
      "Name": "Female",
      "Confidence": 99.70088958740234,
      "Instances": [
        {
          "BoundingBox": {
            "Width": 0.12894393503665924,
            "Height": 0.35750454664230347,
            "Left": 0.4808120131492615,
            "Top": 0.3740279972553253
          },
          "Confidence": 99.70088958740234
        },
        {
          "BoundingBox": {
            "Width": 0.11610560119152069,
            "Height": 0.4229159355163574,
            "Left": 0.0818672701716423,
            "Top": 0.2698194086551666
          },
          "Confidence": 99.66973876953125
        },
        {
          "BoundingBox": {
            "Width": 0.21254201233386993,
            "Height": 0.37966635823249817,
            "Left": 0.7135862112045288,
            "Top": 0.40775251388549805
          },
          "Confidence": 99.6224136352539
        },
        {
          "BoundingBox": {
            "Width": 0.1910828799009323,
            "Height": 0.30100688338279724,
            "Left": 0.20694220066070557,
            "Top": 0.6622647047042847
          },
          "Confidence": 99.55730438232422
        },
        {
          "BoundingBox": {
            "Width": 0.2582959532737732,
            "Height": 0.2904464602470398,
            "Left": 0.6936929821968079,
            "Top": 0.7093237042427063
          },
          "Confidence": 98.30375671386719
        },
        {
          "BoundingBox": {
            "Width": 0.15318384766578674,
            "Height": 0.30458614230155945,
            "Left": 0.7919331192970276,
            "Top": 0.6382029056549072
          },
          "Confidence": 97.72750091552734
        }
      ],
      "Parents": [
        {
          "Name": "Person"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Person Description"
        }
      ]
    },
    {
      "Name": "Woman",
      "Confidence": 99.70088958740234,
      "Instances": [
        {
          "BoundingBox": {
            "Width": 0.12894393503665924,
            "Height": 0.35750454664230347,
            "Left": 0.4808120131492615,
            "Top": 0.3740279972553253
          },
          "Confidence": 99.70088958740234
        },
        {
          "BoundingBox": {
            "Width": 0.11610560119152069,
            "Height": 0.4229159355163574,
            "Left": 0.0818672701716423,
            "Top": 0.2698194086551666
          },
          "Confidence": 99.66973876953125
        },
        {
          "BoundingBox": {
            "Width": 0.21254201233386993,
            "Height": 0.37966635823249817,
            "Left": 0.7135862112045288,
            "Top": 0.40775251388549805
          },
          "Confidence": 99.6224136352539
        },
        {
          "BoundingBox": {
            "Width": 0.1910828799009323,
            "Height": 0.30100688338279724,
            "Left": 0.20694220066070557,
            "Top": 0.6622647047042847
          },
          "Confidence": 99.55730438232422
        },
        {
          "BoundingBox": {
            "Width": 0.2582959532737732,
            "Height": 0.2904464602470398,
            "Left": 0.6936929821968079,
            "Top": 0.7093237042427063
          },
          "Confidence": 98.30375671386719
        },
        {
          "BoundingBox": {
            "Width": 0.15318384766578674,
            "Height": 0.30458614230155945,
            "Left": 0.7919331192970276,
            "Top": 0.6382029056549072
          },
          "Confidence": 97.72750091552734
        }
      ],
      "Parents": [
        {
          "Name": "Adult"
        },
        {
          "Name": "Female"
        },
        {
          "Name": "Person"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Person Description"
        }
      ]
    },
    {
      "Name": "Speech",
      "Confidence": 99.23688507080078,
      "Instances": [],
      "Parents": [
        {
          "Name": "Audience"
        },
        {
          "Name": "Crowd"
        },
        {
          "Name": "Person"
        }
      ],
      "Aliases": [
        {
          "Name": "Public Speaking"
        }
      ],
      "Categories": [
        {
          "Name": "Actions"
        }
      ]
    },
    {
      "Name": "People",
      "Confidence": 98.7227783203125,
      "Instances": [],
      "Parents": [
        {
          "Name": "Person"
        }
      ],
      "Aliases": [],
      "Categories": [
        {
          "Name": "Person Description"
        }
      ]
    }
  ],
  "LabelModelVersion": "3.0",
  "ResponseMetadata": {
    "RequestId": "0ea0a699-dc16-45e9-8a13-028aac977a45",
    "HTTPStatusCode": 200,
    "HTTPHeaders": {
      "x-amzn-requestid": "0ea0a699-dc16-45e9-8a13-028aac977a45",
      "content-type": "application/x-amz-json-1.1",
      "content-length": "7779",
      "date": "Tue, 11 Mar 2025 17:32:47 GMT"
    },
    "RetryAttempts": 0
  }
}
```

#### Compare Console Demo vs JSON Output

Once you’ve tested Rekognition using both the **AWS Console demo** and your **Python script**, compare the **JSON response** from your script with the web demo results.

Focus particularly on the following fields:
- **`BoundingBox`**: Represents the coordinates of detected objects/faces relative to the image.
- **`Confidence`**: Percentage indicating how confident Rekognition is about the detection.

> :question: **Question 6**: What differences or similarities did you find between the JSON output and the console demo?
> Which one provides more usable information, and why?


<a id="Task34" />

## Task 3.4: Get Insights From Website Images Using AWS Rekognition

Let’s now build a Python application that extracts **insights from web images** using Rekognition.

> [!Warning]
> Please make sure that you are not analyzing the same image over and over again since that is going to cause a huge expense on your AWS account. Implement a mechanism to prevent that from happening.

You may combine the following:
- [`requests`](https://pypi.org/project/requests/) – to fetch images from URLs
- [`boto3`](https://boto3.amazonaws.com/) – to interact with AWS Rekognition
- Optional: **Amazon S3** – if you're using Rekognition features that require S3-stored images, use [`S3.py`](Lab03/S3.py) as a template.

### Sample Application Structure

Here’s a starter snippet you can build on. This version assumes:
- You **download an image from a URL**
- You **upload it to an S3 bucket**
- You **analyze it using Rekognition**

```python
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Define the name of the S3 bucket
BUCKET = 'lab03-main.ccbda.upc.edu'

# Create an S3 client using boto3 and credentials loaded from environment variables
s3 = boto3.client(
    's3',  # Specify that it is an S3 client
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Specify the name of the object to be uploaded to S3
objectName = 'sample_image.jpg'

# Open the file located at './images/Lab03-sampleImage.jpeg' in binary read mode
with open('./images/Lab03-sampleImage.jpeg', 'rb') as fd:
    # Read the content of the file as binary data
    image = fd.read()
    # Upload the binary data (image) to the specified S3 bucket with the given object name
    s3.put_object(Bucket=BUCKET, Body=image, Key=objectName)

# Open (or create) a file named 'downloaded.jpeg' in binary write mode to save the downloaded object
with open('./downloaded.jpeg', 'wb') as fd:
    # Retrieve the object from the S3 bucket using its key
    response = s3.get_object(Bucket=BUCKET, Key=objectName)
    # Write the content of the downloaded object to the local file
    fd.write(response['Body'].read())
```

Think of an interesting purpose for your image analysis application and begin exploring.

> :question: **Question 7**: What is the **goal** of your image analysis application?
> (E.g., detecting objects, filtering inappropriate content, facial recognition, etc.)
> 
> Add the Python code of your image analysis application to the repo.

> :question: **Question 8**: What is the mechanism that you have created to prevent sending the same image to AWS Rekognition more than once?


## Submit Your Assignment

> :question: **Question 9:** How much time did you spend on this session?  

> :question: **Question 10:** Using the AWS Billing and Cost Management Service, access the "Cost Explorer"  and capture the cost of last week Using the "Dimension" "Service" where you can see how much did you spend to complete the session in total and per  service.
  
> :question: **Question 11:** What challenges did you encounter, and how did you overcome them?

Push your updated repository to GitHub https://github.com/CCBDA-UPC/2026_1-3-xx **before the deadline**, including:

- `README.md` with all your responses and documentation
- Any screenshots
- All new Python files required by the tasks