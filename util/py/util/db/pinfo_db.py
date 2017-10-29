#!/usr/bin/python3

class PInfo(object):
    # we will not accept anonymous arguments
    # only accept arguments passed through kwargs
    # -- dictionary of named arguments
    def __init__(self, *args, **kwargs):
        self.text = kwargs.get('text')
        self.image_url = kwargs.get('image_url')
        self.video_url = kwargs.get('video_url')
        self.audio_url = kwargs.get('audio_url')
        # Text always set. Only one of Image, Video, or Audio should be set 
        assert(self.text)
        assert(not ((self.image_url and self.video_url) or
                    (self.image_url and self.audio_url) or
                    (self.video_url and self.audio_url)))

    def IsTextOnly(self):
        return not (self.image_url or self.video_url or self.audio_url)

pinfo_db = \
{'pinfo.get':
 {'tesla': PInfo(text =
"""
Tesla is a premium electric Vehicle
Website: http://www.tesla.com.
What would you like to know?"
""", image_url = 'http://images.technewstoday.com.s3.amazonaws.com/tnt/are-automakers-taking-tesla-motors-inc-too-easy.jpg'),
 'nikon': PInfo(text = 
"""
Website: http://www.nikon.com
What would you like to know?"
""", image_url = 'https://en.wikipedia.org/wiki/Nikon#/media/File:Nikon_F4_F4s_Austin_Calhoon_Photograph.jpg')
 },
 'models.get':
 {'tesla' : PInfo(text = 
"""
Telsa has 3 models:
- Model S https://www.tesla.com/models
- Model X https://www.tesla.com/modelx
- Model 3 https://www.tesla.com/model3
""", video_url = 'http://techslides.com/demos/sample-videos/small.mp4')
 },
 'model.get':
 {'tesla' :
  {'Model S':
   PInfo(text = 'Model S: https://www.youtube.com/watch?v=6HtlmNzqQdo',
         image_url = 'http://media.caranddriver.com/images/15q2/657948/2015-tesla-model-s-70d-instrumented-test-review-car-and-driver-photo-658384-s-450x274.jpg'),
   'Model X':
   PInfo(text = 'Model X: https://www.youtube.com/watch?v=KbO6-C2Yajg',
         image_url = 'http://media.zenfs.com/en-US/cms/autos/ConsumerReportsNews/CR-Cars-Inline-2016-Tesla-Model-X-r-open-cliff-04-16.jpg'),
   'Model 3':
   PInfo(text = 'Model 3: https://www.youtube.com/watch?v=CoZXJ0lhy_w',
         image_url = 'https://en.wikipedia.org/wiki/Tesla_Model_3#/media/File:Candy_Red_Tesla_Model_3_trimmed_2.jpg')
  }
 },
 'feature.get':
 {'tesla':
  {'default':
    {'optional-upgrades': PInfo(text =
"""
- List of Optional Upgrades:
  - Autopilot Convenience Features
  - Premium Upgrades Package
  - Smart Air Suspension
  - Subzero Package
  - Ultra High Fidelity Sound
  - Rear Facing Seats
  - High Amperage charger upgrade
"""),
     'gas-savings': PInfo(text =
"""
- $4,400 and $6,600 over 5 years assuming that you drive 
  10,000 to 15,000 miles per year. 
  https://www.tesla.com/models/design
"""),
     'tax-rebates': PInfo(text = 
"""
- In US, the rebates are $7,500. You might also be eligible to state
  sponsored rebates.
""")
    },
   'Model S':
   {'range-per-charge': PInfo(text =
"""
- Model S has several sub-models by Range per Charge
  - 60:   219 MI 
  - 60D:  225 MI
  - 75:   265 MI
  - 75D:  275 MI
  - 90D:  302 MI
  - P90D: 294 MI
"""),
    'price': PInfo(text = 
"""
- Model S has several sub-models and its costs before any 
  tax rebates are
  - 60:   starts at $66,000
  - 60D:  starts at $71,000
  - 75:   265 MI at $74,500
  - 75D:  275 MI at $79,500
  - 90D:  302 MI at $89,500
  - P90D: 294 MI at $112,000
"""),
   },
   'Model X':
   {'range-per-charge': PInfo(text = 
"""
- Range per Charge to be filled
"""),
    'price': PInfo(text =
"""
- Cost and tax rebates to be filled
"""),
   },
   'Model 3':
   {'price': PInfo(text = 
"""
- Cost and tax rebates to be announced
"""),
   },
  }
 }
}

def pinfo_lookup(key_tuple):
    def helper(node, key_coord):
        if node is None:
            return None
        if type(node) is PInfo:
            return node
        if key_coord == len(key_tuple):
            return None

        key_elem = key_tuple[key_coord]
        result = helper(node.get(key_elem), key_coord + 1)

        # !None => result found 
        if result: return result
        
        return helper(node.get('default'), key_coord + 1)
    
    result = helper(pinfo_db, 0)
    if result is None:
        return PInfo(text = "I'm sorry. I could not follow your question")
    return result

def pinfo_unit_tests():
    assert(pinfo_lookup(['feature.get', 'tesla', 'Model S',
                         'optional-upgrades']).text ==
"""
- List of Optional Upgrades:
  - Autopilot Convenience Features
  - Premium Upgrades Package
  - Smart Air Suspension
  - Subzero Package
  - Ultra High Fidelity Sound
  - Rear Facing Seats
  - High Amperage charger upgrade
"""
    )
    assert(pinfo_lookup(['feature.get', 'tesla', 'Model S',
                         'range-per-charge']).text ==
"""
- Model S has several sub-models by Range per Charge
  - 60:   219 MI 
  - 60D:  225 MI
  - 75:   265 MI
  - 75D:  275 MI
  - 90D:  302 MI
  - P90D: 294 MI
"""
    )
    assert(pinfo_lookup(['feature.get', 'tesla', 'Model X',
                         'optional-upgrades']).text ==
"""
- List of Optional Upgrades:
  - Autopilot Convenience Features
  - Premium Upgrades Package
  - Smart Air Suspension
  - Subzero Package
  - Ultra High Fidelity Sound
  - Rear Facing Seats
  - High Amperage charger upgrade
"""
    )
    assert(pinfo_lookup(['feature.get', 'tesla', 'Model 3',
                          'range-per-charge']).text ==
           "I'm sorry. I could not follow your question")
    print("pinfo_unit_tests: All tests passed")

if __name__ == "__main__":
    pinfo_unit_tests()
