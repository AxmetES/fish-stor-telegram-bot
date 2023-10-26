### Description 
Training project, a telegram bot for a web store.

#### Used technology:
    python-telegram-bot==13.15
    
    environs==9.5.0
    
    requests==2.31.0
    
    redis==5.0.1

### Get Start

clone project:
```bash
git clone https://github.com/AxmetES/fish_bot.git
```
activate environments:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```

install requirements:
```bash
pip install -r requirements.txt
```

create ```.env``` example:

    ```BOT_TOKEN = your bot token```
    
    ```API_TOKEN = your API token```
    
    ```DATABASE_PASSWORD = redis db password```
    
    ```DATABASE_HOST = redis host```
    
    ```DATABASE_PORT = redis port```

run ur CMS:
```bash
npm run develop
```
from ur CMS project repository.

run redis docker:
```bash
docker start redis
```
run telegram bot:
```bash
python3 main.py
```