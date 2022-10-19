package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type deleteClubRequest struct {
	ClubID string `query:"club_id"`
}

func (w *Wrapper) DeleteClub(c echo.Context) error {
	form := deleteClubRequest{}

	if err := c.Bind(&form); err != nil {
		return c.String(400, err.Error())
	}

	if form.ClubID == "" {
		return c.String(400, "Parameter club_id must not be empty")
	}

	if err := ldap_impl.DeleteClub(form.ClubID, w.Config, w.AdminWP); err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	return c.NoContent(200)
}
