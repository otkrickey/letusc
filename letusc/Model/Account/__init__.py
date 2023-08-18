# Exception

# TimeoutError
"Model.Account.Session.session_login_letus:Timeout"

# ValueError
"Model.Account.Database.check:CookieError"
"Model.Account.Database.check:PasswordError"
"Model.Account.Database.pull:InvalidMultiID"
"Model.Account.Database.pull:NotFound"
"Model.Account.Database.push:InvalidAccount"
"Model.Account.Session.session_login_ms:PasswordError"

# WriteError
"Model.Account.Database.push:WriteError"
"Model.Account.Database.update:WriteError"

# KeyError
"Model.DiscordUserBase.from_api:KeyError"
"Model.LetusUserBase.from_api:KeyError"
"Model.Cookie.from_api:KeyError"

from .Account import Account
from .AccountBase import AccountBase

__all__ = [
    "Account",
    "AccountBase",
]
