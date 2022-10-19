package handler

import (
	"github.com/labstack/echo/v4"

	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type getClubAdminsRequest struct {
	ClubID string `query:"club_id"`
}

type ClubAdmin struct {
	Firstname string `json:"firstname"`
	Surname   string `json:"surname"`
	Username  string `json:"username"`
}

type getClubAdminsResponse struct {
	ClubAdmins []ClubAdmin `json:"club_admins"`
}

func (w *Wrapper) GetClubAdmins(c echo.Context) error {
	var form getClubAdminsRequest

	if err := c.Bind(&form); err != nil {
		return c.String(400, "Bad request")
	}

	if form.ClubID == "" {
		return c.String(400, "Parameter club_id must not be empty")
	}

	clubadmins, err := ldap_impl.GetClubadmins(form.ClubID, w.Config)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP error")
	}

	res := getClubAdminsResponse{ClubAdmins: make([]ClubAdmin, 0)}

	for _, clubadmin := range clubadmins {
		res.ClubAdmins = append(res.ClubAdmins, ClubAdmin{
			Firstname: clubadmin.Firstname,
			Surname:   clubadmin.Surname,
			Username:  clubadmin.CN,
		})
	}

	return c.JSON(200, res)
}
