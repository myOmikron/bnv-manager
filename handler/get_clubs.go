package handler

import (
	"github.com/labstack/echo/v4"

	"github.com/myOmikron/bnv-manager/modules/ldap_impl"
)

type getClubsResponse struct {
	Clubs []string `json:"clubs"`
}

func (w *Wrapper) GetClubs(c echo.Context) error {
	clubs, err := ldap_impl.GetAllClubs(w.Config)
	if err != nil {
		c.Logger().Error(err)
		return c.String(500, "LDAP Error")
	}

	res := getClubsResponse{Clubs: make([]string, 0)}
	for _, club := range clubs {
		res.Clubs = append(res.Clubs, club.CN)
	}

	return c.JSON(200, res)
}
