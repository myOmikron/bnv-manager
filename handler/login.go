package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
	"github.com/myOmikron/echotools/middleware"
	"github.com/myOmikron/echotools/utility"
)

type loginRequest struct {
	Username *string `json:"username" echotools:"required;not empty"`
	Password *string `json:"password" echotools:"required;not empty"`
}

type loginResponse struct {
	IsAdmin     bool `json:"is_admin"`
	IsClubAdmin bool `json:"is_club_admin"`
}

func (w *Wrapper) Login(c echo.Context) error {
	form := loginRequest{}

	if err := utility.ValidateJsonForm(c, &form); err != nil {
		return c.String(400, err.Error())
	}

	if user, err := ldap_impl.Authenticate(*form.Username, *form.Password, w.DB, w.Config); err != nil {
		c.Logger().Info(err)
		return c.String(401, "Authentication failed")
	} else {
		if err := middleware.Login(w.DB, user, c, true); err != nil {
			c.Logger().Error(err)
			return c.String(500, "Internal server error")
		}

		return c.JSON(200, loginResponse{
			IsAdmin:     user.IsAdmin,
			IsClubAdmin: user.IsClubAdmin,
		})
	}
}
