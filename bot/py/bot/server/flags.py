#
# Copyright (c) 2016 Pi Inc. All rights reserved.
#
# Author: asarcar@piekul.com
#

import gflags

#
# BotServer
#
gflags.DEFINE_integer(
    "bot_port",
    5002,
    "Bot service port.")

gflags.DEFINE_string("bot_access_token",
    "EAAHt2MW3dSkBAO5xs90MJlBkXEC48pcpCAUs1RcEpchZCPDCjgHLnYyr4mFH5LkeZCFTgZAyr08nf0ZClWwvxk2iI7yoD0qD7oiJVmvoqOmr4vdWjUNFx6HqneTCFkFPglY3C3wYZCZCjk8Uez8kWuh1HTcZB23z02ZBVjw896ZBfqQZDZD",
    "Bot access token.")
# T0:"EAAYEfQL5tDIBANu0DnozZB1P8p4oFmhuPadSZB87YSPZCChmuGRZB6d1hdIRWR0jBFlAJl8QlDe4vvDyh3CZCd9pRD3wZCM76f7ZAN9kr0Q9olBd0QnMNbA8W2ftafGQOMVmfzntUKrwECtxXP0nUBqacfPwGMJ2B2kAd6ZAu2jf3gZDZD",
# T1:"EAAHt2MW3dSkBACZAJ2DGjErZAe1GugJTYHsdNz6uhVVPwYpOEbwsCatKF1qqjtbM0YP3LKGxgkZCAYKcrI8eZAqaZBUEXEqDChobENIH9PmIZAgFe2JgJ1BISQCGKhTihZCQZC62XhHLwXq8dRmzjOlRmEWtXhpridX5YnspdAiuCgZDZD",

gflags.DEFINE_string("bot_verify_token",
    "pi_is_cool",
    "Bot message verify token.")
