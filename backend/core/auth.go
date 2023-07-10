package core

import (
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// Create token for authentication
func CreateAuthenticationToken(user AuthenticatedUser, secretKey []byte, expiresDuration time.Duration) (AccessToken, error) {
	expiresAt := time.Now().Add(expiresDuration)
	claims := user.IntoClaims(expiresAt)
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	rawToken, err := token.SignedString(secretKey)
	if err != nil {
		return AccessToken{}, err
	}
	return AccessToken{
		AccessToken: rawToken,
		TokenType:   "Bearer",
		ExpiresIn:   uint(expiresDuration.Seconds()),
	}, nil
}

type AuthenticationDetails struct {
	user *AuthenticatedUser
}

func (a AuthenticationDetails) New(user *AuthenticatedUser) AuthenticationDetails {
	a = AuthenticationDetails{
		user: user,
	}
	return a
}

func (a *AuthenticationDetails) GetAuthenticatedUser() AuthenticatedUser {
	if a.user == nil {
		panic("no authentication has been set")
	}
	return *a.user
}

func (a *AuthenticationDetails) GetOptionalAuthenticatedUser() *AuthenticatedUser {
	return a.user
}
