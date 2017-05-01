import asyncio
import random
import re
import requests

moons=['apple_new_moon_with_face',
       'apple_full_moon_with_face',
       'apple_ios10_new_moon_with_face',
       'apple_ios10_full_moon_with_face',
       'noto_new_moon_with_face',
       'noto_full_moon_with_face',
       'segoe_new_moon_with_face',
       'segoe_full_moon_with_face',
       'apple_new_moon',
       'apple_full_moon',
       'apple_ios10_new_moon',
       'apple_ios10_full_moon',
       'noto_new_moon',
       'noto_full_moon',
       'segoe_new_moon',
       'segoe_full_moon'
]

moons_baseurl="https://util.fiveyellowmice.com/contaminative-moons/gen-image.php"
moons_args="?width={width}&height={height}&count={count}&background={background}&format={format}&moons={moons}"


def upload(file):
    files = {'name': file}
    text=requests.post(url="https://img.yoitsu.moe",files=files).text
    return text

def getmoon(*moons,width=800,height=600,count=16,background='black',format='jpeg'):
    '''get a contaminative moon from FiveYellowMice.'''
    query_url=moons_baseurl+moons_args.format(width=width,height=height,count=count,background=background,format=format,moons=';'.join(moons))
    return requests.get(query_url).content

@asyncio.coroutine
def moon(arg,send):
    try:
        text=upload(getmoon("{},{},{}".format(random.choice(moons),random.uniform(0.01,0.5),random.uniform(0.5,1))))
    except requests.exceptions.RequestException as err:
        text="Failed to process request:"+str(err)
    finally:
        send(text)



help = [
    ('moon'            , '-- Contaminative Moons, made with 🌚 by FiveYellowMice.'),
]

func = [
    (moon              , r"moon"),
]
