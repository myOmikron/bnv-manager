package handler

import (
	"regexp"

	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/middleware"
	"github.com/myOmikron/echotools/utility"

	"github.com/myOmikron/bnv-manager/models/dbmodels"
	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type changePasswordRequest struct {
	NewPassword *string `json:"new_password" echotools:"required;not empty"`
	OldPassword *string `json:"old_password" echotools:"required;not empty"`
}

var (
	lowerCaseAscii = regexp.MustCompile("[a-z]")
	upperCaseAscii = regexp.MustCompile("[A-Z]")
)

func (w *Wrapper) ChangePassword(c echo.Context) error {
	form := changePasswordRequest{}

	if err := utility.ValidateJsonForm(c, &form); err != nil {
		return c.String(400, err.Error())
	}

	var hasUpper, hasLower, hasSpecial bool
	for _, r := range []rune(*form.NewPassword) {
		if lowerCaseAscii.MatchString(string(r)) {
			hasLower = true
		} else if upperCaseAscii.MatchString(string(r)) {
			hasUpper = true
		} else {
			hasSpecial = true
		}

		if hasLower && hasUpper && hasSpecial {
			break
		}
	}
	if len(*form.NewPassword) < 12 {
		return c.String(400, "Password must have a minimum 12 characters")
	} else if !hasLower || !hasUpper {
		return c.String(400, "Password must have lower and upper case characters")
	} else if !hasSpecial {
		return c.String(400, "Password must have at least one special character")
	}

	sessionContext, err := middleware.GetSessionContext(c)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "Internal server error")
	}

	user, ok := sessionContext.GetUser().(*dbmodels.User)
	if !ok {
		c.Logger().Errorf("Could not cast to User")
		return c.String(500, "Internal server error")
	}

	if err := ldap_impl.ChangePasswordForDN(user.DN, *form.OldPassword, *form.NewPassword, w.Config, w.AdminWP); err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	return c.NoContent(200)
}
