package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
	"github.com/myOmikron/echotools/utility"
)

type resetPasswordClubAdminPath struct {
	ID string `param:"id"`
}

type resetPasswordClubAdminRequest struct {
	Password *string `json:"password" echotools:"required;not empty"`
}

func (w *Wrapper) ResetPasswordClubAdmin(c echo.Context) error {
	path := resetPasswordClubAdminPath{}
	form := resetPasswordClubAdminRequest{}

	if err := c.Bind(&path); err != nil {
		return c.String(400, "Bad request")
	}

	if path.ID == "" {
		return c.String(400, "Bad request")
	}

	if err := utility.ValidateJsonForm(c, &form); err != nil {
		return c.String(400, err.Error())
	}

	if err := w.checkPassword(*form.Password); err != nil {
		return c.String(400, err.Error())
	}

	if err := ldap_impl.SetPasswordForClubAdmin(path.ID, *form.Password, w.Config, w.AdminWP); err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	return c.NoContent(200)
}
