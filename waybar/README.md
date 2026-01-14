See:
  https://jessicadeen.com/posts/2024/keylight-cli/
  https://github.com/jldeen/keylight-cli/releases
  https://www.postman.com/apihandyman/hacking-elgato-key-light/documentation/fun9qrm/elgato-key-light


look for servers listening on ort 9123
```
docker run --rm -it instrumentisto/nmap -p 9123 -v 192.168.4.42
docker run --rm -it instrumentisto/nmap -p 9123 --open 192.168.1.0/24
```


get the status of the server
```
curl --location --request GET 'http://192.168.4.42:9123/elgato/lights'
```
returns
```
{"numberOfLights":1,"lights":[{"on":1,"brightness":52,"temperature":307}]}
```

or set the lights brighnes, warmth and on/off status
```
curl --location --request PUT 'http://192.168.4.42:9123/elgato/lights' --header 'Content-Type: application/json' --data '{
    "numberOfLights": 1,
    "lights": [
        {
            "on": 1,
            "brightness": 30,
            "temperature": 313
        }
    ]
}'
```
returns
```
{"numberOfLights":1,"lights":[{"on":1,"brightness":30,"temperature":313}]}
```

or use the executable keylight-cli
```
keylight on --elgato-ip 192.168.4.42 --number-of-lights 1 -b 20 -t 250
```


--- 

# Getting it working in waybar

Add the following script
```
~/.config/waybar/scripts/elgato_keylight.py
```
install yad, and python-requets

Add these sections to walker config
```
"custom/elgato":{
    "exec": "~/.config/waybar/scripts/elgato_keylight.py",
    "return-type": "json",
    "interval": 5,
    "on-click": "~/.config/waybar/scripts/elgato_keylight.py control",
    "format": "{}",
    "format-icons": {
      "on": "󰛨",
      "off": "󰹐",
      "offline": "󰛨"
    }
  },
```

Add the following to the styles file
```
#custom-elgato {
    margin-right: 20px;
}

#custom-elgato.on {
    color: #a6e3a1;
}

#custom-elgato.off {
    color: #6c7086;
}

#custom-elgato.offline {
    color: #f38ba8;
}
```

Add this file to get an item in the menu
```
~/.local/share/applications/elgato-control.desktop to get the walker working
```