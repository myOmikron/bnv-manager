package handler

import (
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

func (w *Wrapper) ChangePassword(c echo.Context) error {
	form := changePasswordRequest{}

	if err := utility.ValidateJsonForm(c, &form); err != nil {
		return c.String(400, err.Error())
	}

	if err := w.checkPassword(*form.NewPassword); err != nil {
		return c.String(400, err.Error())
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

	if err := middleware.Logout(w.DB, c); err != nil {
		c.Logger().Error(err)
	}

	return c.NoContent(200)
}
