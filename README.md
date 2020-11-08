

launch the command to renew the token :

 curl -d @content http://mafreebox.freebox.fr/api/v4/login/authorize/ > result_auth

click on the button on the freebox

take the trackid in json

 curl http://mafreebox.freebox.fr/api/v3/login/authorize/5  > authorize_result



