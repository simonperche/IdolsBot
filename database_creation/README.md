# KPop Database Creation

A KPop Idols database in multiple formats. All data come from [kpopping](https://kpopping.com).

## Tasks

| Feature                     | Progress     |
|-----------------------------|--------------|
| Extract to JSON format      | Done         |
| JSON to SQL                 | Done         |
| Better extraction of images | To do        |

## Database
### JSON
JSON file is made with the following format :
```json
{"id":
    {"url":     "url_of_kpopping_page",
     "name" :   "name_of_idol",
     "groups":  ["group1", "group2"],
     "img_url": ["img1", "img2"]
    }
}
```

Execute `extract_to_json.py` to create `database.json` with this format. 
All fields are mandatory so if an idol does not have group or image, 
he/she will not be kept in the final file.

#### Field example
```json
{"166": 
  {"url": "https://kpopping.com/profiles/artist/2449-Chuu", 
   "name": "Chuu", 
   "groups": ["LOONA", "yyxy"], 
   "img_url": ["https://kpopping.com/uploads/documents/encyclopedia_body_artist/xfirst_Chuu350x600.png.keep.fff.png.pagespeed.ic.lGKs1u5BzV.png", 
               "https://kpopping.com/uploads/documents/encyclopedia_pose_sidebar_top/xsecond_Chuu350x400.png.keep.e6ecf0.png.pagespeed.ic.BGVl8tJy7G.jpg"]
  }
}
```

### SQLite
SQLite database file is created using the previous generated json file. 

The script `json_to_sql.py` may take an argument
(`--file` or `-f`) as input json filename. By default, `database.json` will be used. 
A `database.db`containing SQLite database will be created where the script is executed.

#### Database diagram
![Database Diagram](../readmefiles/idols_db.png)

## Legal rights
All data are extracted from [kpopping website](https://kpopping.com). According to their [__Terms and Policies__](https://kpopping.com/help/21-Terms-and-Policies) (accessed June 29, 2020) :

```
USE OF Kpopping CONTENT

    By downloading an image or copying other user-generated content (UGC) from Kpopping, you agree that you do not claim any rights to it. The following conditions apply:
    You may use UGC for personal, non-commercial purposes.
    You may use UGC for anything that qualifies as fair use under copyright law, for example journalism (news, comment, criticism, etc.), but please include an attribute ("kpopping" or "courtesy of kpopping") next to where it is displayed.
    You may not use UGC for non-journalistic commercial purposes.
    Your use of UGC is at your own risk. kpopping MAKES NO WARRANTIES OF NON-INFRINGEMENT, and you will indemnify and hold kpopping harmless from any copyright infringement claims arising out of your use of the UGC. (See our general disclaimers below.)You may not copy or use any portions of our site that are not UGC except within the limits of fair use.
```
