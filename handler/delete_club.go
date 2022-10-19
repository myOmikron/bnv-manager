package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/echotools/utility"
	
	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type deleteClubRequest struct {
	ClubID *string `json:"club_id" echotools:"required;not empty"`
}

func (w *Wrapper) DeleteClub(c echo.Context) error {
	form := deleteClubRequest{}

	if err := utility.ValidateJsonForm(c, &form); err != nil {
		return c.String(400, err.Error())
	}

	if err := ldap_impl.DeleteClub(*form.ClubID, w.Config); err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	return c.NoContent(200)
}
