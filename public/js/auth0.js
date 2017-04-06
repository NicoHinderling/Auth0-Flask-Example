$(document).ready(function() {
     var lock = new Auth0Lock(AUTH0_CLIENT_ID, AUTH0_DOMAIN, {
        auth: {
          redirectUrl: AUTH0_CALLBACK_URL
        }
     });

    $('.auth0-login-button').click(function(e) {
      e.preventDefault();
      lock.show();
    });
});
