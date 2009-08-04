{
    "transport": "REST",
    "envelope": "JSON",
    "target": "person/78b6854e22ab09d4ae3dac29b92052963103b33e/",
    "additionalParameters": true,
    "services": {
        "add": {
            "target": "add",
            "parameters": [
                {
                    "name":"name",
                    "type":"string",
                    "default": "hello"
                },
                {
                    "name":"age",
                    "optional": true,
                    "type":"integer",
                    "default":0
                }
            ]
        },
        "remove": {
            "target": "remove",
            "parameters": [
                {
                    "name":"name",
                    "type":"string",
                    "default": "hello"
                }
            ]
        }
    }
}
