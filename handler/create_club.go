package handler

import (
	"github.com/labstack/echo/v4"
	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
	"github.com/myOmikron/echotools/utility"
)

type createClubRequest struct {
	ClubID   *string `json:"club_id" echotools:"required;not null"`
	ClubName *string `json:"club_name" echotools:"required;not null"`
}

func (w *Wrapper) CreateClub(c echo.Context) error {
	form := createClubRequest{}

	if err := utility.ValidateJsonForm(c, &form); err != nil {
		return c.String(400, err.Error())
	}

	if err := ldap_impl.CreateClub(*form.ClubID, *form.ClubName, w.Config); err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	return c.NoContent(201)
}
