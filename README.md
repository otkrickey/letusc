# letus-scraper

```bash
/home/otkrickey/dev/letus-scraper/.venv/bin/python /home/otkrickey/dev/letus-scraper/main.py -l info -e 1
/home/otkrickey/dev/letus-scraper/.venv/bin/python /home/otkrickey/dev/letus-scraper/main.py -s checkAccount -d 601235188571176961 -l info -e 1098772108579962950:1099020068198809610
```

## TODO

### Task on MongoDB

- default

  - Discord: (user_id, guild_id, category_id, channel_id, message_id)

- Account

  - Register Account
    - TUS: (student_id, encrypted_password)
  - Update Account Info
    - TUS: (student_id, encrypted_password)
  - Unregister Account
    - TUS: (student_id, encrypted_password)
  - Check Account Info
    - TUS: (student_id)

- Page
  - Register Page
    - LETUS: (page_id)
    - TUS: (student_id) # Optional: If not provided, use the student_id from the account
  - Fetch Page
    - LETUS: (page_id)
    - TUS: (student_id) # Optional: If not provided, use the student_id from the account
  - Unregister Page
    - LETUS: (page_id)
    - TUS: (student_id) # Optional: If not provided, use the student_id from the account

### Flow

```mermaid
graph TD

subgraph ServiceManager
    SM{ServiceManager}

    S1[CheckAccount]
    S2[RegisterAccount]
    S3[CheckContent]

    SM --> S1
    SM --> S3
    SM --> S2
end

subgraph Middleware
    M1[fetchAccount]
    M2[loginAccount]
    M3[registerAccount]
    M4[uploadAccount]
    M5[fetchPage]
    M6[fetchContent]
end

subgraph Manager
    subgraph AccountManager

        AM1[check_account_info]
        AM2[fetch_account_info]
        AM3[register_account]
        AM4[update_account]

        AM1 --> AM2
        AM3 --> AM4
    end
end

subgraph Model
    subgraph LetusAccount
        LA1[discord_id]
        subgraph LetusPage
            LP1[discord_id]
            subgraph LetusContent
                LC1[discord_id]
                LC2[DB_args]
            end
        end
    end

    subgraph LetusSession
        LS1[login]
        LS2[register]
        LS3[__login_letus]
        LS4[__login_microsoft]
        LS5[load_cookie]

        LS1 --> LS2 --> LS3 --> LS4 --> LS5
    end
end

S1 --> M1
S2 --> M3
S3 --> M5

M1 --> AM1
M2 --> LS1
M3 --> LS2
M4 --> AM3
M5 --> M6

LS5 --> M4

AM2 --> M2
LetusPage --> LetusContent
```

```






```
