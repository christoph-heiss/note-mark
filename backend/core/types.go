package core

import (
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

type AuthenticatedUser struct {
	UserID uuid.UUID `json:"userId"`
}

func (u *AuthenticatedUser) IntoClaims(expiresAt time.Time) JWTClaims {
	return JWTClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   u.UserID.String(),
			ExpiresAt: jwt.NewNumericDate(expiresAt),
		},
	}
}

type JWTClaims struct {
	jwt.RegisteredClaims
}

func (c *JWTClaims) ToAuthenticatedUser() (AuthenticatedUser, error) {
	if userID, err := uuid.Parse(c.Subject); err != nil {
		return AuthenticatedUser{}, err
	} else {
		return AuthenticatedUser{
			UserID: userID,
		}, nil
	}
}

// OAuth2.0 Access Token, following: RFC6750 & RFC6749
type AccessToken struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	ExpiresIn   uint   `json:"expires_in"`
}

// OAuth2.0 Access Token Request, following: RFC6749
//
// only supporting 'Resource Owner Password Flow'
type AccessTokenRequest struct {
	GrantType string `json:"grant_type" query:"grant_type" form:"grant_type" validate:"required,eq=password"`
	Username  string `json:"username" query:"username" form:"username" validate:"required"`
	Password  string `json:"password" query:"password" form:"password" validate:"required"`
}

type FindUserParams struct {
	Username string `query:"username" validate:"required"`
}

type ServerInfo struct {
	MinSupportedVersion       string `json:"minSupportedVersion"`
	AllowSignup               bool   `json:"allowSignup"`
	EnableAnonymousUserSearch bool   `json:"enableAnonymousUserSearch"`
}

type DeleteParams struct {
	Permanent bool `query:"permanent" validate:"omitempty,required"`
}

type NoteFilterParams struct {
	Deleted bool `query:"deleted" validate:"omitempty,required"`
}
