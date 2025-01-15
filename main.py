import user
import api

apiv2 = api.util_api("10010", "vv5RulzDxXSuIuqQq19jSDFvUYXOJYVfqhHPXETD", 1)
apiv2.refresh_token()
u = apiv2.get_user(6245906)
print(u)